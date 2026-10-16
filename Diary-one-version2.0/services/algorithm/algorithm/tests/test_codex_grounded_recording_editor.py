"""V1.72.1 protocol checks only; no synthetic image semantics or quality gold."""

import copy
import unittest

from diary_one_ci import codex_editorial_allocation as allocation
from diary_one_ci import codex_d3_research as research
from diary_one_ci import codex_grounded_recording_editor as editor
from diary_one_ci import codex_structure_wire as wire
from diary_one_ci import codex_writer_exit as writer_exit
from diary_one_ci import x02


def fixture():
    chapters = [{
        "candidate_id": "C1", "source_asset_ids": ["c1", "c2", "c3"],
        "fact_ids": ["FC1", "FC2", "FC3"],
    }, {
        "candidate_id": "C2", "source_asset_ids": ["c4", "c5", "c6"],
        "fact_ids": ["FC4", "FC5", "FC6"],
    }]
    chapter_ledger = [
        {"source_index": 0, "candidate_id": "C1", "validation_status": "PASSED",
         "selection_status": "ELIGIBLE", "reason_codes": []},
        {"source_index": 1, "candidate_id": "C2", "validation_status": "PASSED",
         "selection_status": "ELIGIBLE", "reason_codes": []},
    ]
    ahas = [{
        "candidate_id": "A1", "observation_id": "O1", "source_asset_id": "a1",
        "fact_ids": ["FA1"], "event_fact_ids": ["FA1"],
    }, {
        "candidate_id": "A2", "observation_id": "O2", "source_asset_id": "a2",
        "fact_ids": ["FA2"], "event_fact_ids": ["FA2"],
    }, {
        "candidate_id": "A3", "observation_id": "O3", "source_asset_id": "a3",
        "fact_ids": ["FA3"], "event_fact_ids": ["FA3"],
    }]
    aha_ledger = [{
        "candidate_id": item["candidate_id"], "validation_status": "PASSED",
        "selection_status": "ELIGIBLE", "reason_codes": [],
    } for item in ahas]
    observations = [{
        "id": "O%d" % index, "facts": [{
            "fact_id": "FA%d" % index,
            "text": "结构合同占位事实%d" % index,
            "evidence_frame_ids": ["FRAME%d" % index],
            "support_grade": "STRONG",
        }],
    } for index in (1, 2, 3)]
    output = {
        "storyline_proposals": [{"key": "K1"}, {"key": "K2"}],
        "aha_proposals": [{
            "observation_id": "O%d" % index,
            "event_fact_ids": ["FA%d" % index],
            "narrative_duty": "结构合同占位",
            "focus_frame_id": "FRAME%d" % index,
            "moment_focus": "单一焦点%d" % index,
        } for index in (1, 2, 3)],
        editor.CONTEXT_FIELD: {"summary": "结构合同占位", "uncertainty": "无语义质量结论"},
        editor.OUTPUT_FIELD: {
            "chapter_keys": ["K1", "K2"],
            "aha_selections": [
                {"observation_id": "O%d" % index, "fact_id": "FA%d" % index,
                 "focus_frame_id": "FRAME%d" % index,
                 "moment_focus": "单一焦点%d" % index}
                for index in (1, 2, 3)
            ],
            "chapter_aha_relations": [{
                "chapter_key": chapter_key, "observation_id": "O%d" % index,
                "relation": "DISTINCT_STORY", "chapter_fact_ids": [chapter_fact],
                "aha_fact_ids": ["FA%d" % index], "reason": "协议关系占位",
            } for chapter_key, chapter_fact in (("K1", "FC1"), ("K2", "FC4"))
              for index in (1, 2, 3)],
            "aha_aha_relations": [{
                "observation_ids": ["O%d" % left, "O%d" % right],
                "relation": "DISTINCT_STORY",
                "fact_ids": ["FA%d" % left, "FA%d" % right],
                "reason": "协议关系占位",
            } for left, right in ((1, 2), (1, 3), (2, 3))],
            "reason": "结构合同占位",
        },
    }
    scope = [{"observation_id": "O%d" % index, "event_fact_ids": ["FA%d" % index]}
             for index in (1, 2, 3)]
    order = {value: index for index, value in enumerate(
        ["c1", "c2", "c3", "c4", "c5", "c6", "a1", "a2", "a3"]
    )}
    return output, chapters, chapter_ledger, ahas, aha_ledger, observations, scope, order


def plan_and_execute(data):
    output, chapters, chapter_ledger, ahas, aha_ledger, observations, scope, order = data
    plan = editor.compile_plan(output, chapter_ledger, chapters, ahas, scope, observations)
    selected = editor.execute_plan(
        plan, chapters, chapter_ledger, ahas, aha_ledger, observations, order,
        minimum=3, max_chapters=4, max_ahas=3,
    )
    return plan, selected


