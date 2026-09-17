import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from abstract_writer.keys import (
    ENV_VARS,
    find_api_key,
    hermes_env_file,
    missing_key_message,
    own_env_file,
    read_dotenv,
)


@contextmanager
def clean_env(**overrides):
    saved = dict(os.environ)
    for var in (*ENV_VARS, "ABSTRACT_WRITER_ENV_FILE", "HERMES_HOME", "HOME"):
        os.environ.pop(var, None)
    os.environ.update({k: v for k, v in overrides.items() if v is not None})
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)


class ReadDotenvTests(unittest.TestCase):
    def _write(self, d, text):
        p = Path(d) / "f.env"
        p.write_text(text, encoding="utf-8")
        return p

    def test_plain_and_export_and_quotes(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._write(d, 'A=1\nexport B=2\nC="3"\nD=\'4\'\n')
            self.assertEqual(read_dotenv(p), {"A": "1", "B": "2", "C": "3", "D": "4"})

    def test_comments_blanks_and_empty_values_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._write(d, "# note\n\nA=\nB=ok\nnot a pair\n")
            self.assertEqual(read_dotenv(p), {"B": "ok"})

    def test_value_containing_equals(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._write(d, "A=sk-a=b=c\n")
            self.assertEqual(read_dotenv(p)["A"], "sk-a=b=c")

    def test_missing_file_is_empty(self):
        self.assertEqual(read_dotenv(Path("/nonexistent/none.env")), {})


class FindApiKeyTests(unittest.TestCase):
    def test_environment_beats_files(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".abstract-writer.env").write_text("ABSTRACT_WRITER_API_KEY=from-file\n",
                                                       encoding="utf-8")
            with clean_env(HOME=d, ABSTRACT_WRITER_API_KEY="from-env"):
                key, where = find_api_key()
                self.assertEqual(key, "from-env")
                self.assertEqual(where, "$ABSTRACT_WRITER_API_KEY")

    def test_own_file_is_read_without_sourcing(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".abstract-writer.env").write_text(
                "export ABSTRACT_WRITER_API_KEY=from-own\n", encoding="utf-8")
            with clean_env(HOME=d):
                key, where = find_api_key()
                self.assertEqual(key, "from-own")
                self.assertIn(".abstract-writer.env", where)

    def test_own_file_beats_hermes(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".abstract-writer.env").write_text("ABSTRACT_WRITER_API_KEY=own\n",
                                                       encoding="utf-8")
            hermes = Path(d, ".hermes")
            hermes.mkdir()
            (hermes / ".env").write_text("OPENROUTER_API_KEY=hermes\n", encoding="utf-8")
            with clean_env(HOME=d):
                self.assertEqual(find_api_key()[0], "own")

    def test_falls_back_to_hermes_env(self):
        with tempfile.TemporaryDirectory() as d:
            hermes = Path(d, ".hermes")
            hermes.mkdir()
            (hermes / ".env").write_text('OPENROUTER_API_KEY="hermes-key"\n', encoding="utf-8")
            with clean_env(HOME=d):
                key, where = find_api_key()
                self.assertEqual(key, "hermes-key")
                self.assertIn(".hermes", where)

    def test_hermes_home_override(self):
        with tempfile.TemporaryDirectory() as d:
            profile = Path(d, "profile")
            profile.mkdir()
            (profile / ".env").write_text("OPENAI_API_KEY=profiled\n", encoding="utf-8")
            with clean_env(HOME=d, HERMES_HOME=str(profile)):
                self.assertEqual(find_api_key()[0], "profiled")

    def test_nothing_found(self):
        with tempfile.TemporaryDirectory() as d:
            with clean_env(HOME=d):
                self.assertEqual(find_api_key(), (None, "nowhere"))

    def test_env_file_override_path(self):
        with tempfile.TemporaryDirectory() as d:
            custom = Path(d, "custom.env")
            custom.write_text("ABSTRACT_WRITER_API_KEY=custom\n", encoding="utf-8")
            with clean_env(HOME=d, ABSTRACT_WRITER_ENV_FILE=str(custom)):
                self.assertEqual(own_env_file(), custom)
                self.assertEqual(find_api_key()[0], "custom")

    def test_hermes_default_location(self):
        with tempfile.TemporaryDirectory() as d:
            with clean_env(HOME=d):
                self.assertEqual(hermes_env_file(), Path(d) / ".hermes" / ".env")


class MessageTests(unittest.TestCase):
    def test_message_names_the_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, ".abstract-writer.env")
            path.write_text("ABSTRACT_WRITER_API_KEY=\n", encoding="utf-8")
            with clean_env(HOME=d):
                msg = missing_key_message()
            self.assertIn(str(path), msg)
            self.assertIn("nano", msg)
            self.assertIn("--provider mock", msg)

    def test_message_when_file_absent_says_to_create_it(self):
        with tempfile.TemporaryDirectory() as d:
            with clean_env(HOME=d):
                msg = missing_key_message()
            self.assertIn(".abstract-writer.env", msg)
            self.assertNotIn("nano", msg)

    def test_provider_raises_with_that_message(self):
        from abstract_writer.providers import OpenAICompatible, ProviderError
        with tempfile.TemporaryDirectory() as d:
            with clean_env(HOME=d):
                p = OpenAICompatible(model="m", api_key=None)
                with self.assertRaises(ProviderError) as ctx:
                    p.complete("s", "u")
                self.assertIn(".abstract-writer.env", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
