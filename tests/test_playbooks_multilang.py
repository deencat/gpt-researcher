"""Multi-language rendering checks for comedy_shorts playbook. :-)"""

from __future__ import annotations

import pytest

from gpt_researcher.playbooks import (
    apply_playbook,
    clear_playbook_cache,
    comedy_shorts_prompt_for,
    llm_user_message,
    markets_present_in_text,
    single_market_write_target,
)
from gpt_researcher.playbooks.languages import LANGUAGE_CATALOG
from gpt_researcher.playbooks.render import unintended_markets


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_playbook_cache()
    yield
    clear_playbook_cache()


ALL_MARKETS = ["en", "zh-cn", "zh-yue", "zh-tw"]


@pytest.mark.parametrize("lang_id", ALL_MARKETS)
def test_single_market_write_target_is_native_scoped(lang_id: str):
    target = single_market_write_target(lang_id)
    meta = LANGUAGE_CATALOG[lang_id]
    assert meta["llm_name"] == target
    assert meta["native"] in target or lang_id == "en"
    # Single-market must not pull in the multi-market collapse clause.
    assert "do not collapse" not in target


@pytest.mark.parametrize("lang_id", ALL_MARKETS)
def test_comedy_shorts_prompt_targets_one_market(lang_id: str):
    prompt = comedy_shorts_prompt_for(lang_id, query="facial fail hooks")
    assert "facial fail hooks" in prompt
    assert f"You MUST write the brief in: {LANGUAGE_CATALOG[lang_id]['llm_name']}" in prompt
    # Required structure still present so output stays a shippable brief.
    assert "Title options" in prompt
    assert "Hooks" in prompt
    assert "Script outline" in prompt
    present = markets_present_in_text(prompt, [lang_id])
    assert present[lang_id] is True
    assert unintended_markets(prompt, [lang_id]) == []


@pytest.mark.parametrize("lang_id", ALL_MARKETS)
def test_llm_user_message_embeds_context_and_market(lang_id: str):
    message = llm_user_message(
        "comedy_shorts",
        query=f"hooks for {lang_id}",
        language_ids=[lang_id],
    )
    assert "Context:" in message
    assert f"stub context for {lang_id}" in message
    assert LANGUAGE_CATALOG[lang_id]["llm_name"] in message
    # Writer path sections survive into the final user message.
    assert "## Hooks" in message or "Hooks" in message


def test_all_four_markets_together_keep_distinction_clause():
    applied = apply_playbook(
        "comedy_shorts",
        query="weekly beauty comedy angles",
        language_ids=ALL_MARKETS,
    )
    text = applied.custom_prompt
    present = markets_present_in_text(text, ALL_MARKETS)
    assert all(present.values()), present
    assert "普通话" in applied.language
    assert "粵語" in applied.language
    assert "國語" in applied.language
    assert "English" in applied.language
    assert "do not collapse" in applied.language


def test_cantonese_only_excludes_other_chinese_natives():
    prompt = comedy_shorts_prompt_for("zh-yue")
    assert "粵語" in prompt
    assert "普通话" not in prompt
    assert "國語" not in prompt


def test_taiwan_only_excludes_cantonese_and_mainland_natives():
    prompt = comedy_shorts_prompt_for("zh-tw")
    assert "國語" in prompt
    assert "粵語" not in prompt
    assert "普通话" not in prompt


def test_mainland_only_excludes_cantonese_and_taiwan_natives():
    prompt = comedy_shorts_prompt_for("zh-cn")
    assert "普通话" in prompt
    assert "粵語" not in prompt
    assert "國語" not in prompt


def test_english_only_has_no_chinese_natives():
    prompt = comedy_shorts_prompt_for("en")
    assert "You MUST write the brief in: English" in prompt
    assert "普通话" not in prompt
    assert "粵語" not in prompt
    assert "國語" not in prompt
