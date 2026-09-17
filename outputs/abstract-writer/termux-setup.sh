#!/data/data/com.termux/files/usr/bin/env bash
# One-shot setup for running abstract-writer on an Android phone under Termux.
#
#   bash termux-setup.sh
#
# It installs python, adds an `aw` alias, and creates ~/.abstract-writer.env
# for your API key. It never writes the key itself — you paste that in once.
# Re-running it is safe; every step checks before acting.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$HOME/.abstract-writer.env"
RC="$HOME/.bashrc"

say() { printf '\n== %s\n' "$1"; }

if [ ! -d "$HERE/abstract_writer" ]; then
    echo "error: run this from inside the abstract-writer directory" >&2
    exit 1
fi

# ── 1. Python ───────────────────────────────────────────────────────────────
say "Python"
if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
    if command -v pkg >/dev/null 2>&1; then
        echo "installing python via pkg…"
        pkg install -y python
    else
        echo "error: no python and no pkg. Install Python 3.10+ first." >&2
        exit 1
    fi
fi
PY="$(command -v python3 || command -v python)"
"$PY" - <<'PYEOF'
import sys
if sys.version_info < (3, 10):
    sys.exit(f"error: Python 3.10+ required, found {sys.version.split()[0]}")
print(f"ok: {sys.version.split()[0]}")
PYEOF

# ── 2. Smoke test, offline ──────────────────────────────────────────────────
say "Offline check (no API key needed)"
cd "$HERE"
"$PY" -m abstract_writer "기다림" --provider mock -q >/dev/null
echo "ok: the pipeline runs"

# ── 3. API key file ─────────────────────────────────────────────────────────
say "API key"
if [ -f "$ENV_FILE" ]; then
    echo "ok: $ENV_FILE already exists (left untouched)"
else
    cat > "$ENV_FILE" <<'ENVEOF'
# Paste your key after the = and save. Any chat-completions endpoint works.
export ABSTRACT_WRITER_API_KEY=
export ABSTRACT_WRITER_BASE_URL=https://openrouter.ai/api/v1
export ABSTRACT_WRITER_MODEL=anthropic/claude-sonnet-4.5
ENVEOF
    chmod 600 "$ENV_FILE"
    echo "created $ENV_FILE — open it and paste your key:"
    echo "    nano $ENV_FILE"
fi

# ── 4. Shell wiring ─────────────────────────────────────────────────────────
say "Shell setup"
touch "$RC"
if grep -q "abstract-writer.env" "$RC" 2>/dev/null; then
    echo "ok: $RC already wired (left untouched)"
else
    cat >> "$RC" <<RCEOF

# abstract-writer
[ -f "$ENV_FILE" ] && . "$ENV_FILE"
aw() { PYTHONPATH="$HERE" "$PY" -m abstract_writer "\$@"; }

# Type a Korean word on its own and it is written about. Anything that is
# plain ASCII falls through to the shell's usual "command not found", so a
# mistyped command still behaves normally.
command_not_found_handle() {
    case "\$*" in
        *[!\ -~]*)
            PYTHONPATH="$HERE" "$PY" -m abstract_writer --shell-phrase "\$*"
            _aw_rc=\$?
            if [ "\$_aw_rc" -ne 127 ]; then
                return "\$_aw_rc"
            fi
            ;;
    esac
    if [ -x /data/data/com.termux/files/usr/libexec/termux/command-not-found ]; then
        /data/data/com.termux/files/usr/libexec/termux/command-not-found "\$1"
    else
        echo "bash: \$1: command not found" >&2
    fi
    return 127
}
RCEOF
    echo "added the 'aw' command and the bare-word hook to $RC"
fi

say "Done"
cat <<'DONEEOF'
Open a new Termux session (or run: source ~/.bashrc), then just type a word:

    기다림                               write a piece about it
    기다림 함축                          the implicit version
    첫눈 단상 짧게                       fragments, short

Modifiers, all optional, in any order after the topic:
    함축 / 압축, 설명 · 단상, 편지, 에세이 · 짧게, 길게

The full command form still works when you need flags:

    aw "기다림" --out ~/piece.md         save it to a file
    aw --lint ~/piece.md                 check a draft (no key, no network)

Mistyped ASCII commands are untouched: `gti status` still says command not found.

To save straight into your phone's shared storage so other apps can open it,
run `termux-setup-storage` once, then use --out ~/storage/shared/Documents/piece.md
DONEEOF
