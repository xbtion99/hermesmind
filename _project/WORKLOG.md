# WORKLOG

## 2026-09-16  Claude (claude-code-web / xbtion99)
- 목표: 추상적이지만 깊이 있는 글을 쓰는 프로그램을 만들고 검증한다
- 변경 파일: outputs/abstract-writer/** (신규), skills/creative/abstract-deep-writing/SKILL.md (신규), research/2026-09-16_abstract-deep-writing.md, evaluations/2026-09-16_abstract-writer.md, _project/*
- 검증 결과: unittest 42 OK · pytest 42 passed · ruff 통과 · mock 파이프라인 엔드투엔드 실행 [샌드박스 검증됨]. 실제 모델 호출 [Mac·API 키 필요]
- 결정: DECISIONS.md 2026-09-16 5건
- blocker: API 키 없음 → 글 품질 미측정
- 다음 한 가지 행동: Mac에서 API 키 설정 후 실제 모델로 1편 생성, 트레이스와 함께 evaluations/에 기록 (API 키 필요)

## 2026-09-16  Claude (claude-code-web / xbtion99) — 후속
- 목표: 폰(Termux)에서 abstract-writer를 쓸 수 있게 한다
- 변경 파일: outputs/abstract-writer/termux-setup.sh (신규), outputs/abstract-writer/README.md
- 검증 결과: 폴더 복사만으로 실행됨 · PYTHONPATH 실행됨 · 오프라인 린트 동작 · 설정 스크립트 2회 실행 멱등 · 상대경로 출력이 사용자 cwd에 저장됨 확인 · unittest 42 OK · ruff 통과 [샌드박스 검증됨]
- 결정: `aw`를 cd 대신 PYTHONPATH로 구현 (상대경로 footgun 제거)
- blocker: 실제 Termux 기기에서 미실행
- 다음 한 가지 행동: 폰에서 termux-setup.sh를 실행하고 `aw "기다림"` 결과를 확인 (Android 기기 · API 키 필요)

## 2026-09-16  Claude (claude-code-web / xbtion99) — 후속 2
- 목표: 사용자가 Termux에서 만난 `cd: No such file or directory` 원인 규명과 수정
- 원인: 프로그램이 아직 main에 머지되지 않은 PR 브랜치에만 있어 `git clone`이 outputs/ 없는 main을 받음
- 변경 파일: outputs/abstract-writer/README.md (clone 명령에 -b 브랜치 지정, 이미 clone한 경우 복구 절차 추가)
- 검증 결과: 실제 GitHub에서 main 얕은 clone으로 오류 재현 확인 · `git fetch --depth 1 origin <branch>` + `git checkout -b aw FETCH_HEAD` 복구 동작 확인 · `--depth 1 -b <branch>` clone(약 28MB)으로 바로 실행됨 확인 · unittest 42 OK · ruff 통과 [샌드박스 검증됨]
- 결정: 얕은 clone에서는 `git checkout <branch>`가 실패하므로 README는 FETCH_HEAD 방식을 안내한다
- blocker: 없음
- 다음 한 가지 행동: 폰에서 수정된 clone 명령으로 재시도 (Android 기기 필요)

## 2026-09-17  Claude (claude-code-web / xbtion99) — 함축 레지스터
- 목표: 사용자 요청 "좀더 함축적으로"를 일회성 고쳐쓰기가 아니라 프로그램 기능으로 만든다
- 변경 파일: abstract_writer/{prompts,lint,pipeline,cli,providers}.py, METHOD.md(§10 신설), README.md, examples/waiting_ko_compressed.md(신규), skills/creative/abstract-deep-writing/SKILL.md(0.2.0), tests/*
- 검증 결과: 함축 예시가 원본 670자 → 330자, 설명 표지 2 → 0 · compressed 린트 통과 · plain 예시는 plain에서 계속 통과 · mock 엔드투엔드 동작 · unittest 60 OK(42→60) · ruff 통과 [샌드박스 검증됨]
- 결정: 함축을 form/length와 독립된 레지스터 축으로 분리. scaffold_density는 compressed에서만 지적
- blocker: 실제 모델이 함축 지시를 얼마나 지키는지 미측정 (API 키 필요)
- 다음 한 가지 행동: 실제 모델로 plain과 compressed를 같은 주제로 한 편씩 생성해 차이를 evaluations/에 기록 (API 키 필요)

## 2026-09-17  Claude (claude-code-web / xbtion99) — 한글 단어만 입력
- 목표: 폰에서 명령어·따옴표·플래그 없이 한글 주제만 쳐도 글이 나오게 한다
- 변경 파일: abstract_writer/phrase.py(신규), abstract_writer/cli.py(--phrase, --shell-phrase, ABSTRACT_WRITER_PROVIDER), termux-setup.sh(command_not_found_handle), README.md, tests/test_phrase.py(신규), tests/test_cli.py
- 검증 결과: 임시 HOME에 훅 설치 후 5개 경우 실측 — 한글 단어만/한글+수식어는 실행, 영문 오타(gti)와 비ASCII 오타(café)는 평소대로 command not found, 정상 명령 영향 없음 · unittest 79 OK(60→79) · ruff 통과 [샌드박스 검증됨]
- 결정: bash 글로브의 한글 범위는 café도 잡으므로, 셸은 비ASCII만 거르고 한글 판별은 Python이 한다. 한글이 없으면 무출력 127로 끝내 셸이 원래 메시지를 찍게 한다
- 버그 1건: 같은 갈래 수식어가 겹칠 때 주석은 leftmost라고 했으나 실제는 마지막에 친 것이 이김. 테스트가 잡았고, 자기 정정으로 읽는 편이 자연스러워 동작을 유지하고 주석·테스트를 고침
- blocker: 실제 Termux 기기에서 훅 미검증
- 다음 한 가지 행동: 폰에서 setup을 다시 돌리고 `기다림`만 쳐서 확인 (Android 기기 필요)

## 2026-09-17  Claude (claude-code-web / xbtion99) — 훅 설치 실패 수정
- 목표: 폰에서 `저녁`을 쳤는데 command not found가 난 원인 규명과 수정
- 원인: termux-setup.sh의 멱등성 검사가 .bashrc에 "abstract-writer.env" 문자열이 있으면 "이미 설정됨"으로 건너뛰었다. 그 문자열은 이전 버전이 이미 넣어 둔 것이라, 새로 추가된 command_not_found_handle이 영영 설치되지 않았다
- 변경 파일: abstract_writer/shellrc.py(신규), termux-setup.sh(설치를 shellrc에 위임 + 설치 검증 단계 추가), README.md, tests/test_shellrc.py(신규)
- 검증 결과: 사용자와 같은 모양의 예전 .bashrc로 재현 후 업그레이드 확인 — 예전 블록 제거, 사용자 줄 보존, 백업 생성, 2회차 unchanged · 한글 단어/수식어/따옴표 입력 모두 실행, 영문 오타는 command not found 유지 · unittest 92 OK(79→92) · ruff 통과 [샌드박스 검증됨]
- 결정: .bashrc 편집을 "없으면 추가"에서 마커 구간 교체로 바꾼다. 셸 스크립트의 문자열 검사 대신 Python 모듈로 옮겨 단위 테스트를 붙였다
- blocker: 없음
- 다음 한 가지 행동: 폰에서 setup 재실행 후 `저녁` 입력 확인 (Android 기기 필요)

## 2026-09-17  Claude (claude-code-web / xbtion99) — 키 탐색
- 목표: 폰에서 훅은 통과했으나 "no API key"에서 멈춤. 키를 넣는 경로를 짧게 만든다
- 변경 파일: abstract_writer/keys.py(신규), abstract_writer/providers.py, README.md, tests/test_keys.py(신규), tests/test_pipeline.py
- 검증 결과: 환경변수 > ~/.abstract-writer.env > ~/.hermes/.env 순서 실측 · 파일을 실행 시점에 직접 읽어 source 불필요 확인 · 키 없을 때 메시지가 실제 파일 경로와 nano 명령을 지목 · unittest 107 OK(92→107) · ruff 통과 [샌드박스 검증됨]
- 결정: Hermes가 쓰는 $HERMES_HOME/.env를 폴백으로 읽는다. 같은 기기에서 Hermes를 쓰면 키를 두 번 적을 필요가 없고, 경로는 hermes_constants.get_env_path()의 규약과 같다
- blocker: 사용자가 키를 직접 넣어야 한다. 대신할 수 없음
- 다음 한 가지 행동: 폰에서 nano ~/.abstract-writer.env 로 키를 넣고 `저녁` 실행 (API 키 필요)

## 2026-09-17  Claude (claude-code-web / xbtion99) — 키 종류별 엔드포인트 자동 선택
- 목표: "GPT 키를 넣을까"에 대한 답. 키만 넣어도 맞는 엔드포인트로 가게 한다
- 문제: 기본 base_url이 OpenRouter, 기본 모델이 anthropic/claude-sonnet-4.5였다. OpenAI 키를 넣으면 401만 뜨고 원인을 알 수 없다. 게다가 예전 키 파일 템플릿이 그 두 값을 export로 박아 두어 사용자 환경에 이미 들어가 있다
- 변경 파일: abstract_writer/endpoints.py(신규), abstract_writer/keys.py(FoundKey에 var 추가), abstract_writer/providers.py(resolve 사용 + 401/404 메시지), termux-setup.sh(템플릿에서 base/model 주석 처리), README.md, tests/test_endpoints.py(신규), tests/test_keys.py
- 검증 결과: 예전 템플릿 값이 환경에 있는 상태에서 OpenAI 키 → api.openai.com/gpt-4o, OpenRouter 키 → openrouter/claude-sonnet 실측 · 직접 지정한 base/model은 유지 · 401/404 메시지가 현재 값과 바꿀 변수명을 지목 · unittest 125 OK(107→125) · ruff 통과 [샌드박스 검증됨]
- 결정: "기본값과 같은 값은 사용자가 정한 것으로 치지 않는다". 이래야 이미 배포된 키 파일의 낡은 기본값이 자동 선택을 막지 않는다
- blocker: 실제 OpenAI 키로 호출해 보지 못함. gpt-4o가 해당 계정에서 쓸 수 있는 모델인지도 미확인
- 다음 한 가지 행동: 폰에서 OpenAI 키를 넣고 `저녁` 실행. 모델 오류가 나면 메시지가 알려주는 대로 ABSTRACT_WRITER_MODEL 변경 (API 키 필요)

## 2026-09-17  Claude (claude-code-web / xbtion99) — 키 없이 쓰는 경로
- 목표: "GPT 키 넣는 법을 모름, ChatGPT와 연동할까"에 대한 답. ChatGPT 구독은 API 키가 아니므로 연동이 불가능하다. 대신 키 없이 쓰는 길을 만든다
- 변경 파일: abstract_writer/prompts.py(paste_prompt 신설), abstract_writer/phrase.py(프롬프트 수식어), abstract_writer/cli.py(--prompt), termux-setup.sh, README.md, tests/test_phrase.py, tests/test_cli.py
- 검증 결과: HOME과 키 환경변수를 모두 제거한 상태에서 프롬프트 출력 확인 · 레지스터·형식·길이가 프롬프트에 반영됨 · 한글 단어 경로(`저녁 프롬프트 함축`)로도 동작 · unittest 132 OK(125→132) · ruff 통과 [샌드박스 검증됨]
- 결정: 프로젝트 지침 9-2의 "외부 서비스 필요 시 붙여넣기용 프롬프트로 전환" 패턴을 프로그램 기능으로 넣는다. 4단계 파이프라인을 한 프롬프트로 접되, 발굴은 모델이 속으로 하고 글만 출력하도록 지시한다
- 기존 테스트가 새 mode 필드를 잡음(수식어는 모두 Options 필드여야 한다는 불변식). mode는 CLI 동작이라 테스트를 갱신하고 Options 필드 존재 검사를 따로 추가
- blocker: 없음. 키 없이 쓸 수 있다
- 다음 한 가지 행동: 폰에서 `저녁 프롬프트` 출력을 ChatGPT에 붙여넣고, 돌아온 글을 `aw --lint`로 검사 (키 불필요)

## 2026-09-17  Claude (claude-code-web / xbtion99) — 키 없을 때의 한글 단어 경로
- 목표: 사용자가 `버거킹 단상`을 쳤으나 키가 없어 오류만 나고 아무것도 못 얻음
- 변경 파일: abstract_writer/keys.py(오류 메시지에 --prompt 안내 추가), abstract_writer/cli.py(phrase 경로에서 키 없으면 프롬프트로 대체), README.md, tests/test_cli.py
- 검증 결과: 키·HOME 없는 환경에서 `--shell-phrase "버거킹 단상"` → 프롬프트 출력, exit 0, 주제와 단상 형식 반영, stderr에 사유 한 줄 · `abstract_writer "버거킹"` 명령형은 exit 1로 그대로 오류 · unittest 135 OK(132→135) · ruff 통과 [샌드박스 검증됨]
- 결정: 짧게 치는 인터페이스(phrase)는 너그럽게, 길게 치는 인터페이스(명령형)는 정확하게. phrase는 최소 타이핑이 목적이므로 빈손으로 끝내지 않는다
- blocker: 없음
- 다음 한 가지 행동: 폰에서 pull 후 `버거킹 단상` 실행, 나온 프롬프트를 ChatGPT에 붙여넣기 (키 불필요)
- 사고: 위 커밋(9af24c3)을 테스트 1건 실패 상태로 푸시했다. `python3 -m unittest ... | tail -3 && git push` 형태라 파이프 끝의 tail이 0을 반환해 && 체인이 실패를 막지 못했다. 다음 커밋(테스트 문구 갱신)으로 초록 복구. 이후 검증 명령에는 set -o pipefail을 쓴다

## 2026-09-17  Claude (claude-code-web / xbtion99) — 복사된 셸 표시가 주제로 들어감
- 목표: 폰에서 프롬프트는 나왔으나 주제가 "$ 버거킹"이 됨
- 원인: 내가 README와 답변의 예시에 셸 표시 `$ `를 붙여 썼다. 사용자가 그대로 복사해 붙여넣으면 `$`가 인자로 들어오고, 비ASCII가 섞여 있어 훅이 통과시킨다
- 변경 파일: abstract_writer/phrase.py(선행 프롬프트 기호 제거), abstract_writer/prompts.py(한국어 경로의 Register/Form/Length 제목을 한글로), README.md·termux-setup.sh(예시에서 $ 제거), tests/test_phrase.py, tests/test_cli.py
- 검증 결과: "$ 버거킹 단상" → 주제 "버거킹", 형식 fragments 실측 · 마지막 토큰은 절대 지우지 않아 "$" 하나만 쳐도 주제로 남음 · 주제 중간의 $는 보존 · 프롬프트 제목이 한국어 경로에서 한글로 · unittest 141 OK(135→141) · ruff 통과 [샌드박스 검증됨]
- 결정: 문서 예시에 셸 표시를 쓰지 않는다. 코드도 선행 기호($ > % # » ❯)를 떼어내되 마지막 토큰은 건드리지 않는다
- blocker: 없음
- 다음 한 가지 행동: 폰에서 pull 후 `버거킹 단상`, 나온 프롬프트를 ChatGPT에 붙여넣고 결과를 aw --lint로 검사 (키 불필요)

## 2026-09-17  Claude (claude-code-web / xbtion99) — 첫 실제 산출물과 평가
- 목표: --prompt가 만든 프롬프트가 실제 모델에서 방법론대로 작동하는지 확인
- 변경 파일: outputs/abstract-writer/examples/burgerking_ko.md(신규), evaluations/2026-09-17_first-model-output.md(신규)
- 검증 결과: 주제 "버거킹", 단상 14조각, 1231자 · --lint 지적 0건(감시어휘 0, 구별 1.52/100, 닻 14/14, 요약형 아님) [샌드박스 검증됨]
- 발견: 첫 시도가 1026자로 지정 길이(1200~1800) 미달. 린트가 길이·조각 수를 검사하지 않아 못 잡았다. 조각 두 개를 더해 해결
- 결정: 다음 개선은 린트에 길이·조각 수 검사 추가
- blocker: 자동 파이프라인(감사·수정 회차)은 여전히 미검증. API 키 필요
- 다음 한 가지 행동: 린트에 길이·조각 수 검사를 넣는다 (키 불필요)

## 2026-09-17  Claude (claude-code-web / xbtion99) — 린트에 길이·단락 수 검사
- 목표: 어제 평가가 지목한 단 하나의 다음 작업. 린트가 길이 위반(1026자 vs 1200~1800)을 그냥 통과시킨 결함을 없앤다
- 변경 파일: abstract_writer/prompts.py(LENGTH_RANGES·FORM_UNITS 신설, 영어 길이 재보정, essay 4~8로), abstract_writer/lint.py(measure_size·length_target·검사), abstract_writer/pipeline.py, abstract_writer/cli.py(--form/--length 기본값 None), METHOD.md, README.md, tests/*
- 작업 중 드러난 진짜 문제 2건:
  1) 영어 길이 기준이 한국어보다 두 배 가까이 컸다(short: 350~500단어 vs 600~900자 ≈ 200~300단어). 영어를 200~300/400~600/850~1200으로 재보정
  2) essay 형식이 5~8단락을 요구했으나 참조 예시가 4단락이었다. 형식과 예시가 어긋나 있었다. 4~8로 조정
- 결정: 길이·단락 수치를 prompts.py 한 곳에 두고 프롬프트 문구와 린트가 모두 거기서 나오게 한다. 두 수치가 어긋나면 깨지는 불변식 테스트 3개 추가
- 검증 결과: 첫 산출물(버거킹 1230자/14조각)이 브리프와 함께 검사해도 지적 0건 · 1026자 버전은 "shorter than asked"로 잡힘 · mock 4종이 short/essay에서 전부 통과 · --lint만 주면 길이는 안 봄 · unittest 156 OK(141→156) · ruff 통과 [샌드박스 검증됨]
- blocker: 자동 파이프라인(감사·수정 회차) 여전히 미검증. API 키 필요
- 다음 한 가지 행동: API 키가 생기면 파이프라인을 끝까지 돌려 감사 점수 추이를 evaluations/에 기록 (API 키 필요)

