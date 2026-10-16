"""Bounded S11-only check of recorded failures, never an end-to-end run.

No network without --live. Saves request bodies without headers/credentials.
The input contains only already-authorized, previously processed real records.
"""

import argparse
import hashlib
import importlib.util
import json
import uuid
from pathlib import Path

from diary_one_ci import x02
from diary_one_ci.x01 import QwenChatCompletionsAdapter
from diary_one_ci.x01_server import _resolve_qwen_api_key


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/codex_aha_writer_real_failures.json"
EXPERIMENT = ROOT / "tools/codex_aha_writer_prompt_experiment.py"
_spec = importlib.util.spec_from_file_location("codex_archived_writer_experiment", EXPERIMENT)
repair = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(repair)


def recorded_context():
    recorded = json.loads(FIXTURE.read_text(encoding="utf-8"))
    observations = {item["id"]: item for item in recorded["observations"]}
    candidates = []
    for selected in recorded["selected_ahas"]:
        assert selected["proposal_source"] == "DETERMINISTIC_EVENT_PEAK"
        observation = observations[selected["observation_id"]]
        facts = x02._supported_aha_fact_ids(observation)
        candidates.append({
            **selected,
            "fact_ids": facts,
            "event_fact_ids": facts,
            "episode_code": observation["episode_code"],
            "narrative_duty": observation["event_kind"],
        })
    context = x02._writer_context(
        [], candidates, {}, {item["candidate_id"]: item for item in recorded["media"]},
        recorded["observations"], storyline_v04=True,
    )
    failures = [item for item in recorded["writer_audit"] if item["attempt"] == 1]
    retry = repair._writer_retry_context(
        context, [item["candidate_id"] for item in candidates], failures,
    )
    return recorded, retry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--label", required=True)
    parser.add_argument("--request-file", type=Path,
                        help="Replay an exact saved, credential-free request body")
    parser.add_argument("--baseline-report", type=Path,
                        help="Use the prompt/schema/context from a saved pre-edit dry check")
    args = parser.parse_args()
    recorded, context = recorded_context()
    prompt = repair._writer_prompt(context, retry=True)
    schema = repair._writer_request_schema(context, retry=True)
    policy = repair.X02_WRITER_REQUEST_POLICY_VERSION
    if args.baseline_report:
        baseline = json.loads(args.baseline_report.read_text(encoding="utf-8"))
        assert baseline["source"]["run_id"] == recorded["provenance"]["run_id"]
        prompt, schema, context = baseline["prompt"], baseline["schema"], baseline["context"]
        policy = baseline["request_policy_version"]
    context["_x02_policy_version"] = "V04_1"
    report_id = str(uuid.uuid4())
    directory = ROOT / "var/codex_writer_checks" / report_id
    directory.mkdir(parents=True, exist_ok=False)
    report = {
        "check_id": report_id, "label": args.label,
        "scope": "S11_ONLY_RECORDED_FAILURE_REPLAY_NOT_FULL_PIPELINE",
        "source": recorded["provenance"], "source_fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        "implementation_sha256": hashlib.sha256(Path(x02.__file__).read_bytes()).hexdigest(),
        "experiment_sha256": hashlib.sha256(EXPERIMENT.read_bytes()).hexdigest(),
        "request_policy_version": policy,
        "context": context, "live": args.live,
    }
    if not args.live:
        report.update(prompt=prompt, schema=schema)
    else:
        key, _ = _resolve_qwen_api_key()
        if not key:
            raise SystemExit("Existing Qwen credential unavailable; no model call made")
        adapter = QwenChatCompletionsAdapter(
            api_key=key, model=recorded["model"], timeout_seconds=60,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        transport = adapter.transport

        def capture_transport(url, headers, body, timeout):
            if args.request_file:
                body = args.request_file.read_bytes()
                assert json.loads(body)["model"] == adapter.model
            (directory / "request.json").write_bytes(body)
            report["request_sha256"] = hashlib.sha256(body).hexdigest()
            return transport(url, headers, body, timeout)

        adapter.transport = capture_transport
        try:
            run = x02.QwenStageGateway(adapter).call(
                "S11_WRITER_ATTEMPT_2", prompt, schema, context=context,
            )
            narratives, audit, invalid = x02._validate_writer_output(run.output, context, attempt=2)
            report.update(output=run.output, audit=audit, invalid_ids=invalid,
                          accepted_count=len(narratives), metric=x02._metric_from_run(run))
        except x02.X02StageCallError as exc:
            report.update(error=exc.code, metric=x02._metric_from_run(exc.stage_run))
    path = directory / "report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report_path": str(path), "accepted_count": report.get("accepted_count"),
                      "error": report.get("error"), "metric": report.get("metric"),
                      "drafts": [{"text": a.get("draft_text"), "count": a.get("text_visible_characters"),
                                  "status": a["validation_status"]} for a in report.get("audit", [])]},
                     ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
