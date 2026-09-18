"""Turn a bare phrase into a seed plus option overrides.

On a phone the shortest possible input wins, so the shell's
`command_not_found_handle` sends anything non-ASCII here and the user types
only what they want written:

    기다림                → seed "기다림"
    기다림 함축           → seed "기다림", register compressed
    첫눈 단상 짧게        → seed "첫눈", form fragments, length short

Trailing words are read as modifiers right to left and stop at the first word
that is not one. Everything to the left is the seed, so a seed may itself
contain a modifier word as long as something follows it. When two words set the
same thing, the later one wins, since that is someone correcting themselves.
"""

from __future__ import annotations

import re

_HANGUL = re.compile(r"[가-힣]")

# word -> (Options field, value)
MODIFIERS: dict[str, tuple[str, str]] = {
    # register
    "함축": ("register", "compressed"),
    "압축": ("register", "compressed"),
    "함축적으로": ("register", "compressed"),
    "설명": ("register", "plain"),
    "compressed": ("register", "compressed"),
    "plain": ("register", "plain"),
    # form
    "단상": ("form", "fragments"),
    "조각": ("form", "fragments"),
    "편지": ("form", "letter"),
    "에세이": ("form", "essay"),
    "fragments": ("form", "fragments"),
    "letter": ("form", "letter"),
    "essay": ("form", "essay"),
    # mode: print the prompt instead of calling a model
    "프롬프트": ("mode", "prompt"),
    "붙여넣기": ("mode", "prompt"),
    "prompt": ("mode", "prompt"),
    # length
    "짧게": ("length", "short"),
    "길게": ("length", "long"),
    "보통": ("length", "medium"),
    "short": ("length", "short"),
    "long": ("length", "long"),
    "medium": ("length", "medium"),
}


def has_hangul(text: str) -> bool:
    return bool(_HANGUL.search(text))


# People copy examples out of a README along with the prompt character in
# front of them, and the shell passes it straight through.
PROMPT_MARKERS = {"$", ">", "%", "#", "»", "❯"}


def parse_phrase(phrase: str) -> tuple[str, dict[str, str]]:
    """Split a phrase into (seed, overrides).

    Raises ValueError when nothing is left to write about.
    """
    tokens = phrase.split()
    while len(tokens) > 1 and tokens[0] in PROMPT_MARKERS:
        tokens.pop(0)
    if not tokens:
        raise ValueError("빈 입력입니다")

    overrides: dict[str, str] = {}
    end = len(tokens)
    while end > 1:  # never consume the last remaining token
        found = MODIFIERS.get(tokens[end - 1].lower())
        if found is None:
            break
        field, value = found
        # Scanning right to left, so the first value seen is the last one typed.
        # "짧게 길게" is someone correcting themselves: the later word wins.
        overrides.setdefault(field, value)
        end -= 1

    seed = " ".join(tokens[:end]).strip()
    if not seed:
        raise ValueError("주제가 없습니다")
    return seed, overrides
