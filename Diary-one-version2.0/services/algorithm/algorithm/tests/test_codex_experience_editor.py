"""V1.75 protocol tests; fixtures assert structure, not image semantics."""

import copy
import json
import tempfile
import unittest
import uuid
from pathlib import Path

from diary_one_ci import codex_d5_research as research
from diary_one_ci import codex_editorial_allocation as allocation
from diary_one_ci import codex_experience_editor as editor
from diary_one_ci import codex_structure_wire as wire
from diary_one_ci import codex_v174_writer as writer
from diary_one_ci import x02
from tests.test_x02 import ScriptedGateway, make_x02_bundle


def fixture():
    observations = []
    for index in range(1, 5):
        observations.append({
            "id": "OBSERVATION_%d" % index,
            "source_asset_id": "asset_%d" % index,
            "facts": [{
                "fact_id": "FACT_%d" % index,
                "text": "协议事实%d" % index,
                "evidence_frame_ids": ["FRAME_%d" % index],
                "representative_frame_id": "FRAME_%d" % index,
                "support_grade": "STRONG",
            }],
            "limitations": [],
            "event_kind": "NONE", "event_salience": "NONE",
            "episode_code": "OTHER", "subject_codes": [], "motifs": [],
            "quality_score": 0.8,
        })
    roles = [{"observation_id": item["id"], "role": "KEEP"} for item in observations]
    moments = [{
        "id": "MOMENT_%d" % index, "sequence_index": index - 1,
        "observation_ids": ["OBSERVATION_%d" % index], "roles": ["KEEP"],
    } for index in range(1, 5)]
    chapter = {
        "candidate_id": "CHAPTER_CANONICAL", "candidate_type": "CHAPTER",
        "observation_ids": ["OBSERVATION_1", "OBSERVATION_2", "OBSERVATION_3"],
        "source_asset_ids": ["asset_1", "asset_2", "asset_3"],
        "fact_ids": ["FACT_1", "FACT_2", "FACT_3"],
        "episode_code": "OTHER",
        "storyline_identity": {
            "thesis": "协议章节主题", "beat_map": [{
                "observation_id": "OBSERVATION_%d" % index,
                "fact_ids": ["FACT_%d" % index],
                "contribution": "协议贡献%d" % index,
            } for index in range(1, 4)],
        },
    }
    chapter_ledger = [{
        "source_index": 0, "candidate_id": chapter["candidate_id"],
        "validation_status": "PASSED", "selection_status": "ELIGIBLE",
        "reason_codes": [],
    }]
    output = {
        "storyline_proposals": [{"key": "K1"}], "aha_proposals": [],
        editor.CONTEXT_FIELD: {"summary": "协议摘要", "uncertainty": "协议不确定项"},
        editor.OUTPUT_FIELD: {"chapter_keys": ["K1"], "reason": "协议选择"},
    }
    scope = editor.consideration_scope(observations, roles)
    discovery = editor.compile_discovery(output, chapter_ledger, scope)
    order = {"asset_%d" % index: index - 1 for index in range(1, 5)}
    preview = editor.preview_selected_chapters(
        discovery, [chapter], order, minimum=3, max_chapters=4,
    )
    ahas, aha_ledger = editor.build_fact_candidates(
        uuid.uuid4(), observations, roles, moments, order,
    )
    context, maps = editor.editor_input(
        discovery, preview, [chapter], ahas, observations,
    )
    return {
        "observations": observations, "roles": roles, "moments": moments,
        "chapters": [chapter], "chapter_ledger": chapter_ledger,
        "ahas": ahas, "aha_ledger": aha_ledger, "scope": scope,
        "discovery": discovery, "preview": preview, "context": context,
        "maps": maps, "order": order,
    }


def editor_output(data, selected=("F004",)):
    maps = data["maps"]
    chapters = list(maps["chapters"])
    return {
        "uncovered_fact_reviews": [{
            "fact_id": fact_id, "intrinsic_value": "WORTH_REVISITING",
            "revisit_hook": "协议可回看要点", "reason": "协议覆盖审查",
        } for fact_id in maps["uncovered_fact_ids"]],
        "finalists": [{
            "fact_id": fact_id, "intrinsic_value": "WORTH_REVISITING",
            "revisit_hook": "协议可回看要点", "reason": "协议内在价值",
        } for fact_id in selected],
        "selected_ahas": [{
            "fact_id": fact_id, "moment_focus": "协议原子焦点",
            "selection_reason": "协议选择理由",
        } for fact_id in selected],
        "chapter_aha_relations": [{
            "chapter_id": chapter_id, "aha_fact_id": fact_id,
            "relation": "DISTINCT_STORY",
            "chapter_fact_ids": [maps["chapter_facts"][chapter_id][0]],
            "reason": "协议关系",
        } for chapter_id in chapters for fact_id in selected],
        "aha_aha_relations": [{
            "aha_fact_ids": [left, right], "relation": "DISTINCT_STORY",
            "reason": "协议关系",
        } for index, left in enumerate(selected) for right in selected[index + 1:]],
        "set_reason": "协议集合理由",
    }


