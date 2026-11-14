"""Helpers for verifying multi-language playbook prompt rendering. :-)"""

from __future__ import annotations

from typing import Dict, List, Sequence

from .apply import apply_playbook, build_custom_prompt
from .languages import LANGUAGE_CATALOG, format_language_directive, normalize_language_ids
from .loader import get_playbook

# Markers that must appear in the LLM user prompt when a market is selected.
MARKET_MARKERS: Dict[str, List[str]] = {
    "en": ["English"],
    "zh-cn": ["普通话", "Mainland Mandarin"],
    "zh-yue": ["粵語", "Hong Kong Cantonese"],
    "zh-tw": ["國語", "Taiwan Mandarin"],
}


def llm_user_message(playbook_id: str, query: str, language_ids: Sequence[str]) -> str:
    """Build the exact custom_prompt-shaped user message the writer path uses.

    Mirrors ``actions/report_generation.py`` when ``custom_prompt`` is set:
    ``{custom_prompt}\\n\\nContext: {context}``.
    """
    applied = apply_playbook(
        playbook_id,
        query=query,
        language_ids=language_ids,
    )
    # Context is filled at runtime from research; use a stable stub for tests.
    context = f"[stub context for {','.join(applied.language_ids)}]"
    return f"{applied.custom_prompt}\n\nContext: {context}"


def markets_present_in_text(text: str, language_ids: Sequence[str]) -> Dict[str, bool]:
    """Return whether each requested market's markers appear in ``text``."""
    ids = normalize_language_ids(language_ids)
    found: Dict[str, bool] = {}
    for lang_id in ids:
        markers = MARKET_MARKERS[lang_id]
        found[lang_id] = any(marker in text for marker in markers)
    return found


def unintended_markets(text: str, language_ids: Sequence[str]) -> List[str]:
    """Markets whose markers appear even though they were not requested.

    Single-market prompts use only the market's llm_name (no collapse clause),
    so other Chinese markets should not be named.
    """
    requested = set(normalize_language_ids(language_ids))
    if len(requested) != 1:
        return []
    extras: List[str] = []
    for lang_id, markers in MARKET_MARKERS.items():
        if lang_id in requested:
            continue
        # Native script markers are decisive for Chinese markets.
        native = LANGUAGE_CATALOG[lang_id]["native"]
        if lang_id != "en" and native in text:
            extras.append(lang_id)
        elif lang_id == "en" and "English" in text and "write the brief in: English" in text.lower():
            # Only flag English if it is the write-target line for a non-English run.
            pass
    return extras


def single_market_write_target(language_id: str) -> str:
    """The language directive string for a one-market playbook run."""
    return format_language_directive([language_id])


def comedy_shorts_prompt_for(language_id: str, query: str = "salon comedy hooks") -> str:
    """Convenience: comedy_shorts custom prompt scoped to one market."""
    template = get_playbook("comedy_shorts")
    directive = single_market_write_target(language_id)
    return build_custom_prompt(
        template,
        query=query,
        language_directive=directive,
        language_ids=[language_id],
    )
