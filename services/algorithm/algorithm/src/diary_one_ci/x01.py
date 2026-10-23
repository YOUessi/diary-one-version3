from __future__ import annotations

import base64
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from .bundle import ImportedEvidenceBundle, load_app_library_bundle
from .core import canonical_bytes, sha256_file
from .transport_diagnostics import DiagnosticTransport


X01_SCHEMA_VERSION = "DIARY_ONE_X01_PREVIEW_V01"
X01_EXPERIMENT = "X01_DIARY_RESEARCH_PREVIEW"
X01_PIPELINE_VERSION = "X01_DIARY_RESEARCH_PREVIEW_V01"
CHAPTER_CONFIDENCE_THRESHOLD = 0.76
AHA_CONFIDENCE_THRESHOLD = 0.84
MAX_CHAPTERS = 4
MAX_AHAS = 3
CANONICAL_TAG_IDS = frozenset({
    "ACTIVITY.WALKING",
    "ACTIVITY.CITY_WALK",
    "ACTIVITY.CRAFT",
    "ACTIVITY.POTTERY",
    "ACTIVITY.SHARED_MEAL",
    "SETTING.TRADITIONAL_HISTORIC_DISTRICT",
    "SETTING.CAFE_OR_TEA_SHOP",
    "SETTING.HOME",
    "SETTING.OUTDOOR_NATURE",
    "SETTING.WORKPLACE",
    "CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE",
    "CENTRAL_SUBJECT.CAT",
    "CENTRAL_SUBJECT.DOG",
    "CENTRAL_SUBJECT.FOOD_OR_DESSERT",
    "CENTRAL_SUBJECT.CRAFT_OBJECT",
    "OCCASION.TRAVEL_OUTING",
    "OCCASION.BIRTHDAY",
    "OCCASION.FAMILY_GATHERING",
})
UNSUPPORTED_USER_STATE_TERMS = ("最爱", "难忘", "幸福", "好吃", "惊喜", "悠闲", "开心")


class X01Error(RuntimeError):
    pass


class X01ModelNotReady(X01Error):
    pass


class X01ContractError(X01Error):
    pass


class X01PostModelContractError(X01ContractError):
    """Contract failure after a billable model response was already received."""

    def __init__(
        self,
        message: str,
        *,
        model_run: "ModelRun",
        bundle_load_seconds: float,
        model_seconds: float,
        validation_seconds: float,
    ) -> None:
        super().__init__(message)
        self.model_run = model_run
        self.bundle_load_seconds = max(0.0, bundle_load_seconds)
        self.model_seconds = max(0.0, model_seconds)
        self.validation_seconds = max(0.0, validation_seconds)


@dataclass(frozen=True)
class ModelRun:
    output: Dict[str, object]
    provider: str
    model: str
    request_id: str
    input_tokens: int
    output_tokens: int
    latency_seconds: float
    model_frame_count: int
    model_calls: int = 1
    pricing_currency: str = "USD"
    input_rate_per_million: float = 0.0
    output_rate_per_million: float = 0.0
    native_currency_per_usd: float = 1.0
    pricing_basis: str = "unconfigured"
    selected_evidence: Tuple[Dict[str, object], ...] = ()


class EditorialModelAdapter:
    provider = "abstract"
    model = "abstract"
    credential_environment = "MODEL_API_KEY"

    @property
    def ready(self) -> bool:
        return False

    def generate(self, bundle: ImportedEvidenceBundle) -> ModelRun:
        raise NotImplementedError


_OBSERVATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["asset_id", "evidence_frame_ids", "observed_facts", "uncertainty", "confidence"],
    "properties": {
        "asset_id": {"type": "string"},
        "evidence_frame_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "observed_facts": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "uncertainty": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
}

_MOMENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["key", "asset_ids", "time_label", "caption", "confidence", "evidence_frame_ids"],
    "properties": {
        "key": {"type": "string"},
        "asset_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "time_label": {"type": "string"},
        "caption": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "evidence_frame_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    },
}

_CLAIM_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["text", "claim_type", "evidence_frame_ids"],
    "properties": {
        "text": {"type": "string"},
        "claim_type": {"type": "string", "enum": ["OBSERVED", "DERIVED"]},
        "evidence_frame_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    },
}

_EDITORIAL_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "key", "title", "time_label", "story", "tags", "moment_keys",
        "hero_asset_id", "confidence", "evidence_frame_ids", "claims",
    ],
    "properties": {
        "key": {"type": "string"},
        "title": {"type": "string"},
        "time_label": {"type": "string"},
        "story": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 4},
        "moment_keys": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "hero_asset_id": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "evidence_frame_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "claims": {"type": "array", "items": _CLAIM_SCHEMA, "minItems": 1},
    },
}

MODEL_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["observations", "moments", "chapter_candidates", "aha_candidates"],
    "properties": {
        "observations": {"type": "array", "items": _OBSERVATION_SCHEMA},
        "moments": {"type": "array", "items": _MOMENT_SCHEMA},
        "chapter_candidates": {"type": "array", "items": _EDITORIAL_SCHEMA},
        "aha_candidates": {"type": "array", "items": _EDITORIAL_SCHEMA},
    },
}


Transport = Callable[[str, Mapping[str, str], bytes, float], Tuple[int, Mapping[str, str], bytes]]


def _configured_rate(name: str, default: float) -> float:
    raw = os.environ.get(name)
    value = default if raw is None else float(raw)
    if not math.isfinite(value) or value < 0:
        raise ValueError("%s must be a finite non-negative number" % name)
    return value


def _configured_positive_rate(name: str, default: float) -> float:
    value = _configured_rate(name, default)
    if value <= 0:
        raise ValueError("%s must be greater than zero" % name)
    return value


def _qwen_default_pricing(model: str) -> Tuple[float, float, str]:
    if model.startswith("qwen3-vl-flash"):
        return 0.15, 1.50, "alibaba-beijing-input-le-32k-2026-08-18"
    if model.startswith("qwen3.6-flash"):
        return 1.20, 7.20, "alibaba-beijing-input-le-256k-2026-08-18"
    return 0.0, 0.0, "unconfigured-model-rate-override-required"


def _url_transport(
    url: str,
    headers: Mapping[str, str],
    body: bytes,
    timeout: float,
    provider_label: str,
) -> Tuple[int, Mapping[str, str], bytes]:
    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers.items()), exc.read()
    except urllib.error.URLError as exc:
        raise X01Error("Could not reach %s: %s" % (provider_label, exc.reason)) from exc


class _AdapterDiagnosticTransport(DiagnosticTransport):
    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        except urllib.error.URLError as error:
            # Keep X01/V03's existing 502 boundary; the actual cause remains
            # chained for recovery while arbitrary exception text stays private.
            raise X01Error('Could not reach model provider (%s)' % type(error.reason).__name__) from error


