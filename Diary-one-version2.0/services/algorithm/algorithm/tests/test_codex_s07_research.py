"""Offline integration using archived real replies, never semantic gold labels.

Private research archives are not bundled for publication. Full replay requires
the existing local evidence files; no network or substitute scenes are created.
"""
import copy
import hashlib
import json
import unittest
import uuid
from pathlib import Path

from diary_one_ci import codex_editorial_allocation as allocation
from diary_one_ci import codex_s07_research as research
from diary_one_ci import codex_structure_wire as wire
from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes

ROOT = Path(__file__).resolve().parents[1]
B2 = ROOT / "var/codex_structure_model_comparison_20260907"
B3 = ROOT / "var/codex_structure_short_refs_20260907"
OLD = ROOT / "var/codex_v1_68_2_experience_first_chapter_execution"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def original_request(pack):
    return load(B2 / ("pack_%d_request.json" % pack))


def downstream(pack, decoded):
    directory = OLD / ("pack_%d/round_1" % pack)
    old = load(directory / "codex_full_run.json")["result"]
    manifest = load(directory / "codex_manifest.json")
    order = {a["asset_id"]: a["sequence_index"] for a in manifest["assets"]}
    normalized, _ = wire.normalize_output(decoded)
    args = (uuid.UUID(old["session_id"]), old["observations"],
            old["decision_trace"]["observation_roles"], old["moments"], normalized, order)
    chapters, ledger = x02._build_storyline_candidates(*args)
    ahas, _ = x02._build_aha_candidates(*args, value_first=True)
    plan = allocation.compile_relations(normalized, chapters, ledger, ahas)
    selected, _ = x02._select_storyline_set(chapters, ledger, old["observations"], order)
    return old, chapters, ledger, ahas, plan, selected


