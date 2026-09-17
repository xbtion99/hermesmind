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
        valid = {"register": prompts.REGISTERS, "form": prompts.FORMS, "length": prompts.LENGTHS}
        for word, (field, value) in MODIFIERS.items():
            self.assertIn(field, valid, word)
            self.assertIn(value, valid[field], f"{word} -> {field}={value}")


if __name__ == "__main__":
    unittest.main()
