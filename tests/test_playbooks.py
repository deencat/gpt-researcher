"""Tests for the playbook template system. :-)"""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from gpt_researcher.playbooks import (
    PlaybookNotFoundError,
    apply_playbook,
    apply_to_researcher,
    clear_playbook_cache,
    format_language_directive,
    get_playbook,
    list_playbooks,
    merge_start_payload,
    parse_playbook_dict,
)
from gpt_researcher.playbooks.languages import (
    DEFAULT_PLAYBOOK_LANGUAGES,
    LANGUAGE_CATALOG,
    normalize_language_ids,
)
from gpt_researcher.playbooks.loader import _load_file
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


# --- QA coverage expansions ---


def test_parse_rejects_non_mapping():
    with pytest.raises(ValueError, match="mapping"):
        parse_playbook_dict(["not", "a", "dict"])  # type: ignore[arg-type]


def test_parse_requires_id():
    with pytest.raises(ValueError, match="id"):
        parse_playbook_dict({"name": "Missing id"})


def test_parse_uses_fallback_id_from_filename_stem():
    pb = parse_playbook_dict({"name": "From stem"}, fallback_id="stem_id")
    assert pb.id == "stem_id"


def test_parse_empty_languages_falls_back_to_defaults():
    pb = parse_playbook_dict({"id": "empty_langs", "languages": []})
    assert pb.languages == list(DEFAULT_PLAYBOOK_LANGUAGES)


def test_parse_unknown_languages_only_falls_back():
    pb = parse_playbook_dict({"id": "bad_langs", "languages": ["xx", "yy"]})
    assert pb.languages == list(DEFAULT_PLAYBOOK_LANGUAGES)


def test_parse_invalid_total_words_raises():
    with pytest.raises(ValueError, match="total_words"):
        parse_playbook_dict({"id": "bad_words", "total_words": "many"})


def test_parse_string_structure_sections():
    pb = parse_playbook_dict(
        {"id": "str_sections", "structure": ["Hook Ideas", "Script beats"]}
    )
    assert [s.id for s in pb.structure] == ["hook_ideas", "script_beats"]
    assert pb.structure[0].title == "Hook Ideas"


def test_parse_skips_malformed_structure_items():
    pb = parse_playbook_dict(
        {
            "id": "messy",
            "structure": [None, 42, {"title": "OK"}, {"id": ""}, "Keep Me"],
        }
    )
    ids = [s.id for s in pb.structure]
    assert "ok" in ids
    assert "keep_me" in ids
    assert len(ids) == 2


def test_load_file_invalid_yaml_raises(tmp_path: Path):
    bad = tmp_path / "broken.yaml"
    bad.write_text("tone: [unterminated\n", encoding="utf-8")
    with pytest.raises(yaml.YAMLError):
        _load_file(bad)


def test_load_file_yaml_list_rejected(tmp_path: Path):
    path = tmp_path / "list.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        _load_file(path)


def test_index_skips_corrupt_yaml_and_keeps_valid(tmp_path: Path):
    (tmp_path / "good.yaml").write_text(
        yaml.safe_dump({"id": "good_pb", "name": "Good", "tone": "Casual"}),
        encoding="utf-8",
    )
    (tmp_path / "bad.yaml").write_text("::::::not yaml", encoding="utf-8")
    (tmp_path / "_ignored.yaml").write_text(
        yaml.safe_dump({"id": "ignored", "name": "Ignored"}),
        encoding="utf-8",
    )
    playbooks = list_playbooks(tmp_path)
    ids = [p.id for p in playbooks]
    assert ids == ["good_pb"]
    assert "ignored" not in ids


def test_json_template_loads(tmp_path: Path):
    (tmp_path / "json_pb.json").write_text(
        json.dumps({"id": "json_pb", "name": "JSON Pack", "tone": "Objective"}),
        encoding="utf-8",
    )
    pb = get_playbook("json_pb", templates_dir=tmp_path)
    assert pb.name == "JSON Pack"


def test_missing_templates_dir_returns_empty(tmp_path: Path):
    missing = tmp_path / "nope"
    assert list_playbooks(missing) == []
    with pytest.raises(PlaybookNotFoundError):
        get_playbook("anything", templates_dir=missing)


def test_empty_playbook_id_raises():
    with pytest.raises(PlaybookNotFoundError):
        get_playbook("")
    with pytest.raises(PlaybookNotFoundError):
        get_playbook("   ")


