import unittest

from abstract_writer.lint import detect_lang, lint_text, split_paragraphs

HOLLOW_KO = (
    "시간은 흐른다. 우리는 그 흐름 속에서 존재의 본질을 마주한다. "
    "기다림은 삶의 일부이며, 그 안에서 우리는 진정한 자신을 발견한다."
)
DEEP_KO = (
    "기다림에는 두 종류가 있다. 하나는 버스를 기다리는 것처럼 끝이 정해진 기다림이고, "
    "다른 하나는 답장을 기다리는 것처럼 끝이 상대에게 달린 기다림이다. "
    "첫 번째 기다림에서 시간은 줄어들고, 두 번째 기다림에서 시간은 쌓인다. "
    "우리가 \"기다리기 힘들다\"고 말할 때 힘든 것은 시간의 길이가 아니라, "
    "그 시간이 어느 쪽으로 세어지고 있는지 모른다는 사실이다."
)
HOLLOW_EN = (
    "Time flows. Within that flow we encounter the essence of being. "
    "Waiting is part of life, and in it we discover our true self."
)
DEEP_EN = (
    "There are two kinds of waiting. One has a fixed end, like waiting for a bus; "
    "the other has an end that belongs to someone else, like waiting for a reply. "
    "In the first kind time is subtracted; in the second it accumulates. "
    "When we say waiting is hard, what is hard is not the length of the time "
    "but not knowing which way it is being counted."
)


class DetectLangTests(unittest.TestCase):
    def test_korean(self):
        self.assertEqual(detect_lang("기다림에 대하여"), "ko")

    def test_english(self):
        self.assertEqual(detect_lang("on waiting"), "en")

    def test_empty_defaults_to_english(self):
        self.assertEqual(detect_lang("123 ..."), "en")


class ContrastExampleTests(unittest.TestCase):
    """METHOD.md §8: the hollow example must fail, the deep one must pass."""

    def test_hollow_ko_fails(self):
        r = lint_text(HOLLOW_KO)
        self.assertFalse(r.passed)
        self.assertIn("본질", [h.term for h in r.hollow_hits])
        self.assertTrue(any("hollow" in f for f in r.flags))
        self.assertTrue(any("distinctions" in f for f in r.flags))

    def test_deep_ko_passes(self):
        r = lint_text(DEEP_KO)
        self.assertTrue(r.passed, r.flags)
        self.assertEqual(r.hollow_unspecified, 0)
        self.assertGreater(r.distinction_count, 0)
        self.assertEqual(r.anchor_ratio, 1.0)

    def test_hollow_en_fails(self):
        r = lint_text(HOLLOW_EN)
        self.assertFalse(r.passed)
        self.assertIn("essence", [h.term for h in r.hollow_hits])
        self.assertIn("true self", [h.term for h in r.hollow_hits])

    def test_deep_en_passes(self):
        r = lint_text(DEEP_EN)
        self.assertTrue(r.passed, r.flags)


class SpecificationTests(unittest.TestCase):
    def test_hollow_term_is_allowed_when_specified(self):
        # "본질" followed by a distinction in the same sentence is not a hit.
        text = "여기서 본질이란 숨은 알맹이가 아니라, 바꾸면 다른 것이 되는 조건을 뜻한다. 문 앞의 열쇠처럼."
        r = lint_text(text, "ko")
        self.assertEqual(r.hollow_unspecified, 0)
        self.assertTrue(r.passed, r.flags)

    def test_hollow_term_specified_in_next_sentence(self):
        text = "그것은 영원에 가깝다. 시간이 멈춘 것이 아니라 시계가 더 이상 세지 않는 상태다. 침대 옆 시계."
        r = lint_text(text, "ko")
        self.assertEqual(r.hollow_unspecified, 0)


class EndingTests(unittest.TestCase):
    def test_summary_opener_is_flagged(self):
        text = (
            "문 앞에서 기다린다는 것은 오지 않는 것이 아니라 아직 오지 않은 것을 세는 일이다.\n\n"
            "결국 기다림은 세는 일이다. 문이 아니라 시계를 보는 일이다."
        )
        r = lint_text(text, "ko")
        self.assertTrue(r.summary_ending)
        self.assertTrue(any("summary" in f for f in r.flags))

    def test_turn_ending_not_flagged(self):
        text = (
            "문 앞에서 기다린다는 것은 오지 않는 것이 아니라 아직 오지 않은 것을 세는 일이다.\n\n"
            "힘든 것은 길이가 아니라 방향이었다. 문 앞의 신발이 그것을 먼저 알았다."
        )
        r = lint_text(text, "ko")
        self.assertFalse(r.summary_ending)


