"""Stage prompts. Every rule here is a restatement of METHOD.md.

Each stage system prompt starts with a `[STAGE:<name>]` tag. The mock
provider keys on that tag; the real providers ignore it.
"""

from __future__ import annotations

import json

LANG_NAMES = {"ko": "Korean", "en": "English"}

FORMS = {
    "essay": {
        "ko": "에세이. 5~8개 단락. 제목 한 줄을 첫 줄에 `# 제목` 형식으로 붙인다.",
        "en": "An essay of 5–8 paragraphs. Put a one-line title on the first line as `# Title`.",
    },
    "fragments": {
        "ko": "단상(斷想). 번호가 붙은 8~14개의 짧은 조각. 각 조각은 1~3문장. 조각 사이는 빈 줄. 조각들은 순서대로 읽으면 하나의 사유가 진행되어야 한다.",
        "en": "Numbered fragments, 8–14 of them, each 1–3 sentences, blank line between. Read in order they must advance a single line of thought.",
    },
    "letter": {
        "ko": "편지. 특정한 한 사람에게 쓴다(호칭은 짓지 말고 '당신'으로). 4~7개 단락. 서명 없이 마지막 문장으로 끝낸다.",
        "en": "A letter to one specific person, addressed as 'you'. 4–7 paragraphs. No sign-off; end on the last sentence.",
    },
}

LENGTHS = {
    "short": {"ko": "600~900자", "en": "350–500 words"},
    "medium": {"ko": "1200~1800자", "en": "700–1000 words"},
    "long": {"ko": "2500~3500자", "en": "1500–2000 words"},
}

REGISTERS = {
    "plain": {
        "ko": "설명을 허용한다. 구별과 긴장을 문장으로 분명히 말해도 좋다.",
        "en": "Explanation is allowed. You may state the distinctions and the tension outright.",
    },
    "compressed": {
        "ko": """함축. 아래 제약을 형식 제약보다 우선한다.

- **논리를 잇는 접속사를 쓰지 마라.** 그러니, 그래서, 따라서, 왜냐하면, 즉, 다시 말해, 때문이다, 이것은 ~이다.
  문장을 병치하고 사이를 비워 둬라. 독자가 잇는다.
- **자기 글을 설명하는 문장을 쓰지 마라.** "두 문장은 충돌한다", "이는 ~라는 뜻이다" 같은 해설은 삭제한다.
  충돌은 두 문장을 나란히 놓아 보여 주고 이름 붙이지 않는다.
- **구별에 이름을 붙이지 마라.** "A가 아니라 B다"라고 선언하는 대신, A의 장면과 B의 장면을 붙여 놓아 차이가
  저절로 드러나게 한다.
- 문장을 짧게. 지정한 길이의 60% 안에서 끝낸다. 남은 40%는 침묵이다.
- 마지막 문장은 설명하지 않는다. 앞을 다시 읽게 만들고 끝낸다.

함축은 모호함이 아니다. 구별, 닻, 긴장, 결과는 그대로 있어야 한다. 말해지지 않을 뿐이다.""",
        "en": """Compressed. These constraints outrank the form constraints.

- **No logical connectives.** therefore, thus, so, because, that is, in other words, which means, this is why.
  Set sentences side by side and leave the join empty. The reader makes it.
- **No sentence that explains your own piece.** Delete commentary like "the two sentences collide" or
  "which means that". Show the collision by placing the two sentences together; do not name it.
- **Do not name the distinction.** Instead of declaring "not A but B", put the scene of A beside the scene of B
  and let the difference appear on its own.
- Short sentences. Finish inside 60% of the stated length. The other 40% is silence.
- The last sentence explains nothing. It sends the reader back to the opening and stops.

Compressed is not vague. The distinction, the anchors, the tension and the stake must all still be there.
They are simply not said.""",
    },
}

