# abstract-writer

추상적이지만 깊이 있는 글을 쓰는 프로그램. 주제 하나를 받아 **발굴 → 작성 → 검사(린트+감사) → 수정** 파이프라인을 돌려
Markdown 글 한 편을 낸다. 한국어와 영어를 지원한다.

"추상적"은 쉽게 "공허함"으로 미끄러진다. 이 프로그램은 그 미끄러짐을 막는 여섯 가지 규칙(구별, 닻, 긴장, 결과, 전환, 감시 어휘)을
프롬프트와 결정론적 린트 양쪽에 심어 두었다. 규칙의 정본은 [`METHOD.md`](METHOD.md)다.

## 설치

의존성이 없다. Python 3.10 이상이면 된다.

```bash
cd outputs/abstract-writer
python3 -m abstract_writer --version        # 그대로 실행
# 또는
pip install -e .                             # `abstract-writer` 명령이 생긴다
```

## 모델 설정

`/chat/completions` 형식의 아무 엔드포인트나 쓴다 (OpenRouter, Nous Portal, OpenAI, 로컬 서버 등).

```bash
export ABSTRACT_WRITER_API_KEY=sk-...                     # OPENROUTER_API_KEY / OPENAI_API_KEY 도 인식
export ABSTRACT_WRITER_BASE_URL=https://openrouter.ai/api/v1   # 기본값
export ABSTRACT_WRITER_MODEL=anthropic/claude-sonnet-4.5       # 기본값. 원하는 모델로 바꾼다
```

Hermes를 이미 쓰고 있다면 `~/.hermes/.env`의 키와 같은 값을 넣으면 된다.

## 사용

```bash
# 한국어 에세이 (언어는 시드에서 자동 감지)
python3 -m abstract_writer "기다림"

# 영어 단상, 짧게, 파일로 저장, 단계별 기록 남기기
python3 -m abstract_writer "waiting" --lang en --form fragments --length short \
    --out waiting.md --trace waiting.trace.json

# 편지 형식, 수정 회차 최대 3번, 통과 점수 8.0
python3 -m abstract_writer "용서에 대하여" --form letter --rounds 3 --threshold 8.0

# 모델 없이 파이프라인만 확인 (오프라인)
python3 -m abstract_writer "기다림" --provider mock

# 이미 있는 글을 검사만 하기 (종료 코드 0=통과, 1=지적 있음)
python3 -m abstract_writer --lint my_essay.md
python3 -m abstract_writer --lint my_essay.md --json
```

| 옵션 | 값 | 설명 |
|---|---|---|
| `--lang` | `ko`, `en` | 출력 언어. 생략하면 시드에서 감지 |
| `--form` | `essay`, `fragments`, `letter` | 에세이 / 번호 붙은 단상 / 한 사람에게 쓰는 편지 |
| `--length` | `short`, `medium`, `long` | 대략 600~900자 / 1200~1800자 / 2500~3500자 |
| `--rounds` | 정수 | 최대 수정 회차 (기본 2) |
| `--threshold` | 실수 | 감사 점수가 이 값 이상이고 verdict가 pass이면 조기 종료 (기본 7.5) |
| `--no-audit` | | 모델 감사·수정 건너뛰기 (작성 1회만) |
| `--no-lint-gate` | | 린트 지적이 있어도 통과 허용 |
| `--provider` | `openai`, `mock` | `openai`는 모든 chat-completions 호환 엔드포인트 |
| `--trace` | 경로 | 개념 지도, 각 회차의 글·린트·감사 결과를 JSON으로 저장 |

## 파이프라인

```
EXCAVATE (발굴) ─ 주제를 질문으로, 구별 2~3, 긴장 1, 닻 2~3, 결과, 전환 후보  → JSON
COMPOSE  (작성) ─ 개념 지도 위에서 글을 쓴다                               → Markdown
LINT     (검사) ─ 모델 없이: 공허 어휘 밀도, 구별 표지 밀도, 단락별 닻, 요약형 결말
AUDIT    (감사) ─ 모델이 여섯 원리로 채점하고 문제 지점을 인용                 → JSON
REVISE   (수정) ─ 인용된 지점을 고친다. 임계치 통과 또는 최대 회차까지 반복
```

`--trace`로 저장한 파일을 열면 각 단계가 무엇을 만들었는지 볼 수 있다. 글이 마음에 안 들 때는
개념 지도(발굴 결과)부터 본다. 지도가 얕으면 글도 얕다.

## 파이썬에서 쓰기

```python
from abstract_writer.pipeline import Options, write
from abstract_writer.providers import make_provider

provider = make_provider("openai", model="anthropic/claude-sonnet-4.5")
result = write("기다림", provider, Options(lang="ko", form="essay", length="medium"))
print(result.text)
print(result.final_lint.summary())
print(result.final_audit["scores"])
```

## 린트가 보는 것

린트는 글이 좋은지 판단하지 않는다. 추상적인 글이 싸게 실패하는 방식만 잡는다.

- **감시 어휘**: 본질, 진정한, 무한, 초월, 조화, 에너지 … 가 같은 문장이나 다음 문장에서 구별로 구체화되지 않으면 지적
- **구별 밀도**: "A가 아니라 B", "와 달리", "반면" 같은 표지가 100어절당 0.4개 미만이면 지적
- **닻 비율**: 구체 단서(사물·장소·시간·숫자·인용)가 없는 단락이 절반을 넘으면 지적
- **요약형 결말**: 마지막 단락이 "결국", "요컨대", "In conclusion" 으로 시작하면 지적

임계값은 `abstract_writer/lint.py` 상단에 있고, `METHOD.md` §8의 대조 예시로 보정했다
(공허한 예시는 반드시 실패, 깊은 예시는 반드시 통과). 어휘 목록은 휴리스틱이다. 오탐이 있으면
목록을 고치고 테스트를 다시 돌린다.

## 테스트

```bash
cd outputs/abstract-writer
python3 -m unittest discover -s tests -v
# 또는 (저장소 루트의 pytest 설정을 끄고)
python3 -m pytest tests -q -o addopts=""
```

모든 테스트는 오프라인이다. 모델 호출은 `MockProvider`가 대신한다.

## 구조

```
abstract-writer/
  METHOD.md                 # 방법론 정본. 프롬프트와 린트는 여기서 파생
  README.md
  pyproject.toml
  abstract_writer/
    cli.py                  # 명령줄
    pipeline.py             # 단계 연결, JSON 관대 파싱, 수락 조건
    prompts.py              # 단계별 시스템 프롬프트 (ko/en)
    lint.py                 # 결정론적 검사
    providers.py            # OpenAI 호환 클라이언트, Mock
  tests/
  examples/
    waiting_ko.md           # 목표 수준을 보여주는 손으로 쓴 참조 예시
```

## 한계

- 린트의 닻 감지는 단어 목록 기반이라 은유적 구체(예: "무너진 목소리")를 놓친다. 이건 감사 단계가 보완한다.
- 감사 점수는 모델의 판단이라 회차마다 흔들린다. `--trace`로 점수 추이를 보고 `--threshold`를 조정한다.
- 현재 프로바이더는 chat-completions 호환 엔드포인트만 지원한다.
