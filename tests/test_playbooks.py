"""Tests for the playbook template system. :-)"""

from __future__ import annotations

import pytest

from gpt_researcher.playbooks import (
    PlaybookNotFoundError,
    apply_playbook,
    clear_playbook_cache,
    format_language_directive,
    get_playbook,
    list_playbooks,
    merge_start_payload,
)
from gpt_researcher.playbooks.languages import LANGUAGE_CATALOG
from gpt_researcher.utils.enum import Tone


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_playbook_cache()
    yield
    clear_playbook_cache()


def test_list_includes_comedy_shorts():
    ids = [p.id for p in list_playbooks()]
    assert "comedy_shorts" in ids


def test_comedy_shorts_schema():
    pb = get_playbook("comedy_shorts")
    assert pb.name
    assert pb.tone == "Humorous"
    assert Tone[pb.tone]  # must be a valid Tone enum member name
    assert pb.report_type == "research_report"
    assert set(pb.languages) == {"en", "zh-cn", "zh-yue", "zh-tw"}
    assert len(pb.structure) >= 4
    section_ids = {s.id for s in pb.structure}
    assert "hooks" in section_ids
    assert "script_outline" in section_ids
    assert "title_options" in section_ids
    assert pb.starter_prompts
    assert "普通话" in pb.instructions or "普通话" in format_language_directive(pb.languages)


def test_language_directive_distinguishes_chinese_markets():
    text = format_language_directive(["en", "zh-cn", "zh-yue", "zh-tw"])
    assert "普通话" in text
    assert "粵語" in text
    assert "國語" in text
    assert "do not collapse" in text.lower() or "collapse" in text


def test_unknown_playbook_raises():
    with pytest.raises(PlaybookNotFoundError):
        get_playbook("does_not_exist")


def test_apply_playbook_builds_custom_prompt():
    applied = apply_playbook(
        "comedy_shorts",
        query="Funny salon facial fails for Reels",
    )
    assert applied.playbook_id == "comedy_shorts"
    assert applied.tone == "Humorous"
    assert "Funny salon facial fails" in applied.custom_prompt
    assert "## Hooks" in applied.custom_prompt or "Hooks" in applied.custom_prompt
    assert "## Script outline" in applied.custom_prompt or "Script outline" in applied.custom_prompt
    assert "Title options" in applied.custom_prompt
    assert applied.language_ids == ["en", "zh-cn", "zh-yue", "zh-tw"]
    assert applied.total_words == 900


def test_request_overrides_win():
    applied = apply_playbook(
        "comedy_shorts",
        query="test",
        tone="Casual",
        report_type="detailed_report",
        language_ids=["en", "zh-yue"],
    )
    assert applied.tone == "Casual"
    assert applied.report_type == "detailed_report"
    assert applied.language_ids == ["en", "zh-yue"]
    assert "Hong Kong Cantonese" in applied.language


def test_merge_start_payload_without_playbook_is_passthrough():
    raw = {"task": "hello", "report_type": "research_report", "tone": "Objective"}
    merged = merge_start_payload(raw)
    assert merged["task"] == "hello"
    assert "custom_prompt" not in merged
    assert "playbook_id" not in merged


def test_merge_start_payload_with_playbook():
    merged = merge_start_payload(
        {
            "task": "Beauty comedy hooks this week",
            "playbook_id": "comedy_shorts",
            "report_type": "research_report",
        }
    )
    assert merged["playbook_id"] == "comedy_shorts"
    assert merged["tone"] == "Humorous"
    assert merged["custom_prompt"]
    assert "Beauty comedy hooks" in merged["custom_prompt"]
    assert merged["language"]
    assert set(merged["language_ids"]) == set(LANGUAGE_CATALOG)


def test_public_dict_has_expected_keys():
    public = get_playbook("comedy_shorts").to_public_dict()
    for key in (
        "id",
        "name",
        "topic",
        "tone",
        "structure",
        "output_format",
        "languages",
        "starter_prompts",
    ):
        assert key in public
