import json
import unittest

from abstract_writer import pipeline
from abstract_writer.pipeline import Options, StageError, parse_json_lenient, validate_audit, validate_map, write
from abstract_writer.providers import MockProvider, ProviderError, OpenAICompatible, make_provider


class ParseJsonTests(unittest.TestCase):
    def test_bare_object(self):
        self.assertEqual(parse_json_lenient('{"a": 1}'), {"a": 1})

    def test_fenced_object(self):
        self.assertEqual(parse_json_lenient('here:\n```json\n{"a": 1}\n```\nthanks'), {"a": 1})

    def test_object_with_prose_around(self):
        self.assertEqual(parse_json_lenient('Sure. {"a": [1, 2]} Done.'), {"a": [1, 2]})

    def test_not_json_raises(self):
        with self.assertRaises(StageError):
            parse_json_lenient("no braces here")


class ValidationTests(unittest.TestCase):
    def test_map_requires_two_distinctions(self):
        bad = {"question": "q", "distinctions": [{}], "tension": {}, "anchors": ["a", "b"],
               "stake": "s", "turn": "t"}
        with self.assertRaises(StageError):
            validate_map(bad)

    def test_map_missing_key(self):
        with self.assertRaises(StageError):
            validate_map({"question": "q"})

    def test_audit_overall_is_recomputed(self):
        a = validate_audit({"scores": {"distinction": 10, "anchor": 10, "tension": 10,
                                       "stake": 10, "turn": 10, "hollow": 4},
                            "overall": 99, "verdict": "PASS"})
        self.assertEqual(a["overall"], 9.0)
        self.assertEqual(a["verdict"], "pass")

    def test_audit_bad_scores_become_zero(self):
        a = validate_audit({"scores": {"distinction": "x"}, "verdict": "meh"})
        self.assertEqual(a["scores"]["distinction"], 0.0)
        self.assertEqual(a["verdict"], "revise")
        self.assertEqual(a["issues"], [])


class MockPipelineTests(unittest.TestCase):
    def test_full_loop_ko(self):
        p = MockProvider()
        stages = []
        res = write("기다림", p, Options(lang="ko", rounds=2, threshold=8.0),
                    on_stage=lambda n, _: stages.append(n))
        # excavate, compose, lint, audit(revise), revise, lint, audit(pass)
        self.assertEqual(stages, ["excavate", "compose", "lint", "audit", "revise", "lint", "audit"])
        self.assertEqual(len(res.rounds), 2)
        self.assertEqual(res.stopped_because, "accepted")
        self.assertNotEqual(res.rounds[0].piece, res.rounds[1].piece)
        self.assertTrue(res.final_lint.passed, res.final_lint.flags)
        self.assertEqual(res.final_audit["verdict"], "pass")
        self.assertIn("question", res.concept_map)
        self.assertEqual(p.calls, 5)

    def test_full_loop_en(self):
        res = write("waiting", MockProvider(), Options(lang="en", form="fragments", length="short"))
        self.assertTrue(res.text.startswith("# Two Kinds of Waiting"))
        self.assertTrue(res.final_lint.passed, res.final_lint.flags)

    def test_low_threshold_stops_after_first_audit(self):
        # First mock audit scores 7.67 with verdict 'revise'; verdict still blocks.
        res = write("기다림", MockProvider(), Options(lang="ko", rounds=2, threshold=5.0))
        self.assertEqual(len(res.rounds), 2)

    def test_zero_rounds_never_revises(self):
        p = MockProvider()
        res = write("기다림", p, Options(lang="ko", rounds=0))
        self.assertEqual(len(res.rounds), 1)
        self.assertTrue(res.stopped_because.startswith("max rounds reached"))
        self.assertNotIn("revise", [s for s, _ in p.log])

    def test_no_audit_skips_model_judging(self):
        p = MockProvider()
        res = write("기다림", p, Options(lang="ko"), audit=False)
        self.assertEqual(p.calls, 2)
        self.assertIsNone(res.final_audit)
        self.assertEqual(res.stopped_because, "audit disabled")

    def test_trace_is_serializable(self):
        res = write("기다림", MockProvider(), Options(lang="ko"))
        json.dumps(res.to_trace(), ensure_ascii=False)

    def test_empty_seed_rejected(self):
        with self.assertRaises(ValueError):
            write("   ", MockProvider())

    def test_bad_options_rejected(self):
        with self.assertRaises(ValueError):
            write("x", MockProvider(), Options(form="sonnet"))


class ProviderFactoryTests(unittest.TestCase):
    def test_mock(self):
        self.assertIsInstance(make_provider("mock"), MockProvider)

    def test_openai_reads_env(self):
        import os
        old = dict(os.environ)
        try:
            os.environ["ABSTRACT_WRITER_API_KEY"] = "k"
            os.environ["ABSTRACT_WRITER_MODEL"] = "m"
            os.environ["ABSTRACT_WRITER_BASE_URL"] = "https://example.invalid/v1"
            p = make_provider("openai")
            self.assertIsInstance(p, OpenAICompatible)
            self.assertEqual((p.model, p.base_url, p.api_key), ("m", "https://example.invalid/v1", "k"))
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_unknown_provider(self):
        with self.assertRaises(ProviderError):
            make_provider("carrier-pigeon")

    def test_missing_key_is_a_clear_error(self):
        p = OpenAICompatible(model="m", api_key=None)
        with self.assertRaises(ProviderError) as ctx:
            p.complete("s", "u")
        self.assertIn("ABSTRACT_WRITER_API_KEY", str(ctx.exception))


class StageFailureTests(unittest.TestCase):
    def test_bad_excavate_output_raises_stage_error(self):
        class Broken:
            name = "broken"
            def complete(self, system, user, **kw):
                return "I cannot do that."
        with self.assertRaises(StageError):
            write("x", Broken(), Options(lang="en"))

    def test_module_exports(self):
        for name in ("Options", "Result", "write", "parse_json_lenient"):
            self.assertTrue(hasattr(pipeline, name))


if __name__ == "__main__":
    unittest.main()
