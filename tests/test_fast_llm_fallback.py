"""Tests for Fast-slot LLM fallback resolution. :-)"""

import pytest

from gpt_researcher.utils.llm import parse_llm_spec, resolve_fast_fallback


@pytest.fixture(autouse=True)
def _clear_fast_env(monkeypatch):
    monkeypatch.delenv("FAST_LLM", raising=False)
    monkeypatch.delenv("FAST_LLM_FALLBACK", raising=False)


def test_parse_llm_spec():
    assert parse_llm_spec("deepseek:deepseek-chat") == (
        "deepseek",
        "deepseek-chat",
    )


def test_resolve_applies_only_to_fast_primary(monkeypatch):
    monkeypatch.setenv("FAST_LLM", "openrouter:google/gemini-2.5-flash")
    monkeypatch.setenv("FAST_LLM_FALLBACK", "deepseek:deepseek-chat")
    assert (
        resolve_fast_fallback("openrouter", "google/gemini-2.5-flash")
        == "deepseek:deepseek-chat"
    )
    assert resolve_fast_fallback("azure_openai", "gpt-5.2") is None


def test_explicit_fallback_wins(monkeypatch):
    monkeypatch.setenv("FAST_LLM", "openrouter:google/gemini-2.5-flash")
    monkeypatch.setenv("FAST_LLM_FALLBACK", "deepseek:deepseek-chat")
    assert (
        resolve_fast_fallback(
            "openrouter",
            "google/gemini-2.5-flash",
            explicit_fallback="deepseek:deepseek-reasoner",
        )
        == "deepseek:deepseek-reasoner"
    )
