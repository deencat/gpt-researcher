"""Tool schema for Hexsenses computer use (browser lab).

Modeled on Hermes `computer_use` / browser tools and Cinebot's planned
Playwright web automation — but Linux-VPS friendly (no macOS cua-driver).
"""

from __future__ import annotations

from typing import Any, Dict

COMPUTER_USE_SCHEMA: Dict[str, Any] = {
    "name": "computer_use",
    "description": (
        "Drive a headless browser lab to answer research questions that need "
        "interactive web steps or small computations: open pages, read an "
        "accessibility snapshot, click/type by element ref, extract text, "
        "take screenshots, or run short Python in a sandbox. Prefer "
        "action='snapshot' then click(ref='eN') over guessing coordinates."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
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
