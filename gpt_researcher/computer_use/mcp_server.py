"""MCP stdio server exposing Hexsenses computer_use.

Run: ``python -m gpt_researcher.computer_use``

Wire as an MCP preset in the research UI (see frontend MCP_PRESETS).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .actions import handle_computer_use, result_as_text
from .schema import COMPUTER_USE_SCHEMA

logger = logging.getLogger(__name__)


def _tool_schema() -> dict:
    # MCP tools/list shape (JSON Schema under inputSchema).
    return {
        "name": COMPUTER_USE_SCHEMA["name"],
        "description": COMPUTER_USE_SCHEMA["description"],
        "inputSchema": {
            "type": "object",
            "properties": COMPUTER_USE_SCHEMA["parameters"]["properties"],
            "required": COMPUTER_USE_SCHEMA["parameters"]["required"],
        },
    }


async def run_mcp_server() -> None:
    """Start an MCP server over stdio."""
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    server = Server("gptr-computer-use")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        schema = _tool_schema()
        return [
            Tool(
                name=schema["name"],
                description=schema["description"],
                inputSchema=schema["inputSchema"],
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None):
        if name != "computer_use":
            return [TextContent(type="text", text=json.dumps({"ok": False, "error": f"unknown tool {name}"}))]
        result = await handle_computer_use(arguments or {})
        return [TextContent(type="text", text=result_as_text(result))]

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_mcp_server())