class ExperienceEditorTests(unittest.TestCase):
    def test_s04_schema_requires_representative_frame_without_mutating_base(self):
        base = copy.deepcopy(x02.PERCEPTION_SCHEMA_GENERIC_ANIMAL)
        schema = editor.perception_schema(base)
        item = schema["properties"]["observations"]["items"]["properties"]["facts"]["items"]
        self.assertIn(editor.REPRESENTATIVE_FRAME_FIELD, item["required"])
        original = base["properties"]["observations"]["items"]["properties"]["facts"]["items"]
        self.assertNotIn(editor.REPRESENTATIVE_FRAME_FIELD, original["properties"])

    def test_invalid_representative_retains_fact_but_excludes_only_from_aha(self):
        raw = {
            "status": "OBSERVED",
            "facts": [{
                "text": "协议事实", "evidence_frame_ids": ["FRAME_1"],
                "representative_frame_id": "FRAME_OUTSIDE", "support_grade": "STRONG",
            }],
            "setting_code": "OTHER", "activity_code": "OTHER", "episode_code": "OTHER",
            "subject_codes": [], "motifs": [], "event_kind": "NONE",
            "event_salience": "NONE", "quality_score": 0.8, "limitations": [],
        }
        asset = {"asset_id": "asset_1", "media_kind": "PHOTO"}
        observation, degraded = x02._validated_observation(
            uuid.uuid4(), asset, raw, "APP_ASSET_1", {"FRAME_1"},
            unicode_motifs=True, retain_extended_fact_text=True,
            generic_animal_subjects=True, representative_fact_frame=True,
        )
        self.assertEqual(len(observation["facts"]), 1)
        self.assertIsNone(observation["facts"][0][editor.REPRESENTATIVE_FRAME_FIELD])
        self.assertEqual(editor.consideration_scope(
            [observation], [{"observation_id": observation["id"], "role": "KEEP"}],
        ), [])
        self.assertIn("RETAIN_FACT_EXCLUDE_FROM_AHA", [item["action"] for item in degraded])

    def test_s07_is_chapter_only_and_s09_receives_every_eligible_fact(self):
        schema = editor.response_schema(
            wire.response_schema(allocation.structure_schema(x02.STRUCTURE_SCHEMA))
        )
        self.assertEqual(schema["properties"]["aha_proposals"]["maxItems"], 0)
        data = fixture()
        self.assertEqual(len(data["context"]["fact_palette"]), 4)
        serialized = json.dumps(data["context"], ensure_ascii=False)
        for canonical in ("CHAPTER_CANONICAL", "OBSERVATION_1", "FACT_1", "FRAME_1"):
            self.assertNotIn(canonical, serialized)
        self.assertEqual(data["maps"]["uncovered_fact_ids"], ["F004"])
        by_fact = {item["fact_id"]: item for item in data["context"]["fact_palette"]}
        self.assertEqual(by_fact["F001"]["chapter_membership"], ["C01"])
        self.assertEqual(by_fact["F001"]["coverage_status"], "INSIDE_SELECTED_CHAPTER")
        self.assertEqual(by_fact["F004"]["chapter_membership"], [])
        self.assertEqual(by_fact["F004"]["coverage_status"], "OUTSIDE_SELECTED_CHAPTERS")

    def test_missing_uncovered_review_is_audited_and_cannot_authorize_selection(self):
        data = fixture()
        output = editor_output(data)
        output["uncovered_fact_reviews"] = []
        plan = editor.compile_editor(
            output, data["context"], data["maps"], data["discovery"], data["preview"],
        )
        self.assertIn("UNCOVERED_FACT_REVIEW_MISSING", {
            item["code"] for item in plan["diagnostics"]
        })
        self.assertEqual(plan["ahas"]["recommended_candidate_ids"], [])

    def test_chapter_member_can_still_be_aha_when_relation_is_distinct(self):
        data = fixture()
        plan = editor.compile_editor(
            editor_output(data, selected=("F003",)), data["context"], data["maps"],
            data["discovery"], data["preview"],
        )
        _, ahas, _, _ = editor.execute_plan(
            plan, data["chapters"], data["chapter_ledger"], data["ahas"],
            data["aha_ledger"], data["observations"], data["order"],
            minimum=3, max_chapters=4, max_ahas=3,
        )
        self.assertEqual([item["event_fact_ids"] for item in ahas], [["FACT_3"]])

    def test_one_relation_authority_selects_atomic_fact_and_no_fill(self):
        data = fixture()
        plan = editor.compile_editor(
            editor_output(data), data["context"], data["maps"], data["discovery"],
            data["preview"],
        )
        chapters, ahas, _, audit = editor.execute_plan(
            plan, data["chapters"], data["chapter_ledger"], data["ahas"],
            data["aha_ledger"], data["observations"], data["order"],
            minimum=3, max_chapters=4, max_ahas=3,
        )
        self.assertEqual(len(chapters), 1)
        self.assertEqual(len(ahas), 1)
        self.assertEqual(ahas[0]["event_fact_ids"], ["FACT_4"])
        self.assertEqual(ahas[0]["moment_evidence_frame_ids"], ["FRAME_4"])
        self.assertEqual(audit["search_contract"], editor.SEARCH_CONTRACT)
        self.assertFalse(audit["automatic_fill_applied"])

    def test_non_worth_finalist_and_unresolved_relation_fail_locally(self):
        data = fixture()
        output = editor_output(data, selected=("F003", "F004"))
        output["finalists"][0]["intrinsic_value"] = "WEAK"
        plan = editor.compile_editor(
            output, data["context"], data["maps"], data["discovery"], data["preview"],
        )
        _, ahas, _, audit = editor.execute_plan(
            plan, data["chapters"], data["chapter_ledger"], data["ahas"],
            data["aha_ledger"], data["observations"], data["order"],
            minimum=3, max_chapters=4, max_ahas=3,
        )
        self.assertEqual([item["event_fact_ids"] for item in ahas], [["FACT_4"]])
        self.assertFalse(audit["automatic_fill_applied"])

        unresolved = editor_output(data, selected=("F004",))
        unresolved["chapter_aha_relations"][0]["relation"] = "UNRESOLVED"
        unresolved_plan = editor.compile_editor(
            unresolved, data["context"], data["maps"], data["discovery"], data["preview"],
        )
        _, unresolved_ahas, _, unresolved_audit = editor.execute_plan(
            unresolved_plan, data["chapters"], data["chapter_ledger"], data["ahas"],
            data["aha_ledger"], data["observations"], data["order"],
            minimum=3, max_chapters=4, max_ahas=3,
        )
        self.assertEqual(unresolved_ahas, [])
        self.assertEqual(
            unresolved_audit["rejections"][data["maps"]["candidate_by_fact"]["FACT_4"]],
            "CHAPTER_AHA_RELATION_UNRESOLVED",
        )

    def test_writer_short_ids_round_trip_and_unknown_reference_is_not_guessed(self):
        data = fixture()
        chapter = data["chapters"][0]
        context = x02._writer_context(
            [chapter], [], {chapter["candidate_id"]: {
                "media": [{"observation_id": "OBSERVATION_1"}],
            }}, {}, data["observations"], storyline_v04=True, grounded_editor_v2=True,
        )
        context[x02.content_handoff.POLICY_FIELD] = x02.content_handoff.POLICY_VERSION
        context[x02.writer_exit.POLICY_FIELD] = x02.writer_exit.POLICY_VERSION
        context[x02.editorial_allocation.POLICY_FIELD] = x02.editorial_allocation.POLICY_VERSION
        context["editorial_allocation"] = {"relations": [], "diagnostics": []}
        context[x02.grounded_recording_editor.WRITER_POLICY_FIELD] = (
            x02.grounded_recording_editor.POLICY_VERSION
        )
        payload, maps = writer.encode_context(context)
        serialized = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("CHAPTER_CANONICAL", serialized)
        self.assertNotIn("FACT_1", serialized)
        decoded = writer.decode_output({
            "chapters": [{
                "candidate_id": "C01", "title": "协议标题", "text": "协议正文。",
                "claim_ids": ["F001"],
            }], "ahas": [],
        }, maps)
        self.assertEqual(decoded["chapters"][0]["candidate_id"], "CHAPTER_CANONICAL")
        self.assertEqual(decoded["chapters"][0]["claim_ids"], ["FACT_1"])
        unknown = writer.decode_output({
            "chapters": [{
                "candidate_id": "C01", "title": "协议标题", "text": "协议正文。",
                "claim_ids": ["F999"],
            }], "ahas": [],
        }, maps)
        narratives, _, invalid = x02._validate_writer_output(unknown, context)
        self.assertEqual(narratives, {})
        self.assertEqual(invalid, ["CHAPTER_CANONICAL"])