class ParagraphTests(unittest.TestCase):
    def test_headings_are_not_paragraphs(self):
        paras = split_paragraphs("# 제목\n\n첫 단락.\n\n둘째 단락.")
        self.assertEqual(paras, ["첫 단락.", "둘째 단락."])

    def test_html_comments_are_ignored(self):
        paras = split_paragraphs("<!-- 손으로 쓴 메모 -->\n\n첫 단락.")
        self.assertEqual(paras, ["첫 단락."])
        r = lint_text("<!-- 본질 진정한 -->\n\n버스가 아니라 답장.", "ko")
        self.assertEqual(r.hollow_unspecified, 0)
        self.assertEqual(r.paragraphs, 1)

    def test_anchor_ratio_counts_paragraphs(self):
        text = "손에 열쇠가 있다. 그것이 아니라 이것이다.\n\n추상은 추상이 아니라 층위다.\n\n" \
               "그러나 그것이 아니라 저것이다."
        r = lint_text(text, "ko")
        self.assertEqual(r.paragraphs, 3)
        self.assertEqual(r.anchored_paragraphs, 1)
        self.assertTrue(any("anchor" in f for f in r.flags))

    def test_report_dict_is_json_friendly(self):
        import json
        r = lint_text(DEEP_KO)
        json.dumps(r.to_dict(), ensure_ascii=False)


class SizeCheckTests(unittest.TestCase):
    """METHOD.md's brief and the check that reads it back must agree."""

    def test_nothing_is_checked_unless_asked(self):
        r = lint_text("짧다. 버스가 아니라 답장.", "ko")
        self.assertIsNone(r.length_target)
        self.assertIsNone(r.form_target)
        self.assertTrue(r.passed, r.flags)

    def test_too_short_is_flagged(self):
        r = lint_text("짧다. 버스가 아니라 답장이다. 손에 든 전화.", "ko", "plain", "medium")
        self.assertTrue(any("shorter than asked" in f for f in r.flags), r.flags)

    def test_too_long_is_flagged(self):
        text = "버스가 아니라 답장을 기다린다. 손에 든 전화. " * 60
        r = lint_text(text, "ko", "plain", "short")
        self.assertTrue(any("longer than asked" in f for f in r.flags), r.flags)

    def test_tolerance_lets_a_near_miss_through(self):
        from abstract_writer.lint import LENGTH_TOLERANCE
        from abstract_writer.prompts import LENGTH_RANGES
        lo = LENGTH_RANGES["ko"]["short"][0]
        just_under = int(lo * (1 - LENGTH_TOLERANCE / 2))
        text = "문 앞에서 기다린다. 버스가 아니라 답장이다. " + "가" * just_under
        r = lint_text(text, "ko", "plain", "short")
        self.assertFalse(any("shorter" in f for f in r.flags), (r.measure, r.flags))

    def test_compressed_target_is_smaller(self):
        from abstract_writer.lint import length_target
        plain = length_target("ko", "short", "plain")
        compressed = length_target("ko", "short", "compressed")
        self.assertLess(compressed[1], plain[1])
        self.assertLess(compressed[0], plain[0])

    def test_form_paragraph_count(self):
        three = "가나다 버스가 아니라 답장.\n\n두 번째 문 앞.\n\n세 번째 손."
        r = lint_text(three, "ko", "plain", None, "fragments")
        self.assertEqual(r.form_target, (8, 14))
        self.assertTrue(any("paragraphs" in f for f in r.flags), r.flags)

    def test_korean_counts_characters_english_counts_words(self):
        ko = lint_text("가나다라마 바사아자차", "ko")
        en = lint_text("one two three four five", "en")
        self.assertEqual(ko.measure_unit, "자")
        self.assertEqual(en.measure_unit, "words")
        self.assertEqual(en.measure, 5)

    def test_headings_are_not_counted(self):
        with_title = lint_text("# 아주 긴 제목이 여기에 있다\n\n본문이다.", "ko")
        without = lint_text("본문이다.", "ko")
        self.assertEqual(with_title.measure, without.measure)

    def test_report_dict_carries_the_targets(self):
        import json
        r = lint_text("짧다.", "ko", "plain", "short", "essay")
        d = r.to_dict()
        json.dumps(d, ensure_ascii=False)
        self.assertEqual(d["length_target"], [600, 900])
        self.assertEqual(d["form_target"], [4, 8])


