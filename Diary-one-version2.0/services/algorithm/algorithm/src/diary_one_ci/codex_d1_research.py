"""V1.70 opt-in entry. V1.69 gateway and Web/App defaults remain unchanged."""

import copy

from . import codex_editorial_order as editorial_order
from . import codex_s07_research as prior
from . import x02


def profile():
    result = prior.profile()
    result.update(version="CODEX_V1_70_S07_S09_EDITORIAL_ORDER",
                  editorial_order_policy_version=editorial_order.POLICY_VERSION,
                  supersedes_research_profile=prior.VERSION)
    return result


make_gateway = prior.make_gateway


def run_research(manifest_path, gateway):
    if not isinstance(gateway, prior.ResearchGateway) or gateway.calls:
        raise ValueError("Use a fresh research gateway for each run")
    result = x02.run_x02_v041(manifest_path, gateway,
                             editorial_order_policy=editorial_order.POLICY_VERSION)
    return {"research_profile": profile(), "result": result,
            "gateway_audit": copy.deepcopy(gateway.calls)}
