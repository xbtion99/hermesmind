import unittest

from abstract_writer.endpoints import (
    OPENAI_BASE,
    OPENAI_MODEL,
    OPENROUTER_BASE,
    OPENROUTER_MODEL,
    infer_profile,
    profile_of_base,
    resolve,
)

STALE = (OPENROUTER_BASE, OPENROUTER_MODEL)  # what a key file written before this shipped


class InferProfileTests(unittest.TestCase):
    def test_openai_variable_name_wins(self):
        self.assertEqual(infer_profile("anything", "OPENAI_API_KEY"), "openai")

    def test_openrouter_prefix(self):
        self.assertEqual(infer_profile("sk-or-v1-abc", "ABSTRACT_WRITER_API_KEY"), "openrouter")

    def test_openai_prefixes(self):
        self.assertEqual(infer_profile("sk-proj-abc", "ABSTRACT_WRITER_API_KEY"), "openai")
        self.assertEqual(infer_profile("sk-abcdef", "ABSTRACT_WRITER_API_KEY"), "openai")

    def test_unknown_defaults_to_openrouter(self):
        self.assertEqual(infer_profile("nous-abc", None), "openrouter")
        self.assertEqual(infer_profile(None, None), "openrouter")

    def test_profile_of_base(self):
        self.assertEqual(profile_of_base(OPENAI_BASE), "openai")
        self.assertEqual(profile_of_base(OPENROUTER_BASE + "/"), "openrouter")
        self.assertEqual(profile_of_base("http://localhost:1234/v1"), "custom")


class ResolveTests(unittest.TestCase):
    def test_openai_key_against_stale_defaults(self):
        # The exact case a key file written before this change produces.
        self.assertEqual(resolve(*STALE, "sk-proj-abc", "ABSTRACT_WRITER_API_KEY"),
                         (OPENAI_BASE, OPENAI_MODEL))

    def test_openai_key_under_its_own_variable(self):
        self.assertEqual(resolve(*STALE, "whatever", "OPENAI_API_KEY"),
                         (OPENAI_BASE, OPENAI_MODEL))

    def test_openrouter_key_keeps_openrouter(self):
        self.assertEqual(resolve(*STALE, "sk-or-v1-abc", "ABSTRACT_WRITER_API_KEY"),
                         (OPENROUTER_BASE, OPENROUTER_MODEL))

    def test_explicit_base_wins_over_inference(self):
        base, model = resolve("http://localhost:1234/v1", OPENROUTER_MODEL, "sk-proj-abc", None)
        self.assertEqual(base, "http://localhost:1234/v1")

    def test_explicit_model_is_kept(self):
        base, model = resolve(OPENROUTER_BASE, "openai/gpt-4o", "sk-or-v1-abc", None)
        self.assertEqual((base, model), (OPENROUTER_BASE, "openai/gpt-4o"))

    def test_explicit_openai_base_replaces_the_default_model(self):
        # Someone set only the base URL; the stale model would be meaningless there.
        base, model = resolve(OPENAI_BASE, OPENROUTER_MODEL, "sk-abc", None)
        self.assertEqual((base, model), (OPENAI_BASE, OPENAI_MODEL))

    def test_custom_base_keeps_a_custom_model(self):
        self.assertEqual(resolve("http://localhost:1234/v1", "my-model", "sk-abc", None),
                         ("http://localhost:1234/v1", "my-model"))

    def test_custom_base_with_default_model_falls_back_to_openrouter_model(self):
        base, model = resolve("http://localhost:1234/v1", OPENROUTER_MODEL, "sk-or-v1-a", None)
        self.assertEqual(base, "http://localhost:1234/v1")
        self.assertEqual(model, OPENROUTER_MODEL)

    def test_no_key_at_all(self):
        self.assertEqual(resolve(None, None, None, None), (OPENROUTER_BASE, OPENROUTER_MODEL))


class ProviderWiringTests(unittest.TestCase):
    def test_make_provider_infers_from_the_key(self):
        import os
        from abstract_writer.providers import make_provider
        saved = dict(os.environ)
        try:
            for v in ("ABSTRACT_WRITER_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY"):
                os.environ.pop(v, None)
            os.environ["ABSTRACT_WRITER_API_KEY"] = "sk-proj-abc"
            os.environ["ABSTRACT_WRITER_BASE_URL"] = OPENROUTER_BASE
            os.environ["ABSTRACT_WRITER_MODEL"] = OPENROUTER_MODEL
            p = make_provider("openai")
            self.assertEqual(p.base_url, OPENAI_BASE)
            self.assertEqual(p.model, OPENAI_MODEL)
        finally:
            os.environ.clear()
            os.environ.update(saved)

    def test_explicit_flags_beat_inference(self):
        from abstract_writer.providers import make_provider
        p = make_provider("openai", model="m", base_url="http://x/v1", api_key="sk-proj-abc")
        self.assertEqual((p.base_url, p.model), ("http://x/v1", "m"))

    def test_auth_error_names_the_endpoint(self):
        from abstract_writer.providers import OpenAICompatible
        p = OpenAICompatible(model="gpt-4o", base_url=OPENAI_BASE, api_key="k")
        msg = p._http_error(401, OPENAI_BASE, '{"error":"bad key"}')
        self.assertIn("base_url", msg)
        self.assertIn(OPENAI_BASE, msg)
        self.assertIn("ABSTRACT_WRITER_BASE_URL", msg)

    def test_model_error_names_the_model_setting(self):
        from abstract_writer.providers import OpenAICompatible
        p = OpenAICompatible(model="nope", base_url=OPENAI_BASE, api_key="k")
        msg = p._http_error(404, OPENAI_BASE, '{"error":{"message":"The model does not exist"}}')
        self.assertIn("ABSTRACT_WRITER_MODEL", msg)
        self.assertIn("nope", msg)


if __name__ == "__main__":
    unittest.main()