class V175Gateway(ScriptedGateway):
    def _perception(self, context):
        output = super()._perception(context)
        if context.get("fact_representative_frame_required"):
            for observation in output["observations"]:
                for fact in observation["facts"]:
                    fact[editor.REPRESENTATIVE_FRAME_FIELD] = fact["evidence_frame_ids"][0]
        return output

    def _structure(self, context):
        output = super()._structure(context)
        output[editor.CONTEXT_FIELD] = {
            "summary": "协议记录摘要", "uncertainty": "协议不确定项",
        }
        output[editor.OUTPUT_FIELD] = {
            "chapter_keys": [item["key"] for item in output["storyline_proposals"]],
            "reason": "协议 Chapter 选择",
        }
        return output

    def call(self, stage, prompt, schema, evidence=(), context=None):
        if stage != editor.EDITOR_STAGE:
            return super().call(stage, prompt, schema, evidence=evidence, context=context)
        context = context or {}
        self.calls.append({
            "stage": stage, "evidence": list(evidence), "prompt": prompt,
            "context": context,
        })
        chosen = context["fact_palette"][-1]["fact_id"]
        chapter_ids = [item["chapter_id"] for item in context["chapters"]]
        output = {
            "uncovered_fact_reviews": [{
                "fact_id": fact_id, "intrinsic_value": "WORTH_REVISITING",
                "revisit_hook": "协议可回看要点", "reason": "协议覆盖审查",
            } for fact_id in context["coverage_audit"]["uncovered_fact_ids"]],
            "finalists": [{
                "fact_id": chosen, "intrinsic_value": "WORTH_REVISITING",
                "revisit_hook": "协议可回看要点", "reason": "协议内在价值",
            }],
            "selected_ahas": [{
                "fact_id": chosen, "moment_focus": "协议焦点",
                "selection_reason": "协议选择",
            }],
            "chapter_aha_relations": [{
                "chapter_id": chapter_id, "aha_fact_id": chosen,
                "relation": "DISTINCT_STORY",
                "chapter_fact_ids": [context["chapters"][0]["facts"][0]["fact_id"]],
                "reason": "协议关系",
            } for chapter_id in chapter_ids],
            "aha_aha_relations": [], "set_reason": "协议集合",
        }
        return x02.StageRun(
            stage=stage, output=output, provider=self.provider, model=self.model,
            request_id="request-%d" % len(self.calls), input_tokens=100, output_tokens=50,
            latency_seconds=0.01, model_frame_count=0, model_calls=1,
            pricing_currency="USD", input_rate_per_million=1.0,
            output_rate_per_million=2.0, native_currency_per_usd=1.0,
            pricing_basis="test", selected_evidence=(),
        )


