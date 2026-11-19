"""Tool schema for Hexsenses computer use (browser lab + isolated desktop).

Modeled on Batch3 ``isolated_computer`` (Docker XFCE+Chromium+noVNC), Hermes
browser tools, and Cinebot's Playwright plan — Linux-VPS friendly.
"""

from __future__ import annotations

from typing import Any, Dict

COMPUTER_USE_SCHEMA: Dict[str, Any] = {
    "name": "computer_use",
    "description": (
        "Drive a browser lab (headless Playwright, or Batch3-style isolated "
        "Docker desktop when COMPUTER_USE_MODE=isolated) for research that "
        "needs interactive web steps or small computations: open pages, "
        "accessibility snapshot, click/type by element ref, extract text, "
        "screenshots, or short sandboxed Python. Prefer action='snapshot' "
        "then click(ref='eN') over guessing coordinates. Use status/start "
        "with isolated mode to manage the Docker desktop."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "status",
                    "start",
                    "navigate",
                    "snapshot",
                    "click",
                    "type",
                    "scroll",
                    "extract",
                    "screenshot",
                    "run_python",
                    "close",
                ],
                "description": "Which computer-use action to perform.",
            },
            "url": {
                "type": "string",
                "description": "For navigate: absolute http(s) URL.",
            },
            "ref": {
                "type": "string",
                "description": "Element ref from snapshot, e.g. e3 or @e3.",
            },
            "text": {
                "type": "string",
                "description": "For type: text to enter into the focused/ref element.",
            },
            "direction": {
                "type": "string",
                "enum": ["up", "down"],
                "description": "For scroll.",
            },
            "amount": {
                "type": "integer",
                "description": "For scroll: pixel amount (default 600).",
            },
            "selector": {
                "type": "string",
                "description": "Optional CSS selector for extract.",
            },
            "code": {
                "type": "string",
                "description": "For run_python: short Python script (stdout is returned).",
            },
            "x": {
                "type": "integer",
                "description": "For click without ref (isolated mode): desktop X.",
            },
            "y": {
                "type": "integer",
                "description": "For click without ref (isolated mode): desktop Y.",
            },
            "session_id": {
                "type": "string",
                "description": "Optional session id to reuse the same browser tab.",
            },
        },
        "required": ["action"],
    },
}


def get_computer_use_schema() -> Dict[str, Any]:
    return COMPUTER_USE_SCHEMA
