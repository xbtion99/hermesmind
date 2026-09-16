---
name: abstract-deep-writing
description: "Write abstract prose that has depth: distinctions, anchors, tension, a turn — not hollow big words."
version: 0.1.0
author: hermesmind
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [writing, essay, abstract, philosophy, prose, korean, depth, anti-slop]
    category: creative
    related_skills: [humanizer, creative-ideation]
---

# Abstract Deep Writing

Write prose that operates at a high level of generality *and* says something. The failure mode this skill
exists to prevent is hollow abstraction: big words swapped for big words ("the essence of being is flow"),
sentences no reader could disagree with because they claim nothing.

## When to use

The user asks for an essay, reflection, meditation, fragments, or letter on an abstract theme
(time, waiting, forgiveness, attention, loneliness, memory, work, silence…) and wants it to feel
deep rather than decorative. Also use it when the user says a draft "sounds profound but empty".

Korean requests such as "추상적이지만 깊이 있는 글", "사유하는 글", "에세이", "단상" trigger this skill.

## The six principles

1. **Abstraction is a level, not a blur.** Move up and down the ladder of abstraction
   (this cow → cow → livestock → asset → wealth). Every paragraph must descend at least once to something concrete.
2. **The distinction is the unit of depth.** "Not A but B." Split something the reader saw as one into two.
   An abstract sentence with no distinction in it is a candidate for deletion.
3. **Place the tension; do not cover it.** Find two true sentences that collide. Either resolve the collision with a
   third distinction, or name the exact point where it cannot be resolved. "Balance", "harmony", "both sides" are cover-ups.
4. **An anchor is a test, not an example.** A concrete scene exists to check whether the claim survives it.
   "Someone grieved" is not an anchor. "The morning after the funeral he made two cups of coffee out of habit" is.
5. **There must be a stake.** If the reader accepts this, what do they see differently tomorrow?
6. **End on a turn, not a summary.** Never open the last paragraph with "in conclusion", "ultimately", "결국", "요컨대".
   The last sentence should make the first sentence read differently.

**Watched vocabulary** (must be specified by a distinction in the same or next sentence, or deleted):
essence, true self, infinite, transcend, ultimate, profound, the universe, energy, oneness, harmony, journey /
본질, 진정한, 무한, 초월, 궁극, 근원, 존재 자체, 조화, 하나됨, 에너지, 진동, 우주적, 심오, 삶의 의미, 영원.

## Procedure

Do the excavation **before** writing a sentence of the piece, and show it to the user only if they ask.

1. **Excavate.** Turn the seed into one real question (one that can be answered wrongly). Write down
   2–3 distinctions (`a` / `b` / why they get confused), one tension (two true claims and where they collide),
   2–3 mundane, specific anchors (a bus stop, a second cup of coffee), the stake, and a candidate final sentence.
2. **Compose** on that map. Every distinction appears. At least two anchors appear and actually test a claim.
   The tension is placed, not covered. The stake is felt in the last third. End on the turn.
3. **Audit** your own draft against the six principles. Quote the exact places that fail. Score each 0–10.
4. **Revise** only the quoted places. Do not add a summary paragraph. Do not add hedges.
5. Deliver the piece alone. Do not explain the method or the map unless asked.

## Style

Plain. No exclamations, no rhetorical inflation, no rhythmic lists of three. One thought per sentence; mix short and long.
Do not preach ("we must…"). No quotations, famous names, or stock metaphors (journey, voyage, seed, mirror).

## Contrast to calibrate on

Hollow:
> Time flows. Within that flow we encounter the essence of being. Waiting is part of life, and in it we discover our true selves.

Deep:
> There are two kinds of waiting. One has a fixed end, like waiting for a bus; the other has an end that belongs to someone
> else, like waiting for a reply. In the first kind time is subtracted; in the second it accumulates. When we say waiting
> is hard, what is hard is not the length of the time but not knowing which way it is being counted.

The second does: distinction (fixed end / end owned by another), anchors (bus, reply), tension (subtracted / accumulated),
stake (what "hard" means changes), turn (length → direction).

## Standalone program

The same method runs as a pipeline with a deterministic lint in this repository at
`outputs/abstract-writer/` (`python3 -m abstract_writer "seed"`; `--lint file.md` checks an existing draft).
Use it when the user wants batch generation, a trace of each stage, or a mechanical check of a draft.
`outputs/abstract-writer/METHOD.md` is the canonical statement of the method; keep this skill in sync with it.

## Pitfalls

- Writing the piece first and "adding depth" afterwards. Depth comes from the excavation; do it first.
- Anchors that are grand images (the sea, the stars). They cannot break a claim, so they test nothing.
- Resolving the tension with a soothing word. If you cannot resolve it, say precisely where it resists.
- A final paragraph that restates the piece. Cut it and end one paragraph earlier if no turn is available.
