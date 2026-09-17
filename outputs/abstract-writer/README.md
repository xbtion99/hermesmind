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

## 폰에서 쓰기 (Android · Termux)

의존성이 없고 순수 표준 라이브러리만 쓰기 때문에 안드로이드 폰에서 그대로 돌아간다.
컴파일이 필요한 패키지가 없어 Hermes 본체를 Termux에 설치하는 것보다 훨씬 가볍다 (패키지 크기 약 152KB).

[Termux](https://termux.dev/)를 설치한 뒤 한 번만 실행한다.

```bash
pkg install -y git python
git clone --depth 1 -b claude/abstract-deep-writing-program-3q05pn \
    https://github.com/xbtion99/hermesmind
cd hermesmind/outputs/abstract-writer
bash termux-setup.sh
```

`-b`로 브랜치를 지정하는 이유는 이 프로그램이 아직 `main`에 머지되지 않았기 때문이다.
그냥 `git clone`만 하면 `main`을 받게 되고 `outputs/` 폴더가 없어서
`cd: No such file or directory`가 난다. `--depth 1`은 폰에서 받는 양을 줄인다
(전체 이력은 수만 개 객체, 브랜치 하나만 얕게 받으면 약 28MB).

이미 `main`을 clone 해버렸다면 다시 받을 필요 없다. 아래 한 줄을 붙여넣으면 된다.
폰에서는 여러 줄을 붙여넣다 중간에서 끊기기 쉬우므로 한 줄로 두었다.

```bash
cd ~/hermesmind && git fetch --depth 1 origin claude/abstract-deep-writing-program-3q05pn && git checkout -B aw FETCH_HEAD && cd outputs/abstract-writer && bash termux-setup.sh
```

얕은 clone에서는 `git checkout <브랜치이름>`이 통하지 않는다. 위처럼 `FETCH_HEAD`를 써야 한다.

`main`에 머지된 뒤에는 `-b` 없이 평범하게 clone 하면 된다.

`termux-setup.sh`가 하는 일은 네 가지다. Python 3.10 이상인지 확인하고, 키 없이 파이프라인이
도는지 오프라인으로 한 번 돌려보고, `~/.abstract-writer.env`를 만들고, `~/.bashrc`에 `aw` 명령을 추가한다.
키는 스크립트가 쓰지 않는다. 직접 넣어야 한다.

```bash
nano ~/.abstract-writer.env    # ABSTRACT_WRITER_API_KEY= 뒤에 키를 붙여넣는다
source ~/.bashrc               # 또는 Termux 세션을 새로 연다
```

키를 넣기 전에 설치가 제대로 됐는지만 먼저 확인하려면 이렇게 한다.
`--provider mock`은 모델을 호출하지 않으므로 키도 네트워크도 필요 없다.

```bash
aw "기다림" --provider mock
```

함축 버전도 키 없이 볼 수 있다.

```bash
aw "기다림" --provider mock --register compressed
```

이제 폰에서 이렇게 쓴다.

```bash
aw "기다림"                     # 화면에 바로 출력
aw "기다림" --out piece.md      # 지금 있는 폴더에 저장
aw --lint piece.md             # 초고 검사. 키도 네트워크도 필요 없다
```

다른 앱에서 열 수 있게 공유 저장소에 바로 저장하려면 `termux-setup-storage`를 한 번 실행한 뒤
`--out ~/storage/shared/Documents/piece.md` 처럼 쓴다.

폰에서 특히 쓸모 있는 건 `--lint`다. 모델 호출이 없으므로 비행기 모드에서도, 키가 없어도 돌아간다.
이동 중에 쓴 초고가 공허한 추상으로 빠졌는지 그 자리에서 확인할 수 있다.

주의할 점 몇 가지.

- `aw` 명령은 설정 당시의 폴더 경로를 기억한다. 폴더를 옮기면 `termux-setup.sh`를 다시 실행한다.
- 스크립트를 다시 실행해도 안전하다. 이미 있는 키 파일과 `.bashrc` 설정은 건드리지 않는다.
- `git clone` 대신 `abstract_writer/` 폴더만 복사해도 돌아간다. 그 경우 폴더가 있는 곳에서
  `python -m abstract_writer "기다림"` 으로 실행한다.

아이폰에는 Termux가 없다. a-Shell 같은 파이썬 앱에 `abstract_writer/` 폴더를 넣거나,
SSH로 다른 기기에 붙어 실행한다.

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
| `--register` | `plain`, `compressed` | `compressed`(함축)는 접속사와 자기 해설을 금지하고 지정 길이의 60%로 줄인다 |
| `--rounds` | 정수 | 최대 수정 회차 (기본 2) |
| `--threshold` | 실수 | 감사 점수가 이 값 이상이고 verdict가 pass이면 조기 종료 (기본 7.5) |
| `--no-audit` | | 모델 감사·수정 건너뛰기 (작성 1회만) |
| `--no-lint-gate` | | 린트 지적이 있어도 통과 허용 |
| `--provider` | `openai`, `mock` | `openai`는 모든 chat-completions 호환 엔드포인트 |
| `--trace` | 경로 | 개념 지도, 각 회차의 글·린트·감사 결과를 JSON으로 저장 |

## 함축 (`--register compressed`)

같은 여섯 원리로 쓰되 설명을 걷어낸 글을 원할 때 쓴다.

```bash
python3 -m abstract_writer "기다림" --register compressed
```

금지하는 것은 네 가지다. 논리 접속사(그러니, 따라서, 즉, 다시 말해), 자기 글을 해설하는 문장
("두 문장은 충돌한다"), 구별에 이름 붙이기("A가 아니라 B다"), 그리고 길이. 지정 길이의 60% 안에서 끝낸다.

같은 개념 지도에서 나온 두 글을 `examples/`에 나란히 두었다.

| | plain | compressed |
|---|---|---|
| 파일 | `examples/waiting_ko.md` | `examples/waiting_ko_compressed.md` |
| 길이 | 670자 | 330자 |
| 설명 표지 | 2 | 0 |

함축은 모호함이 아니다. 구별, 닻, 긴장, 결과는 전부 남아 있어야 하고, 말해지지 않을 뿐이다.
린트는 설명 표지 밀도(`scaffold_density`)만 보므로 둘을 구별하지 못한다. 그 판단은 감사 단계가 한다.

기존 글이 함축 기준에 맞는지 검사할 수도 있다.

```bash
python3 -m abstract_writer --lint draft.md --register compressed
```

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
- **설명 밀도**: 접속사와 자기 해설 표지의 밀도. `--register compressed`일 때만 지적하고, plain에서는 기록만 한다

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
  termux-setup.sh           # 안드로이드(Termux) 1회 설정
  abstract_writer/
    cli.py                  # 명령줄
    pipeline.py             # 단계 연결, JSON 관대 파싱, 수락 조건
    prompts.py              # 단계별 시스템 프롬프트 (ko/en)
    lint.py                 # 결정론적 검사
    providers.py            # OpenAI 호환 클라이언트, Mock
  tests/
  examples/
    waiting_ko.md              # 목표 수준을 보여주는 손으로 쓴 참조 예시 (plain)
    waiting_ko_compressed.md   # 같은 지도, 함축 레지스터
```

## 한계

- 린트의 닻 감지는 단어 목록 기반이라 은유적 구체(예: "무너진 목소리")를 놓친다. 이건 감사 단계가 보완한다.
- 감사 점수는 모델의 판단이라 회차마다 흔들린다. `--trace`로 점수 추이를 보고 `--threshold`를 조정한다.
- 현재 프로바이더는 chat-completions 호환 엔드포인트만 지원한다.
