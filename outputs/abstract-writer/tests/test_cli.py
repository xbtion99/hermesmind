import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from abstract_writer.cli import main


class CliTests(unittest.TestCase):
    def test_mock_run_prints_piece(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["기다림", "--provider", "mock"])
        self.assertEqual(rc, 0)
        self.assertIn("# 두 종류의 기다림", out.getvalue())
        self.assertIn("[audit]", err.getvalue())

    def test_out_and_trace_files(self):
        with tempfile.TemporaryDirectory() as d:
            piece, trace = Path(d) / "p.md", Path(d) / "t.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rc = main(["waiting", "--provider", "mock", "--lang", "en",
                           "--out", str(piece), "--trace", str(trace), "-q"])
            self.assertEqual(rc, 0)
            self.assertTrue(piece.read_text(encoding="utf-8").startswith("# Two Kinds"))
            data = json.loads(trace.read_text(encoding="utf-8"))
            self.assertEqual(data["seed"], "waiting")
            self.assertEqual(len(data["rounds"]), 2)

    def test_lint_mode_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "bad.md"
            bad.write_text("시간은 흐른다. 존재의 본질을 마주한다. 진정한 자신을 발견한다.", encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                rc = main(["--lint", str(bad), "--json"])
            self.assertEqual(rc, 1)
            self.assertFalse(json.loads(out.getvalue())["passed"])

            good = Path(d) / "good.md"
            good.write_text("버스가 아니라 답장을 기다리는 일. 시간은 줄어드는 것이 아니라 쌓인다.",
                            encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                rc = main(["--lint", str(good)])
            self.assertEqual(rc, 0)

    def test_missing_seed_is_usage_error(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main([]), 2)

    def test_unknown_provider_is_error_not_traceback(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(main(["x", "--provider", "nope"]), 1)
        self.assertIn("unknown provider", err.getvalue())


if __name__ == "__main__":
    unittest.main()
