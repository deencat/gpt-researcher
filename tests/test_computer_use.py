"""Unit tests for computer_use (no live browser required)."""

from __future__ import annotations

import pytest

from gpt_researcher.computer_use.actions import (
    computer_use_mode,
    handle_computer_use,
    run_python_sandbox,
)
from gpt_researcher.computer_use.isolated import _host_allowed as isolated_host_allowed
from gpt_researcher.computer_use.isolated import status as isolated_status
from gpt_researcher.computer_use.schema import get_computer_use_schema
from gpt_researcher.computer_use.session import _host_allowed


def test_schema_has_core_actions():
    schema = get_computer_use_schema()
    assert schema["name"] == "computer_use"
    actions = schema["parameters"]["properties"]["action"]["enum"]
    assert "navigate" in actions
    assert "snapshot" in actions
    assert "run_python" in actions
    assert "status" in actions
    assert "start" in actions


def test_host_blocks_localhost():
    assert _host_allowed("http://127.0.0.1/") is not None
    assert _host_allowed("https://example.com/path") is None
    assert isolated_host_allowed("http://127.0.0.1/") is not None


def test_default_mode_is_playwright(monkeypatch):
    monkeypatch.delenv("COMPUTER_USE_MODE", raising=False)
    assert computer_use_mode() == "playwright"
    monkeypatch.setenv("COMPUTER_USE_MODE", "isolated")
    assert computer_use_mode() == "isolated"


def test_isolated_status_reports_mode():
    st = isolated_status()
    assert st["ok"] is True
    assert st["mode"] == "isolated-docker"
    assert "Batch3" in st["source"]


def test_run_python_ok():
    result = run_python_sandbox("print(2 + 2)")
    assert result["ok"] is True
    assert "4" in result["stdout"]


def test_run_python_blocks_open():
    result = run_python_sandbox("open('/etc/passwd').read()")
    assert result["ok"] is False
    assert "blocked" in result["error"]


@pytest.mark.asyncio
async def test_handle_run_python_action():
    result = await handle_computer_use({"action": "run_python", "code": "print('hi')" })
    assert result["ok"] is True
    assert "hi" in result["stdout"]


@pytest.mark.asyncio
async def test_navigate_blocked_host():
    result = await handle_computer_use({"action": "navigate", "url": "http://localhost:8000"})
    assert result["ok"] is False


@pytest.mark.asyncio
async def test_status_playwright_mode(monkeypatch):
    monkeypatch.setenv("COMPUTER_USE_MODE", "playwright")
    result = await handle_computer_use({"action": "status"})
    assert result["ok"] is True
    assert result["mode"] == "playwright"
