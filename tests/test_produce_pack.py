"""Tests for comedy pack JSON extraction helpers. :-)"""

import pytest

from gpt_researcher.playbooks.produce_pack import PACK_FILES, _extract_json


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
