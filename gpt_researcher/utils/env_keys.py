"""Resolve multi-provider API keys with VPS and legacy alias names. :-)

VPS `.env` uses ``CURSOR_API_KEY1`` / ``CURSOR_API_KEY2`` (no underscore before
the digit) and ``AZURE_OPENAI_GPT52_API_KEY``. Older workspace slots used
``CURSOR_API_KEY_1``, ``CURSOR_API_KEY_2``, and ``ASUS_API_KEY``. Callers should
use these helpers so either spelling works.
"""

from __future__ import annotations

import os
from typing import Iterable


# Canonical slot → accepted environment variable names (first match wins).
CURSOR1_KEY_NAMES: tuple[str, ...] = (
    "CURSOR_API_KEY1",
    "CURSOR_API_KEY_1",
    "CURSOR_API_KEY",
)
CURSOR2_KEY_NAMES: tuple[str, ...] = (
    "CURSOR_API_KEY2",
    "CURSOR_API_KEY_2",
)
AZURE_GPT52_KEY_NAMES: tuple[str, ...] = (
    "AZURE_OPENAI_GPT52_API_KEY",
    "ASUS_API_KEY",
    "AZURE_OPENAI_API_KEY",
)
OPENROUTER_KEY_NAMES: tuple[str, ...] = ("OPENROUTER_API_KEY",)

# Populate missing alias env vars from the preferred VPS names so downstream
# libraries that only know one spelling still work.
_ALIAS_MIRRORS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("CURSOR_API_KEY1", ("CURSOR_API_KEY_1", "CURSOR_API_KEY")),
    ("CURSOR_API_KEY_1", ("CURSOR_API_KEY1",)),
    ("CURSOR_API_KEY2", ("CURSOR_API_KEY_2",)),
    ("CURSOR_API_KEY_2", ("CURSOR_API_KEY2",)),
    ("AZURE_OPENAI_GPT52_API_KEY", ("ASUS_API_KEY",)),
    ("ASUS_API_KEY", ("AZURE_OPENAI_GPT52_API_KEY",)),
)


def first_env(*names: str) -> str | None:
    """Return the first non-empty environment value among ``names``."""
    for name in names:
        value = os.environ.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def require_env(*names: str, label: str | None = None) -> str:
    """Return the first non-empty env value or raise with the accepted names."""
    value = first_env(*names)
    if value:
        return value
    shown = ", ".join(names)
    what = label or "API key"
    raise ValueError(
        f"Missing {what}. Set one of: {shown}."
    )


def apply_llm_key_aliases() -> list[str]:
    """Mirror filled VPS key names onto legacy aliases (and vice versa).

    Returns the list of destination variable names that were newly populated.
    Does not overwrite a destination that is already non-empty.
    """
    populated: list[str] = []
    for source, destinations in _ALIAS_MIRRORS:
        src_val = first_env(source)
        if not src_val:
            continue
        for dest in destinations:
            existing = os.environ.get(dest)
            if existing is not None and str(existing).strip():
                continue
            os.environ[dest] = src_val
            populated.append(dest)
    # Keep standard Azure chat vars aligned with the GPT-5.2 deployment when
    # only the GPT52_* block is filled (common on the research VPS).
    gpt52_key = first_env(*AZURE_GPT52_KEY_NAMES)
    if gpt52_key and not first_env("AZURE_OPENAI_API_KEY"):
        os.environ["AZURE_OPENAI_API_KEY"] = gpt52_key
        populated.append("AZURE_OPENAI_API_KEY")
    gpt52_endpoint = first_env(
        "AZURE_OPENAI_GPT52_ENDPOINT", "AZURE_OPENAI_ENDPOINT"
    )
    if gpt52_endpoint and not first_env("AZURE_OPENAI_ENDPOINT"):
        os.environ["AZURE_OPENAI_ENDPOINT"] = gpt52_endpoint
        populated.append("AZURE_OPENAI_ENDPOINT")
    gpt52_version = first_env(
        "AZURE_OPENAI_GPT52_API_VERSION",
        "AZURE_OPENAI_API_VERSION",
        "OPENAI_API_VERSION",
    )
    if gpt52_version and not first_env("AZURE_OPENAI_API_VERSION"):
        os.environ["AZURE_OPENAI_API_VERSION"] = gpt52_version
        populated.append("AZURE_OPENAI_API_VERSION")
    return populated


def cursor_api_key(slot: int = 1) -> str:
    """Resolve Cursor API key for slot 1 or 2."""
    if slot == 1:
        return require_env(*CURSOR1_KEY_NAMES, label="Cursor API key (slot 1)")
    if slot == 2:
        return require_env(*CURSOR2_KEY_NAMES, label="Cursor API key (slot 2)")
    raise ValueError(f"Unsupported Cursor key slot: {slot}")


def azure_gpt52_api_key() -> str:
    """Resolve Azure GPT-5.2 / Asus API key."""
    return require_env(*AZURE_GPT52_KEY_NAMES, label="Azure GPT-5.2 API key")


def openrouter_api_key() -> str:
    """Resolve OpenRouter API key."""
    return require_env(*OPENROUTER_KEY_NAMES, label="OpenRouter API key")


def filled_slots(names: Iterable[str]) -> dict[str, bool]:
    """Report whether each name is non-empty (never returns secret values)."""
    return {name: bool(first_env(name)) for name in names}
