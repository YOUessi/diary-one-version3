"""Day-level V01 validation for the frozen Diary One V1.0 pipeline.

The evaluator consumes semantic timeline design cases and final-output-shaped
predictions.  It deliberately keeps blocking truth errors, quality misses, and
human-review items separate; it never emits a compensating overall score.

Design-gold results prove evaluator and contract conformance only.  They are
not real-media accuracy, model quality, user preference, or Production claims.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Set, Tuple


SUITE_CONTRACT_VERSION = "DIARY_ONE_VALIDATION_SUITE_V01"
DAY_CASE_CONTRACT_VERSION = "DIARY_ONE_DAY_EVAL_CASE_V01"
SCORECARD_CONTRACT_VERSION = "DIARY_ONE_VALIDATION_SCORECARD_V01"
PIPELINE_CONTRACT_REF = "DIARY_ONE_PRODUCTION_PIPELINE_V1_0"

DAY_STATES = ("CHAPTER_DAY", "HIGHLIGHT_DAY", "EMPTY_DAY")
MEMORY_TYPES = ("CHAPTER", "AHA")
SOURCE_KINDS = ("AUTO", "MANUAL_PHOTO", "MANUAL_VIDEO")
SUPPORT_LEVELS = ("STRONG", "MODERATE", "WEAK", "UNKNOWN")
MEDIA_FORMATS = ("PHOTO", "LIVE_2S", "VIDEO_5S")
EXPECTED_STATUSES = ("PASS", "REVIEW", "QUALITY_FAIL", "BLOCKING_FAIL")
SEVERITY_ORDER = {"BLOCKING": 0, "QUALITY": 1, "REVIEW": 2}

DIMENSIONS = (
    "TRUTH",
    "MEMORY_IDENTITY_AND_BOUNDARY",
    "CHAPTER_AHA_INDEPENDENCE",
    "MEDIA_EDITORIAL",
    "NARRATIVE_CONTRACT",
    "MEMORY_INDEX",
)


class ValidationContractError(ValueError):
    """The V01 suite is structurally invalid or makes an unsafe claim."""


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise ValidationContractError(f"{code}: {detail}")


def _require_keys(value: Mapping[str, object], keys: Iterable[str], code: str) -> None:
    missing = [key for key in keys if key not in value]
    _require(not missing, code, f"missing required keys: {', '.join(missing)}")


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _fingerprint(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def load_validation_suite(path: Path) -> Dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(payload, dict), "SUITE_INVALID", "top level must be an object")
    return payload


def write_validation_suite(payload: Mapping[str, object], path: Path) -> Path:
    """Validate and atomically materialize a versioned V01 suite."""

    normalized: Dict[str, object] = copy.deepcopy(dict(payload))
    validate_validation_suite(normalized)
    _atomic_write_json(path, normalized)
    return path


def _string_list(value: object, code: str, allow_empty: bool = True) -> List[str]:
    _require(isinstance(value, list), code, "must be an array")
    _require(
        all(isinstance(item, str) and bool(item.strip()) for item in value),
        code,
        "items must be non-empty strings",
    )
    result = list(value)
    _require(
        len(result) == len(set(result)),
        code,
        "must not contain duplicates",
    )
    if not allow_empty:
        _require(bool(result), code, "must not be empty")
    return result


def _range_pair(value: object, code: str) -> Tuple[int, int]:
    _require(
        isinstance(value, list) and len(value) == 2,
        code,
        "must contain [minimum, maximum]",
    )
    _require(
        all(type(item) is int for item in value),
        code,
        "range values must be integers",
    )
    minimum, maximum = value
    _require(0 <= minimum <= maximum, code, str(value))
    return minimum, maximum


def validate_validation_suite(payload: MutableMapping[str, object]) -> Dict[str, object]:
    """Validate a V01 suite without evaluating any trial."""

    _require(
        payload.get("contract_version") == SUITE_CONTRACT_VERSION,
        "SUITE_VERSION_INVALID",
        str(payload.get("contract_version")),
    )
    _require_keys(
        payload,
        (
            "suite_id",
            "title",
            "evidence_scope",
            "narrative_locale",
            "pipeline_contract_ref",
            "days",
            "trials",
        ),
        "SUITE_INVALID",
    )
    for key in ("suite_id", "title", "pipeline_contract_ref"):
        _require(
            isinstance(payload[key], str) and bool(payload[key].strip()),
            "SUITE_INVALID",
            f"{key} must be a non-empty string",
        )
    _require(
        len(str(payload["suite_id"])) <= 128
        and re.fullmatch(r"[A-Za-z0-9._-]+", str(payload["suite_id"])) is not None,
        "SUITE_ID_INVALID",
        str(payload["suite_id"]),
    )
    _require(
        payload["evidence_scope"] == "SEMANTIC_TIMELINE_ONLY",
        "EVIDENCE_SCOPE_INVALID",
        str(payload["evidence_scope"]),
    )
    _require(
        payload["narrative_locale"] == "zh-CN",
        "NARRATIVE_LOCALE_UNSUPPORTED",
        str(payload["narrative_locale"]),
    )
    _require(
        payload["pipeline_contract_ref"] == PIPELINE_CONTRACT_REF,
        "PIPELINE_CONTRACT_REF_INVALID",
        str(payload["pipeline_contract_ref"]),
    )
    days = payload["days"]
    trials = payload["trials"]
    _require(isinstance(days, list), "DAYS_INVALID", "must be an array")
    _require(12 <= len(days) <= 20, "DAY_COUNT_INVALID", str(len(days)))
    _require(isinstance(trials, list) and trials, "TRIALS_INVALID", "must be a non-empty array")

    day_by_id: Dict[str, Mapping[str, object]] = {}
    for raw_day in days:
        _validate_day(raw_day)
        day_id = str(raw_day["day_id"])
        _require(day_id not in day_by_id, "DUPLICATE_DAY_ID", day_id)
        day_by_id[day_id] = raw_day

    trial_ids: Set[str] = set()
    nominal_days: Set[str] = set()
    referenced_days: Set[str] = set()
    for raw_trial in trials:
        _validate_trial(raw_trial, day_by_id)
        trial_id = str(raw_trial["trial_id"])
        day_id = str(raw_trial["day_id"])
        _require(trial_id not in trial_ids, "DUPLICATE_TRIAL_ID", trial_id)
        trial_ids.add(trial_id)
        referenced_days.add(day_id)
        if raw_trial["trial_kind"] == "NOMINAL_REFERENCE":
            _require(day_id not in nominal_days, "DUPLICATE_NOMINAL_TRIAL", day_id)
            nominal_days.add(day_id)
    _require(
        referenced_days == set(day_by_id),
        "DAY_TRIAL_COVERAGE_INVALID",
        str(sorted(set(day_by_id) - referenced_days)),
    )
    _require(
        nominal_days == set(day_by_id),
        "NOMINAL_TRIAL_COVERAGE_INVALID",
        str(sorted(set(day_by_id) - nominal_days)),
    )
    _require(
        any(trial["trial_kind"] == "FAILURE_INJECTION" for trial in trials),
        "FAILURE_INJECTION_COVERAGE_INVALID",
        "at least one failure injection is required",
    )
    return {
        "suite_id": str(payload["suite_id"]),
        "day_count": len(days),
        "trial_count": len(trials),
        "design_gold_day_count": sum(
            1
            for day in days
            if day["gold"]["label_origin"] == "DESIGN_GOLD"
        ),
        "human_gold_day_count": sum(
            1
            for day in days
            if day["gold"]["label_origin"] == "HUMAN_ADJUDICATED_GOLD"
        ),
        "status": "VALIDATION_SUITE_CONTRACT_PASS",
    }


def _validate_day(raw_day: object) -> None:
    _require(isinstance(raw_day, Mapping), "DAY_INVALID", "day must be an object")
    _require_keys(
        raw_day,
        (
            "contract_version",
            "day_id",
            "title",
            "profile_id",
            "evidence_mode",
            "timeline_step_minutes",
            "timeline",
            "gold",
            "human_review_prompts",
        ),
        "DAY_INVALID",
    )
    _require(
        raw_day["contract_version"] == DAY_CASE_CONTRACT_VERSION,
        "DAY_VERSION_INVALID",
        str(raw_day["day_id"]),
    )
    for key in ("day_id", "title", "profile_id"):
        _require(
            isinstance(raw_day[key], str) and bool(raw_day[key].strip()),
            "DAY_INVALID",
            f"{key} must be a non-empty string",
        )
    _require(
        raw_day["evidence_mode"] == "SEMANTIC_TIMELINE_ONLY",
        "DAY_EVIDENCE_MODE_INVALID",
        str(raw_day["day_id"]),
    )
    step = int(raw_day["timeline_step_minutes"])
    _require(step == 2, "TIMELINE_STEP_INVALID", str(raw_day["day_id"]))
    timeline = raw_day["timeline"]
    _require(isinstance(timeline, list) and timeline, "TIMELINE_INVALID", str(raw_day["day_id"]))
    seen_windows: Set[str] = set()
    starts: List[int] = []
    for window in timeline:
        _require(isinstance(window, Mapping), "WINDOW_INVALID", str(raw_day["day_id"]))
        _require_keys(
            window,
            (
                "window_id",
                "capture_minute",
                "source_kind",
                "semantic_atoms",
                "evidence_support",
            ),
            "WINDOW_INVALID",
        )
        window_id = str(window["window_id"])
        _require(window_id not in seen_windows, "DUPLICATE_WINDOW_ID", window_id)
        seen_windows.add(window_id)
        minute = int(window["capture_minute"])
        _require(0 <= minute < 1440, "WINDOW_TIME_INVALID", window_id)
        starts.append(minute)
        _require(window["source_kind"] in SOURCE_KINDS, "SOURCE_KIND_INVALID", window_id)
        _require(window["evidence_support"] in SUPPORT_LEVELS, "SUPPORT_INVALID", window_id)
        _string_list(window["semantic_atoms"], "WINDOW_ATOMS_INVALID")
    _require(starts == sorted(starts), "TIMELINE_ORDER_INVALID", str(raw_day["day_id"]))
    for first, second in zip(starts, starts[1:]):
        _require(
            second > first and (second - first) % step == 0,
            "TIMELINE_CADENCE_INVALID",
            f"{raw_day['day_id']}:{first}:{second}",
        )
    _string_list(
        raw_day["human_review_prompts"],
        "HUMAN_REVIEW_PROMPTS_INVALID",
    )
    evidence_atoms = {
        str(atom)
        for window in timeline
        if window["evidence_support"] in ("STRONG", "MODERATE")
        for atom in window["semantic_atoms"]
    }
    _validate_gold(raw_day["gold"], str(raw_day["day_id"]), evidence_atoms)


def _validate_gold(raw_gold: object, day_id: str, evidence_atoms: Set[str]) -> None:
    _require(isinstance(raw_gold, Mapping), "GOLD_INVALID", day_id)
    _require_keys(
        raw_gold,
        (
            "label_origin",
            "label_status",
            "accuracy_eligible",
            "day_state",
            "chapter_count_range",
            "aha_count_range",
            "memories",
            "forbidden_memory_patterns",
            "distinct_story_pairs",
        ),
        "GOLD_INVALID",
    )
    origin = str(raw_gold["label_origin"])
    _require(
        origin in ("DESIGN_GOLD", "HUMAN_ADJUDICATED_GOLD"),
        "GOLD_ORIGIN_INVALID",
        day_id,
    )
    if origin == "DESIGN_GOLD":
        _require(
            raw_gold["label_status"] == "DESIGN_REVIEWED"
            and raw_gold["accuracy_eligible"] is False,
            "DESIGN_GOLD_CLAIM_INVALID",
            day_id,
        )
    else:
        _require(
            raw_gold["label_status"] == "HUMAN_ADJUDICATED"
            and raw_gold["accuracy_eligible"] is True
            and type(raw_gold.get("independent_annotator_count")) is int
            and raw_gold["independent_annotator_count"] >= 2
            and isinstance(raw_gold.get("adjudication_ref"), str)
            and bool(raw_gold["adjudication_ref"].strip()),
            "HUMAN_GOLD_PROVENANCE_INVALID",
            day_id,
        )
    _require(raw_gold["day_state"] in DAY_STATES, "GOLD_DAY_STATE_INVALID", day_id)
    chapter_range = _range_pair(raw_gold["chapter_count_range"], "GOLD_CHAPTER_RANGE_INVALID")
    aha_range = _range_pair(raw_gold["aha_count_range"], "GOLD_AHA_RANGE_INVALID")
    _require(chapter_range[1] <= 5 and aha_range[1] <= 3, "GOLD_CAPACITY_INVALID", day_id)
    memories = raw_gold["memories"]
    _require(isinstance(memories, list), "GOLD_MEMORIES_INVALID", day_id)
    _require(len(memories) <= 8, "GOLD_CAPACITY_INVALID", day_id)
    seen: Set[str] = set()
    memory_by_id: Dict[str, Mapping[str, object]] = {}
    for memory in memories:
        _require(isinstance(memory, Mapping), "GOLD_MEMORY_INVALID", day_id)
        _require_keys(
            memory,
            (
                "gold_memory_id",
                "memory_type",
                "requirement",
                "story_role",
                "acceptable_span_minute",
                "minimum_overlap_ratio",
                "identity_atoms",
                "required_atoms",
                "optional_atoms",
                "forbidden_atoms",
                "required_concept_ids",
                "allowed_concept_ids",
                "forbidden_concept_ids",
                "allowed_entity_ids",
                "media_policy",
                "media_count_range",
                "required_media_atoms",
                "allowed_media_formats",
            ),
            "GOLD_MEMORY_INVALID",
        )
        gold_id = str(memory["gold_memory_id"])
        _require(
            isinstance(memory["gold_memory_id"], str)
            and bool(memory["gold_memory_id"].strip())
            and isinstance(memory["story_role"], str)
            and bool(memory["story_role"].strip()),
            "GOLD_MEMORY_INVALID",
            gold_id,
        )
        _require(gold_id not in seen, "DUPLICATE_GOLD_MEMORY_ID", gold_id)
        seen.add(gold_id)
        memory_by_id[gold_id] = memory
        _require(memory["memory_type"] in MEMORY_TYPES, "GOLD_MEMORY_TYPE_INVALID", gold_id)
        _require(
            memory["requirement"] in ("REQUIRED", "OPTIONAL_REVIEW"),
            "GOLD_REQUIREMENT_INVALID",
            gold_id,
        )
        start, end = _range_pair(memory["acceptable_span_minute"], "GOLD_SPAN_INVALID")
        _require(start < end <= 1440, "GOLD_SPAN_INVALID", gold_id)
        overlap = float(memory["minimum_overlap_ratio"])
        _require(0 < overlap <= 1, "GOLD_OVERLAP_INVALID", gold_id)
        identity = _string_list(memory["identity_atoms"], "GOLD_IDENTITY_ATOMS_INVALID", allow_empty=False)
        required = _string_list(memory["required_atoms"], "GOLD_REQUIRED_ATOMS_INVALID")
        optional = _string_list(memory["optional_atoms"], "GOLD_OPTIONAL_ATOMS_INVALID")
        forbidden = _string_list(memory["forbidden_atoms"], "GOLD_FORBIDDEN_ATOMS_INVALID")
        _require(
            not (set(required) & set(forbidden))
            and not (set(optional) & set(forbidden))
            and set(identity).issubset(set(required) | set(optional)),
            "GOLD_ATOM_SETS_CONFLICT",
            gold_id,
        )
        _require(
            set(identity).issubset(evidence_atoms)
            and set(required).issubset(evidence_atoms),
            "GOLD_ATOMS_UNGROUNDED",
            gold_id,
        )
        required_concepts = _string_list(memory["required_concept_ids"], "GOLD_REQUIRED_CONCEPTS_INVALID")
        allowed_concepts = _string_list(memory["allowed_concept_ids"], "GOLD_ALLOWED_CONCEPTS_INVALID")
        forbidden_concepts = _string_list(memory["forbidden_concept_ids"], "GOLD_FORBIDDEN_CONCEPTS_INVALID")
        _require(
            set(required_concepts).issubset(set(allowed_concepts))
            and not (set(allowed_concepts) & set(forbidden_concepts)),
            "GOLD_CONCEPT_SETS_CONFLICT",
            gold_id,
        )
        _string_list(memory["allowed_entity_ids"], "GOLD_ENTITIES_INVALID")
        media_range = _range_pair(memory["media_count_range"], "GOLD_MEDIA_RANGE_INVALID")
        if memory["memory_type"] == "CHAPTER":
            _require(
                memory["media_policy"] in ("STANDARD_3_TO_5", "COMPACT_2_TO_5"),
                "GOLD_MEDIA_POLICY_INVALID",
                gold_id,
            )
            if memory["media_policy"] == "STANDARD_3_TO_5":
                _require(media_range == (3, 5), "GOLD_MEDIA_RANGE_INVALID", gold_id)
            else:
                _require(
                    media_range == (2, 5)
                    and isinstance(memory.get("compact_pair_gate_ref"), str)
                    and bool(memory["compact_pair_gate_ref"].strip()),
                    "GOLD_COMPACT_GATE_INVALID",
                    gold_id,
                )
        else:
            _require(
                memory["media_policy"] == "AHA_SINGLE"
                and media_range == (1, 1),
                "GOLD_AHA_MEDIA_RANGE_INVALID",
                gold_id,
            )
        required_media_atoms = _string_list(
            memory["required_media_atoms"], "GOLD_REQUIRED_MEDIA_ATOMS_INVALID"
        )
        _require(
            set(required_media_atoms).issubset(evidence_atoms),
            "GOLD_MEDIA_ATOMS_UNGROUNDED",
            gold_id,
        )
        formats = _string_list(memory["allowed_media_formats"], "GOLD_MEDIA_FORMATS_INVALID", allow_empty=False)
        _require(set(formats).issubset(MEDIA_FORMATS), "GOLD_MEDIA_FORMATS_INVALID", gold_id)
    _require(
        isinstance(raw_gold["forbidden_memory_patterns"], list),
        "FORBIDDEN_PATTERNS_INVALID",
        day_id,
    )
    for pattern in raw_gold["forbidden_memory_patterns"]:
        _require(isinstance(pattern, Mapping), "FORBIDDEN_PATTERN_INVALID", day_id)
        _require_keys(pattern, ("memory_type", "any_atoms", "error_code"), "FORBIDDEN_PATTERN_INVALID")
        _require(pattern["memory_type"] in MEMORY_TYPES, "FORBIDDEN_PATTERN_TYPE_INVALID", day_id)
        _string_list(pattern["any_atoms"], "FORBIDDEN_PATTERN_ATOMS_INVALID", allow_empty=False)
    _require(
        isinstance(raw_gold["distinct_story_pairs"], list),
        "DISTINCT_PAIRS_INVALID",
        day_id,
    )
    for pair in raw_gold["distinct_story_pairs"]:
        _require(isinstance(pair, Mapping), "DISTINCT_PAIR_INVALID", day_id)
        _require_keys(
            pair,
            (
                "chapter_gold_id",
                "aha_gold_id",
                "chapter_forbidden_atoms",
                "aha_forbidden_atoms",
            ),
            "DISTINCT_PAIR_INVALID",
        )
        _require(
            str(pair["chapter_gold_id"]) in seen
            and str(pair["aha_gold_id"]) in seen,
            "DISTINCT_PAIR_MEMORY_MISSING",
            day_id,
        )
        _require(
            memory_by_id[str(pair["chapter_gold_id"])]["memory_type"] == "CHAPTER"
            and memory_by_id[str(pair["aha_gold_id"])]["memory_type"] == "AHA",
            "DISTINCT_PAIR_TYPE_INVALID",
            day_id,
        )
        _string_list(pair["chapter_forbidden_atoms"], "DISTINCT_PAIR_ATOMS_INVALID")
        _string_list(pair["aha_forbidden_atoms"], "DISTINCT_PAIR_ATOMS_INVALID")

    required_counts = {
        memory_type: sum(
            1
            for memory in memories
            if memory["memory_type"] == memory_type
            and memory["requirement"] == "REQUIRED"
        )
        for memory_type in MEMORY_TYPES
    }
    total_counts = {
        memory_type: sum(
            1 for memory in memories if memory["memory_type"] == memory_type
        )
        for memory_type in MEMORY_TYPES
    }
    for memory_type, allowed_range in (
        ("CHAPTER", chapter_range),
        ("AHA", aha_range),
    ):
        _require(
            allowed_range[0] <= required_counts[memory_type] <= allowed_range[1]
            and total_counts[memory_type] <= allowed_range[1],
            "GOLD_MEMORY_RANGE_INCONSISTENT",
            f"{day_id}:{memory_type}",
        )
    if raw_gold["day_state"] == "CHAPTER_DAY":
        _require(chapter_range[0] >= 1, "GOLD_DAY_STATE_INCONSISTENT", day_id)
    elif raw_gold["day_state"] == "HIGHLIGHT_DAY":
        _require(
            chapter_range == (0, 0) and aha_range == (1, 1),
            "GOLD_DAY_STATE_INCONSISTENT",
            day_id,
        )
    else:
        _require(
            chapter_range == (0, 0)
            and aha_range == (0, 0)
            and not memories,
            "GOLD_DAY_STATE_INCONSISTENT",
            day_id,
        )


def _validate_trial(raw_trial: object, day_by_id: Mapping[str, Mapping[str, object]]) -> None:
    _require(isinstance(raw_trial, Mapping), "TRIAL_INVALID", "trial must be an object")
    _require_keys(
        raw_trial,
        (
            "trial_id",
            "day_id",
            "trial_kind",
            "prediction",
            "expected_evaluation",
        ),
        "TRIAL_INVALID",
    )
    _require(
        isinstance(raw_trial["trial_id"], str)
        and bool(raw_trial["trial_id"].strip())
        and isinstance(raw_trial["day_id"], str)
        and bool(raw_trial["day_id"].strip()),
        "TRIAL_INVALID",
        str(raw_trial.get("trial_id")),
    )
    day_id = str(raw_trial["day_id"])
    _require(day_id in day_by_id, "TRIAL_DAY_MISSING", day_id)
    _require(
        raw_trial["trial_kind"] in ("NOMINAL_REFERENCE", "FAILURE_INJECTION"),
        "TRIAL_KIND_INVALID",
        str(raw_trial["trial_id"]),
    )
    prediction = raw_trial["prediction"]
    _require(isinstance(prediction, Mapping), "PREDICTION_INVALID", str(raw_trial["trial_id"]))
    _require_keys(prediction, ("day_state", "memories"), "PREDICTION_INVALID")
    _require(prediction["day_state"] in DAY_STATES, "PREDICTION_DAY_STATE_INVALID", str(raw_trial["trial_id"]))
    memories = prediction["memories"]
    _require(isinstance(memories, list), "PREDICTION_MEMORIES_INVALID", str(raw_trial["trial_id"]))
    _require(
        len(memories) <= 16,
        "PREDICTION_EVALUATOR_GUARD_EXCEEDED",
        str(raw_trial["trial_id"]),
    )
    seen: Set[str] = set()
    for memory in memories:
        _require(isinstance(memory, Mapping), "PREDICTION_MEMORY_INVALID", str(raw_trial["trial_id"]))
        _require_keys(
            memory,
            (
                "memory_id",
                "memory_type",
                "span_minute",
                "semantic_atoms",
                "asserted_atoms",
                "canonical_concept_ids",
                "entity_ids",
                "media",
                "narrative",
            ),
            "PREDICTION_MEMORY_INVALID",
        )
        memory_id = str(memory["memory_id"])
        _require(
            isinstance(memory["memory_id"], str) and bool(memory["memory_id"].strip()),
            "PREDICTION_MEMORY_INVALID",
            memory_id,
        )
        _require(memory_id not in seen, "DUPLICATE_PREDICTION_MEMORY_ID", memory_id)
        seen.add(memory_id)
        _require(memory["memory_type"] in MEMORY_TYPES, "PREDICTION_MEMORY_TYPE_INVALID", memory_id)
        start, end = _range_pair(memory["span_minute"], "PREDICTION_SPAN_INVALID")
        _require(start < end <= 1440, "PREDICTION_SPAN_INVALID", memory_id)
        for key in ("semantic_atoms", "asserted_atoms", "canonical_concept_ids", "entity_ids"):
            _string_list(memory[key], "PREDICTION_LIST_INVALID")
        _require(isinstance(memory["media"], list), "PREDICTION_MEDIA_INVALID", memory_id)
        media_ids: Set[str] = set()
        for media in memory["media"]:
            _require(isinstance(media, Mapping), "PREDICTION_MEDIA_INVALID", memory_id)
            _require_keys(media, ("media_id", "semantic_atom", "format", "is_hero"), "PREDICTION_MEDIA_INVALID")
            media_id = str(media["media_id"])
            _require(
                isinstance(media["media_id"], str) and bool(media["media_id"].strip()),
                "PREDICTION_MEDIA_INVALID",
                media_id,
            )
            _require(media_id not in media_ids, "DUPLICATE_PREDICTION_MEDIA_ID", media_id)
            media_ids.add(media_id)
            _require(media["format"] in MEDIA_FORMATS, "PREDICTION_MEDIA_FORMAT_INVALID", media_id)
            _require(type(media["is_hero"]) is bool, "PREDICTION_HERO_INVALID", media_id)
            _require(
                isinstance(media["semantic_atom"], str)
                and bool(media["semantic_atom"].strip()),
                "PREDICTION_MEDIA_ATOM_INVALID",
                media_id,
            )
        _require(isinstance(memory["narrative"], Mapping), "PREDICTION_NARRATIVE_INVALID", memory_id)
        for key, value in memory["narrative"].items():
            _require(
                key
                in (
                    "title",
                    "story",
                    "moment_line",
                    "time_label",
                    "title_soft_extension_reason",
                    "second_sentence_increment_atom",
                )
                and isinstance(value, str),
                "PREDICTION_NARRATIVE_INVALID",
                f"{memory_id}:{key}",
            )
    expected = raw_trial["expected_evaluation"]
    _require(isinstance(expected, Mapping), "EXPECTED_EVALUATION_INVALID", str(raw_trial["trial_id"]))
    _require_keys(expected, ("status", "required_error_codes"), "EXPECTED_EVALUATION_INVALID")
    _require(expected["status"] in EXPECTED_STATUSES, "EXPECTED_STATUS_INVALID", str(raw_trial["trial_id"]))
    required_error_codes = _string_list(
        expected["required_error_codes"], "EXPECTED_ERROR_CODES_INVALID"
    )
    if raw_trial["trial_kind"] == "FAILURE_INJECTION":
        _require(
            expected["status"] in ("QUALITY_FAIL", "BLOCKING_FAIL")
            and bool(required_error_codes),
            "FAILURE_INJECTION_EXPECTATION_INVALID",
            str(raw_trial["trial_id"]),
        )
    else:
        _require(
            expected["status"] in ("PASS", "REVIEW"),
            "NOMINAL_EXPECTATION_INVALID",
            str(raw_trial["trial_id"]),
        )


def _gold_span_coverage_ratio(
    gold_span: Sequence[object], predicted_span: Sequence[object]
) -> float:
    gold_start, gold_end = int(gold_span[0]), int(gold_span[1])
    predicted_start, predicted_end = int(predicted_span[0]), int(predicted_span[1])
    intersection = max(
        0,
        min(gold_end, predicted_end) - max(gold_start, predicted_start),
    )
    return intersection / max(1, gold_end - gold_start)


def _eligible(gold: Mapping[str, object], predicted: Mapping[str, object]) -> bool:
    if gold["memory_type"] != predicted["memory_type"]:
        return False
    if not (set(map(str, gold["identity_atoms"])) & set(map(str, predicted["semantic_atoms"]))):
        return False
    return _gold_span_coverage_ratio(gold["acceptable_span_minute"], predicted["span_minute"]) >= float(
        gold["minimum_overlap_ratio"]
    )


def _correspondence(
    gold_memories: Sequence[Mapping[str, object]],
    predicted_memories: Sequence[Mapping[str, object]],
) -> Dict[int, int]:
    """Find a deterministic correspondence without treating it as a quality score."""

    eligible: Dict[int, List[int]] = {
        gold_index: [
            predicted_index
            for predicted_index, predicted in enumerate(predicted_memories)
            if _eligible(gold, predicted)
        ]
        for gold_index, gold in enumerate(gold_memories)
    }
    def contribution(gold_index: int, predicted_index: int) -> Tuple[int, int, int, int, int]:
        gold = gold_memories[gold_index]
        predicted = predicted_memories[predicted_index]
        predicted_atoms = set(map(str, predicted["semantic_atoms"]))
        return (
            1 if gold["requirement"] == "REQUIRED" else 0,
            1,
            len(set(map(str, gold["identity_atoms"])) & predicted_atoms),
            len(set(map(str, gold["required_atoms"])) & predicted_atoms),
            int(
                _gold_span_coverage_ratio(
                    gold["acceptable_span_minute"], predicted["span_minute"]
                )
                * 1_000_000
            ),
        )

    def add_objectives(
        first: Tuple[int, int, int, int, int],
        second: Tuple[int, int, int, int, int],
    ) -> Tuple[int, int, int, int, int]:
        return tuple(left + right for left, right in zip(first, second))  # type: ignore[return-value]

    @lru_cache(maxsize=None)
    def search(
        gold_index: int, used_prediction_mask: int
    ) -> Tuple[Tuple[int, int, int, int, int], Tuple[Tuple[int, int], ...]]:
        if gold_index == len(gold_memories):
            return (0, 0, 0, 0, 0), ()
        best_objective, best_pairs = search(gold_index + 1, used_prediction_mask)
        for predicted_index in eligible[gold_index]:
            prediction_bit = 1 << predicted_index
            if used_prediction_mask & prediction_bit:
                continue
            suffix_objective, suffix_pairs = search(
                gold_index + 1,
                used_prediction_mask | prediction_bit,
            )
            candidate_objective = add_objectives(
                contribution(gold_index, predicted_index), suffix_objective
            )
            candidate_pairs = ((gold_index, predicted_index),) + suffix_pairs
            if candidate_objective > best_objective or (
                candidate_objective == best_objective
                and candidate_pairs < best_pairs
            ):
                best_objective = candidate_objective
                best_pairs = candidate_pairs
        return best_objective, best_pairs

    _objective, pairs = search(0, 0)
    return dict(pairs)


def _issue(
    severity: str,
    dimension: str,
    code: str,
    detail: str,
    gold_memory_id: Optional[str] = None,
    prediction_memory_id: Optional[str] = None,
) -> Dict[str, object]:
    issue: Dict[str, object] = {
        "severity": severity,
        "dimension": dimension,
        "code": code,
        "detail": detail,
    }
    if gold_memory_id is not None:
        issue["gold_memory_id"] = gold_memory_id
    if prediction_memory_id is not None:
        issue["prediction_memory_id"] = prediction_memory_id
    return issue


def _sentence_count(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, sum(stripped.count(mark) for mark in "。！？!?"))


def _visible_length(text: str) -> int:
    return sum(1 for character in text if not character.isspace())


def evaluate_trial(
    day: Mapping[str, object],
    trial: Mapping[str, object],
) -> Dict[str, object]:
    gold = day["gold"]
    prediction = trial["prediction"]
    gold_memories = list(gold["memories"])
    predicted_memories = list(prediction["memories"])
    evidence_atoms = {
        str(atom)
        for window in day["timeline"]
        if window["evidence_support"] in ("STRONG", "MODERATE")
        for atom in window["semantic_atoms"]
    }
    issues: List[Dict[str, object]] = []

    if prediction["day_state"] != gold["day_state"]:
        issues.append(
            _issue(
                "QUALITY",
                "MEMORY_IDENTITY_AND_BOUNDARY",
                "DAY_STATE_MISMATCH",
                f"expected {gold['day_state']}, got {prediction['day_state']}",
            )
        )
    chapter_count = sum(1 for memory in predicted_memories if memory["memory_type"] == "CHAPTER")
    aha_count = sum(1 for memory in predicted_memories if memory["memory_type"] == "AHA")
    if chapter_count > 5 or aha_count > 3:
        issues.append(
            _issue(
                "BLOCKING",
                "MEMORY_IDENTITY_AND_BOUNDARY",
                "OUTPUT_CAPACITY_EXCEEDED",
                f"chapters={chapter_count}, aha={aha_count}",
            )
        )
    state_shape_valid = (
        prediction["day_state"] == "CHAPTER_DAY" and 1 <= chapter_count <= 5 and aha_count <= 3
    ) or (
        prediction["day_state"] == "HIGHLIGHT_DAY" and chapter_count == 0 and aha_count == 1
    ) or (
        prediction["day_state"] == "EMPTY_DAY" and chapter_count == 0 and aha_count == 0
    )
    if not state_shape_valid:
        issues.append(
            _issue(
                "BLOCKING",
                "MEMORY_IDENTITY_AND_BOUNDARY",
                "DAY_STATE_OUTPUT_SHAPE_INVALID",
                f"{prediction['day_state']}:chapters={chapter_count},aha={aha_count}",
            )
        )
    for count, range_value, label in (
        (chapter_count, gold["chapter_count_range"], "CHAPTER"),
        (aha_count, gold["aha_count_range"], "AHA"),
    ):
        minimum, maximum = map(int, range_value)
        if not minimum <= count <= maximum:
            issues.append(
                _issue(
                    "QUALITY",
                    "MEMORY_IDENTITY_AND_BOUNDARY",
                    f"{label}_COUNT_OUTSIDE_GOLD_RANGE",
                    f"expected {minimum}..{maximum}, got {count}",
                )
            )

    for predicted in predicted_memories:
        predicted_id = str(predicted["memory_id"])
        predicted_atoms = set(map(str, predicted["semantic_atoms"]))
        for atom in sorted(set(map(str, predicted["semantic_atoms"])) - evidence_atoms):
            issues.append(
                _issue(
                    "BLOCKING",
                    "TRUTH",
                    "UNSUPPORTED_MEMORY_ATOM",
                    atom,
                    prediction_memory_id=predicted_id,
                )
            )
        for atom in sorted(set(map(str, predicted["asserted_atoms"])) - evidence_atoms):
            issues.append(
                _issue(
                    "BLOCKING",
                    "TRUTH",
                    "UNSUPPORTED_ASSERTION",
                    atom,
                    prediction_memory_id=predicted_id,
                )
            )
        for media in predicted["media"]:
            media_atom = str(media["semantic_atom"])
            if media_atom not in evidence_atoms:
                issues.append(
                    _issue(
                        "BLOCKING",
                        "TRUTH",
                        "UNSUPPORTED_MEDIA_ATOM",
                        media_atom,
                        prediction_memory_id=predicted_id,
                    )
                )
            elif media_atom not in predicted_atoms:
                issues.append(
                    _issue(
                        "QUALITY",
                        "MEDIA_EDITORIAL",
                        "MEDIA_MEMORY_ALIGNMENT_INVALID",
                        media_atom,
                        prediction_memory_id=predicted_id,
                    )
                )

    media_owners: Dict[str, List[str]] = {}
    for predicted in predicted_memories:
        for media in predicted["media"]:
            media_owners.setdefault(str(media["media_id"]), []).append(
                str(predicted["memory_id"])
            )
    for media_id, owners in sorted(media_owners.items()):
        if len(owners) > 1:
            issues.append(
                _issue(
                    "QUALITY",
                    "MEDIA_EDITORIAL",
                    "CROSS_MEMORY_MEDIA_REUSE",
                    f"{media_id}:{','.join(owners)}",
                )
            )
    required_gold = [
        (index, memory)
        for index, memory in enumerate(gold_memories)
        if memory["requirement"] == "REQUIRED"
    ]
    for predicted in predicted_memories:
        eligible_required = [
            gold_memory
            for _index, gold_memory in required_gold
            if _eligible(gold_memory, predicted)
        ]
        identity_owners = [
            gold_memory
            for gold_memory in eligible_required
            if set(map(str, gold_memory["identity_atoms"]))
            & set(map(str, predicted["semantic_atoms"]))
        ]
        if len(identity_owners) > 1:
            issues.append(
                _issue(
                    "BLOCKING",
                    "MEMORY_IDENTITY_AND_BOUNDARY",
                    "FALSE_MERGE",
                    ",".join(str(memory["gold_memory_id"]) for memory in identity_owners),
                    prediction_memory_id=str(predicted["memory_id"]),
                )
            )

    mapping = _correspondence(gold_memories, predicted_memories)
    matched_prediction_indexes = set(mapping.values())
    mapping_by_gold_id = {
        str(gold_memories[gold_index]["gold_memory_id"]): predicted_memories[predicted_index]
        for gold_index, predicted_index in mapping.items()
    }
    matches: List[Dict[str, object]] = []

    for gold_index, gold_memory in enumerate(gold_memories):
        gold_id = str(gold_memory["gold_memory_id"])
        if gold_index not in mapping:
            if gold_memory["requirement"] == "REQUIRED":
                issues.append(
                    _issue(
                        "QUALITY",
                        "MEMORY_IDENTITY_AND_BOUNDARY",
                        "MISSING_REQUIRED_MEMORY",
                        gold_id,
                        gold_memory_id=gold_id,
                    )
                )
            else:
                issues.append(
                    _issue(
                        "REVIEW",
                        "MEMORY_IDENTITY_AND_BOUNDARY",
                        "OPTIONAL_MEMORY_REVIEW",
                        gold_id,
                        gold_memory_id=gold_id,
                    )
                )
            continue
        predicted = predicted_memories[mapping[gold_index]]
        predicted_id = str(predicted["memory_id"])
        matches.append(
            {
                "gold_memory_id": gold_id,
                "prediction_memory_id": predicted_id,
                "correspondence_basis": "TYPE+IDENTITY_ATOM+TEMPORAL_OVERLAP",
                "gold_span_coverage_ratio": round(
                    _gold_span_coverage_ratio(
                        gold_memory["acceptable_span_minute"],
                        predicted["span_minute"],
                    ),
                    6,
                ),
            }
        )
        predicted_atoms = set(map(str, predicted["semantic_atoms"]))
        missing_atoms = set(map(str, gold_memory["required_atoms"])) - predicted_atoms
        for atom in sorted(missing_atoms):
            issues.append(
                _issue(
                    "QUALITY",
                    "MEMORY_IDENTITY_AND_BOUNDARY",
                    "REQUIRED_MEMORY_ATOM_MISSING",
                    atom,
                    gold_id,
                    predicted_id,
                )
            )
        forbidden_atoms = set(map(str, gold_memory["forbidden_atoms"]))
        present_forbidden = forbidden_atoms & (
            predicted_atoms | set(map(str, predicted["asserted_atoms"]))
        )
        for atom in sorted(present_forbidden):
            issues.append(
                _issue(
                    "BLOCKING",
                    "TRUTH",
                    "FORBIDDEN_MEMORY_ATOM",
                    atom,
                    gold_id,
                    predicted_id,
                )
            )
        predicted_concepts = set(map(str, predicted["canonical_concept_ids"]))
        required_concepts = set(map(str, gold_memory["required_concept_ids"]))
        allowed_concepts = set(map(str, gold_memory["allowed_concept_ids"]))
        forbidden_concepts = set(map(str, gold_memory["forbidden_concept_ids"]))
        for concept in sorted(required_concepts - predicted_concepts):
            issues.append(
                _issue(
                    "QUALITY",
                    "MEMORY_INDEX",
                    "REQUIRED_CONCEPT_MISSING",
                    concept,
                    gold_id,
                    predicted_id,
                )
            )
        for concept in sorted(predicted_concepts - allowed_concepts - forbidden_concepts):
            issues.append(
                _issue(
                    "BLOCKING",
                    "MEMORY_INDEX",
                    "UNAPPROVED_CANONICAL_CONCEPT",
                    concept,
                    gold_id,
                    predicted_id,
                )
            )
        for concept in sorted(predicted_concepts & forbidden_concepts):
            issues.append(
                _issue(
                    "BLOCKING",
                    "MEMORY_INDEX",
                    "FORBIDDEN_CANONICAL_CONCEPT",
                    concept,
                    gold_id,
                    predicted_id,
                )
            )
        predicted_entities = set(map(str, predicted["entity_ids"]))
        allowed_entities = set(map(str, gold_memory["allowed_entity_ids"]))
        for entity in sorted(predicted_entities - allowed_entities):
            issues.append(
                _issue(
                    "BLOCKING",
                    "MEMORY_INDEX",
                    "UNAPPROVED_ENTITY",
                    entity,
                    gold_id,
                    predicted_id,
                )
            )
        _evaluate_media(gold_memory, predicted, issues)
        _evaluate_narrative(gold_memory, predicted, issues)

    for predicted_index, predicted in enumerate(predicted_memories):
        if predicted_index in matched_prediction_indexes:
            continue
        predicted_id = str(predicted["memory_id"])
        atoms = set(map(str, predicted["semantic_atoms"]))
        matched_pattern = None
        for pattern in gold["forbidden_memory_patterns"]:
            if pattern["memory_type"] == predicted["memory_type"] and (
                atoms & set(map(str, pattern["any_atoms"]))
            ):
                matched_pattern = pattern
                break
        if matched_pattern is not None:
            issues.append(
                _issue(
                    "BLOCKING",
                    "CHAPTER_AHA_INDEPENDENCE",
                    str(matched_pattern["error_code"]),
                    predicted_id,
                    prediction_memory_id=predicted_id,
                )
            )
            continue
        fragment_gold = [
            memory
            for memory in gold_memories
            if memory["memory_type"] == predicted["memory_type"]
            and set(map(str, memory["identity_atoms"]))
            & set(map(str, predicted["semantic_atoms"]))
            and _gold_span_coverage_ratio(
                memory["acceptable_span_minute"], predicted["span_minute"]
            )
            > 0
        ]
        if fragment_gold:
            issues.append(
                _issue(
                    "QUALITY",
                    "MEMORY_IDENTITY_AND_BOUNDARY",
                    "FALSE_SPLIT",
                    ",".join(str(memory["gold_memory_id"]) for memory in fragment_gold),
                    prediction_memory_id=predicted_id,
                )
            )
        else:
            issues.append(
                _issue(
                    "BLOCKING",
                    "MEMORY_IDENTITY_AND_BOUNDARY",
                    "FALSE_MEMORY",
                    predicted_id,
                    prediction_memory_id=predicted_id,
                )
            )

    for pair in gold["distinct_story_pairs"]:
        chapter = mapping_by_gold_id.get(str(pair["chapter_gold_id"]))
        aha = mapping_by_gold_id.get(str(pair["aha_gold_id"]))
        if chapter is None or aha is None:
            continue
        chapter_atoms = set(map(str, chapter["semantic_atoms"])) | set(
            map(str, chapter["asserted_atoms"])
        )
        aha_atoms = set(map(str, aha["semantic_atoms"])) | set(
            map(str, aha["asserted_atoms"])
        )
        cross_atoms = (
            chapter_atoms & set(map(str, pair["chapter_forbidden_atoms"]))
        ) | (aha_atoms & set(map(str, pair["aha_forbidden_atoms"])))
        if cross_atoms:
            issues.append(
                _issue(
                    "BLOCKING",
                    "CHAPTER_AHA_INDEPENDENCE",
                    "DISTINCT_STORY_CONTAMINATION",
                    ",".join(sorted(cross_atoms)),
                )
            )

    issues.sort(
        key=lambda item: (
            SEVERITY_ORDER[str(item["severity"])],
            str(item["dimension"]),
            str(item["code"]),
            str(item.get("gold_memory_id", "")),
            str(item.get("prediction_memory_id", "")),
            str(item["detail"]),
        )
    )
    if any(issue["severity"] == "BLOCKING" for issue in issues):
        status = "BLOCKING_FAIL"
    elif any(issue["severity"] == "QUALITY" for issue in issues):
        status = "QUALITY_FAIL"
    elif any(issue["severity"] == "REVIEW" for issue in issues):
        status = "REVIEW"
    else:
        status = "PASS"
    dimension_results = {}
    for dimension in DIMENSIONS:
        dimension_issues = [issue for issue in issues if issue["dimension"] == dimension]
        if any(issue["severity"] == "BLOCKING" for issue in dimension_issues):
            dimension_status = "BLOCKING_FAIL"
        elif any(issue["severity"] == "QUALITY" for issue in dimension_issues):
            dimension_status = "QUALITY_FAIL"
        elif any(issue["severity"] == "REVIEW" for issue in dimension_issues):
            dimension_status = "REVIEW"
        else:
            dimension_status = "PASS"
        dimension_results[dimension] = {
            "status": dimension_status,
            "issue_codes": [str(issue["code"]) for issue in dimension_issues],
        }
    required_gold_count = sum(
        1 for memory in gold_memories if memory["requirement"] == "REQUIRED"
    )
    matched_required_count = sum(
        1
        for gold_index in mapping
        if gold_memories[gold_index]["requirement"] == "REQUIRED"
    )
    return {
        "trial_id": trial["trial_id"],
        "day_id": day["day_id"],
        "trial_kind": trial["trial_kind"],
        "evaluation_status": status,
        "accuracy_claim_eligible": bool(gold["accuracy_eligible"]),
        "matches": sorted(matches, key=lambda item: str(item["gold_memory_id"])),
        "issues": issues,
        "dimension_results": dimension_results,
        "independent_metrics": {
            "required_gold_memory_count": required_gold_count,
            "matched_required_memory_count": matched_required_count,
            "unmatched_prediction_count": len(predicted_memories) - len(matched_prediction_indexes),
            "blocking_issue_count": sum(1 for issue in issues if issue["severity"] == "BLOCKING"),
            "quality_issue_count": sum(1 for issue in issues if issue["severity"] == "QUALITY"),
            "review_issue_count": sum(1 for issue in issues if issue["severity"] == "REVIEW"),
        },
        "human_review_prompts": copy.deepcopy(day["human_review_prompts"]),
        "no_overall_score": True,
    }


def _evaluate_media(
    gold: Mapping[str, object],
    predicted: Mapping[str, object],
    issues: List[Dict[str, object]],
) -> None:
    gold_id = str(gold["gold_memory_id"])
    predicted_id = str(predicted["memory_id"])
    media = predicted["media"]
    minimum, maximum = map(int, gold["media_count_range"])
    if not minimum <= len(media) <= maximum:
        issues.append(
            _issue(
                "QUALITY",
                "MEDIA_EDITORIAL",
                "MEDIA_COUNT_INVALID",
                f"expected {minimum}..{maximum}, got {len(media)}",
                gold_id,
                predicted_id,
            )
        )
    media_atoms = [str(item["semantic_atom"]) for item in media]
    for atom in sorted(set(map(str, gold["required_media_atoms"])) - set(media_atoms)):
        issues.append(
            _issue(
                "QUALITY",
                "MEDIA_EDITORIAL",
                "REQUIRED_MEDIA_ATOM_MISSING",
                atom,
                gold_id,
                predicted_id,
            )
        )
    if len(media_atoms) != len(set(media_atoms)):
        issues.append(
            _issue(
                "QUALITY",
                "MEDIA_EDITORIAL",
                "MEDIA_SEMANTIC_DUPLICATE",
                predicted_id,
                gold_id,
                predicted_id,
            )
        )
    allowed_formats = set(map(str, gold["allowed_media_formats"]))
    for item in media:
        if item["format"] not in allowed_formats:
            issues.append(
                _issue(
                    "QUALITY",
                    "MEDIA_EDITORIAL",
                    "MEDIA_FORMAT_INVALID",
                    str(item["format"]),
                    gold_id,
                    predicted_id,
                )
            )
    hero_count = sum(1 for item in media if item["is_hero"])
    expected_heroes = 1 if predicted["memory_type"] == "CHAPTER" else 0
    if hero_count != expected_heroes:
        issues.append(
            _issue(
                "QUALITY",
                "MEDIA_EDITORIAL",
                "HERO_COUNT_INVALID",
                f"expected {expected_heroes}, got {hero_count}",
                gold_id,
                predicted_id,
            )
        )


def _evaluate_narrative(
    gold: Mapping[str, object],
    predicted: Mapping[str, object],
    issues: List[Dict[str, object]],
) -> None:
    gold_id = str(gold["gold_memory_id"])
    predicted_id = str(predicted["memory_id"])
    narrative = predicted["narrative"]
    if predicted["memory_type"] == "CHAPTER":
        title = str(narrative.get("title") or "").strip()
        story = str(narrative.get("story") or "").strip()
        if not title:
            issues.append(
                _issue(
                    "REVIEW",
                    "NARRATIVE_CONTRACT",
                    "TITLE_POLICY_REVIEW_D2E",
                    predicted_id,
                    gold_id,
                    predicted_id,
                )
            )
        elif not 2 <= _visible_length(title) <= 12:
            issues.append(
                _issue(
                    "QUALITY",
                    "NARRATIVE_CONTRACT",
                    "CHAPTER_TITLE_LENGTH_INVALID",
                    title,
                    gold_id,
                    predicted_id,
                )
            )
        elif _visible_length(title) > 10 and not str(
            narrative.get("title_soft_extension_reason") or ""
        ).strip():
            issues.append(
                _issue(
                    "QUALITY",
                    "NARRATIVE_CONTRACT",
                    "TITLE_SOFT_EXTENSION_REASON_MISSING",
                    title,
                    gold_id,
                    predicted_id,
                )
            )
        sentence_count = _sentence_count(story)
        if sentence_count not in (1, 2):
            issues.append(
                _issue(
                    "QUALITY",
                    "NARRATIVE_CONTRACT",
                    "CHAPTER_STORY_SENTENCE_COUNT_INVALID",
                    story,
                    gold_id,
                    predicted_id,
                )
            )
        elif sentence_count == 2:
            increment_atom = str(
                narrative.get("second_sentence_increment_atom") or ""
            ).strip()
            if not increment_atom:
                issues.append(
                    _issue(
                        "QUALITY",
                        "NARRATIVE_CONTRACT",
                        "SECOND_SENTENCE_INCREMENT_MISSING",
                        predicted_id,
                        gold_id,
                        predicted_id,
                    )
                )
            elif increment_atom not in set(map(str, predicted["semantic_atoms"])):
                issues.append(
                    _issue(
                        "BLOCKING",
                        "TRUTH",
                        "SECOND_SENTENCE_INCREMENT_UNGROUNDED",
                        increment_atom,
                        gold_id,
                        predicted_id,
                    )
                )
        if narrative.get("moment_line"):
            issues.append(
                _issue(
                    "QUALITY",
                    "NARRATIVE_CONTRACT",
                    "CHAPTER_HAS_AHA_SURFACE",
                    predicted_id,
                    gold_id,
                    predicted_id,
                )
            )
    else:
        line = str(narrative.get("moment_line") or "").strip()
        if not 1 <= _visible_length(line) <= 20:
            issues.append(
                _issue(
                    "QUALITY",
                    "NARRATIVE_CONTRACT",
                    "AHA_MOMENT_LINE_LENGTH_INVALID",
                    line,
                    gold_id,
                    predicted_id,
                )
            )
        if narrative.get("title") or narrative.get("story"):
            issues.append(
                _issue(
                    "QUALITY",
                    "NARRATIVE_CONTRACT",
                    "AHA_HAS_CHAPTER_SURFACE",
                    predicted_id,
                    gold_id,
                    predicted_id,
                )
            )


def run_validation_suite(payload: Mapping[str, object]) -> Dict[str, object]:
    normalized: Dict[str, object] = copy.deepcopy(dict(payload))
    contract_summary = validate_validation_suite(normalized)
    day_by_id = {str(day["day_id"]): day for day in normalized["days"]}
    results = [
        evaluate_trial(day_by_id[str(trial["day_id"])], trial)
        for trial in normalized["trials"]
    ]
    conformance_results = []
    for trial, result in zip(normalized["trials"], results):
        expected = trial["expected_evaluation"]
        actual_codes = {str(issue["code"]) for issue in result["issues"]}
        missing_codes = sorted(set(map(str, expected["required_error_codes"])) - actual_codes)
        passed = result["evaluation_status"] == expected["status"] and not missing_codes
        conformance_results.append(
            {
                "trial_id": trial["trial_id"],
                "expected_status": expected["status"],
                "actual_status": result["evaluation_status"],
                "missing_required_error_codes": missing_codes,
                "status": "PASS" if passed else "FAIL",
            }
        )
    status_counts = {
        status: sum(1 for result in results if result["evaluation_status"] == status)
        for status in EXPECTED_STATUSES
    }
    error_code_counts: Dict[str, int] = {}
    for result in results:
        for issue in result["issues"]:
            code = str(issue["code"])
            error_code_counts[code] = error_code_counts.get(code, 0) + 1
    scorecard = {
        "contract_version": SCORECARD_CONTRACT_VERSION,
        "suite_id": normalized["suite_id"],
        "narrative_locale": normalized["narrative_locale"],
        "input_fingerprint": _fingerprint(normalized),
        "contract_summary": contract_summary,
        "scope": {
            "validated": [
                "DAY_LEVEL_GOLD_CONTRACT",
                "SELECTED_DAY_STATE_AND_MEMORY_INVARIANTS",
                "DECLARED_CLAIM_GROUNDING",
                "MEDIA_AND_NARRATIVE_SHAPE",
                "EVALUATOR_FAILURE_ATTRIBUTION",
            ],
            "not_validated": [
                "REAL_MEDIA_PERCEPTION_ACCURACY",
                "S00_S10_STAGE_ENGINE_ACCURACY",
                "REAL_WRITER_NATURALNESS",
                "NARRATIVE_SURFACE_TO_ASSERTION_EXTRACTION",
                "FULL_S11_CLAIM_LEDGER_AND_TONE_PERMISSION",
                "REAL_COST_OR_LATENCY",
                "CLOUD_PRODUCTION_READINESS",
            ],
        },
        "accuracy_claim_status": (
            "HUMAN_GOLD_PRESENT_SEPARATE_REPORT_REQUIRED"
            if contract_summary["human_gold_day_count"]
            else "NOT_ELIGIBLE_DESIGN_GOLD_ONLY"
        ),
        "aggregate": {
            "day_count": contract_summary["day_count"],
            "trial_count": contract_summary["trial_count"],
            "evaluation_status_counts": status_counts,
            "error_code_counts": dict(sorted(error_code_counts.items())),
            "conformance_pass_count": sum(
                1 for item in conformance_results if item["status"] == "PASS"
            ),
            "conformance_fail_count": sum(
                1 for item in conformance_results if item["status"] == "FAIL"
            ),
        },
        "conformance_results": conformance_results,
        "trial_results": results,
        "no_overall_score": True,
        "frozen_pipeline_mutation_by_validation_run": False,
        "status": (
            "VALIDATION_SUITE_PASS"
            if all(item["status"] == "PASS" for item in conformance_results)
            else "VALIDATION_SUITE_FAIL"
        ),
    }
    scorecard["fingerprint"] = _fingerprint(scorecard)
    return scorecard


def write_validation_scorecard(
    payload: Mapping[str, object], artifacts_root: Path
) -> Path:
    scorecard = run_validation_suite(payload)
    output_dir = artifacts_root / (
        f"validation_v01_{scorecard['suite_id']}_{scorecard['input_fingerprint'][:12]}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(output_dir / "validation_suite.snapshot.json", payload)
    _atomic_write_json(output_dir / "validation_scorecard.json", scorecard)
    return output_dir
