"""Real-record plumbing regression, not fresh model quality or semantic gold.

Priority permutations and malformed IDs below test only the new transport
contract. They do not invent picture facts or define scene-specific rules.
"""

import copy
import hashlib
import json
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from diary_one_ci import codex_d1_research as research
from diary_one_ci import codex_editorial_order as order
from diary_one_ci import codex_s07_research as prior
from diary_one_ci import codex_structure_wire as wire
from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes


ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "var/codex_v1_69_full_chain_execution"


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
    normalized, _ = wire.normalize_output(raw)
    args = (uuid.UUID(result["session_id"]), result["observations"],
            result["decision_trace"]["observation_roles"], result["moments"], normalized, asset_order)
    chapters, chapter_ledger = x02._build_storyline_candidates(*args)
    ahas, aha_ledger = x02._build_aha_candidates(*args, value_first=True)
    allocation = x02.editorial_allocation.compile_relations(normalized, chapters, chapter_ledger, ahas)
    # Reproduce the archived priority ONLY to verify unchanged downstream bodies.
    # This is not a new model preference, human label or quality acceptance.
    chosen = result["decision_trace"]["chapter_set_selection"]["selected_candidate_ids"]
    key_by_id = {e["candidate_id"]: e["candidate_key"] for e in chapter_ledger
                 if e["validation_status"] == "PASSED"}
    keys = [key_by_id[cid] for cid in chosen]
    keys += [p["key"] for p in raw["storyline_proposals"] if p["key"] not in keys]
    aha_by_id = {a["candidate_id"]: a["observation_id"] for a in ahas}
    raw[order.OUTPUT_FIELD] = {
        "chapter_keys": keys,
        "observation_ids": [aha_by_id[cid] for cid in result["decision_trace"]["aha_set_selection"]["ranked_candidate_ids"]],
        "reason": "OFFLINE_ARCHIVED_ORDER_REPLAY_NOT_MODEL_JUDGMENT",
    }
    return {"directory": directory, "result": result, "requests": requests, "request": request,
            "raw": raw, "chapters": chapters, "chapter_ledger": chapter_ledger,
            "ahas": ahas, "aha_ledger": aha_ledger, "allocation": allocation, "asset_order": asset_order}


def plan(r):
    return order.compile_order(r["raw"], r["chapter_ledger"], r["ahas"],
                               r["request"]["context"]["aha_relation_scope"])


def select(r, priority):
    chapters, ca = x02._select_storyline_set(r["chapters"], r["chapter_ledger"],
                                            r["result"]["observations"], r["asset_order"],
                                            editorial_priority=priority["chapters"] if priority else None)
    ahas, aa = x02._select_aha_set(r["ahas"], r["aha_ledger"], chapters,
                                  r["result"]["observations"], r["asset_order"], value_first=True,
                                  allocation_plan=r["allocation"],
                                  editorial_priority=priority["ahas"] if priority else None)
    return chapters, ahas, ca, aa


