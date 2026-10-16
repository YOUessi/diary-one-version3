"""Real-record protocol checks, not invented image errors or semantic gold.

We supply controlled recommendation IDs to verify execution. They are NOT new
model outputs, user labels or proof of better Chapter/Aha quality. No network.
"""

import copy
import hashlib
import json
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from diary_one_ci import codex_d2_research as research
from diary_one_ci import codex_recording_editor as editor
from diary_one_ci import codex_s07_research as prior
from diary_one_ci import codex_structure_wire as wire
from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes


ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "var/codex_v1_70_full_chain_execution"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def record(pack):
    directory = AREA / ("pack_%d/round_1" % pack)
    result = load(directory / "codex_full_run.json")["result"]
    requests = [load(p) for p in sorted((directory / "codex_stage_calls").glob("codex_[0-9][0-9][0-9]_request.json"))]
    request = next(q for q in requests if q["stage"] == prior.S07)
    raw = load(directory / ("codex_stage_calls/codex_%03d_response.json" % request["index"]))["output"]
    manifest = load(directory / "codex_manifest.json")
    asset_order = {a["asset_id"]: a["sequence_index"] for a in manifest["assets"]}
    namespace = uuid.UUID(result["session_id"])
    roles = result["decision_trace"]["observation_roles"]
    normalized, _ = wire.normalize_output(raw)
    args = (namespace, result["observations"], roles, result["moments"], normalized, asset_order)
    old_ahas, _ = x02._build_aha_candidates(*args, value_first=True)
    # Convert archived candidate fields to native proposal SHAPE only. No new
    # image descriptions or quality judgments. The frozen raw file is untouched.
    raw["aha_proposals"] = [{"observation_id": a["observation_id"],
                             "event_fact_ids": list(a["event_fact_ids"]),
                             "narrative_duty": a["narrative_duty"]} for a in old_ahas]
    old = result["decision_trace"]
    keys = {e["candidate_id"]: e["candidate_key"] for e in old["chapter_candidates"]
            if e["validation_status"] == "PASSED"}
    aha_ids = {a["candidate_id"]: a["observation_id"] for a in old_ahas}
    raw.pop("editorial_order")
    raw[editor.OUTPUT_FIELD] = {
        "chapter_keys": [keys[cid] for cid in old["chapter_set_selection"]["selected_candidate_ids"]],
        "observation_ids": [aha_ids[cid] for cid in old["aha_set_selection"]["selected_candidate_ids"]],
        "reason": "OFFLINE_ARCHIVED_MEMBERSHIP_PROTOCOL_CHECK_NOT_MODEL_JUDGMENT",
    }
    raw[editor.CONTEXT_FIELD] = {"summary": "OFFLINE_PROTOCOL_CONTEXT_NOT_REAL_MODEL_OVERVIEW",
                                "uncertainty": "CAPTURE_TIME_GPS_WEAR_DURATION_UNKNOWN"}
    return {"directory": directory, "result": result, "requests": requests, "request": request,
            "raw": raw, "asset_order": asset_order, "namespace": namespace, "roles": roles,
            "scope": editor.consideration_scope(result["observations"], roles)}


def compile_record(r):
    normalized, _ = wire.normalize_output(r["raw"])
    args = (r["namespace"], r["result"]["observations"], r["roles"], r["result"]["moments"],
            normalized, r["asset_order"])
    chapters, cl = x02._build_storyline_candidates(*args)
    ahas, al = x02._build_aha_candidates(*args, value_first=True, evidence_nominations_only=True)
    relations = x02.editorial_allocation.compile_relations(normalized, chapters, cl, ahas)
    plan = editor.compile_plan(normalized, cl, ahas, r["scope"])
    return plan, chapters, cl, ahas, al, relations


def select(r):
    plan, chapters, cl, ahas, al, relations = compile_record(r)
    c, a, ca, aa = editor.execute_plan(plan, chapters, cl, ahas, al, r["asset_order"], relations,
                                      minimum=3, max_chapters=4, max_ahas=3)
    return plan, c, a, ca, aa, cl, al


