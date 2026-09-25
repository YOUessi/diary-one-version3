"""V1.72.1 opt-in research entry; no Web/App or prior defaults changed."""

import copy

from . import codex_s07_research as prior
from . import codex_grounded_recording_editor as editor
from . import x02


def profile():
    result = prior.profile()
    result["stage_models"] = {
        **result["stage_models"],
        "S11_WRITER_*": prior.PLUS,
    }
    result.update(
        version="CODEX_V1_72_1_FOCUS_FRAME_WRITER_EXIT",
        recording_editor_policy_version=editor.POLICY_VERSION,
        supersedes_research_profile="CODEX_V1_72_RELATION_ATOMIC_WRITER",
        chapter_aha_pair_matrix="REQUIRED_FOR_SELECTED_SET",
        aha_aha_pair_matrix="REQUIRED_FOR_SELECTED_SET",
        aha_moment_scope="ONE_FACT_ONE_VALIDATED_FOCUS_FRAME",
        aha_value_scope="INDEPENDENTLY_REVISIT_WORTHY_EDITORIAL_JUDGMENT",
        aha_writer_visible_target=editor.AHA_WRITING_TARGET,
        aha_writer_visible_hard_max=editor.AHA_VISIBLE_MAX,
        writer_model_calls=1,
        grounded_aha_deterministic_fallback="FORBIDDEN",
        provider_constrained_decoding="NOT_CLAIMED_JSON_OBJECT_MODE_PLUS_LOCAL_RELEASE_GATE",
    )
    return result


class ResearchGateway(prior.ResearchGateway):
    """Keep S07 short references and route the one S11 call to Plus."""

    def call(self, stage, prompt, schema, evidence=(), context=None):
        if not stage.startswith("S11_"):
            return super().call(stage, prompt, schema, evidence=evidence, context=context)
        gateway = self.structure_gateway
        record = {
            "index": len(self.calls) + 1,
            "stage": stage,
            "model": gateway.model,
            "status": "PREPARED",
            "short_references": False,
        }
        self.calls.append(record)
        self._emit("PREPARED", record)
        try:
            run = prior._priced(gateway.call(
                stage, prompt, schema, evidence=evidence, context=context,
            ))
            if run.model != gateway.model:
                raise x02.X02ContractError(
                    "Research Writer returned an unexpected model identity"
                )
            record.update(status=run.call_status, metric=x02._metric_from_run(run))
            return run
        except Exception as exc:
            record.update(
                status="FAILED", error_type=type(exc).__name__,
                code=getattr(exc, "code", None),
            )
            if isinstance(exc, x02.X02StageCallError):
                exc.stage_run = prior._priced(exc.stage_run)
                record["metric"] = x02._metric_from_run(exc.stage_run)
            raise
        finally:
            self._emit("FINISHED", record)


def make_gateway(api_key, *, transport=None, audit_sink=None):
    base = prior.make_gateway(api_key, transport=transport, audit_sink=audit_sink)
    return ResearchGateway(
        base.default_gateway, base.structure_gateway, audit_sink=audit_sink,
    )


def run_research(manifest_path, gateway):
    if not isinstance(gateway, ResearchGateway) or gateway.calls:
        raise ValueError("Use a fresh research gateway for each run")
    result = x02.run_x02_v041(
        manifest_path, gateway, recording_editor_policy=editor.POLICY_VERSION,
    )
    return {"research_profile": profile(), "result": result,
            "gateway_audit": copy.deepcopy(gateway.calls)}