@unittest.skipUnless((AREA / "pack_3/round_1/codex_full_run.json").exists(), "Private three-pack records unavailable")
class EditorialOrderTests(unittest.TestCase):
    def test_three_pack_scope_binds_every_candidate_and_preserves_real_fields(self):
        for pack in (1, 2, 3):
            r = record(pack)
            before = copy.deepcopy(r)
            p = plan(r)
            self.assertEqual(r, before)
            self.assertTrue(order.applied(p["chapters"]))
            self.assertTrue(order.applied(p["ahas"]))
            self.assertEqual(set(p["ahas"]["ranked_candidate_ids"]), {a["candidate_id"] for a in r["ahas"]})
            self.assertEqual(len(p["ahas"]["ranked_candidate_ids"]), len(r["ahas"]))
            self.assertEqual(p["additional_model_calls"], 0)

    def test_priority_consumed_without_calling_either_legacy_score(self):
        for pack in (1, 2, 3):
            r = record(pack)
            for field in ("chapter_keys", "observation_ids"):
                r["raw"][order.OUTPUT_FIELD][field].reverse()
            p = plan(r)
            with patch.object(x02, "_storyline_selection_value", side_effect=AssertionError("Legacy Chapter score used")), \
                 patch.object(x02, "_aha_rank_inputs", side_effect=AssertionError("Legacy Aha score used")):
                chapters, ahas, ca, aa = select(r, p)
            feasible = [cid for cid in p["chapters"]["ranked_candidate_ids"]
                        if len(next(c for c in r["chapters"] if c["candidate_id"] == cid)["source_asset_ids"]) >= 3]
            self.assertEqual(ca["selected_candidate_ids"][0], feasible[0])
            self.assertEqual(aa["ranked_candidate_ids"], p["ahas"]["ranked_candidate_ids"])
            self.assertTrue(all(len(c["source_asset_ids"]) >= 3 for c in chapters))
            self.assertFalse(ca["proxy_value_thresholds_applied"])
            self.assertEqual(aa["rank_fields"], ["editorial_priority"])
            self.assertTrue(set(aa["selected_candidate_ids"]) <= set(aa["ranked_candidate_ids"]))
            if pack == 3:
                old = r["result"]["decision_trace"]
                self.assertNotEqual(set(ca["selected_candidate_ids"]), set(old["chapter_set_selection"]["selected_candidate_ids"]))
                self.assertNotEqual(set(aa["selected_candidate_ids"]), set(old["aha_set_selection"]["selected_candidate_ids"]))

    def test_real_floor_relations_and_archived_selection_are_preserved(self):
        for pack in (1, 2, 3):
            r = record(pack)
            chapters, ahas, ca, aa = select(r, plan(r))
            old = r["result"]["decision_trace"]
            self.assertEqual([c["candidate_id"] for c in chapters], old["chapter_set_selection"]["selected_candidate_ids"])
            self.assertEqual(aa["selected_candidate_ids"], old["aha_set_selection"]["selected_candidate_ids"])
            self.assertEqual(aa["chapter_relations"], old["aha_set_selection"]["chapter_relations"])
            self.assertEqual(aa["chapter_conflicts"], old["aha_set_selection"]["chapter_conflicts"])
            if pack == 2:
                night = [c for c in chapters if {r["asset_order"][a] for a in c["source_asset_ids"]} == {17, 18, 19}]
                self.assertEqual(len(night), 1)
                self.assertIn(15, [r["asset_order"][a["source_asset_id"]] for a in ahas])
                self.assertEqual(len(aa["chapter_conflicts"]), 3)

    def test_missing_order_uses_identical_legacy_membership_not_empty_output(self):
        for pack in (1, 2, 3):
            r = record(pack)
            r["raw"].pop(order.OUTPUT_FIELD)
            p = plan(r)
            self.assertFalse(order.applied(p["chapters"]))
            self.assertFalse(order.applied(p["ahas"]))
            current = select(r, p)
            legacy = select(record(pack), None)
            self.assertEqual(current[:2], legacy[:2])
            self.assertEqual(current[2]["editorial_order"]["status"], "FALLBACK_LEGACY_ORDER")

    def test_transport_damage_falls_back_only_affected_lane_no_semantic_rules(self):
        # Protocol mutations of real IDs only, not imagined animal/scene failures.
        for damage in ("missing", "duplicate", "unknown", "wrong_type"):
            r = record(3)
            ids = r["raw"][order.OUTPUT_FIELD]["observation_ids"]
            if damage == "missing":
                ids.pop()
            elif damage == "duplicate":
                ids.append(ids[0])
            elif damage == "unknown":
                ids[0] = "unmapped-test-reference"
            else:
                ids[0] = {"invalid": "not-an-id"}
            p = plan(r)
            self.assertTrue(order.applied(p["chapters"]))
            self.assertFalse(order.applied(p["ahas"]))
            self.assertTrue(p["ahas"]["diagnostics"])
            select(r, p)  # valid candidates continue through old Aha selection

    def test_request_schema_and_new_short_ids_are_opt_in_and_reversible(self):
        r = record(3)
        base = r["request"]["schema"]
        before = copy.deepcopy(base)
        new = order.response_schema(base)
        self.assertEqual(base, before)
        self.assertNotIn(order.OUTPUT_FIELD, base["properties"])
        self.assertIn(order.OUTPUT_FIELD, new["required"])
        mapping = prior.maps_for(r["request"]["context"])
        short = prior.transform(r["raw"], mapping["forward"])
        self.assertEqual(prior.transform(short, mapping["reverse"]), r["raw"])
        self.assertTrue(all(v.startswith("O") for v in short[order.OUTPUT_FIELD]["observation_ids"]))
        context = copy.deepcopy(r["request"]["context"])
        context.pop("_x02_policy_version", None)
        self.assertNotIn(order.prompt_instruction(), x02._storyline_structure_prompt(context))
        context[order.POLICY_FIELD] = order.POLICY_VERSION
        self.assertIn(order.prompt_instruction(), x02._storyline_structure_prompt(context))

    def test_three_full_chain_replays_keep_other_request_bodies_and_cards_unchanged(self):
        for pack in (1, 2, 3):
            r = record(pack)
            providers = [load(p) for p in sorted((r["directory"] / "codex_stage_calls").glob("*_provider.json"))]
            calls = []

            def transport(url, headers, body, timeout):
                index = len(calls)
                self.assertLess(index, len(providers), "Unexpected extra call")
                request, provider = r["requests"][index], providers[index]
                payload = copy.deepcopy(provider["payload"])
                sent = json.loads(body)
                calls.append(sent["model"])
                if request["stage"] == prior.S07:
                    self.assertIn(order.prompt_instruction(), sent["messages"][0]["content"][0]["text"])
                    mapping = prior.maps_for(request["context"])
                    payload["choices"][0]["message"]["content"] = json.dumps(
                        prior.transform(r["raw"], mapping["forward"]), ensure_ascii=False)
                else:
                    self.assertEqual(hashlib.sha256(body).hexdigest(), provider["request_body_sha256"], request["stage"])
                return 200, {}, canonical_bytes(payload)

            gateway = research.make_gateway("offline-placeholder", transport=transport)
            replay = research.run_research(r["directory"] / "codex_manifest.json", gateway)
            self.assertEqual(replay["result"]["chapters"], r["result"]["chapters"])
            self.assertEqual(replay["result"]["ahas"], r["result"]["ahas"])
            self.assertEqual(len(calls), len(providers))
            self.assertEqual(calls.count(prior.PLUS), 1)
            self.assertTrue(order.applied(replay["result"]["decision_trace"]["editorial_order"]["ahas"]))


if __name__ == "__main__":
    unittest.main()
