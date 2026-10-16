"""V1.71 opt-in research entry; no Web/App or old research default changes."""

import copy

from . import codex_s07_research as prior
from . import codex_recording_editor as editor
from . import x02


def profile():
    result = prior.profile()
    result.update(version="CODEX_V1_71_RECORDING_CONTEXT_JOINT_SELECTION",
                  recording_editor_policy_version=editor.POLICY_VERSION,
                  supersedes_research_profile="CODEX_V1_70_S07_S09_EDITORIAL_ORDER",
                  input_scope="SUPPLIED_RECORDING_NOT_VERIFIED_COMPLETE_DAY")
    return result


make_gateway = prior.make_gateway


def run_research(manifest_path, gateway):
    if not isinstance(gateway, prior.ResearchGateway) or gateway.calls:
        raise ValueError("Use a fresh research gateway for each run")
    result = x02.run_x02_v041(manifest_path, gateway, recording_editor_policy=editor.POLICY_VERSION)
    return {"research_profile": profile(), "result": result,
            "gateway_audit": copy.deepcopy(gateway.calls)}
