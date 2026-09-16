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