class QwenChatCompletionsAdapter(EditorialModelAdapter):
    """Qwen-first X01 adapter using Model Studio's OpenAI-compatible Chat API.

    Qwen3-VL JSON mode does not promise strict JSON Schema adherence. The prompt
    carries the schema, and the existing X01 contract layer validates every
    returned reference and field before anything reaches the iPhone.
    """

    provider = "alibaba_model_studio"
    credential_environment = "DASHSCOPE_API_KEY"
    pricing_currency = "CNY"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = 180.0,
        transport: Optional[Transport] = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("DASHSCOPE_API_KEY", "")
        self.model = model or os.environ.get(
            "DIARY_ONE_X01_QWEN_MODEL", "qwen3-vl-flash-2026-01-22"
        )
        self.base_url = (
            base_url
            or os.environ.get("DIARY_ONE_X01_QWEN_BASE_URL")
            or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        ).rstrip("/")
        if not self.base_url.startswith("https://"):
            raise ValueError("Qwen base_url must use https")
        self.timeout_seconds = timeout_seconds
        self.transport = transport or _AdapterDiagnosticTransport()
        default_input, default_output, default_basis = _qwen_default_pricing(self.model)
        self.input_rate_per_million = _configured_rate(
            "DIARY_ONE_X01_QWEN_INPUT_CNY_PER_MTOK", default_input
        )
        self.output_rate_per_million = _configured_rate(
            "DIARY_ONE_X01_QWEN_OUTPUT_CNY_PER_MTOK", default_output
        )
        self.native_currency_per_usd = _configured_positive_rate(
            "DIARY_ONE_X01_CNY_PER_USD", 7.20
        )
        self.pricing_basis = os.environ.get(
            "DIARY_ONE_X01_QWEN_PRICING_BASIS", default_basis
        )

    def request_options(self) -> Dict[str, object]:
        return {"enable_thinking": False}

    @property
    def ready(self) -> bool:
        return bool(self.api_key.strip())

    def generate(self, bundle: ImportedEvidenceBundle) -> ModelRun:
        if not self.ready:
            raise X01ModelNotReady(
                "X01 requires DASHSCOPE_API_KEY on the Mac research server; "
                "the key is never stored in the iPhone app."
            )
        selected_frames = _select_model_frames(bundle)
        prompt = _editorial_prompt(bundle, selected_frames) + (
            "\nReturn exactly one valid JSON object. It must conform to this JSON Schema; "
            "do not wrap it in markdown:\n" + json.dumps(MODEL_OUTPUT_SCHEMA, ensure_ascii=False)
        )
        content: List[Dict[str, object]] = [{"type": "text", "text": prompt}]
        for asset, frame, path in selected_frames:
            content.append({
                "type": "text",
                "text": _evidence_label(asset, frame),
            })
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            content.append({
                "type": "image_url",
                "image_url": {"url": "data:image/jpeg;base64," + encoded},
            })

        request_body = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "response_format": {"type": "json_object"},
            "enable_thinking": False,
            "stream": False,
        }
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        started = time.monotonic()
        status, response_headers, response_data = self.transport(
            self.base_url + "/chat/completions",
            headers,
            canonical_bytes(request_body),
            self.timeout_seconds,
        )
        latency = time.monotonic() - started
        if status < 200 or status >= 300:
            message = response_data[:2_048].decode("utf-8", errors="replace")
            raise X01Error("Qwen Chat Completions request failed with HTTP %s: %s" % (status, message))
        try:
            payload = json.loads(response_data.decode("utf-8"))
            output = json.loads(_chat_completions_output_text(payload))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise X01Error("Qwen returned no valid structured X01 output") from exc
        usage = payload.get("usage") if isinstance(payload, dict) else {}
        usage = usage if isinstance(usage, dict) else {}
        request_id = str(
            response_headers.get("x-request-id")
            or response_headers.get("X-Request-Id")
            or response_headers.get("x-dashscope-request-id")
            or response_headers.get("X-DashScope-Request-Id")
            or payload.get("request_id")
            or payload.get("id")
            or "qwen-request-unknown"
        )
        return ModelRun(
            output=output,
            provider=self.provider,
            model=self.model,
            request_id=request_id,
            input_tokens=int(usage.get("prompt_tokens", usage.get("input_tokens", 0))),
            output_tokens=int(usage.get("completion_tokens", usage.get("output_tokens", 0))),
            latency_seconds=latency,
            model_frame_count=len(selected_frames),
            model_calls=1,
            pricing_currency="CNY",
            input_rate_per_million=self.input_rate_per_million,
            output_rate_per_million=self.output_rate_per_million,
            native_currency_per_usd=self.native_currency_per_usd,
            pricing_basis=self.pricing_basis,
            selected_evidence=_selected_evidence_entries(bundle, selected_frames),
        )

    @staticmethod
    def _url_transport(
        url: str, headers: Mapping[str, str], body: bytes, timeout: float
    ) -> Tuple[int, Mapping[str, str], bytes]:
        return _url_transport(url, headers, body, timeout, "Qwen")


class OpenAIResponsesAdapter(EditorialModelAdapter):
    provider = "openai"
    credential_environment = "OPENAI_API_KEY"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 180.0,
        transport: Optional[Transport] = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY", "")
        self.model = model or os.environ.get("DIARY_ONE_X01_OPENAI_MODEL", "gpt-5.6-luna")
        self.timeout_seconds = timeout_seconds
        self.transport = transport or _AdapterDiagnosticTransport()
        self.input_rate_per_million = _configured_rate(
            "DIARY_ONE_X01_OPENAI_INPUT_USD_PER_MTOK", 0.20
        )
        self.output_rate_per_million = _configured_rate(
            "DIARY_ONE_X01_OPENAI_OUTPUT_USD_PER_MTOK", 1.20
        )

    @property
    def ready(self) -> bool:
        return bool(self.api_key.strip())

    def generate(self, bundle: ImportedEvidenceBundle) -> ModelRun:
        if not self.ready:
            raise X01ModelNotReady(
                "X01 requires OPENAI_API_KEY on the Mac research server; the key is never stored in the iPhone app."
            )
        selected_frames = _select_model_frames(bundle)
        content: List[Dict[str, object]] = [{"type": "input_text", "text": _editorial_prompt(bundle, selected_frames)}]
        for asset, frame, path in selected_frames:
            content.append({
                "type": "input_text",
                "text": _evidence_label(asset, frame),
            })
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            content.append({"type": "input_image", "image_url": "data:image/jpeg;base64," + encoded, "detail": "low"})

        request_body = {
            "model": self.model,
            "store": False,
            "input": [{"role": "user", "content": content}],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "diary_one_x01_editorial",
                    "strict": True,
                    "schema": MODEL_OUTPUT_SCHEMA,
                }
            },
        }
        body = canonical_bytes(request_body)
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        started = time.monotonic()
        status, response_headers, response_data = self.transport(
            "https://api.openai.com/v1/responses", headers, body, self.timeout_seconds
        )
        latency = time.monotonic() - started
        if status < 200 or status >= 300:
            message = response_data[:2_048].decode("utf-8", errors="replace")
            raise X01Error("OpenAI Responses request failed with HTTP %s: %s" % (status, message))
        try:
            payload = json.loads(response_data.decode("utf-8"))
            output_text = _responses_output_text(payload)
            output = json.loads(output_text)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise X01Error("OpenAI returned no valid structured X01 output") from exc
        usage = payload.get("usage") if isinstance(payload, dict) else {}
        usage = usage if isinstance(usage, dict) else {}
        request_id = str(
            response_headers.get("x-request-id")
            or response_headers.get("X-Request-Id")
            or payload.get("id")
            or "openai-request-unknown"
        )
        return ModelRun(
            output=output,
            provider=self.provider,
            model=self.model,
            request_id=request_id,
            input_tokens=int(usage.get("input_tokens", 0)),
            output_tokens=int(usage.get("output_tokens", 0)),
            latency_seconds=latency,
            model_frame_count=len(selected_frames),
            model_calls=1,
            pricing_currency="USD",
            input_rate_per_million=self.input_rate_per_million,
            output_rate_per_million=self.output_rate_per_million,
            native_currency_per_usd=1.0,
            pricing_basis="openai-public-rate-config-2026-08-18",
            selected_evidence=_selected_evidence_entries(bundle, selected_frames),
        )

    @staticmethod
    def _url_transport(
        url: str, headers: Mapping[str, str], body: bytes, timeout: float
    ) -> Tuple[int, Mapping[str, str], bytes]:
        return _url_transport(url, headers, body, timeout, "OpenAI")


