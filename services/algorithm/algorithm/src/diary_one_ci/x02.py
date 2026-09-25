from __future__ import annotations

import base64
import copy
import itertools
import json
import math
import re
import time
import unicodedata
import uuid
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .bundle import (
    APP_LIBRARY_BUNDLE_VERSION_V02,
    APP_LIBRARY_BUNDLE_VERSION_V03,
    APP_LIBRARY_BUNDLE_VERSION_V04,
    ImportedEvidenceBundle,
    load_app_library_bundle,
)
from .core import canonical_bytes, sha256_bytes, sha256_file
from . import codex_chapter_media as chapter_display
from . import codex_chapter_coherence as chapter_coherence
from . import codex_content_brief as content_handoff
from . import codex_editorial_allocation as editorial_allocation
from . import codex_structure_wire as structure_wire
from . import codex_editorial_order as editorial_order
from . import codex_recording_editor as recording_editor
from . import codex_grounded_recording_editor as grounded_recording_editor
from . import codex_aha_set_editor as aha_set_editor
from . import codex_experience_editor as experience_editor
from . import codex_v174_writer as v174_writer
from . import codex_writer_exit as writer_exit
from .x01 import (
    EditorialModelAdapter,
    FixtureEditorialAdapter,
    OpenAIResponsesAdapter,
    QwenChatCompletionsAdapter,
    Transport,
    X01Error,
    _chat_completions_output_text,
    _responses_output_text,
)


X02_V03_SCHEMA_VERSION = "DIARY_ONE_X02_STAGED_PREVIEW_V03"
X02_V03_PIPELINE_VERSION = "X02_STAGED_REAL_MEDIA_PREVIEW_V03"
X02_V03_PREVIEW_PATH = "/x02/v0.3/preview"
X02_V03_RUN_SIDECAR_PATH = "/x02/v0.3/run-sidecar"
X02_V041_SCHEMA_VERSION = "DIARY_ONE_X02_STAGED_PREVIEW_V04_1"
X02_V041_PIPELINE_VERSION = "X02_STAGED_REAL_MEDIA_PREVIEW_V04_1"
X02_V041_PREVIEW_PATH = "/x02/v0.4.1/preview"
X02_V041_RUN_SIDECAR_PATH = "/x02/v0.4.1/run-sidecar"
X02_SCHEMA_VERSION = X02_V041_SCHEMA_VERSION
X02_EXPERIMENT = "X02_STAGED_REAL_MEDIA_PREVIEW"
X02_PIPELINE_VERSION = X02_V041_PIPELINE_VERSION
X02_PREVIEW_PATH = X02_V041_PREVIEW_PATH
X02_RUN_SIDECAR_PATH = X02_V041_RUN_SIDECAR_PATH
X02_EVALUATION_RUN_MODE = "FRESH_FULL_RUN"
X02_FIELD_DEGRADATION_VERSION = "DIARY_ONE_X02_FIELD_DEGRADATION_V01"
X02_STORYLINE_CONTRACT_VERSION = "DIARY_ONE_X02_STORYLINE_V03"
X02_WRITER_SURFACE_POLICY_VERSION = "DIARY_ONE_X02_WRITER_SURFACE_V02"
X02_WRITER_GROUNDING_POLICY = "MODEL_GROUNDED_NATURAL_LANGUAGE_V02"
X02_FACT_RETENTION_POLICY_VERSION = "DIARY_ONE_X02_FACT_RETENTION_V01"
X02_AHA_PAIR_CONFLICT_POLICY_VERSION = "DIARY_ONE_X02_AHA_PAIR_CONFLICT_V02"
X02_STRUCTURE_ACCEPTANCE_POLICY_VERSION = "DIARY_ONE_X02_STRUCTURE_ACCEPTANCE_V01"
PERCEPTION_BATCH_MAX_ASSETS = 3
PERCEPTION_BATCH_MAX_FRAMES = 18
PERCEPTION_BATCH_MAX_EVIDENCE_BYTES = 4 * 1024 * 1024
PERCEPTION_SINGLE_ASSET_RETRY_LIMIT = 1
# Fact text is evidence-ledger data, not final user copy. The concise target
# guides S04 output; the larger bounded envelope prevents a formatting miss
# from deleting otherwise grounded evidence. Only V04.1 uses the envelope so
# historical V03 behavior remains compatible.
PERCEPTION_FACT_CONCISE_TARGET_CHARS = 200
PERCEPTION_FACT_PAYLOAD_MAX_CHARS = 1_000
# One V04.1 run may process the server maximum of 240 assets in 80 normal
# perception calls, plus Structure and two Writer attempts. 96 therefore leaves
# room for the complete supported day while still stopping recursive failure
# amplification. This is an operational stop-loss, not a quality threshold.
V041_RUN_MAX_MODEL_CALL_ATTEMPTS = 96
PERCEPTION_V03_BATCH_SIZE = 6
MAX_CHAPTERS = 4
MAX_AHAS = 3
# Internal explanation guidance only, never a candidate eligibility gate.
STORYLINE_THESIS_TARGET_MIN = 2
STORYLINE_THESIS_TARGET_MAX = 160
AHA_NARRATIVE_DUTY_LEGACY_MAX = 120
CHAPTER_TITLE_VISIBLE_MIN = 2
CHAPTER_TITLE_VISIBLE_TARGET_MAX = 10
CHAPTER_TITLE_VISIBLE_HARD_MAX = 12
CHAPTER_STORY_SENTENCE_MIN = 1
CHAPTER_STORY_SENTENCE_MAX = 2
# X02 writing target only. The frozen product contract is sentence-based and
# does not authorize a 48-character rejection gate for Chapter Story.
CHAPTER_STORY_PREVIEW_TARGET_VISIBLE_MAX = 48
# Archived Writer contracts only; current zh-Hans V02 uses writer_exit soft targets.
AHA_MOMENT_LINE_VISIBLE_MAX = 20
WRITER_TITLE_PAYLOAD_MAX = 256
WRITER_TEXT_PAYLOAD_MAX = 2_000
WRITER_AUDIT_TEXT_MAX = 500


OBSERVATION_STATUSES = frozenset({
    "OBSERVED", "PARTIAL", "INSUFFICIENT_EVIDENCE", "FAILED",
})
SUPPORT_GRADES = frozenset({"STRONG", "MODERATE", "WEAK"})
SETTING_CODES = frozenset({
    "HISTORIC_STREET",
    "COMMERCIAL_MARKET",
    "NATURE_TRAIL",
    "CAFE_TEA_SHOP",
    "HOME",
    "WORKPLACE",
    "INDOOR_PUBLIC",
    "URBAN_STREET",
    "TRANSIT",
    "OTHER",
    "UNKNOWN",
})
ACTIVITY_CODES = frozenset({
    "WALKING",
    "BROWSING",
    "EATING_DRINKING",
    "CRAFT",
    "GATHERING",
    "WORKING",
    "OBSERVING",
    "TRANSIT",
    "OTHER",
    "UNKNOWN",
})
EPISODE_CODES = frozenset({
    "HISTORIC_TOWN_WALK",
    "MARKET_VISIT",
    "NATURE_WALK",
    "CAFE_STOP",
    "HOME_LIFE",
    "WORK",
    "MEAL",
    "CRAFT_SESSION",
    "BIRTHDAY_GATHERING",
    "SOCIAL_GATHERING",
    "URBAN_WALK",
    "TRANSIT",
    "OTHER",
    "UNKNOWN",
})
SUBJECT_CODES = frozenset({
    "HISTORIC_ARCHITECTURE",
    "CAT",
    "DOG",
    "FOOD_DESSERT",
    "CRAFT_OBJECT",
    "PEOPLE",
    "LANDSCAPE",
    "STREET_SCENE",
    "OTHER",
    "UNKNOWN",
})
# Current preview uses broad animal classification; species stay in source facts.
# Keep the historical vocabulary and canonical registry unchanged.
SUBJECT_GRANULARITY_VERSION = "DIARY_ONE_X02_SUBJECT_GRANULARITY_V02"
GENERIC_SUBJECT_CODES = (SUBJECT_CODES - {"CAT", "DOG"}) | {"ANIMAL"}
EVENT_KINDS = frozenset({
    "NONE",
    "ACTION",
    "INTERACTION",
    "TRANSITION",
    "DISCOVERY",
    "REACTION",
    "RESULT",
    "CEREMONY",
    "PLAYFUL_ANIMAL",
    "FOOD_MOMENT",
    "OTHER",
})
EVENT_SALIENCE = frozenset({"NONE", "LOW", "MEDIUM", "HIGH"})
PEAK_EVENT_KINDS = frozenset({
    "INTERACTION", "DISCOVERY", "REACTION", "RESULT", "CEREMONY",
    "PLAYFUL_ANIMAL", "FOOD_MOMENT",
})
UNSUPPORTED_USER_STATE_TERMS = (
    "最爱", "难忘", "幸福", "好吃", "惊喜", "悠闲", "开心",
)

X02_OBSERVATION_COMPATIBILITY_VERSION = "DIARY_ONE_X02_OBSERVATION_COMPATIBILITY_V02"


def _load_observation_compatibility_v02() -> Dict[str, object]:
    contract_path = resources.files("diary_one_ci.contracts").joinpath(
        "x02_observation_compatibility_v02.json"
    )
    value = json.loads(contract_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("X02 V02 observation compatibility contract must be an object")
    if value.get("schema_version") != X02_OBSERVATION_COMPATIBILITY_VERSION:
        raise RuntimeError("X02 V02 observation compatibility identity mismatch")
    return value


X02_OBSERVATION_COMPATIBILITY = _load_observation_compatibility_v02()
X02_OBSERVATION_COMPATIBILITY_SHA256 = sha256_bytes(
    canonical_bytes(X02_OBSERVATION_COMPATIBILITY)
)


def _load_field_degradation_v01() -> Dict[str, object]:
    contract_path = resources.files("diary_one_ci.contracts").joinpath(
        "x02_field_degradation_v01.json"
    )
    value = json.loads(contract_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("X02 field degradation contract must be an object")
    if value.get("schema_version") != X02_FIELD_DEGRADATION_VERSION:
        raise RuntimeError("X02 field degradation contract identity mismatch")
    return value


X02_FIELD_DEGRADATION = _load_field_degradation_v01()
X02_FIELD_DEGRADATION_SHA256 = sha256_bytes(canonical_bytes(X02_FIELD_DEGRADATION))


def _load_storyline_v03() -> Dict[str, object]:
    contract_path = resources.files("diary_one_ci.contracts").joinpath(
        "codex_x02_storyline_v03.json"
    )
    value = json.loads(contract_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("X02 Storyline contract must be an object")
    if value.get("schema_version") != X02_STORYLINE_CONTRACT_VERSION:
        raise RuntimeError("X02 Storyline contract identity mismatch")
    return value


X02_STORYLINE_CONTRACT = _load_storyline_v03()
X02_STORYLINE_CONTRACT_SHA256 = sha256_bytes(canonical_bytes(X02_STORYLINE_CONTRACT))
STORYLINE_BASES = frozenset(X02_STORYLINE_CONTRACT["storyline_bases"])
STORYLINE_BEAT_ROLES = frozenset(X02_STORYLINE_CONTRACT["beat_roles"])


def _validated_compatibility_rule_index() -> Dict[str, Mapping[str, object]]:
    generic_raw = X02_OBSERVATION_COMPATIBILITY.get("generic_episode_codes")
    rules_raw = X02_OBSERVATION_COMPATIBILITY.get("episode_rules")
    if not isinstance(generic_raw, list) or not isinstance(rules_raw, list):
        raise RuntimeError("X02 V02 observation compatibility contract shape is invalid")
    generic = set(generic_raw)
    if generic != {"OTHER", "UNKNOWN"}:
        raise RuntimeError("X02 V02 generic Episode contract is invalid")
    index: Dict[str, Mapping[str, object]] = {}
    rule_ids = set()
    code_sets = {
        "setting_codes": SETTING_CODES,
        "activity_codes": ACTIVITY_CODES,
        "event_kinds": EVENT_KINDS,
    }
    for rule in rules_raw:
        if not isinstance(rule, dict):
            raise RuntimeError("X02 V02 Episode rule must be an object")
        episode_code = rule.get("episode_code")
        rule_id = rule.get("rule_id")
        clauses = rule.get("clauses")
        if (
            not isinstance(episode_code, str)
            or episode_code not in EPISODE_CODES
            or episode_code in generic
            or episode_code in index
            or not isinstance(rule_id, str)
            or not rule_id
            or rule_id in rule_ids
            or not isinstance(clauses, list)
            or not clauses
        ):
            raise RuntimeError("X02 V02 Episode rule identity or clauses are invalid")
        for clause in clauses:
            if not isinstance(clause, dict) or not clause:
                raise RuntimeError("X02 V02 compatibility clause must be a non-empty object")
            if set(clause) - set(code_sets):
                raise RuntimeError("X02 V02 compatibility clause has an unknown dimension")
            for field, allowed_codes in clause.items():
                if (
                    not isinstance(allowed_codes, list)
                    or not allowed_codes
                    or len(set(allowed_codes)) != len(allowed_codes)
                    or any(code not in code_sets[field] for code in allowed_codes)
                ):
                    raise RuntimeError("X02 V02 compatibility clause vocabulary is invalid")
        index[episode_code] = rule
        rule_ids.add(rule_id)
    if set(index) != set(EPISODE_CODES) - generic:
        raise RuntimeError("X02 V02 compatibility rules do not cover every specific Episode")
    return index


X02_EPISODE_RULES = _validated_compatibility_rule_index()
X02_GENERIC_EPISODE_CODES = frozenset(
    X02_OBSERVATION_COMPATIBILITY["generic_episode_codes"]
)


def _episode_compatibility(
    setting_code: str,
    activity_code: str,
    episode_code: str,
    event_kind: str,
) -> Tuple[bool, str]:
    if episode_code in X02_GENERIC_EPISODE_CODES:
        return True, "X02V02_GENERIC_EPISODE"
    rule = X02_EPISODE_RULES[episode_code]
    actual = {
        "setting_codes": setting_code,
        "activity_codes": activity_code,
        "event_kinds": event_kind,
    }
    clauses = rule["clauses"]
    if any(all(actual[field] in allowed for field, allowed in clause.items()) for clause in clauses):
        return True, str(rule["rule_id"])
    return False, str(rule["rule_id"])


def _compatibility_prompt_payload() -> Dict[str, object]:
    return {
        "schema_version": X02_OBSERVATION_COMPATIBILITY_VERSION,
        "sha256": X02_OBSERVATION_COMPATIBILITY_SHA256,
        "matching_semantics": X02_OBSERVATION_COMPATIBILITY["matching_semantics"],
        "generic_episode_codes": X02_OBSERVATION_COMPATIBILITY["generic_episode_codes"],
        "episode_rules": X02_OBSERVATION_COMPATIBILITY["episode_rules"],
    }

SETTING_TAGS = {
    "HISTORIC_STREET": "SETTING.TRADITIONAL_HISTORIC_DISTRICT",
    "NATURE_TRAIL": "SETTING.OUTDOOR_NATURE",
    "CAFE_TEA_SHOP": "SETTING.CAFE_OR_TEA_SHOP",
    "HOME": "SETTING.HOME",
    "WORKPLACE": "SETTING.WORKPLACE",
}
SUBJECT_TAGS = {
    "HISTORIC_ARCHITECTURE": "CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE",
    "CAT": "CENTRAL_SUBJECT.CAT",
    "DOG": "CENTRAL_SUBJECT.DOG",
    "FOOD_DESSERT": "CENTRAL_SUBJECT.FOOD_OR_DESSERT",
    "CRAFT_OBJECT": "CENTRAL_SUBJECT.CRAFT_OBJECT",
}
ACTIVITY_TAGS = {
    "WALKING": "ACTIVITY.WALKING",
    "CRAFT": "ACTIVITY.CRAFT",
}
EPISODE_TAGS = {
    "HISTORIC_TOWN_WALK": "ACTIVITY.CITY_WALK",
    "URBAN_WALK": "ACTIVITY.CITY_WALK",
    "CRAFT_SESSION": "ACTIVITY.CRAFT",
    "BIRTHDAY_GATHERING": "OCCASION.BIRTHDAY",
}


class X02Error(RuntimeError):
    pass


class X02ModelNotReady(X02Error):
    pass


class X02ContractError(X02Error):
    pass


class X02CallAttemptLimitReached(X02Error):
    pass


class X02ObservationContractError(X02ContractError):
    def __init__(self, message: str, *, rule_id: str, json_field_path: str) -> None:
        super().__init__(message)
        self.rule_id = rule_id
        self.json_field_path = json_field_path


class X02StageCallError(X02Error):
    def __init__(self, message: str, *, stage_run: "StageRun", code: str) -> None:
        super().__init__(message)
        self.stage_run = stage_run
        self.code = code


class X02ExecutionError(X02Error):
    def __init__(
        self,
        message: str,
        *,
        stage: str,
        code: str,
        stage_runs: Sequence["StageRun"],
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.code = code
        self.stage_runs = tuple(stage_runs)


@dataclass(frozen=True)
class StageRun:
    stage: str
    output: Dict[str, object]
    provider: str
    model: str
    request_id: str
    input_tokens: int
    output_tokens: int
    latency_seconds: float
    model_frame_count: int
    model_calls: int
    pricing_currency: str
    input_rate_per_million: float
    output_rate_per_million: float
    native_currency_per_usd: float
    pricing_basis: str
    selected_evidence: Tuple[Dict[str, object], ...] = ()
    call_status: str = "COMPLETED"

    @property
    def estimated_cost_native(self) -> float:
        return (
            self.input_tokens * self.input_rate_per_million
            + self.output_tokens * self.output_rate_per_million
        ) / 1_000_000

    @property
    def estimated_cost_usd(self) -> float:
        return self.estimated_cost_native / self.native_currency_per_usd


def _transport_failure_code(exc: Exception) -> str:
    if isinstance(exc, TimeoutError) or "timed out" in str(exc).casefold():
        return "MODEL_TRANSPORT_TIMEOUT"
    return "MODEL_TRANSPORT_FAILED"


def _call_stage_transport(
    *,
    stage: str,
    transport: Transport,
    url: str,
    headers: Mapping[str, str],
    body: bytes,
    timeout_seconds: float,
    provider: str,
    model: str,
    selected_evidence: Sequence[Mapping[str, object]],
    frame_count: int,
    pricing_currency: str,
    input_rate: float,
    output_rate: float,
    native_per_usd: float,
    pricing_basis: str,
    audit_pre_response_failures: bool,
) -> Tuple[int, Mapping[str, str], bytes, float]:
    """Turn pre-response transport failures into an auditable failed stage run.

    HTTP responses still flow through the provider-specific historical handling
    below. This boundary only covers failures for which no HTTP response exists.
    """

    started = time.monotonic()
    try:
        status, response_headers, response_data = transport(
            url, headers, body, timeout_seconds
        )
    except (X01Error, TimeoutError, OSError) as exc:
        # Historical V03 allowed the adapter/transport exception to reach the
        # server's legacy model_request_failed boundary. Only V04.1 turns the
        # failed attempt into a StageRun; otherwise the public V03 envelope
        # would drift merely because the new preview exists.
        if not audit_pre_response_failures:
            raise
        latency = time.monotonic() - started
        code = _transport_failure_code(exc)
        failure_run = _failed_stage_run(
            stage=stage,
            provider=provider,
            model=model,
            request_id="%s-transport-no-response" % provider,
            latency_seconds=latency,
            evidence=selected_evidence,
            frame_count=frame_count,
            pricing_currency=pricing_currency,
            input_rate=input_rate,
            output_rate=output_rate,
            native_per_usd=native_per_usd,
            pricing_basis=pricing_basis,
            call_status="FAILED_BEFORE_RESPONSE",
        )
        raise X02StageCallError(
            "%s model transport failed before an HTTP response: %s" % (stage, exc),
            stage_run=failure_run,
            code=code,
        ) from exc
    return status, response_headers, response_data, time.monotonic() - started


class StageModelGateway:
    provider = "abstract"
    model = "abstract"

    @property
    def ready(self) -> bool:
        return False

    def call(
        self,
        stage: str,
        prompt: str,
        schema: Mapping[str, object],
        evidence: Sequence[Tuple[Mapping[str, object], Mapping[str, object], Path]] = (),
        context: Optional[Mapping[str, object]] = None,
    ) -> StageRun:
        raise NotImplementedError


class _RecordingStageGateway(StageModelGateway):
    def __init__(self, gateway: StageModelGateway) -> None:
        self.gateway = gateway
        self.provider = gateway.provider
        self.model = gateway.model
        self.credential_environment = getattr(gateway, "credential_environment", "MODEL_API_KEY")
        self.runs: List[StageRun] = []

    @property
    def ready(self) -> bool:
        return self.gateway.ready

    def call(
        self,
        stage: str,
        prompt: str,
        schema: Mapping[str, object],
        evidence: Sequence[Tuple[Mapping[str, object], Mapping[str, object], Path]] = (),
        context: Optional[Mapping[str, object]] = None,
    ) -> StageRun:
        run = self.gateway.call(stage, prompt, schema, evidence=evidence, context=context)
        self.runs.append(run)
        return run


class QwenStageGateway(StageModelGateway):
    def __init__(self, adapter: QwenChatCompletionsAdapter) -> None:
        self.adapter = adapter
        self.provider = adapter.provider
        self.model = adapter.model
        self.credential_environment = adapter.credential_environment

    @property
    def ready(self) -> bool:
        return self.adapter.ready

    def call(
        self,
        stage: str,
        prompt: str,
        schema: Mapping[str, object],
        evidence: Sequence[Tuple[Mapping[str, object], Mapping[str, object], Path]] = (),
        context: Optional[Mapping[str, object]] = None,
    ) -> StageRun:
        if not self.ready:
            raise X02ModelNotReady(
                "X02 requires DASHSCOPE_API_KEY on the local research server."
            )
        context = context or {}
        audit_v041_failures = context.get("_x02_policy_version") == "V04_1"
        full_prompt = (
            prompt
            + "\nReturn exactly one valid JSON object. Do not include markdown. "
            + "The object must conform to this schema:\n"
            + json.dumps(schema, ensure_ascii=False)
        )
        content: List[Dict[str, object]] = [{"type": "text", "text": full_prompt}]
        selected = []
        for order, (asset, frame, path) in enumerate(evidence):
            label = _evidence_label(asset, frame)
            content.append({"type": "text", "text": label})
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            content.append({
                "type": "image_url",
                "image_url": {"url": "data:image/jpeg;base64," + encoded},
            })
            selected.append(_evidence_ledger_entry(order, asset, frame))
        body = {
            "model": self.adapter.model,
            "messages": [{"role": "user", "content": content}],
            "response_format": {"type": "json_object"},
            "enable_thinking": False,
            "stream": False,
        }
        headers = {
            "Authorization": "Bearer " + self.adapter.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        status, response_headers, response_data, latency = _call_stage_transport(
            stage=stage,
            transport=self.adapter.transport,
            url=self.adapter.base_url + "/chat/completions",
            headers=headers,
            body=canonical_bytes(body),
            timeout_seconds=self.adapter.timeout_seconds,
            provider=self.adapter.provider,
            model=self.adapter.model,
            selected_evidence=selected,
            frame_count=len(evidence),
            pricing_currency="CNY",
            input_rate=self.adapter.input_rate_per_million,
            output_rate=self.adapter.output_rate_per_million,
            native_per_usd=self.adapter.native_currency_per_usd,
            pricing_basis=self.adapter.pricing_basis,
            audit_pre_response_failures=audit_v041_failures,
        )
        if status < 200 or status >= 300:
            message = response_data[:2_048].decode("utf-8", errors="replace")
            if not audit_v041_failures:
                raise X02Error(
                    "%s model request failed: %s" % (stage, message)
                )
            failure_run = _failed_stage_run(
                stage=stage,
                provider=self.adapter.provider,
                model=self.adapter.model,
                request_id=str(
                    response_headers.get("x-request-id")
                    or response_headers.get("X-Request-Id")
                    or response_headers.get("x-dashscope-request-id")
                    or response_headers.get("X-DashScope-Request-Id")
                    or "qwen-request-unknown"
                ),
                latency_seconds=latency,
                evidence=selected,
                frame_count=len(evidence),
                pricing_currency="CNY",
                input_rate=self.adapter.input_rate_per_million,
                output_rate=self.adapter.output_rate_per_million,
                native_per_usd=self.adapter.native_currency_per_usd,
                pricing_basis=self.adapter.pricing_basis,
                call_status="HTTP_FAILED",
            )
            raise X02StageCallError(
                "%s model request failed with HTTP %s: %s" % (stage, status, message),
                stage_run=failure_run,
                code="MODEL_HTTP_%d" % status,
            )
        try:
            payload = json.loads(response_data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            failure_run = _failed_stage_run(
                stage=stage,
                provider=self.adapter.provider,
                model=self.adapter.model,
                request_id=str(
                    response_headers.get("x-request-id")
                    or response_headers.get("X-Request-Id")
                    or "qwen-request-unknown"
                ),
                latency_seconds=latency,
                evidence=selected,
                frame_count=len(evidence),
                pricing_currency="CNY",
                input_rate=self.adapter.input_rate_per_million,
                output_rate=self.adapter.output_rate_per_million,
                native_per_usd=self.adapter.native_currency_per_usd,
                pricing_basis=self.adapter.pricing_basis,
                call_status="RESPONSE_INVALID",
            )
            raise X02StageCallError(
                "%s returned a non-JSON response" % stage,
                stage_run=failure_run,
                code="MODEL_RESPONSE_NOT_JSON",
            ) from exc
        payload_object = payload if isinstance(payload, dict) else {}
        usage = payload_object.get("usage", {})
        usage = usage if isinstance(usage, dict) else {}
        request_id = str(
            response_headers.get("x-request-id")
            or response_headers.get("X-Request-Id")
            or response_headers.get("x-dashscope-request-id")
            or response_headers.get("X-DashScope-Request-Id")
            or payload_object.get("request_id")
            or payload_object.get("id")
            or "qwen-request-unknown"
        )
        try:
            output = json.loads(_chat_completions_output_text(payload_object))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            failure_run = _failed_stage_run(
                stage=stage,
                provider=self.adapter.provider,
                model=self.adapter.model,
                request_id=request_id,
                latency_seconds=latency,
                evidence=selected,
                frame_count=len(evidence),
                pricing_currency="CNY",
                input_rate=self.adapter.input_rate_per_million,
                output_rate=self.adapter.output_rate_per_million,
                native_per_usd=self.adapter.native_currency_per_usd,
                pricing_basis=self.adapter.pricing_basis,
                input_tokens=int(usage.get("prompt_tokens", usage.get("input_tokens", 0))),
                output_tokens=int(usage.get("completion_tokens", usage.get("output_tokens", 0))),
                call_status="RESPONSE_INVALID",
            )
            raise X02StageCallError(
                "%s returned no valid structured output" % stage,
                stage_run=failure_run,
                code="MODEL_STRUCTURED_OUTPUT_INVALID",
            ) from exc
        return StageRun(
            stage=stage,
            output=output,
            provider=self.adapter.provider,
            model=self.adapter.model,
            request_id=request_id,
            input_tokens=int(usage.get("prompt_tokens", usage.get("input_tokens", 0))),
            output_tokens=int(usage.get("completion_tokens", usage.get("output_tokens", 0))),
            latency_seconds=latency,
            model_frame_count=len(evidence),
            model_calls=1,
            pricing_currency="CNY",
            input_rate_per_million=self.adapter.input_rate_per_million,
            output_rate_per_million=self.adapter.output_rate_per_million,
            native_currency_per_usd=self.adapter.native_currency_per_usd,
            pricing_basis=self.adapter.pricing_basis,
            selected_evidence=tuple(selected),
        )


class OpenAIStageGateway(StageModelGateway):
    def __init__(self, adapter: OpenAIResponsesAdapter) -> None:
        self.adapter = adapter
        self.provider = adapter.provider
        self.model = adapter.model
        self.credential_environment = adapter.credential_environment

    @property
    def ready(self) -> bool:
        return self.adapter.ready

    def call(
        self,
        stage: str,
        prompt: str,
        schema: Mapping[str, object],
        evidence: Sequence[Tuple[Mapping[str, object], Mapping[str, object], Path]] = (),
        context: Optional[Mapping[str, object]] = None,
    ) -> StageRun:
        if not self.ready:
            raise X02ModelNotReady(
                "X02 requires OPENAI_API_KEY on the local research server."
            )
        context = context or {}
        audit_v041_failures = context.get("_x02_policy_version") == "V04_1"
        content: List[Dict[str, object]] = [{"type": "input_text", "text": prompt}]
        selected = []
        for order, (asset, frame, path) in enumerate(evidence):
            content.append({"type": "input_text", "text": _evidence_label(asset, frame)})
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            content.append({
                "type": "input_image",
                "image_url": "data:image/jpeg;base64," + encoded,
                "detail": "low",
            })
            selected.append(_evidence_ledger_entry(order, asset, frame))
        body = {
            "model": self.adapter.model,
            "store": False,
            "input": [{"role": "user", "content": content}],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "diary_one_%s" % stage.lower(),
                    "strict": True,
                    "schema": schema,
                }
            },
        }
        headers = {
            "Authorization": "Bearer " + self.adapter.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        status, response_headers, response_data, latency = _call_stage_transport(
            stage=stage,
            transport=self.adapter.transport,
            url="https://api.openai.com/v1/responses",
            headers=headers,
            body=canonical_bytes(body),
            timeout_seconds=self.adapter.timeout_seconds,
            provider=self.adapter.provider,
            model=self.adapter.model,
            selected_evidence=selected,
            frame_count=len(evidence),
            pricing_currency="USD",
            input_rate=self.adapter.input_rate_per_million,
            output_rate=self.adapter.output_rate_per_million,
            native_per_usd=1.0,
            pricing_basis="openai-public-rate-config-2026-08-18",
            audit_pre_response_failures=audit_v041_failures,
        )
        if status < 200 or status >= 300:
            message = response_data[:2_048].decode("utf-8", errors="replace")
            if not audit_v041_failures:
                raise X02Error(
                    "%s model request failed: %s" % (stage, message)
                )
            failure_run = _failed_stage_run(
                stage=stage,
                provider=self.adapter.provider,
                model=self.adapter.model,
                request_id=str(
                    response_headers.get("x-request-id")
                    or response_headers.get("X-Request-Id")
                    or "openai-request-unknown"
                ),
                latency_seconds=latency,
                evidence=selected,
                frame_count=len(evidence),
                pricing_currency="USD",
                input_rate=self.adapter.input_rate_per_million,
                output_rate=self.adapter.output_rate_per_million,
                native_per_usd=1.0,
                pricing_basis="openai-public-rate-config-2026-08-18",
                call_status="HTTP_FAILED",
            )
            raise X02StageCallError(
                "%s model request failed with HTTP %s: %s" % (stage, status, message),
                stage_run=failure_run,
                code="MODEL_HTTP_%d" % status,
            )
        try:
            payload = json.loads(response_data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            failure_run = _failed_stage_run(
                stage=stage,
                provider=self.adapter.provider,
                model=self.adapter.model,
                request_id=str(
                    response_headers.get("x-request-id")
                    or response_headers.get("X-Request-Id")
                    or "openai-request-unknown"
                ),
                latency_seconds=latency,
                evidence=selected,
                frame_count=len(evidence),
                pricing_currency="USD",
                input_rate=self.adapter.input_rate_per_million,
                output_rate=self.adapter.output_rate_per_million,
                native_per_usd=1.0,
                pricing_basis="openai-public-rate-config-2026-08-18",
                call_status="RESPONSE_INVALID",
            )
            raise X02StageCallError(
                "%s returned a non-JSON response" % stage,
                stage_run=failure_run,
                code="MODEL_RESPONSE_NOT_JSON",
            ) from exc
        payload_object = payload if isinstance(payload, dict) else {}
        usage = payload_object.get("usage", {})
        usage = usage if isinstance(usage, dict) else {}
        request_id = str(
            response_headers.get("x-request-id")
            or response_headers.get("X-Request-Id")
            or payload_object.get("id")
            or "openai-request-unknown"
        )
        try:
            output = json.loads(_responses_output_text(payload_object))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            failure_run = _failed_stage_run(
                stage=stage,
                provider=self.adapter.provider,
                model=self.adapter.model,
                request_id=request_id,
                latency_seconds=latency,
                evidence=selected,
                frame_count=len(evidence),
                pricing_currency="USD",
                input_rate=self.adapter.input_rate_per_million,
                output_rate=self.adapter.output_rate_per_million,
                native_per_usd=1.0,
                pricing_basis="openai-public-rate-config-2026-08-18",
                input_tokens=int(usage.get("input_tokens", 0)),
                output_tokens=int(usage.get("output_tokens", 0)),
                call_status="RESPONSE_INVALID",
            )
            raise X02StageCallError(
                "%s returned no valid structured output" % stage,
                stage_run=failure_run,
                code="MODEL_STRUCTURED_OUTPUT_INVALID",
            ) from exc
        return StageRun(
            stage=stage,
            output=output,
            provider=self.adapter.provider,
            model=self.adapter.model,
            request_id=request_id,
            input_tokens=int(usage.get("input_tokens", 0)),
            output_tokens=int(usage.get("output_tokens", 0)),
            latency_seconds=latency,
            model_frame_count=len(evidence),
            model_calls=1,
            pricing_currency="USD",
            input_rate_per_million=self.adapter.input_rate_per_million,
            output_rate_per_million=self.adapter.output_rate_per_million,
            native_currency_per_usd=1.0,
            pricing_basis="openai-public-rate-config-2026-08-18",
            selected_evidence=tuple(selected),
        )


class FixtureStageGateway(StageModelGateway):
    """Deterministic integration fixture; never a semantic-quality substitute."""

    provider = "fixture"
    model = "fixture-staged-contract-only-v1"
    credential_environment = "NOT_APPLICABLE"

    @property
    def ready(self) -> bool:
        return True

    def call(
        self,
        stage: str,
        prompt: str,
        schema: Mapping[str, object],
        evidence: Sequence[Tuple[Mapping[str, object], Mapping[str, object], Path]] = (),
        context: Optional[Mapping[str, object]] = None,
    ) -> StageRun:
        context = context or {}
        if stage.startswith("S04_PERCEPTION"):
            output = _fixture_perception(context)
        elif stage == "S05_S07_STRUCTURE_PROPOSAL":
            output = (
                {"storyline_proposals": [], "aha_proposals": []}
                if context.get("storyline_contract_version") == X02_STORYLINE_CONTRACT_VERSION
                else {"chapter_proposals": [], "aha_proposals": []}
            )
        elif stage.startswith("S11_WRITER"):
            output = _fixture_writer(context)
        else:
            output = {}
        return StageRun(
            stage=stage,
            output=output,
            provider=self.provider,
            model=self.model,
            request_id="fixture-%s" % stage.lower(),
            input_tokens=0,
            output_tokens=0,
            latency_seconds=0.0,
            model_frame_count=len(evidence),
            model_calls=0,
            pricing_currency="USD",
            input_rate_per_million=0.0,
            output_rate_per_million=0.0,
            native_currency_per_usd=1.0,
            pricing_basis="fixture-zero-cost",
            selected_evidence=tuple(
                _evidence_ledger_entry(order, asset, frame)
                for order, (asset, frame, _) in enumerate(evidence)
            ),
        )


def stage_gateway_for_adapter(adapter: EditorialModelAdapter) -> StageModelGateway:
    if isinstance(adapter, QwenChatCompletionsAdapter):
        return QwenStageGateway(adapter)
    if isinstance(adapter, OpenAIResponsesAdapter):
        return OpenAIStageGateway(adapter)
    if isinstance(adapter, FixtureEditorialAdapter):
        return FixtureStageGateway()
    if isinstance(adapter, StageModelGateway):
        return adapter
    raise ValueError("X02 does not support adapter type %s" % type(adapter).__name__)


FACT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["text", "evidence_frame_ids", "support_grade"],
    "properties": {
        "text": {"type": "string"},
        "evidence_frame_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "support_grade": {"type": "string", "enum": sorted(SUPPORT_GRADES)},
    },
}

PERCEPTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["observations"],
    "properties": {
        "observations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "asset_id", "status", "facts", "setting_code", "activity_code",
                    "episode_code", "subject_codes", "motifs", "event_kind",
                    "event_salience", "quality_score", "limitations",
                ],
                "properties": {
                    "asset_id": {"type": "string"},
                    "status": {"type": "string", "enum": sorted(OBSERVATION_STATUSES)},
                    "facts": {"type": "array", "items": FACT_SCHEMA},
                    "setting_code": {"type": "string", "enum": sorted(SETTING_CODES)},
                    "activity_code": {"type": "string", "enum": sorted(ACTIVITY_CODES)},
                    "episode_code": {"type": "string", "enum": sorted(EPISODE_CODES)},
                    "subject_codes": {
                        "type": "array", "items": {"type": "string", "enum": sorted(SUBJECT_CODES)},
                    },
                    "motifs": {"type": "array", "items": {"type": "string"}, "maxItems": 6},
                    "event_kind": {"type": "string", "enum": sorted(EVENT_KINDS)},
                    "event_salience": {"type": "string", "enum": sorted(EVENT_SALIENCE)},
                    "quality_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "limitations": {"type": "array", "items": {"type": "string"}, "maxItems": 6},
                },
            },
        }
    },
}

PERCEPTION_SCHEMA_GENERIC_ANIMAL = copy.deepcopy(PERCEPTION_SCHEMA)
PERCEPTION_SCHEMA_GENERIC_ANIMAL["properties"]["observations"]["items"]["properties"]["subject_codes"]["items"]["enum"] = sorted(GENERIC_SUBJECT_CODES)

STRUCTURE_SCHEMA_V03 = {
    "type": "object",
    "additionalProperties": False,
    "required": ["chapter_proposals", "aha_proposals"],
    "properties": {
        "chapter_proposals": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "observation_ids", "episode_code", "fact_ids", "reason"],
                "properties": {
                    "key": {"type": "string"},
                    "observation_ids": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                    "episode_code": {"type": "string", "enum": sorted(EPISODE_CODES)},
                    "fact_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "reason": {"type": "string"},
                },
            },
        },
        "aha_proposals": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "observation_id", "event_fact_ids", "narrative_duty"],
                "properties": {
                    "key": {"type": "string"},
                    "observation_id": {"type": "string"},
                    "event_fact_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "narrative_duty": {"type": "string"},
                },
            },
        },
    },
}