class GroundedRecordingEditorTests(unittest.TestCase):
    def test_schema_requires_atomic_aha_and_complete_selected_pair_fields(self):
        base = wire.response_schema(allocation.structure_schema(x02.STRUCTURE_SCHEMA))
        before = copy.deepcopy(base)
        schema = editor.response_schema(base)
        self.assertEqual(base, before)
        fact_ids = schema["properties"]["aha_proposals"]["items"]["properties"]["event_fact_ids"]
        self.assertEqual((fact_ids["minItems"], fact_ids["maxItems"]), (1, 1))
        proposal_required = schema["properties"]["aha_proposals"]["items"]["required"]
        self.assertIn("focus_frame_id", proposal_required)
        self.assertIn("moment_focus", proposal_required)
        required = schema["properties"][editor.OUTPUT_FIELD]["required"]
        self.assertIn("chapter_aha_relations", required)
        self.assertIn("aha_aha_relations", required)

    def test_complete_matrix_selects_all_and_narrows_each_aha_to_one_fact_frame(self):
        data = fixture()
        plan, (chapters, ahas, _, aha_audit) = plan_and_execute(data)
        self.assertEqual(plan["execution_status"], "COMPLETE_CLOSED_RELATION_RECOMMENDATION_EXECUTED")
        self.assertEqual((len(chapters), len(ahas)), (2, 3))
        self.assertEqual(len(plan["chapter_aha_relations"]), 6)
        self.assertEqual(len(plan["aha_aha_relations"]), 3)
        self.assertTrue(all(len(item["event_fact_ids"]) == 1 for item in ahas))
        self.assertEqual([item["moment_evidence_frame_ids"] for item in ahas],
                         [["FRAME1"], ["FRAME2"], ["FRAME3"]])
        self.assertEqual([item["moment_focus"] for item in ahas],
                         ["单一焦点1", "单一焦点2", "单一焦点3"])
        self.assertEqual(aha_audit["search_outcome"], "ATOMIC_AHAS_WITH_CLOSED_SELECTED_PAIR_RELATIONS")

    def test_missing_chapter_relation_rejects_only_the_affected_aha(self):
        data = fixture()
        output = data[0]
        output[editor.OUTPUT_FIELD]["chapter_aha_relations"] = [
            row for row in output[editor.OUTPUT_FIELD]["chapter_aha_relations"]
            if row["observation_id"] != "O2"
        ]
        plan, (chapters, ahas, _, aha_audit) = plan_and_execute(data)
        self.assertEqual(len(chapters), 2)
        self.assertEqual([item["candidate_id"] for item in ahas], ["A1", "A3"])
        self.assertEqual(aha_audit["rejections"]["A2"], "CHAPTER_AHA_RELATION_UNRESOLVED")
        self.assertEqual(plan["execution_status"], "PARTIAL_OR_UNRESOLVED_RECOMMENDATION")

    def test_same_story_aha_relation_rejects_later_card_without_replacement(self):
        data = fixture()
        row = next(row for row in data[0][editor.OUTPUT_FIELD]["aha_aha_relations"]
                   if row["observation_ids"] == ["O1", "O2"])
        row["relation"] = "SAME_STORY"
        plan, (_, ahas, _, aha_audit) = plan_and_execute(data)
        self.assertEqual([item["candidate_id"] for item in ahas], ["A1", "A3"])
        self.assertEqual(aha_audit["rejections"]["A2"], "SAME_MODEL_ALLOCATED_AHA_STORY")
        self.assertFalse(aha_audit["automatic_fill_applied"])
        self.assertEqual(plan["additional_model_calls"], 0)

    def test_non_atomic_proposal_cannot_bind_as_selected_aha(self):
        data = fixture()
        data[3][0]["event_fact_ids"] = ["FA1", "FA1B"]
        plan, (_, ahas, _, aha_audit) = plan_and_execute(data)
        self.assertEqual([item["candidate_id"] for item in ahas], ["A2", "A3"])
        self.assertIn("AHA_PROPOSAL_NOT_ATOMIC", [
            item["code"] for item in plan["ahas"]["diagnostics"]
        ])
        self.assertNotIn("A1", aha_audit["recommended_candidate_ids"])

    def test_focus_frame_must_belong_to_fact_and_match_proposal(self):
        data = fixture()
        data[0][editor.OUTPUT_FIELD]["aha_selections"][1]["focus_frame_id"] = "OTHER"
        plan, (_, ahas, _, _) = plan_and_execute(data)
        self.assertEqual([item["candidate_id"] for item in ahas], ["A1", "A3"])
        self.assertIn("AHA_SELECTION_FOCUS_COPY_MISMATCH", [
            item["code"] for item in plan["ahas"]["diagnostics"]
        ])

        data = fixture()
        data[0]["aha_proposals"][1]["focus_frame_id"] = "OTHER"
        data[0][editor.OUTPUT_FIELD]["aha_selections"][1]["focus_frame_id"] = "OTHER"
        plan, (_, ahas, _, _) = plan_and_execute(data)
        self.assertEqual([item["candidate_id"] for item in ahas], ["A1", "A3"])
        self.assertIn("AHA_FOCUS_FRAME_NOT_IN_SELECTED_FACT", [
            item["code"] for item in plan["ahas"]["diagnostics"]
        ])

    def test_writer_schema_and_local_gate_accept_24_and_reject_25(self):
        schema = editor.writer_response_schema(x02.WRITER_SCHEMA)
        self.assertEqual(schema["properties"]["ahas"]["items"]["properties"]["text"]["maxLength"], 24)
        context = {
            "locale": "zh-Hans",
            "writer_grounding_policy": x02.X02_WRITER_GROUNDING_POLICY,
            writer_exit.POLICY_FIELD: writer_exit.POLICY_VERSION,
            editor.WRITER_POLICY_FIELD: editor.POLICY_VERSION,
            "memories": [{
                "candidate_id": "A1", "memory_type": "AHA",
                "facts": [{"fact_id": "F1", "text": "结构合同占位事实"}],
                "event_fact_ids": ["F1"],
                "moment_focus": "单一焦点",
                "selected_media": [{"evidence_frame_ids": ["FRAME1"]}],
            }],
        }
        def output(text):
            return {"chapters": [], "ahas": [{
                "candidate_id": "A1", "title": "瞬间", "text": text,
                "claim_ids": ["F1"],
            }]}
        passed, audit, invalid = x02._validate_writer_output(output("一" * 23 + "。"), context)
        self.assertIn("A1", passed)
        self.assertEqual((audit[0]["text_visible_characters"], invalid), (24, []))
        failed, audit, invalid = x02._validate_writer_output(output("一" * 24 + "。"), context)
        self.assertEqual(failed, {})
        self.assertEqual(invalid, ["A1"])
        self.assertIn("AHA_MOMENT_LINE_OVER_24", audit[0]["reason_codes"])

    def test_writer_context_preserves_policy_and_focus_across_derived_contexts(self):
        context = {
            "locale": "zh-Hans",
            editor.WRITER_POLICY_FIELD: editor.POLICY_VERSION,
            "memories": [{
                "candidate_id": "A1", "memory_type": "AHA",
                "facts": [{"fact_id": "F1", "text": "结构合同占位事实"}],
                "event_fact_ids": ["F1"], "moment_focus": "单一焦点",
                "narrative_duty": "结构合同占位", "selected_media": [],
            }],
        }
        derived = x02._writer_retry_context(context, ["A1"], [])
        self.assertEqual(derived[editor.WRITER_POLICY_FIELD], editor.POLICY_VERSION)
        payload = editor.writer_input(context)
        self.assertEqual(payload["memories"][0]["moment_focus"], "单一焦点")
        self.assertEqual(payload[editor.WRITER_POLICY_FIELD], editor.POLICY_VERSION)

    def test_grounded_aha_has_no_deterministic_fallback_exit(self):
        context = {
            "locale": "zh-Hans",
            editor.WRITER_POLICY_FIELD: editor.POLICY_VERSION,
            "memories": [
                {"candidate_id": "C1", "memory_type": "CHAPTER"},
                {"candidate_id": "A1", "memory_type": "AHA"},
            ],
        }
        self.assertEqual(x02._writer_fallback_ids(context, {}), ["C1"])
        self.assertEqual(x02._writer_fallback_ids(context, {"C1": {}}), [])

    def test_research_gateway_routes_writer_once_to_plus(self):
        class Delegate:
            provider = "offline"
            credential_environment = "OFFLINE"
            ready = True

            def __init__(self, model):
                self.model = model
                self.stages = []

            def call(self, stage, prompt, schema, evidence=(), context=None):
                self.stages.append(stage)
                return x02.StageRun(
                    stage=stage, output={"chapters": [], "ahas": []},
                    provider=self.provider, model=self.model, request_id="offline",
                    input_tokens=1, output_tokens=1, latency_seconds=0.0,
                    model_frame_count=0, model_calls=1, pricing_currency="CNY",
                    input_rate_per_million=0.0, output_rate_per_million=0.0,
                    native_currency_per_usd=7.2, pricing_basis="offline",
                )

        flash, plus = Delegate(research.prior.FLASH), Delegate(research.prior.PLUS)
        gateway = research.ResearchGateway(flash, plus)
        writer = gateway.call("S11_WRITER_ATTEMPT_1", "p", {})
        visual = gateway.call("S10_CHAPTER_VISUAL_SELECTION_01", "p", {})
        self.assertEqual(writer.model, research.prior.PLUS)
        self.assertEqual(visual.model, research.prior.FLASH)
        self.assertEqual(plus.stages, ["S11_WRITER_ATTEMPT_1"])
        self.assertEqual(flash.stages, ["S10_CHAPTER_VISUAL_SELECTION_01"])
        self.assertEqual(research.profile()["stage_models"]["S11_WRITER_*"], research.prior.PLUS)

    def test_prompts_are_general_evidence_rules_without_scene_examples(self):
        combined = editor.prompt_instruction() + editor.perception_instruction()
        for example in ("小狗", "古镇", "石板路", "奶茶"):
            self.assertNotIn(example, combined)


if __name__ == "__main__":
    unittest.main()
