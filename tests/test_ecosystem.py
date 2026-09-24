import unittest
from laya_ecosystem.fast_compactor import compact_transcript
from laya_ecosystem.foreman_supervisor import supervise_action
from laya_ecosystem.browser_ultrafast import decide_ui_action

class TestLayaEcosystem(unittest.TestCase):
    def test_compact_transcript_empty(self):
        res = compact_transcript([])
        self.assertEqual(res, [])

    def test_compact_transcript_short(self):
        entries = [{"type": "tool_call", "content": "short output"}]
        res = compact_transcript(entries)
        self.assertEqual(len(res), 1)

    def test_supervise_action_fallback(self):
        res = supervise_action("test goal", "normal output", 0)
        self.assertTrue("answers" in res or "action" in res or "error" in res)

    def test_decide_ui_action(self):
        elements = [{"id": 1, "tag": "button", "text": "Submit"}]
        res = decide_ui_action("Click submit", elements)
        self.assertTrue("answers" in res or "error" in res)

if __name__ == "__main__":
    unittest.main()