STORYLINE_BEAT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["observation_id", "beat_role", "fact_ids", "contribution"],
    "properties": {
        "observation_id": {"type": "string"},
        "beat_role": {"type": "string", "enum": sorted(STORYLINE_BEAT_ROLES)},
        "fact_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "contribution": {"type": "string"},
    },
}

STRUCTURE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["storyline_proposals", "aha_proposals"],
    "properties": {
        "storyline_proposals": {
            "type": "array",
            "maxItems": int(X02_STORYLINE_CONTRACT["max_model_storyline_proposals"]),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "key", "storyline_basis", "thesis",
                    "observation_ids", "fact_ids", "beat_map", "reason",
                ],
                "properties": {
                    "key": {"type": "string"},
                    "storyline_basis": {"type": "string", "enum": sorted(STORYLINE_BASES)},
                    "focus_code": {"type": "string", "description": "Optional legacy annotation; not a grouping category or ranking signal."},
                    "thesis": {"type": "string"},
                    "observation_ids": {
                        "type": "array", "items": {"type": "string"}, "minItems": 2,
                        "maxItems": int(X02_STORYLINE_CONTRACT["max_content_members"]),
                    },
                    "fact_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "beat_map": {"type": "array", "items": STORYLINE_BEAT_SCHEMA, "minItems": 2},
                    "reason": {"type": "string"},
                },
            },
        },
        "aha_proposals": STRUCTURE_SCHEMA_V03["properties"]["aha_proposals"],
    },
}

WRITER_ITEM_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["candidate_id", "title", "text", "claim_ids"],
    "properties": {
        "candidate_id": {"type": "string"},
        "title": {
            "type": "string",
            "description": (
                "Chapter: 2-10 visible Chinese characters, or 11-12 only when necessary. "
                "Aha: short internal label, not a second user-visible story."
            ),
        },
        "text": {
            "type": "string",
            "description": (
                "Chapter: one concise sentence by default, at most two when the second adds "
                "materially distinct approved information. Aha: exactly one user-visible "
                "sentence of at most 20 visible Chinese characters."
            ),
        },
        "claim_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    },
}

WRITER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["chapters", "ahas"],
    "properties": {
        "chapters": {"type": "array", "items": WRITER_ITEM_SCHEMA},
        "ahas": {"type": "array", "items": WRITER_ITEM_SCHEMA},
    },
}


def x02_runtime_policies() -> Dict[str, str]:
    """Shared health/result receipt for the loaded current preview implementation."""
    return {
        "chapter_coherence": chapter_coherence.POLICY_VERSION,
        "chapter_selection_response": chapter_display.RESPONSE_ACCEPTANCE_VERSION,
        "aha_pair_conflict": X02_AHA_PAIR_CONFLICT_POLICY_VERSION,
        "content_brief": content_handoff.POLICY_VERSION,
        "editorial_allocation": editorial_allocation.POLICY_VERSION,
        "writer_exit": writer_exit.POLICY_VERSION,
        "subject_granularity": SUBJECT_GRANULARITY_VERSION,
        "structure_acceptance": X02_STRUCTURE_ACCEPTANCE_POLICY_VERSION,
        "structure_wire": structure_wire.POLICY_VERSION,
    }


def run_x02(manifest_path: Path, gateway: StageModelGateway) -> Dict[str, object]:
    return _run_x02_with_policy(manifest_path, gateway, "V04_1")


def _retain_failed_stage_run(
    gateway: StageModelGateway,
    stage_runs: List[StageRun],
    stage_run: StageRun,
) -> None:
    stage_runs.append(stage_run)
    if isinstance(gateway, _RecordingStageGateway):
        gateway.runs.append(stage_run)


def run_x02_v041(manifest_path: Path, gateway: StageModelGateway, *,
                 editorial_order_policy: Optional[str] = None,
                 recording_editor_policy: Optional[str] = None) -> Dict[str, object]:
    """Active V04.1 stop-loss research policy."""
    return _run_x02_with_policy(manifest_path, gateway, "V04_1",
                                editorial_order_policy=editorial_order_policy,
                                recording_editor_policy=recording_editor_policy)


def run_x02_v03(manifest_path: Path, gateway: StageModelGateway) -> Dict[str, object]:
    """Historical V03 endpoint behavior; never aliases the V04 Storyline policy."""
    return _run_x02_with_policy(manifest_path, gateway, "V03")


def _run_x02_with_policy(
    manifest_path: Path,
    gateway: StageModelGateway,
    policy_version: str,
    *,
    editorial_order_policy: Optional[str] = None,
    recording_editor_policy: Optional[str] = None,
) -> Dict[str, object]:
    recorder = _RecordingStageGateway(gateway)
    try:
        return _run_x02_impl(manifest_path, recorder, policy_version,
                             editorial_order_policy=editorial_order_policy,
                             recording_editor_policy=recording_editor_policy)
    except X02ModelNotReady:
        raise
    except X02StageCallError as exc:
        raise X02ExecutionError(
            str(exc),
            stage=exc.stage_run.stage,
            code=exc.code,
            stage_runs=[*recorder.runs, exc.stage_run],
        ) from exc
    except X02ContractError as exc:
        if not recorder.runs:
            raise
        raise X02ExecutionError(
            str(exc),
            stage="DETERMINISTIC_CONTRACT_GATE",
            code="POST_MODEL_CONTRACT_VIOLATION",
            stage_runs=recorder.runs,
        ) from exc
    except X02Error as exc:
        raise X02ExecutionError(
            str(exc),
            stage="MODEL_GATEWAY",
            code="MODEL_REQUEST_FAILED",
            stage_runs=recorder.runs,
        ) from exc