class V175IntegrationTests(unittest.TestCase):
    def test_full_chain_uses_full_fact_s09_and_short_writer_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = make_x02_bundle(Path(directory), 4)
            gateway = V175Gateway(storyline_groups=[[0, 1, 2]])
            result = x02.run_x02_v041(
                manifest, gateway, recording_editor_policy=editor.POLICY_VERSION,
            )
        editor_calls = [item for item in gateway.calls if item["stage"] == editor.EDITOR_STAGE]
        writer_calls = [item for item in gateway.calls if item["stage"].startswith("S11_")]
        self.assertEqual(len(editor_calls), 1)
        self.assertEqual(len(editor_calls[0]["context"]["fact_palette"]), 4)
        self.assertEqual(len(writer_calls), 1)
        serialized_writer = json.dumps(writer_calls[0]["context"], ensure_ascii=False)
        self.assertIn('"candidate_id": "C01"', serialized_writer)
        self.assertNotIn(result["decision_trace"]["chapter_set_selection"]["selected_candidate_ids"][0], serialized_writer)
        self.assertEqual((len(result["chapters"]), len(result["ahas"])), (1, 1))
        self.assertEqual(
            result["decision_trace"]["runtime_policies"]["writer_exit"],
            writer.POLICY_VERSION,
        )

    def test_writer_failure_keeps_internal_chapter_media_without_public_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = make_x02_bundle(Path(directory), 4)
            gateway = V175Gateway(storyline_groups=[[0, 1, 2]], fail_all_writer=True)
            result = x02.run_x02_v041(
                manifest, gateway, recording_editor_policy=editor.POLICY_VERSION,
            )
        self.assertEqual(gateway.writer_calls, 1)
        self.assertEqual(result["chapters"], [])
        ledger = result["decision_trace"]["media_only_chapters"]
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]["copy_status"], "UNAVAILABLE")
        self.assertNotIn("story", ledger[0])
        self.assertNotIn("title", ledger[0])
        self.assertTrue(all(
            item.get("surface_source") != "DETERMINISTIC_GROUNDED_FALLBACK"
            for item in result["decision_trace"]["writer_items"]
        ))

    def test_profile_remains_opt_in_and_routes_editor_to_plus(self):
        profile = research.profile()
        self.assertEqual(profile["deployment"], "RESEARCH_OPT_IN_ONLY")
        self.assertEqual(profile["recording_editor_policy_version"], editor.POLICY_VERSION)
        self.assertEqual(profile["stage_models"][editor.EDITOR_STAGE], research.routing.PLUS)


if __name__ == "__main__":
    unittest.main()
