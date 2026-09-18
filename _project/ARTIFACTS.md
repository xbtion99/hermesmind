# ARTIFACTS

| 날짜 | 경로 (프로젝트 기준 상대경로) | 설명 | 검증 결과 |
|---|---|---|---|
| 2026-09-16 | outputs/abstract-writer/README.md | 설치·설정·사용법·구조·한계 | 내용 대조 [샌드박스 검증됨] |
| 2026-09-16 | outputs/abstract-writer/METHOD.md | 방법론 정본 | 대조 예시가 lint 테스트로 고정됨 [샌드박스 검증됨] |
| 2026-09-16 | outputs/abstract-writer/abstract_writer/{cli,pipeline,prompts,lint,providers}.py | 프로그램 본체 | unittest 42 OK, pytest 42 passed, ruff 통과 [샌드박스 검증됨] |
| 2026-09-16 | outputs/abstract-writer/tests/ | 오프라인 테스트 (lint, pipeline, cli) | 42/42 통과 [샌드박스 검증됨] |
| 2026-09-16 | outputs/abstract-writer/examples/waiting_ko.md | 손으로 쓴 참조 예시(목표 수준) | `--lint` 지적 0건 [샌드박스 검증됨] |
| 2026-09-16 | outputs/abstract-writer/pyproject.toml | `pip install -e .` → `abstract-writer` 명령 | 설치 미실행 [Mac 재실행 필요] |
| 2026-09-16 | skills/creative/abstract-deep-writing/SKILL.md | Hermes 스킬 | 프론트매터 YAML 파싱 확인. `hermes -q "..."` 엔드투엔드 미실행 [Mac 재실행 필요] |
| 2026-09-16 | research/2026-09-16_abstract-deep-writing.md | 방법론 근거 | 출처 링크 미검증 |
| 2026-09-16 | evaluations/2026-09-16_abstract-writer.md | 첫 평가 | 실제 모델 품질 미측정 [Mac·API 키 필요] |
| 2026-09-16 | outputs/abstract-writer/termux-setup.sh | 안드로이드(Termux) 1회 설정 스크립트 | bash -n 통과, 임시 HOME으로 2회 실행해 멱등성·alias 동작 확인 [샌드박스 검증됨]. 실제 Termux 미실행 [Android 재실행 필요] |
| 2026-09-17 | outputs/abstract-writer/examples/waiting_ko_compressed.md | 함축 레지스터 참조 예시 (330자, 설명 표지 0) | compressed 린트 통과 [샌드박스 검증됨] |
| 2026-09-17 | outputs/abstract-writer/abstract_writer/{prompts,lint,pipeline,cli,providers}.py | --register plain/compressed 추가, scaffold_density 검사 | unittest 60 OK, ruff 통과 [샌드박스 검증됨] |
| 2026-09-17 | outputs/abstract-writer/abstract_writer/phrase.py | "기다림 함축 짧게" → 주제 + 옵션 파서 | unittest 79 OK [샌드박스 검증됨] |
| 2026-09-17 | outputs/abstract-writer/termux-setup.sh | command_not_found_handle 훅 추가 | 임시 HOME에서 5개 경우 실측 [샌드박스 검증됨], 실제 Termux 미검증 [Android 필요] |
| 2026-09-17 | outputs/abstract-writer/abstract_writer/shellrc.py | .bashrc 관리 구간 설치·갱신 | 예전 블록 업그레이드·멱등성·백업 실측, unittest 92 OK [샌드박스 검증됨] |
| 2026-09-17 | outputs/abstract-writer/abstract_writer/keys.py | API 키 탐색(환경변수 → 자체 .env → Hermes .env) | 우선순위·직접 읽기·오류 메시지 실측, unittest 107 OK [샌드박스 검증됨] |
| 2026-09-17 | outputs/abstract-writer/abstract_writer/endpoints.py | 키 종류 → 엔드포인트·모델 결정 | 낡은 기본값 상황 포함 실측, unittest 125 OK [샌드박스 검증됨] |
| 2026-09-17 | outputs/abstract-writer (--prompt 모드) | 키 없이 붙여넣기용 프롬프트 출력 | 키·HOME 없는 환경에서 실측, unittest 132 OK [샌드박스 검증됨] |
| 2026-09-17 | outputs/abstract-writer/examples/burgerking_ko.md | --prompt 프롬프트로 받은 첫 실제 산출물 (단상, 1231자) | --lint 지적 0건 [샌드박스 검증됨] |
| 2026-09-17 | evaluations/2026-09-17_first-model-output.md | 프롬프트가 실제 모델에서 작동하는지 첫 평가 | 형식·길이·린트 실측 |
| 2026-09-17 | outputs/abstract-writer (길이·단락 검사) | 브리프 대비 길이·단락 수 검사 + 프롬프트/린트 수치 불변식 | unittest 156 OK [샌드박스 검증됨] |
| 2026-09-18 | evaluations/2026-09-18_repo-suite-baseline.md | 저장소 전체 스위트 main 대비 회귀 여부 | main과 결과 일치, 회귀 없음 [샌드박스 검증됨] |