def _run_x02_impl(
    manifest_path: Path,
    gateway: StageModelGateway,
    policy_version: str,
    *,
    editorial_order_policy: Optional[str] = None,
    recording_editor_policy: Optional[str] = None,
) -> Dict[str, object]:
    if recording_editor_policy not in (
        None, recording_editor.POLICY_VERSION, grounded_recording_editor.POLICY_VERSION,
        aha_set_editor.POLICY_VERSION, experience_editor.POLICY_VERSION,
    ):
        raise X02ContractError("unknown research recording editor policy")
    if recording_editor_policy is not None and (policy_version != "V04_1" or editorial_order_policy is not None):
        raise X02ContractError("recording editor requires V04.1 and cannot mix with editorial order")
    if editorial_order_policy not in (None, editorial_order.POLICY_VERSION):
        raise X02ContractError("unknown research editorial order policy")
    if editorial_order_policy is not None and policy_version != "V04_1":
        raise X02ContractError("editorial order requires the V04.1 research chain")
    if policy_version not in ("V03", "V04_1"):
        raise X02ContractError("unknown X02 policy version")
    storyline_policy = policy_version == "V04_1"
    stop_loss_v041 = policy_version == "V04_1"
    active_recording_editor = (
        experience_editor
        if recording_editor_policy == experience_editor.POLICY_VERSION
        else
        aha_set_editor
        if recording_editor_policy == aha_set_editor.POLICY_VERSION
        else grounded_recording_editor
        if recording_editor_policy == grounded_recording_editor.POLICY_VERSION
        else recording_editor
    )
    grounded_editor_v2 = recording_editor_policy in (
        grounded_recording_editor.POLICY_VERSION, aha_set_editor.POLICY_VERSION,
        experience_editor.POLICY_VERSION,
    )
    experience_editor_active = recording_editor_policy == experience_editor.POLICY_VERSION
    result_schema_version = X02_SCHEMA_VERSION if storyline_policy else X02_V03_SCHEMA_VERSION
    pipeline_version = X02_PIPELINE_VERSION if storyline_policy else X02_V03_PIPELINE_VERSION
    run_started = time.monotonic()
    bundle = load_app_library_bundle(manifest_path)
    bundle_complete = time.monotonic()
    input_bundle_version = str(bundle.manifest["bundle_version"])
    if policy_version == "V03" and input_bundle_version in (
        APP_LIBRARY_BUNDLE_VERSION_V03, APP_LIBRARY_BUNDLE_VERSION_V04,
    ):
        raise X02ContractError(
            "historical X02 V03 accepts App Library Bundle V01/V02 only"
        )
    uses_duration_windows = input_bundle_version in (
        APP_LIBRARY_BUNDLE_VERSION_V02,
        APP_LIBRARY_BUNDLE_VERSION_V03,
        APP_LIBRARY_BUNDLE_VERSION_V04,
    )
    if not gateway.ready:
        raise X02ModelNotReady("X02 staged model gateway is not ready")

    namespace = _session_namespace(bundle)
    assets = list(bundle.manifest["assets"])
    asset_order = {str(asset["asset_id"]): index for index, asset in enumerate(assets)}
    app_asset_ids = {
        str(asset["asset_id"]): _app_asset_uuid(str(asset["asset_id"])) for asset in assets
    }
    stage_runs: List[StageRun] = []
    model_call_attempt_count = 0
    model_call_circuit_breaker_tripped = False

    def call_model(
        stage: str,
        prompt: str,
        schema: Mapping[str, object],
        *,
        evidence: Sequence[Tuple[Mapping[str, object], Mapping[str, object], Path]] = (),
        context: Optional[Mapping[str, object]] = None,
    ) -> StageRun:
        nonlocal model_call_attempt_count, model_call_circuit_breaker_tripped
        call_context = dict(context or {})
        if stop_loss_v041:
            call_context["_x02_policy_version"] = "V04_1"
            if model_call_attempt_count >= V041_RUN_MAX_MODEL_CALL_ATTEMPTS:
                model_call_circuit_breaker_tripped = True
                raise X02CallAttemptLimitReached(
                    "V04.1 model-call attempt circuit breaker is open"
                )
        model_call_attempt_count += 1
        return gateway.call(
            stage,
            prompt,
            schema,
            evidence=evidence,
            context=call_context,
        )
    stage_statuses: List[Dict[str, object]] = [
        _stage_status("S00_S02_INTAKE", "COMPLETED", [
            "APP_LIBRARY_BUNDLE_GATE_PASSED",
            "SOURCE_ORDER_PRESERVED",
            "ORIGINAL_MEDIA_NOT_UPLOADED",
        ])
    ]

    perception_started = time.monotonic()
    perception_validation_seconds = 0.0
    observations: List[Dict[str, object]] = []
    observation_ledger: List[Dict[str, object]] = []
    evidence_ledger: List[Dict[str, object]] = []
    for order, (asset, frame, _) in enumerate(_perception_evidence(bundle, assets)):
        evidence_ledger.append(_evidence_ledger_entry(order, asset, frame))
    perception_batch_attempts: List[Dict[str, object]] = []
    unresolved_asset_ids: List[str] = []
    perception_call_sequence = 0

    def process_perception_batch(
        batch_assets: Sequence[Mapping[str, object]],
        *,
        parent_attempt_id: Optional[str] = None,
        retry_budget: int = PERCEPTION_SINGLE_ASSET_RETRY_LIMIT,
        attempt_kind: str = "ROOT",
    ) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
        nonlocal perception_validation_seconds, perception_call_sequence
        perception_call_sequence += 1
        attempt_id = "perception_attempt_%03d" % perception_call_sequence
        evidence = _perception_evidence(bundle, batch_assets)
        evidence_bytes = sum(path.stat().st_size for _, _, path in evidence)
        stage_name = "S04_PERCEPTION_BATCH_%03d" % perception_call_sequence
        prompt = _perception_prompt(
            batch_assets, evidence, import_sequence_only=stop_loss_v041,
            generic_animal_subjects=stop_loss_v041,
            grounded_claims=grounded_editor_v2,
            representative_fact_frame=experience_editor_active,
        )
        context = {
            "assets": list(batch_assets),
            "evidence": evidence,
            "batch_policy": "V04_1_BOUNDED_ASSETS_FRAMES_BYTES",
            "fact_representative_frame_required": experience_editor_active,
        }
        if (
            stop_loss_v041
            and len(batch_assets) == 1
            and evidence_bytes > PERCEPTION_BATCH_MAX_EVIDENCE_BYTES
        ):
            asset_ids = [str(asset["asset_id"]) for asset in batch_assets]
            perception_batch_attempts.append({
                "attempt_id": attempt_id,
                "parent_attempt_id": parent_attempt_id,
                "asset_ids": asset_ids,
                "asset_count": 1,
                "frame_count": len(evidence),
                "evidence_bytes": evidence_bytes,
                "provider_call_attempted": False,
                "attempt_kind": attempt_kind,
                "status": "REJECTED_PREFLIGHT",
                "reason_code": "EVIDENCE_BUDGET_EXCEEDED",
                "recovery_action": "TERMINAL_PREFLIGHT",
                "terminal_unresolved_asset_ids": asset_ids,
            })
            failed_observations, failed_ledger = _failed_batch_observations(
                namespace,
                batch_assets,
                app_asset_ids,
                "EVIDENCE_BUDGET_EXCEEDED",
                "normalized evidence for one asset exceeds the 4 MiB provider budget",
            )
            unresolved_asset_ids.extend(asset_ids)
            return failed_observations, failed_ledger
        error_code = ""
        error_detail = ""
        try:
            stage_run = call_model(
                stage_name, prompt,
                (
                    experience_editor.perception_schema(PERCEPTION_SCHEMA_GENERIC_ANIMAL)
                    if experience_editor_active
                    else PERCEPTION_SCHEMA_GENERIC_ANIMAL
                    if stop_loss_v041 else PERCEPTION_SCHEMA
                ),
                evidence=evidence, context=context,
            )
            stage_runs.append(stage_run)
            batch_validation_started = time.monotonic()
            batch_observations, batch_ledger = _validate_perception_batch(
                namespace,
                batch_assets,
                stage_run,
                app_asset_ids,
                unicode_motifs=stop_loss_v041,
                retain_extended_fact_text=stop_loss_v041,
                generic_animal_subjects=stop_loss_v041,
                representative_fact_frame=experience_editor_active,
            )
            perception_validation_seconds += time.monotonic() - batch_validation_started
        except X02ModelNotReady:
            raise
        except X02CallAttemptLimitReached as exc:
            if not stop_loss_v041:
                raise
            error_code, error_detail = "MODEL_CALL_CIRCUIT_BREAKER_OPEN", str(exc)
        except X02StageCallError as exc:
            if not stop_loss_v041:
                raise
            _retain_failed_stage_run(gateway, stage_runs, exc.stage_run)
            error_code, error_detail = exc.code, str(exc)
        except X02Error as exc:
            if not stop_loss_v041:
                raise
            error_code, error_detail = "PERCEPTION_CONTRACT_ENVELOPE_INVALID", str(exc)
        except Exception as exc:
            error_code, error_detail = "PERCEPTION_OUTPUT_INVALID", str(exc)

        if error_code:
            failed_attempt_entry = {
                "attempt_id": attempt_id,
                "parent_attempt_id": parent_attempt_id,
                "asset_ids": [str(asset["asset_id"]) for asset in batch_assets],
                "asset_count": len(batch_assets),
                "frame_count": len(evidence),
                "evidence_bytes": evidence_bytes,
                "provider_call_attempted": error_code != "MODEL_CALL_CIRCUIT_BREAKER_OPEN",
                "attempt_kind": attempt_kind,
                "status": "FAILED",
                "reason_code": error_code,
                "recovery_action": "TERMINAL_UNRESOLVED",
                "terminal_unresolved_asset_ids": [
                    str(asset["asset_id"]) for asset in batch_assets
                ],
            }
            perception_batch_attempts.append(failed_attempt_entry)
            split_allowed = (
                error_code == "MODEL_HTTP_413"
                or error_code.startswith("PERCEPTION_ASSET_LOCAL_")
            )
            if stop_loss_v041 and split_allowed and len(batch_assets) > 1:
                failed_attempt_entry["recovery_action"] = "BISECT"
                failed_attempt_entry["terminal_unresolved_asset_ids"] = []
                midpoint = len(batch_assets) // 2
                left_observations, left_ledger = process_perception_batch(
                    batch_assets[:midpoint],
                    parent_attempt_id=attempt_id,
                    retry_budget=0,
                    attempt_kind="SPLIT_CHILD",
                )
                right_observations, right_ledger = process_perception_batch(
                    batch_assets[midpoint:],
                    parent_attempt_id=attempt_id,
                    retry_budget=0,
                    attempt_kind="SPLIT_CHILD",
                )
                return left_observations + right_observations, left_ledger + right_ledger
            transient_original_batch_retry = (
                error_code == "MODEL_TRANSPORT_TIMEOUT"
                or bool(re.fullmatch(r"MODEL_HTTP_5\d\d", error_code))
            )
            if (
                stop_loss_v041
                and transient_original_batch_retry
                and parent_attempt_id is None
                and retry_budget > 0
            ):
                failed_attempt_entry["recovery_action"] = "ORIGINAL_BATCH_RETRY"
                failed_attempt_entry["terminal_unresolved_asset_ids"] = []
                return process_perception_batch(
                    batch_assets,
                    parent_attempt_id=attempt_id,
                    retry_budget=retry_budget - 1,
                    attempt_kind="ORIGINAL_BATCH_RETRY",
                )
            if (
                stop_loss_v041
                and error_code.startswith("PERCEPTION_ASSET_LOCAL_")
                and len(batch_assets) == 1
                and parent_attempt_id is None
                and retry_budget > 0
            ):
                failed_attempt_entry["recovery_action"] = "SINGLETON_RETRY"
                failed_attempt_entry["terminal_unresolved_asset_ids"] = []
                return process_perception_batch(
                    batch_assets,
                    parent_attempt_id=attempt_id,
                    retry_budget=retry_budget - 1,
                    attempt_kind="SINGLETON_RETRY",
                )
            failed_observations, failed_ledger = _failed_batch_observations(
                namespace,
                batch_assets,
                app_asset_ids,
                "PERCEPTION_CALL_UNRESOLVED",
                error_detail,
            )
            unresolved_asset_ids.extend(str(asset["asset_id"]) for asset in batch_assets)
            return failed_observations, failed_ledger

        item_failure_ids = {
            str(item["source_asset_id"])
            for item in batch_observations if item["status"] == "FAILED"
        }
        validated_attempt_entry = {
            "attempt_id": attempt_id,
            "parent_attempt_id": parent_attempt_id,
            "asset_ids": [str(asset["asset_id"]) for asset in batch_assets],
            "asset_count": len(batch_assets),
            "frame_count": len(evidence),
            "evidence_bytes": evidence_bytes,
            "provider_call_attempted": True,
            "attempt_kind": attempt_kind,
            "status": "VALIDATED_WITH_ITEM_FAILURES" if item_failure_ids else "VALIDATED",
            "reason_code": (
                "ITEM_LEVEL_VALIDATION_FAILURE_ISOLATED"
                if item_failure_ids else "PERCEPTION_BATCH_VALIDATED"
            ),
            "recovery_action": "ITEM_LEVEL_RETRY" if item_failure_ids else "NONE",
            "terminal_unresolved_asset_ids": [],
        }
        perception_batch_attempts.append(validated_attempt_entry)
        if stop_loss_v041 and item_failure_ids and retry_budget > 0:
            observation_by_asset = {
                str(item["source_asset_id"]): item for item in batch_observations
            }
            ledger_by_asset = {
                str(item.get("source_asset_id")): item
                for item in batch_ledger if item.get("source_asset_id") in observation_by_asset
            }
            for asset in batch_assets:
                asset_id = str(asset["asset_id"])
                if asset_id not in item_failure_ids:
                    continue
                retried_observations, retried_ledger = process_perception_batch(
                    [asset],
                    parent_attempt_id=attempt_id,
                    retry_budget=retry_budget - 1,
                    attempt_kind="ITEM_RETRY",
                )
                observation_by_asset[asset_id] = retried_observations[0]
                if retried_ledger:
                    retried_ledger[0]["prior_failed_attempt"] = ledger_by_asset.get(asset_id)
                    ledger_by_asset[asset_id] = retried_ledger[0]
            batch_observations = [
                observation_by_asset[str(asset["asset_id"])] for asset in batch_assets
            ]
            batch_ledger = [
                ledger_by_asset[str(asset["asset_id"])] for asset in batch_assets
            ]
        for item in batch_observations:
            if item["status"] == "FAILED":
                unresolved_asset_ids.append(str(item["source_asset_id"]))
        if item_failure_ids and not any(
            item.get("parent_attempt_id") == attempt_id
            for item in perception_batch_attempts
        ):
            validated_attempt_entry["recovery_action"] = "TERMINAL_ITEM_FAILURE"
            validated_attempt_entry["terminal_unresolved_asset_ids"] = [
                str(item["source_asset_id"])
                for item in batch_observations if item["status"] == "FAILED"
            ]
        return batch_observations, batch_ledger

    planned_batches = (
        _planned_perception_batches(bundle, assets)
        if stop_loss_v041 else _batches(assets, PERCEPTION_V03_BATCH_SIZE)
    )
    for batch_assets in planned_batches:
        batch_observations, batch_ledger = process_perception_batch(batch_assets)
        observations.extend(batch_observations)
        observation_ledger.extend(batch_ledger)
    unresolved_asset_ids = _unique(unresolved_asset_ids)
    observations.sort(key=lambda item: asset_order[item["source_asset_id"]])
    perception_complete = time.monotonic()
    observed_count = sum(
        1 for item in observations if item["status"] in ("OBSERVED", "PARTIAL")
    )
    degraded_observation_count = sum(1 for item in observations if item["degraded_fields"])
    stage_statuses.append(_stage_status(
        "S04_OBSERVATION_LITE",
        (
            "COMPLETED_WITH_UNRESOLVED_ASSETS"
            if unresolved_asset_ids else "COMPLETED_WITH_FIELD_DEGRADATION"
            if degraded_observation_count else "COMPLETED"
            if observed_count else "COMPLETED_WITH_NO_ACCEPTED_OBSERVATIONS"
        ),
        (
            [
                "ONE_TERMINAL_STATUS_PER_ASSET",
                "PER_ASSET_FAILURE_ISOLATION",
                "ONLY_EXPLICIT_ASSET_LOCAL_FAILURE_OR_HTTP_413_MAY_SPLIT",
                "TIMEOUT_OR_HTTP_5XX_MAY_RETRY_ORIGINAL_BATCH_ONCE_WITHOUT_SPLIT",
                "BOUNDED_SINGLE_ASSET_RETRY",
                "V04_1_RUN_MODEL_CALL_CIRCUIT_BREAKER",
                "VALID_GROUNDED_FACTS_SURVIVE_NONCRITICAL_FIELD_ERRORS",
                X02_FACT_RETENTION_POLICY_VERSION,
            ]
            if stop_loss_v041 else [
                "ONE_TERMINAL_STATUS_PER_ASSET",
                "VALID_GROUNDED_FACTS_SURVIVE_NONCRITICAL_FIELD_ERRORS",
            ]
        ),
    ))

    structure_started = time.monotonic()
    roles = _assign_roles(
        observations,
        reject_degraded_quality=stop_loss_v041,
    )
    edges = _build_boundary_ledger(observations, roles)
    moments = _build_moments(namespace, observations, roles, edges, asset_order)
    structured_observations = (
        active_recording_editor.structure_observations(observations, roles)
        if grounded_editor_v2
        else _structure_observations(observations, roles)
    )
    structure_context = {
        "observations": structured_observations,
        "moments": (
            active_recording_editor.structure_moments(moments)
            if grounded_editor_v2
            else moments
        ),
    }
    if storyline_policy:
        structure_context["storyline_contract_version"] = X02_STORYLINE_CONTRACT_VERSION
        structure_context["storyline_contract_sha256"] = X02_STORYLINE_CONTRACT_SHA256
        # Bundle V01/V02/V03 do not carry verified capture-time provenance.
        # A truthy timestamp is metadata, not chronological proof.
        structure_context["sequence_basis"] = "IMPORT_SEQUENCE_ONLY"
        structure_context["sequence_semantics"] = (
            "Input order is only import sequence; do not infer clock time, elapsed gaps, "
            "or real adjacency. Current bundle versions provide no verified-time provenance."
        )
        if recording_editor_policy is not None:
            eligible_ahas = active_recording_editor.consideration_scope(observations, roles)
            structure_context[active_recording_editor.POLICY_FIELD] = recording_editor_policy
            structure_context["recording_input_context"] = active_recording_editor.input_context()
        else:
            # Old paths retain their exact event-based consideration scope.
            eligible_ahas, _ = _build_aha_candidates(
                namespace, observations, roles, moments, {"aha_proposals": []},
                asset_order, value_first=stop_loss_v041,
            )
        structure_context[editorial_allocation.POLICY_FIELD] = editorial_allocation.POLICY_VERSION
        structure_context[structure_wire.POLICY_FIELD] = structure_wire.POLICY_VERSION
        structure_context[chapter_coherence.POLICY_FIELD] = chapter_coherence.POLICY_VERSION
        structure_context["aha_relation_scope"] = [{
            "observation_id": item["observation_id"],
            "event_fact_ids": list(item["event_fact_ids"]),
        } for item in eligible_ahas]
    if editorial_order_policy is not None:
        structure_context[editorial_order.POLICY_FIELD] = editorial_order_policy
    structure_prompt = (
        _storyline_structure_prompt(structure_context)
        if storyline_policy else _structure_prompt(structure_context)
    )
    structure_before_model = time.monotonic()
    structure_schema = (
        structure_wire.response_schema(editorial_allocation.structure_schema(STRUCTURE_SCHEMA))
        if storyline_policy else STRUCTURE_SCHEMA_V03
    )
    if editorial_order_policy is not None:
        structure_schema = editorial_order.response_schema(structure_schema)
    if recording_editor_policy is not None:
        structure_schema = active_recording_editor.response_schema(structure_schema)
    structure_model_skipped = bool(
        stop_loss_v041
        and model_call_attempt_count >= V041_RUN_MAX_MODEL_CALL_ATTEMPTS
    )
    if structure_model_skipped:
        model_call_circuit_breaker_tripped = True
        structure_output: Mapping[str, object] = {
            "storyline_proposals": [],
            "aha_proposals": [],
        }
    else:
        structure_run = call_model(
            "S05_S07_STRUCTURE_PROPOSAL",
            structure_prompt,
            structure_schema,
            context=structure_context,
        )
        stage_runs.append(structure_run)
        structure_output = structure_run.output
    structure_after_model = time.monotonic()
    structure_wire_audit = None
    if storyline_policy:
        # Keep structure_run.output as the untouched wire response. Only the
        # internal candidate handoff receives the derived redundant fields.
        wire_output_sha256 = sha256_bytes(canonical_bytes(structure_output))
        structure_output, structure_wire_audit = structure_wire.normalize_output(structure_output)
        structure_wire_audit.update({
            "wire_output_sha256": wire_output_sha256,
            "internal_output_sha256": sha256_bytes(canonical_bytes(structure_output)),
        })
    chapter_candidates, chapter_ledger = (
        _build_storyline_candidates(
            namespace,
            observations,
            roles,
            moments,
            structure_output,
            asset_order,
        )
        if storyline_policy
        else _build_chapter_candidates(
            namespace,
            observations,
            roles,
            moments,
            structure_output,
            asset_order,
        )
    )
    aha_candidates, aha_ledger = (
        experience_editor.build_fact_candidates(
            namespace, observations, roles, moments, asset_order,
        )
        if experience_editor_active else
        _build_aha_candidates(
            namespace,
            observations,
            roles,
            moments,
            structure_output,
            asset_order,
            value_first=stop_loss_v041,
            evidence_nominations_only=recording_editor_policy is not None,
        )
    )
    allocation_plan = (
        editorial_allocation.compile_relations(
            structure_output, chapter_candidates, chapter_ledger, aha_candidates,
        ) if storyline_policy and recording_editor_policy not in (
            aha_set_editor.POLICY_VERSION, experience_editor.POLICY_VERSION,
        ) else None
    )
    order_plan = (
        editorial_order.compile_order(structure_output, chapter_ledger, aha_candidates,
                                       structure_context["aha_relation_scope"])
        if editorial_order_policy is not None else None
    )
    aha_discovery_plan = None
    recording_plan = (
        (
            experience_editor.compile_discovery(
                structure_output, chapter_ledger,
                structure_context["aha_relation_scope"],
            )
            if experience_editor_active
            else aha_set_editor.compile_discovery(
                structure_output, chapter_ledger, chapter_candidates, aha_candidates,
                structure_context["aha_relation_scope"], observations,
            )
            if recording_editor_policy == aha_set_editor.POLICY_VERSION
            else
            grounded_recording_editor.compile_plan(
                structure_output, chapter_ledger, chapter_candidates, aha_candidates,
                structure_context["aha_relation_scope"], observations,
            )
            if recording_editor_policy == grounded_recording_editor.POLICY_VERSION
            else recording_editor.compile_plan(
                structure_output, chapter_ledger, aha_candidates,
                structure_context["aha_relation_scope"],
            )
        )
        if recording_editor_policy is not None else None
    )
    if recording_editor_policy in (
        aha_set_editor.POLICY_VERSION, experience_editor.POLICY_VERSION,
    ):
        aha_discovery_plan = recording_plan
    if recording_editor_policy == grounded_recording_editor.POLICY_VERSION:
        allocation_plan = grounded_recording_editor.allocation_plan(recording_plan)
    structure_complete = time.monotonic()
    structure_deterministic_seconds = (
        (structure_before_model - structure_started)
        + (structure_complete - structure_after_model)
    )
    stage_statuses.extend([
        _stage_status("S03_S05_CONTINUITY_BOUNDARY", "COMPLETED", [
            "ADJACENT_DUAL_EVIDENCE_LEDGER", "JOIN_SPLIT_DEFER_DECISIONS",
        ]),
        _stage_status("S06_ROLE_ASSIGNMENT", "COMPLETED", [
            "EXACTLY_ONE_ROLE_PER_OBSERVATION",
        ]),
        _stage_status("S07_CANDIDATE_GENERATION", "COMPLETED", (
            [
                "MODEL_OWNED_CONTENT_GROUPING",
                "STRUCTURE_AND_REFERENCE_CHECKS_NOT_SEMANTIC_VERIFICATION",
                "TAGS_AND_IMPORT_ORDER_DO_NOT_OVERRIDE_MEMBERSHIP",
                "NO_DETERMINISTIC_TAG_GROUP_FALLBACK",
                ("S07_CHAPTER_ONLY_S09_RECEIVES_FULL_SUPPORTED_FACT_PALETTE"
                 if experience_editor_active else
                 "ALL_USABLE_FACTS_CONSIDERED_MODEL_NOMINATIONS_ONLY"
                 if recording_plan is not None else "EVENT_AND_DISCOVERY_AHA_PATHS_SEARCHED"),
                *(
                    ["MODEL_STRUCTURE_SKIPPED_CALL_CIRCUIT_BREAKER"]
                    if structure_model_skipped else []
                ),
            ]
            if storyline_policy else [
                "CANDIDATE_MEMBERSHIP_NOT_CAPPED_AT_FIVE",
                "MODEL_PROPOSALS_REQUIRE_DETERMINISTIC_COHERENCE_VALIDATION",
                "EVENT_AND_DISCOVERY_AHA_PATHS_SEARCHED",
            ]
        )),
    ])

    selection_started = time.monotonic()
    aha_editor_model_seconds = 0.0
    aha_editor_audit = None
    if experience_editor_active:
        preview_chapters = experience_editor.preview_selected_chapters(
            aha_discovery_plan, chapter_candidates, asset_order,
            minimum=chapter_display.MIN_MEDIA, max_chapters=MAX_CHAPTERS,
        )
        editor_context, editor_maps = experience_editor.editor_input(
            aha_discovery_plan, preview_chapters, chapter_candidates, aha_candidates,
            observations,
        )
        aha_editor_audit = {
            "stage": experience_editor.EDITOR_STAGE,
            "input_sha256": sha256_bytes(canonical_bytes(editor_context)),
            "serialized_input_bytes": len(canonical_bytes(editor_context)),
            "fact_palette_count": len(editor_context["fact_palette"]),
            "request_local_reference_map": copy.deepcopy(editor_maps),
            "text_only": True,
            "full_supported_fact_palette": True,
            "retry_or_automatic_fill": False,
        }
        if not editor_context["fact_palette"]:
            empty_editor_output = {
                "finalists": [], "selected_ahas": [],
                "chapter_aha_relations": [], "aha_aha_relations": [],
                "set_reason": "No supported fact with a valid representative frame was available.",
            }
            recording_plan = experience_editor.compile_editor(
                empty_editor_output, editor_context, editor_maps, aha_discovery_plan,
                preview_chapters,
            )
            aha_editor_audit["status"] = "SKIPPED_NO_USABLE_FACT_PALETTE"
        elif model_call_attempt_count >= V041_RUN_MAX_MODEL_CALL_ATTEMPTS:
            model_call_circuit_breaker_tripped = True
            recording_plan = experience_editor.unavailable_plan(
                aha_discovery_plan, "MODEL_CALL_CIRCUIT_BREAKER",
            )
            aha_editor_audit["status"] = "SKIPPED_CALL_CIRCUIT_BREAKER"
        else:
            editor_call_started = time.monotonic()
            try:
                editor_run = call_model(
                    experience_editor.EDITOR_STAGE,
                    experience_editor.editor_prompt(editor_context),
                    experience_editor.editor_response_schema(),
                    context=editor_context,
                )
                stage_runs.append(editor_run)
                recording_plan = experience_editor.compile_editor(
                    editor_run.output, editor_context, editor_maps, aha_discovery_plan,
                    preview_chapters,
                )
                aha_editor_audit.update(
                    status="COMPLETED",
                    output_sha256=sha256_bytes(canonical_bytes(editor_run.output)),
                )
            except X02StageCallError as exc:
                _retain_failed_stage_run(gateway, stage_runs, exc.stage_run)
                recording_plan = experience_editor.unavailable_plan(
                    aha_discovery_plan, exc.code,
                )
                aha_editor_audit.update(status="FAILED_AHA_LANE_CLOSED", error_code=exc.code)
            aha_editor_model_seconds = time.monotonic() - editor_call_started
        allocation_plan = experience_editor.allocation_plan(recording_plan)
        stage_statuses.append(_stage_status(
            experience_editor.EDITOR_STAGE,
            str(aha_editor_audit["status"]),
            [
                "ONE_TEXT_ONLY_EDITOR_CALL_MAXIMUM",
                "ALL_USABLE_SUPPORTED_FACTS_VISIBLE_IN_ONE_PASS",
                "ONE_AUTHORITATIVE_SELECTED_RELATION_MATRIX",
                "ZERO_TO_THREE_AHAS_ACTIVE_TARGET_TWO_TO_THREE_WHEN_SUPPORTED",
                "NO_RETRY_NO_AUTOMATIC_FILL",
                "CHAPTERS_SURVIVE_AHA_EDITOR_FAILURE",
            ],
        ))
    elif recording_editor_policy == aha_set_editor.POLICY_VERSION:
        preview_chapters = aha_set_editor.preview_selected_chapters(
            aha_discovery_plan, chapter_candidates, asset_order,
            minimum=chapter_display.MIN_MEDIA, max_chapters=MAX_CHAPTERS,
        )
        editor_context, editor_maps = aha_set_editor.editor_input(
            aha_discovery_plan, preview_chapters, chapter_candidates, aha_candidates,
            observations,
        )
        aha_editor_audit = {
            "stage": aha_set_editor.EDITOR_STAGE,
            "input_sha256": sha256_bytes(canonical_bytes(editor_context)),
            "request_local_reference_map": copy.deepcopy(editor_maps),
            "text_only": True,
            "retry_or_automatic_fill": False,
        }
        if not editor_context["aha_candidates"]:
            empty_editor_output = {
                "candidate_reviews": [], "selected_aha_ids": [],
                "chapter_aha_relations": [], "aha_aha_relations": [],
                "set_reason": "No validated atomic Aha candidates reached the set editor.",
            }
            recording_plan = aha_set_editor.compile_editor(
                empty_editor_output, editor_context, editor_maps, aha_discovery_plan,
                preview_chapters, chapter_candidates, aha_candidates,
            )
            aha_editor_audit["status"] = "SKIPPED_NO_VALIDATED_SHORTLIST"
        elif model_call_attempt_count >= V041_RUN_MAX_MODEL_CALL_ATTEMPTS:
            model_call_circuit_breaker_tripped = True
            recording_plan = aha_set_editor.unavailable_plan(
                aha_discovery_plan, "MODEL_CALL_CIRCUIT_BREAKER",
            )
            aha_editor_audit["status"] = "SKIPPED_CALL_CIRCUIT_BREAKER"
        else:
            editor_call_started = time.monotonic()
            try:
                editor_run = call_model(
                    aha_set_editor.EDITOR_STAGE,
                    aha_set_editor.editor_prompt(editor_context),
                    aha_set_editor.editor_response_schema(),
                    context=editor_context,
                )
                stage_runs.append(editor_run)
                recording_plan = aha_set_editor.compile_editor(
                    editor_run.output, editor_context, editor_maps, aha_discovery_plan,
                    preview_chapters, chapter_candidates, aha_candidates,
                )
                aha_editor_audit.update(
                    status="COMPLETED",
                    output_sha256=sha256_bytes(canonical_bytes(editor_run.output)),
                )
            except X02StageCallError as exc:
                _retain_failed_stage_run(gateway, stage_runs, exc.stage_run)
                recording_plan = aha_set_editor.unavailable_plan(
                    aha_discovery_plan, exc.code,
                )
                aha_editor_audit.update(status="FAILED_AHA_LANE_CLOSED", error_code=exc.code)
            aha_editor_model_seconds = time.monotonic() - editor_call_started
        allocation_plan = aha_set_editor.allocation_plan(recording_plan)
        stage_statuses.append(_stage_status(
            aha_set_editor.EDITOR_STAGE,
            str(aha_editor_audit["status"]),
            [
                "ONE_TEXT_ONLY_EDITOR_CALL_MAXIMUM",
                "ZERO_TO_THREE_AHAS_ACTIVE_TARGET_TWO_TO_THREE_WHEN_SUPPORTED",
                "NO_RETRY_NO_AUTOMATIC_FILL",
                "CHAPTERS_SURVIVE_AHA_EDITOR_FAILURE",
            ],
        ))
    if recording_plan is not None:
        if experience_editor_active:
            selected_chapters, selected_ahas, selection_audit, aha_selection_audit = experience_editor.execute_plan(
                recording_plan, chapter_candidates, chapter_ledger, aha_candidates, aha_ledger,
                observations, asset_order, minimum=chapter_display.MIN_MEDIA,
                max_chapters=MAX_CHAPTERS, max_ahas=MAX_AHAS,
            )
        elif recording_editor_policy == aha_set_editor.POLICY_VERSION:
            selected_chapters, selected_ahas, selection_audit, aha_selection_audit = aha_set_editor.execute_plan(
                recording_plan, chapter_candidates, chapter_ledger, aha_candidates, aha_ledger,
                observations, asset_order, minimum=chapter_display.MIN_MEDIA,
                max_chapters=MAX_CHAPTERS, max_ahas=MAX_AHAS,
            )
        elif recording_editor_policy == grounded_recording_editor.POLICY_VERSION:
            selected_chapters, selected_ahas, selection_audit, aha_selection_audit = grounded_recording_editor.execute_plan(
                recording_plan, chapter_candidates, chapter_ledger, aha_candidates, aha_ledger,
                observations, asset_order, minimum=chapter_display.MIN_MEDIA,
                max_chapters=MAX_CHAPTERS, max_ahas=MAX_AHAS,
            )
        else:
            selected_chapters, selected_ahas, selection_audit, aha_selection_audit = recording_editor.execute_plan(
                recording_plan, chapter_candidates, chapter_ledger, aha_candidates, aha_ledger,
                asset_order, allocation_plan, minimum=chapter_display.MIN_MEDIA,
                max_chapters=MAX_CHAPTERS, max_ahas=MAX_AHAS,
            )
    else:
        selected_chapters, selection_audit = (
            _select_storyline_set(chapter_candidates, chapter_ledger, observations, asset_order,
                                  editorial_priority=order_plan["chapters"] if order_plan else None)
            if storyline_policy
            else _select_chapter_set(chapter_candidates, chapter_ledger, observations, asset_order)
        )
        selected_ahas, aha_selection_audit = _select_aha_set(
            aha_candidates,
            aha_ledger,
            selected_chapters,
            observations,
            asset_order,
            value_first=stop_loss_v041,
            allocation_plan=allocation_plan,
            editorial_priority=order_plan["ahas"] if order_plan else None,
        )
    selection_complete = time.monotonic()
    stage_statuses.append(_stage_status("S08_S09_EDITORIAL_SET", "COMPLETED", [
        (
            (recording_plan["execution_status"] if recording_plan is not None else
             "MODEL_EDITORIAL_ORDER_WITH_EXISTING_FEASIBILITY_NOT_QUALITY_VERIFIED"
             if order_plan and editorial_order.applied(order_plan["chapters"])
             else "MODEL_GROUPS_WITH_EXISTING_VALUE_THRESHOLDS_NOT_QUALITY_VERIFIED")
            if storyline_policy else "SET_LEVEL_SELECTION_NOT_TOP_K"
        ),
        "INVALID_CANDIDATES_EXCLUDED_BEFORE_OVERLAP",
        "NO_OUTPUT_QUOTA",
        str(aha_selection_audit["search_outcome"]),
    ]))

    media_started = time.monotonic()
    media_model_seconds = 0.0
    media_model_evidence_bytes = 0
    display_selections = {}
    media_content_inputs = []
    if storyline_policy:
        # All facts here are already accepted candidate facts. S10 receives
        # only the current Chapter's relation hints, never a new candidate.
        allocation_media_scope = editorial_allocation.project(allocation_plan, [{
            "candidate_id": candidate["candidate_id"],
            "memory_type": memory_type,
            "facts": [fact for obs in observations for fact in obs["facts"]
                      if fact["fact_id"] in candidate["fact_ids"]],
        } for memory_type, candidates in (("CHAPTER", selected_chapters), ("AHA", selected_ahas))
          for candidate in candidates])
        observations_by_id = {item["id"]: item for item in observations}
        assets_by_id = {asset["asset_id"]: asset for asset in assets}
        for chapter_index, candidate in enumerate(selected_chapters):
            members = [observations_by_id[value] for value in candidate["observation_ids"]]
            output = None
            fallback_reason = "MODEL_NOT_NEEDED"
            evidence = []
            comparison_attempted = False
            if len(members) > chapter_display.MIN_MEDIA:
                for member in members:
                    asset = assets_by_id[member["source_asset_id"]]
                    frame = next(frame for frame in asset["frames"]
                                 if frame["frame_id"] == member["evidence_frame_ids"][0])
                    evidence.append((asset, frame, _manifest_frame_path(bundle, frame)))
                evidence_bytes = sum(path.stat().st_size for _, _, path in evidence)
                # Reuse the existing request-byte bound; never add uploads or retries.
                writer_call_reserve = 2 * (len(selected_chapters) + len(selected_ahas))
                if model_call_attempt_count + writer_call_reserve >= V041_RUN_MAX_MODEL_CALL_ATTEMPTS:
                    fallback_reason = "CALL_BUDGET_RESERVED_FOR_EXISTING_PIPELINE"
                elif len(evidence) > chapter_display.MAX_COMPARISON_FRAMES or evidence_bytes > PERCEPTION_BATCH_MAX_EVIDENCE_BYTES:
                    fallback_reason = "COMPARISON_EXCEEDS_EXISTING_REQUEST_BOUND"
                else:
                    context = {
                        "candidate_id": candidate["candidate_id"],
                        **content_handoff.chapter_selection_content(candidate, members),
                        "members": [{
                            "observation_id": member["id"],
                            "source_asset_id": member["source_asset_id"],
                            "preview_frame_id": member["evidence_frame_ids"][0],
                            "media_kind": member["media_kind"],
                            "quality_score": member["quality_score"],
                        } for member in members],
                    }
                    context[editorial_allocation.POLICY_FIELD] = editorial_allocation.POLICY_VERSION
                    context["chapter_aha_relations"] = [
                        relation for relation in allocation_media_scope["relations"]
                        if relation["chapter_candidate_id"] == candidate["candidate_id"]
                    ]
                    media_prompt = chapter_display.selection_prompt(context)
                    call_started = time.monotonic()
                    media_content_inputs.append({
                        "candidate_id": candidate["candidate_id"],
                        "input_sha256": sha256_bytes(canonical_bytes(context)),
                        "prompt_sha256": sha256_bytes(media_prompt.encode("utf-8")),
                        "observation_ids": [member["id"] for member in members],
                        "fact_ids": [fact["fact_id"] for fact in context["facts"]],
                    })
                    media_model_evidence_bytes += evidence_bytes
                    comparison_attempted = True
                    try:
                        media_run = call_model(
                            "S10_CHAPTER_VISUAL_SELECTION_%02d" % (chapter_index + 1),
                            media_prompt,
                            chapter_display.SELECTION_SCHEMA,
                            evidence=evidence, context=context,
                        )
                        stage_runs.append(media_run)
                        output = media_run.output
                    except X02StageCallError as exc:
                        _retain_failed_stage_run(gateway, stage_runs, exc.stage_run)
                        fallback_reason = exc.code
                    media_model_seconds += time.monotonic() - call_started
            decision = chapter_display.choose_display(members, output, fallback_reason)
            decision["comparison_attempted"] = comparison_attempted
            decision["comparison_frame_ids"] = [frame["frame_id"] for _, frame, _ in evidence] if comparison_attempted else []
            display_selections[candidate["candidate_id"]] = decision
    chapter_media = {
        candidate["candidate_id"]: _select_chapter_media(
            candidate, observations, app_asset_ids, asset_order,
            display_selection=display_selections.get(candidate["candidate_id"]),
        )
        for candidate in selected_chapters
    }
    aha_media = {
        candidate["candidate_id"]: _select_aha_media(
            candidate, observations, app_asset_ids
        )
        for candidate in selected_ahas
    }
    media_complete = time.monotonic()
    stage_statuses.append(_stage_status("S10_MEDIA_EDITORIAL", "COMPLETED", [
        "FINAL_CHAPTER_MEDIA_THREE_TO_FIVE_NO_FILL_QUOTA",
        "ONE_STATIC_PREVIEW_HERO",
        "HQ_MATERIALIZATION_NOT_EXECUTED",
    ]))

    writer_started = time.monotonic()
    writer_context = _writer_context(
        selected_chapters,
        selected_ahas,
        chapter_media,
        aha_media,
        observations,
        storyline_v04=storyline_policy,
        grounded_editor_v2=grounded_editor_v2,
    )
    if storyline_policy:
        writer_context[content_handoff.POLICY_FIELD] = content_handoff.POLICY_VERSION
        writer_context[writer_exit.POLICY_FIELD] = writer_exit.POLICY_VERSION
        writer_context[editorial_allocation.POLICY_FIELD] = editorial_allocation.POLICY_VERSION
        writer_context["editorial_allocation"] = editorial_allocation.project(
            allocation_plan, writer_context["memories"],
        )
        if grounded_editor_v2:
            writer_context[grounded_recording_editor.WRITER_POLICY_FIELD] = (
                grounded_recording_editor.POLICY_VERSION
            )
        if experience_editor_active:
            writer_context[v174_writer.POLICY_FIELD] = v174_writer.POLICY_VERSION
    writer_schema = writer_exit.response_schema(WRITER_SCHEMA, writer_context)
    if grounded_editor_v2:
        writer_schema = grounded_recording_editor.writer_response_schema(writer_schema)
    if experience_editor_active:
        writer_model_context, writer_reference_maps = v174_writer.encode_context(writer_context)
        writer_model_prompt = v174_writer.prompt(writer_context, writer_model_context, {
            "title_min": CHAPTER_TITLE_VISIBLE_MIN,
            "title_target": CHAPTER_TITLE_VISIBLE_TARGET_MAX,
            "title_max": CHAPTER_TITLE_VISIBLE_HARD_MAX,
            "chapter_target": CHAPTER_STORY_PREVIEW_TARGET_VISIBLE_MAX,
            "aha_max": grounded_recording_editor.AHA_VISIBLE_MAX,
        })
    else:
        writer_model_context = writer_context
        writer_reference_maps = None
        writer_model_prompt = _writer_prompt(writer_context, retry=False)
    if writer_context["memories"] and not stop_loss_v041:
        writer_run = call_model(
            "S11_WRITER_ATTEMPT_1",
            writer_model_prompt,
            writer_schema,
            context=writer_model_context,
        )
        stage_runs.append(writer_run)
        writer_validation_started = time.monotonic()
        writer_output = (
            v174_writer.decode_output(writer_run.output, writer_reference_maps)
            if experience_editor_active else writer_run.output
        )
        narratives, writer_audit, invalid_ids = _validate_writer_output(
            writer_output, writer_context, attempt=1
        )
        if invalid_ids:
            retry_context = _writer_retry_context(writer_context, invalid_ids, writer_audit)
            retry_run = call_model(
                "S11_WRITER_ATTEMPT_2",
                _writer_prompt(retry_context, retry=True),
                writer_schema,
                context=retry_context,
            )
            stage_runs.append(retry_run)
            retry_narratives, retry_audit, _ = _validate_writer_output(
                retry_run.output, retry_context, attempt=2
            )
            narratives.update(retry_narratives)
            writer_audit.extend(retry_audit)
        writer_complete = time.monotonic()
        writer_model_seconds = sum(
            run.latency_seconds for run in stage_runs if run.stage.startswith("S11_")
        )
        writer_validation_seconds = max(
            0.0,
            (writer_complete - writer_validation_started)
            - max(0.0, writer_model_seconds - writer_run.latency_seconds),
        )
        writer_status = (
            "COMPLETED"
            if len(narratives) == len(writer_context["memories"])
            else "COMPLETED_WITH_ITEM_BLOCKS"
        )
    elif writer_context["memories"]:
        writer_validation_started = time.monotonic()
        narratives: Dict[str, Dict[str, object]] = {}
        writer_audit: List[Dict[str, object]] = []
        invalid_ids = [str(item["candidate_id"]) for item in writer_context["memories"]]

        def record_writer_call_failure(
            call_context: Mapping[str, object],
            attempt: int,
            reason_code: str,
            detail: str,
        ) -> None:
            writer_audit.extend({
                "candidate_id": str(item["candidate_id"]),
                "memory_type": str(item["memory_type"]),
                "attempt": attempt,
                "surface_source": "MODEL_WRITER",
                "surface_policy_version": X02_WRITER_SURFACE_POLICY_VERSION,
                "validation_status": "REJECTED",
                "reason_codes": [reason_code],
                "detail": detail[:500],
            } for item in call_context.get("memories", []))

        try:
            writer_run = call_model(
                "S11_WRITER_ATTEMPT_1",
                writer_model_prompt,
                writer_schema,
                context=writer_model_context,
            )
            stage_runs.append(writer_run)
            writer_output = (
                v174_writer.decode_output(writer_run.output, writer_reference_maps)
                if experience_editor_active else writer_run.output
            )
            narratives, attempt_audit, invalid_ids = _validate_writer_output(
                writer_output, writer_context, attempt=1
            )
            writer_audit.extend(attempt_audit)
        except X02StageCallError as exc:
            _retain_failed_stage_run(gateway, stage_runs, exc.stage_run)
            record_writer_call_failure(writer_context, 1, exc.code, str(exc))
        except X02Error as exc:
            record_writer_call_failure(
                writer_context, 1, "WRITER_MODEL_REQUEST_FAILED", str(exc)
            )
        if invalid_ids and not writer_exit.enabled(writer_context):
            retry_context = _writer_retry_context(writer_context, invalid_ids, writer_audit)
            try:
                retry_run = call_model(
                    "S11_WRITER_ATTEMPT_2",
                    _writer_prompt(retry_context, retry=True),
                    writer_schema,
                    context=retry_context,
                )
                stage_runs.append(retry_run)
                retry_narratives, retry_audit, _ = _validate_writer_output(
                    retry_run.output, retry_context, attempt=2
                )
                narratives.update(retry_narratives)
                writer_audit.extend(retry_audit)
            except X02StageCallError as exc:
                _retain_failed_stage_run(gateway, stage_runs, exc.stage_run)
                record_writer_call_failure(retry_context, 2, exc.code, str(exc))
            except X02Error as exc:
                record_writer_call_failure(
                    retry_context, 2, "WRITER_MODEL_REQUEST_FAILED", str(exc)
                )
        fallback_ids = (
            [] if experience_editor_active
            else _writer_fallback_ids(writer_context, narratives)
        )
        if fallback_ids:
            fallback_context = _writer_retry_context(
                writer_context, fallback_ids, writer_audit
            )
            fallback_output, fallback_generation_audit = _deterministic_writer_fallback(
                fallback_context
            )
            fallback_narratives, fallback_audit, _ = _validate_writer_output(
                fallback_output,
                fallback_context,
                attempt=3,
                surface_source="DETERMINISTIC_GROUNDED_FALLBACK",
            )
            narratives.update(fallback_narratives)
            writer_audit.extend(fallback_generation_audit)
            writer_audit.extend(fallback_audit)
        writer_complete = time.monotonic()
        writer_model_seconds = sum(
            run.latency_seconds for run in stage_runs if run.stage.startswith("S11_")
        )
        writer_validation_seconds = max(
            0.0,
            (writer_complete - writer_validation_started)
            - writer_model_seconds,
        )
        fallback_used = any(
            item.get("surface_source") == "DETERMINISTIC_GROUNDED_FALLBACK"
            and item.get("validation_status") == "PASSED"
            for item in writer_audit
        )
        if len(narratives) != len(writer_context["memories"]):
            writer_status = "COMPLETED_WITH_ITEM_BLOCKS"
        elif fallback_used:
            writer_status = "COMPLETED_WITH_GROUNDED_FALLBACK"
        else:
            writer_status = "COMPLETED"
    else:
        narratives, writer_audit, writer_validation_seconds = {}, [], 0.0
        writer_status = "SKIPPED_NO_SELECTED_MEMORY"
    stage_statuses.append(_stage_status(
        "S11_GROUNDED_NARRATIVE",
        writer_status,
        (["APPROVED_CLAIM_IDS_ONLY", "BOUNDED_WRITER_RETRY"] if not stop_loss_v041 else [
            "MODEL_NATURAL_COPY_WITH_FORMAT_AND_REFERENCE_CHECKS",
            "DETERMINISTIC_ALLOWED_TITLE_GATE",
            ("WRITER_SINGLE_PASS_NO_MODEL_REWRITE" if writer_exit.enabled(writer_context)
             else "BOUNDED_WRITER_RETRY"),
            (
                "NO_RAW_FACT_OR_GENERIC_COPY_FALLBACK"
                if experience_editor_active
                else "SAME_SELECTED_MEMORY_DETERMINISTIC_GROUNDED_FALLBACK"
            ),
            *(["REQUEST_LOCAL_SHORT_REFERENCES_PRIVATE_CANONICAL_MAP"]
              if experience_editor_active else []),
            "NO_WRITER_TIME_CANDIDATE_REPLACEMENT",
        ]),
    ))

    validation_started = time.monotonic()
    chapters, blocked_chapters = _public_chapters(
        namespace,
        selected_chapters,
        chapter_media,
        narratives,
        observations,
        moments,
        asset_order,
        include_storyline=storyline_policy,
        include_surface_provenance=stop_loss_v041,
        generic_animal_subjects=stop_loss_v041,
    )
    ahas, blocked_ahas = _public_ahas(
        namespace,
        selected_ahas,
        aha_media,
        narratives,
        observations,
        moments,
        asset_order,
        include_surface_provenance=stop_loss_v041,
        generic_animal_subjects=stop_loss_v041,
    )
    validation_complete = time.monotonic()
    if writer_exit.enabled(writer_context):
        for blocked in blocked_chapters + blocked_ahas:
            if blocked["failure_owner"] == "S11_WRITER":
                blocked["reason_code"] = (
                    "NO_VALID_WRITER_OUTPUT_AFTER_SINGLE_PASS_NO_FALLBACK"
                    if experience_editor_active
                    else "NO_VALID_WRITER_OUTPUT_AFTER_SINGLE_PASS_AND_LOCAL_FALLBACK"
                )
    media_only_chapters = []
    if experience_editor_active:
        writer_failures = {
            str(item.get("candidate_id")): list(item.get("reason_codes", []))
            for item in writer_audit if item.get("validation_status") == "REJECTED"
        }
        for candidate in selected_chapters:
            candidate_id = str(candidate["candidate_id"])
            if candidate_id in narratives:
                continue
            media = chapter_media.get(candidate_id, {})
            if not 3 <= len(media.get("media", [])) <= 5:
                continue
            media_only_chapters.append({
                "memory_id": _stable_id(namespace, "chapter:" + candidate_id),
                "candidate_id": candidate_id,
                "storyline_identity": copy.deepcopy(candidate.get("storyline_identity", {})),
                "hero_asset_id": media.get("hero_asset_id"),
                "selected_media": copy.deepcopy(media.get("media", [])),
                "fact_ids": list(candidate.get("fact_ids", [])),
                "copy_status": "UNAVAILABLE",
                "visibility_state": "INTERNAL_MEDIA_LEDGER_ONLY",
                "reason_codes": writer_failures.get(
                    candidate_id, ["NO_VALID_WRITER_OUTPUT_AFTER_SINGLE_PASS_NO_FALLBACK"],
                ),
            })
    stage_statuses.append(_stage_status(
        "S12_FINAL_VALIDATION",
        "COMPLETED" if not blocked_chapters and not blocked_ahas else "COMPLETED_WITH_ITEM_BLOCKS",
        ["NO_SILENT_CROSS_STAGE_REPAIR", "UNSUPPORTED_COPY_OR_TAG_BLOCKED"],
    ))
    stage_statuses.append(_stage_status("S13_HQ_EXPORT", "NOT_EXECUTED", [
        "OUTSIDE_STAGED_WEB_PREVIEW",
    ]))

    model_complete = time.monotonic()
    stage_metrics = [
        _metric("S00_S02_BUNDLE_LOAD", bundle_complete - run_started),
    ]
    stage_metrics.extend(_metric_from_run(run) for run in stage_runs if run.stage.startswith("S04_"))
    stage_metrics.extend([
        _metric("S04_DETERMINISTIC_VALIDATION", perception_validation_seconds),
    ])
    stage_metrics.extend(_metric_from_run(run) for run in stage_runs if run.stage == "S05_S07_STRUCTURE_PROPOSAL")
    stage_metrics.extend(
        _metric_from_run(run) for run in stage_runs
        if run.stage in (aha_set_editor.EDITOR_STAGE, experience_editor.EDITOR_STAGE)
    )
    stage_metrics.extend([
        _metric("S03_S07_DETERMINISTIC_STRUCTURE", structure_deterministic_seconds),
        _metric(
            "S08_S09_SET_SELECTION",
            max(0.0, selection_complete - selection_started - aha_editor_model_seconds),
        ),
        _metric("S10_MEDIA_EDITORIAL", max(0.0, media_complete - media_started - media_model_seconds)),
    ])
    stage_metrics.extend(_metric_from_run(run) for run in stage_runs if run.stage.startswith("S10_CHAPTER_VISUAL_SELECTION_"))
    stage_metrics.extend(_metric_from_run(run) for run in stage_runs if run.stage.startswith("S11_"))
    stage_metrics.append(_metric("S11_DETERMINISTIC_VALIDATION", writer_validation_seconds))
    stage_metrics.append(_metric("S12_FINAL_VALIDATION", validation_complete - validation_started))

    input_tokens = sum(run.input_tokens for run in stage_runs)
    output_tokens = sum(run.output_tokens for run in stage_runs)
    model_calls = sum(run.model_calls for run in stage_runs)
    total_cost_usd = sum(run.estimated_cost_usd for run in stage_runs)
    uploaded_bytes = sum(
        _manifest_frame_path(bundle, frame).stat().st_size
        for asset in assets
        for frame in asset["frames"]
    )
    model_evidence_bytes = media_model_evidence_bytes + sum(
        path.stat().st_size
        for asset in assets
        for _, _, path in _perception_evidence(bundle, [asset])
    )
    request_ids = [run.request_id for run in stage_runs]
    run_id = str(uuid.uuid4())
    blocked_memories = blocked_chapters + blocked_ahas
    coverage_status = "PARTIAL_UNRESOLVED" if unresolved_asset_ids else "COMPLETE"
    if unresolved_asset_ids:
        for item in [*chapters, *ahas]:
            item["publication_status"] = "STAGED_PREVIEW_DIAGNOSTIC_ONLY"
    if unresolved_asset_ids:
        semantic_day_state = "UNRESOLVED_DAY"
    elif selected_chapters:
        semantic_day_state = "CHAPTER_DAY"
    elif selected_ahas:
        semantic_day_state = "HIGHLIGHT_DAY"
    else:
        semantic_day_state = "EMPTY_DAY"
    public_candidate_ids = {
        str(item["candidate_id"]) for item in [*chapters, *ahas]
    }
    selected_memory_outcomes = []
    for memory_type, selected_items, media_map in (
        ("CHAPTER", selected_chapters, chapter_media),
        ("AHA", selected_ahas, aha_media),
    ):
        for candidate in selected_items:
            candidate_id = str(candidate["candidate_id"])
            narrative = narratives.get(candidate_id)
            media_entry = media_map.get(candidate_id, {})
            minimum_media = (
                3 if memory_type == "CHAPTER" else 1
            )
            media_ready = minimum_media <= len(media_entry.get("media", [])) <= (
                5 if memory_type == "CHAPTER" else 1
            )
            if narrative is None:
                surface_state = "COPY_BLOCKED"
            elif narrative.get("surface_source") == "DETERMINISTIC_GROUNDED_FALLBACK":
                surface_state = "DETERMINISTIC_FALLBACK_VERIFIED"
            else:
                surface_state = "MODEL_SURFACE_VERIFIED"
            visible = candidate_id in public_candidate_ids and not unresolved_asset_ids
            selected_memory_outcomes.append({
                "memory_type": memory_type,
                "memory_id": _stable_id(
                    namespace,
                    ("chapter:" if memory_type == "CHAPTER" else "aha:") + candidate_id,
                ),
                "selection_state": "S09_SELECTED",
                "media_state": "S10_MEDIA_READY" if media_ready else "S10_MEDIA_BLOCKED",
                "surface_state": surface_state if media_ready else "NOT_ATTEMPTED",
                "visibility_state": "VISIBLE_PREVIEW" if visible else "DIAGNOSTIC_ONLY",
            })
    visible_outcomes = [
        item for item in selected_memory_outcomes
        if item["visibility_state"] == "VISIBLE_PREVIEW"
    ]
    if unresolved_asset_ids:
        delivery_state = "PIPELINE_BLOCKED"
    elif not selected_memory_outcomes:
        delivery_state = "NO_GROUNDED_MEMORY"
    elif len(visible_outcomes) < len(selected_memory_outcomes):
        delivery_state = (
            "READY_WITH_ITEM_BLOCKS" if visible_outcomes else "PIPELINE_BLOCKED"
        )
    elif any(
        item["surface_state"] == "DETERMINISTIC_FALLBACK_VERIFIED"
        for item in selected_memory_outcomes
    ):
        delivery_state = "READY_WITH_GROUNDED_COPY_FALLBACK"
    else:
        delivery_state = "READY_PRIMARY_COPY"
    output_mode = (
        "PIPELINE_BLOCKED" if delivery_state == "PIPELINE_BLOCKED" else semantic_day_state
    )
    capture_times = [str(asset["capture_time"]) for asset in assets if asset.get("capture_time")]
    # V04.1 intentionally refuses to elevate unverified timestamps in current
    # bundle versions into day/date/interval truth. Historical V03 projection
    # below remains unchanged.
    capture_time_reliable = False
    timeline_basis = "SYNTHETIC_SEQUENCE_ONLY"
    timeline_date = None
    time_reliability = {
        "capture_time_reliable": capture_time_reliable,
        "interval_reliable": capture_time_reliable,
        "timezone_reliable": capture_time_reliable and str(
            bundle.manifest["session"].get("timezone", "")
        ) not in ("", "TEST_DAY_NO_TIMEZONE"),
    }
    result = {
        "schema_version": result_schema_version,
        "experiment": X02_EXPERIMENT,
        "experimental": True,
        "leaderboard_eligible": False,
        "production_ready": False,
        "observation_semantic_contract_version": X02_OBSERVATION_COMPATIBILITY_VERSION,
        "observation_semantic_contract_sha256": X02_OBSERVATION_COMPATIBILITY_SHA256,
        "field_degradation_contract_version": X02_FIELD_DEGRADATION_VERSION,
        "field_degradation_contract_sha256": X02_FIELD_DEGRADATION_SHA256,
        "writer_surface_policy_version": X02_WRITER_SURFACE_POLICY_VERSION,
        "evaluation_run_mode": X02_EVALUATION_RUN_MODE,
        "cross_run_semantic_cache_used": False,
        "session_id": str(bundle.manifest["session"]["session_id"]),
        "bundle_manifest_sha256": sha256_file(bundle.manifest_path),
        "output_mode": output_mode,
        "semantic_day_state": semantic_day_state,
        "delivery_state": delivery_state,
        "selected_memory_outcomes": selected_memory_outcomes,
        "validation_scope": "STAGED_PREVIEW_ONLY",
        "coverage_status": coverage_status,
        "unresolved_asset_ids": unresolved_asset_ids,
        "timeline_basis": timeline_basis,
        "timeline_date": timeline_date,
        "time_reliability": time_reliability,
        "observations": observations,
        "moments": moments,
        "chapters": chapters,
        "ahas": ahas,
        "decision_trace": {
            "trace_type": "AUDITABLE_STAGE_DECISION_EVIDENCE",
            "contains_hidden_reasoning": False,
            "scope_note": (
                "Shows supplied evidence, model-visible structured outputs, deterministic gates, "
                "lineage, and reason codes. It does not expose or invent model chain-of-thought."
            ),
            "stage_statuses": stage_statuses,
            "evidence_selection": {
                "strategy": (
                    "PHOTO_ONE_FRAME_VIDEO_DURATION_AWARE_WINDOWS_IN_BOUNDED_DYNAMIC_BATCHES"
                    if stop_loss_v041 and uses_duration_windows
                    else "PHOTO_ONE_FRAME_VIDEO_DURATION_AWARE_WINDOWS_IN_BALANCED_ASSET_BATCHES"
                    if uses_duration_windows
                    else "LEGACY_PHOTO_MIDDLE_VIDEO_FIXED_THREE_IN_BALANCED_ASSET_BATCHES"
                ),
                "input_order_bias_prevention": True,
                "selected": evidence_ledger,
            },
            "perception_batching": {
                "policy": (
                    "V04_1_BOUNDED_ASSETS_FRAMES_BYTES_WITH_FAILURE_ISOLATION"
                    if stop_loss_v041 else "V03_FIXED_ASSET_BATCHES"
                ),
                "max_assets": PERCEPTION_BATCH_MAX_ASSETS if stop_loss_v041 else PERCEPTION_V03_BATCH_SIZE,
                "max_frames": PERCEPTION_BATCH_MAX_FRAMES if stop_loss_v041 else None,
                "max_evidence_bytes": PERCEPTION_BATCH_MAX_EVIDENCE_BYTES if stop_loss_v041 else None,
                "single_asset_retry_limit": PERCEPTION_SINGLE_ASSET_RETRY_LIMIT if stop_loss_v041 else 0,
                "run_max_model_call_attempts": (
                    V041_RUN_MAX_MODEL_CALL_ATTEMPTS if stop_loss_v041 else None
                ),
                "model_call_attempt_count": model_call_attempt_count,
                "circuit_breaker_tripped": model_call_circuit_breaker_tripped,
                "planned_batch_count": len(planned_batches),
                "attempts": perception_batch_attempts,
                "coverage_status": coverage_status,
                "unresolved_asset_ids": unresolved_asset_ids,
            },
            "observation_candidates": observation_ledger,
            "boundary_edges": edges,
            "observation_roles": roles,
            "chapter_candidates": chapter_ledger,
            "aha_candidates": aha_ledger,
            "chapter_set_selection": selection_audit,
            "aha_set_selection": aha_selection_audit,
            "s10_chapter_media": list(chapter_media.values()),
            "s10_aha_media": list(aha_media.values()),
            "writer_items": writer_audit,
            "media_only_chapters": media_only_chapters,
            "blocked_memories": blocked_memories,
            "counts": {
                "asset_count": len(assets),
                "accepted_observation_count": observed_count,
                "field_degraded_observation_count": degraded_observation_count,
                "insufficient_evidence_observation_count": sum(
                    1 for item in observations if item["status"] == "INSUFFICIENT_EVIDENCE"
                ),
                "failed_observation_count": sum(
                    1 for item in observations if item["status"] == "FAILED"
                ),
                "moment_count": len(moments),
                "chapter_candidate_count": len(chapter_candidates),
                "selected_chapter_count_before_writer": len(selected_chapters),
                "published_preview_chapter_count": len(chapters),
                "aha_candidate_count": len(aha_candidates),
                "selected_aha_count_before_writer": len(selected_ahas),
                "published_preview_aha_count": len(ahas),
            },
        },
        "trace": {
            "run_id": run_id,
            "pipeline_version": pipeline_version,
            "execution_mode": "STAGED_REAL_MEDIA_PREVIEW_NOT_PRODUCTION",
            "evaluation_run_mode": X02_EVALUATION_RUN_MODE,
            "cross_run_semantic_cache_used": False,
            "input_bundle_version": input_bundle_version,
            "evidence_profile_version": str(
                bundle.validation.get("evidence_profile_version", "UNKNOWN")
            ),
            "provider": gateway.provider,
            "model": gateway.model,
            "request_id": request_ids[-1] if request_ids else "no-model-request",
            "request_ids": request_ids,
            "model_calls": model_calls,
            "model_call_attempted_count": model_call_attempt_count,
            "model_call_completed_count": sum(
                run.model_calls for run in stage_runs if run.call_status == "COMPLETED"
            ),
            "model_call_failed_count": sum(
                run.model_calls for run in stage_runs if run.call_status != "COMPLETED"
            ),
            "run_max_model_call_attempts": (
                V041_RUN_MAX_MODEL_CALL_ATTEMPTS if stop_loss_v041 else None
            ),
            "model_call_circuit_breaker_tripped": model_call_circuit_breaker_tripped,
            "asset_count": len(assets),
            "evidence_frame_count": len(evidence_ledger),
            "model_frame_count": sum(run.model_frame_count for run in stage_runs),
            "uploaded_bytes": uploaded_bytes,
            "model_evidence_bytes": model_evidence_bytes,
            "originals_uploaded": 0,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_seconds": round(sum(run.latency_seconds for run in stage_runs), 6),
            "estimated_cost_usd": round(total_cost_usd, 8),
            "stage_metrics": stage_metrics,
            "total_duration_ms": round((model_complete - run_started) * 1_000.0, 3),
            "stage_metric_scope": (
                "Measured staged-preview work. Tokens and cost are attributed to the exact model call "
                "that incurred them; deterministic stages report zero model usage."
            ),
            "s13_status": "NOT_EXECUTED_IN_WEB_PREVIEW",
        },
    }
    if storyline_policy:
        result["storyline_contract_version"] = X02_STORYLINE_CONTRACT_VERSION
        result["decision_trace"]["runtime_policies"] = x02_runtime_policies()
        if experience_editor_active:
            result["decision_trace"]["runtime_policies"]["writer_exit"] = (
                v174_writer.POLICY_VERSION
            )
        result["decision_trace"]["structure_wire"] = structure_wire_audit
        if order_plan is not None:
            result["decision_trace"]["editorial_order"] = order_plan
        if recording_plan is not None:
            result["decision_trace"]["recording_editor"] = recording_plan
            result["decision_trace"]["runtime_policies"]["recording_editor"] = recording_editor_policy
        if aha_editor_audit is not None:
            result["decision_trace"][
                "aha_experience_editor" if experience_editor_active else "aha_set_editor"
            ] = aha_editor_audit
        result["decision_trace"]["editorial_allocation"] = {
            "plan": allocation_plan,
            "writer_projection": writer_context["editorial_allocation"],
            "additional_model_steps": (
                1 if recording_editor_policy in (
                    aha_set_editor.POLICY_VERSION, experience_editor.POLICY_VERSION,
                ) else 0
            ),
            "scope": "RESEARCH_PREVIEW_NOT_FULL_CANONICAL_INDEPENDENCE_VERIFICATION",
        }
        result["storyline_contract_sha256"] = X02_STORYLINE_CONTRACT_SHA256
        result["chapter_media_policy_version"] = chapter_display.POLICY_VERSION
        projected_writer_input = (
            writer_model_context
            if experience_editor_active
            else grounded_recording_editor.writer_input(writer_context)
            if grounded_editor_v2
            else content_handoff.writer_input(writer_context)
        )
        result["decision_trace"]["content_handoff"] = {
            "policy_version": content_handoff.POLICY_VERSION,
            "guidance_scope": "EDITORIAL_HINTS_NOT_FACT_EVIDENCE",
            "media_comparison_inputs": media_content_inputs,
            "prepared_first_writer_scope": [{
                "candidate_id": item["candidate_id"],
                "memory_type": item["memory_type"],
                "material_fact_refs": [{
                    "observation_id": material["observation_id"],
                    "fact_ids": material["fact_ids"],
                } for material in item["content_brief"]["materials"]],
                "fact_ids": [fact["fact_id"] for fact in item["facts"]],
            } for item in projected_writer_input["memories"]],
            "prepared_first_writer_input_sha256": sha256_bytes(canonical_bytes(projected_writer_input)),
            "prepared_first_writer_prompt_sha256": sha256_bytes(
                writer_model_prompt.encode("utf-8")
            ),
            **({
                "request_local_reference_map": writer_reference_maps,
                "writer_exit_policy_version": v174_writer.POLICY_VERSION,
            } if experience_editor_active else {}),
            "fact_validation_scope_unchanged": True,
            "additional_model_steps": 0,
        }
    if stop_loss_v041:
        _validate_v041_result_state(
            result,
            expected_asset_ids=[str(asset["asset_id"]) for asset in assets],
            expected_evidence_frame_ids=[
                str(frame["frame_id"])
                for asset in assets
                for _, frame, _ in _perception_evidence(bundle, [asset])
            ],
        )
    if not stop_loss_v041:
        if chapters:
            result["output_mode"] = "CHAPTER_DAY"
        elif ahas:
            result["output_mode"] = "HIGHLIGHT_DAY"
        elif blocked_memories:
            result["output_mode"] = "PIPELINE_BLOCKED"
        else:
            result["output_mode"] = "EMPTY_DAY"
        result["timeline_date"] = (
            min(capture_times)
            if capture_times else str(bundle.manifest["session"]["exported_at"])
        )
        for field in (
            "writer_surface_policy_version",
            "semantic_day_state",
            "delivery_state",
            "selected_memory_outcomes",
            "validation_scope",
            "coverage_status",
            "unresolved_asset_ids",
            "timeline_basis",
            "time_reliability",
        ):
            result.pop(field, None)
        for field in (
            "model_call_attempted_count",
            "model_call_completed_count",
            "model_call_failed_count",
            "run_max_model_call_attempts",
            "model_call_circuit_breaker_tripped",
        ):
            result["trace"].pop(field, None)
        for metric in result["trace"]["stage_metrics"]:
            metric.pop("call_status", None)
        result["decision_trace"].pop("perception_batching", None)
    return result


