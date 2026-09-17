"""Model providers.

- OpenAICompatible: any `/chat/completions` endpoint (OpenRouter, Nous Portal,
  OpenAI, local servers, Anthropic's OpenAI-compatible endpoint). Stdlib only.
- MockProvider: deterministic canned answers keyed on the `[STAGE:...]` tag,
  so the whole pipeline runs offline for tests and dry runs.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-sonnet-4.5"


class ProviderError(RuntimeError):
    pass


class Provider(Protocol):
    name: str

    def complete(self, system: str, user: str, *, temperature: float = 0.7,
                 max_tokens: int = 4000) -> str: ...


@dataclass
class OpenAICompatible:
    """Minimal chat-completions client. No SDK dependency."""

    model: str
    base_url: str = DEFAULT_BASE_URL
    api_key: str | None = None
    timeout: float = 120.0
    retries: int = 3
    name: str = "openai"
    calls: int = field(default=0, init=False)

    def complete(self, system: str, user: str, *, temperature: float = 0.7,
                 max_tokens: int = 4000) -> str:
        if not self.api_key:
            raise ProviderError(
                "no API key: set ABSTRACT_WRITER_API_KEY (or OPENROUTER_API_KEY / OPENAI_API_KEY)"
            )
        url = self.base_url.rstrip("/") + "/chat/completions"
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            # OpenRouter attribution headers; harmless elsewhere.
            "HTTP-Referer": "https://github.com/xbtion99/hermesmind",
            "X-Title": "abstract-writer",
        }
        last: Exception | None = None
        for attempt in range(self.retries):
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                self.calls += 1
                return _extract_content(payload)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:500]
                last = ProviderError(f"HTTP {exc.code} from {url}: {detail}")
                if exc.code in (400, 401, 403, 404):
                    raise last from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last = ProviderError(f"request failed: {exc}")
            time.sleep(2 ** attempt)
        raise last or ProviderError("unknown provider failure")


def _extract_content(payload: dict) -> str:
    try:
        choice = payload["choices"][0]
        msg = choice.get("message") or {}
        content = msg.get("content")
        if isinstance(content, list):  # some servers return content parts
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        if not content:
            raise KeyError("empty content")
        return content
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError(f"unexpected response shape: {json.dumps(payload)[:300]}") from exc


# ---------------------------------------------------------------------------
# Mock provider
# ---------------------------------------------------------------------------

_MOCK_MAP_KO = {
    "question": "기다림이 힘든 것은 시간이 길어서인가, 아니면 그 시간이 어느 쪽으로 세어지는지 몰라서인가?",
    "distinctions": [
        {"a": "끝이 정해진 기다림", "b": "끝이 상대에게 달린 기다림",
         "why_confused": "둘 다 '기다린다'는 같은 동사로 불리기 때문"},
        {"a": "시간이 줄어드는 기다림", "b": "시간이 쌓이는 기다림",
         "why_confused": "시계는 두 경우에 똑같이 움직이기 때문"},
    ],
    "tension": {"claim_1": "기다림은 아무것도 하지 않는 시간이다",
                "claim_2": "기다림은 가장 많은 일이 일어나는 시간이다",
                "where_they_collide": "손은 멈춰 있는데 마음은 계속 계산하고 있는 순간"},
    "anchors": ["정류장에서 전광판의 남은 분을 보는 사람", "보낸 메시지의 '읽음' 표시를 확인하는 손가락"],
    "stake": "'기다리기 힘들다'는 말을 들었을 때, 얼마나 오래인지 대신 어느 쪽 기다림인지 묻게 된다",
    "turn": "길이가 아니라 방향이었다.",
}

_MOCK_PIECE_KO = """# 두 종류의 기다림

기다림에는 두 종류가 있다. 하나는 버스를 기다리는 것처럼 끝이 정해진 기다림이고, 다른 하나는 답장을 기다리는 것처럼 끝이 상대에게 달린 기다림이다. 우리는 둘을 같은 동사로 부르지만, 정류장에서 전광판의 남은 분을 보는 사람과 보낸 메시지의 읽음 표시를 확인하는 손가락은 서로 다른 일을 하고 있다.

