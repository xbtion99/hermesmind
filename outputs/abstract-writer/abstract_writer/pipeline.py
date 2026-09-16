"""EXCAVATE → COMPOSE → [LINT + AUDIT] → REVISE loop. See METHOD.md §9."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from . import prompts
from .lint import LintReport, lint_text
from .providers import Provider, ProviderError

_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


class StageError(RuntimeError):
    pass


def parse_json_lenient(text: str) -> dict:
    """Accept a bare object, a fenced object, or an object with prose around it."""
    text = text.strip()
    candidates = [text]
    m = _JSON_FENCE.search(text)
    if m:
        candidates.insert(0, m.group(1).strip())
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])
    for cand in candidates:
        try:
            obj = json.loads(cand)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    raise StageError(f"stage did not return a JSON object: {text[:200]!r}")


def validate_map(cmap: dict) -> dict:
    required = ["question", "distinctions", "tension", "anchors", "stake", "turn"]
    missing = [k for k in required if k not in cmap]
    if missing:
        raise StageError(f"concept map missing keys: {missing}")
    if not isinstance(cmap["distinctions"], list) or len(cmap["distinctions"]) < 2:
        raise StageError("concept map needs at least two distinctions")
    if not isinstance(cmap["anchors"], list) or len(cmap["anchors"]) < 2:
        raise StageError("concept map needs at least two anchors")
    return cmap


def validate_audit(audit: dict) -> dict:
    scores = audit.get("scores")
    if not isinstance(scores, dict):
        raise StageError("audit missing 'scores'")
    keys = ["distinction", "anchor", "tension", "stake", "turn", "hollow"]
    vals = []
    for k in keys:
        try:
            vals.append(float(scores.get(k, 0)))
        except (TypeError, ValueError):
            vals.append(0.0)
    audit["scores"] = dict(zip(keys, vals))
    audit["overall"] = round(sum(vals) / len(vals), 2)  # recompute; never trust the model's mean
    audit.setdefault("issues", [])
    if not isinstance(audit["issues"], list):
        audit["issues"] = []
    audit["verdict"] = "pass" if str(audit.get("verdict", "")).lower() == "pass" else "revise"
    return audit


@dataclass
class Options:
    lang: str = "ko"
    form: str = "essay"
    length: str = "medium"
    rounds: int = 2            # maximum revise rounds
    threshold: float = 7.5     # audit overall needed to stop early
    temperature: float = 0.8
    require_lint_pass: bool = True

    def validate(self) -> "Options":
        if self.lang not in prompts.LANG_NAMES:
            raise ValueError(f"lang must be one of {list(prompts.LANG_NAMES)}")
        if self.form not in prompts.FORMS:
            raise ValueError(f"form must be one of {list(prompts.FORMS)}")
        if self.length not in prompts.LENGTHS:
            raise ValueError(f"length must be one of {list(prompts.LENGTHS)}")
        if self.rounds < 0:
            raise ValueError("rounds must be >= 0")
        return self


@dataclass
class Round:
    index: int
    piece: str
    lint: LintReport
    audit: dict | None


@dataclass
class Result:
    seed: str
    options: Options
    concept_map: dict
    rounds: list[Round] = field(default_factory=list)
    stopped_because: str = ""

    @property
    def text(self) -> str:
        return self.rounds[-1].piece if self.rounds else ""

    @property
    def final_lint(self) -> LintReport:
        return self.rounds[-1].lint

    @property
    def final_audit(self) -> dict | None:
        return self.rounds[-1].audit

    def to_trace(self) -> dict:
        return {
            "seed": self.seed,
            "options": self.options.__dict__,
            "concept_map": self.concept_map,
            "stopped_because": self.stopped_because,
            "rounds": [
                {"index": r.index, "lint": r.lint.to_dict(), "audit": r.audit, "piece": r.piece}
                for r in self.rounds
            ],
        }


def _accept(lint: LintReport, audit: dict, opts: Options) -> tuple[bool, str]:
    if audit["overall"] < opts.threshold:
        return False, f"audit overall {audit['overall']} < threshold {opts.threshold}"
    if audit["verdict"] != "pass":
        return False, "audit verdict is 'revise'"
    if opts.require_lint_pass and not lint.passed:
        return False, "lint flags: " + "; ".join(lint.flags)
    return True, "accepted"


def write(seed: str, provider: Provider, options: Options | None = None,
          *, audit: bool = True, on_stage=None) -> Result:
    """Run the full pipeline. `on_stage(name, payload)` is called after each stage."""
    opts = (options or Options()).validate()
    seed = seed.strip()
    if not seed:
        raise ValueError("seed is empty")

    def emit(name: str, payload):
        if on_stage:
            on_stage(name, payload)

    # 1. EXCAVATE
    raw = provider.complete(prompts.excavate_system(opts.lang), prompts.excavate_user(seed),
                            temperature=opts.temperature, max_tokens=1500)
    cmap = validate_map(parse_json_lenient(raw))
    emit("excavate", cmap)

    result = Result(seed=seed, options=opts, concept_map=cmap)

    # 2. COMPOSE
    piece = provider.complete(prompts.compose_system(opts.lang, opts.form, opts.length),
                              prompts.compose_user(seed, cmap),
                              temperature=opts.temperature, max_tokens=4000).strip()
    emit("compose", piece)

    for idx in range(opts.rounds + 1):
        lint = lint_text(piece, opts.lang)
        emit("lint", lint)
        audit_obj: dict | None = None
        if audit:
            raw = provider.complete(prompts.audit_system(opts.lang),
                                    prompts.audit_user(piece, lint.summary()),
                                    temperature=0.2, max_tokens=1500)
            audit_obj = validate_audit(parse_json_lenient(raw))
            emit("audit", audit_obj)
        result.rounds.append(Round(index=idx, piece=piece, lint=lint, audit=audit_obj))

        if not audit:
            result.stopped_because = "audit disabled"
            break
        ok, why = _accept(lint, audit_obj, opts)
        if ok:
            result.stopped_because = why
            break
        if idx == opts.rounds:
            result.stopped_because = f"max rounds reached ({why})"
            break

        # 3. REVISE
        piece = provider.complete(prompts.revise_system(opts.lang, opts.form, opts.length),
                                  prompts.revise_user(piece, audit_obj, lint.summary()),
                                  temperature=opts.temperature, max_tokens=4000).strip()
        emit("revise", piece)

    return result


__all__ = ["Options", "Result", "Round", "write", "parse_json_lenient", "StageError", "ProviderError"]
