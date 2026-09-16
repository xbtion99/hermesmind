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


if __name__ == "__main__":
    unittest.main()
