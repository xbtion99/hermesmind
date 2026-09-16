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
