"""Production-shaped Diary One V1 control-plane reference.

This module is deliberately media-free.  It validates immutable S00-S10
handoffs, executes the frozen S11 indexing/narrative contract, performs S12's
two validation phases, simulates only predeclared S13 materialization routes,
and writes deterministic reference artifacts.  It is not a cloud deployment,
a perception model, or an HQ media renderer.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Set, Tuple


PIPELINE_CONTRACT_VERSION = "DIARY_ONE_PRODUCTION_PIPELINE_V1_0"
S11_CONTRACT_VERSION = "DIARY_ONE_S11_GROUNDED_NARRATIVE_V1_0"
S12_CONTRACT_VERSION = "DIARY_ONE_S12_TWO_PHASE_VALIDATION_V1_0"
S13_CONTRACT_VERSION = "DIARY_ONE_S13_MATERIALIZATION_EXPORT_V1_0"
REGISTRY_CONTRACT_VERSION = "DIARY_ONE_CANONICAL_CONCEPT_REGISTRY_V1_0"

UPSTREAM_STAGES = tuple(f"S{index:02d}" for index in range(11))
FACETS = ("ACTIVITY", "SETTING", "CENTRAL_SUBJECT", "OCCASION")
MEMORY_TYPES = ("CHAPTER", "AHA")
DAY_STATES = ("CHAPTER_DAY", "HIGHLIGHT_DAY", "EMPTY_DAY")
MEDIA_FORMATS = ("PHOTO", "LIVE_2S", "VIDEO_5S")
ENTITY_TYPES = ("PLACE", "PERSON", "PET", "VENUE", "OTHER_NAMED_ENTITY")
ROUTE_OUTCOMES = (
    "SUCCESS",
    "TRANSIENT_FAILURE",
    "TERMINAL_FAILURE",
    "CONTRACT_INVALID",
)
UNSUPPORTED_AFFECT_TOKENS = ("幸福", "难忘", "惊喜", "治愈", "好吃", "最爱")
LIGHT_AFFECT_POLICIES = {
    "LIGHT_AFFECT.CAT_PLAYFUL_V1": ("调皮", "CENTRAL_SUBJECT.CAT"),
    "LIGHT_AFFECT.DOG_LIVELY_V1": ("活泼", "CENTRAL_SUBJECT.DOG"),
}


class PipelineContractError(ValueError):
    """A versioned stage contract is missing, inconsistent, or unsafe."""

    def __init__(self, stage: str, code: str, detail: str):
        super().__init__(f"{stage}:{code}: {detail}")
        self.stage = stage
        self.code = code
        self.detail = detail


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _fingerprint(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require(condition: bool, stage: str, code: str, detail: str) -> None:
    if not condition:
        raise PipelineContractError(stage, code, detail)


def _require_keys(value: Mapping[str, object], keys: Iterable[str], stage: str, code: str) -> None:
    missing = [key for key in keys if key not in value]
    _require(not missing, stage, code, f"missing required keys: {', '.join(missing)}")


def _visible_length(text: str) -> int:
    return sum(1 for char in text if not char.isspace())


def _sentence_count(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    boundaries = sum(stripped.count(mark) for mark in "。！？!?" )
    return max(1, boundaries)


def _atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@dataclass(frozen=True)
class Concept:
    concept_id: str
    facet: str
    parent_id: Optional[str]
    labels: Mapping[str, str]
    active: bool


class CanonicalConceptRegistry:
    """Closed, versioned, locale-neutral concept registry."""

    def __init__(self, payload: Mapping[str, object]):
        _require(
            payload.get("registry_contract_version") == REGISTRY_CONTRACT_VERSION,
            "S11",
            "REGISTRY_VERSION_MISMATCH",
            "unsupported Canonical Concept Registry version",
        )
        concepts: Dict[str, Concept] = {}
        for raw in payload.get("concepts", []):
            _require(isinstance(raw, Mapping), "S11", "REGISTRY_CONCEPT_INVALID", "concept must be an object")
            _require_keys(raw, ("concept_id", "facet", "labels", "active"), "S11", "REGISTRY_CONCEPT_INVALID")
            concept_id = str(raw["concept_id"])
            facet = str(raw["facet"])
            _require(facet in FACETS, "S11", "REGISTRY_FACET_INVALID", f"{concept_id}: {facet}")
            _require(concept_id not in concepts, "S11", "REGISTRY_DUPLICATE_CONCEPT", concept_id)
            labels = raw["labels"]
            _require(isinstance(labels, Mapping), "S11", "REGISTRY_LABELS_INVALID", concept_id)
            concepts[concept_id] = Concept(
                concept_id=concept_id,
                facet=facet,
                parent_id=(str(raw["parent_id"]) if raw.get("parent_id") else None),
                labels={str(key): str(value) for key, value in labels.items()},
                active=bool(raw["active"]),
            )
        _require(bool(concepts), "S11", "REGISTRY_EMPTY", "registry must contain concepts")
        for concept in concepts.values():
            if concept.parent_id:
                _require(concept.parent_id in concepts, "S11", "REGISTRY_PARENT_MISSING", concept.concept_id)
                _require(
                    concepts[concept.parent_id].facet == concept.facet,
                    "S11",
                    "REGISTRY_CROSS_FACET_PARENT",
                    concept.concept_id,
                )
        self._concepts = concepts
        self._validate_acyclic()
        self.version = str(payload.get("registry_version", "UNVERSIONED"))

    @classmethod
    def from_path(cls, path: Path) -> "CanonicalConceptRegistry":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def _validate_acyclic(self) -> None:
        for concept_id in self._concepts:
            seen: Set[str] = set()
            cursor: Optional[str] = concept_id
            while cursor:
                _require(cursor not in seen, "S11", "REGISTRY_CYCLE", concept_id)
                seen.add(cursor)
                cursor = self._concepts[cursor].parent_id

    def require_active(self, concept_id: str) -> Concept:
        _require(concept_id in self._concepts, "S11", "UNREGISTERED_CONCEPT", concept_id)
        concept = self._concepts[concept_id]
        _require(concept.active, "S11", "INACTIVE_CONCEPT", concept_id)
        return concept

    def label(self, concept_id: str, locale: str) -> Optional[str]:
        return self.require_active(concept_id).labels.get(locale)


class ProductionPipelineV1:
    """Deterministic reference orchestrator for the S00-S13 V1 contracts."""

    def __init__(self, registry: CanonicalConceptRegistry):
        self.registry = registry

    @classmethod
    def from_registry_path(cls, registry_path: Path) -> "ProductionPipelineV1":
        return cls(CanonicalConceptRegistry.from_path(registry_path))

    def validate(self, payload: Mapping[str, object]) -> Dict[str, object]:
        normalized = copy.deepcopy(dict(payload))
        run = self._validate_envelope(normalized)
        upstream_trace = self._validate_upstream_lineage(normalized, run)
        memories = self._validate_memories_input(normalized, run)
        writer_provenance = self._validate_writer_provenance(normalized)
        s11 = self._execute_s11(memories, run, writer_provenance)
        s12_pre = self._execute_s12_pre(normalized, s11, run)
        return {
            "contract_version": PIPELINE_CONTRACT_VERSION,
            "input_fingerprint": _fingerprint(normalized),
            "run": copy.deepcopy(run),
            "upstream_trace": upstream_trace,
            "s11": s11,
            "s12_pre": s12_pre,
            "status": "VALIDATED_FOR_REFERENCE_MATERIALIZATION",
        }

    def run(self, payload: Mapping[str, object], artifacts_root: Path) -> Path:
        validated = self.validate(payload)
        normalized = copy.deepcopy(dict(payload))
        run = validated["run"]
        input_fingerprint = str(validated["input_fingerprint"])
        output_dir = artifacts_root / (
            f"production_v1_{run['user_local_day']}_{run['revision_id']}_{input_fingerprint[:12]}"
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        materialization = self._execute_s13_materialization(
            normalized, validated["s11"], run
        )
        if materialization["status"] == "HOLD":
            run_manifest = self._run_manifest(
                validated,
                materialization,
                activation_validation=None,
                exported=False,
            )
            _atomic_write_json(output_dir / "s11_narrative_bundle.json", validated["s11"])
            _atomic_write_json(output_dir / "s12_pre_materialization_decision.json", validated["s12_pre"])
            _atomic_write_json(output_dir / "s13_materialization_bundle.json", materialization)
            _atomic_write_json(output_dir / "run_manifest.json", run_manifest)
            return output_dir

        activation_validation = self._execute_s12_activation(
            normalized,
            validated["s11"],
            validated["s12_pre"],
            materialization,
            run,
        )
        if activation_validation["status"] != "PASS":
            run_manifest = self._run_manifest(
                validated,
                materialization,
                activation_validation,
                exported=False,
            )
            artifacts = {
                "s11_narrative_bundle.json": validated["s11"],
                "s12_pre_materialization_decision.json": validated["s12_pre"],
                "s13_materialization_bundle.json": materialization,
                "s12_activation_decision.json": activation_validation,
                "run_manifest.json": run_manifest,
            }
            for filename, value in artifacts.items():
                _atomic_write_json(output_dir / filename, value)
            return output_dir
        diary_export = self._build_user_export(
            normalized,
            validated["s11"],
            materialization,
            activation_validation,
            run,
        )
        audit_run = self._build_audit_run(
            validated,
            materialization,
            activation_validation,
            diary_export,
        )
        run_manifest = self._run_manifest(
            validated,
            materialization,
            activation_validation,
            exported=True,
        )

        artifacts = {
            "s11_narrative_bundle.json": validated["s11"],
            "s12_pre_materialization_decision.json": validated["s12_pre"],
            "s13_materialization_bundle.json": materialization,
            "s12_activation_decision.json": activation_validation,
            "user_diary_export.json": diary_export,
            "internal_audit_run.json": audit_run,
            "run_manifest.json": run_manifest,
        }
        for filename, value in artifacts.items():
            _atomic_write_json(output_dir / filename, value)
        return output_dir

    def _validate_envelope(self, payload: MutableMapping[str, object]) -> Mapping[str, object]:
        _require(
            payload.get("contract_version") == PIPELINE_CONTRACT_VERSION,
            "PIPELINE",
            "CONTRACT_VERSION_MISMATCH",
            "unsupported pipeline contract version",
        )
        _require_keys(
            payload,
            (
                "run",
                "upstream_stages",
                "s09",
                "memories",
                "hq_requests",
                "writer_provenance",
            ),
            "PIPELINE",
            "ENVELOPE_INVALID",
        )
        run = payload["run"]
        _require(isinstance(run, Mapping), "S00", "RUN_INVALID", "run must be an object")
        _require_keys(
            run,
            (
                "run_id",
                "user_local_day",
                "revision_id",
                "revision_kind",
                "snapshot_id",
                "pipeline_version",
            ),
            "S00",
            "RUN_INVALID",
        )
        _require(run["revision_kind"] in ("PREVIEW", "FINAL"), "S00", "REVISION_KIND_INVALID", str(run["revision_kind"]))
        return run

    def _validate_upstream_lineage(
        self, payload: Mapping[str, object], run: Mapping[str, object]
    ) -> List[Dict[str, object]]:
        raw_stages = payload["upstream_stages"]
        _require(isinstance(raw_stages, list), "PIPELINE", "UPSTREAM_STAGES_INVALID", "must be an array")
        stage_ids = [str(item.get("stage_id")) for item in raw_stages if isinstance(item, Mapping)]
        _require(tuple(stage_ids) == UPSTREAM_STAGES, "PIPELINE", "UPSTREAM_STAGE_ORDER_INVALID", str(stage_ids))
        trace: List[Dict[str, object]] = []
        for expected, raw in zip(UPSTREAM_STAGES, raw_stages):
            _require(isinstance(raw, Mapping), expected, "STAGE_ARTIFACT_INVALID", "must be an object")
            _require_keys(raw, ("stage_id", "artifact_ref", "revision_id", "snapshot_id", "status", "fingerprint"), expected, "STAGE_ARTIFACT_INVALID")
            _require(raw["revision_id"] == run["revision_id"], expected, "REVISION_MISMATCH", str(raw["revision_id"]))
            _require(raw["snapshot_id"] == run["snapshot_id"], expected, "SNAPSHOT_MISMATCH", str(raw["snapshot_id"]))
            _require(raw["status"] == "READY", expected, "UPSTREAM_NOT_READY", str(raw["status"]))
            trace.append(
                {
                    "stage_id": expected,
                    "artifact_ref": raw["artifact_ref"],
                    "fingerprint": raw["fingerprint"],
                    "execution_mode": "CONTRACT_ADAPTER_VALIDATED",
                    "status": "PASS",
                }
            )
        return trace

    def _validate_writer_provenance(
        self, payload: Mapping[str, object]
    ) -> Dict[str, object]:
        raw = payload["writer_provenance"]
        _require(
            isinstance(raw, Mapping),
            "S11",
            "WRITER_PROVENANCE_INVALID",
            "must be an object",
        )
        _require_keys(
            raw,
            (
                "execution_mode",
                "source_artifact_ref",
                "provider",
                "model",
                "prompt_version",
                "parameter_version",
                "logical_calls",
                "input_tokens",
                "output_tokens",
                "estimated_cost_usd",
                "cache_status",
            ),
            "S11",
            "WRITER_PROVENANCE_INVALID",
        )
        _require(
            raw["execution_mode"] == "REFERENCE_PRECOMPUTED",
            "S11",
            "WRITER_EXECUTION_MODE_INVALID",
            str(raw["execution_mode"]),
        )
        for key in (
            "source_artifact_ref",
            "provider",
            "model",
            "prompt_version",
            "parameter_version",
        ):
            _require(
                bool(str(raw[key]).strip()),
                "S11",
                "WRITER_PROVENANCE_INVALID",
                key,
            )
        for key in ("logical_calls", "input_tokens", "output_tokens"):
            _require(
                int(raw[key]) >= 0,
                "S11",
                "WRITER_PROVENANCE_INVALID",
                key,
            )
        _require(
            float(raw["estimated_cost_usd"]) >= 0,
            "S11",
            "WRITER_PROVENANCE_INVALID",
            "estimated_cost_usd",
        )
        _require(
            raw["cache_status"] in (
                "NOT_APPLICABLE_REFERENCE",
                "REFERENCE_CACHE_HIT",
            ),
            "S11",
            "WRITER_CACHE_STATUS_INVALID",
            str(raw["cache_status"]),
        )
        return copy.deepcopy(dict(raw))

    def _validate_memories_input(
        self, payload: Mapping[str, object], run: Mapping[str, object]
    ) -> List[Mapping[str, object]]:
        memories = payload["memories"]
        _require(isinstance(memories, list), "S11", "MEMORIES_INVALID", "must be an array")
        seen: Set[str] = set()
        seen_candidate_ids: Set[str] = set()
        global_media_ids: Set[str] = set()
        for memory in memories:
            _require(isinstance(memory, Mapping), "S11", "MEMORY_INVALID", "memory must be an object")
            _require_keys(
                memory,
                (
                    "memory_id",
                    "memory_type",
                    "candidate_id",
                    "revision_id",
                    "capture_start_ms",
                    "selected_content_unit_ids",
                    "active_media",
                    "claims",
                    "narrative",
                    "canonical_assignments",
                    "entity_links",
                ),
                "S11",
                "MEMORY_INVALID",
            )
            memory_id = str(memory["memory_id"])
            _require(memory_id not in seen, "S11", "DUPLICATE_MEMORY_ID", memory_id)
            seen.add(memory_id)
            candidate_id = str(memory["candidate_id"])
            _require(
                candidate_id not in seen_candidate_ids,
                "S11",
                "DUPLICATE_CANDIDATE_ID",
                candidate_id,
            )
            seen_candidate_ids.add(candidate_id)
            _require(memory["memory_type"] in MEMORY_TYPES, "S11", "MEMORY_TYPE_INVALID", memory_id)
            _require(memory["revision_id"] == run["revision_id"], "S11", "MEMORY_REVISION_MISMATCH", memory_id)
            _require(int(memory["capture_start_ms"]) >= 0, "S11", "MEMORY_CAPTURE_TIME_INVALID", memory_id)
            selected_units = list(map(str, memory["selected_content_unit_ids"]))
            _require(bool(selected_units), "S11", "MEMORY_SCOPE_EMPTY", memory_id)
            _require(
                len(selected_units) == len(set(selected_units)),
                "S11",
                "DUPLICATE_CONTENT_UNIT_ID",
                memory_id,
            )
            active_media = memory["active_media"]
            _require(
                isinstance(active_media, list),
                "S11",
                "ACTIVE_MEDIA_INVALID",
                memory_id,
            )
            for media in active_media:
                _require(
                    isinstance(media, Mapping) and bool(media.get("media_id")),
                    "S11",
                    "MEDIA_ID_INVALID",
                    memory_id,
                )
                media_id = str(media["media_id"])
                _require(
                    media_id not in global_media_ids,
                    "S11",
                    "DUPLICATE_GLOBAL_MEDIA_ID",
                    media_id,
                )
                global_media_ids.add(media_id)
        return memories

    def _execute_s11(
        self,
        memories: Sequence[Mapping[str, object]],
        run: Mapping[str, object],
        writer_provenance: Mapping[str, object],
    ) -> Dict[str, object]:
        output_memories = [self._validate_and_project_memory(memory) for memory in memories]
        output = {
            "contract_version": S11_CONTRACT_VERSION,
            "revision_id": run["revision_id"],
            "snapshot_id": run["snapshot_id"],
            "registry_version": self.registry.version,
            "locale_profile": "zh-Hans-CN-V1-TEST",
            "writer_provenance": copy.deepcopy(writer_provenance),
            "validation_provenance": {
                "execution_mode": "DETERMINISTIC_LOCAL_REFERENCE",
                "model_calls_executed": 0,
                "validator_contract_version": S11_CONTRACT_VERSION,
            },
            "memories": output_memories,
            "status": "S11_READY_FOR_S12",
            "explicit_deferrals": [
                "TITLE_FAILURE_PRODUCT_POLICY_D2E",
                "ENGLISH_AND_OTHER_LOCALE_RELEASE_NUMBERS",
                "REAL_DATA_THRESHOLD_CALIBRATION",
            ],
        }
        output["fingerprint"] = _fingerprint(output)
        return output

    def _validate_and_project_memory(self, memory: Mapping[str, object]) -> Dict[str, object]:
        memory_id = str(memory["memory_id"])
        claims = memory["claims"]
        _require(isinstance(claims, list) and claims, "S11", "CLAIM_LEDGER_EMPTY", memory_id)
        claim_map: Dict[str, Mapping[str, object]] = {}
        active_media_ids = {
            str(media["media_id"])
            for media in memory["active_media"]
            if isinstance(media, Mapping) and media.get("media_id")
        }
        allowed_surface_names = {
            "TITLE",
            "STORY",
            "AHA_MOMENT_LINE",
            "CANONICAL_TAG",
        }
        for claim in claims:
            _require(isinstance(claim, Mapping), "S11", "CLAIM_INVALID", memory_id)
            _require_keys(
                claim,
                ("claim_id", "normalized_assertion", "semantic_status", "support_grade", "evidence_refs", "allowed_surfaces"),
                "S11",
                "CLAIM_INVALID",
            )
            claim_id = str(claim["claim_id"])
            _require(claim_id not in claim_map, "S11", "DUPLICATE_CLAIM_ID", claim_id)
            _require(claim["semantic_status"] == "CLAIM_SEMANTIC_SUPPORTED", "S11", "CLAIM_NOT_SUPPORTED", claim_id)
            _require(claim["support_grade"] in ("STRONG", "MODERATE"), "S11", "CLAIM_SUPPORT_TOO_WEAK", claim_id)
            _require(bool(claim["evidence_refs"]), "S11", "CLAIM_EVIDENCE_EMPTY", claim_id)
            allowed_surfaces = list(map(str, claim["allowed_surfaces"]))
            _require(
                bool(allowed_surfaces)
                and len(allowed_surfaces) == len(set(allowed_surfaces))
                and set(allowed_surfaces).issubset(allowed_surface_names),
                "S11",
                "CLAIM_ALLOWED_SURFACES_INVALID",
                claim_id,
            )
            required_media_ids = list(
                map(str, claim.get("required_media_ids", []))
            )
            _require(
                len(required_media_ids) == len(set(required_media_ids))
                and set(required_media_ids).issubset(active_media_ids),
                "S11",
                "CLAIM_REQUIRED_MEDIA_INVALID",
                claim_id,
            )
            claim_map[claim_id] = claim

        narrative = memory["narrative"]
        _require(isinstance(narrative, Mapping), "S11", "NARRATIVE_INVALID", memory_id)
        self._validate_narrative(memory, narrative, claim_map, removed_media_ids=set())
        assignments, display_labels = self._validate_assignments(memory, claim_map, str(narrative["locale"]))
        entity_links = self._validate_entity_links(memory, claim_map)

        projected = {
            "memory_id": memory_id,
            "memory_type": memory["memory_type"],
            "candidate_id": memory["candidate_id"],
            "capture_start_ms": int(memory["capture_start_ms"]),
            "selected_content_unit_ids": copy.deepcopy(memory["selected_content_unit_ids"]),
            "claim_ledger": copy.deepcopy(claims),
            "grounded_narrative": copy.deepcopy(narrative),
            "canonical_tag_decisions": assignments,
            "entity_index_links": entity_links,
            "display_label_candidates": display_labels,
            "protected_user_text": copy.deepcopy(memory.get("protected_user_text", [])),
            "active_media": copy.deepcopy(memory["active_media"]),
            "status": "MEMORY_NARRATIVE_READY",
        }
        projected["fingerprint"] = _fingerprint(projected)
        return projected

    def _validate_narrative(
        self,
        memory: Mapping[str, object],
        narrative: Mapping[str, object],
        claim_map: Mapping[str, Mapping[str, object]],
        removed_media_ids: Set[str],
    ) -> None:
        memory_id = str(memory["memory_id"])
        _require_keys(narrative, ("locale", "surface_claim_refs"), "S11", "NARRATIVE_INVALID")
        _require(narrative["locale"] == "zh-Hans", "S11", "LOCALE_NOT_RELEASED", memory_id)
        surface_refs = narrative["surface_claim_refs"]
        _require(isinstance(surface_refs, Mapping), "S11", "SURFACE_REFS_INVALID", memory_id)

        if memory["memory_type"] == "CHAPTER":
            _require(not narrative.get("moment_line"), "S11", "CHAPTER_HAS_AHA_SURFACE", memory_id)
            story = str(narrative.get("story", "")).strip()
            _require(_sentence_count(story) in (1, 2), "S11", "CHAPTER_STORY_SENTENCE_COUNT", memory_id)
            title_outcome = narrative.get("title_outcome", "PRESENT")
            if title_outcome == "PRESENT":
                title = str(narrative.get("title", "")).strip()
                visible = _visible_length(title)
                _require(2 <= visible <= 12, "S11", "CHAPTER_TITLE_LENGTH", memory_id)
                if visible > 10:
                    _require(
                        narrative.get("title_length_class") == "SOFT_EXTENSION_11_12"
                        and bool(narrative.get("title_soft_extension_reason")),
                        "S11",
                        "TITLE_SOFT_EXTENSION_UNJUSTIFIED",
                        memory_id,
                    )
            else:
                _require(
                    title_outcome == "OMITTED_POLICY_DEFERRED_D2E" and not narrative.get("title"),
                    "S11",
                    "TITLE_OUTCOME_INVALID",
                    memory_id,
                )
            required_surfaces = ("STORY",)
            if title_outcome == "PRESENT":
                required_surfaces = ("TITLE", "STORY")
        else:
            _require(not narrative.get("title") and not narrative.get("story"), "S11", "AHA_HAS_CHAPTER_SURFACE", memory_id)
            line = str(narrative.get("moment_line", "")).strip()
            _require(1 <= _visible_length(line) <= 20, "S11", "AHA_MOMENT_LINE_LENGTH", memory_id)
            required_surfaces = ("AHA_MOMENT_LINE",)
            for token in UNSUPPORTED_AFFECT_TOKENS:
                _require(token not in line, "S11", "UNSUPPORTED_AFFECTIVE_ASSERTION", f"{memory_id}:{token}")
            used_light_affect = [
                policy_id
                for policy_id, (token, _concept_id) in LIGHT_AFFECT_POLICIES.items()
                if token in line
            ]
            if used_light_affect:
                _require(len(used_light_affect) == 1, "S11", "MULTIPLE_LIGHT_AFFECT_POLICIES", memory_id)
                policy_id = used_light_affect[0]
                _require(narrative.get("light_affect_permission_ref") == policy_id, "S11", "LIGHT_AFFECT_PERMISSION_MISSING", memory_id)
                target_ref = str(narrative.get("light_affect_target_claim_ref", ""))
                _require(target_ref in surface_refs.get("AHA_MOMENT_LINE", []), "S11", "LIGHT_AFFECT_TARGET_INVALID", memory_id)
                required_concept = LIGHT_AFFECT_POLICIES[policy_id][1]
                assigned_concepts = {
                    str(item.get("concept_id"))
                    for item in memory.get("canonical_assignments", [])
                    if isinstance(item, Mapping)
                }
                _require(required_concept in assigned_concepts, "S11", "LIGHT_AFFECT_SUBJECT_MISMATCH", memory_id)

        _require(
            set(map(str, surface_refs.keys())) == set(required_surfaces),
            "S11",
            "SURFACE_REFS_SCOPE_INVALID",
            memory_id,
        )

        for surface in required_surfaces:
            refs = surface_refs.get(surface, [])
            _require(isinstance(refs, list) and refs, "S11", "SURFACE_WITHOUT_CLAIMS", f"{memory_id}:{surface}")
            for claim_ref in refs:
                claim_ref = str(claim_ref)
                _require(claim_ref in claim_map, "S11", "SURFACE_CLAIM_MISSING", claim_ref)
                claim = claim_map[claim_ref]
                _require(surface in claim["allowed_surfaces"], "S11", "SURFACE_NOT_ALLOWED", f"{claim_ref}:{surface}")
                required_media = set(map(str, claim.get("required_media_ids", [])))
                _require(not (required_media & removed_media_ids), "S11", "ACTIVATION_INVALIDATES_CLAIM", claim_ref)
        surface_texts = {
            "TITLE": str(narrative.get("title", "") or ""),
            "STORY": str(narrative.get("story", "") or ""),
            "AHA_MOMENT_LINE": str(narrative.get("moment_line", "") or ""),
        }
        self._validate_span_bindings(
            memory_id,
            narrative,
            required_surfaces,
            surface_texts,
            surface_refs,
            claim_map,
        )

    def _validate_span_bindings(
        self,
        memory_id: str,
        narrative: Mapping[str, object],
        required_surfaces: Sequence[str],
        surface_texts: Mapping[str, str],
        surface_refs: Mapping[str, object],
        claim_map: Mapping[str, Mapping[str, object]],
    ) -> None:
        bindings = narrative.get("span_bindings")
        _require(
            isinstance(bindings, list),
            "S11",
            "SPAN_BINDINGS_MISSING",
            memory_id,
        )
        for binding in bindings:
            _require(
                isinstance(binding, Mapping),
                "S11",
                "SPAN_BINDING_INVALID",
                memory_id,
            )
            _require(
                str(binding.get("surface")) in set(required_surfaces),
                "S11",
                "SPAN_SURFACE_SCOPE_INVALID",
                str(binding.get("surface")),
            )
        punctuation = set("，。！？、；：,.!?;:–—-（）()[]【】《》\"'“”‘’")
        for surface in required_surfaces:
            text = surface_texts[surface]
            surface_bindings = [
                binding
                for binding in bindings
                if isinstance(binding, Mapping)
                and str(binding.get("surface")) == surface
            ]
            _require(
                bool(surface_bindings),
                "S11",
                "SURFACE_SPAN_BINDINGS_EMPTY",
                f"{memory_id}:{surface}",
            )
            covered: Set[int] = set()
            bound_claims: Set[str] = set()
            same_kind_ranges: Dict[str, List[Tuple[int, int]]] = {}
            for binding in surface_bindings:
                _require_keys(
                    binding,
                    ("kind", "start", "end", "text"),
                    "S11",
                    "SPAN_BINDING_INVALID",
                )
                kind = str(binding["kind"])
                _require(
                    kind in ("CLAIM", "TONE_PERMISSION"),
                    "S11",
                    "SPAN_BINDING_KIND_INVALID",
                    kind,
                )
                start = int(binding["start"])
                end = int(binding["end"])
                _require(
                    0 <= start < end <= len(text),
                    "S11",
                    "SPAN_RANGE_INVALID",
                    f"{surface}:{start}:{end}",
                )
                _require(
                    text[start:end] == str(binding["text"]),
                    "S11",
                    "SPAN_TEXT_MISMATCH",
                    f"{surface}:{start}:{end}",
                )
                for prior_start, prior_end in same_kind_ranges.setdefault(kind, []):
                    _require(
                        end <= prior_start or start >= prior_end,
                        "S11",
                        "OVERLAPPING_SAME_KIND_SPANS",
                        f"{surface}:{kind}",
                    )
                same_kind_ranges[kind].append((start, end))
                covered.update(range(start, end))
                if kind == "CLAIM":
                    claim_refs = list(map(str, binding.get("claim_refs", [])))
                    _require(
                        bool(claim_refs),
                        "S11",
                        "CLAIM_SPAN_WITHOUT_CLAIM",
                        f"{memory_id}:{surface}",
                    )
                    allowed_surface_refs = set(
                        map(str, surface_refs.get(surface, []))
                    )
                    for claim_ref in claim_refs:
                        _require(
                            claim_ref in claim_map
                            and claim_ref in allowed_surface_refs,
                            "S11",
                            "UNPLANNED_SPAN_CLAIM",
                            claim_ref,
                        )
                        bound_claims.add(claim_ref)
                else:
                    permission_ref = str(binding.get("permission_ref", ""))
                    _require(
                        permission_ref
                        and permission_ref
                        == str(narrative.get("light_affect_permission_ref", "")),
                        "S11",
                        "TONE_SPAN_PERMISSION_INVALID",
                        permission_ref,
                    )
                    permitted_token = LIGHT_AFFECT_POLICIES.get(
                        permission_ref, ("", "")
                    )[0]
                    _require(
                        str(binding["text"]) in (
                            permitted_token,
                            f"{permitted_token}地",
                        ),
                        "S11",
                        "TONE_SPAN_TEXT_NOT_PERMITTED",
                        str(binding["text"]),
                    )
            required_positions = {
                index
                for index, char in enumerate(text)
                if not char.isspace() and char not in punctuation
            }
            _require(
                required_positions.issubset(covered),
                "S11",
                "UNBOUND_SURFACE_TEXT",
                f"{memory_id}:{surface}",
            )
            _require(
                bound_claims == set(map(str, surface_refs.get(surface, []))),
                "S11",
                "SURFACE_CLAIM_SPAN_COVERAGE_INVALID",
                f"{memory_id}:{surface}",
            )

    def _validate_assignments(
        self,
        memory: Mapping[str, object],
        claim_map: Mapping[str, Mapping[str, object]],
        locale: str,
    ) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
        raw_assignments = memory["canonical_assignments"]
        _require(isinstance(raw_assignments, list), "S11", "TAG_ASSIGNMENTS_INVALID", str(memory["memory_id"]))
        _require(len(raw_assignments) <= len(FACETS), "S11", "TAG_ASSIGNMENT_LIMIT", str(memory["memory_id"]))
        facets_seen: Set[str] = set()
        concepts_seen: Set[str] = set()
        primary_count = 0
        assignments: List[Dict[str, object]] = []
        for raw in raw_assignments:
            _require(isinstance(raw, Mapping), "S11", "TAG_ASSIGNMENT_INVALID", str(memory["memory_id"]))
            _require_keys(raw, ("concept_id", "role", "rank", "claim_refs", "evidence_refs"), "S11", "TAG_ASSIGNMENT_INVALID")
            concept_id = str(raw["concept_id"])
            concept = self.registry.require_active(concept_id)
            _require(concept_id not in concepts_seen, "S11", "DUPLICATE_TAG_ASSIGNMENT", concept_id)
            _require(concept.facet not in facets_seen, "S11", "MULTIPLE_ASSIGNMENTS_PER_FACET", concept.facet)
            concepts_seen.add(concept_id)
            facets_seen.add(concept.facet)
            role = str(raw["role"])
            _require(role in ("PRIMARY", "SECONDARY"), "S11", "TAG_ROLE_INVALID", concept_id)
            primary_count += int(role == "PRIMARY")
            _require(bool(raw["evidence_refs"]), "S11", "TAG_EVIDENCE_EMPTY", concept_id)
            claim_refs = list(map(str, raw["claim_refs"]))
            _require(bool(claim_refs), "S11", "TAG_CLAIM_EMPTY", concept_id)
            claim_evidence: Set[str] = set()
            for claim_ref in claim_refs:
                claim_ref = str(claim_ref)
                _require(claim_ref in claim_map, "S11", "TAG_CLAIM_MISSING", claim_ref)
                _require("CANONICAL_TAG" in claim_map[claim_ref]["allowed_surfaces"], "S11", "TAG_CLAIM_NOT_ALLOWED", claim_ref)
                claim_evidence.update(map(str, claim_map[claim_ref]["evidence_refs"]))
            _require(
                set(map(str, raw["evidence_refs"])).issubset(claim_evidence),
                "S11",
                "TAG_EVIDENCE_NOT_IN_CLAIMS",
                concept_id,
            )
            assignments.append(
                {
                    "concept_id": concept_id,
                    "facet": concept.facet,
                    "role": role,
                    "rank": int(raw["rank"]),
                    "claim_refs": list(map(str, raw["claim_refs"])),
                    "evidence_refs": list(map(str, raw["evidence_refs"])),
                    "decision": "ASSIGNED_MOST_SPECIFIC_SUPPORTED",
                }
            )
        _require(primary_count <= 1, "S11", "MULTIPLE_PRIMARY_TAGS", str(memory["memory_id"]))
        if assignments:
            _require(primary_count == 1, "S11", "PRIMARY_TAG_MISSING", str(memory["memory_id"]))
        assignments.sort(key=lambda item: (0 if item["role"] == "PRIMARY" else 1, item["rank"], item["concept_id"]))
        labels: List[Dict[str, object]] = []
        for assignment in assignments:
            label = self.registry.label(str(assignment["concept_id"]), locale)
            if label and len(labels) < 2:
                labels.append(
                    {
                        "concept_id": assignment["concept_id"],
                        "locale": locale,
                        "label": label,
                        "status": "DISPLAY_CANDIDATE_ONLY",
                    }
                )
        return assignments, labels

    def _validate_entity_links(
        self,
        memory: Mapping[str, object],
        claim_map: Mapping[str, Mapping[str, object]],
    ) -> List[Dict[str, object]]:
        raw_links = memory["entity_links"]
        _require(isinstance(raw_links, list), "S11", "ENTITY_LINKS_INVALID", str(memory["memory_id"]))
        seen: Set[Tuple[str, str]] = set()
        links: List[Dict[str, object]] = []
        for raw in raw_links:
            _require(isinstance(raw, Mapping), "S11", "ENTITY_LINK_INVALID", str(memory["memory_id"]))
            _require_keys(raw, ("entity_id", "entity_type", "display_name", "claim_refs", "evidence_refs"), "S11", "ENTITY_LINK_INVALID")
            entity_type = str(raw["entity_type"])
            entity_id = str(raw["entity_id"])
            _require(entity_type in ENTITY_TYPES, "S11", "ENTITY_TYPE_INVALID", entity_type)
            _require((entity_type, entity_id) not in seen, "S11", "DUPLICATE_ENTITY_LINK", entity_id)
            seen.add((entity_type, entity_id))
            _require(bool(raw["evidence_refs"]), "S11", "ENTITY_EVIDENCE_EMPTY", entity_id)
            claim_refs = list(map(str, raw["claim_refs"]))
            _require(bool(claim_refs), "S11", "ENTITY_CLAIM_EMPTY", entity_id)
            claim_evidence: Set[str] = set()
            for claim_ref in claim_refs:
                _require(claim_ref in claim_map, "S11", "ENTITY_CLAIM_MISSING", claim_ref)
                claim_evidence.update(map(str, claim_map[claim_ref]["evidence_refs"]))
            _require(
                set(map(str, raw["evidence_refs"])).issubset(claim_evidence),
                "S11",
                "ENTITY_EVIDENCE_NOT_IN_CLAIMS",
                entity_id,
            )
            links.append(
                {
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "display_name": str(raw["display_name"]),
                    "claim_refs": list(map(str, raw["claim_refs"])),
                    "evidence_refs": list(map(str, raw["evidence_refs"])),
                    "decision": "VERIFIED_ENTITY_INDEX_LINK",
                }
            )
        links.sort(key=lambda item: (item["entity_type"], item["entity_id"]))
        return links

    def _execute_s12_pre(
        self,
        payload: Mapping[str, object],
        s11: Mapping[str, object],
        run: Mapping[str, object],
    ) -> Dict[str, object]:
        s09 = payload["s09"]
        _require(isinstance(s09, Mapping), "S12", "S09_HANDOFF_INVALID", "must be an object")
        _require_keys(s09, ("day_state", "selected_chapter_ids", "selected_aha_ids", "chapter_aha_pair_decisions"), "S12", "S09_HANDOFF_INVALID")
        day_state = str(s09["day_state"])
        _require(day_state in DAY_STATES, "S12", "DAY_STATE_INVALID", day_state)
        chapters = list(map(str, s09["selected_chapter_ids"]))
        ahas = list(map(str, s09["selected_aha_ids"]))
        _require(len(chapters) == len(set(chapters)), "S12", "DUPLICATE_SELECTED_CHAPTER", str(chapters))
        _require(len(ahas) == len(set(ahas)), "S12", "DUPLICATE_SELECTED_AHA", str(ahas))
        if day_state == "CHAPTER_DAY":
            _require(1 <= len(chapters) <= 5 and len(ahas) <= 3, "S12", "CHAPTER_DAY_CAPACITY_INVALID", f"{len(chapters)}/{len(ahas)}")
        elif day_state == "HIGHLIGHT_DAY":
            _require(not chapters and len(ahas) == 1, "S12", "HIGHLIGHT_DAY_CAPACITY_INVALID", f"{len(chapters)}/{len(ahas)}")
        else:
            _require(not chapters and not ahas, "S12", "EMPTY_DAY_CAPACITY_INVALID", f"{len(chapters)}/{len(ahas)}")
        if run["revision_kind"] == "PREVIEW":
            _require(
                len(chapters) <= 4 and len(ahas) <= 2,
                "S12",
                "PREVIEW_CAPACITY_INVALID",
                f"{len(chapters)}/{len(ahas)}",
            )
        if len(chapters) == 5:
            _require(
                run["revision_kind"] == "FINAL"
                and s09.get("fifth_chapter_gate") == "PASS",
                "S12",
                "FIFTH_CHAPTER_GATE_REQUIRED",
                str(run["revision_kind"]),
            )

        memory_by_id = {str(memory["memory_id"]): memory for memory in payload["memories"]}
        _require(set(memory_by_id) == set(chapters + ahas), "S12", "S09_S11_MEMBERSHIP_MISMATCH", str(sorted(memory_by_id)))
        for selected_ids, label in ((chapters, "CHAPTER"), (ahas, "AHA")):
            expected_order = sorted(
                selected_ids,
                key=lambda memory_id: (
                    int(memory_by_id[memory_id]["capture_start_ms"]),
                    memory_id,
                ),
            )
            _require(
                selected_ids == expected_order,
                "S12",
                "CANONICAL_MEMORY_ORDER_INVALID",
                f"{label}:{selected_ids}",
            )
        for memory_id in chapters:
            _require(memory_by_id[memory_id]["memory_type"] == "CHAPTER", "S12", "CHAPTER_TYPE_MISMATCH", memory_id)
            self._validate_media_capacity(memory_by_id[memory_id])
        for memory_id in ahas:
            _require(memory_by_id[memory_id]["memory_type"] == "AHA", "S12", "AHA_TYPE_MISMATCH", memory_id)
            self._validate_media_capacity(memory_by_id[memory_id])
        self._validate_pair_decisions(chapters, ahas, s09["chapter_aha_pair_decisions"])
        self._validate_requests(payload)
        self._validate_cross_memory_reuse(payload)

        output = {
            "contract_version": S12_CONTRACT_VERSION,
            "phase": "PRE_MATERIALIZATION",
            "revision_id": run["revision_id"],
            "snapshot_id": run["snapshot_id"],
            "day_state": day_state,
            "chapter_count": len(chapters),
            "aha_count": len(ahas),
            "s11_fingerprint": s11["fingerprint"],
            "decision": (
                "NO_MATERIALIZATION_EMPTY_EXPORT_ALLOWED"
                if day_state == "EMPTY_DAY"
                else "MATERIALIZATION_ALLOWED"
            ),
            "repair_permission": "NONE",
            "status": "PASS",
        }
        output["fingerprint"] = _fingerprint(output)
        return output

    def _validate_media_capacity(self, memory: Mapping[str, object]) -> None:
        media = memory["active_media"]
        _require(isinstance(media, list), "S12", "ACTIVE_MEDIA_INVALID", str(memory["memory_id"]))
        if memory["memory_type"] == "CHAPTER":
            if len(media) == 2:
                _require(memory.get("compact_pair_gate") == "PASS", "S12", "COMPACT_PAIR_GATE_REQUIRED", str(memory["memory_id"]))
            else:
                _require(3 <= len(media) <= 5, "S12", "CHAPTER_MEDIA_CAPACITY_INVALID", str(memory["memory_id"]))
        else:
            _require(len(media) == 1, "S12", "AHA_SINGLE_MEDIA_REQUIRED", str(memory["memory_id"]))
        seen: Set[str] = set()
        hero_count = 0
        for item in media:
            _require(isinstance(item, Mapping), "S12", "MEDIA_ITEM_INVALID", str(memory["memory_id"]))
            _require_keys(item, ("media_id", "media_plan_ref", "evidence_anchor_ref", "raw_asset_id", "format", "hq_request_id", "semantic_scope_id", "source_family_id", "is_hero"), "S12", "MEDIA_ITEM_INVALID")
            media_id = str(item["media_id"])
            _require(media_id not in seen, "S12", "DUPLICATE_MEDIA_ID", media_id)
            seen.add(media_id)
            _require(item["format"] in MEDIA_FORMATS, "S12", "MEDIA_FORMAT_INVALID", media_id)
            if memory["memory_type"] == "AHA":
                _require(
                    item["format"] in ("PHOTO", "LIVE_2S"),
                    "S12",
                    "AHA_MEDIA_FORMAT_INVALID",
                    media_id,
                )
            hero_count += int(bool(item["is_hero"]))
        if memory["memory_type"] == "CHAPTER":
            _require(hero_count == 1, "S12", "CHAPTER_HERO_COUNT_INVALID", str(memory["memory_id"]))
            plans = memory.get("d1_survivor_plans", [])
            _require(
                isinstance(plans, list),
                "S12",
                "D1_PLANS_INVALID",
                str(memory["memory_id"]),
            )
            failed_ids = [
                str(plan.get("failed_media_id"))
                for plan in plans
                if isinstance(plan, Mapping)
            ]
            _require(
                len(failed_ids) == len(plans)
                and len(failed_ids) == len(set(failed_ids)),
                "S12",
                "D1_PLAN_COVERAGE_INVALID",
                str(memory["memory_id"]),
            )
            for failed_media_id in failed_ids:
                _require(
                    failed_media_id in seen,
                    "S12",
                    "D1_FAILED_MEDIA_MISSING",
                    failed_media_id,
                )
                self._validated_d1_plan(
                    memory,
                    failed_media_id,
                    d1_already_used=False,
                )
        else:
            _require(hero_count == 0, "S12", "AHA_MUST_NOT_HAVE_HERO", str(memory["memory_id"]))

    def _validate_pair_decisions(
        self,
        chapters: Sequence[str],
        ahas: Sequence[str],
        raw_decisions: object,
    ) -> None:
        _require(isinstance(raw_decisions, list), "S12", "PAIR_DECISIONS_INVALID", "must be an array")
        decisions: Dict[Tuple[str, str], str] = {}
        for raw in raw_decisions:
            _require(isinstance(raw, Mapping), "S12", "PAIR_DECISION_INVALID", "must be an object")
            _require_keys(raw, ("chapter_id", "aha_id", "decision"), "S12", "PAIR_DECISION_INVALID")
            key = (str(raw["chapter_id"]), str(raw["aha_id"]))
            _require(key not in decisions, "S12", "DUPLICATE_PAIR_DECISION", str(key))
            decision = str(raw["decision"])
            _require(decision in ("DISJOINT_PASS", "NARRATIVELY_DISTINCT_PASS"), "S12", "PAIR_NOT_INDEPENDENT", str(key))
            decisions[key] = decision
        expected = {(chapter, aha) for chapter in chapters for aha in ahas}
        _require(set(decisions) == expected, "S12", "PAIR_DECISION_COVERAGE_INVALID", f"expected {len(expected)}, got {len(decisions)}")

    def _validate_requests(self, payload: Mapping[str, object]) -> None:
        raw_requests = payload["hq_requests"]
        _require(isinstance(raw_requests, list), "S13", "HQ_REQUESTS_INVALID", "must be an array")
        requests: Dict[str, Mapping[str, object]] = {}
        for request in raw_requests:
            _require(isinstance(request, Mapping), "S13", "HQ_REQUEST_INVALID", "must be an object")
            _require_keys(request, ("request_id", "raw_asset_id", "source_start_ms", "source_end_ms", "routes"), "S13", "HQ_REQUEST_INVALID")
            request_id = str(request["request_id"])
            _require(request_id not in requests, "S13", "DUPLICATE_HQ_REQUEST", request_id)
            _require(int(request["source_end_ms"]) >= int(request["source_start_ms"]), "S13", "HQ_INTERVAL_INVALID", request_id)
            routes = request["routes"]
            _require(isinstance(routes, list) and 1 <= len(routes) <= 3, "S13", "ROUTE_COUNT_INVALID", request_id)
            priorities: Set[int] = set()
            route_ids: Set[str] = set()
            for route in routes:
                _require(isinstance(route, Mapping), "S13", "ROUTE_INVALID", request_id)
                _require_keys(route, ("route_id", "priority", "format", "source_ref", "evidence_anchor_ref", "semantic_scope_id", "reference_outcome"), "S13", "ROUTE_INVALID")
                route_id = str(route["route_id"])
                priority = int(route["priority"])
                _require(route_id not in route_ids and priority not in priorities, "S13", "DUPLICATE_ROUTE", request_id)
                route_ids.add(route_id)
                priorities.add(priority)
                _require(route["format"] in MEDIA_FORMATS, "S13", "ROUTE_FORMAT_INVALID", route_id)
                _require(route["reference_outcome"] in ROUTE_OUTCOMES, "S13", "REFERENCE_OUTCOME_INVALID", route_id)
            _require(priorities == set(range(len(routes))), "S13", "ROUTE_PRIORITY_INVALID", request_id)
            requests[request_id] = request

        used_requests: Set[str] = set()
        for memory in payload["memories"]:
            for media in memory["active_media"]:
                request_id = str(media["hq_request_id"])
                _require(request_id in requests, "S13", "MEDIA_REQUEST_MISSING", request_id)
                request = requests[request_id]
                _require(request["raw_asset_id"] == media["raw_asset_id"], "S13", "MEDIA_REQUEST_ASSET_MISMATCH", request_id)
                primary = min(request["routes"], key=lambda route: int(route["priority"]))
                _require(primary["format"] == media["format"], "S13", "PRIMARY_ROUTE_FORMAT_MISMATCH", request_id)
                _require(primary["evidence_anchor_ref"] == media["evidence_anchor_ref"], "S13", "PRIMARY_ROUTE_ANCHOR_MISMATCH", request_id)
                _require(primary["semantic_scope_id"] == media["semantic_scope_id"], "S13", "PRIMARY_ROUTE_SCOPE_MISMATCH", request_id)
                _require(
                    str(primary.get("source_family_id", media["source_family_id"]))
                    == str(media["source_family_id"]),
                    "S13",
                    "PRIMARY_ROUTE_SOURCE_FAMILY_MISMATCH",
                    request_id,
                )
                if memory["memory_type"] == "AHA":
                    _require(
                        all(
                            route["format"] in ("PHOTO", "LIVE_2S")
                            for route in request["routes"]
                        ),
                        "S13",
                        "AHA_ROUTE_FORMAT_INVALID",
                        request_id,
                    )
                used_requests.add(request_id)
        _require(used_requests == set(requests), "S13", "UNUSED_OR_MISSING_HQ_REQUEST", str(sorted(set(requests) ^ used_requests)))

    def _validate_cross_memory_reuse(self, payload: Mapping[str, object]) -> None:
        owners: Dict[str, List[str]] = {}
        possible_owners: Dict[str, Set[str]] = {}
        primary_signatures: Dict[str, Set[Tuple[object, ...]]] = {}
        request_by_id = {
            str(request["request_id"]): request
            for request in payload["hq_requests"]
        }
        for memory in payload["memories"]:
            for media in memory["active_media"]:
                memory_id = str(memory["memory_id"])
                source_family = str(media["source_family_id"])
                owners.setdefault(source_family, []).append(memory_id)
                request = request_by_id[str(media["hq_request_id"])]
                primary = min(
                    request["routes"], key=lambda route: int(route["priority"])
                )
                primary_signatures.setdefault(source_family, set()).add(
                    (
                        request["raw_asset_id"],
                        request["source_start_ms"],
                        request["source_end_ms"],
                        primary["source_ref"],
                        primary["format"],
                    )
                )
                for route in request["routes"]:
                    possible_source = str(
                        route.get("source_family_id", source_family)
                    )
                    possible_owners.setdefault(possible_source, set()).add(
                        memory_id
                    )
        required = {
            source: set(memory_ids)
            for source, memory_ids in owners.items()
            if len(set(memory_ids)) > 1
        }
        raw = payload.get("cross_memory_reuse_decisions", [])
        _require(isinstance(raw, list), "S12", "REUSE_DECISIONS_INVALID", "must be an array")
        supplied: Dict[str, Set[str]] = {}
        for decision in raw:
            _require(isinstance(decision, Mapping), "S12", "REUSE_DECISION_INVALID", "must be an object")
            _require(decision.get("decision") == "NECESSARY_EXACT_REUSE", "S12", "UNAPPROVED_CROSS_MEMORY_REUSE", str(decision))
            source = str(decision.get("source_family_id"))
            memory_ids = set(map(str, decision.get("memory_ids", [])))
            _require(
                source not in supplied
                and len(memory_ids) >= 2
                and memory_ids.issubset(possible_owners.get(source, set())),
                "S12",
                "REUSE_DECISION_SCOPE_INVALID",
                str(decision),
            )
            supplied[source] = memory_ids
        for source, required_owners in required.items():
            _require(
                source in supplied
                and required_owners.issubset(supplied[source]),
                "S12",
                "REUSE_DECISION_COVERAGE_INVALID",
                f"{source}:{sorted(required_owners)}",
            )
            _require(
                len(primary_signatures[source]) == 1,
                "S12",
                "PLANNED_REUSE_NOT_EXACT",
                source,
            )

    def _execute_s13_materialization(
        self,
        payload: Mapping[str, object],
        s11: Mapping[str, object],
        run: Mapping[str, object],
    ) -> Dict[str, object]:
        requests = {str(request["request_id"]): request for request in payload["hq_requests"]}
        receipts: List[Dict[str, object]] = []
        activation_deltas: List[Dict[str, object]] = []
        failures: List[Dict[str, object]] = []
        resolved_failures: List[Dict[str, object]] = []
        omitted_media_ids: Set[str] = set()
        d1_used_memory_ids: Set[str] = set()
        active_source_families: Dict[str, Set[str]] = {}

        for memory in payload["memories"]:
            memory_id = str(memory["memory_id"])
            active_source_families.setdefault(memory_id, set())
            for media in memory["active_media"]:
                request = requests[str(media["hq_request_id"])]
                selected_route: Optional[Mapping[str, object]] = None
                terminal_route_ids: List[str] = []
                for route in sorted(request["routes"], key=lambda item: int(item["priority"])):
                    outcome = str(route["reference_outcome"])
                    if outcome == "CONTRACT_INVALID":
                        raise PipelineContractError("S13", "MATERIALIZATION_CONTRACT_INVALID", str(route["route_id"]))
                    if outcome == "TRANSIENT_FAILURE":
                        failures.append(
                            {
                                "memory_id": memory_id,
                                "media_id": media["media_id"],
                                "request_id": request["request_id"],
                                "route_id": route["route_id"],
                                "failure_class": outcome,
                            }
                        )
                        return self._materialization_hold(
                            run,
                            len(requests),
                            receipts,
                            activation_deltas,
                            failures,
                            omitted_media_ids,
                            resolved_failures,
                        )
                    if outcome == "TERMINAL_FAILURE":
                        terminal_route_ids.append(str(route["route_id"]))
                        continue
                    _require(route["evidence_anchor_ref"] == media["evidence_anchor_ref"], "S13", "FALLBACK_ANCHOR_CHANGED", str(route["route_id"]))
                    _require(route["semantic_scope_id"] == media["semantic_scope_id"], "S13", "FALLBACK_SCOPE_CHANGED", str(route["route_id"]))
                    source_family = str(route.get("source_family_id", media["source_family_id"]))
                    if source_family in active_source_families[memory_id]:
                        terminal_route_ids.append(str(route["route_id"]))
                        continue
                    selected_route = route
                    active_source_families[memory_id].add(source_family)
                    break
                if selected_route is None:
                    d1_plan = self._validated_d1_plan(
                        memory,
                        str(media["media_id"]),
                        d1_already_used=memory_id in d1_used_memory_ids,
                    )
                    if d1_plan is None:
                        failures.append(
                            {
                                "memory_id": memory_id,
                                "media_id": media["media_id"],
                                "request_id": request["request_id"],
                                "route_ids_exhausted": terminal_route_ids,
                                "failure_class": "ALL_PREDECLARED_ROUTES_EXHAUSTED",
                            }
                        )
                        return self._materialization_hold(
                            run,
                            len(requests),
                            receipts,
                            activation_deltas,
                            failures,
                            omitted_media_ids,
                            resolved_failures,
                        )
                    d1_used_memory_ids.add(memory_id)
                    omitted_media_ids.add(str(media["media_id"]))
                    resolved_failures.append(
                        {
                            "memory_id": memory_id,
                            "media_id": media["media_id"],
                            "request_id": request["request_id"],
                            "route_ids_exhausted": terminal_route_ids,
                            "resolution": "D1_SURVIVOR_ACTIVATED",
                        }
                    )
                    activation_deltas.append(
                        {
                            "delta_type": "D1_SURVIVOR_ACTIVATED",
                            "memory_id": memory_id,
                            "media_id": media["media_id"],
                            "removed_media_ids": [media["media_id"]],
                            "survivor_media_ids": d1_plan["survivor_media_ids"],
                            "alternate_hero_media_id": d1_plan.get(
                                "alternate_hero_media_id"
                            ),
                            "affected_artifacts": ["S10", "S11", "S12"],
                        }
                    )
                    continue
                route_id = str(selected_route["route_id"])
                if int(selected_route["priority"]) > 0:
                    activation_deltas.append(
                        {
                            "delta_type": "FALLBACK_ROUTE_ACTIVATED",
                            "memory_id": memory_id,
                            "media_id": media["media_id"],
                            "from_route_id": min(request["routes"], key=lambda item: int(item["priority"]))["route_id"],
                            "to_route_id": route_id,
                            "affected_artifacts": ["S11", "S12"],
                        }
                    )
                receipt_payload = {
                    "request_id": request["request_id"],
                    "route_id": route_id,
                    "memory_id": memory_id,
                    "media_id": media["media_id"],
                    "format": selected_route["format"],
                    "source_ref": selected_route["source_ref"],
                    "source_interval_ms": [request["source_start_ms"], request["source_end_ms"]],
                    "evidence_anchor_ref": selected_route["evidence_anchor_ref"],
                    "semantic_scope_id": selected_route["semantic_scope_id"],
                    "source_family_id": str(
                        selected_route.get(
                            "source_family_id", media["source_family_id"]
                        )
                    ),
                }
                receipts.append(
                    {
                        **receipt_payload,
                        "receipt_checksum": _fingerprint(receipt_payload),
                        "materialization_status": "REFERENCE_RECEIPT_SUCCESS",
                        "media_bytes_materialized": False,
                    }
                )

        output = {
            "contract_version": S13_CONTRACT_VERSION,
            "phase": "REFERENCE_MATERIALIZATION",
            "revision_id": run["revision_id"],
            "snapshot_id": run["snapshot_id"],
            "reference_only": True,
            "active_request_count": len(requests),
            "successful_reference_receipt_count": len(receipts),
            "receipts": receipts,
            "activation_deltas": activation_deltas,
            "omitted_media_ids": sorted(omitted_media_ids),
            "resolved_failures": resolved_failures,
            "failures": failures,
            "status": "REFERENCE_MATERIALIZATION_COMPLETE",
        }
        output["fingerprint"] = _fingerprint(output)
        return output

    def _materialization_hold(
        self,
        run: Mapping[str, object],
        active_request_count: int,
        receipts: Sequence[Mapping[str, object]],
        activation_deltas: Sequence[Mapping[str, object]],
        failures: Sequence[Mapping[str, object]],
        omitted_media_ids: Sequence[str] = (),
        resolved_failures: Sequence[Mapping[str, object]] = (),
    ) -> Dict[str, object]:
        output = {
            "contract_version": S13_CONTRACT_VERSION,
            "phase": "REFERENCE_MATERIALIZATION",
            "revision_id": run["revision_id"],
            "snapshot_id": run["snapshot_id"],
            "reference_only": True,
            "active_request_count": active_request_count,
            "successful_reference_receipt_count": len(receipts),
            "receipts": list(receipts),
            "activation_deltas": list(activation_deltas),
            "omitted_media_ids": sorted(map(str, omitted_media_ids)),
            "resolved_failures": list(resolved_failures),
            "failures": list(failures),
            "status": "HOLD",
        }
        output["fingerprint"] = _fingerprint(output)
        return output

    def _validated_d1_plan(
        self,
        memory: Mapping[str, object],
        failed_media_id: str,
        d1_already_used: bool,
    ) -> Optional[Mapping[str, object]]:
        if memory["memory_type"] != "CHAPTER" or d1_already_used:
            return None
        plans = memory.get("d1_survivor_plans", [])
        _require(isinstance(plans, list), "S13", "D1_PLANS_INVALID", str(memory["memory_id"]))
        matches = [
            plan
            for plan in plans
            if isinstance(plan, Mapping)
            and str(plan.get("failed_media_id")) == failed_media_id
        ]
        if not matches:
            return None
        _require(len(matches) == 1, "S13", "D1_PLAN_AMBIGUOUS", failed_media_id)
        plan = matches[0]
        _require(plan.get("decision") == "PASS", "S13", "D1_PLAN_NOT_PREVALIDATED", failed_media_id)
        current_ids = {str(item["media_id"]) for item in memory["active_media"]}
        survivor_ids = list(map(str, plan.get("survivor_media_ids", [])))
        _require(
            set(survivor_ids) == current_ids - {failed_media_id}
            and len(survivor_ids) == len(set(survivor_ids)),
            "S13",
            "D1_SURVIVOR_SET_INVALID",
            failed_media_id,
        )
        if len(survivor_ids) == 2:
            _require(
                plan.get("resulting_compact_pair_gate") == "PASS",
                "S13",
                "D1_COMPACT_PAIR_GATE_REQUIRED",
                failed_media_id,
            )
        else:
            _require(3 <= len(survivor_ids) <= 4, "S13", "D1_SURVIVOR_CAPACITY_INVALID", failed_media_id)
        failed_media = next(
            item
            for item in memory["active_media"]
            if str(item["media_id"]) == failed_media_id
        )
        alternate_hero = plan.get("alternate_hero_media_id")
        if bool(failed_media["is_hero"]):
            _require(
                alternate_hero is not None
                and str(alternate_hero) in set(survivor_ids),
                "S13",
                "D1_ALTERNATE_HERO_REQUIRED",
                failed_media_id,
            )
        else:
            _require(
                alternate_hero in (None, ""),
                "S13",
                "D1_UNNECESSARY_HERO_CHANGE",
                failed_media_id,
            )
        return plan

    def _execute_s12_activation(
        self,
        payload: Mapping[str, object],
        s11: Mapping[str, object],
        s12_pre: Mapping[str, object],
        materialization: Mapping[str, object],
        run: Mapping[str, object],
    ) -> Dict[str, object]:
        _require(materialization["status"] == "REFERENCE_MATERIALIZATION_COMPLETE", "S12", "MATERIALIZATION_NOT_COMPLETE", str(materialization["status"]))
        omitted_media_ids = set(map(str, materialization.get("omitted_media_ids", [])))
        expected_media = (
            sum(len(memory["active_media"]) for memory in payload["memories"])
            - len(omitted_media_ids)
        )
        _require(len(materialization["receipts"]) == expected_media, "S12", "RECEIPT_COVERAGE_INVALID", f"{len(materialization['receipts'])}/{expected_media}")

        try:
            self._validate_receipt_cross_memory_reuse(payload, materialization)
        except PipelineContractError as error:
            return self._activation_hold(
                s11,
                s12_pre,
                materialization,
                run,
                error,
            )

        affected = {str(delta["memory_id"]) for delta in materialization["activation_deltas"]}
        memory_by_id = {str(memory["memory_id"]): memory for memory in payload["memories"]}
        revalidation: List[Dict[str, object]] = []
        for memory_id in sorted(affected):
            memory = memory_by_id[memory_id]
            claim_map = {str(claim["claim_id"]): claim for claim in memory["claims"]}
            removed_for_memory = {
                media_id
                for media_id in omitted_media_ids
                if any(
                    str(item["media_id"]) == media_id
                    for item in memory["active_media"]
                )
            }
            try:
                self._validate_narrative(
                    memory,
                    memory["narrative"],
                    claim_map,
                    removed_media_ids=removed_for_memory,
                )
            except PipelineContractError as error:
                if error.code == "ACTIVATION_INVALIDATES_CLAIM":
                    return self._activation_hold(
                        s11,
                        s12_pre,
                        materialization,
                        run,
                        error,
                    )
                raise
            revalidation.append(
                {
                    "memory_id": memory_id,
                    "scope": ["NARRATIVE", "CLAIMS", "TAGS", "MEDIA_ALIGNMENT"],
                    "decision": "AFFECTED_ARTIFACTS_REVALIDATED",
                }
            )

        output = {
            "contract_version": S12_CONTRACT_VERSION,
            "phase": "ACTIVATION_AND_EXPORT",
            "revision_id": run["revision_id"],
            "snapshot_id": run["snapshot_id"],
            "pre_validation_fingerprint": s12_pre["fingerprint"],
            "s11_fingerprint": s11["fingerprint"],
            "materialization_fingerprint": materialization["fingerprint"],
            "affected_artifact_revalidation": revalidation,
            "expected_published_head": run.get("expected_published_head"),
            "decision": "REFERENCE_EXPORT_ALLOWED",
            "production_cas_executed": False,
            "status": "PASS",
        }
        output["fingerprint"] = _fingerprint(output)
        return output

    def _validate_receipt_cross_memory_reuse(
        self,
        payload: Mapping[str, object],
        materialization: Mapping[str, object],
    ) -> None:
        owners: Dict[str, Set[str]] = {}
        signatures: Dict[str, Set[Tuple[object, ...]]] = {}
        for receipt in materialization["receipts"]:
            source = str(receipt["source_family_id"])
            owners.setdefault(source, set()).add(
                str(receipt["memory_id"])
            )
            signatures.setdefault(source, set()).add(
                (
                    receipt["source_ref"],
                    tuple(receipt["source_interval_ms"]),
                    receipt["format"],
                )
            )
        required = {
            source: memory_ids
            for source, memory_ids in owners.items()
            if len(memory_ids) > 1
        }
        supplied = {
            str(decision.get("source_family_id")): set(
                map(str, decision.get("memory_ids", []))
            )
            for decision in payload.get("cross_memory_reuse_decisions", [])
            if isinstance(decision, Mapping)
            and decision.get("decision") == "NECESSARY_EXACT_REUSE"
        }
        for source, required_owners in required.items():
            _require(
                source in supplied
                and required_owners.issubset(supplied[source]),
                "S12",
                "ACTIVATED_REUSE_DECISION_INVALID",
                f"{source}:{sorted(required_owners)}",
            )
            _require(
                len(signatures[source]) == 1,
                "S12",
                "ACTIVATED_REUSE_NOT_EXACT",
                source,
            )

    def _activation_hold(
        self,
        s11: Mapping[str, object],
        s12_pre: Mapping[str, object],
        materialization: Mapping[str, object],
        run: Mapping[str, object],
        error: PipelineContractError,
    ) -> Dict[str, object]:
        output = {
            "contract_version": S12_CONTRACT_VERSION,
            "phase": "ACTIVATION_AND_EXPORT",
            "revision_id": run["revision_id"],
            "snapshot_id": run["snapshot_id"],
            "pre_validation_fingerprint": s12_pre["fingerprint"],
            "s11_fingerprint": s11["fingerprint"],
            "materialization_fingerprint": materialization["fingerprint"],
            "affected_artifact_revalidation": [],
            "decision": "OWNER_REPLAN_REQUIRED",
            "owner_stage": error.stage,
            "reason_code": error.code,
            "reason_detail": error.detail,
            "production_cas_executed": False,
            "status": "HOLD",
        }
        output["fingerprint"] = _fingerprint(output)
        return output

    def _build_user_export(
        self,
        payload: Mapping[str, object],
        s11: Mapping[str, object],
        materialization: Mapping[str, object],
        activation_validation: Mapping[str, object],
        run: Mapping[str, object],
    ) -> Dict[str, object]:
        receipt_by_media = {str(receipt["media_id"]): receipt for receipt in materialization["receipts"]}
        omitted_media_ids = set(map(str, materialization.get("omitted_media_ids", [])))
        alternate_heroes = {
            str(delta["memory_id"]): str(delta["alternate_hero_media_id"])
            for delta in materialization["activation_deltas"]
            if delta.get("alternate_hero_media_id")
        }
        memories_by_id: Dict[str, Dict[str, object]] = {}
        for memory in s11["memories"]:
            visible_media = []
            for media in memory["active_media"]:
                if str(media["media_id"]) in omitted_media_ids:
                    continue
                receipt = receipt_by_media[str(media["media_id"])]
                is_hero = bool(media["is_hero"])
                if str(memory["memory_id"]) in alternate_heroes:
                    is_hero = (
                        str(media["media_id"])
                        == alternate_heroes[str(memory["memory_id"])]
                    )
                visible_media.append(
                    {
                        "media_id": media["media_id"],
                        "format": receipt["format"],
                        "reference_receipt_id": receipt["receipt_checksum"],
                        "is_hero": is_hero,
                    }
                )
            grounded = memory["grounded_narrative"]
            if memory["memory_type"] == "CHAPTER":
                user_narrative = {
                    "title": grounded.get("title"),
                    "story": grounded.get("story"),
                    "time_label": grounded.get("time_label"),
                }
            else:
                user_narrative = {
                    "moment_line": grounded.get("moment_line"),
                    "time_label": grounded.get("time_label"),
                }
            memories_by_id[str(memory["memory_id"])] = {
                "memory_id": memory["memory_id"],
                "memory_type": memory["memory_type"],
                "narrative": user_narrative,
                "display_labels": memory["display_label_candidates"],
                "visible_media": visible_media,
                "protected_user_text": memory["protected_user_text"],
            }
        s09 = payload["s09"]
        chapters = [
            memories_by_id[str(memory_id)]
            for memory_id in s09["selected_chapter_ids"]
        ]
        ahas = [
            memories_by_id[str(memory_id)]
            for memory_id in s09["selected_aha_ids"]
        ]
        output = {
            "export_contract_version": "DIARY_ONE_USER_DIARY_EXPORT_V1_0",
            "reference_only": True,
            "user_local_day": run["user_local_day"],
            "revision_id": run["revision_id"],
            "day_state": s09["day_state"],
            "chapters": chapters,
            "ahas": ahas,
            "activation_validation_ref": activation_validation["fingerprint"],
        }
        output["fingerprint"] = _fingerprint(output)
        return output

    def _build_audit_run(
        self,
        validated: Mapping[str, object],
        materialization: Mapping[str, object],
        activation_validation: Mapping[str, object],
        diary_export: Mapping[str, object],
    ) -> Dict[str, object]:
        return {
            "audit_contract_version": "DIARY_ONE_INTERNAL_AUDIT_RUN_V1_0",
            "input_fingerprint": validated["input_fingerprint"],
            "upstream_trace": validated["upstream_trace"],
            "s11_fingerprint": validated["s11"]["fingerprint"],
            "s12_pre_fingerprint": validated["s12_pre"]["fingerprint"],
            "s13_fingerprint": materialization["fingerprint"],
            "s12_activation_fingerprint": activation_validation["fingerprint"],
            "export_fingerprint": diary_export["fingerprint"],
            "cost_provenance": {
                "model_calls_executed_by_reference": 0,
                "media_bytes_materialized_by_reference": 0,
                "writer_input_provenance": validated["s11"][
                    "writer_provenance"
                ],
                "hq_request_count": materialization["active_request_count"],
                "successful_reference_receipt_count": materialization[
                    "successful_reference_receipt_count"
                ],
                "fallback_activation_count": sum(
                    1
                    for delta in materialization["activation_deltas"]
                    if delta.get("delta_type") == "FALLBACK_ROUTE_ACTIVATED"
                ),
                "d1_omission_count": len(
                    materialization.get("omitted_media_ids", [])
                ),
            },
            "status": "REFERENCE_AUDIT_COMPLETE",
        }

    def _run_manifest(
        self,
        validated: Mapping[str, object],
        materialization: Mapping[str, object],
        activation_validation: Optional[Mapping[str, object]],
        exported: bool,
    ) -> Dict[str, object]:
        status = (
            "REFERENCE_VALIDATED_NOT_CLOUD_PRODUCTION"
            if exported
            else "HOLD_NO_REFERENCE_EXPORT"
        )
        stages = list(validated["upstream_trace"])
        stages.extend(
            [
                {"stage_id": "S11", "execution_mode": "REFERENCE_EXECUTED", "status": "PASS"},
                {"stage_id": "S12A", "execution_mode": "REFERENCE_EXECUTED", "status": "PASS"},
                {
                    "stage_id": "S13A",
                    "execution_mode": "REFERENCE_EXECUTED",
                    "status": materialization["status"],
                },
            ]
        )
        if activation_validation is not None:
            stages.append(
                {
                    "stage_id": "S12B",
                    "execution_mode": "REFERENCE_EXECUTED",
                    "status": activation_validation["status"],
                }
            )
        if exported:
            stages.append(
                {
                    "stage_id": "S13B",
                    "execution_mode": "REFERENCE_EXECUTED",
                    "status": "REFERENCE_EXPORT_WRITTEN",
                }
            )
        return {
            "contract_version": PIPELINE_CONTRACT_VERSION,
            "input_fingerprint": validated["input_fingerprint"],
            "full_flow_status": status,
            "stages": stages,
            "reference_only": True,
            "explicit_non_claims": [
                "NO_CLOUD_DEPLOYMENT",
                "NO_REAL_MODEL_INFERENCE",
                "NO_HQ_MEDIA_BYTES_RENDERED",
                "NO_APP_OR_FIRMWARE_INTEGRATION",
                "NO_PRODUCTION_CAS_OR_PUBLISHED_HEAD_MUTATION",
            ],
        }


def load_production_manifest(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(payload, Mapping), "PIPELINE", "MANIFEST_NOT_OBJECT", str(path))
    return payload