@unittest.skipUnless((AREA / "pack_3/round_1/codex_full_run.json").exists(), "Private real records unavailable")
class RecordingEditorTests(unittest.TestCase):
    def test_real_supported_scope_includes_previously_non_event_observations(self):
        counts = []
        for pack in (1, 2, 3):
            r = record(pack)
            before = copy.deepcopy(r)
            expected = {o["id"] for o in r["result"]["observations"]
                        if next(e["role"] for e in r["roles"] if e["observation_id"] == o["id"]) == "KEEP"
                        and x02._supported_aha_fact_ids(o)}
            self.assertEqual({s["observation_id"] for s in r["scope"]}, expected)
            self.assertEqual(r, before)
            old_scope = r["request"]["context"]["aha_relation_scope"]
            self.assertLessEqual({s["observation_id"] for s in old_scope}, expected)
            counts.append((len(old_scope), len(expected)))
        r = record(3)
        observation = r["result"]["observations"][48]
        self.assertEqual(observation["event_kind"], "NONE")
        self.assertIn(observation["id"], {s["observation_id"] for s in r["scope"]})
        self.assertNotIn(observation["id"], {s["observation_id"] for s in r["request"]["context"]["aha_relation_scope"]})
        self.assertTrue(all(new > old for old, new in counts))

    def test_three_real_sets_execute_exact_subset_without_proxy_ranking(self):
        for pack in (1, 2, 3):
            r = record(pack)
            with patch.object(x02, "_storyline_selection_value", side_effect=AssertionError("legacy score")), \
                 patch.object(x02, "_aha_rank_inputs", side_effect=AssertionError("legacy score")):
                plan, c, a, ca, aa, _, _ = select(r)
            old = r["result"]["decision_trace"]
            self.assertEqual(ca["selected_candidate_ids"], old["chapter_set_selection"]["selected_candidate_ids"])
            self.assertEqual(aa["selected_candidate_ids"], old["aha_set_selection"]["selected_candidate_ids"])
            self.assertEqual(plan["execution_status"], "COMPLETE_RECOMMENDATION_EXECUTED")
            self.assertTrue(all(len(item["source_asset_ids"]) >= 3 for item in c))
            self.assertFalse(ca["automatic_fill_applied"])
            self.assertFalse(aa["motif_overlap_gating_applied"])

    def test_pack2_unrecommended_two_member_alternative_does_not_break_valid_selection(self):
        r = record(2)
        two = next(p for p in r["raw"]["storyline_proposals"] if len(p["beat_map"]) == 2)
        self.assertNotIn(two["key"], r["raw"][editor.OUTPUT_FIELD]["chapter_keys"])
        plan, c, _, _, _, _, _ = select(r)
        self.assertEqual(plan["chapters"]["status"], "MODEL_SELECTION_BOUND")
        self.assertEqual(len(c), 4)

    def test_recommendations_do_not_fill_unrequested_slots(self):
        r = record(3)
        r["raw"][editor.OUTPUT_FIELD]["chapter_keys"] = r["raw"][editor.OUTPUT_FIELD]["chapter_keys"][:1]
        r["raw"][editor.OUTPUT_FIELD]["observation_ids"] = r["raw"][editor.OUTPUT_FIELD]["observation_ids"][:1]
        plan, c, a, _, _, _, _ = select(r)
        self.assertEqual((len(c), len(a)), (1, 1))
        self.assertEqual(plan["execution_status"], "COMPLETE_RECOMMENDATION_EXECUTED")

    def test_no_native_proposals_never_restores_automatic_events(self):
        r = record(3)
        r["raw"]["aha_proposals"] = []
        r["raw"][editor.OUTPUT_FIELD]["observation_ids"] = []
        plan, c, a, _, aa, _, al = select(r)
        self.assertTrue(r["scope"])
        self.assertEqual((len(a), len(al)), (0, 0))
        self.assertEqual(len(c), 4)
        self.assertEqual(aa["search_outcome"], "MODEL_RECOMMENDED_NO_AHA_NOT_PROOF_OF_NO_VALUE")

    def test_single_real_observation_can_be_nominated_without_duration_or_event_gate(self):
        r = record(3)
        obs = r["result"]["observations"][48]
        r["result"]["observations"] = [obs]
        r["raw"]["storyline_proposals"] = []
        r["raw"]["aha_proposals"] = [{"observation_id": obs["id"],
                                      "event_fact_ids": x02._supported_aha_fact_ids(obs),
                                      "narrative_duty": obs["facts"][0]["text"]}]
        r["raw"][editor.OUTPUT_FIELD].update(chapter_keys=[], observation_ids=[obs["id"]])
        r["scope"] = editor.consideration_scope([obs], r["roles"])
        plan, c, a, _, aa, _, _ = select(r)
        self.assertEqual((len(c), len(a)), (0, 1))
        self.assertEqual(a[0]["event_kind"], "NONE")
        self.assertEqual(aa["capacity"], 1)  # inherited cap, not a new sparse-day policy
        self.assertIsNone(plan["recording_input_context"]["wear_duration_minutes"])

    def test_missing_lane_differs_from_explicit_empty_and_preserves_other_lane(self):
        for field, lane in (("chapter_keys", "chapters"), ("observation_ids", "ahas")):
            r = record(3)
            r["raw"][editor.OUTPUT_FIELD].pop(field)
            plan, c, a, _, aa, _, _ = select(r)
            self.assertEqual(plan[lane]["status"], "MISSING_OR_INVALID_SELECTION")
            self.assertEqual(plan["execution_status"], "PARTIAL_OR_MISSING_RECOMMENDATION")
            if lane == "ahas":
                self.assertEqual((len(c), len(a)), (4, 0))
                self.assertEqual(aa["search_outcome"], "AHA_RECOMMENDATION_TECHNICALLY_UNRESOLVED")
            else:
                self.assertEqual((len(c), len(a)), (0, 1))

    def test_local_reference_damage_does_not_trigger_whole_lane_fallback(self):
        for damage in ("unknown", "duplicate", "wrong_type"):
            r = record(3)
            r["raw"][editor.OUTPUT_FIELD]["chapter_keys"].append(
                "unmapped-protocol-reference" if damage == "unknown" else
                r["raw"][editor.OUTPUT_FIELD]["chapter_keys"][0] if damage == "duplicate" else {"invalid": "id"})
            plan, c, a, _, _, _, _ = select(r)
            self.assertEqual((len(c), len(a)), (4, 3))
            self.assertEqual(plan["chapters"]["status"], "PARTIAL_SELECTION_BOUND")
            self.assertEqual(plan["execution_status"], "PARTIAL_OR_MISSING_RECOMMENDATION")

    def test_ambiguous_native_proposal_does_not_guess_an_identity(self):
        r = record(3)
        oid = r["raw"][editor.OUTPUT_FIELD]["observation_ids"][0]
        r["raw"]["aha_proposals"].append(copy.deepcopy(next(a for a in r["raw"]["aha_proposals"] if a["observation_id"] == oid)))
        plan, c, a, _, _, _, _ = select(r)
        self.assertEqual((len(c), len(a)), (4, 2))
        self.assertIn("AMBIGUOUS_PROPOSAL_REFERENCE", [e["code"] for e in plan["ahas"]["diagnostics"]])

    def test_existing_three_member_floor_and_same_story_are_not_relaxed(self):
        r = record(2)
        two = next(p for p in r["raw"]["storyline_proposals"] if len(p["beat_map"]) == 2)
        r["raw"][editor.OUTPUT_FIELD]["chapter_keys"].insert(0, two["key"])
        plan, c, _, ca, _, _, _ = select(r)
        self.assertEqual(len(c), 4)
        self.assertIn("CHAPTER_DISPLAY_NEEDS_THREE_MATERIALS", ca["rejections"].values())
        r = record(1)
        _, _, _, ahas, _, _ = compile_record(r)
        dog = next(a for a in ahas if r["asset_order"][a["source_asset_id"]] == 4)
        r["raw"][editor.OUTPUT_FIELD]["observation_ids"].insert(0, dog["observation_id"])
        plan, _, a, _, aa, _, _ = select(r)
        self.assertNotIn(dog["candidate_id"], {x["candidate_id"] for x in a})
        self.assertEqual(aa["rejections"][dog["candidate_id"]], "SAME_MODEL_ALLOCATED_CHAPTER_STORY")
        self.assertEqual(plan["execution_status"], "PARTIAL_OR_MISSING_RECOMMENDATION")

    def test_missing_context_is_diagnostic_not_a_new_semantic_gate(self):
        r = record(3)
        r["raw"].pop(editor.CONTEXT_FIELD)
        r["raw"][editor.OUTPUT_FIELD].pop("reason")
        plan, c, a, _, _, _, _ = select(r)
        self.assertEqual((len(c), len(a)), (4, 3))
        self.assertEqual(len(plan["diagnostics"]), 3)
        self.assertEqual(plan["execution_status"], "PARTIAL_OR_MISSING_RECOMMENDATION")

    def test_opt_in_schema_short_reference_roundtrip_and_policy_isolation(self):
        r = record(3)
        context = copy.deepcopy(r["request"]["context"])
        context.pop("_x02_policy_version")
        context.pop("codex_editorial_order_policy_version")
        base = wire.response_schema(x02.editorial_allocation.structure_schema(x02.STRUCTURE_SCHEMA))
        before = copy.deepcopy(base)
        schema = editor.response_schema(base)
        self.assertEqual(base, before)
        self.assertNotIn("editorial_order", schema["properties"])
        self.assertNotIn(editor.OUTPUT_FIELD, base["properties"])
        self.assertNotIn(editor.prompt_instruction(), x02._storyline_structure_prompt(context))
        context[editor.POLICY_FIELD] = editor.POLICY_VERSION
        context["recording_input_context"] = editor.input_context()
        context["aha_relation_scope"] = r["scope"]
        prompt = x02._storyline_structure_prompt(context)
        self.assertIn(editor.prompt_instruction(), prompt)
        _, _, mapping = prior.encode_request(prompt, context)
        unknown = []
        short = prior.transform(r["raw"], mapping["forward"], unknown=unknown)
        self.assertEqual(unknown, [])
        self.assertEqual(prior.transform(short, mapping["reverse"]), r["raw"])
        self.assertTrue(all(i.startswith("O") for i in short[editor.OUTPUT_FIELD]["observation_ids"]))
        with self.assertRaises(x02.X02ContractError):
            x02.run_x02_v041(Path("not-read"), research.make_gateway("offline-placeholder", transport=lambda *a: self.fail("No call allowed")),
                              editorial_order_policy=x02.editorial_order.POLICY_VERSION,
                              recording_editor_policy=editor.POLICY_VERSION)

    def test_three_full_function_replays_have_one_s07_no_extra_calls_and_same_cards(self):
        for pack in (1, 2, 3):
            r = record(pack)
            providers = [load(p) for p in sorted((r["directory"] / "codex_stage_calls").glob("*_provider.json"))]
            calls, events = [], []

            def transport(url, headers, body, timeout):
                index = len(calls)
                self.assertLess(index, len(providers), "Unexpected extra call")
                request, provider = r["requests"][index], providers[index]
                payload = copy.deepcopy(provider["payload"])
                sent = json.loads(body)
                calls.append(sent["model"])
                if request["stage"] == prior.S07:
                    text = sent["messages"][0]["content"][0]["text"]
                    self.assertIn(editor.prompt_instruction(), text)
                    self.assertNotIn(x02.editorial_order.prompt_instruction(), text)
                    short_context, _ = json.JSONDecoder().raw_decode(text.rsplit("Input:\n", 1)[1])
                    self.assertEqual(len(short_context["aha_relation_scope"]), len(r["scope"]))
                    self.assertFalse(short_context["recording_input_context"]["capture_time_reliable"])
                    mapping = prior.maps_for(request["context"])
                    payload["choices"][0]["message"]["content"] = json.dumps(prior.transform(r["raw"], mapping["forward"]), ensure_ascii=False)
                elif request["stage"].startswith("S04"):
                    self.assertEqual(hashlib.sha256(body).hexdigest(), provider["request_body_sha256"])
                return 200, {}, canonical_bytes(payload)

            gateway = research.make_gateway("offline-placeholder", transport=transport,
                                            audit_sink=lambda event, row: events.append((event, row)))
            with patch.object(x02, "_select_storyline_set", side_effect=AssertionError("Old selector called")), \
                 patch.object(x02, "_select_aha_set", side_effect=AssertionError("Old selector called")):
                replay = research.run_research(r["directory"] / "codex_manifest.json", gateway)
            self.assertEqual(replay["result"]["chapters"], r["result"]["chapters"])
            self.assertEqual(replay["result"]["ahas"], r["result"]["ahas"])
            self.assertEqual(len(calls), len(providers))
            self.assertEqual(calls.count(prior.PLUS), 1)
            trace = replay["result"]["decision_trace"]
            self.assertNotIn("editorial_order", trace)
            self.assertEqual(trace["recording_editor"]["execution_status"], "COMPLETE_RECOMMENDATION_EXECUTED")
            self.assertEqual(trace["runtime_policies"]["recording_editor"], editor.POLICY_VERSION)
            finished_s07 = next(row for event, row in events if event == "FINISHED" and row["stage"] == prior.S07)
            self.assertEqual(finished_s07["unknown_short_references"], [])


if __name__ == "__main__":
    unittest.main()
