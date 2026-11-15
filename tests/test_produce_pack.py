"""Tests for comedy pack JSON extraction helpers. :-)"""

import pytest

from gpt_researcher.playbooks.produce_pack import (
    PACK_FILES,
    STORIES_PER_LANGUAGE,
    STORY_LANGUAGES,
    _extract_json,
    _slice_stories_for_language,
    assemble_scripts_markdown,
    assemble_stories_markdown,
)


def test_extract_json_from_fenced_payload():
    raw = """```json
{"plan": "# Comedy Channel — Production Plan\\nA", "stories": "# Comedy Channel — Scored Story List\\nB", "scripts": "# Comedy Channel — Shootable Scripts\\nC"}
```"""
    data = _extract_json(raw)
    assert set(data) >= {"plan", "stories", "scripts"}
    assert data["plan"].startswith("# Comedy Channel")


def test_pack_filenames():
    assert [f for _, f in PACK_FILES] == ["01_Plan.md", "02_Stories.md", "03_Scripts.md"]


def test_extract_json_rejects_garbage():
    with pytest.raises(ValueError):
        _extract_json("no json here")


def test_story_language_targets():
    assert STORIES_PER_LANGUAGE == 10
    assert len(STORY_LANGUAGES) == 4
    assert STORIES_PER_LANGUAGE * len(STORY_LANGUAGES) == 40
    labels = " ".join(lang["label"] for lang in STORY_LANGUAGES)
    assert "English" in labels
    assert "粵語" in labels
    assert "普通话" in labels
    assert "國語" in labels


def test_assemble_stories_markdown_joins_batches():
    md = assemble_stories_markdown(
        [
            "## English (EN) — 10 stories\n\n## 1) ID: EN01 — A",
            "## Hong Kong Cantonese (粵語) — 10 stories\n\n## 1) ID: YUE01 — B",
        ]
    )
    assert md.startswith("# Comedy Channel — Scored Story List")
    assert "40 total" in md
    assert "EN01" in md and "YUE01" in md


def test_slice_stories_for_language():
    md = (
        "# Comedy Channel — Scored Story List\n\n"
        "## English (EN) — 10 stories\n\n1. **EN01 — Trim**\n\n"
        "## Hong Kong Cantonese (粵語) — 10 stories\n\n1. **YUE01 — Speed**\n\n"
        "## Mainland Mandarin (普通话) — 10 stories\n\n1. **CMN01 — Bao**\n\n"
        "## Taiwan Mandarin (國語) — 10 stories\n\n1. **TW01 — Micro**\n"
    )
    en = _slice_stories_for_language(md, STORY_LANGUAGES[0])
    yue = _slice_stories_for_language(md, STORY_LANGUAGES[1])
    assert "EN01" in en and "YUE01" not in en
    assert "YUE01" in yue and "EN01" not in yue


def test_assemble_scripts_markdown():
    md = assemble_scripts_markdown(
        [
            '## Script (EN01): “Trim” (40s, English)\nCast: A',
            '## Script (YUE01): “Speed” (30s, 粵語)\nCast: B',
        ]
    )
    assert md.startswith("# Comedy Channel — Shootable Scripts")
    assert "EN01" in md and "YUE01" in md
