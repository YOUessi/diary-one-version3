"""V1.73 opt-in research entry for the one-pass Aha set editor."""

import copy

from . import codex_aha_set_editor as editor
from . import codex_d3_research as prior
from . import codex_s07_research as routing
from . import x02


def profile():
    result = prior.profile()
    result["stage_models"] = {
        **result["stage_models"],
        editor.EDITOR_STAGE: routing.PLUS,
    }
    result.update(
        version="CODEX_V1_73_AHA_SET_EDITOR",
        recording_editor_policy_version=editor.POLICY_VERSION,
        supersedes_research_profile="CODEX_V1_72_1_FOCUS_FRAME_WRITER_EXIT",
        aha_discovery="S07_ATOMIC_SHORTLIST_MAX_8",
        aha_set_editor="S09_ONE_TEXT_ONLY_PLUS_CALL",
        aha_quantity_contract="ZERO_TO_THREE_ACTIVE_TARGET_TWO_TO_THREE_WHEN_SUPPORTED",
        aha_relation_scope="SELECTED_CHAPTER_AHA_AND_AHA_AHA_CLOSED_MATRIX",
        writer_policy_unchanged=prior.editor.POLICY_VERSION,
        additional_model_calls=1,
        editor_retry_or_automatic_fill="FORBIDDEN",
        deployment="RESEARCH_OPT_IN_ONLY",
    )
    return result


class ResearchGateway(prior.ResearchGateway):
    """Route S07, S09 and S11 to Plus; only S07 uses short-ref codec."""

    def call(self, stage, prompt, schema, evidence=(), context=None):
        if stage != editor.EDITOR_STAGE:
            return super().call(stage, prompt, schema, evidence=evidence, context=context)
        if evidence:
            raise x02.X02ContractError("V1.73 S09 Aha set editor is text-only")
        gateway = self.structure_gateway
        record = {
            "index": len(self.calls) + 1,
            "stage": stage,
            "model": gateway.model,
            "status": "PREPARED",
            "short_references": True,
        }
        self.calls.append(record)
        self._emit("PREPARED", record)
        try:
            run = routing._priced(gateway.call(
                stage, prompt, schema, evidence=evidence, context=context,
            ))
            if run.model != gateway.model:
                raise x02.X02ContractError(
                    "Research Aha set editor returned an unexpected model identity"
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
        raise ValueError("Use a fresh V1.73 research gateway for each run")
    result = x02.run_x02_v041(
        manifest_path, gateway, recording_editor_policy=editor.POLICY_VERSION,
    )
    return {
        "research_profile": profile(),
        "result": result,
        "gateway_audit": copy.deepcopy(gateway.calls),
    }