class FixtureEditorialAdapter(EditorialModelAdapter):
    """Explicit contract-test adapter. Never selected implicitly by the research server."""

    provider = "fixture"
    model = "fixture-contract-only-v1"

    @property
    def ready(self) -> bool:
        return True

    def generate(self, bundle: ImportedEvidenceBundle) -> ModelRun:
        selected_frames = _select_model_frames(bundle)
        selected_by_asset: Dict[str, List[str]] = {}
        for asset, frame, _ in selected_frames:
            selected_by_asset.setdefault(str(asset["asset_id"]), []).append(str(frame["frame_id"]))
        observations = []
        moments = []
        for index, asset in enumerate(bundle.manifest["assets"]):
            frame_ids = selected_by_asset[str(asset["asset_id"])]
            observations.append({
                "asset_id": asset["asset_id"],
                "evidence_frame_ids": frame_ids,
                "observed_facts": ["A normalized research fixture is present."],
                "uncertainty": "Contract fixture; no semantic claim.",
                "confidence": 1.0,
            })
            moments.append({
                "key": "fixture_moment_%d" % index,
                "asset_ids": [asset["asset_id"]],
                "time_label": "第%d项" % (index + 1),
                "caption": "合同测试 Evidence",
                "confidence": 1.0,
                "evidence_frame_ids": frame_ids,
            })
        first = bundle.manifest["assets"][0]
        chapter = {
            "key": "fixture_chapter",
            "title": "测试序列",
            "time_label": "导入序列",
            "story": "这是一条仅用于合同测试的确定性结果。",
            "tags": [],
            "moment_keys": [moment["key"] for moment in moments],
            "hero_asset_id": first["asset_id"],
            "confidence": 1.0,
            "evidence_frame_ids": [
                frame_id
                for asset in bundle.manifest["assets"]
                for frame_id in selected_by_asset[str(asset["asset_id"])]
            ],
            "claims": [{
                "text": "这是一条合同测试结果。",
                "claim_type": "OBSERVED",
                "evidence_frame_ids": [selected_by_asset[str(first["asset_id"])][0]],
            }],
        }
        return ModelRun(
            output={
                "observations": observations,
                "moments": moments,
                "chapter_candidates": [chapter],
                "aha_candidates": [],
            },
            provider=self.provider,
            model=self.model,
            request_id="fixture-request",
            input_tokens=0,
            output_tokens=0,
            latency_seconds=0.0,
            model_frame_count=len(selected_frames),
            model_calls=0,
            pricing_currency="USD",
            input_rate_per_million=0.0,
            output_rate_per_million=0.0,
            native_currency_per_usd=1.0,
            pricing_basis="fixture-zero-cost",
            selected_evidence=_selected_evidence_entries(bundle, selected_frames),
        )


def run_x01(manifest_path: Path, adapter: EditorialModelAdapter) -> Dict[str, object]:
    run_started = time.monotonic()
    bundle = load_app_library_bundle(manifest_path)
    bundle_loaded = time.monotonic()
    model_run = adapter.generate(bundle)
    model_complete = time.monotonic()
    try:
        result = _compose_preview(bundle, model_run)
    except X01ContractError as exc:
        validation_failed = time.monotonic()
        raise X01PostModelContractError(
            str(exc),
            model_run=model_run,
            bundle_load_seconds=bundle_loaded - run_started,
            model_seconds=model_complete - bundle_loaded,
            validation_seconds=validation_failed - model_complete,
        ) from exc
    validation_complete = time.monotonic()
    trace = result["trace"]
    if not isinstance(trace, dict):  # pragma: no cover - internal invariant
        raise X01ContractError("X01 trace must be an object")
    estimated_cost_usd = float(trace["estimated_cost_usd"])
    trace["stage_metrics"] = [
        _stage_metric("BUNDLE_LOAD", bundle_loaded - run_started),
        _stage_metric(
            "EDITORIAL_MODEL_BRIDGE",
            model_complete - bundle_loaded,
            model_calls=model_run.model_calls,
            input_tokens=model_run.input_tokens,
            output_tokens=model_run.output_tokens,
            estimated_cost_usd=estimated_cost_usd,
        ),
        _stage_metric(
            "DETERMINISTIC_VALIDATION_SELECTION",
            validation_complete - model_complete,
        ),
    ]
    trace["total_duration_ms"] = _duration_ms(validation_complete - run_started)
    trace["stage_metric_scope"] = (
        "Measured X01 compatibility-bridge stages. Token and cost attribution belongs only to "
        "EDITORIAL_MODEL_BRIDGE; it is not an invented S00-S13 split."
    )
    return result


def model_run_audit_snapshot(run: ModelRun) -> Dict[str, object]:
    """Return a storage-safe model/cost snapshot even when validation failed."""
    input_tokens = _safe_non_negative_int(run.input_tokens)
    output_tokens = _safe_non_negative_int(run.output_tokens)
    model_calls = _safe_non_negative_int(run.model_calls)
    model_frame_count = _safe_non_negative_int(run.model_frame_count)
    input_rate = _safe_non_negative_float(run.input_rate_per_million)
    output_rate = _safe_non_negative_float(run.output_rate_per_million)
    native_per_usd = _safe_positive_float(run.native_currency_per_usd)
    estimated_native: Optional[float] = None
    estimated_usd: Optional[float] = None
    if (
        input_tokens is not None
        and output_tokens is not None
        and input_rate is not None
        and output_rate is not None
    ):
        estimated_native = (
            input_tokens * input_rate + output_tokens * output_rate
        ) / 1_000_000
        if native_per_usd is not None:
            estimated_usd = estimated_native / native_per_usd
    return {
        "provider": str(run.provider)[:120],
        "model": str(run.model)[:240],
        "request_id": str(run.request_id)[:500],
        "model_calls": model_calls,
        "model_frame_count": model_frame_count,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_seconds": _safe_non_negative_float(run.latency_seconds),
        "pricing": {
            "currency": str(run.pricing_currency)[:12],
            "input_rate_per_million": input_rate,
            "output_rate_per_million": output_rate,
            "native_currency_per_usd": native_per_usd,
            "estimated_cost_native": (
                round(estimated_native, 8) if estimated_native is not None else None
            ),
            "estimated_cost_usd": (
                round(estimated_usd, 8) if estimated_usd is not None else None
            ),
            "basis": str(run.pricing_basis)[:500],
        },
        "selected_evidence": [dict(entry) for entry in run.selected_evidence],
        "raw_model_output": run.output,
    }


def _safe_non_negative_int(value: object) -> Optional[int]:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _safe_non_negative_float(value: object) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and number >= 0 else None


def _safe_positive_float(value: object) -> Optional[float]:
    number = _safe_non_negative_float(value)
    return number if number is not None and number > 0 else None