def _validate_v041_result_state(
    result: Mapping[str, object],
    *,
    expected_asset_ids: Optional[Sequence[str]] = None,
    expected_evidence_frame_ids: Optional[Sequence[str]] = None,
) -> None:
    """Fail closed if independently derived V04.1 result axes disagree."""

    try:
        coverage = str(result["coverage_status"])
        unresolved = list(result["unresolved_asset_ids"])
        batching = result["decision_trace"]["perception_batching"]
        outcomes = list(result["selected_memory_outcomes"])
        chapters = list(result["chapters"])
        ahas = list(result["ahas"])
    except (KeyError, TypeError) as exc:
        raise X02ContractError("V04.1 final state is incomplete") from exc
    if coverage != batching.get("coverage_status") or unresolved != list(
        batching.get("unresolved_asset_ids", [])
    ):
        raise X02ContractError("V04.1 coverage ledger mismatch")
    if (
        batching.get("max_assets") != PERCEPTION_BATCH_MAX_ASSETS
        or batching.get("max_frames") != PERCEPTION_BATCH_MAX_FRAMES
        or batching.get("max_evidence_bytes") != PERCEPTION_BATCH_MAX_EVIDENCE_BYTES
        or batching.get("single_asset_retry_limit") != PERCEPTION_SINGLE_ASSET_RETRY_LIMIT
    ):
        raise X02ContractError("V04.1 perception batching contract mismatch")
    if (
        batching.get("run_max_model_call_attempts")
        != V041_RUN_MAX_MODEL_CALL_ATTEMPTS
        or result.get("trace", {}).get("run_max_model_call_attempts")
        != V041_RUN_MAX_MODEL_CALL_ATTEMPTS
        or batching.get("model_call_attempt_count")
        != result.get("trace", {}).get("model_call_attempted_count")
    ):
        raise X02ContractError("V04.1 model-call attempt ledger mismatch")
    attempted_count = batching.get("model_call_attempt_count")
    if (
        not isinstance(attempted_count, int)
        or isinstance(attempted_count, bool)
        or not 0 <= attempted_count <= V041_RUN_MAX_MODEL_CALL_ATTEMPTS
    ):
        raise X02ContractError("V04.1 model-call attempt count invalid")

    observations = list(result.get("observations", []))
    observation_asset_ids = [str(item.get("source_asset_id")) for item in observations]
    if (
        len(observation_asset_ids) != len(set(observation_asset_ids))
        or len(observation_asset_ids) != result.get("trace", {}).get("asset_count")
    ):
        raise X02ContractError("V04.1 observation asset coverage invalid")
    if (
        expected_asset_ids is not None
        and observation_asset_ids != list(expected_asset_ids)
    ):
        raise X02ContractError("V04.1 observation assets do not match input bundle")
    selected_evidence = list(
        result.get("decision_trace", {}).get("evidence_selection", {}).get("selected", [])
    )
    selected_frame_ids = [str(item.get("frame_id")) for item in selected_evidence]
    if (
        len(selected_frame_ids) != len(set(selected_frame_ids))
        or len(selected_frame_ids) != result.get("trace", {}).get("evidence_frame_count")
        or any(
            str(item.get("source_asset_id")) not in set(observation_asset_ids)
            for item in selected_evidence
        )
    ):
        raise X02ContractError("V04.1 evidence-frame coverage invalid")
    if (
        expected_evidence_frame_ids is not None
        and selected_frame_ids != list(expected_evidence_frame_ids)
    ):
        raise X02ContractError("V04.1 evidence frames do not match input bundle")

    attempts = list(batching.get("attempts", []))
    attempt_by_id: Dict[str, Mapping[str, object]] = {}
    for attempt in attempts:
        if not isinstance(attempt, Mapping):
            raise X02ContractError("V04.1 perception attempt must be an object")
        attempt_id = str(attempt.get("attempt_id", ""))
        asset_ids = [str(value) for value in attempt.get("asset_ids", [])]
        terminal_ids = [
            str(value) for value in attempt.get("terminal_unresolved_asset_ids", [])
        ]
        status = attempt.get("status")
        action = attempt.get("recovery_action")
        reason_code = str(attempt.get("reason_code", ""))
        provider_called = attempt.get("provider_call_attempted")
        if (
            not attempt_id
            or attempt_id in attempt_by_id
            or not asset_ids
            or len(asset_ids) != len(set(asset_ids))
            or not set(asset_ids).issubset(set(observation_asset_ids))
            or attempt.get("asset_count") != len(asset_ids)
            or not isinstance(attempt.get("frame_count"), int)
            or isinstance(attempt.get("frame_count"), bool)
            or attempt.get("frame_count") < 1
            or not isinstance(attempt.get("evidence_bytes"), int)
            or isinstance(attempt.get("evidence_bytes"), bool)
            or attempt.get("evidence_bytes") < 0
            or provider_called not in {True, False}
            or not reason_code
            or len(terminal_ids) != len(set(terminal_ids))
            or not set(terminal_ids).issubset(set(asset_ids))
        ):
            raise X02ContractError("V04.1 perception attempt identity invalid")
        if status == "REJECTED_PREFLIGHT":
            valid_state = (
                action == "TERMINAL_PREFLIGHT"
                and reason_code == "EVIDENCE_BUDGET_EXCEEDED"
                and provider_called is False
                and terminal_ids == asset_ids
            )
        elif status == "FAILED":
            valid_state = (
                action in {
                    "BISECT", "ORIGINAL_BATCH_RETRY", "SINGLETON_RETRY",
                    "TERMINAL_UNRESOLVED",
                }
                and (
                    not terminal_ids
                    if action in {"BISECT", "ORIGINAL_BATCH_RETRY", "SINGLETON_RETRY"}
                    else terminal_ids == asset_ids
                )
                and (
                    provider_called is False
                    if reason_code == "MODEL_CALL_CIRCUIT_BREAKER_OPEN"
                    else provider_called is True
                )
            )
        elif status == "VALIDATED":
            valid_state = (
                action == "NONE"
                and provider_called is True
                and not terminal_ids
            )
        elif status == "VALIDATED_WITH_ITEM_FAILURES":
            valid_state = (
                action in {"ITEM_LEVEL_RETRY", "TERMINAL_ITEM_FAILURE"}
                and provider_called is True
                and (
                    not terminal_ids
                    if action == "ITEM_LEVEL_RETRY"
                    else bool(terminal_ids)
                )
            )
        else:
            valid_state = False
        if not valid_state:
            raise X02ContractError("V04.1 perception attempt state invalid")
        attempt_by_id[attempt_id] = attempt
    roots = [attempt for attempt in attempts if attempt.get("parent_attempt_id") is None]
    root_asset_ids = [
        str(asset_id) for attempt in roots for asset_id in attempt.get("asset_ids", [])
    ]
    if (
        len(root_asset_ids) != len(set(root_asset_ids))
        or root_asset_ids != observation_asset_ids
        or len(roots) != batching.get("planned_batch_count")
    ):
        raise X02ContractError("V04.1 root perception batches do not partition input")
    children_by_parent: Dict[str, List[Mapping[str, object]]] = {}
    for attempt in attempts:
        parent_id = attempt.get("parent_attempt_id")
        if parent_id is None:
            if attempt.get("attempt_kind") != "ROOT":
                raise X02ContractError("V04.1 root perception attempt kind invalid")
            continue
        parent = attempt_by_id.get(str(parent_id))
        if parent is None:
            raise X02ContractError("V04.1 perception attempt parent missing")
        if not set(attempt.get("asset_ids", [])).issubset(set(parent.get("asset_ids", []))):
            raise X02ContractError("V04.1 perception child escapes parent assets")
        children_by_parent.setdefault(str(parent_id), []).append(attempt)
    for parent_id, children in children_by_parent.items():
        parent = attempt_by_id[parent_id]
        action = parent.get("recovery_action")
        if action == "BISECT":
            child_assets = [
                str(asset_id) for child in children for asset_id in child.get("asset_ids", [])
            ]
            if (
                len(children) != 2
                or any(child.get("attempt_kind") != "SPLIT_CHILD" for child in children)
                or len(child_assets) != len(set(child_assets))
                or set(child_assets) != set(parent.get("asset_ids", []))
                or not (
                    parent.get("reason_code") == "MODEL_HTTP_413"
                    or str(parent.get("reason_code", "")).startswith(
                        "PERCEPTION_ASSET_LOCAL_"
                    )
                )
            ):
                raise X02ContractError("V04.1 bisection children do not partition parent")
        elif action == "SINGLETON_RETRY":
            if (
                len(children) != 1
                or children[0].get("attempt_kind") != "SINGLETON_RETRY"
                or len(parent.get("asset_ids", [])) != 1
                or not str(parent.get("reason_code", "")).startswith(
                    "PERCEPTION_ASSET_LOCAL_"
                )
            ):
                raise X02ContractError("V04.1 singleton retry ancestry invalid")
        elif action == "ORIGINAL_BATCH_RETRY":
            if (
                len(children) != 1
                or children[0].get("attempt_kind") != "ORIGINAL_BATCH_RETRY"
                or list(children[0].get("asset_ids", []))
                != list(parent.get("asset_ids", []))
                or not (
                    parent.get("reason_code") == "MODEL_TRANSPORT_TIMEOUT"
                    or bool(re.fullmatch(
                        r"MODEL_HTTP_5\d\d", str(parent.get("reason_code", ""))
                    ))
                )
            ):
                raise X02ContractError("V04.1 original-batch retry ancestry invalid")
        elif action == "ITEM_LEVEL_RETRY":
            child_assets = [
                str(asset_id)
                for child in children
                for asset_id in child.get("asset_ids", [])
            ]
            if (
                not children
                or any(
                    child.get("attempt_kind") != "ITEM_RETRY"
                    or len(child.get("asset_ids", [])) != 1
                    for child in children
                )
                or len(child_assets) != len(set(child_assets))
            ):
                raise X02ContractError("V04.1 item retry ancestry invalid")
        else:
            raise X02ContractError("V04.1 terminal attempt unexpectedly has children")
    for attempt in attempts:
        action = attempt.get("recovery_action")
        has_children = str(attempt.get("attempt_id")) in children_by_parent
        if action in {
            "BISECT", "ORIGINAL_BATCH_RETRY", "SINGLETON_RETRY", "ITEM_LEVEL_RETRY",
        } and not has_children:
            raise X02ContractError("V04.1 recovery attempt is missing child attempts")
        if action not in {
            "BISECT", "ORIGINAL_BATCH_RETRY", "SINGLETON_RETRY", "ITEM_LEVEL_RETRY",
        } and has_children:
            raise X02ContractError("V04.1 terminal attempt unexpectedly has children")
    terminal_attempt_asset_list = [
        str(asset_id)
        for attempt in attempts
        for asset_id in attempt.get("terminal_unresolved_asset_ids", [])
    ]
    terminal_attempt_assets = set(terminal_attempt_asset_list)
    failed_observation_assets = {
        str(item.get("source_asset_id"))
        for item in observations if item.get("status") == "FAILED"
    }
    if (
        len(unresolved) != len(set(unresolved))
        or len(terminal_attempt_asset_list) != len(terminal_attempt_assets)
        or terminal_attempt_assets != set(unresolved)
        or failed_observation_assets != set(unresolved)
    ):
        raise X02ContractError("V04.1 terminal failure and unresolved assets disagree")
    if coverage == "COMPLETE" and terminal_attempt_assets:
        raise X02ContractError("V04.1 complete coverage retains terminal failure")

    outcome_keys = [
        "%s:%s" % (item.get("memory_type"), item.get("memory_id"))
        for item in outcomes
    ]
    if len(outcome_keys) != len(set(outcome_keys)):
        raise X02ContractError("V04.1 selected memory outcome identity duplicated")
    chapter_outcomes = [item for item in outcomes if item.get("memory_type") == "CHAPTER"]
    aha_outcomes = [item for item in outcomes if item.get("memory_type") == "AHA"]
    if len(chapter_outcomes) + len(aha_outcomes) != len(outcomes):
        raise X02ContractError("V04.1 selected memory outcome type invalid")
    for item in outcomes:
        media_state = item.get("media_state")
        surface_state = item.get("surface_state")
        visibility_state = item.get("visibility_state")
        if media_state == "S10_MEDIA_BLOCKED":
            local_state_valid = (
                surface_state == "NOT_ATTEMPTED"
                and visibility_state == "DIAGNOSTIC_ONLY"
            )
        elif media_state == "S10_MEDIA_READY" and surface_state == "COPY_BLOCKED":
            local_state_valid = visibility_state == "DIAGNOSTIC_ONLY"
        elif media_state == "S10_MEDIA_READY" and surface_state in {
            "MODEL_SURFACE_VERIFIED", "DETERMINISTIC_FALLBACK_VERIFIED",
        }:
            local_state_valid = visibility_state in {"VISIBLE_PREVIEW", "DIAGNOSTIC_ONLY"}
        else:
            local_state_valid = False
        if not local_state_valid:
            raise X02ContractError("V04.1 selected memory outcome state invalid")

    if coverage == "PARTIAL_UNRESOLVED":
        if not unresolved:
            raise X02ContractError("V04.1 partial coverage needs unresolved assets")
        expected_semantic = "UNRESOLVED_DAY"
    elif coverage == "COMPLETE":
        if unresolved:
            raise X02ContractError("V04.1 complete coverage cannot retain unresolved assets")
        if chapter_outcomes:
            expected_semantic = "CHAPTER_DAY"
        elif aha_outcomes:
            if len(aha_outcomes) != 1:
                raise X02ContractError("V04.1 Highlight Day requires exactly one Aha")
            expected_semantic = "HIGHLIGHT_DAY"
        else:
            expected_semantic = "EMPTY_DAY"
    else:
        raise X02ContractError("V04.1 coverage status invalid")
    if result.get("semantic_day_state") != expected_semantic:
        raise X02ContractError("V04.1 semantic day state mismatch")

    publishable_ids = {
        str(item.get("memory_type")): {
            str(outcome.get("memory_id"))
            for outcome in outcomes
            if outcome.get("memory_type") == item.get("memory_type")
            and outcome.get("media_state") == "S10_MEDIA_READY"
            and outcome.get("surface_state") in {
                "MODEL_SURFACE_VERIFIED", "DETERMINISTIC_FALLBACK_VERIFIED",
            }
        }
        for item in ({"memory_type": "CHAPTER"}, {"memory_type": "AHA"})
    }
    actual_ids = {
        "CHAPTER": {str(item.get("id")) for item in chapters},
        "AHA": {str(item.get("id")) for item in ahas},
    }
    if actual_ids != publishable_ids:
        raise X02ContractError("V04.1 public memory and outcome identity mismatch")
    diagnostic_run = coverage == "PARTIAL_UNRESOLVED"
    for memory_type, memories in (("CHAPTER", chapters), ("AHA", ahas)):
        for memory in memories:
            expected_publication = (
                "STAGED_PREVIEW_DIAGNOSTIC_ONLY"
                if diagnostic_run else "STAGED_PREVIEW_VALIDATED"
            )
            if memory.get("publication_status") != expected_publication:
                raise X02ContractError("V04.1 memory publication status mismatch")
            matching = [
                item for item in outcomes
                if item.get("memory_type") == memory_type
                and item.get("memory_id") == memory.get("id")
            ]
            expected_visibility = "DIAGNOSTIC_ONLY" if diagnostic_run else "VISIBLE_PREVIEW"
            if len(matching) != 1 or matching[0].get("visibility_state") != expected_visibility:
                raise X02ContractError("V04.1 memory visibility outcome mismatch")

    visible = [item for item in outcomes if item.get("visibility_state") == "VISIBLE_PREVIEW"]
    if diagnostic_run:
        expected_delivery = "PIPELINE_BLOCKED"
    elif not outcomes:
        expected_delivery = "NO_GROUNDED_MEMORY"
    elif len(visible) < len(outcomes):
        expected_delivery = "READY_WITH_ITEM_BLOCKS" if visible else "PIPELINE_BLOCKED"
    elif any(
        item.get("surface_state") == "DETERMINISTIC_FALLBACK_VERIFIED"
        for item in outcomes
    ):
        expected_delivery = "READY_WITH_GROUNDED_COPY_FALLBACK"
    else:
        expected_delivery = "READY_PRIMARY_COPY"
    if result.get("delivery_state") != expected_delivery:
        raise X02ContractError("V04.1 delivery state mismatch")
    expected_output = "PIPELINE_BLOCKED" if expected_delivery == "PIPELINE_BLOCKED" else expected_semantic
    if result.get("output_mode") != expected_output:
        raise X02ContractError("V04.1 output projection mismatch")

    reliability = result.get("time_reliability", {})
    if not isinstance(reliability, Mapping):
        raise X02ContractError("V04.1 time reliability state invalid")
    if (
        result.get("timeline_basis") != "SYNTHETIC_SEQUENCE_ONLY"
        or result.get("timeline_date") is not None
        or dict(reliability) != {
            "capture_time_reliable": False,
            "interval_reliable": False,
            "timezone_reliable": False,
        }
    ):
        raise X02ContractError("V04.1 unverified-time stop-loss mismatch")


def _session_namespace(bundle: ImportedEvidenceBundle) -> uuid.UUID:
    try:
        return uuid.UUID(str(bundle.manifest["session"]["session_id"]))
    except ValueError as exc:
        raise X02ContractError("session.session_id must be a UUID for X02") from exc


def _batches(values: Sequence[Mapping[str, object]], size: int) -> List[List[Mapping[str, object]]]:
    return [list(values[index:index + size]) for index in range(0, len(values), size)]


def _planned_perception_batches(
    bundle: ImportedEvidenceBundle,
    assets: Sequence[Mapping[str, object]],
) -> List[List[Mapping[str, object]]]:
    batches: List[List[Mapping[str, object]]] = []
    current: List[Mapping[str, object]] = []
    current_frames = 0
    current_bytes = 0
    for asset in assets:
        evidence = _perception_evidence(bundle, [asset])
        frame_count = len(evidence)
        evidence_bytes = sum(path.stat().st_size for _, _, path in evidence)
        exceeds = current and (
            len(current) + 1 > PERCEPTION_BATCH_MAX_ASSETS
            or current_frames + frame_count > PERCEPTION_BATCH_MAX_FRAMES
            or current_bytes + evidence_bytes > PERCEPTION_BATCH_MAX_EVIDENCE_BYTES
        )
        if exceeds:
            batches.append(current)
            current = []
            current_frames = 0
            current_bytes = 0
        current.append(asset)
        current_frames += frame_count
        current_bytes += evidence_bytes
    if current:
        batches.append(current)
    return batches


def _manifest_frame_path(bundle: ImportedEvidenceBundle, frame: Mapping[str, object]) -> Path:
    return (bundle.manifest_path.parent / str(frame["relative_path"])).resolve()


def _perception_evidence(
    bundle: ImportedEvidenceBundle,
    assets: Sequence[Mapping[str, object]],
) -> List[Tuple[Mapping[str, object], Mapping[str, object], Path]]:
    selected = []
    for asset in assets:
        frames = sorted(
            asset["frames"],
            key=lambda item: (
                int(item.get("window_index", 0)),
                int(item["canonical_offset_ms"]),
            ),
        )
        if asset["media_kind"] == "PHOTO" and len(frames) > 1:
            frames = [min(frames, key=lambda item: abs(int(item["canonical_offset_ms"]) - 4_500))]
        for frame in frames:
            selected.append((asset, frame, _manifest_frame_path(bundle, frame)))
    return selected


def _evidence_label(asset: Mapping[str, object], frame: Mapping[str, object]) -> str:
    return (
        "Evidence follows. asset_id=%s frame_id=%s media_kind=%s "
        "window_index=%s window_count=%s sample_role=%s "
        "canonical_offset_ms=%s source_timestamp_ms=%s"
        % (
            asset["asset_id"],
            frame["frame_id"],
            asset["media_kind"],
            frame.get("window_index", 0),
            frame.get("window_count", 1),
            frame.get("sample_role", "LEGACY_CANONICAL_SAMPLE"),
            frame["canonical_offset_ms"],
            frame.get("source_timestamp_ms"),
        )
    )


def _evidence_ledger_entry(
    order: int,
    asset: Mapping[str, object],
    frame: Mapping[str, object],
) -> Dict[str, object]:
    return {
        "selection_order": order,
        "asset_id": _app_asset_uuid(str(asset["asset_id"])),
        "source_asset_id": str(asset["asset_id"]),
        "frame_id": str(frame["frame_id"]),
        "media_kind": str(asset["media_kind"]),
        "window_index": int(frame.get("window_index", 0)),
        "window_count": int(frame.get("window_count", 1)),
        "sample_role": str(frame.get("sample_role", "LEGACY_CANONICAL_SAMPLE")),
        "canonical_offset_ms": int(frame["canonical_offset_ms"]),
        "source_timestamp_ms": (
            None if frame.get("source_timestamp_ms") is None
            else int(frame["source_timestamp_ms"])
        ),
        "reason_code": (
            "PHOTO_SINGLE_MIDDLE_FRAME"
            if asset["media_kind"] == "PHOTO"
            else "VIDEO_DURATION_AWARE_WINDOWS"
            if "evidence_window_count" in asset
            else "VIDEO_FIXED_THREE_FRAME_CONTRACT"
        ),
    }