첫 번째 기다림에서 시간은 줄어든다. 3분이 2분이 되고, 2분이 1분이 된다. 시계가 하는 일과 내가 하는 일이 같은 방향이다. 두 번째 기다림에서 시간은 쌓인다. 한 시간이 지났다는 것은 한 시간만큼 가까워졌다는 뜻이 아니라, 한 시간만큼의 침묵이 더 생겼다는 뜻이다.

기다림은 아무것도 하지 않는 시간이라고들 한다. 그런데 손은 멈춰 있는데 마음은 쉬지 않고 계산하는 순간이 있다. 두 문장은 같은 순간을 가리키면서 충돌한다. 충돌은 '기다림'이라는 단어가 몸의 상태와 마음의 상태를 한꺼번에 부르기 때문에 생긴다. 몸은 정말로 아무것도 하지 않는다. 마음은 그 시간이 어느 쪽으로 세어지고 있는지 알아내려고 애쓴다.

그러니 누군가 기다리기 힘들다고 말할 때, 얼마나 오래 기다렸는지 묻는 것은 잘못된 질문이다. 물어야 할 것은 그 기다림의 끝이 누구에게 있는가이다. 힘든 것은 길이가 아니라 방향이었다."""

_MOCK_PIECE_KO_COMPRESSED = """# 두 종류의 기다림

기다림에는 두 종류가 있다. 버스는 끝이 정해져 있다. 답장은 끝이 상대에게 있다.

전광판의 숫자가 줄어든다. 3분, 2분, 1분. 시계와 내가 같은 방향으로 간다.

읽음 표시가 없는 화면은 줄어들지 않는다. 손가락이 화면을 다시 켠다. 한 시간이 지나면 한 시간만큼의 침묵이 늘어난다.

기다림은 아무것도 하지 않는 시간이라고들 한다. 발은 멈춰 있고 눈은 숫자를 세고 있다. 한 단어가 몸과 마음을 한꺼번에 부른다.

누가 기다리기 힘들다고 말한다. 정류장에서든 방에서든, 얼마나 오래인지는 답이 아니다. 그 끝이 누구에게 있는가.

길이가 아니라 방향이었다."""

_MOCK_PIECE_EN_COMPRESSED = """# Two Kinds of Waiting

There are two kinds of waiting. A bus has a fixed end. A reply has an end that belongs to someone else.

The number on the display drops. Three minutes, two, one. The clock and I run the same way.

A screen with no read receipt does not drop. A thumb wakes it again. An hour passing adds an hour of silence.

Waiting is time in which nothing happens, people say. The feet are still and the eyes are counting the display.
One word calls the body and the mind at once.

Someone says waiting is hard. At the stop or in the room, how long is not the answer. Whose the end is.

It was never the length."""

_MOCK_MAP_EN = {
    "question": "Is waiting hard because the time is long, or because we do not know which way it is being counted?",
    "distinctions": [
        {"a": "waiting with a fixed end", "b": "waiting whose end belongs to someone else",
         "why_confused": "both are called by the same verb"},
        {"a": "time that is subtracted", "b": "time that accumulates",
         "why_confused": "the clock moves the same way in both"},
    ],
    "tension": {"claim_1": "Waiting is time in which nothing happens",
                "claim_2": "Waiting is the time in which the most happens",
                "where_they_collide": "the moment the hands are still and the mind will not stop counting"},
    "anchors": ["a person at a bus stop watching the minutes on the display", "a thumb checking whether a message has been read"],
    "stake": "when someone says waiting is hard, you ask which kind, not how long",
    "turn": "It was never the length. It was the direction.",
}

_MOCK_PIECE_EN = """# Two Kinds of Waiting

There are two kinds of waiting. One has a fixed end, like waiting for a bus; the other has an end that belongs to someone else, like waiting for a reply. We call both by the same verb, but the person at the stop watching the minutes on the display and the thumb checking whether a message has been read are not doing the same thing.

In the first kind, time is subtracted. Three minutes becomes two, two becomes one. What the clock does and what I do point the same way. In the second kind, time accumulates. An hour passing does not mean an hour closer; it means an hour more of silence, added to the pile.

