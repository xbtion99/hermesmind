"""Command-line interface.

    abstract-writer "기다림"                        # write (needs an API key)
    abstract-writer "waiting" --lang en --form fragments --length short
    abstract-writer "기다림" --provider mock          # offline dry run
    abstract-writer --lint piece.md                  # deterministic checks only
    abstract-writer "기다림" --out piece.md --trace trace.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__
from .lint import detect_lang, lint_text
from .phrase import has_hangul, parse_phrase
from .pipeline import Options, ProviderError, StageError, write
from .providers import make_provider
from . import prompts


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="abstract-writer",
        description="Write abstract prose that earns its abstraction (see METHOD.md).",
    )
    p.add_argument("seed", nargs="?", help="topic, phrase, or question to write from")
    p.add_argument("--phrase", metavar="TEXT", default=None,
                   help="주제 뒤에 수식어를 붙인 한 줄. 예: \"기다림 함축 짧게\". "
                        "수식어: 함축/압축, 설명, 단상, 편지, 에세이, 짧게, 길게")
    p.add_argument("--shell-phrase", metavar="TEXT", default=None,
                   help="--phrase와 같지만 한글이 없으면 아무 출력 없이 127로 끝난다. "
                        "셸의 command_not_found_handle이 쓴다")
    p.add_argument("--lang", choices=list(prompts.LANG_NAMES), default=None,
                   help="output language (default: detected from the seed)")
    p.add_argument("--form", choices=list(prompts.FORMS), default="essay")
    p.add_argument("--length", choices=list(prompts.LENGTHS), default="medium")
    p.add_argument("--register", choices=list(prompts.REGISTERS), default="plain",
                   help="plain은 설명을 허용하고, compressed(함축)는 접속사와 자기 해설을 금지한다")
    p.add_argument("--rounds", type=int, default=2, help="max revise rounds (default 2)")
    p.add_argument("--threshold", type=float, default=7.5, help="audit score needed to stop early")
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--no-audit", action="store_true", help="skip the model audit/revise loop")
    p.add_argument("--no-lint-gate", action="store_true", help="do not require lint to pass")
    p.add_argument("--provider", default=os.environ.get("ABSTRACT_WRITER_PROVIDER", "openai"),
                   help="openai (any /chat/completions endpoint) or mock. "
                        "기본값은 $ABSTRACT_WRITER_PROVIDER, 없으면 openai")
    p.add_argument("--model", default=None, help="model id (default: $ABSTRACT_WRITER_MODEL)")
    p.add_argument("--base-url", default=None, help="API base URL (default: $ABSTRACT_WRITER_BASE_URL)")
    p.add_argument("--out", type=Path, default=None, help="write the piece to this file")
    p.add_argument("--trace", type=Path, default=None, help="write stage-by-stage JSON trace here")
    p.add_argument("--lint", type=Path, default=None, metavar="FILE",
                   help="only lint an existing file and exit")
    p.add_argument("--json", action="store_true", help="with --lint: print the report as JSON")
    p.add_argument("-q", "--quiet", action="store_true", help="no progress on stderr")
    p.add_argument("--version", action="version", version=f"abstract-writer {__version__}")
    return p


def _progress(quiet: bool):
    def on_stage(name: str, payload):
        if quiet:
            return
        if name == "lint":
            flags = payload.flags
            print(f"[lint] {'ok' if not flags else str(len(flags)) + ' flag(s)'}", file=sys.stderr)
        elif name == "audit":
            print(f"[audit] overall={payload['overall']} verdict={payload['verdict']} "
                  f"issues={len(payload['issues'])}", file=sys.stderr)
        elif name == "excavate":
            print(f"[excavate] question: {payload.get('question', '')}", file=sys.stderr)
        else:
            print(f"[{name}] done", file=sys.stderr)
    return on_stage


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.lint is not None:
        text = args.lint.read_text(encoding="utf-8")
        report = lint_text(text, args.lang, args.register)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) if args.json else report.summary())
        return 0 if report.passed else 1

    phrase = args.phrase or args.shell_phrase
    overrides: dict[str, str] = {}
    if phrase is not None:
        if args.shell_phrase is not None and not has_hangul(phrase):
            # Not Korean, so this was an ordinary mistyped command. Say nothing
            # and let the shell print its own "command not found".
            return 127
        try:
            args.seed, overrides = parse_phrase(phrase)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    if not args.seed:
        build_parser().print_usage(sys.stderr)
        print("error: a seed is required unless --lint is given", file=sys.stderr)
        return 2

    lang = args.lang or detect_lang(args.seed)
    opts = Options(
        lang=lang, form=args.form, length=args.length, register=args.register, rounds=args.rounds,
        threshold=args.threshold, temperature=args.temperature,
        require_lint_pass=not args.no_lint_gate,
    )
    # Words in the phrase override the flag defaults.
    for field, value in overrides.items():
        setattr(opts, field, value)
    try:
        provider = make_provider(args.provider, model=args.model, base_url=args.base_url)
        result = write(args.seed, provider, opts, audit=not args.no_audit,
                       on_stage=_progress(args.quiet))
    except (ProviderError, StageError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.out:
        args.out.write_text(result.text + "\n", encoding="utf-8")
        if not args.quiet:
            print(f"[done] {args.out} ({result.stopped_because})", file=sys.stderr)
    else:
        print(result.text)
    if args.trace:
        args.trace.write_text(json.dumps(result.to_trace(), ensure_ascii=False, indent=2),
                              encoding="utf-8")
    if not args.quiet and not args.out:
        print(f"\n[done] {result.stopped_because}", file=sys.stderr)
    return 0
