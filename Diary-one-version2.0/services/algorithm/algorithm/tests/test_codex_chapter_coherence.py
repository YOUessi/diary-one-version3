"""Owner-approved grouping contract checks; no synthetic scene gold."""

import tempfile
import unittest
from pathlib import Path

from diary_one_ci import codex_chapter_coherence as coherence
from diary_one_ci import x02
from tests.test_x02 import ScriptedGateway, make_x02_bundle_v03


class ChapterCoherenceTests(unittest.TestCase):
    def test_active_policy_is_visible_in_receipt_and_structure_context(self):
        self.assertEqual(
            x02.x02_runtime_policies()["chapter_coherence"],
            coherence.POLICY_VERSION,
        )
        context = {coherence.POLICY_FIELD: coherence.POLICY_VERSION}
        instruction = coherence.prompt_instruction(context)
        self.assertIn("experience-first Chapter boundary", instruction)
        self.assertIn("never sufficient by itself", instruction)
        self.assertIn("Cross-setting members are allowed", instruction)
        self.assertIn("connect transitively across the beat_map", instruction)
        self.assertIn("every member must connect", instruction)
        self.assertIn("absence of a contradiction is not connection evidence", instruction)
        self.assertIn("omit that Chapter rather than padding it", instruction)
        self.assertIn("existing Aha search", instruction)

    def test_inactive_policy_does_not_change_legacy_prompt_path(self):
        self.assertEqual(coherence.prompt_instruction({}), "")
        legacy = x02._structure_prompt({"observations": [], "moments": []})
        self.assertNotIn("experience-first Chapter boundary", legacy)
        legacy_storyline = x02._storyline_structure_prompt({
            "editorial_allocation_policy_version":
                "DIARY_ONE_X02_EDITORIAL_ALLOCATION_V01",
            "observations": [],
            "moments": [],
        })
        self.assertIn(
            "A common theme can justify grouping without claiming one continuous outing",
            legacy_storyline,
        )

    def test_current_pipeline_sends_one_active_policy_to_existing_structure_call(self):
        gateway = ScriptedGateway(storyline_groups=[[0, 1, 2]])
        with tempfile.TemporaryDirectory() as directory:
            result = x02.run_x02(make_x02_bundle_v03(Path(directory)), gateway)
        calls = [call for call in gateway.calls
                 if call["stage"] == "S05_S07_STRUCTURE_PROPOSAL"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0]["context"][coherence.POLICY_FIELD],
            coherence.POLICY_VERSION,
        )
        self.assertIn(coherence.prompt_instruction(calls[0]["context"]), calls[0]["prompt"])
        self.assertEqual(
            result["decision_trace"]["runtime_policies"]["chapter_coherence"],
            coherence.POLICY_VERSION,
        )

    def test_current_prompt_removes_the_superseded_theme_permission(self):
        context = {
            coherence.POLICY_FIELD: coherence.POLICY_VERSION,
            "observations": [],
            "moments": [],
        }
        prompt = x02._storyline_structure_prompt(context)
        self.assertNotIn(
            "A common theme can justify grouping without claiming one continuous outing",
            prompt,
        )
        self.assertIn(coherence.prompt_instruction(context), prompt)
        self.assertIn(
            "IMPORT_SEQUENCE_ONLY means the order is an editorial index",
            prompt,
        )

    def test_policy_adds_no_semantic_gate_or_model_call(self):
        instruction = coherence.prompt_instruction(
            {coherence.POLICY_FIELD: coherence.POLICY_VERSION}
        )
        self.assertNotIn("food", instruction.lower())
        self.assertNotIn("night", instruction.lower())
        self.assertNotIn("architecture", instruction.lower())
        self.assertFalse(hasattr(coherence, "validate_candidate"))


if __name__ == "__main__":
    unittest.main()
