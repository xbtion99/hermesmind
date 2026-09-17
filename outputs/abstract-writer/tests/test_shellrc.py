import tempfile
import unittest
from pathlib import Path

from abstract_writer.shellrc import BEGIN, END, install, main, render_block, strip_block

LEGACY = """export PATH=$PATH:~/bin
alias ll='ls -l'

# abstract-writer
[ -f "/home/x/.abstract-writer.env" ] && . "/home/x/.abstract-writer.env"
aw() { PYTHONPATH="/old" "/old/python" -m abstract_writer "$@"; }
"""

BLOCK = render_block("/HERE", "/PY", "/ENV")


class RenderTests(unittest.TestCase):
    def test_block_has_markers_and_both_entry_points(self):
        self.assertTrue(BLOCK.startswith(BEGIN))
        self.assertIn(END, BLOCK)
        self.assertIn("aw()", BLOCK)
        self.assertIn("command_not_found_handle()", BLOCK)
        self.assertIn("--shell-phrase", BLOCK)

    def test_paths_are_substituted(self):
        self.assertIn('PYTHONPATH="/HERE"', BLOCK)
        self.assertIn('"/PY" -m abstract_writer', BLOCK)
        self.assertIn('[ -f "/ENV" ]', BLOCK)

    def test_block_is_valid_bash(self):
        import subprocess
        with tempfile.NamedTemporaryFile("w", suffix=".sh", encoding="utf-8", delete=False) as fh:
            fh.write(BLOCK)
            path = fh.name
        proc = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)


class StripTests(unittest.TestCase):
    def test_removes_legacy_block_and_keeps_user_lines(self):
        out = strip_block(LEGACY)
        self.assertNotIn("aw()", out)
        self.assertNotIn("/old", out)
        self.assertIn("alias ll=", out)
        self.assertIn("export PATH", out)

    def test_removes_managed_block(self):
        text = "user line\n\n" + BLOCK
        out = strip_block(text)
        self.assertNotIn(BEGIN, out)
        self.assertIn("user line", out)

    def test_leaves_unrelated_text_alone(self):
        text = "alias g=git\nexport EDITOR=nano\n"
        self.assertEqual(strip_block(text), text)


class InstallTests(unittest.TestCase):
    def test_upgrade_from_legacy_leaves_one_block(self):
        out = install(LEGACY, BLOCK)
        self.assertEqual(out.count(BEGIN), 1)
        self.assertNotIn("/old", out)
        self.assertIn("alias ll=", out)
        self.assertIn("command_not_found_handle", out)

    def test_second_install_is_idempotent(self):
        once = install(LEGACY, BLOCK)
        twice = install(once, BLOCK)
        self.assertEqual(once, twice)
        self.assertEqual(twice.count(BEGIN), 1)

    def test_install_into_empty_file(self):
        out = install("", BLOCK)
        self.assertEqual(out, BLOCK)

    def test_changing_paths_replaces_the_old_ones(self):
        first = install("", render_block("/A", "/PYA", "/ENVA"))
        second = install(first, render_block("/B", "/PYB", "/ENVB"))
        self.assertNotIn("/PYA", second)
        self.assertIn("/PYB", second)
        self.assertEqual(second.count(BEGIN), 1)


class MainTests(unittest.TestCase):
    def _run(self, rc: Path) -> int:
        return main(["--rc", str(rc), "--here", "/HERE", "--python", "/PY", "--env-file", "/ENV"])

    def test_creates_file_and_reports_unchanged_on_rerun(self):
        with tempfile.TemporaryDirectory() as d:
            rc = Path(d) / ".bashrc"
            self.assertEqual(self._run(rc), 0)
            first = rc.read_text(encoding="utf-8")
            self.assertIn(BEGIN, first)
            self.assertEqual(self._run(rc), 0)
            self.assertEqual(rc.read_text(encoding="utf-8"), first)

    def test_backs_up_before_changing(self):
        with tempfile.TemporaryDirectory() as d:
            rc = Path(d) / ".bashrc"
            rc.write_text(LEGACY, encoding="utf-8")
            self._run(rc)
            backup = rc.with_suffix(rc.suffix + ".abstract-writer.bak")
            self.assertTrue(backup.exists())
            self.assertEqual(backup.read_text(encoding="utf-8"), LEGACY)

    def test_no_backup_when_nothing_changes(self):
        with tempfile.TemporaryDirectory() as d:
            rc = Path(d) / ".bashrc"
            self._run(rc)
            backup = rc.with_suffix(rc.suffix + ".abstract-writer.bak")
            backup.unlink(missing_ok=True)
            self._run(rc)
            self.assertFalse(backup.exists())


if __name__ == "__main__":
    unittest.main()
