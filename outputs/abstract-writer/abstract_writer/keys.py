"""Find the API key without making the user re-source their shell.

On a phone the shortest path matters. Someone edits ~/.abstract-writer.env in
nano and runs the program in the same session; the shell never re-read the
file, so the environment variable is still empty. So the files are read
directly, in this order:

1. ABSTRACT_WRITER_API_KEY, then OPENROUTER_API_KEY, then OPENAI_API_KEY,
   from the environment. An explicit export always wins.
2. ~/.abstract-writer.env, this program's own key file.
3. $HERMES_HOME/.env (default ~/.hermes/.env), where Hermes keeps its keys,
   so a phone that already runs Hermes needs no second copy of the key.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import NamedTuple

ENV_VARS = ("ABSTRACT_WRITER_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY")


def own_env_file() -> Path:
    override = os.environ.get("ABSTRACT_WRITER_ENV_FILE")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".abstract-writer.env"


def hermes_env_file() -> Path:
    home = os.environ.get("HERMES_HOME")
    base = Path(home).expanduser() if home else Path.home() / ".hermes"
    return base / ".env"


def read_dotenv(path: Path) -> dict[str, str]:
    """Parse a KEY=value file. Tolerates `export`, quotes, comments, blanks."""
    values: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return values
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        line = line.removeprefix("export ").lstrip()
        name, _, value = line.partition("=")
        name = name.strip()
        if not name:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if value:
            values[name] = value
    return values


class FoundKey(NamedTuple):
    key: str | None
    origin: str   # human-readable: "$VAR" or "/path (VAR)"
    var: str | None   # which variable name held it, for endpoint inference


def find_api_key() -> FoundKey:
    """Where the key is, and which variable name held it."""
    for var in ENV_VARS:
        value = os.environ.get(var)
        if value:
            return FoundKey(value, f"${var}", var)
    for path in (own_env_file(), hermes_env_file()):
        if not path.is_file():
            continue
        values = read_dotenv(path)
        for var in ENV_VARS:
            if values.get(var):
                return FoundKey(values[var], f"{path} ({var})", var)
    return FoundKey(None, "nowhere", None)


def missing_key_message() -> str:
    own = own_env_file()
    if own.is_file():
        where = f"    nano {own}\n    ABSTRACT_WRITER_API_KEY= 뒤에 키를 붙여넣고 저장하면 된다."
    else:
        where = (
            f"    {own} 파일을 만들고 다음 한 줄을 넣는다.\n"
            f"    ABSTRACT_WRITER_API_KEY=키"
        )
    return (
        "API 키가 없다.\n"
        f"{where}\n"
        "    다시 로그인하거나 source 할 필요는 없다. 이 파일은 실행할 때마다 직접 읽는다.\n"
        "    OpenRouter 키는 https://openrouter.ai/keys 에서 만든다.\n"
        "    키 없이 동작만 보려면: --provider mock"
    )
