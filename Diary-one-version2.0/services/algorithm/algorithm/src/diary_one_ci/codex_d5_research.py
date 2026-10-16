"""V1.75 opt-in research entry for Chapter-coverage-audited Aha editing."""

import copy

from . import codex_d4_research as prior
from . import codex_experience_editor as editor
from . import codex_s07_research as routing
from . import codex_v174_writer as writer
from . import x02


def profile():
    result = prior.profile()
    result.pop("writer_policy_unchanged", None)
    result["stage_models"] = {
        **{
            stage: model for stage, model in result["stage_models"].items()
            if stage != prior.editor.EDITOR_STAGE
        },
        editor.EDITOR_STAGE: routing.PLUS,
    }
    result["short_reference_stages"] = [
        routing.S07, editor.EDITOR_STAGE, "S11_WRITER_*",
    ]
    result.update(
        version="CODEX_V1_75_UNCOVERED_FACT_AUDIT",
        recording_editor_policy_version=editor.POLICY_VERSION,
        supersedes_research_profile="CODEX_V1_74_1_EXPERIENCE_EDITOR_SAFE_EXIT",
        s07_responsibility="CHAPTER_ONLY",
        aha_discovery="S09_FULL_USABLE_SUPPORTED_FACT_PALETTE",
        aha_chapter_coverage="EXPLICIT_MEMBERSHIP_AND_EXACT_UNCOVERED_FACT_REVIEW",
        aha_uncovered_fact_selection="REVIEW_REQUIRED_SELECTION_NOT_REQUIRED",
        aha_set_editor="S09_ONE_TEXT_ONLY_PLUS_CALL_FINAL_COEXISTABLE_SET",
        aha_relation_contract="EXACT_COMPLETE_SELECTED_PAIR_MATRIX_FAIL_CLOSED",
        aha_quantity_contract="ZERO_TO_THREE_ACTIVE_TARGET_TWO_TO_THREE_WHEN_SUPPORTED",
        aha_media="S04_FACT_REPRESENTATIVE_FRAME",
        aha_moment_scope="ONE_FACT_ONE_S04_REPRESENTATIVE_FRAME",
        writer_reference_contract="REQUEST_LOCAL_SHORT_IDS",
        writer_exit_policy_version=writer.POLICY_VERSION,
        writer_model_calls=1,
        chapter_writer_failure="INTERNAL_MEDIA_LEDGER_NO_PUBLIC_BAD_COPY",
        deterministic_copy_fallback="FORBIDDEN",
        additional_model_calls=1,
        editor_retry_or_automatic_fill="FORBIDDEN",
        deployment="RESEARCH_OPT_IN_ONLY",
    )
    return result


class ResearchGateway(prior.ResearchGateway):
    """Route the V1.75 S09 call to Plus without changing existing routes."""

    def call(self, stage, prompt, schema, evidence=(), context=None):
        if stage != editor.EDITOR_STAGE:
            return super().call(stage, prompt, schema, evidence=evidence, context=context)
        if evidence:
            raise x02.X02ContractError("V1.75 S09 Aha experience editor is text-only")
        gateway = self.structure_gateway
        record = {
            "index": len(self.calls) + 1,
            "stage": stage,
            "model": gateway.model,
            "status": "PREPARED",
            "short_references": True,
            "full_supported_fact_palette": True,
        }
        self.calls.append(record)
        self._emit("PREPARED", record)
        try:
            run = routing._priced(gateway.call(
                stage, prompt, schema, evidence=evidence, context=context,
            ))
            if run.model != gateway.model:
                raise x02.X02ContractError(
                    "Research Aha experience editor returned an unexpected model identity"
                )
            record.update(status=run.call_status, metric=x02._metric_from_run(run))
            return run
        except Exception as exc:
            record.update(
                status="FAILED", error_type=type(exc).__name__,
                code=getattr(exc, "code", None),
            )
            if isinstance(exc, x02.X02StageCallError):
                exc.stage_run = routing._priced(exc.stage_run)
                record["metric"] = x02._metric_from_run(exc.stage_run)
            raise
        finally:
            self._emit("FINISHED", record)


def make_gateway(api_key, *, transport=None, audit_sink=None):
    base = routing.make_gateway(api_key, transport=transport, audit_sink=audit_sink)
    return ResearchGateway(
        base.default_gateway, base.structure_gateway, audit_sink=audit_sink,
    )


def run_research(manifest_path, gateway):
    if not isinstance(gateway, ResearchGateway) or gateway.calls:
        raise ValueError("Use a fresh V1.75 research gateway for each run")
    result = x02.run_x02_v041(
        manifest_path, gateway, recording_editor_policy=editor.POLICY_VERSION,
    )
    return {
        "research_profile": profile(),
        "result": result,
        "gateway_audit": copy.deepcopy(gateway.calls),
    }
