import unittest

from abstract_writer.phrase import has_hangul, parse_phrase


class HasHangulTests(unittest.TestCase):
    def test_korean(self):
        self.assertTrue(has_hangul("기다림"))
        self.assertTrue(has_hangul("waiting 기다림"))

    def test_not_korean(self):
        for text in ("waiting", "gti", "café", "", "123", "日本語"):
            self.assertFalse(has_hangul(text), text)


class ParsePhraseTests(unittest.TestCase):
    def test_bare_topic(self):
        self.assertEqual(parse_phrase("기다림"), ("기다림", {}))

    def test_single_modifier(self):
        self.assertEqual(parse_phrase("기다림 함축"), ("기다림", {"register": "compressed"}))

    def test_several_modifiers(self):
        seed, ov = parse_phrase("첫눈 단상 짧게")
        self.assertEqual(seed, "첫눈")
        self.assertEqual(ov, {"form": "fragments", "length": "short"})

    def test_multiword_seed_is_kept(self):
        seed, ov = parse_phrase("기다림에 대하여 편지")
        self.assertEqual(seed, "기다림에 대하여")
        self.assertEqual(ov, {"form": "letter"})

    def test_modifier_alone_stays_a_seed(self):
        # The last remaining token is never consumed, so "편지" is writable.
        self.assertEqual(parse_phrase("편지"), ("편지", {}))
        self.assertEqual(parse_phrase("편지 함축"), ("편지", {"register": "compressed"}))

    def test_parsing_stops_at_first_non_modifier(self):
        # "함축" is not trailing here, so it stays part of the seed.
        seed, ov = parse_phrase("함축 그 자체")
        self.assertEqual(seed, "함축 그 자체")
        self.assertEqual(ov, {})

    def test_repeated_field_keeps_the_last_word_typed(self):
        # Someone correcting themselves: "짧게" then "길게" means long.
        seed, ov = parse_phrase("기다림 짧게 길게")
        self.assertEqual(seed, "기다림")
        self.assertEqual(ov["length"], "long")
        self.assertEqual(parse_phrase("기다림 길게 짧게")[1]["length"], "short")

    def test_english_modifiers(self):
        self.assertEqual(parse_phrase("waiting compressed"), ("waiting", {"register": "compressed"}))
        self.assertEqual(parse_phrase("waiting LETTER")[1], {"form": "letter"})

    def test_extra_whitespace(self):
        self.assertEqual(parse_phrase("  기다림   함축  "), ("기다림", {"register": "compressed"}))

    def test_empty_raises(self):
        for text in ("", "   "):
            with self.assertRaises(ValueError):
                parse_phrase(text)

    def test_every_modifier_maps_to_a_real_option(self):
        from abstract_writer import prompts
        from abstract_writer.phrase import MODIFIERS
        valid = {
            "register": prompts.REGISTERS,
            "form": prompts.FORMS,
            "length": prompts.LENGTHS,
            # not an Options field: the CLI reads it and changes what it does
            "mode": {"prompt": None},
        }
        for word, (field, value) in MODIFIERS.items():
            self.assertIn(field, valid, word)
            self.assertIn(value, valid[field], f"{word} -> {field}={value}")

    def test_options_fields_really_exist(self):
        from abstract_writer.phrase import MODIFIERS
        from abstract_writer.pipeline import Options
        opts = Options()
        for word, (field, _value) in MODIFIERS.items():
            if field == "mode":
                continue
            self.assertTrue(hasattr(opts, field), f"{word} -> Options has no {field}")

    def test_copied_shell_prompt_marker_is_dropped(self):
        # Someone copies "$ 버거킹 단상" out of a README, prompt character and all.
        self.assertEqual(parse_phrase("$ 버거킹 단상"), ("버거킹", {"form": "fragments"}))
        self.assertEqual(parse_phrase("> 저녁 함축"), ("저녁", {"register": "compressed"}))
        self.assertEqual(parse_phrase("% waiting"), ("waiting", {}))
        self.assertEqual(parse_phrase("❯ 저녁"), ("저녁", {}))

    def test_marker_alone_is_still_a_seed(self):
        # Never strip the last token, so nothing silently becomes empty.
        self.assertEqual(parse_phrase("$"), ("$", {}))

    def test_marker_inside_the_seed_is_kept(self):
        self.assertEqual(parse_phrase("돈과 $ 사이"), ("돈과 $ 사이", {}))

    def test_prompt_mode_modifier(self):
        self.assertEqual(parse_phrase("저녁 프롬프트"), ("저녁", {"mode": "prompt"}))
        seed, ov = parse_phrase("저녁 프롬프트 함축 짧게")
        self.assertEqual(seed, "저녁")
        self.assertEqual(ov, {"mode": "prompt", "register": "compressed", "length": "short"})


if __name__ == "__main__":
    unittest.main()
