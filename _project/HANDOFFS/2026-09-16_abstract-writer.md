# 인수인계 2026-09-16 — abstract-writer v0.1.0

## 무엇을 만들었나

"추상적이지만 깊이 있는 글"을 쓰는 프로그램. 위치: `outputs/abstract-writer/`.
주제 하나 → 발굴(질문·구별·긴장·닻·결과·전환) → 작성 → 린트+모델 감사 → 수정 → Markdown 한 편.

핵심 아이디어는 `outputs/abstract-writer/METHOD.md`에 있다. 요지: 깊이는 큰 단어가 아니라
**구별**("A가 아니라 B")과 **닻**(주장을 흔들 수 있는 구체)과 **긴장**(덮지 않고 놓기)과 **전환**(요약 아닌 결말)에서 온다.

## 어떻게 확인하나

```bash
cd outputs/abstract-writer
python3 -m unittest discover -s tests -v          # 42 tests OK
python3 -m abstract_writer "기다림" --provider mock  # 오프라인 엔드투엔드
python3 -m abstract_writer --lint examples/waiting_ko.md
```

실제 모델:
```bash
export ABSTRACT_WRITER_API_KEY=...       # OpenRouter 등 chat-completions 호환 키
python3 -m abstract_writer "기다림" --trace trace.json --out piece.md
```

## 무엇이 검증되지 않았나

- 실제 모델이 만든 글의 품질. 샌드박스에 API 키가 없어 mock으로만 돌렸다.
- `pip install -e .`와 `hermes -q "Use the abstract-deep-writing skill ..."` 엔드투엔드.
- research 문서의 출처 링크.

## 다음 한 가지 행동

Mac에서 API 키를 설정하고 실제 모델로 `"기다림"` 한 편을 생성해 `--trace`와 함께 `outputs/abstract-writer/examples/`에 저장하고,
감사 점수·린트 결과·본인 판단을 `evaluations/2026-09-xx_abstract-writer-model.md`에 기록한다 (ABSTRACT_WRITER_API_KEY 필요).

## 손대지 말아야 할 것

`METHOD.md` §8 대조 예시는 린트 임계값의 보정 기준이자 테스트 고정값이다. 바꾸려면 `tests/test_lint.py`를 같이 바꾼다.
