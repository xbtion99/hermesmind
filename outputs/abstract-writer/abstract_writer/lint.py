"""Deterministic, model-free checks derived from METHOD.md.

The lint does not judge whether a piece is *good*. It catches the cheap
failure modes of abstract writing: hollow vocabulary that is never pinned
down, paragraphs that never touch anything concrete, an absence of
distinctions, and a summary-shaped ending. Anything it flags is a candidate
for the model-driven audit and revision stages, not a verdict.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Vocabulary tables (mirror METHOD.md §7). Keep the two in sync.
# ---------------------------------------------------------------------------

HOLLOW_TERMS = {
    "ko": [
        "본질", "진정한", "무한", "초월", "궁극", "근원", "존재 자체", "조화", "하나됨",
        "에너지", "진동", "우주적", "심오", "삶의 의미", "모든 것", "영원", "아름다움 그 자체",
    ],
    "en": [
        "essence", "true self", "infinite", "transcend", "ultimate", "profound",
        "the universe", "energy", "vibration", "oneness", "harmony", "deep meaning",
        "everything", "eternal", "journey",
    ],
}

# Markers that a hollow term is being *specified* rather than merely invoked.
DISTINCTION_MARKERS = {
    "ko": [
        "아니라", "와 달리", "과 달리", "이 아닌", "가 아닌", "구별", "구분", "차이",
        "반면", "오히려", "라기보다", "두 종류", "두 가지", "하나는", "다른 하나는",
    ],
    "en": [
        "rather than", "unlike", "whereas", "the difference", "distinguish",
        "instead of", "two kinds", "one is", "the other is", "not the same as",
    ],
}

# Regex-level distinction shapes that a word list cannot capture.
DISTINCTION_PATTERNS = {
    "ko": [re.compile(r"[가-힣]+(?:이|가)\s*아니라\s*[가-힣]")],
    "en": [re.compile(r"\bnot\b[^.!?]{1,60}\bbut\b", re.IGNORECASE)],
}

# Cheap concreteness cues. Deliberately mundane: the method wants anchors that
# are ordinary objects and situations, not grand images.
CONCRETE_CUES = {
    "ko": [
        "손", "문", "창", "책상", "의자", "길", "비", "눈", "아침", "저녁", "밤", "커피",
        "전화", "편지", "답장", "병원", "버스", "지하철", "방", "벽", "바닥", "신발", "가방",
        "부엌", "식탁", "접시", "물", "불", "돌", "나무", "종이", "사진", "옷", "열쇠",
        "시계", "정류장", "계단", "복도", "이름", "목소리", "얼굴", "잔", "그릇", "침대",
    ],
    "en": [
        "hand", "door", "window", "desk", "chair", "road", "rain", "snow", "morning",
        "evening", "night", "coffee", "phone", "letter", "reply", "hospital", "bus",
        "train", "room", "wall", "floor", "shoe", "bag", "kitchen", "table", "plate",
        "water", "fire", "stone", "tree", "paper", "photograph", "coat", "key", "clock",
        "stop", "stairs", "hallway", "name", "voice", "face", "glass", "bowl", "bed",
    ],
}

SUMMARY_OPENERS = {
    "ko": ["결국", "요컨대", "정리하면", "결론적으로", "종합하면", "다시 말해", "이처럼"],
    "en": ["in conclusion", "to summarize", "in summary", "ultimately,", "overall,",
           "in the end,", "to sum up", "all in all"],
}

_HANGUL = re.compile(r"[가-힣]")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?。])\s+|\n+")


def detect_lang(text: str) -> str:
    """Return 'ko' when the text contains a meaningful share of Hangul."""
    letters = sum(1 for ch in text if ch.isalpha())
    if letters == 0:
        return "en"
    hangul = len(_HANGUL.findall(text))
    return "ko" if hangul / letters > 0.3 else "en"


_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def split_paragraphs(text: str) -> list[str]:
    text = _HTML_COMMENT.sub("", text)
    parts = re.split(r"\n\s*\n", text.strip())
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Drop markdown headings; they are not prose paragraphs.
        if re.match(r"^#{1,6}\s", p):
            continue
        out.append(p)
    return out


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def word_count(text: str) -> int:
    return len(text.split())


@dataclass
class HollowHit:
    term: str
    sentence: str
    specified: bool  # True when a distinction marker appears nearby


@dataclass
class LintReport:
    lang: str
    words: int
    paragraphs: int
    hollow_hits: list[HollowHit] = field(default_factory=list)
    hollow_unspecified: int = 0
    hollow_density: float = 0.0          # unspecified hollow hits per 100 words
    distinction_count: int = 0
    distinction_density: float = 0.0     # per 100 words
    anchored_paragraphs: int = 0
    anchor_ratio: float = 0.0            # anchored / paragraphs
    question_count: int = 0
    summary_ending: bool = False
    flags: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.flags

    def to_dict(self) -> dict:
        return {
            "lang": self.lang,
            "words": self.words,
            "paragraphs": self.paragraphs,
            "hollow_unspecified": self.hollow_unspecified,
            "hollow_density": round(self.hollow_density, 3),
            "hollow_terms": [h.term for h in self.hollow_hits if not h.specified],
            "distinction_count": self.distinction_count,
            "distinction_density": round(self.distinction_density, 3),
            "anchored_paragraphs": self.anchored_paragraphs,
            "anchor_ratio": round(self.anchor_ratio, 3),
            "question_count": self.question_count,
            "summary_ending": self.summary_ending,
            "flags": list(self.flags),
            "passed": self.passed,
        }

    def summary(self) -> str:
        lines = [
            f"lang={self.lang} words={self.words} paragraphs={self.paragraphs}",
            f"hollow (unspecified)={self.hollow_unspecified} density={self.hollow_density:.2f}/100w",
            f"distinctions={self.distinction_count} density={self.distinction_density:.2f}/100w",
            f"anchored paragraphs={self.anchored_paragraphs}/{self.paragraphs} ({self.anchor_ratio:.0%})",
            f"questions={self.question_count} summary_ending={self.summary_ending}",
        ]
        if self.flags:
            lines.append("FLAGS:")
            lines.extend(f"  - {f}" for f in self.flags)
        else:
            lines.append("no flags")
        return "\n".join(lines)


# Thresholds. Tuned against the contrastive examples in METHOD.md §8: the
# hollow example must fail and the deep example must pass.
MAX_HOLLOW_DENSITY = 1.0       # unspecified hollow terms per 100 words
MIN_DISTINCTION_DENSITY = 0.4  # distinction markers per 100 words
MIN_ANCHOR_RATIO = 0.5         # share of paragraphs with a concrete cue


def _count_markers(text: str, lang: str) -> int:
    low = text.lower()
    n = sum(low.count(m) for m in DISTINCTION_MARKERS[lang])
    for pat in DISTINCTION_PATTERNS[lang]:
        n += len(pat.findall(text))
    return n


def _has_concrete_cue(paragraph: str, lang: str) -> bool:
    if re.search(r"\d", paragraph):
        return True
    if re.search(r"[\"“”'‘’「」]", paragraph):  # quoted speech is concrete
        return True
    low = paragraph.lower()
    if lang == "ko":
        return any(cue in paragraph for cue in CONCRETE_CUES["ko"])
    return any(re.search(rf"\b{re.escape(cue)}s?\b", low) for cue in CONCRETE_CUES["en"])


def lint_text(text: str, lang: str | None = None) -> LintReport:
    text = _HTML_COMMENT.sub("", text)
    lang = lang or detect_lang(text)
    if lang not in HOLLOW_TERMS:
        lang = "en"
    paragraphs = split_paragraphs(text)
    words = max(word_count(text), 1)
    report = LintReport(lang=lang, words=words, paragraphs=len(paragraphs))

    # Hollow vocabulary: a hit is "specified" when the same sentence or the
    # following sentence carries a distinction marker.
    sentences = split_sentences(text)
    for i, sent in enumerate(sentences):
        low = sent.lower()
        for term in HOLLOW_TERMS[lang]:
            if term in low:
                window = sent + " " + (sentences[i + 1] if i + 1 < len(sentences) else "")
                specified = _count_markers(window, lang) > 0
                report.hollow_hits.append(HollowHit(term=term, sentence=sent, specified=specified))
    report.hollow_unspecified = sum(1 for h in report.hollow_hits if not h.specified)
    report.hollow_density = report.hollow_unspecified * 100.0 / words

    report.distinction_count = _count_markers(text, lang)
    report.distinction_density = report.distinction_count * 100.0 / words

    report.anchored_paragraphs = sum(1 for p in paragraphs if _has_concrete_cue(p, lang))
    report.anchor_ratio = report.anchored_paragraphs / len(paragraphs) if paragraphs else 0.0

    report.question_count = text.count("?") + text.count("？")

    if paragraphs:
        last = paragraphs[-1].strip().lower()
        report.summary_ending = any(last.startswith(op) for op in SUMMARY_OPENERS[lang])

    if report.hollow_density > MAX_HOLLOW_DENSITY:
        terms = ", ".join(sorted({h.term for h in report.hollow_hits if not h.specified}))
        report.flags.append(
            f"hollow vocabulary left unspecified ({report.hollow_unspecified} hits: {terms})"
        )
    if report.distinction_density < MIN_DISTINCTION_DENSITY:
        report.flags.append(
            f"too few distinctions ({report.distinction_count} markers in {words} words)"
        )
    if paragraphs and report.anchor_ratio < MIN_ANCHOR_RATIO:
        report.flags.append(
            f"paragraphs without a concrete anchor ({report.anchored_paragraphs}/{len(paragraphs)} anchored)"
        )
    if report.summary_ending:
        report.flags.append("last paragraph opens like a summary instead of a turn")
    return report
