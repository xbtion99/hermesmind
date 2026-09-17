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

