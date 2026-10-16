"""Opt-in V1.69 research gateway; never installed in Web/App defaults.

Only S07 uses Plus and request-local references. All canonical facts, prompts,
schemas, candidate rules and subsequent stages remain owned by the V1.68 chain.
The codec makes no semantic decisions and never guesses a missing reference.
"""

import copy
import json
from dataclasses import replace

from . import x02
from .x01 import QwenChatCompletionsAdapter


VERSION = "CODEX_V1_69_S07_PLUS_SHORT_REFERENCES"
S07 = "S05_S07_STRUCTURE_PROPOSAL"
FLASH = "qwen3-vl-flash-2026-01-22"
PLUS = "qwen3.7-plus-2026-05-26"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
PRICE_BASIS = "BEIJING_LIST_RATE_SNAPSHOT_2026_09_07_NOT_ACCOUNT_BILL"
REF_KINDS = {key: "observations" for key in ("observation_id", "observation_ids")}
REF_KINDS.update({key: "facts" for key in
                 ("fact_id", "fact_ids", "event_fact_ids", "chapter_fact_ids", "aha_fact_ids")})


def profile():
    return {"version": VERSION, "default_model": FLASH, "stage_models": {S07: PLUS},
            "short_reference_stages": [S07], "reference_fields": list(REF_KINDS),
            "endpoint": BASE_URL + "/chat/completions", "enable_thinking": False,
            "short_ids_are": "REQUEST_LOCAL_REFERENCES_NOT_TIMESTAMPS_OR_CATEGORIES",
            "additional_model_calls": 0, "deployment": "RESEARCH_OPT_IN_ONLY",
            "pricing_basis": PRICE_BASIS}


def transform(value, maps, field=None, path=(), unknown=None):
    """Exact lookup in typed ID fields only; preserve prose and unknown values."""
    if isinstance(value, dict):
        return {key: transform(item, maps, key, path + (key,), unknown)
                for key, item in value.items()}
    if isinstance(value, list):
        return [transform(item, maps, field, path + (index,), unknown)
                for index, item in enumerate(value)]
    if isinstance(value, str) and field in REF_KINDS:
        table = maps[REF_KINDS[field]]
        if value in table:
            return table[value]
        if unknown is not None:
            unknown.append({"path": list(path), "unmapped_reference": value})
    return value


def maps_for(context):
    tables = {"observations": {}, "facts": {}}
    for observation in context["observations"]:
        entries = [("observations", observation["observation_id"], "O")]
        entries.extend(("facts", fact["fact_id"], "F") for fact in observation["facts"])
        for kind, identity, prefix in entries:
            if not isinstance(identity, str) or not identity or identity in tables[kind]:
                raise x02.X02ContractError("S07 requires unique nonempty canonical reference IDs")
            tables[kind][identity] = "%s%02d" % (prefix, len(tables[kind]) + 1)
    return {"forward": tables,
            "reverse": {kind: {short: long for long, short in table.items()}
                        for kind, table in tables.items()}}


def encode_request(prompt, context):
    """Keep the existing prompt prefix and schema; translate its JSON input only."""
    try:
        prefix, text = prompt.rsplit("Input:\n", 1)
        original = json.loads(text)
    except (ValueError, AttributeError) as exc:
        raise x02.X02ContractError("S07 request has no supported JSON input section") from exc
    if original != {key: value for key, value in context.items() if key != "_x02_policy_version"}:
        raise x02.X02ContractError("S07 prompt input and audit context disagree")
    mapping = maps_for(original)
    unknown = []
    short_input = transform(original, mapping["forward"], unknown=unknown)
    if unknown or transform(short_input, mapping["reverse"]) != original:
        raise x02.X02ContractError("S07 input references cannot be mapped reversibly")
    short_context = transform(context, mapping["forward"])
    return prefix + "Input:\n" + json.dumps(short_input, ensure_ascii=False), short_context, mapping


def pricing_rates(model, incoming):
    """Historical public list estimate only; provider total tokens counted once."""
    if model == PLUS:
        return (2.0, 8.0) if incoming <= 256000 else (6.0, 24.0)
    if model == FLASH:
        rate = 0.15 if incoming <= 32768 else 0.30 if incoming <= 131072 else 0.60
        return rate, rate * 10
    raise ValueError("Model has no price in this frozen research profile")