class BriefAgreementTests(unittest.TestCase):
    """The numbers a prompt states and the numbers the lint enforces are one table."""

    def test_length_text_states_the_range(self):
        from abstract_writer.prompts import LENGTHS, LENGTH_RANGES
        for name, ranges in LENGTH_RANGES.items():
            for length, (lo, hi) in ranges.items():
                text = LENGTHS[length][name]
                self.assertIn(str(lo), text, f"{name}/{length}: {text}")
                self.assertIn(str(hi), text, f"{name}/{length}: {text}")

    def test_form_text_states_the_unit_count(self):
        from abstract_writer.prompts import FORMS, FORM_UNITS
        for form, (lo, hi) in FORM_UNITS.items():
            for lang in ("ko", "en"):
                text = FORMS[form][lang]
                self.assertIn(str(lo), text, f"{form}/{lang}: {text}")
                self.assertIn(str(hi), text, f"{form}/{lang}: {text}")

    def test_every_form_and_length_has_a_range(self):
        from abstract_writer.prompts import FORMS, FORM_UNITS, LENGTHS, LENGTH_RANGES
        self.assertEqual(set(FORMS), set(FORM_UNITS))
        for lang in ("ko", "en"):
            self.assertEqual(set(LENGTHS), set(LENGTH_RANGES[lang]))


class RegisterTests(unittest.TestCase):
    """METHOD.md §10: scaffolding is recorded always, flagged only when compressed."""

    EXPLANATORY = (
        "기다림에는 두 종류가 있다. 버스는 끝이 정해져 있고 답장은 끝이 상대에게 있다.\n\n"
        "그러니 시계를 보는 일과 화면을 보는 일은 다르다. 이것은 시간이 세어지는 방향이 "
        "다르기 때문이다. 다시 말해 길이가 아니라 방향이 문제인 것이다."
    )
    IMPLICIT = (
        "기다림에는 두 종류가 있다. 버스는 끝이 정해져 있다. 답장은 끝이 상대에게 있다.\n\n"
        "전광판의 숫자가 줄어든다. 3분, 2분, 1분. 손가락이 화면을 다시 켠다.\n\n"
        "길이가 아니라 방향이었다. 정류장에 남은 것은 시계뿐이다."
    )

    def test_scaffolding_counted_in_both_registers(self):
        plain = lint_text(self.EXPLANATORY, "ko", "plain")
        comp = lint_text(self.EXPLANATORY, "ko", "compressed")
        self.assertEqual(plain.scaffold_count, comp.scaffold_count)
        self.assertGreater(plain.scaffold_count, 0)

    def test_scaffolding_flagged_only_when_compressed(self):
        plain = lint_text(self.EXPLANATORY, "ko", "plain")
        comp = lint_text(self.EXPLANATORY, "ko", "compressed")
        self.assertFalse(any("scaffolding" in f for f in plain.flags), plain.flags)
        self.assertTrue(any("scaffolding" in f for f in comp.flags), comp.flags)

    def test_implicit_prose_passes_compressed(self):
        r = lint_text(self.IMPLICIT, "ko", "compressed")
        self.assertEqual(r.scaffold_count, 0)
        self.assertTrue(r.passed, r.flags)

    def test_english_scaffolding(self):
        text = ("There are two kinds of waiting. A bus has a fixed end.\n\n"
                "Therefore the clock and the screen are different. In other words, "
                "which means the direction is what matters, not the length of the room.")
        r = lint_text(text, "en", "compressed")
        self.assertGreater(r.scaffold_count, 0)
        self.assertTrue(any("scaffolding" in f for f in r.flags))

    def test_unknown_register_falls_back_to_plain(self):
        r = lint_text(self.EXPLANATORY, "ko", "함축")
        self.assertEqual(r.register, "plain")
        self.assertFalse(any("scaffolding" in f for f in r.flags))

    def test_register_in_report_dict_and_summary(self):
        r = lint_text(self.IMPLICIT, "ko", "compressed")
        self.assertEqual(r.to_dict()["register"], "compressed")
        self.assertIn("register=compressed", r.summary())


class ReferenceExampleTests(unittest.TestCase):
    """The two shipped reference pieces must keep passing their own register."""

    import pathlib as _pathlib
    EXAMPLES = _pathlib.Path(__file__).resolve().parent.parent / "examples"

    def test_plain_reference_passes_plain(self):
        text = (self.EXAMPLES / "waiting_ko.md").read_text(encoding="utf-8")
        self.assertTrue(lint_text(text, "ko", "plain").passed)

    def test_compressed_reference_passes_compressed(self):
        text = (self.EXAMPLES / "waiting_ko_compressed.md").read_text(encoding="utf-8")
        r = lint_text(text, "ko", "compressed")
        self.assertTrue(r.passed, r.flags)
        self.assertEqual(r.scaffold_count, 0)

    def test_compressed_reference_is_shorter(self):
        plain = (self.EXAMPLES / "waiting_ko.md").read_text(encoding="utf-8")
        comp = (self.EXAMPLES / "waiting_ko_compressed.md").read_text(encoding="utf-8")
        self.assertLess(lint_text(comp, "ko").words, lint_text(plain, "ko").words)


if __name__ == "__main__":
    unittest.main()
