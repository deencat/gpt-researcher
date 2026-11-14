"""Tests for multi-provider API key alias resolution. :-)"""

import os

import pytest

from gpt_researcher.utils.env_keys import (
    apply_llm_key_aliases,
    cursor_api_key,
    first_env,
    openrouter_api_key,
    require_env,
)


@pytest.fixture(autouse=True)
def _clear_key_env(monkeypatch):
    for name in (
        "CURSOR_API_KEY1",
        "CURSOR_API_KEY2",
        "CURSOR_API_KEY_1",
        "CURSOR_API_KEY_2",
        "CURSOR_API_KEY",
        "ASUS_API_KEY",
        "AZURE_OPENAI_GPT52_API_KEY",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_GPT52_ENDPOINT",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_GPT52_API_VERSION",
        "AZURE_OPENAI_API_VERSION",
        "OPENAI_API_VERSION",
        "OPENROUTER_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_first_env_prefers_vps_cursor_key1(monkeypatch):
    monkeypatch.setenv("CURSOR_API_KEY1", "vps-key-1")
    monkeypatch.setenv("CURSOR_API_KEY_1", "legacy-key-1")
    assert first_env("CURSOR_API_KEY1", "CURSOR_API_KEY_1") == "vps-key-1"
    assert cursor_api_key(1) == "vps-key-1"


def test_cursor_slot2_accepts_legacy_underscore(monkeypatch):
    monkeypatch.setenv("CURSOR_API_KEY_2", "legacy-key-2")
    assert cursor_api_key(2) == "legacy-key-2"


def test_apply_aliases_mirrors_vps_names(monkeypatch):
    monkeypatch.setenv("CURSOR_API_KEY1", "k1")
    monkeypatch.setenv("CURSOR_API_KEY2", "k2")
    monkeypatch.setenv("AZURE_OPENAI_GPT52_API_KEY", "azure52")
    populated = apply_llm_key_aliases()
    assert "CURSOR_API_KEY_1" in populated
    assert os.environ["CURSOR_API_KEY_1"] == "k1"
    assert os.environ["CURSOR_API_KEY_2"] == "k2"
    assert os.environ["ASUS_API_KEY"] == "azure52"
    assert os.environ["AZURE_OPENAI_API_KEY"] == "azure52"


def test_openrouter_required(monkeypatch):
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        openrouter_api_key()
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
    assert openrouter_api_key() == "or-key"


def test_require_env_lists_accepted_names():
    with pytest.raises(ValueError, match="CURSOR_API_KEY1"):
        require_env("CURSOR_API_KEY1", "CURSOR_API_KEY_1", label="Cursor")
