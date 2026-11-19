"""Dispatch computer_use actions (browser + optional sandboxed Python)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, Optional

from .session import close_session, get_session

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = int(os.getenv("COMPUTER_USE_PYTHON_TIMEOUT", "20"))
_MAX_CODE_CHARS = 8_000
_BLOCKED_CODE = [
    re.compile(r"\bos\.system\b"),
    re.compile(r"\bsubprocess\b"),
    re.compile(r"\b__import__\s*\(\s*['\"]os['\"]"),
    re.compile(r"\bopen\s*\("),
    re.compile(r"\bsocket\b"),
    re.compile(r"\bshutil\b"),
    re.compile(r"\bpathlib\b"),
]


def _blocked_python(code: str) -> Optional[str]:
    for pat in _BLOCKED_CODE:
        if pat.search(code):
            return f"blocked pattern: {pat.pattern}"
    return None


def run_python_sandbox(code: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """Run short Python in a scrubbed subprocess (no network helpers)."""
    if not code or not code.strip():
        return {"ok": False, "error": "empty code"}
    if len(code) > _MAX_CODE_CHARS:
        return {"ok": False, "error": f"code exceeds {_MAX_CODE_CHARS} chars"}
    bad = _blocked_python(code)
    if bad:
        return {"ok": False, "error": bad}

    timeout = timeout or _DEFAULT_TIMEOUT
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": tempfile.gettempdir(),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    with tempfile.TemporaryDirectory(prefix="gptr-cu-") as tmp:
        script = os.path.join(tmp, "snippet.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            proc = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmp,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"timeout after {timeout}s"}
        stdout = (proc.stdout or "")[:50_000]
        stderr = (proc.stderr or "")[:10_000]
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": stdout,
            "stderr": stderr,
        }


async def handle_computer_use(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute one computer_use action and return a JSON-serializable result."""
    action = (args.get("action") or "").strip()
    session_id = (args.get("session_id") or "default").strip() or "default"

    if not action:
        return {"ok": False, "error": "action is required"}

    try:
        if action == "run_python":
            return run_python_sandbox(args.get("code") or "")

        if action == "close":
            await close_session(session_id)
            return {"ok": True, "closed": session_id}

        sess = await get_session(session_id)

        if action == "navigate":
            url = args.get("url") or ""
            return await sess.navigate(url)
        if action == "snapshot":
            return await sess.snapshot()
        if action == "click":
            return await sess.click(args.get("ref") or "")
        if action == "type":
            return await sess.type_text(args.get("ref") or "", args.get("text") or "")
        if action == "scroll":
            return await sess.scroll(
                direction=args.get("direction") or "down",
                amount=int(args.get("amount") or 600),
            )
        if action == "extract":
            return await sess.extract(args.get("selector"))
        if action == "screenshot":
            return await sess.screenshot()

        return {"ok": False, "error": f"unknown action: {action}"}
    except Exception as e:
        logger.exception("computer_use %s failed", action)
        return {"ok": False, "error": str(e), "action": action}


def handle_computer_use_sync(args: Dict[str, Any]) -> Dict[str, Any]:
    """Sync wrapper for chat / MCP callers."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Nested loop (e.g. already in async): run in a thread.
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(lambda: asyncio.run(handle_computer_use(args))).result(
                    timeout=120
                )
        return loop.run_until_complete(handle_computer_use(args))
    except RuntimeError:
        return asyncio.run(handle_computer_use(args))


def result_as_text(result: Dict[str, Any]) -> str:
    """Compact text for LLM tool messages (omit huge base64 by default)."""
    payload = dict(result)
    if "image_base64" in payload:
        payload["image_base64"] = f"<omitted {payload.get('bytes', 0)} bytes png>"
    return json.dumps(payload, ensure_ascii=False, indent=2)