def _compose_preview(bundle: ImportedEvidenceBundle, run: ModelRun) -> Dict[str, object]:
    manifest = bundle.manifest
    session_id = str(manifest["session"]["session_id"])
    try:
        namespace = uuid.UUID(session_id)
    except ValueError as exc:
        raise X01ContractError("session.session_id must be a UUID for X01") from exc

    assets = manifest["assets"]
    asset_by_id: Dict[str, Dict[str, object]] = {str(asset["asset_id"]): asset for asset in assets}
    app_uuid_by_asset = {asset_id: _app_asset_uuid(asset_id) for asset_id in asset_by_id}
    asset_order = {str(asset["asset_id"]): index for index, asset in enumerate(assets)}
    frame_by_id: Dict[str, Dict[str, object]] = {}
    frame_asset: Dict[str, str] = {}
    for asset in assets:
        for frame in asset["frames"]:
            frame_id = str(frame["frame_id"])
            frame_by_id[frame_id] = frame
            frame_asset[frame_id] = str(asset["asset_id"])
    allowed_model_frame_ids = _validated_reported_evidence(
        run, frame_by_id, frame_asset
    )

    output = run.output
    if not isinstance(output, dict):
        raise X01ContractError("model output must be an object")
    for key in ("observations", "moments", "chapter_candidates", "aha_candidates"):
        if not isinstance(output.get(key), list):
            raise X01ContractError("model output.%s must be an array" % key)

    observations, observation_ledger = _validate_observations(
        output["observations"], namespace, asset_by_id, app_uuid_by_asset,
        frame_by_id, frame_asset, allowed_model_frame_ids,
    )
    moments, moment_assets, materialized_moment_assets, moment_ledger = _validate_moments(
        output["moments"], namespace, asset_by_id, app_uuid_by_asset,
        asset_order, frame_by_id, frame_asset, allowed_model_frame_ids,
    )
    moment_id_by_asset = {moment["_source_asset_id"]: moment["id"] for moment in moments}
    public_moments = [{key: value for key, value in moment.items() if not key.startswith("_")} for moment in moments]

    chapter_ledger: List[Dict[str, object]] = []
    aha_ledger: List[Dict[str, object]] = []
    chapters = _validated_candidates(
        output["chapter_candidates"], "chapter", namespace, CHAPTER_CONFIDENCE_THRESHOLD,
        asset_by_id, app_uuid_by_asset, asset_order, frame_by_id, frame_asset,
        moment_assets, materialized_moment_assets, moment_id_by_asset,
        allowed_model_frame_ids, chapter_ledger,
    )
    ahas = _validated_candidates(
        output["aha_candidates"], "aha", namespace, AHA_CONFIDENCE_THRESHOLD,
        asset_by_id, app_uuid_by_asset, asset_order, frame_by_id, frame_asset,
        moment_assets, materialized_moment_assets, moment_id_by_asset,
        allowed_model_frame_ids, aha_ledger,
    )
    selected_chapters = _select_chapters(chapters, chapter_ledger)
    selected_ahas = _select_ahas(ahas, selected_chapters, aha_ledger)
    public_chapters = [_public_candidate(candidate) for candidate in selected_chapters]
    public_ahas = [_public_candidate(candidate) for candidate in selected_ahas]

    if public_chapters:
        output_mode = "CHAPTER_DAY"
    elif public_ahas:
        output_mode = "HIGHLIGHT_DAY"
    else:
        output_mode = "EMPTY_DAY"

    all_frame_paths = [manifest_path_for_frame(bundle.manifest_path, frame) for frame in frame_by_id.values()]
    uploaded_bytes = sum(path.stat().st_size for path in all_frame_paths)
    if run.model_calls < 0:
        raise X01ContractError("model_calls cannot be negative")
    if run.input_tokens < 0 or run.output_tokens < 0:
        raise X01ContractError("model token counts cannot be negative")
    if run.model_frame_count <= 0:
        raise X01ContractError("model_frame_count must be positive")
    if run.pricing_currency not in ("USD", "CNY") or not run.pricing_basis.strip():
        raise X01ContractError("model pricing metadata is invalid")
    rates = (run.input_rate_per_million, run.output_rate_per_million)
    if any(not math.isfinite(rate) or rate < 0 for rate in rates):
        raise X01ContractError("model pricing rates must be finite and non-negative")
    if not math.isfinite(run.native_currency_per_usd) or run.native_currency_per_usd <= 0:
        raise X01ContractError("native_currency_per_usd must be finite and positive")
    estimated_cost_native = (
        run.input_tokens * run.input_rate_per_million
        + run.output_tokens * run.output_rate_per_million
    ) / 1_000_000
    estimated_cost_usd = estimated_cost_native / run.native_currency_per_usd

    capture_times = [str(asset["capture_time"]) for asset in assets if asset.get("capture_time")]
    timeline_date = min(capture_times) if capture_times else str(manifest["session"]["exported_at"])
    return {
        "schema_version": X01_SCHEMA_VERSION,
        "experiment": X01_EXPERIMENT,
        "experimental": True,
        "leaderboard_eligible": False,
        "session_id": session_id,
        "bundle_manifest_sha256": sha256_file(bundle.manifest_path),
        "output_mode": output_mode,
        "timeline_date": timeline_date,
        "observations": observations,
        "moments": public_moments,
        "chapters": public_chapters,
        "ahas": public_ahas,
        "decision_trace": {
            "trace_type": "AUDITABLE_DECISION_EVIDENCE",
            "contains_hidden_reasoning": False,
            "scope_note": (
                "Records supplied evidence, contract checks, deterministic selection outcomes, and reason codes. "
                "It is not model chain-of-thought or hidden reasoning. Invalid observations are rejected individually "
                "and remain visible in the observation candidate ledger; they never receive fabricated evidence."
            ),
            "evidence_selection": {
                "strategy": "ONE_MIDDLE_FRAME_PER_ASSET_THEN_VIDEO_CONTEXT_WITHIN_BUDGET",
                "available_frame_count": len(frame_by_id),
                "model_frame_count": run.model_frame_count,
                "reported_selected_frame_count": len(run.selected_evidence),
                "adapter_reported_selection": bool(run.selected_evidence),
                "selected": [dict(entry) for entry in run.selected_evidence],
            },
            "counts": {
                "model_observation_count": len(output["observations"]),
                "validated_observation_count": len(observations),
                "rejected_observation_count": sum(
                    1 for entry in observation_ledger if entry["validation_status"] == "REJECTED"
                ),
                "model_moment_count": len(output["moments"]),
                "validated_moment_candidate_count": sum(
                    1 for entry in moment_ledger if entry["validation_status"] == "PASSED"
                ),
                "materialized_moment_count": len(public_moments),
                "model_chapter_candidate_count": len(output["chapter_candidates"]),
                "validated_chapter_candidate_count": len(chapters),
                "selected_chapter_count": len(public_chapters),
                "model_aha_candidate_count": len(output["aha_candidates"]),
                "validated_aha_candidate_count": len(ahas),
                "selected_aha_count": len(public_ahas),
            },
            "observation_candidates": observation_ledger,
            "moment_candidates": moment_ledger,
            "chapter_candidates": chapter_ledger,
            "aha_candidates": aha_ledger,
        },
        "trace": {
            "pipeline_version": X01_PIPELINE_VERSION,
            "provider": run.provider,
            "model": run.model,
            "request_id": run.request_id,
            "model_calls": run.model_calls,
            "asset_count": len(assets),
            "evidence_frame_count": len(frame_by_id),
            "model_frame_count": run.model_frame_count,
            "uploaded_bytes": uploaded_bytes,
            "originals_uploaded": 0,
            "input_tokens": run.input_tokens,
            "output_tokens": run.output_tokens,
            "latency_seconds": round(run.latency_seconds, 6),
            "estimated_cost_usd": round(estimated_cost_usd, 8),
            "pricing": {
                "currency": run.pricing_currency,
                "input_rate_per_million": run.input_rate_per_million,
                "output_rate_per_million": run.output_rate_per_million,
                "native_currency_per_usd": run.native_currency_per_usd,
                "estimated_cost_native": round(estimated_cost_native, 8),
                "basis": run.pricing_basis,
            },
        },
    }


def manifest_path_for_frame(manifest_path: Path, frame: Mapping[str, object]) -> Path:
    return (manifest_path.parent / str(frame["relative_path"])).resolve()


def _duration_ms(seconds: float) -> float:
    return round(max(0.0, seconds) * 1_000.0, 3)


def _stage_metric(
    stage: str,
    duration_seconds: float,
    model_calls: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost_usd: float = 0.0,
) -> Dict[str, object]:
    return {
        "stage": stage,
        "duration_ms": _duration_ms(duration_seconds),
        "model_calls": model_calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(estimated_cost_usd, 8),
    }


def _candidate_ledger_entry(
    item: object, kind: str, source_index: int
) -> Dict[str, object]:
    mapping = item if isinstance(item, dict) else {}
    return {
        "candidate_kind": kind.upper(),
        "source_index": source_index,
        "source_key": mapping.get("key") if isinstance(mapping.get("key"), str) else None,
        "candidate_id": None,
        "title": str(mapping.get("title", ""))[:100],
        "story": str(mapping.get("story", ""))[:700],
        "confidence": (
            mapping.get("confidence")
            if not isinstance(mapping.get("confidence"), bool)
            and isinstance(mapping.get("confidence"), (int, float))
            and math.isfinite(float(mapping.get("confidence")))
            else None
        ),
        "source_asset_ids": [],
        "evidence_frame_ids": _trace_string_list(mapping.get("evidence_frame_ids")),
        "validation_status": "PENDING",
        "selection_status": "NOT_ELIGIBLE",
        "reason_code": None,
        "reason_codes": [],
    }