METHOD_CORE = {
    "ko": """\
## 추상적이지만 깊이 있는 글의 여섯 원리

1. **추상은 층위이지 흐림이 아니다.** 추상 사다리(이 소 → 소 → 가축 → 자산 → 부)를 오르내려라.
   꼭대기에만 머무는 글은 공허하고, 바닥에만 머무는 글은 보고서다. 모든 단락은 최소 한 번 사다리를 내려와
   구체적인 것에 닿는다.
2. **구별이 깊이의 단위다.** "A가 아니라 B", "A와 B는 흔히 혼동되지만"의 형태로, 독자가 하나로 보던 것을 둘로 나눠라.
   구별 없는 추상 문장은 쓰지 마라.
3. **긴장을 덮지 말고 정확히 놓아라.** 두 참인 문장이 충돌하는 지점을 찾아, 해소하는 제3의 구별을 내놓거나
   해소가 불가능한 정확한 지점을 명시하라. "조화", "균형", "양면성"으로 덮는 것은 금지다.
4. **닻은 예시가 아니라 시험이다.** 구체적 장면·사물·상황은 추상 주장이 견디는지 시험하는 장치다.
   "어떤 사람이 슬퍼했다"는 닻이 아니다. "장례식 다음 날 아침, 습관처럼 두 잔의 커피를 내렸다"가 닻이다.
5. **결과가 있어야 한다.** 독자가 이 추상을 받아들이면 내일 무엇을 다르게 보는가. 답이 없으면 장식이다.
6. **요약이 아니라 전환으로 끝나라.** "결국", "요컨대", "정리하면"으로 시작하는 마지막 단락은 금지.
   마지막 문장은 첫 문장을 다시 읽으면 다르게 읽히게 만들어야 한다.

## 감시 어휘
본질, 진정한, 무한, 초월, 궁극, 근원, 존재 자체, 조화, 하나됨, 에너지, 진동, 우주적, 심오, 삶의 의미, 모든 것, 영원.
이 단어들은 등장하는 즉시 같은 문장이나 다음 문장에서 구별로 구체화되어야 한다. 그렇지 않으면 삭제하라.

## 대조 예시

공허한 추상:
> 시간은 흐른다. 우리는 그 흐름 속에서 존재의 본질을 마주한다. 기다림은 삶의 일부이며, 그 안에서 우리는 진정한 자신을 발견한다.

깊은 추상:
> 기다림에는 두 종류가 있다. 하나는 버스를 기다리는 것처럼 끝이 정해진 기다림이고, 다른 하나는 답장을 기다리는 것처럼
> 끝이 상대에게 달린 기다림이다. 첫 번째 기다림에서 시간은 줄어들고, 두 번째 기다림에서 시간은 쌓인다.
> 우리가 "기다리기 힘들다"고 말할 때 힘든 것은 시간의 길이가 아니라, 그 시간이 어느 쪽으로 세어지고 있는지 모른다는 사실이다.

두 번째 예시가 하는 일: 구별(끝이 정해진/상대에게 달린), 닻(버스, 답장), 긴장(줄어듦/쌓임), 결과("힘들다"의 뜻이 바뀜), 전환(길이 → 방향).

## 문체
- 담백하게. 감탄사, 수사적 과장, 나열식 삼항 구조("A이고, B이며, C이다")를 피한다.
- 한 문장에 하나의 생각. 짧은 문장과 긴 문장을 섞는다.
- 독자에게 설교하지 않는다. "우리는 ~해야 한다"를 피한다.
- 인용구, 유명인 이름, 상투적 비유(여행, 항해, 씨앗, 거울)에 기대지 않는다.
""",
    "en": """\
## Six principles of abstract writing that has depth

1. **Abstraction is a level, not a blur.** Move up and down the ladder of abstraction
   (this cow → cow → livestock → asset → wealth). A piece that stays at the top is hollow;
   one that stays at the bottom is a report. Every paragraph descends at least once to touch something concrete.
2. **The distinction is the unit of depth.** "Not A but B", "A and B are usually confused, but…":
   split something the reader saw as one thing into two. Never write an abstract sentence that carries no distinction.
3. **Place the tension exactly; do not cover it.** Find where two true sentences collide. Either supply a
   third distinction that resolves the collision, or name the exact point where it cannot be resolved.
   Covering it with "balance", "harmony", "both sides" is forbidden.
4. **An anchor is a test, not an example.** A concrete scene, object or situation exists to test whether the
   abstract claim survives contact with it. "Someone grieved" is not an anchor. "The morning after the funeral
   he made two cups of coffee out of habit" is an anchor.
5. **There must be a stake.** If the reader accepts this abstraction, what do they see differently tomorrow?
   If there is no answer, the abstraction is decoration.
6. **End on a turn, not a summary.** No final paragraph opening with "In conclusion", "Ultimately", "In the end".
   The last sentence should make the first sentence read differently.

## Watched vocabulary
essence, true self, infinite, transcend, ultimate, profound, the universe, energy, vibration, oneness,
harmony, deep meaning, everything, eternal, journey.
Each of these must be specified by a distinction in the same or the next sentence, or deleted.

## Contrast

Hollow abstraction:
> Time flows. Within that flow we encounter the essence of being. Waiting is part of life, and in it we discover our true selves.

Abstraction with depth:
> There are two kinds of waiting. One has a fixed end, like waiting for a bus; the other has an end that belongs
> to someone else, like waiting for a reply. In the first kind time is subtracted; in the second it accumulates.
> When we say waiting is hard, what is hard is not the length of the time but not knowing which way it is being counted.

What the second passage does: distinction (fixed end / end owned by another), anchors (bus, reply),
tension (subtracted / accumulated), stake (what "hard" means changes), turn (length → direction).

## Style
- Plain. No exclamations, no rhetorical inflation, no lists of three ("A, B, and C") as a rhythm.
- One thought per sentence. Mix short and long sentences.
- Do not preach. Avoid "we must".
- No quotations, no famous names, no stock metaphors (journey, voyage, seed, mirror).
""",
}