def test_language_directive_empty_falls_back_to_english():
    assert format_language_directive([]) == "english"
    assert format_language_directive(None) == "english"


def test_language_directive_single_market_no_collapse_clause():
    text = format_language_directive(["en"])
    assert text == "English"
    assert "collapse" not in text


def test_normalize_language_ids_dedupes_and_drops_unknown():
    assert normalize_language_ids(["EN", "zh-yue", "en", "nope"]) == ["en", "zh-yue"]


def test_apply_empty_language_ids_uses_template_defaults():
    applied = apply_playbook("comedy_shorts", query="q", language_ids=[])
    assert applied.language_ids == ["en", "zh-cn", "zh-yue", "zh-tw"]


def test_apply_unknown_language_ids_fall_back_to_template():
    applied = apply_playbook("comedy_shorts", query="q", language_ids=["xx"])
    assert applied.language_ids == ["en", "zh-cn", "zh-yue", "zh-tw"]


def test_apply_seeds_subtopics_from_structure():
    applied = apply_playbook("comedy_shorts", query="q")
    titles = [s["task"] for s in applied.subtopics]
    assert "Hooks" in titles
    assert "Script outline" in titles


def test_apply_to_researcher_mutates_cfg_and_role():
    applied = apply_playbook("comedy_shorts", query="q")
    researcher = SimpleNamespace(
        cfg=SimpleNamespace(language="english", report_format="apa", total_words=1000),
        agent="auto",
        role="auto",
    )
    apply_to_researcher(researcher, applied)
    assert researcher.cfg.language == applied.language
    assert researcher.cfg.report_format == "markdown"
    assert researcher.cfg.total_words == 900
    assert researcher.agent == applied.agent_role
    assert researcher.role == applied.agent_role


def test_merge_whitespace_playbook_id_is_ignored():
    merged = merge_start_payload({"task": "x", "playbook_id": "   "})
    assert "custom_prompt" not in merged


def test_merge_playbook_alias_string_works():
    merged = merge_start_payload({"task": "alias query", "playbook": "comedy_shorts"})
    assert merged["playbook_id"] == "comedy_shorts"
    assert "alias query" in merged["custom_prompt"]


def test_merge_ignores_non_string_playbook_metadata_dict():
    """Already-merged `playbook` dict must not be treated as an id."""
    merged = merge_start_payload(
        {
            "task": "x",
            "playbook": {"playbook_id": "comedy_shorts", "custom_prompt": "stale"},
        }
    )
    assert "custom_prompt" not in merged


def test_merge_malformed_non_dict_returns_empty():
    assert merge_start_payload(None) == {}
    assert merge_start_payload("not-json") == {}
    assert merge_start_payload(["list"]) == {}


def test_merge_empty_language_ids_list_uses_template():
    merged = merge_start_payload(
        {
            "task": "x",
            "playbook_id": "comedy_shorts",
            "language_ids": [],
        }
    )
    assert merged["language_ids"] == ["en", "zh-cn", "zh-yue", "zh-tw"]


def test_merge_preserves_existing_subtopics():
    custom = [{"task": "Custom", "description": "Keep me"}]
    merged = merge_start_payload(
        {
            "task": "x",
            "playbook_id": "comedy_shorts",
            "subtopics": custom,
        }
    )
    assert merged["subtopics"] == custom


def test_merge_non_string_tone_ignored_uses_template():
    merged = merge_start_payload(
        {
            "task": "x",
            "playbook_id": "comedy_shorts",
            "tone": ["Humorous"],
            "report_type": 123,
        }
    )
    assert merged["tone"] == "Humorous"
    assert merged["report_type"] == "research_report"


def test_merge_unknown_playbook_raises():
    with pytest.raises(PlaybookNotFoundError):
        merge_start_payload({"task": "x", "playbook_id": "missing_pack"})


def test_concurrent_list_playbooks_is_stable():
    results = []
    errors = []

    def worker():
        try:
            results.append(tuple(p.id for p in list_playbooks()))
        except Exception as exc:  # pragma: no cover - failure path
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    assert len(results) == 8
    assert all(r == results[0] for r in results)
    assert "comedy_shorts" in results[0]


def test_concurrent_apply_playbook_via_pool():
    with ThreadPoolExecutor(max_workers=4) as pool:
        outs = list(
            pool.map(
                lambda i: apply_playbook("comedy_shorts", query=f"q{i}").playbook_id,
                range(12),
            )
        )
    assert outs == ["comedy_shorts"] * 12
