"""Hexsenses computer use — Playwright browser lab + optional Python sandbox.

Inspired by Hermes computer_use / browser tools and Cinebot's Playwright plan.
Linux-VPS friendly (no macOS cua-driver).
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
