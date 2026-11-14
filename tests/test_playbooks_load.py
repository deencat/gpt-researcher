"""Parallel load tests for playbook catalog + merge. :-)"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from gpt_researcher.playbooks import (
    apply_playbook,
    clear_playbook_cache,
    get_playbook,
    list_playbooks,
    merge_start_payload,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_playbook_cache()
    yield
    clear_playbook_cache()


def test_parallel_catalog_reads_are_identical():
    def read(_i: int):
        return tuple(sorted(p.id for p in list_playbooks()))

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(read, range(64)))
    assert all(r == results[0] for r in results)
    assert "comedy_shorts" in results[0]


def test_parallel_merges_with_varying_languages():
    languages = [
        ["en"],
        ["zh-cn"],
        ["zh-yue"],
        ["zh-tw"],
        ["en", "zh-yue"],
        ["en", "zh-cn", "zh-yue", "zh-tw"],
    ]

    def merge_one(i: int):
        langs = languages[i % len(languages)]
        payload = merge_start_payload(
            {
                "task": f"load-test-{i}",
                "playbook_id": "comedy_shorts",
                "language_ids": langs,
            }
        )
        return payload["playbook_id"], tuple(payload["language_ids"]), f"load-test-{i}" in payload["custom_prompt"]

    with ThreadPoolExecutor(max_workers=12) as pool:
        outs = list(pool.map(merge_one, range(48)))

    assert all(pid == "comedy_shorts" for pid, _, _ in outs)
    assert all(ok for _, _, ok in outs)
    # Spot-check a few language resolutions survived concurrency.
    resolved = {langs for _, langs, _ in outs}
    assert ("en",) in resolved
    assert ("zh-yue",) in resolved
    assert ("en", "zh-cn", "zh-yue", "zh-tw") in resolved


def test_parallel_mixed_get_apply_merge():
    errors: list[BaseException] = []
    results: list[str] = []

    def catalog():
        results.append("c:" + ",".join(p.id for p in list_playbooks()))

    def fetch():
        results.append("g:" + get_playbook("comedy_shorts").id)

    def apply_one(i: int):
        applied = apply_playbook("comedy_shorts", query=f"q{i}", language_ids=["en", "zh-tw"])
        results.append("a:" + applied.playbook_id + ":" + ",".join(applied.language_ids))

    def merge_one(i: int):
        merged = merge_start_payload(
            {"task": f"m{i}", "playbook_id": "comedy_shorts", "language_ids": ["zh-cn"]}
        )
        results.append("m:" + merged["playbook_id"])

    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = []
        for i in range(20):
            futures.append(pool.submit(catalog))
            futures.append(pool.submit(fetch))
            futures.append(pool.submit(apply_one, i))
            futures.append(pool.submit(merge_one, i))
        for fut in as_completed(futures):
            try:
                fut.result()
            except BaseException as exc:  # pragma: no cover
                errors.append(exc)

    assert not errors
    assert any(r.startswith("c:") and "comedy_shorts" in r for r in results)
    assert results.count("g:comedy_shorts") == 20
    assert sum(1 for r in results if r.startswith("a:comedy_shorts:en,zh-tw")) == 20
    assert results.count("m:comedy_shorts") == 20


def test_parallel_unknown_playbook_errors_isolated():
    def boom(_i: int):
        with pytest.raises(Exception):
            merge_start_payload({"task": "x", "playbook_id": "missing_pack"})
        return True

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert all(pool.map(boom, range(16)))
    # Catalog still healthy after parallel failures.
    assert get_playbook("comedy_shorts").id == "comedy_shorts"