We say waiting is time in which nothing happens. Yet there is a moment when the hands are still and the mind will not stop counting. The two sentences describe the same moment and collide. They collide because the word covers the body and the mind at once. The body really does nothing. The mind is working out which way the time is being counted.

So when someone says waiting is hard, asking how long is the wrong question. The question is whose the end is. It was never the length. It was the direction."""


@dataclass
class MockProvider:
    """Canned, stage-keyed responses. The first audit returns 'revise' so the
    loop is exercised; later audits return 'pass'."""

    name: str = "mock"
    calls: int = field(default=0, init=False)
    audits: int = field(default=0, init=False)
    log: list[tuple[str, str]] = field(default_factory=list)

    def complete(self, system: str, user: str, *, temperature: float = 0.7,
                 max_tokens: int = 4000) -> str:
        self.calls += 1
        stage = system.split("]", 1)[0].removeprefix("[STAGE:") if system.startswith("[STAGE:") else "unknown"
        lang = "ko" if "Write in Korean" in system or "values in Korean" in system else "en"
        register = "compressed" if "[REGISTER:compressed]" in system else "plain"
        self.log.append((stage, lang))
        if stage == "excavate":
            return json.dumps(_MOCK_MAP_KO if lang == "ko" else _MOCK_MAP_EN, ensure_ascii=False)
        if stage == "compose":
            if register == "compressed":
                return _MOCK_PIECE_KO_COMPRESSED if lang == "ko" else _MOCK_PIECE_EN_COMPRESSED
            return _MOCK_PIECE_KO if lang == "ko" else _MOCK_PIECE_EN
        if stage == "audit":
            self.audits += 1
            if self.audits == 1:
                return json.dumps({
                    "scores": {"distinction": 8, "anchor": 7, "tension": 6, "stake": 7, "turn": 8, "hollow": 10},
                    "overall": 7.67,
                    "issues": [{"where": "두 문장은 같은 순간을 가리키면서 충돌한다." if lang == "ko" else "The two sentences describe the same moment and collide.",
                                "problem": "the collision is announced, not shown",
                                "fix": "add one concrete beat before naming the collision"}],
                    "verdict": "revise",
                }, ensure_ascii=False)
            return json.dumps({
                "scores": {"distinction": 9, "anchor": 8, "tension": 8, "stake": 8, "turn": 9, "hollow": 10},
                "overall": 8.67, "issues": [], "verdict": "pass",
            })
        if stage == "revise":
            if register == "compressed":
                # A compressed revise tightens rather than adds.
                if lang == "ko":
                    return _MOCK_PIECE_KO_COMPRESSED.replace(
                        "정류장에서든 방에서든, 얼마나 오래인지는 답이 아니다.",
                        "정류장에서든 방에서든. 얼마나 오래인지는 답이 아니다.")
                return _MOCK_PIECE_EN_COMPRESSED.replace(
                    "At the stop or in the room, how long is not the answer.",
                    "At the stop, in the room. How long is not the answer.")
            # Apply the one fix the first audit asked for, so tests can see a change.
            if lang == "ko":
                return _MOCK_PIECE_KO.replace(
                    "두 문장은 같은 순간을 가리키면서 충돌한다.",
                    "전광판 앞에서 발은 멈춰 있고 눈은 숫자를 세고 있다. 두 문장은 같은 순간을 가리키면서 충돌한다.")
            return _MOCK_PIECE_EN.replace(
                "The two sentences describe the same moment and collide.",
                "At the stop the feet are still and the eyes are counting the display. The two sentences describe the same moment and collide.")
        return "{}"


def make_provider(name: str = "openai", *, model: str | None = None, base_url: str | None = None,
                  api_key: str | None = None) -> Provider:
    name = (name or "openai").lower()
    if name == "mock":
        return MockProvider()
    if name in ("openai", "openrouter", "compatible"):
        return OpenAICompatible(
            model=model or os.environ.get("ABSTRACT_WRITER_MODEL", DEFAULT_MODEL),
            base_url=base_url or os.environ.get("ABSTRACT_WRITER_BASE_URL", DEFAULT_BASE_URL),
            api_key=api_key
            or os.environ.get("ABSTRACT_WRITER_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("OPENAI_API_KEY"),
        )
    raise ProviderError(f"unknown provider: {name}")
