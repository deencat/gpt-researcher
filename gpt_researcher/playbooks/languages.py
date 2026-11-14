"""Multi-language defaults for playbook templates. :-)"""

from __future__ import annotations

from typing import Dict, List, Sequence

# Stable ids used in YAML templates and the project setup coach.
LANGUAGE_CATALOG: Dict[str, Dict[str, str]] = {
    "en": {
        "id": "en",
        "label": "English",
        "native": "English",
        "llm_name": "English",
    },
    "zh-cn": {
        "id": "zh-cn",
        "label": "Mainland Mandarin",
        "native": "普通话",
        "llm_name": "Mainland Mandarin (普通话)",
    },
    "zh-yue": {
        "id": "zh-yue",
        "label": "Hong Kong Cantonese",
        "native": "粵語",
        "llm_name": "Hong Kong Cantonese (粵語)",
    },
    "zh-tw": {
        "id": "zh-tw",
        "label": "Taiwan Mandarin",
        "native": "國語",
        "llm_name": "Taiwan Mandarin (國語)",
    },
}

DEFAULT_PLAYBOOK_LANGUAGES: List[str] = ["en", "zh-cn", "zh-yue", "zh-tw"]


def normalize_language_ids(ids: Sequence[str] | None) -> List[str]:
    """Return known language ids, preserving order and dropping unknowns."""
    if not ids:
        return []
    seen = set()
    out: List[str] = []
    for raw in ids:
        key = str(raw).strip().lower()
        if key in LANGUAGE_CATALOG and key not in seen:
            seen.add(key)
            out.append(key)
    return out


def language_labels(ids: Sequence[str] | None) -> List[str]:
    """Human-readable labels for the given language ids."""
    return [LANGUAGE_CATALOG[i]["llm_name"] for i in normalize_language_ids(ids)]


def format_language_directive(ids: Sequence[str] | None) -> str:
    """Build the LANGUAGE string written into report prompts.

    Multi-market playbooks need an explicit directive so the model does not
    collapse 普通话 / 粵語 / 國語 into a single "Chinese".
    """
    labels = language_labels(ids)
    if not labels:
        return "english"
    if len(labels) == 1:
        return labels[0]
    joined = ", ".join(labels[:-1]) + f", and {labels[-1]}"
    return (
        f"{joined}. When Chinese markets are included, always distinguish "
        "Mainland Mandarin (普通话), Hong Kong Cantonese (粵語), and Taiwan "
        "Mandarin (國語) — do not collapse them. Separate findings by market "
        "when humor, slang, or taboos differ"
    )


def catalog_public() -> List[Dict[str, str]]:
    """Public catalog for API / frontend selectors."""
    return [
        {
            "id": meta["id"],
            "label": meta["label"],
            "native": meta["native"],
        }
        for meta in LANGUAGE_CATALOG.values()
    ]
