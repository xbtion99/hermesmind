"""Install or upgrade the shell block in ~/.bashrc.

The block is delimited by markers so a later run replaces it instead of
appending a second copy. The first released version had no markers, so this
also recognizes that shape and removes it before writing the new block.

    python -m abstract_writer.shellrc --rc ~/.bashrc --here /path --python /usr/bin/python \\
        --env-file ~/.abstract-writer.env
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BEGIN = "# >>> abstract-writer >>>"
END = "# <<< abstract-writer <<<"

# The marker-delimited block, including any blank line right before it.
_MANAGED = re.compile(
    rf"\n*{re.escape(BEGIN)}\n.*?{re.escape(END)}\n?",
    re.DOTALL,
)

# The first release appended a bare "# abstract-writer" comment followed by the
# env source line and the aw() function, optionally a command_not_found_handle.
_LEGACY = re.compile(
    r"\n*# abstract-writer\n"
    r"(?:[^\n]*\n)*?"           # env source line, blank lines, comments
    r"aw\(\)[^\n]*\n"           # the one-line aw function
    r"(?:"                      # optionally the handler that followed it
    r"(?:[^\n]*\n)*?"
    r"\}\n"
    r")?",
)


def render_block(here: str, python: str, env_file: str) -> str:
    """The managed block, ready to append."""
    return f"""{BEGIN}
# Written by abstract-writer's termux-setup.sh. Re-running the script replaces
# everything between these markers, so edit elsewhere if you want it kept.
[ -f "{env_file}" ] && . "{env_file}"
aw() {{ PYTHONPATH="{here}" "{python}" -m abstract_writer "$@"; }}

# Type a Korean topic on its own and it gets written about. Plain ASCII falls
# through to the shell's usual "command not found", so mistyped commands and
# the API bill are both left alone.
command_not_found_handle() {{
    case "$*" in
        *[!\\ -~]*)
            PYTHONPATH="{here}" "{python}" -m abstract_writer --shell-phrase "$*"
            _aw_rc=$?
            if [ "$_aw_rc" -ne 127 ]; then
                return "$_aw_rc"
            fi
            ;;
    esac
    if [ -x /data/data/com.termux/files/usr/libexec/termux/command-not-found ]; then
        /data/data/com.termux/files/usr/libexec/termux/command-not-found "$1"
    else
        echo "bash: $1: command not found" >&2
    fi
    return 127
}}
{END}
"""


def strip_block(rc_text: str) -> str:
    """Remove any block this tool wrote before, old shape or new."""
    rc_text = _MANAGED.sub("\n", rc_text)
    rc_text = _LEGACY.sub("\n", rc_text)
    return rc_text


def install(rc_text: str, block: str) -> str:
    body = strip_block(rc_text).rstrip("\n")
    if body:
        return body + "\n\n" + block
    return block


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="abstract_writer.shellrc")
    p.add_argument("--rc", required=True, type=Path)
    p.add_argument("--here", required=True)
    p.add_argument("--python", required=True)
    p.add_argument("--env-file", required=True)
    args = p.parse_args(argv)

    rc_text = args.rc.read_text(encoding="utf-8") if args.rc.exists() else ""
    block = render_block(args.here, args.python, args.env_file)
    new_text = install(rc_text, block)
    if new_text == rc_text:
        print("unchanged")
        return 0
    if args.rc.exists():
        backup = args.rc.with_suffix(args.rc.suffix + ".abstract-writer.bak")
        backup.write_text(rc_text, encoding="utf-8")
        print(f"backup: {backup}")
    args.rc.write_text(new_text, encoding="utf-8")
    print("installed" if BEGIN not in rc_text and "# abstract-writer" not in rc_text else "upgraded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