def _perception_prompt(
    assets: Sequence[Mapping[str, object]],
    evidence: Sequence[Tuple[Mapping[str, object], Mapping[str, object], Path]],
    *,
    import_sequence_only: bool = False,
    generic_animal_subjects: bool = False,
    grounded_claims: bool = False,
    representative_fact_frame: bool = False,
) -> str:
    catalog = [{
        "asset_id": asset["asset_id"],
        "frame_id": frame["frame_id"],
        "media_kind": asset["media_kind"],
        "window_index": frame.get("window_index", 0),
        "window_count": frame.get("window_count", 1),
        "sample_role": frame.get("sample_role", "LEGACY_CANONICAL_SAMPLE"),
        "canonical_offset_ms": frame["canonical_offset_ms"],
        "source_timestamp_ms": frame.get("source_timestamp_ms"),
    } for asset, frame, _ in evidence]
    return (
        "You are S04 Observation Lite for a one-day Diary One staged research preview. "
        "Analyze every listed asset independently and return exactly one observation per asset. "
        "Use only visible evidence. Never infer exact place, identity, relationship, emotion, preference, "
        "taste, intent, or causality. A video may use all of its chronologically ordered sampled Windows "
        "to describe visible continuity or change; a photo has one presented frame. Facts must cite only "
        "frame IDs presented for that same asset. "
        "Use the closed setting/activity/episode/subject/event codes in the schema. Every specific Episode "
        "must match at least one clause in the supplied versioned compatibility contract; every field "
        "present in that clause must match, while an omitted field is unconstrained. OTHER and UNKNOWN "
        "remain generic labels for genuinely weak or uncategorized evidence, never fallbacks for repairing "
        "a contradictory specific tuple. Mark a real short event peak only "
        "when an action, interaction, discovery, reaction, result, ceremony, playful-animal action, or food "
        "interaction is visibly supported. DISCOVERY may also describe one concrete, distinctive, "
        "independently memorable visible detail in a still photo, but generic attractive scenery is not "
        "enough. Use concise Chinese "
        "fact text. If evidence is weak, use PARTIAL or INSUFFICIENT_EVIDENCE rather than guessing. "
        + (
            "Across assets, order is input/import sequence only; never infer clock time, elapsed gap, "
            "or real adjacency. Capture time and GPS are not supplied to this perception call. When an "
            "event peak is claimed, include a concise, self-contained fact describing that event. "
            "Fact recording has no Aha copy-length limit; concise presentation belongs to the Writer. "
            "Keep each fact at or below 200 characters when possible. The absolute fact payload limit "
            "is 1000 characters; do not use that safety envelope as permission to be verbose. "
            "Use a subject code only when supported by the visible content; when no specific code fits, "
            "use OTHER and retain the actual observed subject in the fact text. "
            if import_sequence_only else
            "Asset order is chronology, but capture time/GPS may be absent. "
        )
        + (
            "Subject granularity: use ANIMAL for visibly supported non-human animals, "
            "regardless of species. Do not use CAT or DOG subject codes. Keep the specific "
            "observed subject name in facts; a broad code must not replace or rewrite it. "
            "For other subjects without a suitable code, use OTHER rather than guessing "
            "a nearby category. These subject codes are classifications, not extra fact evidence. "
            if generic_animal_subjects else ""
        )
        + (grounded_recording_editor.perception_instruction() if grounded_claims else "")
        + (experience_editor.perception_instruction() if representative_fact_frame else "")
        + "Compatibility contract:\n"
        + (
            "Presented frames use aspect-fit letterboxing to preserve the complete source image. "
            "Plain padding outside the image is not scene content.\n"
            if any(frame.get("spatial_transform") == "ASPECT_FIT_LETTERBOX" for _, frame, _ in evidence)
            else ""
        )
        + json.dumps(_compatibility_prompt_payload(), ensure_ascii=False, sort_keys=True)
        + "\nCatalog:\n"
        + json.dumps(catalog, ensure_ascii=False, sort_keys=True)
    )


