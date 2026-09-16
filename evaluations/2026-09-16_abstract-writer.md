# 2026-09-16 평가: abstract-writer v0.1.0

## 평가 대상

- `outputs/abstract-writer/` (패키지 `abstract_writer` 0.1.0)
- `skills/creative/abstract-deep-writing/SKILL.md` 0.1.0
- 브랜치 `claude/abstract-deep-writing-program-3q05pn`

## 평가 기준

1. 파이프라인이 발굴→작성→검사→수정 순서로 끝까지 돈다.
2. 린트가 `METHOD.md` §8의 대조 예시를 올바르게 가른다 (공허 → 실패, 깊은 → 통과).
3. 모델 응답이 깨졌을 때(JSON 아님, 키 누락) 트레이스백 대신 명확한 오류를 낸다.
4. 저장소 규칙(ruff PLW1514)을 통과한다.
5. 실제 모델로 만든 글이 사람이 보기에 "추상적이지만 깊다".

## 실제 확인 방법과 결과

| 기준 | 방법 | 결과 | 검증 단계 |
|---|---|---|---|
| 1 | `python3 -m abstract_writer "기다림" --provider mock` | 7단계(excavate, compose, lint, audit, revise, lint, audit) 실행 후 accepted | [샌드박스 검증됨] |
| 2 | `tests/test_lint.py` ContrastExampleTests 4건 | 통과. 공허 예시: hollow 2건·구별 0·닻 0으로 실패. 깊은 예시: 지적 없음 | [샌드박스 검증됨] |
| 3 | `tests/test_pipeline.py` StageFailureTests, ValidationTests, `tests/test_cli.py` | 통과. 잘못된 프로바이더·빈 시드·비JSON 응답 모두 종료코드 1과 메시지 | [샌드박스 검증됨] |
| 4 | `ruff check outputs/abstract-writer` | All checks passed | [샌드박스 검증됨] |
| 5 | 실제 모델 호출 | **미검증**. API 키 없음 | [Mac·API 키 필요] |

테스트 총계: `python3 -m unittest discover -s tests` → 42 tests, OK. `python3 -m pytest tests -q -o addopts=""` → 42 passed.

## 통과한 점

- 오프라인으로 전체 파이프라인과 CLI(`--out`, `--trace`, `--lint`, 종료 코드)가 검증된다.
- 린트 임계값이 방법론의 대조 예시에 보정되어 있어, 규칙을 바꾸면 테스트가 바로 깨진다(회귀 방지).
- 감사 점수의 평균을 모델 값 대신 재계산하므로 모델이 자기 점수를 부풀려도 수락 조건이 흔들리지 않는다.

## 발견한 문제와 심각도

| 문제 | 심각도 | 비고 |
|---|---|---|
| 실제 모델 출력 품질 미측정 | 높음 | 프로그램의 존재 이유가 이것. 키 필요 |
| 닻 감지가 단어 목록 기반 → 은유적 구체("무너진 목소리") 미탐 | 중간 | 감사 단계가 보완하지만 `--no-audit` 모드에서는 구멍 |
| 영어 감시 어휘 "true self"가 "true selves"를 못 잡음 | 낮음 | 복수형·활용형 미처리 |
| 프로바이더가 chat-completions 호환만 지원 | 낮음 | Anthropic 네이티브 API 미지원. OpenRouter 경유로 우회 가능 |

## 이전 평가 대비

첫 평가. 비교 대상 없음.

## 다음 개선 우선순위 한 가지

실제 모델로 주제 5개를 돌려 `examples/`에 트레이스와 함께 저장하고, 감사 점수·린트 지적·사람 판단을 한 표로 대조한다 (ABSTRACT_WRITER_API_KEY 필요).
