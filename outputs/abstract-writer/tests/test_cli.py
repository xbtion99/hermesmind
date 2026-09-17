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

    def test_register_flag_changes_output(self):
        outs = {}
        for reg in ("plain", "compressed"):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                rc = main(["기다림", "--provider", "mock", "--register", reg, "-q"])
            self.assertEqual(rc, 0)
            outs[reg] = buf.getvalue()
        self.assertNotEqual(outs["plain"], outs["compressed"])
        self.assertLess(len(outs["compressed"]), len(outs["plain"]))

    def test_lint_mode_honors_register(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "explanatory.md"
            f.write_text(
                "버스가 아니라 답장을 기다린다. 그러니 시계는 소용이 없다. "
                "이것은 방향의 문제이기 때문이다. 다시 말해 길이가 아니다.",
                encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--lint", str(f), "--lang", "ko"]), 0)
            out = io.StringIO()
            with redirect_stdout(out):
                rc = main(["--lint", str(f), "--lang", "ko", "--register", "compressed", "--json"])
            self.assertEqual(rc, 1)
            report = json.loads(out.getvalue())
            self.assertEqual(report["register"], "compressed")
            self.assertTrue(any("scaffolding" in f for f in report["flags"]))

    def test_bad_register_is_argparse_error(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(["기다림", "--register", "함축"])

    def test_phrase_applies_modifiers(self):
        outs = {}
        for phrase in ("기다림", "기다림 함축"):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                rc = main(["--phrase", phrase, "--provider", "mock", "-q"])
            self.assertEqual(rc, 0, phrase)
            outs[phrase] = buf.getvalue()
        self.assertLess(len(outs["기다림 함축"]), len(outs["기다림"]))

    def test_phrase_modifier_reaches_the_trace(self):
        with tempfile.TemporaryDirectory() as d:
            trace = Path(d) / "t.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                main(["--phrase", "첫눈 단상 짧게", "--provider", "mock", "-q",
                      "--trace", str(trace)])
            opts = json.loads(trace.read_text(encoding="utf-8"))["options"]
            self.assertEqual(opts["form"], "fragments")
            self.assertEqual(opts["length"], "short")
            self.assertEqual(json.loads(trace.read_text(encoding="utf-8"))["seed"], "첫눈")

    def test_shell_phrase_exits_127_silently_without_hangul(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(["--shell-phrase", "gti status", "--provider", "mock"])
        self.assertEqual(rc, 127)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "")

    def test_shell_phrase_writes_when_korean(self):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            rc = main(["--shell-phrase", "기다림 함축", "--provider", "mock", "-q"])
        self.assertEqual(rc, 0)
        self.assertIn("# 두 종류의 기다림", out.getvalue())

    def test_empty_phrase_is_usage_error(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--phrase", "   ", "--provider", "mock"]), 2)

    def test_provider_env_var_is_the_default(self):
        import os
        old = os.environ.get("ABSTRACT_WRITER_PROVIDER")
        os.environ["ABSTRACT_WRITER_PROVIDER"] = "mock"
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["기다림", "-q"]), 0)
        finally:
            if old is None:
                os.environ.pop("ABSTRACT_WRITER_PROVIDER", None)
            else:
                os.environ["ABSTRACT_WRITER_PROVIDER"] = old

    def test_prompt_mode_needs_no_key_and_no_network(self):
        import os
        saved = dict(os.environ)
        try:
            for v in ("ABSTRACT_WRITER_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY"):
                os.environ.pop(v, None)
            os.environ["HOME"] = "/nonexistent-home-for-this-test"
            out = io.StringIO()
            with redirect_stdout(out), redirect_stderr(io.StringIO()):
                rc = main(["저녁", "--prompt"])
            self.assertEqual(rc, 0)
            text = out.getvalue()
            self.assertIn("저녁", text)
            self.assertIn("여섯 원리", text)
            self.assertNotIn("API 키가 없다", text)
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_prompt_mode_carries_the_register(self):
        outs = {}
        for reg in ("plain", "compressed"):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                main(["저녁", "--prompt", "--register", reg])
            outs[reg] = buf.getvalue()
        self.assertIn("설명을 허용한다", outs["plain"])
        self.assertIn("논리를 잇는 접속사", outs["compressed"])

    def test_prompt_mode_via_a_bare_phrase(self):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            rc = main(["--shell-phrase", "저녁 프롬프트 함축"])
        self.assertEqual(rc, 0)
        self.assertIn("논리를 잇는 접속사", out.getvalue())
        self.assertIn("저녁", out.getvalue())

    def test_prompt_mode_writes_to_out(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "p.txt"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rc = main(["저녁", "--prompt", "--out", str(path), "-q"])
            self.assertEqual(rc, 0)
            self.assertIn("저녁", path.read_text(encoding="utf-8"))

    def test_prompt_mode_english(self):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            main(["evening", "--prompt", "--lang", "en"])
        self.assertIn("Six principles", out.getvalue())

    def _no_key_env(self, home):
        import os
        saved = dict(os.environ)
        for v in ("ABSTRACT_WRITER_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY",
                  "ABSTRACT_WRITER_PROVIDER", "HERMES_HOME"):
            os.environ.pop(v, None)
        os.environ["HOME"] = home
        return saved

    def test_phrase_without_a_key_falls_back_to_the_prompt(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            saved = self._no_key_env(d)
            try:
                out, err = io.StringIO(), io.StringIO()
                with redirect_stdout(out), redirect_stderr(err):
                    rc = main(["--shell-phrase", "버거킹 단상"])
                self.assertEqual(rc, 0)
                self.assertIn("## 주제", out.getvalue())
                self.assertIn("버거킹", out.getvalue())
                self.assertIn("단상", out.getvalue())
                self.assertIn("키 없음", err.getvalue())
            finally:
                os.environ.clear()
                os.environ.update(saved)

    def test_spelled_out_command_without_a_key_still_fails(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            saved = self._no_key_env(d)
            try:
                err = io.StringIO()
                with redirect_stdout(io.StringIO()), redirect_stderr(err):
                    rc = main(["버거킹"])
                self.assertEqual(rc, 1)
                self.assertIn("--prompt", err.getvalue())
                self.assertIn("프롬프트", err.getvalue())
            finally:
                os.environ.clear()
                os.environ.update(saved)

    def test_phrase_with_a_key_does_not_fall_back(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            saved = self._no_key_env(d)
            try:
                os.environ["ABSTRACT_WRITER_PROVIDER"] = "mock"
                out, err = io.StringIO(), io.StringIO()
                with redirect_stdout(out), redirect_stderr(err):
                    rc = main(["--shell-phrase", "기다림", "-q"])
                self.assertEqual(rc, 0)
                self.assertIn("# 두 종류의 기다림", out.getvalue())
                self.assertNotIn("## 주제", out.getvalue())
            finally:
                os.environ.clear()
                os.environ.update(saved)

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