def _validate_perception_batch(
    namespace: uuid.UUID,
    expected_assets: Sequence[Mapping[str, object]],
    run: StageRun,
    app_asset_ids: Mapping[str, str],
    *,
    unicode_motifs: bool = False,
    retain_extended_fact_text: bool = False,
    generic_animal_subjects: bool = False,
    representative_fact_frame: bool = False,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    raw = run.output.get("observations") if isinstance(run.output, dict) else None
    if not isinstance(raw, list):
        raise X02ContractError("perception output.observations must be an array")
    expected = {str(asset["asset_id"]): asset for asset in expected_assets}
    presented_by_asset: Dict[str, set] = {asset_id: set() for asset_id in expected}
    for entry in run.selected_evidence:
        source_asset_id = str(entry.get("source_asset_id", ""))
        frame_id = str(entry.get("frame_id", ""))
        if source_asset_id in presented_by_asset:
            presented_by_asset[source_asset_id].add(frame_id)
    raw_by_asset: Dict[str, object] = {}
    duplicate_assets = set()
    extras = []
    for item in raw:
        asset_id = str(item.get("asset_id", "")) if isinstance(item, dict) else ""
        if asset_id not in expected:
            extras.append(asset_id or "<invalid>")
        elif asset_id in raw_by_asset:
            duplicate_assets.add(asset_id)
        else:
            raw_by_asset[asset_id] = item

    observations = []
    ledger = []
    for asset in expected_assets:
        source_asset_id = str(asset["asset_id"])
        item = raw_by_asset.get(source_asset_id)
        if item is None or source_asset_id in duplicate_assets:
            reason = "MISSING_OBSERVATION" if item is None else "DUPLICATE_OBSERVATION"
            observation, audit = _failed_observation(
                namespace,
                asset,
                app_asset_ids[source_asset_id],
                reason,
                "",
                validation_rule_id="X02V03_" + reason,
                json_field_path="$.observations",
            )
        else:
            try:
                observation, degraded_fields = _validated_observation(
                    namespace,
                    asset,
                    item,
                    app_asset_ids[source_asset_id],
                    presented_by_asset[source_asset_id],
                    unicode_motifs=unicode_motifs,
                    retain_extended_fact_text=retain_extended_fact_text,
                    generic_animal_subjects=generic_animal_subjects,
                    representative_fact_frame=representative_fact_frame,
                )
                _, compatibility_rule_id = _episode_compatibility(
                    observation["setting_code"],
                    observation["activity_code"],
                    observation["episode_code"],
                    observation["event_kind"],
                )
                audit = {
                    "source_asset_id": source_asset_id,
                    "observation_id": observation["id"],
                    "validation_status": (
                        "PASSED_WITH_FIELD_DEGRADATION" if degraded_fields else "PASSED"
                    ),
                    "terminal_status": observation["status"],
                    "reason_codes": [
                        "VALID_GROUNDED_FACTS_PRESERVED_WITH_FIELD_DEGRADATION"
                        if degraded_fields else "PER_ASSET_CONTRACT_PASSED"
                    ],
                    "degraded_fields": degraded_fields,
                    "compatibility_rule_id": compatibility_rule_id,
                    "semantic_contract_version": X02_OBSERVATION_COMPATIBILITY_VERSION,
                    "semantic_contract_sha256": X02_OBSERVATION_COMPATIBILITY_SHA256,
                    "field_degradation_contract_version": X02_FIELD_DEGRADATION_VERSION,
                    "field_degradation_contract_sha256": X02_FIELD_DEGRADATION_SHA256,
                }
                if degraded_fields:
                    audit["canonical_candidate_sha256"] = sha256_bytes(canonical_bytes(item))
                if retain_extended_fact_text and any(
                    len(str(fact.get("text", ""))) > PERCEPTION_FACT_CONCISE_TARGET_CHARS
                    for fact in observation["facts"]
                ):
                    audit["reason_codes"].append(
                        "OVER_CONCISE_FACT_TEXT_RETAINED_WITHOUT_SEMANTIC_REWRITE"
                    )
            except (TypeError, ValueError, X02ContractError) as exc:
                validation_rule_id, json_field_path = _observation_rejection_metadata(exc)
                observation, audit = _failed_observation(
                    namespace,
                    asset,
                    app_asset_ids[source_asset_id],
                    "OBSERVATION_CONTRACT_INVALID",
                    str(exc),
                    raw_candidate=item,
                    generic_animal_subjects=generic_animal_subjects,
                    validation_rule_id=validation_rule_id,
                    json_field_path=json_field_path,
                )
        observations.append(observation)
        ledger.append(audit)
    for extra in extras:
        ledger.append({
            "source_asset_id": extra,
            "observation_id": None,
            "validation_status": "REJECTED",
            "terminal_status": "FAILED",
            "reason_codes": ["UNKNOWN_ASSET_REFERENCE"],
            "validation_rule_id": "X02V03_UNKNOWN_ASSET_REFERENCE",
            "json_field_path": "$.observations[*].asset_id",
            "semantic_contract_version": X02_OBSERVATION_COMPATIBILITY_VERSION,
            "semantic_contract_sha256": X02_OBSERVATION_COMPATIBILITY_SHA256,
            "field_degradation_contract_version": X02_FIELD_DEGRADATION_VERSION,
            "field_degradation_contract_sha256": X02_FIELD_DEGRADATION_SHA256,
        })
    return observations, ledger


def _validated_observation(
    namespace: uuid.UUID,
    asset: Mapping[str, object],
    raw: object,
    app_asset_id: str,
    presented_frames: set,
    *,
    unicode_motifs: bool = False,
    retain_extended_fact_text: bool = False,
    generic_animal_subjects: bool = False,
    representative_fact_frame: bool = False,
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    if not isinstance(raw, dict):
        raise X02ContractError("observation must be an object")
    source_asset_id = str(asset["asset_id"])
    degraded_fields: List[Dict[str, object]] = []

    def degrade(path: str, rule_id: str, action: str, sentinel: str) -> None:
        degraded_fields.append({
            "json_field_path": path,
            "validation_rule_id": rule_id,
            "action": action,
            "original_value_sentinel": sentinel,
        })

    raw_status = raw.get("status")
    status = raw_status if isinstance(raw_status, str) and raw_status in OBSERVATION_STATUSES else None
    if status is None:
        degrade(
            "$.observations[*].status",
            "X02V03_STATUS_INVALID",
            "DERIVE_CONSERVATIVE_STATUS_FROM_SURVIVING_FACTS",
            _field_value_sentinel(raw_status, OBSERVATION_STATUSES),
        )
    facts_raw = raw.get("facts")
    if not isinstance(facts_raw, list):
        degrade(
            "$.observations[*].facts",
            "X02V03_FACT_ARRAY_INVALID",
            "TREAT_AS_NO_SURVIVING_FACTS",
            _field_value_sentinel(facts_raw),
        )
        facts_raw = []
    facts = []
    for index, fact_raw in enumerate(facts_raw):
        fact_path = "$.observations[*].facts[%d]" % index
        try:
            if not isinstance(fact_raw, dict):
                raise X02ContractError("fact must be an object")
            text = _bounded_string(
                fact_raw.get("text"),
                1,
                (
                    PERCEPTION_FACT_PAYLOAD_MAX_CHARS
                    if retain_extended_fact_text
                    else PERCEPTION_FACT_CONCISE_TARGET_CHARS
                ),
                "fact.text",
            )
            evidence_frame_ids = _string_list(
                fact_raw.get("evidence_frame_ids"), "fact.evidence_frame_ids"
            )
            if not set(evidence_frame_ids).issubset(presented_frames):
                raise X02ContractError("fact cites evidence not presented for its asset")
            support_grade = _enum(
                fact_raw.get("support_grade"), SUPPORT_GRADES, "fact.support_grade"
            )
        except (TypeError, ValueError, X02ContractError) as exc:
            degrade(
                fact_path,
                "X02V03_INVALID_FACT_DROPPED",
                "DROP_ONLY_INVALID_FACT",
                _fact_failure_sentinel(exc),
            )
            continue
        fact = {
            "fact_id": _stable_id(namespace, "fact:%s:%d" % (source_asset_id, index)),
            "text": text,
            "evidence_frame_ids": evidence_frame_ids,
            "support_grade": support_grade,
        }
        if representative_fact_frame:
            representative = fact_raw.get(experience_editor.REPRESENTATIVE_FRAME_FIELD)
            if not isinstance(representative, str) or representative not in evidence_frame_ids:
                degrade(
                    fact_path + "." + experience_editor.REPRESENTATIVE_FRAME_FIELD,
                    "CODEX_V174_FACT_REPRESENTATIVE_FRAME_INVALID",
                    "RETAIN_FACT_EXCLUDE_FROM_AHA",
                    _field_value_sentinel(representative),
                )
                fact[experience_editor.REPRESENTATIVE_FRAME_FIELD] = None
            else:
                fact[experience_editor.REPRESENTATIVE_FRAME_FIELD] = representative
        facts.append(fact)

    setting_code = _degradable_enum(
        raw.get("setting_code"), SETTING_CODES, "setting_code", "UNKNOWN", degrade
    )
    activity_code = _degradable_enum(
        raw.get("activity_code"), ACTIVITY_CODES, "activity_code", "UNKNOWN", degrade
    )
    episode_code = _degradable_enum(
        raw.get("episode_code"), EPISODE_CODES, "episode_code", "UNKNOWN", degrade
    )
    subject_codes = _degradable_enum_list(
        raw.get("subject_codes"),
        GENERIC_SUBJECT_CODES if generic_animal_subjects else SUBJECT_CODES,
        "subject_codes", degrade,
    )
    motifs = _degradable_motifs(
        raw.get("motifs"),
        degrade,
        unicode_safe=unicode_motifs,
    )
    event_kind = _degradable_enum(
        raw.get("event_kind"), EVENT_KINDS, "event_kind", "NONE", degrade
    )
    event_salience = _degradable_enum(
        raw.get("event_salience"), EVENT_SALIENCE, "event_salience", "NONE", degrade
    )
    if (event_kind == "NONE") != (event_salience == "NONE"):
        degrade(
            "$.observations[*].event_kind|event_salience",
            "X02V03_EVENT_TUPLE_CONTRADICTION",
            "USE_NONE_NONE_WITHOUT_EVENT_INFERENCE",
            "<CONTRADICTORY_CLOSED_VOCABULARY_TUPLE>",
        )
        event_kind, event_salience = "NONE", "NONE"
    compatible, compatibility_rule_id = _episode_compatibility(
        setting_code,
        activity_code,
        episode_code,
        event_kind,
    )
    if not compatible:
        degrade(
            "$.observations[*].episode_code",
            compatibility_rule_id,
            "USE_UNKNOWN_WITHOUT_INFERRING_REPLACEMENT_EPISODE",
            "<CONTRADICTORY_CLOSED_VOCABULARY_TUPLE>",
        )
        episode_code = "UNKNOWN"
        compatibility_rule_id = "X02V02_GENERIC_EPISODE"
    quality_score = _degradable_quality(raw.get("quality_score"), degrade)
    limitations = _degradable_limitations(raw.get("limitations"), degrade)

    if not facts:
        status = "INSUFFICIENT_EVIDENCE"
    elif status not in ("OBSERVED", "PARTIAL"):
        degrade(
            "$.observations[*].status",
            "X02V03_STATUS_FACT_CONTRADICTION",
            "USE_PARTIAL_FOR_SURVIVING_GROUNDED_FACTS",
            "<STATUS_CONTRADICTS_SURVIVING_FACTS>",
        )
        status = "PARTIAL"
    elif degraded_fields and status == "OBSERVED":
        status = "PARTIAL"

    observation = {
        "id": _stable_id(namespace, "observation:%s" % source_asset_id),
        "asset_id": app_asset_id,
        "source_asset_id": source_asset_id,
        "media_kind": str(asset["media_kind"]),
        "status": status,
        "facts": facts,
        "setting_code": setting_code,
        "activity_code": activity_code,
        "episode_code": episode_code,
        "subject_codes": _unique(subject_codes),
        "motifs": _unique(motifs),
        "event_kind": event_kind,
        "event_salience": event_salience,
        "quality_score": quality_score,
        "limitations": limitations,
        "degraded_fields": degraded_fields,
        "evidence_frame_ids": _unique([
            frame_id for fact in facts for frame_id in fact["evidence_frame_ids"]
        ]),
    }
    return observation, degraded_fields


def _field_value_sentinel(value: object, allowed: Optional[frozenset] = None) -> str:
    if value is None:
        return "<MISSING>"
    if allowed is not None and isinstance(value, str) and value not in allowed:
        return "<OUTSIDE_CLOSED_VOCABULARY>"
    if isinstance(value, list):
        return "<ARRAY_WITH_INVALID_ENTRY>"
    if isinstance(value, dict):
        return "<INVALID_OBJECT_VALUE>"
    return "<INVALID_FIELD_TYPE_OR_VALUE>"


def _fact_failure_sentinel(exc: BaseException) -> str:
    message = str(exc)
    if "not presented" in message:
        return "<EVIDENCE_REFERENCE_NOT_PRESENTED>"
    if "support_grade" in message:
        return "<SUPPORT_GRADE_INVALID>"
    if "text" in message:
        return "<FACT_TEXT_INVALID>"
    return "<FACT_SHAPE_INVALID>"


def _degradable_enum(value, allowed, field_name, fallback, degrade):
    if isinstance(value, str) and value in allowed:
        return value
    degrade(
        "$.observations[*].%s" % field_name,
        "X02V03_ENUM_FIELD_INVALID",
        "USE_%s_WITHOUT_SEMANTIC_INFERENCE" % fallback,
        _field_value_sentinel(value, allowed),
    )
    return fallback


def _degradable_enum_list(value, allowed, field_name, degrade) -> List[str]:
    if not isinstance(value, list):
        degrade(
            "$.observations[*].%s" % field_name,
            "X02V03_ENUM_LIST_INVALID",
            "USE_EMPTY_LIST",
            _field_value_sentinel(value),
        )
        return []
    valid = []
    for index, item in enumerate(value[:32]):
        if isinstance(item, str) and item in allowed:
            valid.append(item)
        else:
            degrade(
                "$.observations[*].%s[%d]" % (field_name, index),
                "X02V03_ENUM_LIST_VALUE_DROPPED",
                "DROP_ONLY_INVALID_LIST_ENTRY",
                _field_value_sentinel(item, allowed),
            )
    if len(value) > 32:
        degrade(
            "$.observations[*].%s" % field_name,
            "X02V03_ENUM_LIST_TOO_LARGE",
            "KEEP_FIRST_32_ENTRIES_BEFORE_VALIDATION",
            "<ARRAY_OVER_SAFETY_LIMIT>",
        )
    return _unique(valid)


def _degradable_motifs(value, degrade, *, unicode_safe: bool = False) -> List[str]:
    if not isinstance(value, list):
        degrade(
            "$.observations[*].motifs",
            "X02V03_MOTIF_LIST_INVALID",
            "USE_EMPTY_LIST",
            _field_value_sentinel(value),
        )
        return []
    motifs = []
    for index, item in enumerate(value[:6]):
        normalized = (
            _normalized_motif(item, unicode_safe=unicode_safe)
            if isinstance(item, str) else ""
        )
        if normalized:
            motifs.append(normalized)
        else:
            degrade(
                "$.observations[*].motifs[%d]" % index,
                "X02V03_MOTIF_VALUE_DROPPED",
                "DROP_ONLY_INVALID_MOTIF",
                _field_value_sentinel(item),
            )
    if len(value) > 6:
        degrade(
            "$.observations[*].motifs",
            "X02V03_MOTIF_LIST_TOO_LARGE",
            "KEEP_FIRST_SIX_MOTIFS",
            "<ARRAY_OVER_SAFETY_LIMIT>",
        )
    return _unique(motifs)


def _degradable_quality(value, degrade) -> float:
    if not isinstance(value, bool) and isinstance(value, (int, float)):
        number = float(value)
        if math.isfinite(number) and 0 <= number <= 1:
            return number
    degrade(
        "$.observations[*].quality_score",
        "X02V03_QUALITY_SCORE_INVALID",
        "USE_CONSERVATIVE_PRESENTATION_FLOOR_0_35",
        _field_value_sentinel(value),
    )
    return 0.35


def _degradable_limitations(value, degrade) -> List[str]:
    if not isinstance(value, list):
        degrade(
            "$.observations[*].limitations",
            "X02V03_LIMITATION_LIST_INVALID",
            "USE_EMPTY_LIST",
            _field_value_sentinel(value),
        )
        return []
    limitations = []
    for index, item in enumerate(value[:6]):
        if isinstance(item, str) and 1 <= len(item.strip()) <= 120:
            limitations.append(item.strip())
        else:
            degrade(
                "$.observations[*].limitations[%d]" % index,
                "X02V03_LIMITATION_VALUE_DROPPED",
                "DROP_ONLY_INVALID_LIMITATION",
                _field_value_sentinel(item),
            )
    if len(value) > 6:
        degrade(
            "$.observations[*].limitations",
            "X02V03_LIMITATION_LIST_TOO_LARGE",
            "KEEP_FIRST_SIX_LIMITATIONS",
            "<ARRAY_OVER_SAFETY_LIMIT>",
        )
    return _unique(limitations)


def _observation_rejection_metadata(exc: BaseException) -> Tuple[str, str]:
    if isinstance(exc, X02ObservationContractError):
        return exc.rule_id, exc.json_field_path
    message = str(exc)
    if "fact cites evidence not presented" in message:
        return (
            "X02V03_FACT_EVIDENCE_NOT_PRESENTED",
            "$.observations[*].facts[*].evidence_frame_ids",
        )
    if "accepted observation needs at least one grounded fact" in message:
        return "X02V03_ACCEPTED_OBSERVATION_FACT_REQUIRED", "$.observations[*].facts"
    if "event NONE must have salience NONE" in message:
        return "X02V03_EVENT_SALIENCE_CONTRADICTION", "$.observations[*].event_salience"
    if "non-empty event needs non-NONE salience" in message:
        return "X02V03_EVENT_SALIENCE_REQUIRED", "$.observations[*].event_salience"
    location = message.split(" ", 1)[0]
    if location.startswith("observation."):
        path = "$.observations[*]." + location.removeprefix("observation.")
    elif location.startswith("fact."):
        path = "$.observations[*].facts[*]." + location.removeprefix("fact.")
    else:
        path = "$.observations[*]"
    if "closed vocabulary" in message:
        return "X02V03_ENUM_INVALID", path
    if "must be" in message or "length is invalid" in message:
        return "X02V03_STRUCTURED_FIELD_INVALID", path
    return "X02V03_OBSERVATION_CONTRACT_INVALID", path


def _privacy_safe_enum(value: object, allowed: frozenset) -> object:
    if isinstance(value, str) and value in allowed:
        return value
    if value is None:
        return None
    return "<OUTSIDE_CLOSED_VOCABULARY>"


def _privacy_safe_enum_list(value: object, allowed: frozenset) -> List[object]:
    if not isinstance(value, list):
        return ["<NON_ARRAY_VALUE>"] if value is not None else []
    return [_privacy_safe_enum(item, allowed) for item in value[:32]]


def _rejected_structured_candidate_snapshot(
    raw: object, *, generic_animal_subjects: bool = False,
) -> Optional[Dict[str, object]]:
    if not isinstance(raw, dict):
        return None
    try:
        candidate_sha256 = sha256_bytes(canonical_bytes(raw))
    except (TypeError, ValueError):
        return None
    return {
        "candidate_status": _privacy_safe_enum(raw.get("status"), OBSERVATION_STATUSES),
        "raw_enum_fields": {
            "setting_code": _privacy_safe_enum(raw.get("setting_code"), SETTING_CODES),
            "activity_code": _privacy_safe_enum(raw.get("activity_code"), ACTIVITY_CODES),
            "episode_code": _privacy_safe_enum(raw.get("episode_code"), EPISODE_CODES),
            "subject_codes": _privacy_safe_enum_list(
                raw.get("subject_codes"),
                GENERIC_SUBJECT_CODES if generic_animal_subjects else SUBJECT_CODES,
            ),
            "event_kind": _privacy_safe_enum(raw.get("event_kind"), EVENT_KINDS),
            "event_salience": _privacy_safe_enum(raw.get("event_salience"), EVENT_SALIENCE),
        },
        "canonical_candidate_sha256": candidate_sha256,
        "privacy_contract": "ENUM_FIELDS_AND_CANONICAL_HASH_ONLY_V01",
    }


def _failed_observation(
    namespace: uuid.UUID,
    asset: Mapping[str, object],
    app_asset_id: str,
    reason_code: str,
    detail: str,
    *,
    raw_candidate: object = None,
    generic_animal_subjects: bool = False,
    validation_rule_id: str = "X02V03_OBSERVATION_REJECTED",
    json_field_path: str = "$.observations[*]",
) -> Tuple[Dict[str, object], Dict[str, object]]:
    source_asset_id = str(asset["asset_id"])
    observation_id = _stable_id(namespace, "observation:%s" % source_asset_id)
    observation = {
        "id": observation_id,
        "asset_id": app_asset_id,
        "source_asset_id": source_asset_id,
        "media_kind": str(asset["media_kind"]),
        "status": "FAILED",
        "facts": [],
        "setting_code": "UNKNOWN",
        "activity_code": "UNKNOWN",
        "episode_code": "UNKNOWN",
        "subject_codes": [],
        "motifs": [],
        "event_kind": "NONE",
        "event_salience": "NONE",
        "quality_score": 0.0,
        "limitations": [reason_code],
        "degraded_fields": [],
        "evidence_frame_ids": [],
    }
    audit = {
        "source_asset_id": source_asset_id,
        "observation_id": observation_id,
        "validation_status": "REJECTED",
        "terminal_status": "FAILED",
        "reason_codes": [reason_code],
        "detail": detail[:500],
        "validation_rule_id": validation_rule_id,
        "json_field_path": json_field_path,
        "semantic_contract_version": X02_OBSERVATION_COMPATIBILITY_VERSION,
        "semantic_contract_sha256": X02_OBSERVATION_COMPATIBILITY_SHA256,
        "field_degradation_contract_version": X02_FIELD_DEGRADATION_VERSION,
        "field_degradation_contract_sha256": X02_FIELD_DEGRADATION_SHA256,
    }
    rejected_snapshot = _rejected_structured_candidate_snapshot(
        raw_candidate, generic_animal_subjects=generic_animal_subjects,
    )
    if rejected_snapshot is not None:
        audit["rejected_structured_candidate"] = rejected_snapshot
    return observation, audit


def _failed_batch_observations(
    namespace: uuid.UUID,
    assets: Sequence[Mapping[str, object]],
    app_asset_ids: Mapping[str, str],
    reason_code: str,
    detail: str,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    pairs = [
        _failed_observation(
            namespace,
            asset,
            app_asset_ids[str(asset["asset_id"])],
            reason_code,
            detail,
            validation_rule_id="X02V03_PERCEPTION_OUTPUT_INVALID",
            json_field_path="$.observations",
        )
        for asset in assets
    ]
    return [pair[0] for pair in pairs], [pair[1] for pair in pairs]


def _assign_roles(
    observations: Sequence[Mapping[str, object]],
    *,
    reject_degraded_quality: bool = False,
) -> List[Dict[str, object]]:
    roles = []
    for observation in observations:
        status = observation["status"]
        facts = observation["facts"]
        support = {fact["support_grade"] for fact in facts}
        quality_was_invalid = any(
            field.get("validation_rule_id") == "X02V03_QUALITY_SCORE_INVALID"
            for field in observation.get("degraded_fields", [])
        )
        if status in ("FAILED", "INSUFFICIENT_EVIDENCE"):
            role, reason = "DROP", "NO_ACCEPTED_OBSERVATION_EVIDENCE"
        elif reject_degraded_quality and quality_was_invalid:
            role, reason = "CONTEXT_ONLY", "INVALID_PRESENTATION_QUALITY_PROVENANCE"
        elif observation["quality_score"] < 0.35:
            role, reason = "CONTEXT_ONLY", "BELOW_PRESENTATION_USABILITY_FLOOR"
        elif support and support.issubset({"WEAK"}):
            role, reason = "CONTEXT_ONLY", "WEAK_FACT_SUPPORT_ONLY"
        else:
            role, reason = "KEEP", "GROUNDED_CONTENT_OR_EVENT_EVIDENCE"
        roles.append({
            "observation_id": observation["id"],
            "source_asset_id": observation["source_asset_id"],
            "role": role,
            "reason_code": reason,
        })
    return roles


def _build_boundary_ledger(
    observations: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
) -> List[Dict[str, object]]:
    role_by_id = {item["observation_id"]: item["role"] for item in roles}
    edges = []
    for index in range(len(observations) - 1):
        left, right = observations[index], observations[index + 1]
        continuity = []
        boundary = []
        if left["episode_code"] == right["episode_code"] and left["episode_code"] not in ("UNKNOWN", "OTHER"):
            continuity.append("SAME_EPISODE_CODE")
        if left["setting_code"] == right["setting_code"] and left["setting_code"] != "UNKNOWN":
            continuity.append("SAME_SETTING_CODE")
        if set(left["motifs"]) & set(right["motifs"]):
            continuity.append("SHARED_GROUNDED_MOTIF")
        if left["episode_code"] != right["episode_code"]:
            boundary.append("EPISODE_CODE_CHANGED")
        if left["setting_code"] != right["setting_code"]:
            boundary.append("SETTING_CODE_CHANGED")
        if role_by_id[left["id"]] == "DROP" or role_by_id[right["id"]] == "DROP":
            boundary.append("LOW_EVIDENCE_SIDE")
        if left["episode_code"] in ("UNKNOWN", "OTHER") or right["episode_code"] in ("UNKNOWN", "OTHER"):
            decision, reason = "DEFER", "INSUFFICIENT_CLOSED_SEMANTIC_EVIDENCE"
        elif continuity and not boundary:
            decision, reason = "JOIN", "CONTINUITY_OUTWEIGHS_BOUNDARY"
        else:
            decision, reason = "SPLIT", "BOUNDARY_OUTWEIGHS_CONTINUITY"
        edges.append({
            "edge_id": "edge_%03d_%03d" % (index, index + 1),
            "left_observation_id": left["id"],
            "right_observation_id": right["id"],
            "continuity_evidence": continuity,
            "boundary_evidence": boundary,
            "decision": decision,
            "reason_code": reason,
        })
    return edges


def _build_moments(
    namespace: uuid.UUID,
    observations: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
    edges: Sequence[Mapping[str, object]],
    asset_order: Mapping[str, int],
) -> List[Dict[str, object]]:
    if not observations:
        return []
    groups: List[List[Mapping[str, object]]] = [[observations[0]]]
    for index, edge in enumerate(edges):
        if edge["decision"] == "JOIN":
            groups[-1].append(observations[index + 1])
        else:
            groups.append([observations[index + 1]])
    role_by_id = {item["observation_id"]: item["role"] for item in roles}
    moments = []
    for index, group in enumerate(groups):
        source_asset_ids = [str(item["source_asset_id"]) for item in group]
        observation_ids = [str(item["id"]) for item in group]
        moments.append({
            "id": _stable_id(namespace, "moment:%s" % ",".join(source_asset_ids)),
            "sequence_index": index,
            "observation_ids": observation_ids,
            "asset_ids": [_app_asset_uuid(value) for value in source_asset_ids],
            "source_asset_ids": source_asset_ids,
            "episode_codes": _unique([str(item["episode_code"]) for item in group]),
            "setting_codes": _unique([str(item["setting_code"]) for item in group]),
            "activity_codes": _unique([str(item["activity_code"]) for item in group]),
            "roles": [str(role_by_id[item["id"]]) for item in group],
            "time_label": _sequence_label(
                min(asset_order[value] for value in source_asset_ids),
                max(asset_order[value] for value in source_asset_ids),
            ),
        })
    return moments


def _structure_observations(
    observations: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
) -> List[Dict[str, object]]:
    role_by_id = {item["observation_id"]: item for item in roles}
    return [{
        "observation_id": item["id"],
        "sequence_index": index,
        "role": role_by_id[item["id"]]["role"],
        "setting_code": item["setting_code"],
        "activity_code": item["activity_code"],
        "episode_code": item["episode_code"],
        "subject_codes": item["subject_codes"],
        "motifs": item["motifs"],
        "event_kind": item["event_kind"],
        "event_salience": item["event_salience"],
        "facts": item["facts"],
    } for index, item in enumerate(observations)]




def _storyline_structure_prompt(context: Mapping[str, object]) -> str:
    single_source = context.get(structure_wire.POLICY_FIELD) == structure_wire.POLICY_VERSION
    recording_editor_version = context.get(recording_editor.POLICY_FIELD)
    chapter_only = recording_editor_version == experience_editor.POLICY_VERSION
    joint_selection = recording_editor_version in (
        recording_editor.POLICY_VERSION, grounded_recording_editor.POLICY_VERSION,
        aha_set_editor.POLICY_VERSION,
    )
    experience_first = (
        context.get(chapter_coherence.POLICY_FIELD) == chapter_coherence.POLICY_VERSION
    )
    legacy_theme_instruction = (
        "" if experience_first else
        "A common theme can justify grouping without claiming one continuous outing. "
    )
    allocation_instruction = (
        ("For nominated aha_proposals, consider their relation to the proposed Chapters. Return "
         if joint_selection else
         "For each observation in aha_relation_scope, consider its relation to the proposed Chapters "
         "(including observations for which you do not make a native aha_proposal). Return ")
        + ("aha_relations inside each containing Chapter and inside any other Chapter with a potentially "
           if single_source else
           "chapter_aha_relations for its containing Chapter and any other Chapter with a potentially ")
        +
        "overlapping story; do not enumerate unrelated pairs just to fill a table. "
        + ("Use the exact input observation_id consistently in beat_map, aha_proposals and aha_relations. "
           "Do not invent native Aha keys; relation ownership comes from the containing Chapter object. "
           + ("Consider relations for nominated Ahas; do not enumerate every usable observation. "
              if joint_selection else
              "Check every eligible beat_map member against aha_relation_scope, not only your native Aha list. ")
           if single_source else "Use the Chapter key and exact observation/fact IDs. ")
        +
        "Judge the story each card would tell, not its beat_role or whether an image is shared. "
        "SAME_STORY means the Aha is the Chapter's core, climax, outcome or a restatement of it; "
        "different wording, a tighter crop or a different image alone does not make a separate story. "
        "DISTINCT_STORY requires a concrete separate event or discovery grounded in the given facts; "
        "briefly explain what the Chapter covers and what the Aha adds. This can be inside or outside "
        "Chapter material. Use UNRESOLVED when the material does not support deciding. "
        "For each decided relation cite nonempty chapter_fact_ids from that Chapter and aha_fact_ids "
        "from that observation's approved event facts (and from your native event_fact_ids if proposed). "
        "The relation reason is editorial guidance, not new evidence. Do not omit otherwise valid "
        "Aha candidates merely because a competing Chapter is proposed: final selection handles that. "
        + legacy_theme_instruction +
        "Never invent "
        "arrival, transition, preparation-to-consumption, shared participants or causal progression "
        "to connect images; EVENT_PROGRESSION and beat roles do not prove those relationships. "
        if context.get(editorial_allocation.POLICY_FIELD) == editorial_allocation.POLICY_VERSION else ""
    )
    if recording_editor_version == grounded_recording_editor.POLICY_VERSION:
        allocation_instruction = (
            "This selected-set editor does not use legacy per-Chapter relation lists: return an empty aha_relations "
            "array in every storyline proposal. Put every relation for the actually recommended set "
            "in day_selection.chapter_aha_relations and day_selection.aha_aha_relations, following "
            "the exact closed-matrix contract below. Relation reasons are editorial guidance, not facts. "
        )
    elif recording_editor_version == aha_set_editor.POLICY_VERSION:
        allocation_instruction = (
            "This discovery call does not decide the final Aha set or any selected-set relations. Return an "
            "empty aha_relations array in every storyline proposal. The separate one-pass S09 editor will "
            "compare validated atomic nominations with the technically executable Chapters. "
        )
    elif chapter_only:
        allocation_instruction = (
            "This S07 call is Chapter-only. Return an empty aha_proposals array and an empty "
            "aha_relations array in every storyline proposal. Do not select, rank, focus, or relate "
            "Ahas here. The separate one-pass S09 editor receives every usable supported fact after "
            "the technically executable Chapters are known. "
        )
    return (
        "Organize Diary One's usable material into coherent Chapter candidate groups"
        + (". " if chapter_only else " and Aha proposals. ")
        +
        "Base grouping on the supplied facts and the relationships among the actual material. "
        "Setting, activity, episode, subject and motif labels are descriptive hints, not grouping requirements. "
        "The supplied Moments are organizational context, not mandatory Chapter boundaries. "
        "Shared labels do not prove one experience; different labels do not require separate groups. "
        "A Chapter is a naturally coherent memory that can be expressed in one or two sentences, "
        "not a required plot with a beginning, climax and ending. Different objects may contribute to the "
        "same experience. Propose separate groups when the actual material supports distinct substantial memories, "
        "not to fill a fixed set of topics or meet a count. Compare the proposed groups and avoid redundant stories. "
        "For each group, identify its members and supported facts, explain their common content in thesis, "
        "preserve each member's contribution in beat_map, and describe its distinction from other groups in reason. "
        + ("beat_map is the sole Chapter member/fact list: provide one complete entry per chosen member. "
           "Do not return Chapter-level observation_ids or fact_ids; the program derives those lists. "
           if single_source else "")
        +
        "Use one beat entry per member. A published Chapter needs at least three KEEP observations under "
        "the current display policy; the old two-item display exception is retired. Do not force unrelated material into a group. "
        "storyline_basis and beat_role describe your proposed organization; they are not scene categories. "
        "focus_code is optional legacy metadata and need not be supplied. "
        "The thesis is internal context, not user-visible prose or new evidence. Aim for "
        f"{STORYLINE_THESIS_TARGET_MIN}-{STORYLINE_THESIS_TARGET_MAX} characters as writing guidance, "
        "not a reason to omit a supported group. Do not invent time, location, intent, identity or relationships. "
        "IMPORT_SEQUENCE_ONLY means the order is an editorial index, not verified capture time or real adjacency. "
        + (
            ""
            if chapter_only else
            "Also actively search the full usable scope for grounded ordinary moments and independently memorable discoveries as Ahas. "
            if joint_selection else
            "Also search for visible local event peaks and concrete independently memorable discoveries as Ahas. "
        )
        + (
            ""
            if chapter_only else
            "Aha proposals may come from material inside or outside Chapter groups; do not duplicate a Chapter's core story. "
            "Material left out of Chapters remains available to the Aha search. Return empty arrays when appropriate; "
            "never fill a quota. "
        )
        + "Contract version and hash: "
        + X02_STORYLINE_CONTRACT_VERSION + " / " + X02_STORYLINE_CONTRACT_SHA256
        + ". " + allocation_instruction + chapter_coherence.prompt_instruction(context)
        + (editorial_order.prompt_instruction()
           if context.get(editorial_order.POLICY_FIELD) == editorial_order.POLICY_VERSION else "")
        + (
            experience_editor.prompt_instruction()
            if recording_editor_version == experience_editor.POLICY_VERSION
            else aha_set_editor.prompt_instruction()
            if recording_editor_version == aha_set_editor.POLICY_VERSION
            else grounded_recording_editor.prompt_instruction()
            if recording_editor_version == grounded_recording_editor.POLICY_VERSION
            else recording_editor.prompt_instruction() if joint_selection else ""
        )
        + "Input:\n" + json.dumps(context, ensure_ascii=False)
    )


def _storyline_segments(
    observations: Sequence[Mapping[str, object]],
    asset_order: Mapping[str, int],
) -> List[Dict[str, object]]:
    ordered = sorted(observations, key=lambda item: asset_order[str(item["source_asset_id"])])
    groups: List[List[Mapping[str, object]]] = []
    for observation in ordered:
        if not groups:
            groups.append([observation])
            continue
        previous = asset_order[str(groups[-1][-1]["source_asset_id"])]
        current = asset_order[str(observation["source_asset_id"])]
        if current == previous + 1:
            groups[-1].append(observation)
        else:
            groups.append([observation])
    return [{
        "observation_ids": [str(item["id"]) for item in group],
        "source_asset_ids": [str(item["source_asset_id"]) for item in group],
        "time_label": _sequence_label(
            asset_order[str(group[0]["source_asset_id"])],
            asset_order[str(group[-1]["source_asset_id"])],
        ),
    } for group in groups]


def _storyline_form(
    member_observation_ids: Sequence[str],
    moments: Sequence[Mapping[str, object]],
    segments: Sequence[Mapping[str, object]],
    asset_order: Mapping[str, int],
) -> str:
    member_set = set(member_observation_ids)
    owner_moments = [
        moment for moment in moments if member_set & set(moment["observation_ids"])
    ]
    if len(owner_moments) == 1:
        return "SINGLE"
    if len(segments) == 1:
        return "ADJACENT_GROUP"
    segment_ranges = [(
        asset_order[str(segment["source_asset_ids"][0])],
        asset_order[str(segment["source_asset_ids"][-1])],
    ) for segment in segments]
    largest_interruption = max(
        (
            max(0, right_start - left_end - 1)
            for (_, left_end), (right_start, _) in zip(
                segment_ranges, segment_ranges[1:]
            )
        ),
        default=0,
    )
    if len(segments) == 2 and largest_interruption <= 2:
        return "RESUMED_EPISODE"
    return "LOCAL_EPISODE_GROUP"


def _dominant_episode_code(observations: Sequence[Mapping[str, object]]) -> str:
    counts: Dict[str, int] = {}
    first_index: Dict[str, int] = {}
    for index, observation in enumerate(observations):
        code = str(observation["episode_code"])
        counts[code] = counts.get(code, 0) + 1
        first_index.setdefault(code, index)
    return min(counts, key=lambda value: (-counts[value], first_index[value], value))


def _validate_storyline_beat_map(
    raw_beats: object,
    member_observations: Sequence[Mapping[str, object]],
) -> List[Dict[str, object]]:
    if not isinstance(raw_beats, list):
        raise _GateReject("STORYLINE_BEAT_MAP_INVALID")
    observation_by_id = {str(item["id"]): item for item in member_observations}
    beats: List[Dict[str, object]] = []
    seen = set()
    for raw in raw_beats:
        if not isinstance(raw, dict):
            raise _GateReject("STORYLINE_BEAT_MAP_INVALID")
        observation_id = _bounded_string(raw.get("observation_id"), 1, 200, "beat.observation_id")
        if observation_id not in observation_by_id or observation_id in seen:
            raise _GateReject("STORYLINE_BEAT_MEMBERSHIP_INVALID")
        seen.add(observation_id)
        role = _enum(raw.get("beat_role"), STORYLINE_BEAT_ROLES, "beat.beat_role")
        fact_ids = _unique(_string_list(raw.get("fact_ids"), "beat.fact_ids"))
        available = {
            str(fact["fact_id"]) for fact in observation_by_id[observation_id]["facts"]
        }
        if not fact_ids or not set(fact_ids).issubset(available):
            raise _GateReject("STORYLINE_BEAT_FACT_INVALID")
        contribution = raw.get("contribution")
        if not isinstance(contribution, str):
            raise X02ContractError("beat.contribution must be a string")
        # Explanatory text is not replaced by tags or used as a semantic gate.
        contribution = contribution.strip()
        beats.append({
            "observation_id": observation_id,
            "beat_role": role,
            "fact_ids": fact_ids,
            "contribution": contribution,
        })
    if seen != set(observation_by_id):
        raise _GateReject("STORYLINE_BEAT_COVERAGE_INCOMPLETE")
    return beats


def _compact_storyline_eligible(
    member_observations: Sequence[Mapping[str, object]],
) -> bool:
    """Check the two-member support contract, not their semantic distinctness."""
    policy = X02_STORYLINE_CONTRACT["compact_two_member_policy"]
    return (
        bool(policy["enabled"])
        and len(member_observations) == int(policy["required_member_count"])
        and all(
            any(
                fact.get("support_grade") in policy["allowed_fact_support_grades"]
                for fact in observation.get("facts", [])
            )
            for observation in member_observations
        )
    )


def _storyline_structure_gate(
    member_observations: Sequence[Mapping[str, object]],
    beat_map: Sequence[Mapping[str, object]],
    interruptions: Sequence[str],
    segments: Sequence[Mapping[str, object]],
    member_indices: Sequence[int],
) -> Dict[str, object]:
    """Technical structure only; import-order statistics cannot prove a story."""
    compact_eligible = _compact_storyline_eligible(member_observations)
    count_valid = 3 <= len(member_observations) <= int(
        X02_STORYLINE_CONTRACT["max_content_members"]
    ) or compact_eligible
    beat_valid = len(beat_map) == len(member_observations)
    total_span = max(member_indices) - min(member_indices) if member_indices else 0
    metrics = {
        "member_count": len(member_observations),
        "total_span_in_source_order": total_span,
        "interruption_count": len(interruptions),
        "interruption_ratio": round(len(interruptions) / max(1, total_span + 1), 6),
        "temporal_segment_count": len(segments),
    }
    return {
        "decision": "PASS" if count_valid and beat_valid else "REJECT",
        "validation_scope": "STRUCTURE_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION",
        "reason_codes": [
            "MODEL_GROUPING_NOT_OVERRIDDEN_BY_TAGS_OR_IMPORT_ORDER",
            "MEMBER_COUNT_AND_BEAT_COVERAGE_PASSED" if count_valid and beat_valid
            else "MEMBER_COUNT_OR_BEAT_COVERAGE_FAILED",
        ],
        **metrics,
        "checks": {"compact_eligible": compact_eligible, **metrics},
        # Retain the legacy diagnostic envelope, explicitly without a semantic verdict.
        "split_challenge": {
            "triggered": False,
            "trigger_reason_codes": [],
            "whole_candidate_summary": metrics,
            "partition_alternatives": [],
            "decision": "NOT_PROGRAMMATICALLY_EVALUATED",
            "reason_codes": ["GROUPING_AND_SPLITTING_ASSIGNED_TO_STRUCTURE_MODEL"],
        },
    }


def _build_storyline_candidates(
    namespace: uuid.UUID,
    observations: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
    moments: Sequence[Mapping[str, object]],
    structure_output: Mapping[str, object],
    asset_order: Mapping[str, int],
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    observation_by_id = {str(item["id"]): item for item in observations}
    role_by_id = {str(item["observation_id"]): str(item["role"]) for item in roles}
    all_fact_ids = {
        str(fact["fact_id"]) for item in observations for fact in item["facts"]
    }
    proposals = []
    model_proposals = (
        structure_output.get("storyline_proposals", [])
        if isinstance(structure_output, dict) else []
    )
    if isinstance(model_proposals, list):
        for proposal in model_proposals[:int(X02_STORYLINE_CONTRACT["max_model_storyline_proposals"])]:
            if isinstance(proposal, dict):
                proposals.append({**proposal, "source": "MODEL_STORYLINE_PROPOSAL"})

    candidates: List[Dict[str, object]] = []
    ledger: List[Dict[str, object]] = []
    seen_identity = set()
    max_members = int(X02_STORYLINE_CONTRACT["max_content_members"])
    for source_index, proposal in enumerate(proposals):
        entry: Dict[str, object] = {
            "source_index": source_index,
            "proposal_source": proposal.get("source", "UNKNOWN"),
            "candidate_key": str(proposal.get("key", ""))[:120],
            "validation_status": "REJECTED",
            "selection_status": "NOT_ELIGIBLE",
            "reason_codes": [],
        }
        try:
            raw_focus = proposal.get("focus_code", "")
            focus_code = raw_focus.strip() if isinstance(raw_focus, str) else ""
            storyline_basis = _enum(
                proposal.get("storyline_basis"), STORYLINE_BASES, "storyline.storyline_basis"
            )
            observation_ids = _unique(
                _string_list(proposal.get("observation_ids"), "storyline.observation_ids")
            )
            if not 2 <= len(observation_ids) <= max_members:
                raise _GateReject("STORYLINE_CONTENT_UNIT_COUNT_INVALID")
            if any(value not in observation_by_id for value in observation_ids):
                raise _GateReject("UNKNOWN_OBSERVATION_REFERENCE")
            if any(role_by_id[value] != "KEEP" for value in observation_ids):
                raise _GateReject("NON_KEEP_MEMBER")
            member_observations = sorted(
                [observation_by_id[value] for value in observation_ids],
                key=lambda item: asset_order[str(item["source_asset_id"])],
            )
            entry.update({
                "focus_code": focus_code,
                "storyline_basis": storyline_basis,
                "observation_ids": [str(item["id"]) for item in member_observations],
                "source_asset_ids": [
                    str(item["source_asset_id"]) for item in member_observations
                ],
            })
            member_indices = [
                asset_order[str(item["source_asset_id"])] for item in member_observations
            ]
            supplied_fact_ids = set(
                _string_list(proposal.get("fact_ids"), "storyline.fact_ids")
            )
            member_fact_ids = {
                str(fact["fact_id"])
                for item in member_observations for fact in item["facts"]
            }
            if (
                not supplied_fact_ids
                or not supplied_fact_ids.issubset(all_fact_ids)
                or not supplied_fact_ids.issubset(member_fact_ids)
            ):
                raise _GateReject("STORYLINE_FACT_REFERENCE_INVALID")
            beat_map = _validate_storyline_beat_map(
                proposal.get("beat_map"), member_observations
            )
            beat_fact_ids = {
                fact_id for beat in beat_map for fact_id in beat["fact_ids"]
            }
            # Both the supplied summary's member scope and every per-member
            # beat reference have passed validation. The summary is redundant:
            # derive from the validated beats, never add members or rebind facts.
            entry["fact_summary_audit"] = {
                "supplied_fact_ids": sorted(supplied_fact_ids),
                "validated_beat_fact_ids": sorted(beat_fact_ids),
                "added_from_validated_beats": sorted(beat_fact_ids - supplied_fact_ids),
                "unused_supplied_fact_ids": sorted(supplied_fact_ids - beat_fact_ids),
                "membership_changed": False,
                "fact_text_changed": False,
                "candidate_eligibility_effect": (
                    "REDUNDANT_SUMMARY_OMISSION_REMOVED"
                    if beat_fact_ids - supplied_fact_ids else "NONE"
                ),
            }
            raw_thesis = proposal.get("thesis")
            if not isinstance(raw_thesis, str):
                raise X02ContractError("storyline.thesis must be a string")
            thesis = raw_thesis.strip()
            # Preserve the explanation without using its length to judge the
            # member/fact structure. Empty text is not replaced with a theme.
            entry["thesis"] = thesis
            entry["thesis_field_audit"] = {
                "supplied_text": raw_thesis,
                "character_count": len(thesis),
                "within_length_guidance": (
                    STORYLINE_THESIS_TARGET_MIN <= len(thesis) <= STORYLINE_THESIS_TARGET_MAX
                ),
                "candidate_eligibility_effect": "NONE",
            }
            ordered_ids = tuple(str(item["id"]) for item in member_observations)
            identity = tuple(sorted(ordered_ids))
            if identity in seen_identity:
                raise _GateReject("DUPLICATE_STORYLINE_IDENTITY")
            segments = _storyline_segments(member_observations, asset_order)
            first_index, last_index = min(member_indices), max(member_indices)
            member_id_set = set(ordered_ids)
            interruptions = [
                str(item["id"]) for item in observations
                if first_index < asset_order[str(item["source_asset_id"])] < last_index
                and str(item["id"]) not in member_id_set
            ]
            one_story_gate = _storyline_structure_gate(
                member_observations,
                beat_map,
                interruptions,
                segments,
                member_indices,
            )
            entry["one_story_gate"] = one_story_gate
            if one_story_gate["decision"] != "PASS":
                entry["reason_codes"].extend(
                    code for code in one_story_gate["reason_codes"]
                    if code.endswith("FAILED") or "REJECT" in code
                )
                raise _GateReject("STORYLINE_STRUCTURE_GATE_REJECTED")
            seen_identity.add(identity)
            episode_codes = _unique([str(item["episode_code"]) for item in member_observations])
            candidate_id = _stable_id(
                namespace,
                "storyline-v03-candidate:%s" % ",".join(identity),
            )
            storyline_identity = {
                "contract_version": X02_STORYLINE_CONTRACT_VERSION,
                "storyline_basis": storyline_basis,
                "focus_code": focus_code,
                "thesis": thesis,
                "storyline_form": (
                    "COMPACT_TWO_MEMBER"
                    if one_story_gate["checks"]["compact_eligible"]
                    else _storyline_form(ordered_ids, moments, segments, asset_order)
                ),
                "episode_codes": episode_codes,
                "temporal_segments": segments,
                "interruption_observation_ids": interruptions,
                "beat_map": beat_map,
                "continuity_evidence": [],
                "boundary_evidence": [],
                "one_story_gate": one_story_gate,
            }
            candidate = {
                "candidate_id": candidate_id,
                "candidate_type": "CHAPTER",
                "episode_code": _dominant_episode_code(member_observations),
                "episode_codes": episode_codes,
                "storyline_basis": storyline_basis,
                "focus_code": focus_code,
                "storyline_identity": storyline_identity,
                "observation_ids": list(ordered_ids),
                "source_asset_ids": [str(item["source_asset_id"]) for item in member_observations],
                "fact_ids": sorted(beat_fact_ids),
                "motifs": _unique([motif for item in member_observations for motif in item["motifs"]]),
                "subject_codes": _unique([
                    code for item in member_observations for code in item["subject_codes"]
                ]),
                "setting_codes": _unique([str(item["setting_code"]) for item in member_observations]),
                "activity_codes": _unique([str(item["activity_code"]) for item in member_observations]),
                "quality_mean": round(sum(
                    float(item["quality_score"]) for item in member_observations
                ) / len(member_observations), 6),
                "proposal_source": proposal.get("source", "UNKNOWN"),
                "compact_eligible": bool(
                    one_story_gate["checks"]["compact_eligible"]
                ),
            }
            candidates.append(candidate)
            entry.update({
                "candidate_id": candidate_id,
                "validation_status": "PASSED",
                "selection_status": "ELIGIBLE",
                "reason_codes": [
                    "MODEL_MEMBERSHIP_STRUCTURE_PASSED_NOT_QUALITY_VERIFIED",
                    "BEAT_MAP_COMPLETE",
                    "CANDIDATE_SIZE_%d_NOT_FINAL_MEDIA_COUNT" % len(member_observations),
                ],
                "storyline_basis": storyline_basis,
                "focus_code": focus_code,
                "thesis": thesis,
                "storyline_identity": storyline_identity,
                "model_grouping_reason": proposal.get("reason", ""),
                "episode_codes": episode_codes,
                "observation_ids": list(ordered_ids),
                "source_asset_ids": candidate["source_asset_ids"],
            })
        except _GateReject as exc:
            entry["reason_codes"].append(exc.reason_code)
        except (TypeError, ValueError, X02ContractError) as exc:
            entry["reason_codes"].append("STORYLINE_CONTRACT_INVALID")
            entry["detail"] = str(exc)[:500]
        ledger.append(entry)
    return candidates, ledger


def _storyline_pair_conflict(
    left: Mapping[str, object],
    right: Mapping[str, object],
    asset_order: Mapping[str, int],
) -> Optional[str]:
    # Content relationships belong to the Structure model. The code enforces
    # only the existing no-shared-raw-asset publishing constraint here.
    if set(left["source_asset_ids"]) & set(right["source_asset_ids"]):
        return "CHAPTER_RAW_ASSET_CONFLICT"
    return None


def _storyline_selection_value(
    candidate: Mapping[str, object],
    observation_by_id: Mapping[str, Mapping[str, object]],
) -> Tuple[float, Dict[str, float]]:
    selected_fact_ids = set(candidate.get("fact_ids", []))
    selected_facts = [
        fact
        for observation_id in candidate.get("observation_ids", [])
        for fact in observation_by_id[str(observation_id)].get("facts", [])
        if str(fact.get("fact_id")) in selected_fact_ids
    ]
    support_points = {"STRONG": 1.0, "MODERATE": 0.65, "WEAK": 0.2}
    support = (
        sum(support_points.get(str(fact.get("support_grade")), 0.0) for fact in selected_facts)
        / len(selected_facts)
        if selected_facts else 0.0
    )
    member_count = len(candidate.get("observation_ids", []))
    member_depth = min(1.0, member_count / 5.0)
    if candidate.get("compact_eligible"):
        member_depth = max(member_depth, 0.7)
    beat_roles = {
        str(beat.get("beat_role"))
        for beat in candidate.get("storyline_identity", {}).get("beat_map", [])
    }
    beat_diversity = min(1.0, len(beat_roles) / 4.0)
    quality = float(candidate.get("quality_mean", 0.0))
    value = 0.4 * quality + 0.3 * support + 0.2 * member_depth + 0.1 * beat_diversity
    inputs = {
        "trusted_quality_mean": round(quality, 6),
        "fact_support_mean": round(support, 6),
        "member_depth": round(member_depth, 6),
        "beat_role_diversity": round(beat_diversity, 6),
        "storyline_value": round(value, 6),
    }
    return round(value, 6), inputs


def _select_storyline_set(
    candidates: Sequence[Mapping[str, object]],
    ledger: List[Dict[str, object]],
    observations: Sequence[Mapping[str, object]],
    asset_order: Mapping[str, int],
    *,
    editorial_priority: Optional[Mapping[str, object]] = None,
) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    if editorial_order.applied(editorial_priority):
        return editorial_order.select_chapters(
            candidates, ledger, asset_order, editorial_priority,
            minimum=chapter_display.MIN_MEDIA, maximum=MAX_CHAPTERS,
            pair_conflict=_storyline_pair_conflict,
        )
    observation_by_id = {str(item["id"]): item for item in observations}
    candidate_values: Dict[str, float] = {}
    rank_inputs: Dict[str, Dict[str, float]] = {}
    for candidate in candidates:
        candidate_id = str(candidate["candidate_id"])
        value, inputs = _storyline_selection_value(candidate, observation_by_id)
        candidate_values[candidate_id] = value
        rank_inputs[candidate_id] = inputs
        candidate["selection_value"] = value
        candidate["selection_rank_inputs"] = inputs
    thresholds = (0.52, 0.56, 0.60, 0.72)
    eligible = [
        candidate for candidate in candidates
        if candidate_values[str(candidate["candidate_id"])] >= thresholds[0]
        and len(candidate["source_asset_ids"]) >= chapter_display.MIN_MEDIA
    ]
    best_combo: Tuple[Mapping[str, object], ...] = ()
    best_objective = (0.0, 0.0, 0, 0, ())
    evaluated = 0
    pair_ledger: List[Dict[str, object]] = []
    conflict_by_pair: Dict[Tuple[str, str], str] = {}
    for index, left in enumerate(eligible):
        for right in eligible[index + 1:]:
            conflict = _storyline_pair_conflict(left, right, asset_order)
            left_id, right_id = str(left["candidate_id"]), str(right["candidate_id"])
            key = tuple(sorted((left_id, right_id)))
            if conflict:
                conflict_by_pair[key] = conflict
            pair_ledger.append({
                "candidate_a_id": left_id,
                "candidate_b_id": right_id,
                "same_memory_evidence": [],
                "distinct_memory_evidence": [],
                "reason_codes": [conflict or "NO_SHARED_ASSET_NOT_PROOF_OF_STORY_INDEPENDENCE"],
                "selection_effect": "FORBID_COSELECT" if conflict else "ALLOW_COSELECT",
            })
    for count in range(0, min(MAX_CHAPTERS, len(eligible)) + 1):
        for combo in itertools.combinations(eligible, count):
            evaluated += 1
            candidate_ids = [str(candidate["candidate_id"]) for candidate in combo]
            if any(
                tuple(sorted((left, right))) in conflict_by_pair
                for index, left in enumerate(candidate_ids)
                for right in candidate_ids[index + 1:]
            ):
                continue
            values = sorted(
                (candidate_values[str(candidate["candidate_id"])] for candidate in combo),
                reverse=True,
            )
            if any(value < thresholds[index] for index, value in enumerate(values)):
                continue
            quality = sum(float(candidate["quality_mean"]) for candidate in combo)
            beat_roles = {
                str(beat["beat_role"])
                for candidate in combo
                for beat in candidate["storyline_identity"]["beat_map"]
            }
            covered = {
                str(asset_id) for candidate in combo for asset_id in candidate["source_asset_ids"]
            }
            order_key = tuple(
                min(asset_order[str(value)] for value in candidate["source_asset_ids"])
                for candidate in combo
            )
            marginal_utility = sum(
                value - thresholds[index] for index, value in enumerate(values)
            )
            objective = (
                round(marginal_utility, 6),
                round(quality, 6),
                len(beat_roles),
                len(covered),
                tuple(-value for value in order_key),
            )
            if objective > best_objective:
                best_combo, best_objective = combo, objective
    selected_ids = {str(candidate["candidate_id"]) for candidate in best_combo}
    for entry in ledger:
        candidate_id = str(entry.get("candidate_id", ""))
        if entry["validation_status"] != "PASSED":
            continue
        if candidate_id in selected_ids:
            entry["selection_status"] = "SELECTED"
            entry["reason_codes"].append("SELECTED_BY_EXISTING_VALUE_FORMULA_NOT_QUALITY_VERIFIED")
        else:
            entry["selection_status"] = "NOT_SELECTED"
            conflicts = [
                value for pair, value in conflict_by_pair.items()
                if candidate_id in pair and any(selected in pair for selected in selected_ids)
            ]
            if len(entry.get("source_asset_ids", [])) < chapter_display.MIN_MEDIA:
                entry["reason_codes"].append("CHAPTER_DISPLAY_NEEDS_THREE_MATERIALS")
            elif candidate_values.get(candidate_id, 0.0) < thresholds[0]:
                entry["reason_codes"].append("BELOW_MINIMUM_STORYLINE_VALUE")
            else:
                entry["reason_codes"].append(
                    conflicts[0] if conflicts else "LOWER_INDEPENDENT_STORYLINE_VALUE"
                )
        entry["selection_rank_inputs"] = rank_inputs.get(candidate_id, {})
    selected = sorted(
        [dict(candidate) for candidate in best_combo],
        key=lambda candidate: min(
            asset_order[str(value)] for value in candidate["source_asset_ids"]
        ),
    )
    return selected, {
        "algorithm": "STORYLINE_V03_MODEL_GROUPS_BOUNDED_SET_SEARCH",
        **({"editorial_order": copy.deepcopy(editorial_priority)}
           if editorial_priority is not None else {}),
        "search_status": "EXACT_WITHIN_PREVIEW_POLICY",
        "evaluated_set_count": evaluated,
        "eligible_candidate_count": len(eligible),
        "candidate_input_truncated": False,
        "selected_candidate_ids": [str(item["candidate_id"]) for item in selected],
        "pair_ledger": pair_ledger,
        "objective_order": [
            "MODEL_PROPOSED_STRUCTURE_VALID_CANDIDATES_ONLY",
            "MINIMUM_VALUE_AND_POSITION_THRESHOLDS",
            "TOTAL_MARGINAL_STORYLINE_VALUE",
            "TRUSTED_QUALITY_MEAN",
            "BEAT_ROLE_DIVERSITY",
            "ASSET_COVERAGE_TELEMETRY_ONLY",
            "DETERMINISTIC_ORDER_TIEBREAK",
        ],
        "objective": {
            "marginal_storyline_value": best_objective[0],
            "quality_mean_sum": best_objective[1],
            "beat_role_diversity": best_objective[2],
            "covered_asset_count_telemetry": best_objective[3],
        },
        "position_value_thresholds": list(thresholds),
        "candidate_rank_inputs": rank_inputs,
        "target_note": "Three to four Chapters is a quality target, never an output quota.",
    }


def _structure_prompt(context: Mapping[str, object]) -> str:
    return (
        "You are a bounded S05-S07 proposal helper. You receive already validated chronological "
        "Observations and deterministic contiguous Moments. Propose optional Chapter groupings and Aha "
        "events; deterministic code will validate every proposal. Do not rewrite facts or codes. A Chapter "
        "is a coherent episode, may contain more than five candidate observations, and normally needs at "
        "least three KEEP observations. Historic architecture and stone lanes can share HISTORIC_TOWN_WALK. "
        "A forest scene cannot support that episode merely because it also contains stone. A short cafe stop "
        "between two historic-town runs does not force the two town runs into separate Chapters; propose the "
        "resumed town episode using only the observations that support it. Do not add the cafe observation to "
        "that Chapter unless its episode code truly matches. Search both Aha paths: a visible local Event "
        "peak, and a concrete distinctive Discovery that can be independently memorable even in a still "
        "photo. Generic attractive scenery is not enough. An Aha must never repeat the same story duty as "
        "its enclosing Chapter. "
        "Reference only supplied observation_id and fact_id values. Returning empty arrays is valid. Input:\n"
        + json.dumps(context, ensure_ascii=False)
    )


def _build_chapter_candidates(
    namespace: uuid.UUID,
    observations: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
    moments: Sequence[Mapping[str, object]],
    structure_output: Mapping[str, object],
    asset_order: Mapping[str, int],
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    observation_by_id = {str(item["id"]): item for item in observations}
    role_by_id = {str(item["observation_id"]): str(item["role"]) for item in roles}
    fact_ids = {
        str(fact["fact_id"])
        for item in observations
        for fact in item["facts"]
    }
    proposals = []
    for episode_code, group in _deterministic_episode_groups(observations, role_by_id, asset_order):
        proposals.append({
            "source": "DETERMINISTIC_EPISODE_GROUP",
            "key": "det_%s_%s" % (episode_code.lower(), group[0]["source_asset_id"]),
            "observation_ids": [item["id"] for item in group],
            "episode_code": episode_code,
            "fact_ids": [fact["fact_id"] for item in group for fact in item["facts"]],
            "reason": "Closed semantic episode group with bounded interruption resume.",
        })
    model_proposals = structure_output.get("chapter_proposals", []) if isinstance(structure_output, dict) else []
    if isinstance(model_proposals, list):
        for proposal in model_proposals:
            if isinstance(proposal, dict):
                proposals.append({**proposal, "source": "MODEL_STRUCTURE_PROPOSAL"})

    candidates = []
    ledger = []
    seen_identity = set()
    for source_index, proposal in enumerate(proposals):
        entry = {
            "source_index": source_index,
            "proposal_source": proposal.get("source", "UNKNOWN"),
            "candidate_key": str(proposal.get("key", ""))[:120],
            "validation_status": "REJECTED",
            "selection_status": "NOT_ELIGIBLE",
            "reason_codes": [],
        }
        try:
            episode_code = _enum(proposal.get("episode_code"), EPISODE_CODES, "chapter.episode_code")
            observation_ids = _unique(_string_list(proposal.get("observation_ids"), "chapter.observation_ids"))
            if len(observation_ids) < 3:
                raise _GateReject("CHAPTER_NEEDS_AT_LEAST_THREE_CONTENT_UNITS")
            if any(value not in observation_by_id for value in observation_ids):
                raise _GateReject("UNKNOWN_OBSERVATION_REFERENCE")
            member_observations = [observation_by_id[value] for value in observation_ids]
            if any(role_by_id[value] != "KEEP" for value in observation_ids):
                raise _GateReject("NON_KEEP_MEMBER")
            if any(item["episode_code"] != episode_code for item in member_observations):
                raise _GateReject("SEMANTIC_MEMBER_COHERENCE_FAILED")
            supplied_fact_ids = set(_string_list(proposal.get("fact_ids"), "chapter.fact_ids"))
            if not supplied_fact_ids or not supplied_fact_ids.issubset(fact_ids):
                raise _GateReject("FACT_REFERENCE_INVALID")
            member_fact_ids = {
                fact["fact_id"] for item in member_observations for fact in item["facts"]
            }
            if not supplied_fact_ids.issubset(member_fact_ids):
                raise _GateReject("FACT_OUTSIDE_CANDIDATE_MEMBERSHIP")
            ordered = sorted(member_observations, key=lambda item: asset_order[item["source_asset_id"]])
            identity = (episode_code, tuple(item["id"] for item in ordered))
            if identity in seen_identity:
                raise _GateReject("DUPLICATE_CANDIDATE_IDENTITY")
            seen_identity.add(identity)
            candidate_id = _stable_id(namespace, "chapter-candidate:%s:%s" % (
                episode_code, ",".join(item["source_asset_id"] for item in ordered)
            ))
            candidate = {
                "candidate_id": candidate_id,
                "candidate_type": "CHAPTER",
                "episode_code": episode_code,
                "observation_ids": [item["id"] for item in ordered],
                "source_asset_ids": [item["source_asset_id"] for item in ordered],
                "fact_ids": _unique([fact["fact_id"] for item in ordered for fact in item["facts"]]),
                "motifs": _unique([motif for item in ordered for motif in item["motifs"]]),
                "subject_codes": _unique([code for item in ordered for code in item["subject_codes"]]),
                "setting_codes": _unique([item["setting_code"] for item in ordered]),
                "activity_codes": _unique([item["activity_code"] for item in ordered]),
                "proposal_source": proposal.get("source", "UNKNOWN"),
            }
            candidates.append(candidate)
            entry.update({
                "candidate_id": candidate_id,
                "validation_status": "PASSED",
                "selection_status": "ELIGIBLE",
                "reason_codes": [
                    "MEMBER_SUPPORT_COMPLETE",
                    "EPISODE_COHERENCE_PASSED",
                    "CANDIDATE_SIZE_%d_NOT_FINAL_MEDIA_COUNT" % len(ordered),
                ],
                "episode_code": episode_code,
                "observation_ids": candidate["observation_ids"],
                "source_asset_ids": candidate["source_asset_ids"],
            })
        except _GateReject as exc:
            entry["reason_codes"].append(exc.reason_code)
        except (TypeError, ValueError, X02ContractError) as exc:
            entry["reason_codes"].append("CANDIDATE_CONTRACT_INVALID")
            entry["detail"] = str(exc)[:500]
        ledger.append(entry)
    return candidates, ledger


def _deterministic_episode_groups(
    observations: Sequence[Mapping[str, object]],
    role_by_id: Mapping[str, str],
    asset_order: Mapping[str, int],
) -> List[Tuple[str, List[Mapping[str, object]]]]:
    by_episode: Dict[str, List[Mapping[str, object]]] = {}
    for item in observations:
        if role_by_id[item["id"]] != "KEEP" or item["episode_code"] in ("UNKNOWN", "OTHER", "TRANSIT"):
            continue
        by_episode.setdefault(str(item["episode_code"]), []).append(item)
    groups = []
    for episode_code, items in by_episode.items():
        ordered = sorted(items, key=lambda item: asset_order[item["source_asset_id"]])
        current = [ordered[0]]
        for item in ordered[1:]:
            previous_index = asset_order[current[-1]["source_asset_id"]]
            current_index = asset_order[item["source_asset_id"]]
            if current_index - previous_index <= 2:
                current.append(item)
            else:
                if len(current) >= 3:
                    groups.append((episode_code, current))
                current = [item]
        if len(current) >= 3:
            groups.append((episode_code, current))
    groups.sort(key=lambda pair: asset_order[pair[1][0]["source_asset_id"]])
    return groups


def _supported_aha_fact_ids(observation: Mapping[str, object]) -> List[str]:
    """Return supported proposal facts; words and categories do not prove event linkage.

    The existing Structure model may nominate a narrower event scope. This
    fallback scope is a proposal only, not a semantic-quality verdict.
    """
    return _unique([
        str(fact["fact_id"])
        for fact in observation.get("facts", [])
        if isinstance(fact.get("fact_id"), str)
        and fact["fact_id"]
        and str(fact.get("support_grade")) in {"STRONG", "MODERATE"}
    ])


def _build_aha_candidates(
    namespace: uuid.UUID,
    observations: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
    moments: Sequence[Mapping[str, object]],
    structure_output: Mapping[str, object],
    asset_order: Mapping[str, int],
    *,
    value_first: bool = False,
    evidence_nominations_only: bool = False,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    if evidence_nominations_only and not value_first:
        raise X02ContractError("Evidence nomination scope requires the supported-fact research path")
    observation_by_id = {str(item["id"]): item for item in observations}
    role_by_id = {str(item["observation_id"]): str(item["role"]) for item in roles}
    moment_by_observation = {
        observation_id: moment["id"]
        for moment in moments
        for observation_id in moment["observation_ids"]
    }
    deterministic_proposals = []
    for item in (() if evidence_nominations_only else observations):
        event_eligible = item["event_salience"] == "HIGH" or (
            item["event_salience"] == "MEDIUM" and item["event_kind"] in PEAK_EVENT_KINDS
        )
        event_fact_ids = (
            _supported_aha_fact_ids(item) if value_first
            else [fact["fact_id"] for fact in item["facts"]]
        )
        if role_by_id[item["id"]] == "KEEP" and event_eligible and event_fact_ids:
            deterministic_proposals.append({
                "source": "DETERMINISTIC_EVENT_PEAK",
                "key": "event_%s" % item["source_asset_id"],
                "observation_id": item["id"],
                "event_fact_ids": event_fact_ids,
                "narrative_duty": item["event_kind"],
            })
    validated_model_proposals = []
    model_proposals = structure_output.get("aha_proposals", []) if isinstance(structure_output, dict) else []
    if isinstance(model_proposals, list):
        for proposal in model_proposals:
            if isinstance(proposal, dict):
                validated_model_proposals.append({**proposal, "source": "MODEL_STRUCTURE_PROPOSAL"})
    proposals = (
        validated_model_proposals + deterministic_proposals
        if value_first else deterministic_proposals + validated_model_proposals
    )

    candidates = []
    ledger = []
    candidate_by_observation: Dict[str, Dict[str, object]] = {}
    for source_index, proposal in enumerate(proposals):
        entry = {
            "source_index": source_index,
            "proposal_source": proposal.get("source", "UNKNOWN"),
            "candidate_key": str(proposal.get("key", ""))[:120],
            "validation_status": "REJECTED",
            "selection_status": "NOT_ELIGIBLE",
            "reason_codes": [],
        }
        try:
            observation_id = _bounded_string(proposal.get("observation_id"), 1, 200, "aha.observation_id")
            if observation_id not in observation_by_id:
                raise _GateReject("UNKNOWN_OBSERVATION_REFERENCE")
            observation = observation_by_id[observation_id]
            if role_by_id[observation_id] != "KEEP":
                raise _GateReject("NON_KEEP_MEMBER")
            if not evidence_nominations_only and observation["event_kind"] not in PEAK_EVENT_KINDS:
                raise _GateReject("EVENT_KIND_NOT_INDEPENDENT_PEAK")
            if not evidence_nominations_only and observation["event_salience"] not in ("MEDIUM", "HIGH"):
                raise _GateReject("EVENT_SALIENCE_TOO_LOW")
            supplied_fact_ids = set(_string_list(proposal.get("event_fact_ids"), "aha.event_fact_ids"))
            fact_by_id = {
                str(fact["fact_id"]): fact for fact in observation.get("facts", [])
            }
            member_fact_ids = set(fact_by_id)
            if not supplied_fact_ids or not supplied_fact_ids.issubset(member_fact_ids):
                raise _GateReject("EVENT_FACT_REFERENCE_INVALID")
            linked_fact_ids = (
                {
                    fact_id for fact_id in supplied_fact_ids
                    if str(fact_by_id[fact_id].get("support_grade"))
                    in {"STRONG", "MODERATE"}
                }
                if value_first and proposal.get("source") == "MODEL_STRUCTURE_PROPOSAL"
                else supplied_fact_ids
            )
            if not linked_fact_ids:
                raise _GateReject("EVENT_FACT_SUPPORT_TOO_WEAK")
            if observation_id in candidate_by_observation:
                existing = candidate_by_observation[observation_id]
                entry["alias_of_candidate_id"] = existing["candidate_id"]
                if value_first and existing["proposal_source"] != "MODEL_STRUCTURE_PROPOSAL":
                    merged_fact_ids = sorted(
                        set(existing["fact_ids"]) | linked_fact_ids
                    )
                    existing["fact_ids"] = merged_fact_ids
                    existing["event_fact_ids"] = merged_fact_ids
                    existing["fact_support_grades"] = [
                        str(fact_by_id[value].get("support_grade", "WEAK"))
                        for value in merged_fact_ids
                    ]
                    entry["merged_fact_ids"] = merged_fact_ids
                    raise _GateReject("MERGED_SAME_OBSERVATION_AHA_PROPOSAL")
                raise _GateReject("DUPLICATE_AHA_EVENT")
            raw_narrative_duty = proposal.get("narrative_duty")
            if value_first:
                if not isinstance(raw_narrative_duty, str) or not raw_narrative_duty.strip():
                    raise X02ContractError("aha.narrative_duty must be a non-empty string")
                # An editorial explanation is not evidence or a quality score.
                # Preserve its content; do not reject the event for verbosity.
                narrative_duty = raw_narrative_duty.strip()
                entry["narrative_duty_field_audit"] = {
                    "supplied_text": raw_narrative_duty,
                    "character_count": len(narrative_duty),
                    "within_legacy_length_limit": len(narrative_duty) <= AHA_NARRATIVE_DUTY_LEGACY_MAX,
                    "candidate_eligibility_effect": "NONE",
                    "semantic_status": "EDITORIAL_HINT_NOT_FACT_EVIDENCE",
                }
            else:
                narrative_duty = _bounded_string(
                    raw_narrative_duty, 1, AHA_NARRATIVE_DUTY_LEGACY_MAX, "aha.narrative_duty"
                )
            candidate_id = _stable_id(namespace, "aha-candidate:%s" % observation["source_asset_id"])
            candidate_facts = [fact_by_id[value] for value in sorted(linked_fact_ids)]
            candidate = {
                "candidate_id": candidate_id,
                "candidate_type": "AHA",
                "observation_id": observation_id,
                "moment_id": moment_by_observation[observation_id],
                "source_asset_id": observation["source_asset_id"],
                "fact_ids": sorted(linked_fact_ids),
                "event_fact_ids": sorted(linked_fact_ids),
                "event_kind": observation["event_kind"],
                "event_salience": observation["event_salience"],
                "episode_code": observation["episode_code"],
                "narrative_duty": narrative_duty,
                "proposal_source": proposal.get("source", "UNKNOWN"),
                "subject_codes": list(observation.get("subject_codes", [])),
                "motifs": list(observation.get("motifs", [])),
                "quality_score": float(observation.get("quality_score", 0.0)),
                "fact_support_grades": [
                    str(fact.get("support_grade", "WEAK")) for fact in candidate_facts
                ],
            }
            candidates.append(candidate)
            candidate_by_observation[observation_id] = candidate
            entry.update({
                "candidate_id": candidate_id,
                "validation_status": "PASSED",
                "selection_status": "ELIGIBLE",
                "reason_codes": ["SUPPORTED_MODEL_NOMINATION_NOT_QUALITY_VERIFIED"
                                 if evidence_nominations_only else "INDEPENDENT_LOCAL_EVENT_PEAK_SUPPORTED"],
                "observation_id": observation_id,
                "source_asset_id": observation["source_asset_id"],
                "event_kind": observation["event_kind"],
                "event_salience": observation["event_salience"],
                "proposal_aliases": [],
            })
        except _GateReject as exc:
            entry["reason_codes"].append(exc.reason_code)
        except (TypeError, ValueError, X02ContractError) as exc:
            entry["reason_codes"].append("AHA_CONTRACT_INVALID")
            entry["detail"] = str(exc)[:500]
        ledger.append(entry)
    accepted_by_id = {
        str(entry.get("candidate_id")): entry
        for entry in ledger if entry.get("validation_status") == "PASSED"
    }
    for entry in ledger:
        alias_id = entry.get("alias_of_candidate_id")
        if alias_id in accepted_by_id:
            accepted_by_id[str(alias_id)].setdefault("proposal_aliases", []).append({
                "proposal_source": entry.get("proposal_source"),
                "candidate_key": entry.get("candidate_key"),
                "reason_code": "SAME_OBSERVATION_PROPOSAL_ALIAS",
            })
    return candidates, ledger


def _select_chapter_set(
    candidates: Sequence[Mapping[str, object]],
    ledger: List[Dict[str, object]],
    observations: Sequence[Mapping[str, object]],
    asset_order: Mapping[str, int],
) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    observation_by_id = {str(item["id"]): item for item in observations}
    eligible = list(candidates)[:16]
    best_combo: Tuple[Mapping[str, object], ...] = ()
    best_objective = (-1, -1, -1, -1.0, ())
    evaluated = 0
    for count in range(0, min(MAX_CHAPTERS, len(eligible)) + 1):
        for combo in itertools.combinations(eligible, count):
            evaluated += 1
            asset_sets = [set(candidate["source_asset_ids"]) for candidate in combo]
            if any(left & right for index, left in enumerate(asset_sets) for right in asset_sets[index + 1:]):
                continue
            covered = set().union(*asset_sets) if asset_sets else set()
            episode_diversity = len({candidate["episode_code"] for candidate in combo})
            quality = sum(
                float(observation_by_id[observation_id]["quality_score"])
                for candidate in combo
                for observation_id in candidate["observation_ids"]
            )
            order_key = tuple(
                min(asset_order[value] for value in candidate["source_asset_ids"])
                for candidate in combo
            )
            objective = (len(covered), episode_diversity, len(combo), round(quality, 6), tuple(-value for value in order_key))
            if objective > best_objective:
                best_combo, best_objective = combo, objective
    selected_ids = {candidate["candidate_id"] for candidate in best_combo}
    for entry in ledger:
        candidate_id = entry.get("candidate_id")
        if entry["validation_status"] != "PASSED":
            continue
        if candidate_id in selected_ids:
            entry["selection_status"] = "SELECTED"
            entry["reason_codes"].append("MAXIMIZES_SET_COVERAGE_DISTINCTNESS")
        else:
            entry["selection_status"] = "NOT_SELECTED"
            entry["reason_codes"].append("LOWER_SET_LEVEL_INCREMENTAL_VALUE_OR_CONFLICT")
    selected = sorted(
        [dict(candidate) for candidate in best_combo],
        key=lambda candidate: min(asset_order[value] for value in candidate["source_asset_ids"]),
    )
    return selected, {
        "algorithm": "DETERMINISTIC_BOUNDED_SET_SEARCH",
        "evaluated_set_count": evaluated,
        "eligible_candidate_count": len(eligible),
        "selected_candidate_ids": [item["candidate_id"] for item in selected],
        "objective": {
            "covered_asset_count": best_objective[0],
            "episode_diversity": best_objective[1],
            "chapter_count": best_objective[2],
            "quality_tiebreak_sum": best_objective[3],
        },
        "target_note": "Three to four Chapters is a product target, never an output quota.",
    }


def _aha_rank_inputs(
    candidate: Mapping[str, object],
    candidates: Sequence[Mapping[str, object]],
    selected_chapters: Sequence[Mapping[str, object]],
) -> Dict[str, float]:
    salience = 1.0 if candidate.get("event_salience") == "HIGH" else 0.65
    support_points = {"STRONG": 1.0, "MODERATE": 0.65, "WEAK": 0.2}
    support_values = [
        support_points.get(str(value), 0.0)
        for value in candidate.get("fact_support_grades", [])
    ]
    support = sum(support_values) / len(support_values) if support_values else 0.0
    # Specificity is earned only by the validated closed event code. Free model
    # prose in narrative_duty is never a ranking signal.
    event_kind = str(candidate.get("event_kind", "")).strip()
    specificity = 1.0 if event_kind in PEAK_EVENT_KINDS else 0.5
    motifs = set(candidate.get("motifs", []))
    if motifs:
        novelty = sum(
            1.0 / max(1, sum(motif in set(other.get("motifs", [])) for other in candidates))
            for motif in motifs
        ) / len(motifs)
    else:
        subjects = set(candidate.get("subject_codes", []))
        novelty = (
            sum(
                1.0 / max(
                    1,
                    sum(bool(subjects & set(other.get("subject_codes", []))) for other in candidates),
                )
                for _ in subjects
            ) / len(subjects)
            if subjects else 0.0
        )
    return {
        "event_salience": round(salience, 6),
        "fact_support": round(support, 6),
        "event_specificity": round(specificity, 6),
        "novelty": round(novelty, 6),
        "presentation_quality_tiebreak": round(float(candidate.get("quality_score", 0.0)), 6),
    }


def _aha_pair_conflict(
    left: Mapping[str, object],
    right: Mapping[str, object],
    asset_order: Mapping[str, int],
) -> Optional[str]:
    # Keep asset_order in the call interface, but import proximity and shared
    # broad categories cannot establish that different assets depict one event.
    if (
        left.get("observation_id") == right.get("observation_id")
        or left.get("source_asset_id") == right.get("source_asset_id")
    ):
        return "SAME_OBSERVATION_AHA_DUPLICATE"
    left_motifs = set(left.get("motifs", []))
    right_motifs = set(right.get("motifs", []))
    if left.get("event_kind") == right.get("event_kind") == "DISCOVERY" and left_motifs and right_motifs:
        overlap = len(left_motifs & right_motifs) / max(1, len(left_motifs | right_motifs))
        if overlap >= 0.67:
            return "HIGH_MOTIF_OVERLAP_DISCOVERY_POTENTIAL_CONFLICT"
    return None


def _aha_chapter_conflict(
    candidate: Mapping[str, object],
    chapter: Mapping[str, object],
) -> Optional[str]:
    if candidate.get("source_asset_id") not in set(chapter.get("source_asset_ids", [])):
        return None
    # An event category or an automatically assigned beat cannot establish
    # narrative ownership. Only reuse of facts explicitly assigned by the
    # existing Structure model to a Chapter climax/result is checked here.
    if chapter.get("proposal_source") != "MODEL_STORYLINE_PROPOSAL":
        return None
    event_fact_ids = set(candidate.get("event_fact_ids", candidate.get("fact_ids", [])))
    beats = chapter.get("storyline_identity", {}).get("beat_map", [])
    core_fact_ids = {
        fact_id
        for beat in beats
        if beat.get("beat_role") in {"PEAK", "RESULT"}
        for fact_id in beat.get("fact_ids", [])
    }
    if event_fact_ids and event_fact_ids <= core_fact_ids:
        return "SAME_MODEL_ASSIGNED_CHAPTER_CORE_FACTS"
    # No match means this limited check found no ownership evidence. It does
    # not prove that the two stories are independent.
    return None


def _select_aha_set(
    candidates: Sequence[Mapping[str, object]],
    ledger: List[Dict[str, object]],
    selected_chapters: Sequence[Mapping[str, object]],
    observations: Sequence[Mapping[str, object]],
    asset_order: Mapping[str, int],
    *,
    value_first: bool = False,
    allocation_plan: Optional[Mapping[str, object]] = None,
    editorial_priority: Optional[Mapping[str, object]] = None,
) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    if not value_first:
        selected = []
        rejection_by_id = {}
        for candidate in sorted(candidates, key=lambda item: asset_order[item["source_asset_id"]]):
            overlapping = [
                chapter for chapter in selected_chapters
                if candidate["source_asset_id"] in chapter["source_asset_ids"]
            ]
            if overlapping and any(
                chapter["episode_code"] == "BIRTHDAY_GATHERING"
                and candidate["event_kind"] in ("CEREMONY", "RESULT")
                for chapter in overlapping
            ):
                rejection_by_id[candidate["candidate_id"]] = "OWNED_BY_CHAPTER_NARRATIVE_CLIMAX"
                continue
            if len(selected) >= MAX_AHAS:
                rejection_by_id[candidate["candidate_id"]] = "AHA_PREVIEW_CAPACITY_REACHED"
                continue
            selected.append(dict(candidate))
        selected_ids = {candidate["candidate_id"] for candidate in selected}
        for entry in ledger:
            candidate_id = entry.get("candidate_id")
            if entry["validation_status"] != "PASSED":
                continue
            if candidate_id in selected_ids:
                entry["selection_status"] = "SELECTED"
                entry["reason_codes"].append("INDEPENDENT_EVENT_PEAK_SELECTED")
            else:
                entry["selection_status"] = "NOT_SELECTED"
                entry["reason_codes"].append(
                    rejection_by_id.get(candidate_id, "LOWER_SET_LEVEL_INCREMENTAL_VALUE")
                )
        event_candidate_count = sum(1 for item in candidates if item["event_kind"] != "DISCOVERY")
        discovery_candidate_count = sum(1 for item in candidates if item["event_kind"] == "DISCOVERY")
        return selected, {
            "algorithm": "NARRATIVE_INDEPENDENCE_THEN_BOUNDED_SET",
            "search_contract": "EVENT_AND_DISCOVERY_AHA_PATHS_V01",
            "search_outcome": "GROUNDED_AHA_SELECTED" if selected else "NO_GROUNDED_AHA_AFTER_SEARCH",
            "event_candidate_count": event_candidate_count,
            "discovery_candidate_count": discovery_candidate_count,
            "eligible_candidate_count": len(candidates),
            "selected_candidate_ids": [item["candidate_id"] for item in selected],
            "rejections": rejection_by_id,
            "target_note": "Historical V03 selection semantics.",
        }

    observation_by_id = {str(item["id"]): item for item in observations}
    model_ordered = editorial_order.applied(editorial_priority)
    rank_inputs = {
        str(candidate["candidate_id"]): _aha_rank_inputs(
            candidate, candidates, selected_chapters
        )
        for candidate in candidates
    } if not model_ordered else {
        cid: {"editorial_priority": index + 1}
        for index, cid in enumerate(editorial_priority["ranked_candidate_ids"])
    }
    rank_fields = (
        "event_salience",
        "fact_support",
        "event_specificity",
        "novelty",
        "presentation_quality_tiebreak",
    )
    ranked = sorted(
        candidates,
        key=lambda item: (
            asset_order[str(item["source_asset_id"])], str(item["candidate_id"])
        ),
    )
    if model_ordered:
        ranked.sort(key=lambda item: rank_inputs[str(item["candidate_id"])]["editorial_priority"])
        rank_fields = ("editorial_priority",)
    else:
        ranked.sort(
            key=lambda item: tuple(
                rank_inputs[str(item["candidate_id"])][field] for field in rank_fields
            ),
            reverse=True,
        )
    selected = []
    rejection_by_id: Dict[str, str] = {}
    suppressed_by: Dict[str, str] = {}
    pair_ledger: List[Dict[str, object]] = []
    chapter_conflicts: List[Dict[str, object]] = []
    chapter_relations: List[Dict[str, object]] = []
    max_selected = 1 if not selected_chapters else MAX_AHAS
    for candidate in ranked:
        candidate_id = str(candidate["candidate_id"])
        overlapping = [
            chapter for chapter in selected_chapters
            if candidate["source_asset_id"] in chapter["source_asset_ids"]
        ]
        chapter_conflict = next(
            (
                (chapter, conflict)
                for chapter in overlapping
                for conflict in [_aha_chapter_conflict(candidate, chapter)]
                if conflict
            ),
            None,
        ) if allocation_plan is None else None
        if allocation_plan is not None:
            # The model's explicit fact-bound allocation replaces the legacy
            # PEAK/RESULT proxy. Missing decisions are visible uncertainty,
            # not positive proof of independence or an extra rejection gate.
            for chapter in selected_chapters:
                relation = editorial_allocation.for_selection(
                    allocation_plan, str(chapter["candidate_id"]), candidate_id,
                )
                chapter_relations.append(copy.deepcopy(relation))
                if relation["relation"] == "SAME_STORY" and chapter_conflict is None:
                    chapter_conflict = (chapter, "SAME_MODEL_ALLOCATED_CHAPTER_STORY")
        if chapter_conflict is not None:
            chapter, conflict = chapter_conflict
            rejection_by_id[candidate_id] = conflict
            chapter_conflicts.append({
                "aha_candidate_id": candidate_id,
                "chapter_candidate_id": str(chapter["candidate_id"]),
                "reason_code": conflict,
                "selection_effect": "SUPPRESS_AHA_ONLY",
            })
            continue
        conflicting = None
        for chosen in selected:
            conflict = _aha_pair_conflict(candidate, chosen, asset_order)
            exact_duplicate = conflict == "SAME_OBSERVATION_AHA_DUPLICATE"
            relation = (
                "EXACT_DUPLICATE"
                if exact_duplicate
                else "UNRESOLVED_POTENTIAL_CONFLICT" if conflict
                else "NO_CONFLICT_EVIDENCE"
            )
            pair_ledger.append({
                "candidate_a_id": candidate_id,
                "candidate_b_id": str(chosen["candidate_id"]),
                "relation": relation,
                "same_memory_evidence": [conflict] if conflict else [],
                # Absence of same-peak evidence is not positive proof that two
                # candidates are distinct memories.
                "distinct_memory_evidence": [],
                "selection_effect": (
                    "FORBID_COSELECT" if exact_duplicate
                    else "AT_MOST_ONE" if conflict else "ALLOW_COSELECT"
                ),
                "reason_codes": [conflict or "NO_CONFLICT_EVIDENCE_ALLOW_COSELECT"],
            })
            if conflict and conflicting is None:
                conflicting = (chosen, conflict)
        if conflicting is not None:
            chosen, conflict = conflicting
            rejection_by_id[candidate_id] = conflict
            suppressed_by[candidate_id] = str(chosen["candidate_id"])
            continue
        if len(selected) >= max_selected:
            rejection_by_id[candidate_id] = "AHA_PREVIEW_CAPACITY_REACHED"
            continue
        selected.append(dict(candidate))
    selected_membership_ids = [str(item["candidate_id"]) for item in selected]
    selected.sort(key=lambda item: (
        asset_order[str(item["source_asset_id"])], str(item["candidate_id"])
    ))
    selected_ids = {str(candidate["candidate_id"]) for candidate in selected}
    for entry in ledger:
        candidate_id = str(entry.get("candidate_id", ""))
        if entry["validation_status"] != "PASSED":
            continue
        entry["rank_inputs"] = rank_inputs.get(candidate_id, {})
        if candidate_id in selected_ids:
            entry["selection_status"] = "SELECTED"
            entry["reason_codes"].append(
                "MODEL_EDITORIAL_PRIORITY_AHA_SELECTED_RELATION_STATUS_RECORDED" if model_ordered else
                "VALUE_RANKED_AHA_SELECTED_RELATION_STATUS_RECORDED"
                if allocation_plan is not None else "VALUE_RANKED_INDEPENDENT_AHA_SELECTED"
            )
        else:
            entry["selection_status"] = "NOT_SELECTED"
            entry["reason_codes"].append(
                rejection_by_id.get(candidate_id, "LOWER_SET_LEVEL_INCREMENTAL_VALUE")
            )
            if candidate_id in suppressed_by:
                entry["suppressed_by_candidate_id"] = suppressed_by[candidate_id]
    event_candidate_count = sum(
        1 for item in candidates if item["event_kind"] != "DISCOVERY"
    )
    discovery_candidate_count = sum(
        1 for item in candidates if item["event_kind"] == "DISCOVERY"
    )
    search_outcome = (
        "GROUNDED_AHA_SELECTED"
        if selected else "NO_GROUNDED_AHA_AFTER_SEARCH"
    )
    return selected, {
        "algorithm": ("MODEL_EDITORIAL_PRIORITY_RELATION_AWARE_AHA_SELECTION" if model_ordered
                      else "V04_1_AHA_LEXICOGRAPHIC_RELATION_AWARE_SET_SELECTION"),
        **({"editorial_order": copy.deepcopy(editorial_priority)}
           if editorial_priority is not None else {}),
        "search_contract": "EVENT_AND_DISCOVERY_AHA_PATHS_V02",
        "pair_conflict_policy_version": X02_AHA_PAIR_CONFLICT_POLICY_VERSION,
        "search_outcome": search_outcome,
        "event_candidate_count": event_candidate_count,
        "discovery_candidate_count": discovery_candidate_count,
        "eligible_candidate_count": len(candidates),
        "rank_fields": list(rank_fields),
        "ranked_candidate_ids": [str(item["candidate_id"]) for item in ranked],
        "candidate_rank_inputs": rank_inputs,
        "selected_candidate_ids": selected_membership_ids,
        "published_sequence_candidate_ids": [item["candidate_id"] for item in selected],
        "publication_order_basis": "IMPORT_SEQUENCE_INDEX_THEN_CANDIDATE_ID_NOT_CHRONOLOGY",
        "membership_order_separate_from_output_order": True,
        "pair_ledger": pair_ledger,
        "chapter_conflicts": chapter_conflicts,
        "chapter_relations": chapter_relations,
        "editorial_allocation_policy_version": (
            editorial_allocation.POLICY_VERSION if allocation_plan is not None else None
        ),
        "rejections": rejection_by_id,
        "suppressed_by_candidate_id": suppressed_by,
        "target_note": (
            "One to two Ahas is the ordinary quality target and two to three is the rich-day target. "
            "Zero requires the explicit audited no-grounded-candidate outcome; no fabrication quota is enforced."
        ),
    }


def _select_chapter_media(
    candidate: Mapping[str, object],
    observations: Sequence[Mapping[str, object]],
    app_asset_ids: Mapping[str, str],
    asset_order: Mapping[str, int],
    display_selection: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    observation_by_id = {str(item["id"]): item for item in observations}
    members = [observation_by_id[value] for value in candidate["observation_ids"]]
    members.sort(key=lambda item: asset_order[item["source_asset_id"]])
    if display_selection is not None:
        selected_ids = display_selection["selected_observation_ids"]
        selected = [observation_by_id[value] for value in selected_ids]
        hero = selected[0]
        selected.sort(key=lambda item: asset_order[item["source_asset_id"]])
        return {
            "candidate_id": candidate["candidate_id"],
            "candidate_content_unit_count": len(members),
            "final_media_count": len(selected),
            "hero_asset_id": app_asset_ids[hero["source_asset_id"]],
            "media": [_media_item(item, app_asset_ids, "HERO" if item["id"] == hero["id"] else "SUPPORT") for item in selected],
            "display_selection": dict(display_selection),
            "reason_codes": ["THREE_TO_FIVE_DISPLAY_ONLY_MEMBERSHIP_PRESERVED", str(display_selection["selection_source"])],
        }
    target_count = min(5, len(members))
    hero = max(
        members,
        key=lambda item: (
            item["quality_score"],
            len(item["subject_codes"]),
            -abs(asset_order[item["source_asset_id"]] - asset_order[members[len(members) // 2]["source_asset_id"]]),
        ),
    )
    selected = []
    for item in (members[0], hero, members[-1]):
        if item not in selected:
            selected.append(item)
    while len(selected) < target_count:
        selected_ids = {item["id"] for item in selected}
        selected_motifs = {motif for item in selected for motif in item["motifs"]}
        selected_subjects = {code for item in selected for code in item["subject_codes"]}
        candidate_item = max(
            (item for item in members if item["id"] not in selected_ids),
            key=lambda item: (
                len(set(item["motifs"]) - selected_motifs) + len(set(item["subject_codes"]) - selected_subjects),
                min(abs(asset_order[item["source_asset_id"]] - asset_order[other["source_asset_id"]]) for other in selected),
                item["quality_score"],
                -asset_order[item["source_asset_id"]],
            ),
        )
        selected.append(candidate_item)
    selected.sort(key=lambda item: asset_order[item["source_asset_id"]])
    media = [_media_item(item, app_asset_ids, "HERO" if item["id"] == hero["id"] else "SUPPORT") for item in selected]
    return {
        "candidate_id": candidate["candidate_id"],
        "candidate_content_unit_count": len(members),
        "final_media_count": len(media),
        "hero_asset_id": app_asset_ids[hero["source_asset_id"]],
        "media": media,
        "reason_codes": [
            "QUALITY_DIVERSITY_TIMELINE_SPREAD",
            "CANDIDATE_MEMBERSHIP_REDUCED_ONLY_AT_S10",
        ],
    }


def _select_aha_media(
    candidate: Mapping[str, object],
    observations: Sequence[Mapping[str, object]],
    app_asset_ids: Mapping[str, str],
) -> Dict[str, object]:
    observation = next(item for item in observations if item["id"] == candidate["observation_id"])
    evidence_frame_ids = candidate.get("moment_evidence_frame_ids")
    return {
        "candidate_id": candidate["candidate_id"],
        "final_media_count": 1,
        "media": [_media_item(
            observation, app_asset_ids, "CORE",
            evidence_frame_ids=evidence_frame_ids if isinstance(evidence_frame_ids, list) else None,
        )],
        "reason_codes": [
            "ATOMIC_FACT_EVIDENCE_MEDIA" if isinstance(evidence_frame_ids, list)
            else "SINGLE_EVENT_PEAK_MEDIA"
        ],
    }


def _media_item(
    observation: Mapping[str, object],
    app_asset_ids: Mapping[str, str],
    role: str,
    evidence_frame_ids: Optional[Sequence[str]] = None,
) -> Dict[str, object]:
    return {
        "asset_id": app_asset_ids[observation["source_asset_id"]],
        "source_asset_id": observation["source_asset_id"],
        "observation_id": observation["id"],
        "role": role,
        "media_kind": observation["media_kind"],
        "preview_format": "PHOTO_EVIDENCE",
        "evidence_frame_ids": (
            list(evidence_frame_ids)
            if evidence_frame_ids is not None else observation["evidence_frame_ids"]
        ),
        "quality_score": observation["quality_score"],
        "motifs": observation["motifs"],
    }


def _writer_context(
    chapters: Sequence[Mapping[str, object]],
    ahas: Sequence[Mapping[str, object]],
    chapter_media: Mapping[str, Mapping[str, object]],
    aha_media: Mapping[str, Mapping[str, object]],
    observations: Sequence[Mapping[str, object]],
    storyline_v04: bool = False,
    grounded_editor_v2: bool = False,
) -> Dict[str, object]:
    observation_by_id = {str(item["id"]): item for item in observations}
    memories = []
    for candidate in chapters:
        selected_observation_ids = {
            str(item["observation_id"])
            for item in chapter_media[candidate["candidate_id"]]["media"]
        }
        allowed_fact_ids = set(candidate.get("fact_ids", []))
        facts = [
            fact
            for observation_id in candidate["observation_ids"]
            if not storyline_v04 or observation_id in selected_observation_ids
            for fact in observation_by_id[observation_id]["facts"]
            if not storyline_v04 or fact["fact_id"] in allowed_fact_ids
        ]
        memory = {
            "candidate_id": candidate["candidate_id"],
            "memory_type": "CHAPTER",
            "episode_code": candidate["episode_code"],
            "facts": facts,
            "selected_media": chapter_media[candidate["candidate_id"]]["media"],
        }
        if storyline_v04:
            memory["storyline_identity"] = candidate["storyline_identity"]
        if grounded_editor_v2:
            memory["evidence_cautions"] = _unique([
                str(value)
                for observation_id in selected_observation_ids
                for value in observation_by_id[observation_id].get("limitations", [])
                if isinstance(value, str) and value.strip()
            ])
        memories.append(memory)
    for candidate in ahas:
        observation = observation_by_id[candidate["observation_id"]]
        memory = {
            "candidate_id": candidate["candidate_id"],
            "memory_type": "AHA",
            "event_kind": candidate["event_kind"],
            "narrative_duty": candidate["narrative_duty"],
            "episode_code": candidate["episode_code"],
            "event_fact_ids": list(candidate.get("event_fact_ids", candidate["fact_ids"])),
            "facts": [
                fact for fact in observation["facts"] if fact["fact_id"] in candidate["fact_ids"]
            ],
            "selected_media": aha_media[candidate["candidate_id"]]["media"],
        }
        if grounded_editor_v2:
            memory["moment_focus"] = candidate.get("moment_focus")
            memory["evidence_cautions"] = _unique([
                str(value) for value in observation.get("limitations", [])
                if isinstance(value, str) and value.strip()
            ])
        memories.append(memory)
    context: Dict[str, object] = {"locale": "zh-Hans", "memories": memories}
    if storyline_v04:
        context["writer_grounding_policy"] = X02_WRITER_GROUNDING_POLICY
    return context


def _writer_retry_context(
    context: Mapping[str, object],
    invalid_ids: Sequence[str],
    writer_audit: Sequence[Mapping[str, object]],
) -> Dict[str, object]:
    invalid_set = set(invalid_ids)
    retry_context = {
        "locale": context["locale"],
        "memories": [item for item in context["memories"] if item["candidate_id"] in invalid_set],
        "previous_failures": [item for item in writer_audit if item["candidate_id"] in invalid_set],
    }
    if "writer_grounding_policy" in context:
        retry_context["writer_grounding_policy"] = context["writer_grounding_policy"]
    if context.get(content_handoff.POLICY_FIELD) == content_handoff.POLICY_VERSION:
        retry_context[content_handoff.POLICY_FIELD] = content_handoff.POLICY_VERSION
    if writer_exit.enabled(context):
        retry_context[writer_exit.POLICY_FIELD] = context[writer_exit.POLICY_FIELD]
    if grounded_recording_editor.writer_enabled(context):
        retry_context[grounded_recording_editor.WRITER_POLICY_FIELD] = (
            context[grounded_recording_editor.WRITER_POLICY_FIELD]
        )
    if context.get(editorial_allocation.POLICY_FIELD) == editorial_allocation.POLICY_VERSION:
        retry_context[editorial_allocation.POLICY_FIELD] = editorial_allocation.POLICY_VERSION
        retry_context["editorial_allocation"] = editorial_allocation.project(
            context.get("editorial_allocation", {}), retry_context["memories"],
        )
    return retry_context


def _writer_fallback_ids(
    context: Mapping[str, object],
    narratives: Mapping[str, Mapping[str, object]],
) -> List[str]:
    """Grounded Ahas fail closed; deterministic prose is never their exit."""
    return [
        str(item["candidate_id"])
        for item in context.get("memories", [])
        if str(item["candidate_id"]) not in narratives
        and not (
            grounded_recording_editor.writer_enabled(context)
            and item.get("memory_type") == "AHA"
        )
    ]


def _writer_prompt(context: Mapping[str, object], retry: bool) -> str:
    if grounded_recording_editor.writer_enabled(context):
        return grounded_recording_editor.writer_prompt(context, limits={
            "title_min": CHAPTER_TITLE_VISIBLE_MIN,
            "title_target": CHAPTER_TITLE_VISIBLE_TARGET_MAX,
            "title_max": CHAPTER_TITLE_VISIBLE_HARD_MAX,
            "chapter_target": CHAPTER_STORY_PREVIEW_TARGET_VISIBLE_MAX,
            "aha_max": grounded_recording_editor.AHA_VISIBLE_MAX,
        })
    if (context.get(content_handoff.POLICY_FIELD) == content_handoff.POLICY_VERSION
            or writer_exit.soft_length_enabled(context)):
        return content_handoff.writer_prompt(context, retry=retry, limits={
            "title_min": CHAPTER_TITLE_VISIBLE_MIN,
            "title_target": CHAPTER_TITLE_VISIBLE_TARGET_MAX,
            "title_max": CHAPTER_TITLE_VISIBLE_HARD_MAX,
            "chapter_target": CHAPTER_STORY_PREVIEW_TARGET_VISIBLE_MAX,
            "aha_max": AHA_MOMENT_LINE_VISIBLE_MAX,
        })
    retry_note = (
        "This is the only bounded repair attempt. Correct every listed validation failure. "
        "The previous_failures entries give the exact draft, measured visible-character count, "
        "sentence count, and applicable target for each item. Rewrite only those supplied items. "
        if retry else ""
    )
    natural_policy = context.get("writer_grounding_policy") == X02_WRITER_GROUNDING_POLICY
    style_note = (
        "Summarize and paraphrase the supplied facts naturally; verbatim copying is not required. "
        "Choose a concise title from this memory's actual content. Restrained expressive language may "
        "reflect visible actions and atmosphere, for any subject or setting. Do not turn that tone into "
        "a claim about the user's unobserved feelings, preferences, intentions, or personal history. "
        "The internal storyline thesis is organizational context, not additional fact evidence. "
        "If it is empty, use the supplied facts and member/beat structure without inventing a missing theme. "
        if natural_policy else
        "Do not use 最爱、难忘、幸福、好吃、惊喜、悠闲 or 开心 without protected user evidence "
        "(none is supplied here). "
    )
    return (
        "You are the bounded S11 Writer for Diary One zh-Hans testing. " + retry_note
        + "Write only from the approved facts supplied for each memory. Reference the fact_id values "
        "actually used; do not create claims. Never add a place, identity, relationship, taste judgment, "
        "intent, cause, dialogue, or event absent from those facts. " + style_note
        + "For a Chapter, title must be "
        f"{CHAPTER_TITLE_VISIBLE_MIN}-{CHAPTER_TITLE_VISIBLE_TARGET_MAX} visible Chinese characters, with "
        f"{CHAPTER_TITLE_VISIBLE_TARGET_MAX + 1}-{CHAPTER_TITLE_VISIBLE_HARD_MAX} allowed only when necessary; "
        "text is one concise natural sentence by default and at most two restrained sentences only when the "
        "second adds materially distinct approved information. Aim for at most "
        f"{CHAPTER_STORY_PREVIEW_TARGET_VISIBLE_MAX} visible characters when natural; this is a writing "
        "target, not a reason to truncate text. Keep the title and sentence centered on the supplied "
        "storyline_identity and actual facts, rather than listing everything in the broader Day Episode. "
        "Avoid exhaustive fact recaps, semicolon inventories, and mechanical descriptions of the writing itself. "
        "For an Aha, title is a short internal label and text is the sole user-visible moment line: one sentence, "
        f"at most {AHA_MOMENT_LINE_VISIBLE_MAX} visible characters, centered on the single event. "
        "Use the event_fact_ids to select the facts supporting that moment. Rewrite a long fact concisely "
        "without changing its meaning; do not omit the item merely because the source fact is long. "
        "For length counting, every Chinese character, Latin letter, digit, and punctuation mark counts; "
        "whitespace does not. Count the Aha line before returning it and rewrite it if it exceeds the limit. "
        "Chapter and Aha must carry different story duties. Return one item for every supplied memory "
        "and no others. Input:\n"
        + json.dumps(context, ensure_ascii=False)
    )


def _fallback_source_bindings(
    text: str,
    claim_ids: Sequence[str],
    memory: Mapping[str, object],
    context: Optional[Mapping[str, object]] = None,
) -> Optional[List[Dict[str, str]]]:
    """Verify mechanical fallback copying, not the semantics of model prose."""
    if len(claim_ids) != 1:
        return None
    for fact in memory.get("facts", []):
        if str(fact.get("fact_id")) != claim_ids[0]:
            continue
        copied = _grounded_fallback_clause(
            fact.get("text"),
            visible_max=(AHA_MOMENT_LINE_VISIBLE_MAX
                         if memory.get("memory_type") == "AHA"
                         and not writer_exit.soft_length_enabled(context or {}) else None),
        )
        if copied == text:
            return [{"claim_id": claim_ids[0], "source_match": "COMPLETE_APPROVED_FACT"}]
    return None


def _validate_writer_output(
    output: Mapping[str, object],
    context: Mapping[str, object],
    attempt: int = 1,
    *,
    surface_source: str = "MODEL_WRITER",
) -> Tuple[Dict[str, Dict[str, object]], List[Dict[str, object]], List[str]]:
    expected = {str(item["candidate_id"]): item for item in context["memories"]}
    output, normalization_notes = writer_exit.normalize_buckets(output, context)
    raw_items = []
    if isinstance(output, dict):
        for key, memory_type in (("chapters", "CHAPTER"), ("ahas", "AHA")):
            values = output.get(key, [])
            if isinstance(values, list):
                raw_items.extend((value, memory_type) for value in values)
    raw_by_id: Dict[str, Tuple[object, str]] = {}
    duplicates = set()
    for raw, memory_type in raw_items:
        candidate_id = str(raw.get("candidate_id", "")) if isinstance(raw, dict) else ""
        if candidate_id in raw_by_id:
            duplicates.add(candidate_id)
        else:
            raw_by_id[candidate_id] = (raw, memory_type)
    narratives = {}
    audit = []
    invalid = []
    for candidate_id, memory in expected.items():
        entry = {
            "candidate_id": candidate_id,
            "memory_type": memory["memory_type"],
            "attempt": attempt,
            "surface_source": surface_source,
            "surface_policy_version": X02_WRITER_SURFACE_POLICY_VERSION,
            "validation_status": "REJECTED",
            "reason_codes": [],
        }
        if writer_exit.enabled(context):
            entry[writer_exit.POLICY_FIELD] = context[writer_exit.POLICY_FIELD]
        entry.update(normalization_notes.get(candidate_id, {}))
        try:
            pair = raw_by_id.get(candidate_id)
            if pair is None:
                raise _GateReject("WRITER_ITEM_MISSING")
            if candidate_id in duplicates:
                raise _GateReject("WRITER_ITEM_DUPLICATED")
            raw, reported_type = pair
            if reported_type != memory["memory_type"]:
                raise _GateReject("WRITER_MEMORY_TYPE_MISMATCH")
            if not isinstance(raw, dict):
                raise _GateReject("WRITER_ITEM_INVALID")
            title_value = raw.get("title")
            text_value = raw.get("text")
            if isinstance(title_value, str):
                title = title_value.strip()
                entry["draft_title"] = title[:WRITER_AUDIT_TEXT_MAX]
                entry["title_visible_characters"] = _visible_length(title)
            else:
                raise _GateReject("WRITER_TITLE_NOT_STRING")
            if isinstance(text_value, str):
                text = text_value.strip()
                entry["draft_text"] = text[:WRITER_AUDIT_TEXT_MAX]
                entry["text_visible_characters"] = _visible_length(text)
                entry["sentence_count"] = _sentence_count(text)
            else:
                raise _GateReject("WRITER_TEXT_NOT_STRING")
            if not title:
                raise _GateReject("WRITER_TITLE_EMPTY")
            if not text:
                raise _GateReject("WRITER_TEXT_EMPTY")
            if len(title) > WRITER_TITLE_PAYLOAD_MAX:
                raise _GateReject("WRITER_TITLE_PAYLOAD_TOO_LARGE")
            if len(text) > WRITER_TEXT_PAYLOAD_MAX:
                raise _GateReject("WRITER_TEXT_PAYLOAD_TOO_LARGE")
            claim_ids = _unique(_string_list(raw.get("claim_ids"), "writer.claim_ids"))
            allowed_claim_ids = {str(fact["fact_id"]) for fact in memory["facts"]}
            if not claim_ids or not set(claim_ids).issubset(allowed_claim_ids):
                raise _GateReject("WRITER_CLAIM_REFERENCE_INVALID")
            natural_policy = context.get("writer_grounding_policy") == X02_WRITER_GROUNDING_POLICY
            if not natural_policy and any(
                term in title or term in text for term in UNSUPPORTED_USER_STATE_TERMS
            ):
                raise _GateReject("UNSUPPORTED_USER_STATE_LANGUAGE")
            if memory["memory_type"] == "CHAPTER":
                entry["required_title_visible_min"] = CHAPTER_TITLE_VISIBLE_MIN
                entry["required_title_visible_max"] = CHAPTER_TITLE_VISIBLE_HARD_MAX
                entry["required_sentence_count_min"] = CHAPTER_STORY_SENTENCE_MIN
                entry["required_sentence_count_max"] = CHAPTER_STORY_SENTENCE_MAX
                entry["chapter_story_preview_target_visible_max"] = (
                    CHAPTER_STORY_PREVIEW_TARGET_VISIBLE_MAX
                )
                title_length = int(entry["title_visible_characters"])
                if (
                    title_length < CHAPTER_TITLE_VISIBLE_MIN
                    or title_length > CHAPTER_TITLE_VISIBLE_HARD_MAX
                ):
                    raise _GateReject("CHAPTER_TITLE_LENGTH_INVALID")
                sentence_count = int(entry["sentence_count"])
                if (
                    sentence_count < CHAPTER_STORY_SENTENCE_MIN
                    or sentence_count > CHAPTER_STORY_SENTENCE_MAX
                ):
                    raise _GateReject("CHAPTER_STORY_SENTENCE_COUNT_INVALID")
                if int(entry["text_visible_characters"]) > CHAPTER_STORY_PREVIEW_TARGET_VISIBLE_MAX:
                    entry["quality_flags"] = ["CHAPTER_STORY_OVER_PREVIEW_WRITING_TARGET"]
            else:
                if natural_policy and not set(claim_ids).issubset(
                    set(memory.get("event_fact_ids", allowed_claim_ids))
                ):
                    raise _GateReject("WRITER_EVENT_FACT_REFERENCE_INVALID")
                if grounded_recording_editor.writer_enabled(context) and len(
                    memory.get("event_fact_ids", [])
                ) != 1:
                    raise _GateReject("WRITER_AHA_NOT_ATOMIC")
                if grounded_recording_editor.writer_enabled(context):
                    if not isinstance(memory.get("moment_focus"), str) or not memory["moment_focus"].strip():
                        raise _GateReject("WRITER_AHA_FOCUS_MISSING")
                    selected_media = memory.get("selected_media", [])
                    if (not isinstance(selected_media, list) or len(selected_media) != 1
                            or len(selected_media[0].get("evidence_frame_ids", [])) != 1):
                        raise _GateReject("WRITER_AHA_FOCUS_MEDIA_INVALID")
                entry["required_sentence_count_min"] = 1
                entry["required_sentence_count_max"] = 1
                if grounded_recording_editor.writer_enabled(context):
                    entry["writing_target_visible_max"] = grounded_recording_editor.AHA_WRITING_TARGET
                    entry["required_text_visible_max"] = grounded_recording_editor.AHA_VISIBLE_MAX
                    if int(entry["text_visible_characters"]) > grounded_recording_editor.AHA_VISIBLE_MAX:
                        raise _GateReject("AHA_MOMENT_LINE_OVER_24")
                    entry["length_status"] = (
                        "WITHIN_TARGET"
                        if int(entry["text_visible_characters"]) <= grounded_recording_editor.AHA_WRITING_TARGET
                        else "WITHIN_TOLERANCE"
                    )
                elif writer_exit.soft_length_enabled(context):
                    entry.update(writer_exit.length_audit(int(entry["text_visible_characters"])))
                else:
                    entry["required_text_visible_max"] = AHA_MOMENT_LINE_VISIBLE_MAX
                    if int(entry["text_visible_characters"]) > AHA_MOMENT_LINE_VISIBLE_MAX:
                        raise _GateReject("AHA_MOMENT_LINE_INVALID")
                if int(entry["sentence_count"]) != 1:
                    raise _GateReject("AHA_MOMENT_LINE_INVALID")
            source_bindings: Optional[List[Dict[str, str]]] = None
            if surface_source == "DETERMINISTIC_GROUNDED_FALLBACK":
                source_bindings = _fallback_source_bindings(
                    text, claim_ids, memory, context
                )
                if source_bindings is None:
                    raise _GateReject("FALLBACK_NOT_COMPLETE_APPROVED_FACT")
            narratives[candidate_id] = {
                "candidate_id": candidate_id,
                "title": title,
                "text": text,
                "claim_ids": claim_ids,
                "surface_source": surface_source,
                "surface_policy_version": X02_WRITER_SURFACE_POLICY_VERSION,
            }
            if source_bindings is not None:
                entry["source_bindings"] = source_bindings
            entry["validation_scope"] = (
                "COMPLETE_FACT_COPY_FORMAT_AND_REFERENCES"
                if source_bindings is not None
                else "FORMAT_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION"
            )
            entry["validation_status"] = "PASSED"
            entry["reason_codes"] = [
                "COMPLETE_APPROVED_FACT_FALLBACK_PASSED"
                if source_bindings is not None
                else "WRITER_FORMAT_AND_REFERENCES_PASSED"
                if natural_policy
                else "GROUNDED_WRITER_CONTRACT_PASSED"
            ]
        except _GateReject as exc:
            entry["reason_codes"].append(exc.reason_code)
            invalid.append(candidate_id)
        except (TypeError, ValueError, X02ContractError) as exc:
            entry["reason_codes"].append("WRITER_CONTRACT_INVALID")
            entry["detail"] = str(exc)[:500]
            invalid.append(candidate_id)
        audit.append(entry)
    return narratives, audit, _unique(invalid)


def _grounded_fallback_clause(
    fact_text: object,
    *,
    visible_max: Optional[int] = None,
) -> Optional[str]:
    if not isinstance(fact_text, str):
        return None
    text = re.sub(r"\s+", "", fact_text.strip())
    if not text:
        return None
    full = text if text[-1:] in "。！？!?" else text + "。"
    if _sentence_count(full) == 1 and (
        visible_max is None or _visible_length(full) <= visible_max
    ):
        return full
    # This non-model fallback copies a whole fact; it does not rewrite one.
    return None


def _fallback_title(memory: Mapping[str, object]) -> str:
    # A neutral failure-path label must not infer a mood or story from a class.
    return "生活片段" if memory["memory_type"] == "CHAPTER" else "这一刻"


def _deterministic_writer_fallback(
    context: Mapping[str, object],
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    chapters: List[Dict[str, object]] = []
    ahas: List[Dict[str, object]] = []
    generation_audit: List[Dict[str, object]] = []
    for memory in context.get("memories", []):
        facts = list(memory.get("facts", []))
        candidates = []
        for fact in facts:
            clause = _grounded_fallback_clause(
                fact.get("text"),
                visible_max=(
                    AHA_MOMENT_LINE_VISIBLE_MAX
                    if memory.get("memory_type") == "AHA"
                    and not writer_exit.soft_length_enabled(context) else None
                ),
            )
            if clause:
                candidates.append((
                    _visible_length(clause),
                    str(fact.get("fact_id")),
                    clause,
                    ["COMPLETE_APPROVED_FACT"],
                ))
        if not candidates:
            generation_audit.append({
                "candidate_id": str(memory.get("candidate_id")),
                "memory_type": str(memory.get("memory_type")),
                "attempt": 3,
                "surface_source": "DETERMINISTIC_GROUNDED_FALLBACK",
                "surface_policy_version": X02_WRITER_SURFACE_POLICY_VERSION,
                "validation_status": "REJECTED",
                "reason_codes": ["DETERMINISTIC_FALLBACK_NOT_PROVABLY_SAFE"],
            })
            continue
        _, claim_id, text, source_basis = min(candidates)
        item = {
            "candidate_id": str(memory["candidate_id"]),
            "title": _fallback_title(memory),
            "text": text,
            "claim_ids": [claim_id],
        }
        (chapters if memory["memory_type"] == "CHAPTER" else ahas).append(item)
        generation_entry = {
            "candidate_id": str(memory.get("candidate_id")),
            "memory_type": str(memory.get("memory_type")),
            "attempt": 3,
            "surface_source": "DETERMINISTIC_GROUNDED_FALLBACK",
            "surface_policy_version": X02_WRITER_SURFACE_POLICY_VERSION,
            "validation_status": "PASSED",
            "reason_codes": [
                "COMPLETE_APPROVED_FACT_FALLBACK_PASSED"
            ],
        }
        generation_entry["source_basis"] = source_basis
        generation_audit.append(generation_entry)
    return {"chapters": chapters, "ahas": ahas}, generation_audit


def _public_chapters(
    namespace: uuid.UUID,
    candidates: Sequence[Mapping[str, object]],
    media_by_candidate: Mapping[str, Mapping[str, object]],
    narratives: Mapping[str, Mapping[str, object]],
    observations: Sequence[Mapping[str, object]],
    moments: Sequence[Mapping[str, object]],
    asset_order: Mapping[str, int],
    include_storyline: bool = False,
    include_surface_provenance: bool = False,
    generic_animal_subjects: bool = False,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    observation_by_id = {str(item["id"]): item for item in observations}
    moment_ids_by_observation = {
        observation_id: moment["id"]
        for moment in moments
        for observation_id in moment["observation_ids"]
    }
    chapters = []
    blocked = []
    for candidate in candidates:
        candidate_id = str(candidate["candidate_id"])
        narrative = narratives.get(candidate_id)
        if narrative is None:
            blocked.append({
                "candidate_id": candidate_id,
                "memory_type": "CHAPTER",
                "failure_owner": "S11_WRITER",
                "reason_code": "NO_VALID_WRITER_OUTPUT_AFTER_BOUNDED_RETRY",
            })
            continue
        media = media_by_candidate[candidate_id]
        minimum_media = 3
        if not minimum_media <= len(media["media"]) <= 5:
            blocked.append({
                "candidate_id": candidate_id,
                "memory_type": "CHAPTER",
                "failure_owner": "S10_MEDIA_EDITORIAL",
                "reason_code": "FINAL_MEDIA_COUNT_INVALID",
            })
            continue
        tags = _canonical_tags(
            candidate, [observation_by_id[value] for value in candidate["observation_ids"]],
            generic_animal_subjects=generic_animal_subjects,
        )
        selected_facts = {
            fact["fact_id"]: fact
            for observation_id in candidate["observation_ids"]
            for fact in observation_by_id[observation_id]["facts"]
        }
        selected_claims = [selected_facts[value] for value in narrative["claim_ids"]]
        first_index = min(asset_order[value] for value in candidate["source_asset_ids"])
        last_index = max(asset_order[value] for value in candidate["source_asset_ids"])
        chapter = {
            "id": _stable_id(namespace, "chapter:%s" % candidate_id),
            "candidate_id": candidate_id,
            "title": narrative["title"],
            "time_label": _sequence_label(first_index, last_index),
            "story": narrative["text"],
            "tags": tags,
            "moment_ids": _unique([
                moment_ids_by_observation[value] for value in candidate["observation_ids"]
            ]),
            "hero_asset_id": media["hero_asset_id"],
            "selected_media": media["media"],
            "evidence_support": _memory_support(selected_claims),
            "evidence_frame_ids": _unique([
                frame_id for fact in selected_claims for frame_id in fact["evidence_frame_ids"]
            ]),
            "claims": selected_claims,
            "publication_status": "STAGED_PREVIEW_VALIDATED",
        }
        if include_storyline:
            chapter["storyline_identity"] = candidate["storyline_identity"]
        if include_surface_provenance:
            chapter["surface_source"] = narrative.get("surface_source", "MODEL_WRITER")
            chapter["surface_policy_version"] = narrative.get(
                "surface_policy_version", X02_WRITER_SURFACE_POLICY_VERSION
            )
        chapters.append(chapter)
    return chapters, blocked


def _public_ahas(
    namespace: uuid.UUID,
    candidates: Sequence[Mapping[str, object]],
    media_by_candidate: Mapping[str, Mapping[str, object]],
    narratives: Mapping[str, Mapping[str, object]],
    observations: Sequence[Mapping[str, object]],
    moments: Sequence[Mapping[str, object]],
    asset_order: Mapping[str, int],
    include_surface_provenance: bool = False,
    generic_animal_subjects: bool = False,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    observation_by_id = {str(item["id"]): item for item in observations}
    ahas = []
    blocked = []
    for candidate in candidates:
        candidate_id = str(candidate["candidate_id"])
        narrative = narratives.get(candidate_id)
        if narrative is None:
            blocked.append({
                "candidate_id": candidate_id,
                "memory_type": "AHA",
                "failure_owner": "S11_WRITER",
                "reason_code": "NO_VALID_WRITER_OUTPUT_AFTER_BOUNDED_RETRY",
            })
            continue
        observation = observation_by_id[candidate["observation_id"]]
        media = media_by_candidate[candidate_id]
        selected_facts = {
            fact["fact_id"]: fact for fact in observation["facts"]
        }
        selected_claims = [selected_facts[value] for value in narrative["claim_ids"]]
        index = asset_order[candidate["source_asset_id"]]
        aha = {
            "id": _stable_id(namespace, "aha:%s" % candidate_id),
            "candidate_id": candidate_id,
            "title": narrative["title"],
            "time_label": _sequence_label(index, index),
            "story": narrative["text"],
            "tags": _canonical_tags(candidate, [observation], generic_animal_subjects=generic_animal_subjects),
            "moment_ids": [candidate["moment_id"]],
            "hero_asset_id": media["media"][0]["asset_id"],
            "selected_media": media["media"],
            "evidence_support": _memory_support(selected_claims),
            "evidence_frame_ids": _unique([
                frame_id for fact in selected_claims for frame_id in fact["evidence_frame_ids"]
            ]),
            "claims": selected_claims,
            "publication_status": "STAGED_PREVIEW_VALIDATED",
        }
        if include_surface_provenance:
            aha["surface_source"] = narrative.get("surface_source", "MODEL_WRITER")
            aha["surface_policy_version"] = narrative.get(
                "surface_policy_version", X02_WRITER_SURFACE_POLICY_VERSION
            )
        ahas.append(aha)
    return ahas, blocked


def _canonical_tags(
    candidate: Mapping[str, object],
    observations: Sequence[Mapping[str, object]],
    *,
    generic_animal_subjects: bool = False,
) -> List[str]:
    votes: Dict[str, int] = {}
    episode_code = str(candidate.get("episode_code", "UNKNOWN"))
    episode_tag = EPISODE_TAGS.get(episode_code)
    if episode_tag:
        votes[episode_tag] = len(observations)
    for observation in observations:
        for code, mapping in (
            (observation["setting_code"], SETTING_TAGS),
            (observation["activity_code"], ACTIVITY_TAGS),
        ):
            tag = mapping.get(code)
            if tag:
                votes[tag] = votes.get(tag, 0) + 1
        for subject in observation["subject_codes"]:
            if generic_animal_subjects and subject not in GENERIC_SUBJECT_CODES:
                continue
            tag = SUBJECT_TAGS.get(subject)
            if tag:
                votes[tag] = votes.get(tag, 0) + 1
    threshold = max(1, int(math.ceil(len(observations) / 2.0)))
    supported = [tag for tag, count in votes.items() if count >= threshold]
    facet_order = {"ACTIVITY": 0, "SETTING": 1, "CENTRAL_SUBJECT": 2, "OCCASION": 3}
    supported.sort(key=lambda tag: (-votes[tag], facet_order.get(tag.split(".", 1)[0], 9), tag))
    selected = []
    used_facets = set()
    for tag in supported:
        facet = tag.split(".", 1)[0]
        if facet in used_facets:
            continue
        selected.append(tag)
        used_facets.add(facet)
        if len(selected) == 4:
            break
    return selected


def _memory_support(facts: Sequence[Mapping[str, object]]) -> str:
    grades = {str(fact["support_grade"]) for fact in facts}
    if grades == {"STRONG"}:
        return "STRONG"
    if "WEAK" in grades:
        return "LIMITED"
    return "MODERATE"


def _fixture_perception(context: Mapping[str, object]) -> Dict[str, object]:
    assets = list(context.get("assets", []))
    evidence = list(context.get("evidence", []))
    frames_by_asset: Dict[str, List[str]] = {}
    for asset, frame, _ in evidence:
        frames_by_asset.setdefault(str(asset["asset_id"]), []).append(str(frame["frame_id"]))
    observations = []
    for asset in assets:
        asset_id = str(asset["asset_id"])
        fact = {
            "text": "可见一段合同测试街景。",
            "evidence_frame_ids": frames_by_asset[asset_id],
            "support_grade": "STRONG",
        }
        if context.get("fact_representative_frame_required") and frames_by_asset[asset_id]:
            fact[experience_editor.REPRESENTATIVE_FRAME_FIELD] = frames_by_asset[asset_id][0]
        observations.append({
            "asset_id": asset_id,
            "status": "OBSERVED",
            "facts": [fact],
            "setting_code": "HISTORIC_STREET",
            "activity_code": "WALKING",
            "episode_code": "HISTORIC_TOWN_WALK",
            "subject_codes": ["HISTORIC_ARCHITECTURE"],
            "motifs": ["historic_street"],
            "event_kind": "NONE",
            "event_salience": "NONE",
            "quality_score": 0.8,
            "limitations": ["CONTRACT_FIXTURE_NOT_SEMANTIC_EVIDENCE"],
        })
    return {"observations": observations}


def _fixture_writer(context: Mapping[str, object]) -> Dict[str, object]:
    chapters = []
    ahas = []
    for memory in context.get("memories", []):
        fact_ids = [fact["fact_id"] for fact in memory["facts"]]
        if memory["memory_type"] == "CHAPTER":
            chapters.append({
                "candidate_id": memory["candidate_id"],
                "title": "街巷片段",
                "text": "街巷里的几处景致，沿路慢慢展开。",
                "claim_ids": fact_ids[:3] or fact_ids,
            })
        else:
            ahas.append({
                "candidate_id": memory["candidate_id"],
                "title": "小瞬间",
                "text": "眼前忽然有了小动静。",
                "claim_ids": fact_ids[:1] or fact_ids,
            })
    return {"chapters": chapters, "ahas": ahas}


def _stage_status(stage: str, status: str, reason_codes: Sequence[str]) -> Dict[str, object]:
    return {"stage": stage, "status": status, "reason_codes": list(reason_codes)}


def _metric(
    stage: str,
    duration_seconds: float,
    model_calls: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost_usd: float = 0.0,
) -> Dict[str, object]:
    return {
        "stage": stage,
        "duration_ms": round(max(0.0, duration_seconds) * 1_000.0, 3),
        "model_calls": model_calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(max(0.0, estimated_cost_usd), 8),
    }


def _metric_from_run(run: StageRun) -> Dict[str, object]:
    metric = _metric(
        run.stage,
        run.latency_seconds,
        model_calls=run.model_calls,
        input_tokens=run.input_tokens,
        output_tokens=run.output_tokens,
        estimated_cost_usd=run.estimated_cost_usd,
    )
    metric.update({
        "provider": run.provider,
        "model": run.model,
        "request_id": run.request_id,
        "model_frame_count": run.model_frame_count,
        "pricing_basis": run.pricing_basis,
        "call_status": run.call_status,
    })
    return metric


def stage_run_audit_snapshot(run: StageRun) -> Dict[str, object]:
    return {
        "stage": run.stage,
        "call_status": run.call_status,
        "provider": run.provider,
        "model": run.model,
        "request_id": run.request_id,
        "model_calls": run.model_calls,
        "model_frame_count": run.model_frame_count,
        "input_tokens": run.input_tokens,
        "output_tokens": run.output_tokens,
        "latency_seconds": round(max(0.0, run.latency_seconds), 6),
        "estimated_cost_usd": round(max(0.0, run.estimated_cost_usd), 8),
        "pricing": {
            "currency": run.pricing_currency,
            "input_rate_per_million": run.input_rate_per_million,
            "output_rate_per_million": run.output_rate_per_million,
            "native_currency_per_usd": run.native_currency_per_usd,
            "estimated_cost_native": round(max(0.0, run.estimated_cost_native), 8),
            "basis": run.pricing_basis,
        },
        "selected_evidence": [dict(item) for item in run.selected_evidence],
    }


def _failed_stage_run(
    *,
    stage: str,
    provider: str,
    model: str,
    request_id: str,
    latency_seconds: float,
    evidence: Sequence[Mapping[str, object]],
    frame_count: int,
    pricing_currency: str,
    input_rate: float,
    output_rate: float,
    native_per_usd: float,
    pricing_basis: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    call_status: str = "HTTP_FAILED",
) -> StageRun:
    if call_status not in {
        "HTTP_FAILED", "FAILED_BEFORE_RESPONSE", "RESPONSE_INVALID",
    }:
        raise ValueError("failed StageRun call_status is invalid")
    return StageRun(
        stage=stage,
        output={"failure": "STRUCTURED_RESPONSE_UNAVAILABLE"},
        provider=provider,
        model=model,
        request_id=request_id,
        input_tokens=max(0, input_tokens),
        output_tokens=max(0, output_tokens),
        latency_seconds=max(0.0, latency_seconds),
        model_frame_count=max(0, frame_count),
        model_calls=1,
        pricing_currency=pricing_currency,
        input_rate_per_million=max(0.0, input_rate),
        output_rate_per_million=max(0.0, output_rate),
        native_currency_per_usd=max(1e-12, native_per_usd),
        pricing_basis=pricing_basis,
        selected_evidence=tuple(dict(item) for item in evidence),
        call_status=call_status,
    )


def _sequence_label(first_index: int, last_index: int) -> str:
    if first_index == last_index:
        return "第%d项" % (first_index + 1)
    return "第%d–%d项" % (first_index + 1, last_index + 1)


def _app_asset_uuid(asset_id: str) -> str:
    value = asset_id[6:] if asset_id.startswith("asset_") else asset_id
    try:
        return str(uuid.UUID(value))
    except ValueError:
        return value


def _stable_id(namespace: uuid.UUID, name: str) -> str:
    return str(uuid.uuid5(namespace, name))


def _bounded_string(value: object, minimum: int, maximum: int, location: str) -> str:
    if not isinstance(value, str):
        raise X02ContractError("%s must be a string" % location)
    stripped = value.strip()
    if len(stripped) < minimum or len(stripped) > maximum:
        raise X02ContractError("%s length is invalid" % location)
    return stripped


def _string_list(value: object, location: str, allow_empty: bool = False) -> List[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise X02ContractError("%s must be %sa string array" % (location, "possibly empty " if allow_empty else ""))
    result = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise X02ContractError("%s entries must be non-empty strings" % location)
        result.append(item.strip())
    return result


def _enum(value: object, allowed: frozenset, location: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise X02ContractError("%s is outside the closed vocabulary" % location)
    return value


def _enum_list(value: object, allowed: frozenset, location: str, allow_empty: bool = False) -> List[str]:
    values = _string_list(value, location, allow_empty=allow_empty)
    if any(item not in allowed for item in values):
        raise X02ContractError("%s contains a value outside the closed vocabulary" % location)
    return values


def _unit_float(value: object, location: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise X02ContractError("%s must be a number" % location)
    number = float(value)
    if not math.isfinite(number) or number < 0 or number > 1:
        raise X02ContractError("%s must be between zero and one" % location)
    return number


def _normalized_motif(value: str, *, unicode_safe: bool = False) -> str:
    if not unicode_safe:
        return re.sub(r"[^a-z0-9_\-]+", "_", value.strip().lower()).strip("_")[:80]
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"[^\w\-]+", "_", normalized, flags=re.UNICODE).strip("_")[:80]


def _unique(values: Sequence[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _visible_length(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def _sentence_count(value: str) -> int:
    stripped = value.strip()
    if not stripped:
        return 0
    pieces = [piece for piece in re.split(r"[。！？!?]+", stripped) if piece.strip()]
    return len(pieces)


class _GateReject(Exception):
    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code
