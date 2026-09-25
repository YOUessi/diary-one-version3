"""Offline preparation only for a separately authorized V1.55 comparison.

No network, credentials, runtime edits, synthetic semantics or model answers.
Reuses the pinned V1.53 inputs/control prompt, replacing only its editorial paragraph.
"""
import hashlib
import json
from pathlib import Path

from diary_one_ci import x02
from diary_one_ci.core import canonical_bytes
from codex_run_writer_core_focus_v1_53 import (
    MODEL, ENDPOINT, OLD_FOCUS, NEW_FOCUS, prepare as prepare_v153,
)
from codex_run_writer_model_only_v1_51 import digest, expected_body

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "docs/codex_V1_54_WRITER_MODIFIER_SELECTION.md"
PRIOR = ROOT / "var/codex_writer_checks/codex_v1_53_core_focus/report.json"
PRIOR_SHA = "e153671ee56103c9a65b16192b4749204ee8eaa1dbad1b1a5ee58ca4076d3a72"
ORDER_NOTE = "素材/封面排序不等于文字重点排序。"


def prepare():
    assert digest(PRIOR) == PRIOR_SHA
    # Read the approved discussion draft; never copy its per-scene examples.
    paragraphs = [line[2:] for line in DRAFT.read_text().splitlines() if line.startswith("> ")]
    assert len(paragraphs) == 1
    guidance = paragraphs[0]
    prior = json.loads(PRIOR.read_text())
    prior_controls = {c["sample"]: c for c in prior["cells"] if c["variant"] == "control"}
    plans = []
    for control in prepare_v153():
        if control["variant"] != "control":
            continue
        archived = prior_controls[control["sample"]]
        assert control["context"] == archived["context"]
        assert control["request_sha256"] == archived["request_sha256"]
        instructions, input_json = control["prompt"].rsplit("Input:\n", 1)
        assert instructions.count(OLD_FOCUS) == 1
        assert NEW_FOCUS not in instructions
        modified = instructions.replace(OLD_FOCUS, guidance + ORDER_NOTE)
        assert modified.replace(guidance + ORDER_NOTE, OLD_FOCUS) == instructions
        for variant, prefix in (("control", instructions), ("candidate", modified)):
            prompt = prefix + "Input:\n" + input_json
            body = expected_body(prompt, x02.WRITER_SCHEMA, MODEL)
            assert all(p["type"] == "text" for m in body["messages"] for p in m["content"])
            plans.append({"cell": control["sample"] + "_" + variant,
                          "sample": control["sample"], "variant": variant,
                          "context": control["context"], "prompt": prompt, "body": body,
                          "input_sha256": hashlib.sha256(input_json.encode()).hexdigest(),
                          "request_sha256": hashlib.sha256(canonical_bytes(body)).hexdigest()})
    assert len(plans) == 4
    for left, right in zip(plans[::2], plans[1::2]):
        assert left["input_sha256"] == right["input_sha256"]
        assert left["context"] == right["context"]
        assert {k: v for k, v in left["body"].items() if k != "messages"} == {
            k: v for k, v in right["body"].items() if k != "messages"}
    return plans


if __name__ == "__main__":
    plans = prepare()
    print(json.dumps({
        "status": "OFFLINE_PREPARED_AWAITING_NEW_TRANSMISSION_APPROVAL",
        "actual_model_calls": 0, "planned_maximum_calls": 4,
        "planned_endpoint": ENDPOINT, "model": MODEL,
        "scope": "S11_TWO_SOURCE_PACKS_SEPARATE_CONTEXTS_NO_MERGING_OR_REGROUPING",
        "same_facts_schema_model_and_soft_length_within_pairs": True,
        "control_exact_match_to_v153_request": True,
        "candidate_only_replaces_editorial_paragraph_with_v154_draft": True,
        "source_report_sha256": PRIOR_SHA,
        "editorial_draft_sha256": digest(DRAFT),
        "items": [{k: p[k] for k in ("cell", "input_sha256", "request_sha256")}
                  for p in plans],
    }, ensure_ascii=False, indent=2))
