"""Recorded-data projection and interface checks, not semantic or writing gold."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci import codex_content_brief as brief
from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes, sha256_bytes
from test_codex_x02_chapter_media import MediaGateway
from test_x02 import assert_json_schema_instance, make_x02_bundle_v03


ROOT = Path(__file__).resolve().parents[1]


class ContentBriefTests(unittest.TestCase):
    def setUp(self):
        recorded = json.loads((ROOT / "tests/fixtures/codex_aha_writer_real_failures.json").read_text())
        self.chapter = recorded["chapter_memory"]
        observations = {item["id"]: item for item in recorded["observations"]}
        media = {item["candidate_id"]: item for item in recorded["media"]}
        ahas = []
        for selected in recorded["selected_ahas"]:
            observation = observations[selected["observation_id"]]
            ahas.append({
                "candidate_id": selected["candidate_id"], "memory_type": "AHA",
                "facts": observation["facts"],
                "event_fact_ids": [fact["fact_id"] for fact in observation["facts"]],
                # This archived selection used deterministic event-kind duty.
                "narrative_duty": observation["event_kind"],
                "selected_media": media[selected["candidate_id"]]["media"],
            })
        self.context = {
            "locale": "zh-Hans", "writer_grounding_policy": x02.X02_WRITER_GROUNDING_POLICY,
            brief.POLICY_FIELD: brief.POLICY_VERSION, "memories": [self.chapter, *ahas],
        }

    def test_verbatim_facts_and_existing_guidance_survive_without_mutating_ledger(self):
        before = copy.deepcopy(self.context)
        outgoing = brief.writer_input(self.context)
        for original, projected in zip(self.context["memories"], outgoing["memories"]):
            self.assertEqual(projected["facts"], brief.compact_facts(original))
            self.assertEqual(projected["candidate_id"], original["candidate_id"])
            self.assertNotIn("selected_media", projected)
            self.assertNotIn("storyline_identity", projected)
        self.assertEqual(outgoing["memories"][0]["content_brief"]["theme_hint"],
                         self.chapter["storyline_identity"]["thesis"])
        self.assertEqual(self.context, before)
        outgoing["memories"][0]["facts"][0]["text"] = ""
        self.assertEqual(self.context, before)

    def test_three_item_projection_keeps_only_current_material_contributions(self):
        original = copy.deepcopy(self.chapter)
        selected = copy.deepcopy(self.chapter)
        selected["selected_media"] = selected["selected_media"][:3]
        selected_ids = {item["observation_id"] for item in selected["selected_media"]}
        beats = selected["storyline_identity"]["beat_map"]
        allowed = {fid for beat in beats if beat["observation_id"] in selected_ids
                   for fid in beat["fact_ids"]}
        selected["facts"] = [fact for fact in selected["facts"] if fact["fact_id"] in allowed]
        projected = brief.build_brief(selected)
        self.assertEqual(len(projected["materials"]), 3)
        self.assertEqual({item["observation_id"] for item in projected["materials"]}, selected_ids)
        self.assertEqual({fid for item in projected["materials"] for fid in item["fact_ids"]}, allowed)
        self.assertEqual(self.chapter, original)

    def test_media_and_writer_use_the_same_theme_and_member_contributions(self):
        memory = self.chapter
        beats = {b["observation_id"]: b for b in memory["storyline_identity"]["beat_map"]}
        members = [{"id": media["observation_id"], "facts": [
            fact for fact in memory["facts"] if fact["fact_id"] in beats[media["observation_id"]]["fact_ids"]
        ]} for media in memory["selected_media"]]
        candidate = {"storyline_identity": memory["storyline_identity"],
                     "fact_ids": [fact["fact_id"] for fact in memory["facts"]]}
        media_input = brief.chapter_selection_content(candidate, members)
        self.assertEqual(media_input["content_brief"], brief.build_brief(memory))
        self.assertEqual(media_input["facts"], brief.compact_facts(memory))

    def test_empty_guidance_does_not_remove_material_or_facts(self):
        context = copy.deepcopy(self.context)
        memory = context["memories"][0]
        memory["storyline_identity"]["thesis"] = ""
        for beat in memory["storyline_identity"]["beat_map"]:
            beat["contribution"] = ""
        outgoing = brief.writer_input(context)["memories"][0]
        self.assertEqual(outgoing["facts"], brief.compact_facts(memory))
        self.assertEqual(len(outgoing["content_brief"]["materials"]), len(memory["selected_media"]))
        self.assertEqual(outgoing["content_brief"]["theme_hint"], "")

    def test_unavailable_hint_reference_does_not_expand_fact_scope(self):
        memory = copy.deepcopy(self.chapter)
        beat = memory["storyline_identity"]["beat_map"][0]
        # Pure ID-scope probe; no invented visual or semantic claim.
        beat["fact_ids"].append("unavailable-reference")
        projected = brief.build_brief(memory)
        material = next(m for m in projected["materials"] if m["observation_id"] == beat["observation_id"])
        self.assertNotIn("unavailable-reference", material["fact_ids"])
        self.assertEqual(material["contribution_hint"], "")
        self.assertEqual(memory["facts"], self.chapter["facts"])

    def test_aha_duty_event_scope_and_source_binding_survive(self):
        outgoing = brief.writer_input(self.context)
        for original, projected in zip(self.context["memories"][1:], outgoing["memories"][1:]):
            self.assertEqual(projected["event_fact_ids"], original["event_fact_ids"])
            self.assertEqual(projected["content_brief"]["moment_hint"], original["narrative_duty"])
            material = projected["content_brief"]["materials"][0]
            self.assertEqual(material["fact_ids"], original["event_fact_ids"])
            self.assertEqual(material["observation_id"], original["selected_media"][0]["observation_id"])

    def test_current_prompt_uses_projection_and_legacy_context_stays_legacy(self):
        prompt = x02._writer_prompt(self.context, retry=False)
        outgoing = json.loads(prompt.split("Input:\n", 1)[1])
        self.assertEqual(outgoing, brief.writer_input(self.context))
        self.assertEqual(outgoing["guidance_scope"], "EDITORIAL_HINTS_NOT_FACT_EVIDENCE")
        legacy = copy.deepcopy(self.context)
        legacy.pop(brief.POLICY_FIELD)
        legacy_prompt = x02._writer_prompt(legacy, retry=False)
        self.assertEqual(json.loads(legacy_prompt.split("Input:\n", 1)[1]), legacy)
        self.assertNotIn(brief.POLICY_VERSION, legacy_prompt)

    def test_retry_inherits_policy_and_only_the_failed_memory(self):
        original = copy.deepcopy(self.context)
        candidate_id = self.context["memories"][1]["candidate_id"]
        retry = x02._writer_retry_context(self.context, [candidate_id], [])
        self.assertEqual(retry[brief.POLICY_FIELD], brief.POLICY_VERSION)
        projected = json.loads(x02._writer_prompt(retry, retry=True).split("Input:\n", 1)[1])
        self.assertEqual([m["candidate_id"] for m in projected["memories"]], [candidate_id])
        self.assertEqual(projected["memories"][0]["facts"], brief.compact_facts(self.context["memories"][1]))
        self.assertEqual(self.context, original)

    def run_fixture(self, gateway):
        with tempfile.TemporaryDirectory() as temporary:
            return x02.run_x02(make_x02_bundle_v03(Path(temporary)), gateway)

    def test_pipeline_preserves_call_topology_and_current_output_schema(self):
        gateway = MediaGateway(display_count=3)
        result = self.run_fixture(gateway)
        media_calls = [c for c in gateway.calls if c["stage"].startswith("S10_")]
        writers = [c for c in gateway.calls if c["stage"].startswith("S11_")]
        self.assertEqual((len(media_calls), len(writers)), (1, 1))
        self.assertEqual(len(media_calls[0]["context"]["content_brief"]["materials"]), 5)
        writer_input = json.loads(writers[0]["prompt"].split("Input:\n", 1)[1])
        self.assertEqual(len(writer_input["memories"][0]["content_brief"]["materials"]), 3)
        receipt = result["decision_trace"]["content_handoff"]
        self.assertEqual(receipt["policy_version"], brief.POLICY_VERSION)
        self.assertEqual(receipt["prepared_first_writer_input_sha256"], sha256_bytes(canonical_bytes(writer_input)))
        self.assertEqual(receipt["media_comparison_inputs"][0]["prompt_sha256"],
                         sha256_bytes(media_calls[0]["prompt"].encode("utf-8")))
        self.assertEqual(receipt["additional_model_steps"], 0)
        self.assertNotIn("prepared_first_writer_input", receipt)
        self.assertNotIn("facts", receipt["media_comparison_inputs"][0])
        schema = json.loads((ROOT / "contracts/codex_x02_staged_preview_v04_1_media_v01.schema.json").read_text())
        assert_json_schema_instance(self, schema, result)

    def test_current_writer_uses_one_call_and_preserves_content_policy(self):
        gateway = MediaGateway(fail_first_writer=True)
        result = self.run_fixture(gateway)
        writers = [c for c in gateway.calls if c["stage"].startswith("S11_")]
        self.assertEqual(len(writers), 1)
        for call in writers:
            payload = json.loads(call["prompt"].split("Input:\n", 1)[1])
            self.assertEqual(payload[brief.POLICY_FIELD], brief.POLICY_VERSION)
        self.assertEqual(len(result["chapters"][0]["selected_media"]), 3)


if __name__ == "__main__":
    unittest.main()
