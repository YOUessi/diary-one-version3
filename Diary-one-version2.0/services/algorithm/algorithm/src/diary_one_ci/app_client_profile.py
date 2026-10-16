"""App-declared memory preferences → soft editorial signals for X02.

Contract (multipart field ``app_client_profile`` JSON):
  {
    "schema_version": "APP_CLIENT_PROFILE_V01",
    "memory_preferences": ["title: text", ...],   # legacy free-text lines
    "boost_tags": ["Coffee", ...],                 # optional
    "avoid_topics": ["Work stress detail", ...], # optional
    "writing_style": "Empathetic and warm",      # optional
    "preferred_categories": ["Daily life", ...]  # optional
  }

Rules (V1.75 compatible):
  - Never invent facts or memories from preferences.
  - Soft guidance for structure/writer prompts only.
  - Soft reorder of already-selected public chapters (boost earlier, avoid later).
  - Hard drop of grounded chapters is forbidden.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

POLICY_VERSION = "APP_CLIENT_PROFILE_V01"
POLICY_FIELD = "app_client_profile_policy_version"
PROFILE_FILENAME = "app_client_profile.json"


def empty_profile() -> Dict[str, Any]:
    return {
        "schema_version": POLICY_VERSION,
        "memory_preferences": [],
        "boost_tags": [],
        "avoid_topics": [],
        "writing_style": None,
        "preferred_categories": [],
        "present": False,
    }


def normalize_profile(raw: Any) -> Dict[str, Any]:
    profile = empty_profile()
    if not isinstance(raw, dict):
        return profile
    prefs = raw.get("memory_preferences")
    if isinstance(prefs, list):
        profile["memory_preferences"] = [
            str(x).strip() for x in prefs if isinstance(x, (str, int, float)) and str(x).strip()
        ]
    for key in ("boost_tags", "avoid_topics", "preferred_categories"):
        vals = raw.get(key)
        if isinstance(vals, list):
            profile[key] = [
                str(x).strip() for x in vals if isinstance(x, (str, int, float)) and str(x).strip()
            ]
    style = raw.get("writing_style")
    if isinstance(style, str) and style.strip():
        profile["writing_style"] = style.strip()
    # Infer structured fields from legacy free-text lines when missing
    if not profile["boost_tags"] or not profile["avoid_topics"] or not profile["writing_style"]:
        _infer_from_lines(profile)
    profile["present"] = bool(
        profile["memory_preferences"]
        or profile["boost_tags"]
        or profile["avoid_topics"]
        or profile["writing_style"]
        or profile["preferred_categories"]
    )
    profile["schema_version"] = POLICY_VERSION
    return profile


def _infer_from_lines(profile: Dict[str, Any]) -> None:
    for line in profile["memory_preferences"]:
        lower = line.lower()
        if "writing style:" in lower and not profile["writing_style"]:
            m = re.search(
                r"writing style:\s*(?:writing style:\s*)?([^.\n]+)",
                line,
                re.I,
            )
            if m:
                profile["writing_style"] = m.group(1).strip()
        if "boost these tags" in lower and not profile["boost_tags"]:
            m = re.search(r"boost these tags when evidence exists:\s*(.+)$", line, re.I)
            if m:
                profile["boost_tags"] = [
                    p.strip().rstrip(".") for p in m.group(1).split(",") if p.strip()
                ]
        if "prefer writing about:" in lower and not profile["preferred_categories"]:
            m = re.search(r"prefer writing about:\s*(.+)$", line, re.I)
            if m:
                profile["preferred_categories"] = [
                    p.strip().rstrip(".") for p in m.group(1).split(",") if p.strip()
                ]
        if lower.startswith("avoid:") or "do not emphasize" in lower or "skip scenes" in lower:
            # Keep readable avoid label
            label = line.split(":", 1)[-1].strip() if ":" in line else line.strip()
            if label and label not in profile["avoid_topics"]:
                profile["avoid_topics"].append(label[:120])


def load_beside_manifest(manifest_path: Path) -> Dict[str, Any]:
    path = Path(manifest_path).resolve().parent / PROFILE_FILENAME
    if not path.is_file():
        return empty_profile()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return empty_profile()
    return normalize_profile(raw)


def write_profile(root: Path, raw_bytes: bytes) -> Dict[str, Any]:
    try:
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("app_client_profile is not valid UTF-8 JSON") from exc
    profile = normalize_profile(raw)
    destination = Path(root) / PROFILE_FILENAME
    destination.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return profile


def public_view(profile: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        POLICY_FIELD: POLICY_VERSION,
        "present": bool(profile.get("present")),
        "boost_tags": list(profile.get("boost_tags") or []),
        "avoid_topics": list(profile.get("avoid_topics") or []),
        "writing_style": profile.get("writing_style"),
        "preferred_categories": list(profile.get("preferred_categories") or []),
        "memory_preference_count": len(profile.get("memory_preferences") or []),
    }


def prompt_instruction(profile: Mapping[str, Any]) -> str:
    if not profile.get("present"):
        return ""
    parts = [
        "USER DECLARED SIGNALS (soft editorial only — never invent evidence):",
        "These signals may bias which evidenced moments are emphasized and how copy is worded.",
        "Do not invent people, places, events, or feelings that are not in the supplied facts.",
        "Do not drop a grounded storyline solely because it mismatches preferences.",
    ]
    cats = profile.get("preferred_categories") or []
    if cats:
        parts.append("Preferred content categories (when evidence exists): " + ", ".join(cats) + ".")
    boost = profile.get("boost_tags") or []
    if boost:
        parts.append("Boost tags when observations support them: " + ", ".join(boost) + ".")
    avoid = profile.get("avoid_topics") or []
    if avoid:
        parts.append(
            "Deprioritize (do not fabricate absence): "
            + "; ".join(avoid[:12])
            + "."
        )
    style = profile.get("writing_style")
    if style:
        parts.append(f"Preferred writing style when wording grounded copy: {style}.")
    lines = profile.get("memory_preferences") or []
    if lines:
        parts.append("Raw preference lines:")
        for line in lines[:16]:
            parts.append(f"- {line}")
    return "\n".join(parts)


def _haystack(chapter: Mapping[str, Any]) -> str:
    bits: List[str] = []
    for key in ("title", "summary", "body", "ai_story", "story"):
        val = chapter.get(key)
        if isinstance(val, str):
            bits.append(val)
    tags = chapter.get("tags") or chapter.get("detail_tags") or []
    if isinstance(tags, list):
        bits.extend(str(t) for t in tags if t)
    narrative = chapter.get("narrative")
    if isinstance(narrative, dict):
        for key in ("title", "body", "summary"):
            val = narrative.get(key)
            if isinstance(val, str):
                bits.append(val)
    return " ".join(bits).lower()


def apply_soft_editorial(
    chapters: Sequence[Mapping[str, Any]],
    profile: Mapping[str, Any],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Reorder public chapters: boost matches first, avoid matches last. Never drop."""
    items = [dict(ch) for ch in chapters]
    audit: Dict[str, Any] = {
        POLICY_FIELD: POLICY_VERSION,
        "applied": False,
        "present": bool(profile.get("present")),
        "reorder": [],
        "mode": "SOFT_REORDER_ONLY",
    }
    if not profile.get("present") or len(items) <= 1:
        return items, audit

    boost = [b.lower() for b in (profile.get("boost_tags") or []) + (profile.get("preferred_categories") or [])]
    avoid = [a.lower() for a in (profile.get("avoid_topics") or [])]

    def score(ch: Mapping[str, Any]) -> Tuple[int, int]:
        text = _haystack(ch)
        b = sum(1 for term in boost if term and term in text)
        a = sum(1 for term in avoid if term and term in text)
        return (-b, a)  # more boost first, more avoid last

    indexed = list(enumerate(items))
    indexed.sort(key=lambda pair: (score(pair[1]), pair[0]))
    reordered = [ch for _, ch in indexed]
    if [id(x) for x in reordered] != [id(x) for x in items]:
        audit["applied"] = True
        audit["reorder"] = [
            {
                "from_index": old_i,
                "to_index": new_i,
                "memory_id": reordered[new_i].get("memory_id") or reordered[new_i].get("id"),
                "score": {"boost_hits": -score(reordered[new_i])[0], "avoid_hits": score(reordered[new_i])[1]},
            }
            for new_i, (old_i, _) in enumerate(indexed)
            if old_i != new_i
        ]
    return reordered, audit
