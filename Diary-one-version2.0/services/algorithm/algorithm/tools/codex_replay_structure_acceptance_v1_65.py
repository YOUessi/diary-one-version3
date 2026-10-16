"""Read-only replay of recorded structure responses; no gateway or network call.

Prints a derived audit to stdout. Does not mutate source runs or persist output.
The historical implementation must run in its own process to isolate imports.
"""

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / "var/codex_v1_64_repeat_review"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation", choices=("current", "v1_63"), required=True)
    parser.add_argument("--full-ledger", action="store_true", help="Include full existing candidate metadata")
    args = parser.parse_args()
    source = ROOT / "src" if args.implementation == "current" else AREA / "codex_runtime/src"
    sys.path.insert(0, str(source))
    from diary_one_ci import x02
    assert Path(x02.__file__).resolve() == (source / "diary_one_ci/x02.py").resolve()
    records = []
    for pack in range(1, 4):
        for round_number in range(1, 4):
            directory = AREA / ("pack_%d" % pack) / ("round_%d" % round_number)
            run_path = directory / "codex_full_run.json"
            run = json.loads(run_path.read_text())
            record = {"pack": pack, "round": round_number, "original_run_status": run["status"]}
            records.append(record)
            result = run.get("result")
            if not result:
                record["replay_status"] = "NO_RESULT_NOT_REPLAYED_NOT_ZERO_CONTENT"
                continue
            response_paths = []
            for path in sorted((directory / "codex_stage_calls").glob("*_response.json")):
                response = json.loads(path.read_text())
                if response.get("stage") == "S05_S07_STRUCTURE_PROPOSAL" and "output" in response:
                    response_paths.append((path, response))
            assert len(response_paths) == 1
            response_path, response = response_paths[0]
            manifest_path = directory / "codex_manifest.json"
            manifest = json.loads(manifest_path.read_text())
            arguments = (
                uuid.UUID(result["session_id"]), result["observations"],
                result["decision_trace"]["observation_roles"], result["moments"],
                response["output"],
                {asset["asset_id"]: index for index, asset in enumerate(manifest["assets"])},
            )
            chapters, chapter_ledger = x02._build_storyline_candidates(*arguments)
            ahas, aha_ledger = x02._build_aha_candidates(*arguments, value_first=True)
            record.update({
                "replay_status": "RECORDED_INPUT_FIELD_ACCEPTANCE_ONLY",
                "coverage_status": result["coverage_status"],
                "original_delivery_state": result["delivery_state"],
                "sources": {str(p.relative_to(ROOT)): sha(p) for p in (run_path, response_path, manifest_path)},
                "accepted_chapter_candidates": len(chapters),
                "accepted_aha_candidates": len(ahas),
                "chapter_ledger": chapter_ledger,
                "aha_ledger": aha_ledger,
            })
            if args.implementation == "v1_63":
                for actual, key in ((chapter_ledger, "chapter_candidates"), (aha_ledger, "aha_candidates")):
                    saved = result["decision_trace"][key]
                    def identity(entry):
                        return (entry["proposal_source"], entry["candidate_key"], entry["validation_status"], entry["reason_codes"][0])
                    assert [identity(e) for e in actual] == [identity(e) for e in saved]
                record["baseline_first_rejections_reproduced"] = True
            if not args.full_ledger:
                fields = (
                    "proposal_source", "candidate_key", "validation_status", "reason_codes",
                    "candidate_id", "observation_id", "observation_ids", "alias_of_candidate_id",
                    "fact_summary_audit",
                )
                for key in ("chapter_ledger", "aha_ledger"):
                    record[key] = [{k: entry[k] for k in fields if k in entry} for entry in record[key]]
    print(json.dumps({
        "scope": "OFFLINE_RECORDED_STRUCTURE_ACCEPTANCE_NOT_FRESH_PIPELINE_OR_QUALITY_EVALUATION",
        "implementation": args.implementation,
        "implementation_sha256": sha(Path(x02.__file__)),
        "model_calls": 0,
        "records": records,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
