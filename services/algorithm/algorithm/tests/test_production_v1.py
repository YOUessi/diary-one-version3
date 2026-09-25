import copy
import json
import tempfile
import unittest
from pathlib import Path

from diary_one_ci.production_v1 import (
    CanonicalConceptRegistry,
    PipelineContractError,
    ProductionPipelineV1,
    load_production_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "fixtures" / "production_v1" / "ancient_town_reference_day.json"
REGISTRY_PATH = REPO_ROOT / "contracts" / "canonical_concept_registry_v1.json"
SCHEMA_PATH = REPO_ROOT / "contracts" / "production_pipeline_v1.schema.json"
OUTPUT_SCHEMA_PATH = (
    REPO_ROOT / "contracts" / "production_pipeline_v1.outputs.schema.json"
)


def fixture():
    return copy.deepcopy(load_production_manifest(FIXTURE_PATH))


def expand_to_five_chapters(payload):
    base = payload["memories"][0]
    chapter_ids = [base["memory_id"]]
    for index in range(2, 6):
        clone = copy.deepcopy(base)
        clone["memory_id"] = f"chapter_{index}"
        clone["candidate_id"] = f"candidate_chapter_{index}"
        clone["capture_start_ms"] = base["capture_start_ms"] + index * 3_600_000
        for media in clone["active_media"]:
            media["media_id"] = f"{media['media_id']}_{index}"
        payload["memories"].append(clone)
        chapter_ids.append(clone["memory_id"])
    payload["s09"]["selected_chapter_ids"] = chapter_ids
    return payload


class ProductionPipelineV1Tests(unittest.TestCase):
    def setUp(self):
        self.pipeline = ProductionPipelineV1.from_registry_path(REGISTRY_PATH)

    def test_happy_path_runs_s00_through_s13_reference_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = self.pipeline.run(fixture(), Path(tmp))
            manifest = json.loads((output / "run_manifest.json").read_text())
            self.assertEqual(
                manifest["full_flow_status"],
                "REFERENCE_VALIDATED_NOT_CLOUD_PRODUCTION",
            )
            self.assertEqual(
                [stage["stage_id"] for stage in manifest["stages"]],
                [
                    "S00",
                    "S01",
                    "S02",
                    "S03",
                    "S04",
                    "S05",
                    "S06",
                    "S07",
                    "S08",
                    "S09",
                    "S10",
                    "S11",
                    "S12A",
                    "S13A",
                    "S12B",
                    "S13B",
                ],
            )
            materialization = json.loads(
                (output / "s13_materialization_bundle.json").read_text()
            )
            self.assertEqual(len(materialization["activation_deltas"]), 1)
            self.assertEqual(
                materialization["activation_deltas"][0]["to_route_id"],
                "route_hall_photo",
            )
            self.assertTrue((output / "user_diary_export.json").exists())
            self.assertTrue((output / "internal_audit_run.json").exists())
            diary = json.loads((output / "user_diary_export.json").read_text())
            self.assertEqual(len(diary["chapters"]), 1)
            self.assertEqual(len(diary["ahas"]), 1)
            self.assertNotIn("memories", diary)
            chapter_narrative = diary["chapters"][0]["narrative"]
            self.assertEqual(
                set(chapter_narrative), {"title", "story", "time_label"}
            )
            self.assertNotIn("surface_claim_refs", chapter_narrative)
            self.assertNotIn("span_bindings", chapter_narrative)

    def test_reference_run_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self.pipeline.run(fixture(), Path(tmp))
            first_manifest = (first / "run_manifest.json").read_text()
            second = self.pipeline.run(fixture(), Path(tmp))
            self.assertEqual(first, second)
            self.assertEqual(first_manifest, (second / "run_manifest.json").read_text())

    def test_display_labels_are_derived_and_entity_stays_separate(self):
        result = self.pipeline.validate(fixture())
        chapter = result["s11"]["memories"][0]
        self.assertEqual(
            [label["label"] for label in chapter["display_label_candidates"]],
            ["城市漫步", "古镇街区"],
        )
        self.assertEqual(
            chapter["entity_index_links"][0]["display_name"], "周庄古镇"
        )
        assigned_ids = {
            decision["concept_id"]
            for decision in chapter["canonical_tag_decisions"]
        }
        self.assertNotIn("place_zhouzhuang_ancient_town", assigned_ids)

    def test_tag_evidence_must_come_from_its_cited_claims(self):
        payload = fixture()
        payload["memories"][0]["canonical_assignments"][0][
            "evidence_refs"
        ] = ["unrelated_observation"]
        with self.assertRaisesRegex(
            PipelineContractError, "TAG_EVIDENCE_NOT_IN_CLAIMS"
        ):
            self.pipeline.validate(payload)

    def test_entity_evidence_must_come_from_its_cited_claims(self):
        payload = fixture()
        payload["memories"][0]["entity_links"][0]["evidence_refs"] = [
            "unrelated_observation"
        ]
        with self.assertRaisesRegex(
            PipelineContractError, "ENTITY_EVIDENCE_NOT_IN_CLAIMS"
        ):
            self.pipeline.validate(payload)

    def test_zero_canonical_assignments_is_allowed_for_chapter(self):
        payload = fixture()
        payload["memories"][0]["canonical_assignments"] = []
        result = self.pipeline.validate(payload)
        self.assertEqual(
            result["s11"]["memories"][0]["canonical_tag_decisions"], []
        )

    def test_upstream_revision_mismatch_is_rejected(self):
        payload = fixture()
        payload["upstream_stages"][7]["revision_id"] = "stale_revision"
        with self.assertRaisesRegex(PipelineContractError, "S07:REVISION_MISMATCH"):
            self.pipeline.validate(payload)

    def test_unregistered_free_tag_is_rejected(self):
        payload = fixture()
        payload["memories"][0]["canonical_assignments"][0][
            "concept_id"
        ] = "ACTIVITY.GREAT_ANCIENT_TOWN_DAY"
        with self.assertRaisesRegex(PipelineContractError, "UNREGISTERED_CONCEPT"):
            self.pipeline.validate(payload)

    def test_multiple_assignments_in_one_facet_are_rejected(self):
        payload = fixture()
        payload["memories"][0]["canonical_assignments"][1][
            "concept_id"
        ] = "ACTIVITY.WALKING"
        with self.assertRaisesRegex(
            PipelineContractError, "MULTIPLE_ASSIGNMENTS_PER_FACET"
        ):
            self.pipeline.validate(payload)

    def test_light_affect_needs_exact_permission(self):
        payload = fixture()
        payload["memories"][1]["narrative"].pop("light_affect_permission_ref")
        with self.assertRaisesRegex(
            PipelineContractError, "LIGHT_AFFECT_PERMISSION_MISSING"
        ):
            self.pipeline.validate(payload)

    def test_unsupported_affective_claim_is_rejected(self):
        payload = fixture()
        payload["memories"][1]["narrative"][
            "moment_line"
        ] = "小猫碰倒纸杯，留下难忘一刻。"
        with self.assertRaisesRegex(
            PipelineContractError, "UNSUPPORTED_AFFECTIVE_ASSERTION"
        ):
            self.pipeline.validate(payload)

    def test_claim_without_evidence_is_rejected(self):
        payload = fixture()
        payload["memories"][0]["claims"][0]["evidence_refs"] = []
        with self.assertRaisesRegex(PipelineContractError, "CLAIM_EVIDENCE_EMPTY"):
            self.pipeline.validate(payload)

    def test_writer_cost_and_model_provenance_is_required(self):
        payload = fixture()
        payload.pop("writer_provenance")
        with self.assertRaisesRegex(
            PipelineContractError, "ENVELOPE_INVALID"
        ):
            self.pipeline.validate(payload)

    def test_every_narrative_surface_requires_span_bindings(self):
        payload = fixture()
        payload["memories"][0]["narrative"].pop("span_bindings")
        with self.assertRaisesRegex(
            PipelineContractError, "SPAN_BINDINGS_MISSING"
        ):
            self.pipeline.validate(payload)

    def test_unbound_story_text_is_rejected(self):
        payload = fixture()
        payload["memories"][0]["narrative"]["span_bindings"].pop()
        with self.assertRaisesRegex(
            PipelineContractError, "UNBOUND_SURFACE_TEXT"
        ):
            self.pipeline.validate(payload)

    def test_span_cannot_cite_claim_outside_surface_plan(self):
        payload = fixture()
        payload["memories"][0]["narrative"]["span_bindings"][1][
            "claim_refs"
        ] = ["claim_exact_place"]
        with self.assertRaisesRegex(
            PipelineContractError, "UNPLANNED_SPAN_CLAIM"
        ):
            self.pipeline.validate(payload)

    def test_tone_permission_cannot_launder_arbitrary_adjectives(self):
        payload = fixture()
        narrative = payload["memories"][1]["narrative"]
        narrative["moment_line"] = "小猫可爱地碰倒了纸杯。"
        narrative["span_bindings"][1]["text"] = "可爱地"
        with self.assertRaisesRegex(
            PipelineContractError, "TONE_SPAN_TEXT_NOT_PERMITTED"
        ):
            self.pipeline.validate(payload)

    def test_media_ids_are_unique_across_the_day_revision(self):
        payload = fixture()
        payload["memories"][1]["active_media"][0]["media_id"] = "media_gate"
        with self.assertRaisesRegex(
            PipelineContractError, "DUPLICATE_GLOBAL_MEDIA_ID"
        ):
            self.pipeline.validate(payload)

    def test_day_state_and_membership_must_agree(self):
        payload = fixture()
        payload["s09"]["day_state"] = "HIGHLIGHT_DAY"
        with self.assertRaisesRegex(
            PipelineContractError, "HIGHLIGHT_DAY_CAPACITY_INVALID"
        ):
            self.pipeline.validate(payload)

    def test_empty_day_exports_without_hq_requests(self):
        payload = fixture()
        payload["memories"] = []
        payload["hq_requests"] = []
        payload["s09"] = {
            "day_state": "EMPTY_DAY",
            "selected_chapter_ids": [],
            "selected_aha_ids": [],
            "chapter_aha_pair_decisions": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            output = self.pipeline.run(payload, Path(tmp))
            pre = json.loads(
                (output / "s12_pre_materialization_decision.json").read_text()
            )
            self.assertEqual(
                pre["decision"], "NO_MATERIALIZATION_EMPTY_EXPORT_ALLOWED"
            )
            diary = json.loads((output / "user_diary_export.json").read_text())
            self.assertEqual(diary["day_state"], "EMPTY_DAY")
            self.assertEqual(diary["chapters"], [])
            self.assertEqual(diary["ahas"], [])

    def test_highlight_day_has_one_aha_and_no_chapter(self):
        payload = fixture()
        payload["memories"] = [payload["memories"][1]]
        payload["hq_requests"] = [payload["hq_requests"][3]]
        payload["s09"] = {
            "day_state": "HIGHLIGHT_DAY",
            "selected_chapter_ids": [],
            "selected_aha_ids": ["aha_playful_cat"],
            "chapter_aha_pair_decisions": [],
        }
        result = self.pipeline.validate(payload)
        self.assertEqual(result["s12_pre"]["chapter_count"], 0)
        self.assertEqual(result["s12_pre"]["aha_count"], 1)

    def test_final_fifth_chapter_requires_exceptional_gate(self):
        payload = expand_to_five_chapters(fixture())
        with self.assertRaisesRegex(
            PipelineContractError, "FIFTH_CHAPTER_GATE_REQUIRED"
        ):
            self.pipeline.validate(payload)

    def test_preview_never_allows_five_chapters(self):
        payload = expand_to_five_chapters(fixture())
        payload["run"]["revision_kind"] = "PREVIEW"
        payload["s09"]["fifth_chapter_gate"] = "PASS"
        with self.assertRaisesRegex(
            PipelineContractError, "PREVIEW_CAPACITY_INVALID"
        ):
            self.pipeline.validate(payload)

    def test_all_chapter_aha_pairs_need_independence_decisions(self):
        payload = fixture()
        payload["s09"]["chapter_aha_pair_decisions"] = []
        with self.assertRaisesRegex(
            PipelineContractError, "PAIR_DECISION_COVERAGE_INVALID"
        ):
            self.pipeline.validate(payload)

    def test_selected_memory_order_must_be_chronological(self):
        payload = fixture()
        second = copy.deepcopy(payload["memories"][0])
        second["memory_id"] = "chapter_evening"
        second["candidate_id"] = "candidate_chapter_evening"
        second["capture_start_ms"] = 64800000
        for item in second["active_media"]:
            item["media_id"] = f"{item['media_id']}_evening"
        payload["memories"].append(second)
        payload["s09"]["selected_chapter_ids"] = [
            "chapter_evening",
            "chapter_ancient_town",
        ]
        with self.assertRaisesRegex(
            PipelineContractError, "CANONICAL_MEMORY_ORDER_INVALID"
        ):
            self.pipeline.validate(payload)

    def test_two_item_chapter_requires_compact_pair_gate(self):
        payload = fixture()
        payload["memories"][0]["active_media"].pop()
        payload["hq_requests"] = [
            request
            for request in payload["hq_requests"]
            if request["request_id"] != "hq_river"
        ]
        with self.assertRaisesRegex(
            PipelineContractError, "COMPACT_PAIR_GATE_REQUIRED"
        ):
            self.pipeline.validate(payload)

    def test_aha_requires_exactly_one_visible_media(self):
        payload = fixture()
        payload["memories"][1]["active_media"] = []
        payload["hq_requests"] = [
            request
            for request in payload["hq_requests"]
            if request["request_id"] != "hq_cat_peak"
        ]
        with self.assertRaisesRegex(
            PipelineContractError, "AHA_SINGLE_MEDIA_REQUIRED"
        ):
            self.pipeline.validate(payload)

    def test_aha_body_cannot_use_five_second_video(self):
        payload = fixture()
        payload["memories"][1]["active_media"][0]["format"] = "VIDEO_5S"
        payload["hq_requests"][3]["routes"][0]["format"] = "VIDEO_5S"
        with self.assertRaisesRegex(
            PipelineContractError, "AHA_MEDIA_FORMAT_INVALID"
        ):
            self.pipeline.validate(payload)

    def test_aha_fallback_cannot_switch_to_five_second_video(self):
        payload = fixture()
        payload["hq_requests"][3]["routes"].append(
            {
                "route_id": "route_cat_video",
                "priority": 1,
                "format": "VIDEO_5S",
                "source_ref": "reference://manual_video_03/4700-9700",
                "evidence_anchor_ref": "anchor_cat_peak",
                "semantic_scope_id": "scope_cat_cup_peak",
                "source_family_id": "source_family_cat_peak",
                "reference_outcome": "SUCCESS",
            }
        )
        with self.assertRaisesRegex(
            PipelineContractError, "AHA_ROUTE_FORMAT_INVALID"
        ):
            self.pipeline.validate(payload)

    def test_transient_materialization_failure_holds_without_export(self):
        payload = fixture()
        payload["hq_requests"][0]["routes"][0][
            "reference_outcome"
        ] = "TRANSIENT_FAILURE"
        with tempfile.TemporaryDirectory() as tmp:
            output = self.pipeline.run(payload, Path(tmp))
            manifest = json.loads((output / "run_manifest.json").read_text())
            self.assertEqual(manifest["full_flow_status"], "HOLD_NO_REFERENCE_EXPORT")
            self.assertFalse((output / "user_diary_export.json").exists())
            self.assertFalse((output / "s12_activation_decision.json").exists())

    def test_prevalidated_d1_survivor_can_remove_one_terminal_member(self):
        payload = fixture()
        payload["hq_requests"][2]["routes"][0][
            "reference_outcome"
        ] = "TERMINAL_FAILURE"
        payload["memories"][0]["d1_survivor_plans"] = [
            {
                "failed_media_id": "media_river",
                "survivor_media_ids": ["media_gate", "media_hall"],
                "decision": "PASS",
                "resulting_compact_pair_gate": "PASS",
                "alternate_hero_media_id": None,
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            output = self.pipeline.run(payload, Path(tmp))
            materialization = json.loads(
                (output / "s13_materialization_bundle.json").read_text()
            )
            self.assertEqual(materialization["omitted_media_ids"], ["media_river"])
            self.assertEqual(
                materialization["activation_deltas"][-1]["delta_type"],
                "D1_SURVIVOR_ACTIVATED",
            )
            diary = json.loads((output / "user_diary_export.json").read_text())
            self.assertEqual(len(diary["chapters"][0]["visible_media"]), 2)

    def test_d1_that_invalidates_a_required_claim_holds_for_replan(self):
        payload = fixture()
        payload["hq_requests"][2]["routes"][0][
            "reference_outcome"
        ] = "TERMINAL_FAILURE"
        payload["memories"][0]["d1_survivor_plans"] = [
            {
                "failed_media_id": "media_river",
                "survivor_media_ids": ["media_gate", "media_hall"],
                "decision": "PASS",
                "resulting_compact_pair_gate": "PASS",
                "alternate_hero_media_id": None,
            }
        ]
        payload["memories"][0]["claims"][2]["required_media_ids"] = [
            "media_river"
        ]
        with tempfile.TemporaryDirectory() as tmp:
            output = self.pipeline.run(payload, Path(tmp))
            decision = json.loads(
                (output / "s12_activation_decision.json").read_text()
            )
            self.assertEqual(decision["status"], "HOLD")
            self.assertEqual(
                decision["reason_code"], "ACTIVATION_INVALIDATES_CLAIM"
            )
            self.assertFalse((output / "user_diary_export.json").exists())

    def test_d1_hero_loss_requires_and_activates_predeclared_alternate(self):
        payload = fixture()
        payload["hq_requests"][0]["routes"][0][
            "reference_outcome"
        ] = "TERMINAL_FAILURE"
        payload["memories"][0]["d1_survivor_plans"] = [
            {
                "failed_media_id": "media_gate",
                "survivor_media_ids": ["media_hall", "media_river"],
                "decision": "PASS",
                "resulting_compact_pair_gate": "PASS",
                "alternate_hero_media_id": "media_hall",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            output = self.pipeline.run(payload, Path(tmp))
            diary = json.loads((output / "user_diary_export.json").read_text())
            media = diary["chapters"][0]["visible_media"]
            heroes = [item["media_id"] for item in media if item["is_hero"]]
            self.assertEqual(heroes, ["media_hall"])

    def test_dormant_d1_plan_is_validated_before_hq_work(self):
        payload = fixture()
        payload["memories"][0]["d1_survivor_plans"] = [
            {
                "failed_media_id": "media_river",
                "survivor_media_ids": ["media_gate"],
                "decision": "PASS",
                "resulting_compact_pair_gate": "PASS",
                "alternate_hero_media_id": None,
            }
        ]
        with self.assertRaisesRegex(
            PipelineContractError, "D1_SURVIVOR_SET_INVALID"
        ):
            self.pipeline.validate(payload)

    def test_fallback_created_cross_memory_reuse_requires_a_decision(self):
        payload = fixture()
        payload["hq_requests"][1]["routes"][1][
            "source_family_id"
        ] = "source_family_cat_peak"
        with tempfile.TemporaryDirectory() as tmp:
            output = self.pipeline.run(payload, Path(tmp))
            decision = json.loads(
                (output / "s12_activation_decision.json").read_text()
            )
            self.assertEqual(decision["status"], "HOLD")
            self.assertEqual(
                decision["reason_code"], "ACTIVATED_REUSE_DECISION_INVALID"
            )
            self.assertFalse((output / "user_diary_export.json").exists())

    def test_predeclared_fallback_reuse_must_still_be_exact(self):
        payload = fixture()
        payload["hq_requests"][1]["routes"][1][
            "source_family_id"
        ] = "source_family_cat_peak"
        payload["cross_memory_reuse_decisions"] = [
            {
                "source_family_id": "source_family_cat_peak",
                "memory_ids": ["chapter_ancient_town", "aha_playful_cat"],
                "decision": "NECESSARY_EXACT_REUSE",
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            output = self.pipeline.run(payload, Path(tmp))
            decision = json.loads(
                (output / "s12_activation_decision.json").read_text()
            )
            self.assertEqual(decision["status"], "HOLD")
            self.assertEqual(
                decision["reason_code"], "ACTIVATED_REUSE_NOT_EXACT"
            )
            self.assertFalse((output / "user_diary_export.json").exists())

    def test_fallback_cannot_change_semantic_scope(self):
        payload = fixture()
        payload["hq_requests"][1]["routes"][1][
            "semantic_scope_id"
        ] = "different_scope"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(
                PipelineContractError, "FALLBACK_SCOPE_CHANGED"
            ):
                self.pipeline.run(payload, Path(tmp))

    def test_contract_files_are_valid_json_and_registry_is_acyclic(self):
        schema = json.loads(SCHEMA_PATH.read_text())
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        output_schema = json.loads(OUTPUT_SCHEMA_PATH.read_text())
        self.assertEqual(len(output_schema["oneOf"]), 6)
        registry = CanonicalConceptRegistry.from_path(REGISTRY_PATH)
        self.assertEqual(registry.require_active("ACTIVITY.CITY_WALK").facet, "ACTIVITY")


if __name__ == "__main__":
    unittest.main()