def _trace_string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item)[:240] for item in value[:64] if isinstance(item, str)]


def _reject_candidate(entry: Dict[str, object], reason_code: str) -> None:
    entry["validation_status"] = "REJECTED"
    entry["selection_status"] = "NOT_ELIGIBLE"
    entry["reason_code"] = reason_code
    entry["reason_codes"] = [reason_code]


def _not_selected_candidate(entry: Dict[str, object], reason_code: str) -> None:
    entry["selection_status"] = "NOT_SELECTED"
    entry["reason_code"] = reason_code
    reasons = list(entry.get("reason_codes", []))
    reasons.append(reason_code)
    entry["reason_codes"] = reasons


def _selected_candidate(entry: Dict[str, object], reason_code: str) -> None:
    entry["selection_status"] = "SELECTED"
    entry["reason_code"] = reason_code
    reasons = list(entry.get("reason_codes", []))
    reasons.append(reason_code)
    entry["reason_codes"] = reasons


def _validated_reported_evidence(
    run: ModelRun,
    frame_by_id: Mapping[str, Dict[str, object]],
    frame_asset: Mapping[str, str],
) -> set:
    if not run.selected_evidence:
        raise X01ContractError("model adapter must report the evidence frames presented to the model")
    if len(run.selected_evidence) != run.model_frame_count:
        raise X01ContractError("reported model evidence count does not match model_frame_count")
    allowed = set()
    for index, entry in enumerate(run.selected_evidence):
        if not isinstance(entry, dict):
            raise X01ContractError("selected_evidence[%d] must be an object" % index)
        frame_id = entry.get("frame_id")
        source_asset_id = entry.get("source_asset_id")
        if not isinstance(frame_id, str) or frame_id not in frame_by_id:
            raise X01ContractError("selected_evidence references an unknown frame")
        if not isinstance(source_asset_id, str) or frame_asset[frame_id] != source_asset_id:
            raise X01ContractError("selected_evidence frame ownership is invalid")
        if frame_id in allowed:
            raise X01ContractError("selected_evidence contains a duplicate frame")
        allowed.add(frame_id)
    return allowed