def _priced(run):
    incoming, outgoing = pricing_rates(run.model, run.input_tokens)
    return replace(run, pricing_currency="CNY", input_rate_per_million=incoming,
                   output_rate_per_million=outgoing, pricing_basis=PRICE_BASIS)


class ResearchGateway(x02.StageModelGateway):
    """One delegated call per stage; decode S07 before existing candidate checks.

    audit_sink(event, record), if supplied, receives local audit copies, never
    credentials. Persist them outside public output; records contain user facts.
    No downstream request can access the request-local short-ID map.
    """

    def __init__(self, default_gateway, structure_gateway, audit_sink=None):
        if default_gateway.model != FLASH or structure_gateway.model != PLUS:
            raise ValueError("Research model routing differs from the frozen profile")
        if default_gateway.provider != structure_gateway.provider:
            raise ValueError("Research gateways must use the same provider")
        self.default_gateway = default_gateway
        self.structure_gateway = structure_gateway
        self.provider = default_gateway.provider
        self.model = "mixed:" + FLASH + "+" + PLUS
        self.credential_environment = default_gateway.credential_environment
        self.audit_sink = audit_sink
        self.calls = []

    @property
    def ready(self):
        return self.default_gateway.ready and self.structure_gateway.ready

    def _emit(self, event, record):
        if self.audit_sink is not None:
            self.audit_sink(event, copy.deepcopy(record))

    def call(self, stage, prompt, schema, evidence=(), context=None):
        gateway = self.structure_gateway if stage == S07 else self.default_gateway
        mapping = None
        sent_prompt, sent_context = prompt, context
        if stage == S07:
            if evidence:
                raise x02.X02ContractError("This research S07 profile is text-only")
            sent_prompt, sent_context, mapping = encode_request(prompt, context or {})
        record = {"index": len(self.calls) + 1, "stage": stage, "model": gateway.model,
                  "status": "PREPARED", "short_references": mapping is not None}
        if mapping is not None:
            record.update(reference_map=mapping, wire_prompt=sent_prompt, wire_context=sent_context)
        self.calls.append(record)
        self._emit("PREPARED", record)
        try:
            run = _priced(gateway.call(stage, sent_prompt, schema,
                                       evidence=evidence, context=sent_context))
            if run.model != gateway.model:
                raise x02.X02ContractError("Research stage returned an unexpected model identity")
            if mapping is not None:
                unknown = []
                output = transform(run.output, mapping["reverse"], unknown=unknown)
                record.update(raw_short_output=copy.deepcopy(run.output),
                              decoded_output=copy.deepcopy(output), unknown_short_references=unknown)
                run = replace(run, output=output)
            record.update(status=run.call_status, metric=x02._metric_from_run(run))
            return run
        except Exception as exc:
            record.update(status="FAILED", error_type=type(exc).__name__, code=getattr(exc, "code", None))
            if isinstance(exc, x02.X02StageCallError):
                exc.stage_run = _priced(exc.stage_run)
                record["metric"] = x02._metric_from_run(exc.stage_run)
            raise
        finally:
            self._emit("FINISHED", record)


def make_gateway(api_key, *, transport=None, audit_sink=None):
    """Explicit key injection; no credential reads, global settings or defaults changed."""
    delegates = []
    for model in (FLASH, PLUS):
        adapter = QwenChatCompletionsAdapter(api_key=api_key, model=model, base_url=BASE_URL,
                                            timeout_seconds=180, transport=transport)
        adapter.input_rate_per_million, adapter.output_rate_per_million = pricing_rates(model, 0)
        adapter.pricing_basis = PRICE_BASIS
        delegates.append(x02.QwenStageGateway(adapter))
    return ResearchGateway(*delegates, audit_sink=audit_sink)


def run_research(manifest_path, gateway):
    """Full existing S04-S12 function entry, not S13 export or Web deployment.

    A caller must supply freshly normalized evidence for a fresh real test.
    Offline replay is also possible and must be labelled as replay by the caller.
    """
    if not isinstance(gateway, ResearchGateway) or gateway.calls:
        raise ValueError("Use a fresh V1.69 research gateway for each run")
    result = x02.run_x02_v041(manifest_path, gateway)
    return {"research_profile": profile(), "result": result,
            "gateway_audit": copy.deepcopy(gateway.calls)}
