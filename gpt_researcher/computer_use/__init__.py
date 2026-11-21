"""Hexsenses computer use — Playwright lab + Batch3 isolated Docker desktop.

Modes via ``COMPUTER_USE_MODE``:

* ``playwright`` — headless Chromium on the host
* ``isolated`` — Batch3 ``isolated_computer`` pattern (XFCE+Chromium+noVNC)

Also inspired by Hermes browser tools and Cinebot's Playwright plan.
"""

from .actions import handle_computer_use, handle_computer_use_sync, result_as_text
from .schema import COMPUTER_USE_SCHEMA, get_computer_use_schema

__all__ = [
    "COMPUTER_USE_SCHEMA",
    "get_computer_use_schema",
    "handle_computer_use",
    "handle_computer_use_sync",
    "result_as_text",
]
