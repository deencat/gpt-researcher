"""Unit tests for computer_use (no live browser required)."""

from __future__ import annotations

import pytest

from gpt_researcher.computer_use.actions import run_python_sandbox, handle_computer_use
from gpt_researcher.computer_use.schema import get_computer_use_schema
from gpt_researcher.computer_use.session import _host_allowed


def test_schema_has_core_actions():
    schema = get_computer_use_schema()
    assert schema["name"] == "computer_use"
    actions = schema["parameters"]["properties"]["action"]["enum"]
    assert "navigate" in actions
    assert "snapshot" in actions
    assert "run_python" in actions


def test_host_blocks_localhost():
    assert _host_allowed("http://127.0.0.1/") is not None
    assert _host_allowed("https://example.com/path") is None


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