def excavate_system(lang: str) -> str:
    L = LANG_NAMES[lang]
    return f"""[STAGE:excavate]
You are the first stage of a writing pipeline. You do not write the piece. You dig up what the piece will be built on.

{METHOD_CORE[lang]}

## Your task
Given a seed (a topic, a phrase, a question), produce a concept map as a single JSON object with exactly these keys.
Write all values in {L}.

{{
  "question": "the seed turned into one real question (not a topic; something that can be answered wrongly)",
  "distinctions": [
    {{"a": "...", "b": "...", "why_confused": "why readers usually treat a and b as one thing"}}
  ],
  "tension": {{"claim_1": "a true sentence", "claim_2": "another true sentence", "where_they_collide": "the exact point of conflict"}},
  "anchors": ["a short, precise concrete scene or object that could break the claim", "..."],
  "stake": "what the reader sees differently tomorrow if they accept this",
  "turn": "a candidate final sentence that makes the opening read differently"
}}

Rules: 2–3 distinctions, 2–3 anchors. Anchors must be mundane and specific (a bus stop, a second cup of coffee), not grand images.
Return only the JSON object. No prose, no code fence."""


def compose_system(lang: str, form: str, length: str, register: str = "plain") -> str:
    L = LANG_NAMES[lang]
    return f"""[STAGE:compose][REGISTER:{register}]
You write abstract prose that earns its abstraction. Write in {L}.

{METHOD_CORE[lang]}

## Register
{REGISTERS[register][lang]}

## Form
{FORMS[form][lang]}
Length: {LENGTHS[length][lang]}.

## Task
You will receive a seed and a concept map (question, distinctions, tension, anchors, stake, turn).
Build the piece on that map. Every distinction must appear. At least two anchors must appear and must actually test a claim.
The tension must be placed, not covered. The stake must be felt in the last third. End on the turn (you may rewrite it).
Do not mention the map, the method, or that you are following rules. Do not explain the piece.
Output only the piece in Markdown."""


def audit_system(lang: str, register: str = "plain") -> str:
    L = LANG_NAMES[lang]
    return f"""[STAGE:audit][REGISTER:{register}]
You are a severe editor. You grade a piece of abstract prose against six principles and you quote the exact places where it fails.

{METHOD_CORE[lang]}

## Scoring (0–10 each; 10 means the principle is fully honored)
- distinction: does the piece split things the reader saw as one? Are the splits real, not decorative?
- anchor: does each abstract claim meet a concrete thing that could break it?
- tension: is a real collision placed and either resolved by a third distinction or precisely marked unresolvable?
- stake: is it clear what changes for the reader?
- turn: does the ending change how the opening reads, rather than summarize?
- hollow: 10 means no watched vocabulary left unspecified; each unspecified hit costs 2 points.

Register for this piece: {REGISTERS[register][lang]}
When the register is compressed, a sentence that explains the piece's own moves, or a logical connective that
does the reader's work, is an issue worth reporting even if everything else is sound.

overall = mean of the six.

Return a single JSON object, values in {L} except the keys:
{{
  "scores": {{"distinction": 0, "anchor": 0, "tension": 0, "stake": 0, "turn": 0, "hollow": 0}},
  "overall": 0.0,
  "issues": [{{"where": "exact quote from the piece", "problem": "what is wrong in one sentence", "fix": "the concrete change to make"}}],
  "verdict": "pass" or "revise"
}}
Quote precisely; the next stage patches by your quotes. List at most 6 issues, most damaging first.
Return only the JSON object. No prose, no code fence."""


