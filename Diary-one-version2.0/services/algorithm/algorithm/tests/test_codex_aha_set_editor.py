"""V1.73 protocol tests only; no invented image semantics or quality gold."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci import codex_aha_set_editor as editor
from diary_one_ci import codex_d4_research as research
from diary_one_ci import codex_editorial_allocation as allocation
from diary_one_ci import codex_structure_wire as wire
from diary_one_ci import x02
from tests.test_x02 import ScriptedGateway, make_x02_bundle


def fixture(*, chapters=True):
    chapter_candidates = [{
        "candidate_id": "CANONICAL_CHAPTER_1",
        "source_asset_ids": ["c1", "c2", "c3"],
        "fact_ids": ["CANONICAL_CHAPTER_FACT_1"],
        "storyline_identity": {"thesis": "协议占位章节主旨"},
    }]
    chapter_ledger = [{
        "source_index": 0, "candidate_id": "CANONICAL_CHAPTER_1",
        "validation_status": "PASSED", "selection_status": "ELIGIBLE",
        "reason_codes": [],
    }]
    aha_candidates = [{
        "candidate_id": "CANONICAL_AHA_%d" % index,
        "observation_id": "CANONICAL_OBSERVATION_%d" % index,
        "source_asset_id": "a%d" % index,
        "fact_ids": ["CANONICAL_AHA_FACT_%d" % index],
        "event_fact_ids": ["CANONICAL_AHA_FACT_%d" % index],
        "narrative_duty": "协议占位回看职责%d" % index,
        "event_kind": "DISCOVERY", "event_salience": "MEDIUM",
        "episode_code": "OTHER",
    } for index in (1, 2, 3)]
    aha_ledger = [{
        "candidate_id": item["candidate_id"], "validation_status": "PASSED",
        "selection_status": "ELIGIBLE", "reason_codes": [],
    } for item in aha_candidates]
    observations = [{
        "id": "CANONICAL_OBSERVATION_%d" % index,
        "limitations": ["UNCERTAINTY_PLACEHOLDER"] if index == 3 else [],
        "facts": [{
            "fact_id": "CANONICAL_AHA_FACT_%d" % index,
            "text": "协议占位原子事实%d" % index,
            "evidence_frame_ids": ["CANONICAL_FRAME_%d" % index],
            "support_grade": "STRONG",
        }],
    } for index in (1, 2, 3)]
    observations.append({
        "id": "CANONICAL_CHAPTER_OBSERVATION",
        "limitations": [],
        "facts": [{
            "fact_id": "CANONICAL_CHAPTER_FACT_1",
            "text": "协议占位章节事实",
            "evidence_frame_ids": ["CANONICAL_CHAPTER_FRAME"],
            "support_grade": "STRONG",
        }],
    })
    output = {
        "storyline_proposals": [{"key": "K1"}],
        "aha_proposals": [{
            "observation_id": "CANONICAL_OBSERVATION_%d" % index,
            "event_fact_ids": ["CANONICAL_AHA_FACT_%d" % index],
            "narrative_duty": "协议占位回看职责%d" % index,
            "focus_frame_id": "CANONICAL_FRAME_%d" % index,
            "moment_focus": "协议占位焦点%d" % index,
        } for index in (1, 2, 3)],
        editor.CONTEXT_FIELD: {
            "summary": "协议占位记录摘要", "uncertainty": "协议占位不确定项",
        },
        editor.OUTPUT_FIELD: {
            "chapter_keys": ["K1"] if chapters else [],
            "reason": "协议占位章节选择理由",
        },
    }
    scope = [{
        "observation_id": "CANONICAL_OBSERVATION_%d" % index,
        "event_fact_ids": ["CANONICAL_AHA_FACT_%d" % index],
    } for index in (1, 2, 3)]
    order = {value: index for index, value in enumerate(["c1", "c2", "c3", "a1", "a2", "a3"])}
    discovery = editor.compile_discovery(
        output, chapter_ledger, chapter_candidates, aha_candidates, scope, observations,
    )
    preview = editor.preview_selected_chapters(
        discovery, chapter_candidates, order, minimum=3, max_chapters=4,
    )
    context, maps = editor.editor_input(
        discovery, preview, chapter_candidates, aha_candidates, observations,
    )
    return {
        "output": output, "chapters": chapter_candidates, "chapter_ledger": chapter_ledger,
        "ahas": aha_candidates, "aha_ledger": aha_ledger, "observations": observations,
        "scope": scope, "order": order, "discovery": discovery, "preview": preview,
        "context": context, "maps": maps,
    }


def editor_output(data, selected=("A01", "A02", "A03")):
    maps = data["maps"]
    chapters = list(maps["chapters"])
    result = {
        "candidate_reviews": [{
            "candidate_id": candidate_id, "status": "STANDALONE",
            "reason": "协议占位独立回看职责",
        } for candidate_id in maps["ahas"]],
        "selected_aha_ids": list(selected),
        "chapter_aha_relations": [{
            "chapter_candidate_id": chapter_id,
            "aha_candidate_id": aha_id,
            "relation": "DISTINCT_STORY",
            "chapter_fact_ids": [maps["chapter_facts"][chapter_id][0]],
            "aha_fact_id": maps["aha_facts"][aha_id],
            "reason": "协议占位不同回看职责",
        } for chapter_id in chapters for aha_id in selected],
        "aha_aha_relations": [{
            "aha_candidate_ids": [left, right],
            "relation": "DISTINCT_STORY",
            "fact_ids": [maps["aha_facts"][left], maps["aha_facts"][right]],
            "reason": "协议占位不同回看职责",
        } for index, left in enumerate(selected) for right in selected[index + 1:]],
        "set_reason": "协议占位集合选择理由",
    }
    return result


def compile_and_execute(data, output):
    plan = editor.compile_editor(
        output, data["context"], data["maps"], data["discovery"], data["preview"],
        data["chapters"], data["ahas"],
    )
    selected = editor.execute_plan(
        plan, data["chapters"], data["chapter_ledger"], data["ahas"],
        data["aha_ledger"], data["observations"], data["order"],
        minimum=3, max_chapters=4, max_ahas=3,
    )
    return plan, selected


class AhaSetEditorTests(unittest.TestCase):
    def test_s07_schema_is_discovery_only_and_shortlist_is_bounded(self):
        base = wire.response_schema(allocation.structure_schema(x02.STRUCTURE_SCHEMA))
        schema = editor.response_schema(base)
        self.assertEqual(schema["properties"]["aha_proposals"]["maxItems"], 8)
        selection = schema["properties"][editor.OUTPUT_FIELD]
        self.assertEqual(selection["required"], ["chapter_keys", "reason"])
        self.assertNotIn("aha_selections", selection["properties"])
        self.assertNotIn("chapter_aha_relations", selection["properties"])

    def test_editor_input_has_only_request_local_references_and_no_proxy_ranking(self):
        data = fixture()
        serialized = json.dumps(data["context"], ensure_ascii=False)
        for canonical in (
            "CANONICAL_CHAPTER_1", "CANONICAL_AHA_1", "CANONICAL_OBSERVATION_1",
            "CANONICAL_AHA_FACT_1", "CANONICAL_FRAME_1",
        ):
            self.assertNotIn(canonical, serialized)
        for proxy in ("motifs", "event_kind", "quality_score", "subject_codes", "gps"):
            self.assertNotIn('"%s"' % proxy, serialized)
        self.assertEqual(list(data["maps"]["ahas"]), ["A01", "A02", "A03"])
        self.assertEqual(list(data["maps"]["chapters"]), ["C01"])

    def test_complete_editor_set_selects_three_atomic_ahas(self):
        data = fixture()
        plan, (chapters, ahas, _, audit) = compile_and_execute(data, editor_output(data))
        self.assertEqual((len(chapters), len(ahas)), (1, 3))
        self.assertEqual(len(plan["chapter_aha_relations"]), 3)
        self.assertEqual(len(plan["aha_aha_relations"]), 3)
        self.assertTrue(all(len(item["event_fact_ids"]) == 1 for item in ahas))
        self.assertEqual(audit["capacity"], 3)
        self.assertFalse(audit["automatic_fill_applied"])

    def test_no_chapter_day_still_allows_three_ahas(self):
        data = fixture(chapters=False)
        plan, (chapters, ahas, _, audit) = compile_and_execute(data, editor_output(data))
        self.assertEqual(chapters, [])
        self.assertEqual(len(ahas), 3)
        self.assertEqual(audit["capacity"], 3)
        self.assertEqual(plan["additional_model_calls"], 1)

    def test_same_story_rejects_only_later_aha_without_fill(self):
        data = fixture()
        output = editor_output(data)
        output["aha_aha_relations"][0]["relation"] = "SAME_STORY"
        _, (_, ahas, _, audit) = compile_and_execute(data, output)
        self.assertEqual([item["candidate_id"] for item in ahas], [
            "CANONICAL_AHA_1", "CANONICAL_AHA_3",
        ])
        self.assertEqual(audit["rejections"]["CANONICAL_AHA_2"], "SAME_MODEL_ALLOCATED_AHA_STORY")
        self.assertFalse(audit["automatic_fill_applied"])

    def test_missing_unselected_review_does_not_delete_valid_selected_siblings(self):
        data = fixture()
        output = editor_output(data, selected=("A01", "A02"))
        output["candidate_reviews"] = output["candidate_reviews"][:2]
        plan, (_, ahas, _, _) = compile_and_execute(data, output)
        self.assertEqual([item["candidate_id"] for item in ahas], [
            "CANONICAL_AHA_1", "CANONICAL_AHA_2",
        ])
        self.assertIn("AHA_REVIEW_MISSING", [item["code"] for item in plan["diagnostics"]])

    def test_non_standalone_candidate_cannot_be_selected(self):
        data = fixture()
        output = editor_output(data)
        output["candidate_reviews"][1]["status"] = "CHAPTER_SUPPORT"
        plan, (_, ahas, _, _) = compile_and_execute(data, output)
        self.assertEqual([item["candidate_id"] for item in ahas], [
            "CANONICAL_AHA_1", "CANONICAL_AHA_3",
        ])
        self.assertIn("AHA_SELECTION_NOT_STANDALONE", [item["code"] for item in plan["diagnostics"]])

    def test_unavailable_editor_preserves_chapter_and_closes_only_aha_lane(self):
        data = fixture()
        plan = editor.unavailable_plan(data["discovery"], "MODEL_TIMEOUT")
        chapters, ahas, _, audit = editor.execute_plan(
            plan, data["chapters"], data["chapter_ledger"], data["ahas"],
            data["aha_ledger"], data["observations"], data["order"],
            minimum=3, max_chapters=4, max_ahas=3,
        )
        self.assertEqual(len(chapters), 1)
        self.assertEqual(ahas, [])
        self.assertEqual(audit["selection_binding_status"], "AHA_SET_EDITOR_UNAVAILABLE")

    def test_gateway_routes_one_text_editor_call_to_plus(self):
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
                    stage=stage, output={}, provider=self.provider, model=self.model,
                    request_id="offline", input_tokens=1, output_tokens=1,
                    latency_seconds=0.0, model_frame_count=0, model_calls=1,
                    pricing_currency="CNY", input_rate_per_million=0.0,
                    output_rate_per_million=0.0, native_currency_per_usd=7.2,
                    pricing_basis="offline",
                )

        flash = Delegate(research.routing.FLASH)
        plus = Delegate(research.routing.PLUS)
        gateway = research.ResearchGateway(flash, plus)
        run = gateway.call(editor.EDITOR_STAGE, "p", {}, context={})
        self.assertEqual(run.model, research.routing.PLUS)
        self.assertEqual(plus.stages, [editor.EDITOR_STAGE])
        self.assertEqual(flash.stages, [])
        self.assertEqual(research.profile()["additional_model_calls"], 1)

    def test_prompts_have_general_rules_without_user_example_scenes(self):
        combined = editor.prompt_instruction() + editor.editor_prompt({})
        for example in ("小狗", "古镇", "石板路", "奶茶"):
            self.assertNotIn(example, combined)

    def test_full_x02_branch_runs_s07_s09_s11_once_and_publishes_three_ahas(self):
        class IntegrationGateway(ScriptedGateway):
            def _structure(self, context):
                output = super()._structure(context)
                candidates = context["observations"][:3]
                output["aha_proposals"] = [{
                    "observation_id": item["observation_id"],
                    "event_fact_ids": [item["facts"][0]["fact_id"]],
                    "narrative_duty": "Pipeline protocol candidate %d" % index,
                    "focus_frame_id": item["facts"][0]["evidence_frame_ids"][0],
                    "moment_focus": "Pipeline protocol focus %d" % index,
                } for index, item in enumerate(candidates, 1)]
                output[editor.CONTEXT_FIELD] = {
                    "summary": "Pipeline protocol context",
                    "uncertainty": "Semantic quality not asserted",
                }
                output[editor.OUTPUT_FIELD] = {
                    "chapter_keys": [item["key"] for item in output["storyline_proposals"]],
                    "reason": "Pipeline protocol Chapter choice",
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
                selected = [item["candidate_id"] for item in context["aha_candidates"]]
                output = {
                    "candidate_reviews": [{
                        "candidate_id": value, "status": "STANDALONE",
                        "reason": "Pipeline protocol independent duty",
                    } for value in selected],
                    "selected_aha_ids": selected,
                    "chapter_aha_relations": [{
                        "chapter_candidate_id": chapter["candidate_id"],
                        "aha_candidate_id": aha["candidate_id"],
                        "relation": "DISTINCT_STORY",
                        "chapter_fact_ids": [chapter["facts"][0]["fact_id"]],
                        "aha_fact_id": aha["fact"]["fact_id"],
                        "reason": "Pipeline protocol different duty",
                    } for chapter in context["chapters"] for aha in context["aha_candidates"]],
                    "aha_aha_relations": [{
                        "aha_candidate_ids": [left, right],
                        "relation": "DISTINCT_STORY",
                        "fact_ids": [
                            next(item["fact"]["fact_id"] for item in context["aha_candidates"]
                                 if item["candidate_id"] == left),
                            next(item["fact"]["fact_id"] for item in context["aha_candidates"]
                                 if item["candidate_id"] == right),
                        ],
                        "reason": "Pipeline protocol different duty",
                    } for index, left in enumerate(selected) for right in selected[index + 1:]],
                    "set_reason": "Pipeline protocol set choice",
                }
                return x02.StageRun(
                    stage=stage, output=output, provider=self.provider, model=self.model,
                    request_id="request-%d" % len(self.calls), input_tokens=100,
                    output_tokens=50, latency_seconds=0.01, model_frame_count=0,
                    model_calls=1, pricing_currency="USD", input_rate_per_million=1.0,
                    output_rate_per_million=2.0, native_currency_per_usd=1.0,
                    pricing_basis="test",
                )

        gateway = IntegrationGateway()
        with tempfile.TemporaryDirectory() as temporary:
            manifest = make_x02_bundle(Path(temporary), 6)
            result = x02.run_x02_v041(
                manifest, gateway, recording_editor_policy=editor.POLICY_VERSION,
            )
        self.assertEqual(len(result["chapters"]), 1)
        self.assertEqual(len(result["ahas"]), 3)
        self.assertEqual(
            [item["stage"] for item in gateway.calls].count(editor.EDITOR_STAGE), 1,
        )
        self.assertEqual(
            [item["stage"] for item in gateway.calls].count("S11_WRITER_ATTEMPT_1"), 1,
        )
        self.assertEqual(
            result["decision_trace"]["aha_set_editor"]["status"], "COMPLETED",
        )
        self.assertEqual(
            result["decision_trace"]["editorial_allocation"]["additional_model_steps"], 1,
        )


if __name__ == "__main__":
    unittest.main()