def _validate_observations(
    raw: Sequence[object],
    namespace: uuid.UUID,
    asset_by_id: Mapping[str, Dict[str, object]],
    app_uuid_by_asset: Mapping[str, str],
    frame_by_id: Mapping[str, Dict[str, object]],
    frame_asset: Mapping[str, str],
    allowed_model_frame_ids: set,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    seen = set()
    validated = []
    ledger: List[Dict[str, object]] = []
    for index, item in enumerate(raw):
        entry = _observation_ledger_entry(item, index)
        ledger.append(entry)
        if not isinstance(item, dict):
            _reject_observation(entry, "CANDIDATE_NOT_OBJECT")
            continue
        try:
            asset_id = _required_string(item, "asset_id", "observation")
        except X01ContractError:
            _reject_observation(entry, "ASSET_ID_INVALID")
            continue
        entry["source_asset_id"] = asset_id
        if asset_id not in asset_by_id:
            _reject_observation(entry, "UNKNOWN_ASSET")
            continue
        if asset_id in seen:
            _reject_observation(entry, "DUPLICATE_ASSET_OBSERVATION")
            continue
        try:
            frame_ids = _unique(
                _string_list(item.get("evidence_frame_ids"), "observation.evidence_frame_ids")
            )
        except X01ContractError:
            _reject_observation(entry, "EVIDENCE_FRAME_IDS_INVALID")
            continue
        entry["evidence_frame_ids"] = frame_ids
        if any(frame_id not in frame_by_id or frame_asset[frame_id] != asset_id for frame_id in frame_ids):
            entry["invalid_frame_ids"] = [
                frame_id
                for frame_id in frame_ids
                if frame_id not in frame_by_id or frame_asset.get(frame_id) != asset_id
            ]
            _reject_observation(entry, "INVALID_FRAME")
            continue
        unpresented = [
            frame_id for frame_id in frame_ids if frame_id not in allowed_model_frame_ids
        ]
        if unpresented:
            entry["invalid_frame_ids"] = unpresented
            _reject_observation(entry, "EVIDENCE_FRAME_NOT_PRESENTED_TO_MODEL")
            continue
        try:
            facts = _string_list(item.get("observed_facts"), "observation.observed_facts")
        except X01ContractError:
            _reject_observation(entry, "OBSERVED_FACTS_INVALID")
            continue
        try:
            confidence = _confidence(item.get("confidence"), "observation.confidence")
        except X01ContractError:
            _reject_observation(entry, "CONFIDENCE_INVALID")
            continue
        entry["confidence"] = confidence
        entry["validation_status"] = "PASSED"
        entry["reason_code"] = "VALIDATION_PASSED"
        entry["reason_codes"] = ["VALIDATION_PASSED"]
        seen.add(asset_id)
        validated.append({
            "id": "obs_" + str(uuid.uuid5(namespace, "observation:" + asset_id)),
            "asset_id": app_uuid_by_asset[asset_id],
            "evidence_frame_ids": frame_ids,
            "observed_facts": [fact[:240] for fact in facts[:8]],
            "uncertainty": str(item.get("uncertainty", ""))[:240],
            "confidence": confidence,
        })
    return validated, ledger


def _observation_ledger_entry(item: object, source_index: int) -> Dict[str, object]:
    mapping = item if isinstance(item, dict) else {}
    confidence = mapping.get("confidence")
    return {
        "source_index": source_index,
        "source_asset_id": (
            mapping.get("asset_id") if isinstance(mapping.get("asset_id"), str) else None
        ),
        "confidence": (
            confidence
            if not isinstance(confidence, bool)
            and isinstance(confidence, (int, float))
            and math.isfinite(float(confidence))
            else None
        ),
        "evidence_frame_ids": _trace_string_list(mapping.get("evidence_frame_ids")),
        "invalid_frame_ids": [],
        "validation_status": "PENDING",
        "reason_code": None,
        "reason_codes": [],
    }


def _reject_observation(entry: Dict[str, object], reason_code: str) -> None:
    entry["validation_status"] = "REJECTED"
    entry["reason_code"] = reason_code
    entry["reason_codes"] = [reason_code]


def _validate_moments(
    raw: Sequence[object],
    namespace: uuid.UUID,
    asset_by_id: Mapping[str, Dict[str, object]],
    app_uuid_by_asset: Mapping[str, str],
    asset_order: Mapping[str, int],
    frame_by_id: Mapping[str, Dict[str, object]],
    frame_asset: Mapping[str, str],
    allowed_model_frame_ids: set,
) -> Tuple[
    List[Dict[str, object]],
    Dict[str, List[str]],
    Dict[str, List[str]],
    List[Dict[str, object]],
]:
    keys = set()
    moment_assets: Dict[str, List[str]] = {}
    ledger: List[Dict[str, object]] = []
    candidates_by_asset: Dict[str, List[Tuple[int, Dict[str, object]]]] = {}
    for index, item in enumerate(raw):
        entry = _moment_ledger_entry(item, index)
        ledger.append(entry)
        if not isinstance(item, dict):
            _reject_moment(entry, "CANDIDATE_NOT_OBJECT")
            continue
        try:
            key = _required_string(item, "key", "moment")
        except X01ContractError:
            _reject_moment(entry, "KEY_INVALID")
            continue
        entry["source_key"] = key
        if key in keys:
            _reject_moment(entry, "DUPLICATE_KEY")
            continue
        keys.add(key)
        try:
            asset_ids = _unique(_string_list(item.get("asset_ids"), "moment.asset_ids"))
        except X01ContractError:
            _reject_moment(entry, "ASSET_IDS_INVALID")
            continue
        entry["source_asset_ids"] = asset_ids
        if any(asset_id not in asset_by_id for asset_id in asset_ids):
            _reject_moment(entry, "UNKNOWN_ASSET")
            continue
        try:
            frame_ids = _unique(_string_list(item.get("evidence_frame_ids"), "moment.evidence_frame_ids"))
        except X01ContractError:
            _reject_moment(entry, "INVALID_FRAME")
            continue
        entry["evidence_frame_ids"] = frame_ids
        if (
            any(frame_id not in frame_by_id or frame_asset[frame_id] not in asset_ids for frame_id in frame_ids)
            or any(not any(frame_asset[frame_id] == asset_id for frame_id in frame_ids) for asset_id in asset_ids)
        ):
            _reject_moment(entry, "INVALID_FRAME")
            continue
        if any(frame_id not in allowed_model_frame_ids for frame_id in frame_ids):
            _reject_moment(entry, "EVIDENCE_FRAME_NOT_PRESENTED_TO_MODEL")
            continue
        try:
            confidence = _confidence(item.get("confidence"), "moment.confidence")
        except X01ContractError:
            _reject_moment(entry, "CONFIDENCE_INVALID")
            continue
        entry["confidence"] = confidence
        try:
            time_label = _required_string(item, "time_label", "moment")[:80]
            caption = _required_string(item, "caption", "moment")[:240] or None
        except X01ContractError:
            _reject_moment(entry, "COPY_FIELD_INVALID")
            continue
        moment_assets[key] = asset_ids
        entry["validation_status"] = "PASSED"
        entry["materialization_status"] = "PENDING"
        entry["reason_code"] = "VALIDATION_PASSED"
        entry["reason_codes"] = ["VALIDATION_PASSED"]
        for asset_id in asset_ids:
            asset_frames = [frame_id for frame_id in frame_ids if frame_asset[frame_id] == asset_id]
            candidate = {
                "id": str(uuid.uuid5(namespace, "moment:" + asset_id)),
                "asset_id": app_uuid_by_asset[asset_id],
                "time_label": time_label,
                "caption": caption,
                "confidence": confidence,
                "evidence_frame_ids": asset_frames,
                "_source_asset_id": asset_id,
                "_order": asset_order[asset_id],
            }
            candidates_by_asset.setdefault(asset_id, []).append((len(ledger) - 1, candidate))

    best_by_asset: Dict[str, Dict[str, object]] = {}
    for asset_id, choices in candidates_by_asset.items():
        winner_ledger_index, winner = max(
            choices,
            key=lambda choice: (choice[1]["confidence"], -choice[0]),
        )
        best_by_asset[asset_id] = winner
        winner_entry = ledger[winner_ledger_index]
        winner_entry["materialized_asset_ids"].append(asset_id)
        for ledger_index, candidate in choices:
            if ledger_index == winner_ledger_index:
                continue
            losing_entry = ledger[ledger_index]
            if candidate["confidence"] < winner["confidence"]:
                _append_reason(losing_entry, "LOW_CONFIDENCE")
                _append_reason(losing_entry, "SUPERSEDED_BY_HIGHER_CONFIDENCE")
                losing_entry["reason_code"] = "SUPERSEDED_BY_HIGHER_CONFIDENCE"
            else:
                _append_reason(losing_entry, "SUPERSEDED_BY_EARLIER_EQUAL_CONFIDENCE")
                losing_entry["reason_code"] = "SUPERSEDED_BY_EARLIER_EQUAL_CONFIDENCE"

    for entry in ledger:
        if entry["validation_status"] != "PASSED":
            continue
        materialized_count = len(entry["materialized_asset_ids"])
        source_count = len(entry["source_asset_ids"])
        if materialized_count == source_count:
            entry["materialization_status"] = "MATERIALIZED"
            entry["reason_code"] = "MATERIALIZED"
            _append_reason(entry, "MATERIALIZED")
        elif materialized_count:
            entry["materialization_status"] = "PARTIALLY_MATERIALIZED"
            _append_reason(entry, "MATERIALIZED")
        else:
            entry["materialization_status"] = "NOT_MATERIALIZED"
    moments = sorted(best_by_asset.values(), key=lambda item: item["_order"])
    materialized_moment_assets = {
        str(entry["source_key"]): list(entry["materialized_asset_ids"])
        for entry in ledger
        if entry["validation_status"] == "PASSED"
    }
    return moments, moment_assets, materialized_moment_assets, ledger


def _moment_ledger_entry(item: object, source_index: int) -> Dict[str, object]:
    mapping = item if isinstance(item, dict) else {}
    return {
        "source_index": source_index,
        "source_key": mapping.get("key") if isinstance(mapping.get("key"), str) else None,
        "confidence": None,
        "source_asset_ids": _trace_string_list(mapping.get("asset_ids")),
        "materialized_asset_ids": [],
        "evidence_frame_ids": _trace_string_list(mapping.get("evidence_frame_ids")),
        "validation_status": "PENDING",
        "materialization_status": "NOT_ELIGIBLE",
        "reason_code": None,
        "reason_codes": [],
    }


def _reject_moment(entry: Dict[str, object], reason_code: str) -> None:
    entry["validation_status"] = "REJECTED"
    entry["materialization_status"] = "NOT_ELIGIBLE"
    entry["reason_code"] = reason_code
    entry["reason_codes"] = [reason_code]


def _append_reason(entry: Dict[str, object], reason_code: str) -> None:
    reasons = list(entry.get("reason_codes", []))
    if reason_code not in reasons:
        reasons.append(reason_code)
    entry["reason_codes"] = reasons


def _validated_candidates(
    raw: Sequence[object],
    kind: str,
    namespace: uuid.UUID,
    threshold: float,
    asset_by_id: Mapping[str, Dict[str, object]],
    app_uuid_by_asset: Mapping[str, str],
    asset_order: Mapping[str, int],
    frame_by_id: Mapping[str, Dict[str, object]],
    frame_asset: Mapping[str, str],
    moment_assets: Mapping[str, List[str]],
    materialized_moment_assets: Mapping[str, List[str]],
    moment_id_by_asset: Mapping[str, str],
    allowed_model_frame_ids: set,
    ledger: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    validated = []
    seen_keys = set()
    for source_index, item in enumerate(raw):
        entry = _candidate_ledger_entry(item, kind, source_index)
        ledger.append(entry)
        if not isinstance(item, dict):
            _reject_candidate(entry, "CANDIDATE_NOT_OBJECT")
            continue
        try:
            key = _required_string(item, "key", kind)
        except X01ContractError:
            _reject_candidate(entry, "KEY_INVALID")
            continue
        entry["source_key"] = key
        if key in seen_keys:
            _reject_candidate(entry, "DUPLICATE_KEY")
            continue
        seen_keys.add(key)
        try:
            confidence = _confidence(item.get("confidence"), kind + ".confidence")
        except X01ContractError:
            _reject_candidate(entry, "CONFIDENCE_INVALID")
            continue
        entry["confidence"] = confidence
        if confidence < threshold:
            _reject_candidate(entry, "BELOW_CONFIDENCE_THRESHOLD")
            continue
        try:
            moment_keys = _unique(_string_list(item.get("moment_keys"), kind + ".moment_keys"))
        except X01ContractError:
            _reject_candidate(entry, "MOMENT_KEYS_INVALID")
            continue
        if any(moment_key not in moment_assets for moment_key in moment_keys):
            _reject_candidate(entry, "UNKNOWN_MOMENT_KEY")
            continue
        if any(
            set(materialized_moment_assets.get(moment_key, [])) != set(moment_assets[moment_key])
            for moment_key in moment_keys
        ):
            _reject_candidate(entry, "MOMENT_NOT_MATERIALIZED")
            continue
        asset_ids = _unique([
            asset_id for moment_key in moment_keys for asset_id in moment_assets[moment_key]
        ])
        entry["source_asset_ids"] = asset_ids
        if not asset_ids or any(asset_id not in moment_id_by_asset for asset_id in asset_ids):
            _reject_candidate(entry, "ASSET_WITHOUT_MATERIALIZED_MOMENT")
            continue
        if kind == "chapter" and not 2 <= len(asset_ids) <= 5:
            _reject_candidate(entry, "CHAPTER_ASSET_COUNT_OUT_OF_RANGE")
            continue
        if kind == "aha" and len(asset_ids) != 1:
            _reject_candidate(entry, "AHA_ASSET_COUNT_NOT_ONE")
            continue
        try:
            hero_asset_id = _required_string(item, "hero_asset_id", kind)
        except X01ContractError:
            _reject_candidate(entry, "HERO_ASSET_INVALID")
            continue
        if hero_asset_id not in asset_ids:
            _reject_candidate(entry, "HERO_ASSET_OUTSIDE_CANDIDATE")
            continue
        try:
            frame_ids = _unique(_string_list(item.get("evidence_frame_ids"), kind + ".evidence_frame_ids"))
        except X01ContractError:
            _reject_candidate(entry, "EVIDENCE_FRAME_IDS_INVALID")
            continue
        if any(frame_id not in frame_by_id or frame_asset[frame_id] not in asset_ids for frame_id in frame_ids):
            _reject_candidate(entry, "EVIDENCE_FRAME_OUTSIDE_CANDIDATE")
            continue
        if any(frame_id not in allowed_model_frame_ids for frame_id in frame_ids):
            _reject_candidate(entry, "EVIDENCE_FRAME_NOT_PRESENTED_TO_MODEL")
            continue
        claims = _validated_claims(
            item.get("claims"), frame_ids, frame_by_id, allowed_model_frame_ids
        )
        if not claims:
            _reject_candidate(entry, "CLAIMS_INVALID")
            continue
        try:
            title = _required_string(item, "title", kind)
            story = _required_string(item, "story", kind)
            time_label = _required_string(item, "time_label", kind)
        except X01ContractError:
            _reject_candidate(entry, "COPY_FIELD_INVALID")
            continue
        if len(title) > 100 or len(story) > 700 or len(time_label) > 80:
            _reject_candidate(entry, "COPY_HARD_LENGTH_LIMIT")
            continue
        try:
            tags = _unique(_string_list(item.get("tags"), kind + ".tags", allow_empty=True))[:4]
        except X01ContractError:
            _reject_candidate(entry, "TAGS_INVALID")
            continue
        if any(tag not in CANONICAL_TAG_IDS for tag in tags):
            _reject_candidate(entry, "UNKNOWN_CANONICAL_TAG")
            continue
        if any(term in title or term in story for term in UNSUPPORTED_USER_STATE_TERMS):
            _reject_candidate(entry, "UNSUPPORTED_USER_STATE_TERM")
            continue
        if kind == "chapter":
            if not 2 <= len(title) <= 12 or _sentence_count(story) not in (1, 2):
                _reject_candidate(entry, "CHAPTER_COPY_CONTRACT_FAILED")
                continue
        elif len(story) > 20 or _sentence_count(story) != 1:
            _reject_candidate(entry, "AHA_COPY_CONTRACT_FAILED")
            continue
        candidate_id = str(uuid.uuid5(namespace, kind + ":" + key))
        entry.update({
            "candidate_id": candidate_id,
            "validation_status": "PASSED",
            "selection_status": "PENDING",
            "reason_code": "VALIDATION_PASSED",
            "reason_codes": ["VALIDATION_PASSED"],
        })
        validated.append({
            "id": candidate_id,
            "title": title,
            "time_label": time_label,
            "story": story,
            "tags": tags,
            "moment_ids": [moment_id_by_asset[asset_id] for asset_id in asset_ids],
            "hero_asset_id": app_uuid_by_asset[hero_asset_id],
            "confidence": confidence,
            "evidence_frame_ids": frame_ids,
            "claims": claims,
            "_asset_ids": asset_ids,
            "_timeline_order": min(asset_order[asset_id] for asset_id in asset_ids),
            "_ledger_index": len(ledger) - 1,
        })
    return validated


def _validated_claims(
    value: object,
    candidate_frame_ids: Sequence[str],
    frame_by_id: Mapping[str, Dict[str, object]],
    allowed_model_frame_ids: set,
) -> List[Dict[str, object]]:
    if not isinstance(value, list):
        return []
    allowed = set(candidate_frame_ids)
    claims = []
    for claim in value:
        if not isinstance(claim, dict):
            return []
        text = str(claim.get("text", "")).strip()
        claim_type = str(claim.get("claim_type", ""))
        try:
            evidence = _unique(_string_list(claim.get("evidence_frame_ids"), "claim.evidence_frame_ids"))
        except X01ContractError:
            return []
        if (
            not text or len(text) > 300 or claim_type not in ("OBSERVED", "DERIVED")
            or any(
                frame_id not in allowed
                or frame_id not in frame_by_id
                or frame_id not in allowed_model_frame_ids
                for frame_id in evidence
            )
        ):
            return []
        claims.append({"text": text, "claim_type": claim_type, "evidence_frame_ids": evidence})
    return claims


def _select_chapters(
    candidates: Sequence[Dict[str, object]], ledger: List[Dict[str, object]]
) -> List[Dict[str, object]]:
    selected = []
    used_assets = set()
    for candidate in sorted(candidates, key=lambda item: (-item["confidence"], item["_timeline_order"])):
        entry = ledger[int(candidate["_ledger_index"])]
        if len(selected) == MAX_CHAPTERS:
            _not_selected_candidate(entry, "CHAPTER_CAPACITY_LIMIT")
            continue
        assets = set(candidate["_asset_ids"])
        if assets & used_assets:
            _not_selected_candidate(entry, "ASSET_OVERLAP_WITH_SELECTED_CHAPTER")
            continue
        selected.append(candidate)
        used_assets.update(assets)
        _selected_candidate(entry, "SELECTED_BY_CONFIDENCE_AND_TIMELINE")
    return sorted(selected, key=lambda item: item["_timeline_order"])


def _select_ahas(
    candidates: Sequence[Dict[str, object]],
    chapters: Sequence[Dict[str, object]],
    ledger: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    selected = []
    existing = [_editorial_tokens(item) for item in chapters]
    chapter_assets = {
        asset_id for chapter in chapters for asset_id in chapter.get("_asset_ids", [])
    }
    for candidate in sorted(candidates, key=lambda item: (-item["confidence"], item["_timeline_order"])):
        entry = ledger[int(candidate["_ledger_index"])]
        if len(selected) == MAX_AHAS:
            _not_selected_candidate(entry, "AHA_CAPACITY_LIMIT")
            continue
        if set(candidate.get("_asset_ids", [])) & chapter_assets:
            # X01 has no full V1.20 narrative-independence ledger. Conservatively
            # require a separate core asset instead of pretending exact reuse was proven.
            _not_selected_candidate(entry, "CORE_ASSET_ALREADY_OWNED_BY_CHAPTER")
            continue
        tokens = _editorial_tokens(candidate)
        if any(_editorial_overlap(tokens, prior) >= 0.35 for prior in existing):
            _not_selected_candidate(entry, "EDITORIAL_OVERLAP_THRESHOLD")
            continue
        selected.append(candidate)
        existing.append(tokens)
        _selected_candidate(entry, "SELECTED_BY_CONFIDENCE_AND_NARRATIVE_SEPARATION")
    return sorted(selected, key=lambda item: item["_timeline_order"])


def _public_candidate(candidate: Mapping[str, object]) -> Dict[str, object]:
    return {key: value for key, value in candidate.items() if not key.startswith("_")}


def _editorial_tokens(candidate: Mapping[str, object]) -> set:
    text = (str(candidate.get("title", "")) + " " + str(candidate.get("story", ""))).lower()
    words = {
        token for token in re.findall(r"[a-z0-9_]+", text)
        if len(token) >= 2
    }
    chinese = "".join(re.findall(r"[\u3400-\u9fff]", text))
    bigrams = {chinese[index:index + 2] for index in range(max(0, len(chinese) - 1))}
    return words | bigrams


def _sentence_count(value: str) -> int:
    text = value.strip()
    if not text:
        return 0
    endings = re.findall(r"[。！？!?]+", text)
    return max(1, len(endings))


def _jaccard(left: set, right: set) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _editorial_overlap(left: set, right: set) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left & right)
    return max(_jaccard(left, right), intersection / min(len(left), len(right)))


def _select_model_frames(
    bundle: ImportedEvidenceBundle,
) -> List[Tuple[Dict[str, object], Dict[str, object], Path]]:
    selected: List[Tuple[Dict[str, object], Dict[str, object], Path]] = []
    extras: List[Tuple[Dict[str, object], Dict[str, object], Path]] = []
    for asset in bundle.manifest["assets"]:
        frames = sorted(asset["frames"], key=lambda frame: int(frame["canonical_offset_ms"]))
        middle = min(frames, key=lambda frame: abs(int(frame["canonical_offset_ms"]) - 4_500))
        selected.append((asset, middle, manifest_path_for_frame(bundle.manifest_path, middle)))
        if asset["media_kind"] == "VIDEO":
            for frame in frames:
                if frame["frame_id"] != middle["frame_id"]:
                    extras.append((asset, frame, manifest_path_for_frame(bundle.manifest_path, frame)))
    limit = max(len(selected), int(os.environ.get("DIARY_ONE_X01_MAX_MODEL_FRAMES", "48")))
    selected.extend(extras[: max(0, limit - len(selected))])
    return selected


def _selected_evidence_entries(
    bundle: ImportedEvidenceBundle,
    selected_frames: Sequence[Tuple[Dict[str, object], Dict[str, object], Path]],
) -> Tuple[Dict[str, object], ...]:
    middle_by_asset: Dict[str, str] = {}
    for asset in bundle.manifest["assets"]:
        frames = sorted(asset["frames"], key=lambda frame: int(frame["canonical_offset_ms"]))
        middle = min(frames, key=lambda frame: abs(int(frame["canonical_offset_ms"]) - 4_500))
        middle_by_asset[str(asset["asset_id"])] = str(middle["frame_id"])
    entries = []
    for order, (asset, frame, _) in enumerate(selected_frames):
        source_asset_id = str(asset["asset_id"])
        frame_id = str(frame["frame_id"])
        entries.append({
            "selection_order": order,
            "asset_id": _app_asset_uuid(source_asset_id),
            "source_asset_id": source_asset_id,
            "frame_id": frame_id,
            "media_kind": str(asset["media_kind"]),
            "canonical_offset_ms": int(frame["canonical_offset_ms"]),
            "reason_code": (
                "PRIMARY_MIDDLE_FRAME_PER_ASSET"
                if middle_by_asset[source_asset_id] == frame_id
                else "SUPPLEMENTAL_VIDEO_CONTEXT_WITHIN_BUDGET"
            ),
        })
    return tuple(entries)


def _evidence_label(asset: Mapping[str, object], frame: Mapping[str, object]) -> str:
    return (
        "Evidence follows. asset_id=%s frame_id=%s media_kind=%s "
        "canonical_offset_ms=%s source_timestamp_ms=%s"
        % (
            asset["asset_id"],
            frame["frame_id"],
            asset["media_kind"],
            frame["canonical_offset_ms"],
            frame.get("source_timestamp_ms"),
        )
    )


def _editorial_prompt(
    bundle: ImportedEvidenceBundle,
    selected_frames: Sequence[Tuple[Dict[str, object], Dict[str, object], Path]],
) -> str:
    catalog = [{
        "asset_id": asset["asset_id"],
        "media_kind": asset["media_kind"],
        "capture_time": asset.get("capture_time"),
        "timeline_offset_ms": asset.get("timeline_offset_ms"),
        "frame_id": frame["frame_id"],
        "canonical_offset_ms": frame["canonical_offset_ms"],
        "source_timestamp_ms": frame.get("source_timestamp_ms"),
    } for asset, frame, _ in selected_frames]
    return (
        "You are the real-media research bridge for Diary One Canonical V1.25. This is not the full staged Production "
        "S00-S13 engine, but every visible candidate must follow the latest frozen product contract. Analyze only the "
        "supplied evidence and return zh-Hans test copy. The asset order is a synthetic chronology for one test day; "
        "capture time and GPS are deliberately unavailable. Never state clock time, exact place, or elapsed duration. "
        "First write conservative per-asset observations, then chronological local moments, then optional Chapter and "
        "Aha candidates. Use continuity evidence as well as visual similarity: a short B interruption may sit inside one "
        "A-C Chapter when A and C resume the same main experience. A long dominant motif may retain several spaced, "
        "meaningfully different views; do not delete all architecture merely because it shares a style. Do not cluster "
        "distant items only because they look alike. "
        "A Chapter is one complete, independently worthwhile episode with 3-5 selected assets; use exactly 2 only when "
        "the pair alone forms a complete compact experience. Its Chinese title must contain 2-10 visible characters, "
        "or 11-12 only when semantically necessary. Its story is one sentence by default and never more than two; write "
        "a natural, restrained scene or change, not an explanation such as 'these formed the main picture'. "
        "An Aha is one short, narratively independent peak, not a low-score Chapter and not the climax already owned by "
        "a Chapter. It must select exactly one core asset. For schema compatibility only, put a short internal label in "
        "aha.title and put the sole user-visible MOMENT_LINE in aha.story; that line must be one sentence and no more than "
        "20 visible Chinese characters. A birthday candle-blowing climax belongs to the birthday Chapter; an independent "
        "dessert interaction during a town walk may be an Aha when it has a different story duty. "
        "Returning no candidates is correct when evidence is weak. Never invent identity, relationship, user emotion, "
        "preference, intent, cause, taste, exact location, dialogue, or events outside visible evidence. Without protected "
        "user evidence, do not write 最爱、难忘、幸福、好吃、惊喜、悠闲 or 开心. Common light-affect wording such as "
        "调皮 for a visibly playful cat may be used conservatively when the action itself supports it. Every claim must "
        "cite supplied frame IDs and be OBSERVED or DERIVED. Tags are optional and must be zero to four exact IDs from "
        "this closed registry: " + ", ".join(sorted(CANONICAL_TAG_IDS)) + ". Do not output free-form tags. Candidate "
        "confidence reflects evidence support, not prose quality. "
        "Frame IDs are opaque allowlist tokens: copy them verbatim from the catalog. Never construct, infer, edit, "
        "or predict a frame ID from an asset ID or canonical offset. If no listed frame supports an item, omit that "
        "Observation, Moment, Chapter, Aha, or Claim instead of inventing a citation. "
        "Use the exact asset IDs and frame IDs from this catalog:\n" + json.dumps(catalog, ensure_ascii=False)
    )


def _chat_completions_output_text(payload: Mapping[str, object]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise KeyError("choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise KeyError("message")
    content = message.get("content")
    if isinstance(content, str) and content:
        return content
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str) and text:
                return text
    raise KeyError("message.content")


def _responses_output_text(payload: Mapping[str, object]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct:
        return direct
    output = payload.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict) and part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    return part["text"]
    raise KeyError("output_text")


def _app_asset_uuid(asset_id: str) -> str:
    value = asset_id[6:] if asset_id.startswith("asset_") else asset_id
    try:
        return str(uuid.UUID(value))
    except ValueError as exc:
        raise X01ContractError("X01 App Library asset_id must contain a UUID: %s" % asset_id) from exc


def _required_string(mapping: Mapping[str, object], key: str, location: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise X01ContractError("%s.%s must be a non-empty string" % (location, key))
    return value.strip()


def _string_list(value: object, location: str, allow_empty: bool = False) -> List[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise X01ContractError("%s must be an array%s" % (location, "" if allow_empty else " with values"))
    output = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise X01ContractError("%s contains an invalid string" % location)
        output.append(item.strip())
    return output


def _confidence(value: object, location: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise X01ContractError("%s must be numeric" % location)
    result = float(value)
    if not math.isfinite(result) or result < 0 or result > 1:
        raise X01ContractError("%s must be between 0 and 1" % location)
    return result


def _unique(values: Sequence[str]) -> List[str]:
    return list(dict.fromkeys(values))