@unittest.skipUnless((B3 / "codex_preparation.json").exists(), "Private real replay archives unavailable")
class S07ResearchTests(unittest.TestCase):
    def test_two_requests_match_actual_b3_http_body_and_restore_all_information(self):
        for pack in (1, 2):
            request = original_request(pack)
            before = copy.deepcopy(request)
            prompt, context, mapping = research.encode_request(request["prompt"], request["context"])
            archived = load(B3 / ("pack_%d_request.json" % pack))
            self.assertEqual(prompt, archived["prompt"])
            self.assertEqual(context, archived["context"])
            self.assertEqual(mapping, load(B3 / ("pack_%d_reference_map.json" % pack)))
            self.assertEqual(research.transform(context, mapping["reverse"]), request["context"])
            self.assertEqual(request, before)
            self.assertEqual(context["sequence_basis"], "IMPORT_SEQUENCE_ONLY")
            self.assertEqual([f["text"] for o in context["observations"] for f in o["facts"]],
                             [f["text"] for o in request["context"]["observations"] for f in o["facts"]])

    def test_four_real_plus_replies_decode_exactly_with_no_added_calls(self):
        for slot in load(B3 / "codex_execution_summary.json")["results"]:
            with self.subTest(slot=slot["slot"]):
                directory = B3 / ("slot_%02d" % slot["slot"])
                provider = load(directory / "codex_provider.json")["payload"]
                request = original_request(slot["pack"])
                sent = []

                def transport(url, headers, body, timeout):
                    sent.append(json.loads(body))
                    self.assertEqual(sent[-1], load(B3 / ("pack_%d_SHORT_body.json" % slot["pack"])))
                    return 200, {}, canonical_bytes(provider)

                gateway = research.make_gateway("offline-placeholder", transport=transport)
                result = gateway.call(request["stage"], request["prompt"], request["schema"], context=request["context"])
                self.assertEqual(len(sent), 1)
                self.assertEqual(result.output, load(directory / "codex_result.json")["output"])
                self.assertEqual(gateway.calls[0]["raw_short_output"], load(directory / "codex_raw_output.json"))
                self.assertEqual(gateway.calls[0]["unknown_short_references"], [])
                self.assertEqual(result.model, research.PLUS)
                self.assertAlmostEqual(result.estimated_cost_native,
                                       slot["usage"]["list_price_estimated_cny"])

    def test_eight_old_outputs_roundtrip_without_fixing_real_invalid_ids(self):
        unknown_count = 0
        for slot in load(B2 / "codex_execution_summary.json")["results"]:
            raw = load(B2 / ("slot_%02d/codex_result.json" % slot["slot"]))["output"]
            before = copy.deepcopy(raw)
            mapping = research.maps_for(original_request(slot["pack"])["context"])
            unknown = []
            short = research.transform(raw, mapping["forward"], unknown=unknown)
            self.assertEqual(research.transform(short, mapping["reverse"]), raw)
            self.assertEqual(raw, before)
            unknown_count += len(unknown)
        self.assertGreater(unknown_count, 0)  # Archived errors, not invented negatives.

    def test_real_b3_downstream_references_three_floor_and_ambiguous_keys(self):
        counts, two_member_count, ambiguous_count = [], 0, 0
        for slot in load(B3 / "codex_execution_summary.json")["results"]:
            decoded = load(B3 / ("slot_%02d/codex_result.json" % slot["slot"]))["output"]
            old, chapters, ledger, ahas, plan, selected = downstream(slot["pack"], decoded)
            counts.append(len(chapters))
            self.assertTrue(all(entry["validation_status"] == "PASSED" for entry in ledger))
            self.assertEqual(len({c["candidate_id"] for c in chapters}), len(chapters))
            self.assertEqual({c["candidate_id"] for c in chapters},
                             {r["chapter_candidate_id"] for r in plan["relations"]})
            for entry in ledger:
                if len(entry["source_asset_ids"]) == 2:
                    two_member_count += 1
                    self.assertEqual(entry["selection_status"], "NOT_SELECTED")
                    self.assertIn("CHAPTER_DISPLAY_NEEDS_THREE_MATERIALS", entry["reason_codes"])
            self.assertTrue(all(len(c["source_asset_ids"]) >= 3 for c in selected))
            if slot["pack"] == 2:
                request = original_request(2)
                night_ids = {o["observation_id"] for o in request["context"]["observations"][17:20]}
                selected_night = [c for c in selected if set(c["observation_ids"]) == night_ids]
                self.assertEqual(len(selected_night), 1)
                members = [o for o in old["observations"] if o["id"] in night_ids]
                display = x02.chapter_display.choose_display(members)
                self.assertEqual(set(display["selected_observation_ids"]), night_ids)
                self.assertEqual(display["selection_source"], "THREE_MEMBER_FLOOR_NO_COMPARISON_NEEDED")
            ambiguities = [r for r in plan["diagnostics"] if r["code"] == "AMBIGUOUS_CHAPTER_KEY"]
            ambiguous_count += len(ambiguities)
            for row in ambiguities:
                candidates = {e["candidate_id"] for e in ledger if e["candidate_key"] == row["chapter_key"]}
                self.assertEqual(len(candidates), 2)
                self.assertTrue(all(r["relation"] == "UNRESOLVED" for r in plan["relations"]
                                    if r["chapter_candidate_id"] in candidates))
        self.assertEqual(counts, [3, 5, 3, 5])
        self.assertEqual(two_member_count, 2)
        self.assertEqual(ambiguous_count, 1)

    def test_two_full_archived_chains_preserve_cards_and_route_only_s07(self):
        # This replays OLD content through the NEW entry, not new Plus quality.
        # Only transport envelope/model identity and S07 reference encoding change.
        for pack in (1, 2):
            with self.subTest(pack=pack):
                directory = OLD / ("pack_%d/round_1" % pack)
                requests = [load(p) for p in sorted((directory / "codex_stage_calls").glob("*_request.json"))]
                providers = [load(p) for p in sorted((directory / "codex_stage_calls").glob("*_provider.json"))]
                calls = []

                def transport(url, headers, body, timeout):
                    index = len(calls)
                    self.assertLess(index, len(requests), "Unexpected extra model call")
                    request, record = requests[index], providers[index]
                    payload = copy.deepcopy(record["payload"])
                    sent = json.loads(body)
                    calls.append(sent["model"])
                    if request["stage"] == research.S07:
                        mapping = research.maps_for(request["context"])
                        expected_prompt, _, _ = research.encode_request(request["prompt"], request["context"])
                        full_prompt = expected_prompt + "\nReturn exactly one valid JSON object. Do not include markdown. "
                        full_prompt += "The object must conform to this schema:\n" + json.dumps(request["schema"], ensure_ascii=False)
                        self.assertEqual(sent["messages"], [{"role": "user", "content": [{"type": "text", "text": full_prompt}]}])
                        self.assertEqual(sent["model"], research.PLUS)
                        message = payload["choices"][0]["message"]
                        message["content"] = json.dumps(research.transform(json.loads(message["content"]), mapping["forward"]), ensure_ascii=False)
                        payload["model"] = research.PLUS
                    else:
                        self.assertEqual(sent["model"], research.FLASH)
                        self.assertEqual(hashlib.sha256(body).hexdigest(), record["request_body_sha256"])
                    return 200, {}, canonical_bytes(payload)

                gateway = research.make_gateway("offline-placeholder", transport=transport)
                replay = research.run_research(directory / "codex_manifest.json", gateway)
                old = load(directory / "codex_full_run.json")["result"]
                self.assertEqual(replay["result"]["chapters"], old["chapters"])
                self.assertEqual(replay["result"]["ahas"], old["ahas"])
                self.assertEqual(len(calls), len(requests))
                self.assertEqual(calls.count(research.PLUS), 1)
                self.assertEqual(replay["result"]["decision_trace"]["runtime_policies"],
                                 old["decision_trace"]["runtime_policies"])
                self.assertEqual(replay["research_profile"], research.profile())
                for call in replay["gateway_audit"]:
                    self.assertEqual(call["short_references"], call["stage"] == research.S07)
                    self.assertEqual(call["status"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