def revise_system(lang: str, form: str, length: str, register: str = "plain") -> str:
    L = LANG_NAMES[lang]
    return f"""[STAGE:revise][REGISTER:{register}]
You revise a piece of abstract prose so that it honors the six principles. Write in {L}.

{METHOD_CORE[lang]}

## Register
{REGISTERS[register][lang]}

## Form
{FORMS[form][lang]}
Length: {LENGTHS[length][lang]}.

## Task
You receive the piece, an editor's issue list (with exact quotes), and a lint report.
Fix every issue at the quoted place. Keep what already works; do not rewrite passages that were not flagged unless a fix requires it.
Do not add a summary paragraph. Do not add hedges. Do not explain your changes.
Output only the revised piece in Markdown."""


def excavate_user(seed: str) -> str:
    return f"Seed:\n{seed.strip()}"


def compose_user(seed: str, concept_map: dict) -> str:
    return f"Seed:\n{seed.strip()}\n\nConcept map:\n{json.dumps(concept_map, ensure_ascii=False, indent=2)}"


def audit_user(piece: str, lint_summary: str) -> str:
    return f"Piece:\n<<<\n{piece.strip()}\n>>>\n\nDeterministic lint (advisory):\n{lint_summary}"


def revise_user(piece: str, audit: dict, lint_summary: str) -> str:
    return (
        f"Piece:\n<<<\n{piece.strip()}\n>>>\n\n"
        f"Editor's audit:\n{json.dumps(audit, ensure_ascii=False, indent=2)}\n\n"
        f"Deterministic lint (advisory):\n{lint_summary}"
    )

def paste_prompt(lang: str, form: str, length: str, register: str, seed: str) -> str:
    """One self-contained prompt to paste into a chat window.

    No API key, no network. The pipeline's four stages are folded into a single
    instruction: the model does the excavation privately and returns only the
    piece. Use it with ChatGPT, Claude, or any chat interface, then bring the
    result back through `--lint` to check it mechanically.
    """
    if lang == "ko":
        head = "아래 규칙을 지켜서 글 한 편을 써라."
        task = f"""
## 주제
{seed.strip()}

## 순서
1. 먼저 혼자 정리해라(출력하지 마라): 이 주제를 틀릴 수 있는 질문 하나로 바꾸고,
   구별 2~3개, 긴장 1개, 구체적인 닻 2~3개, 결과 하나, 마지막 문장 후보 하나.
2. 그 위에 글을 써라. 구별은 전부 나와야 하고, 닻은 최소 둘이 실제로 주장을 시험해야 한다.
3. 출력은 글 본문만. 규칙이나 정리 과정은 쓰지 마라. 글에 대한 설명도 붙이지 마라."""
        tail = "\n이제 글만 출력해라."
    else:
        head = "Write one piece, following the rules below."
        task = f"""
## Topic
{seed.strip()}

## Order of work
1. Work this out privately first, and do not print it: turn the topic into one question
   that could be answered wrongly, then 2–3 distinctions, one tension, 2–3 concrete
   anchors, one stake, one candidate final sentence.
2. Write the piece on top of that. Every distinction appears; at least two anchors
   actually test a claim.
3. Output the piece only. No rules, no notes, no explanation of what you did."""
        tail = "\nNow output the piece only."

    return f"""{head}

{METHOD_CORE[lang]}

## Register
{REGISTERS[register][lang]}

## Form
{FORMS[form][lang]}
Length: {LENGTHS[length][lang]}.
{task}
{tail}
"""
