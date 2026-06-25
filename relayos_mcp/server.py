"""Minimal MCP server — Claude Code calls relay agents as tools.

How it works:
1. Start:  relayos-mcp
2. Claude Code connects via stdio MCP transport
3. Claude Code calls tools like: ask_mimo(), ask_opencode(), run_command()
4. Each tool pipes the prompt to the agent and returns the result
"""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
import subprocess
import sys
import time

logger = logging.getLogger(__name__)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest, ListToolsRequest, Tool, TextContent,
    )
    MCP_OK = True
except ImportError:
    MCP_OK = False


# ── Agent detection ─────────────────────────────────────────────

def detect_agents() -> list[dict]:
    """Detect available CLI agents on PATH."""
    agents = []
    for name in ["mimo", "opencode", "claude", "codex"]:
        path = shutil.which(name)
        agents.append({"name": name, "available": path is not None, "path": path or ""})
    return agents


def ask_agent(agent: str, prompt: str, timeout: int = 120) -> str:
    """Ask a CLI agent a question. Returns the response."""
    binary = shutil.which(agent)
    if not binary:
        return f"[Error] '{agent}' not found in PATH"

    try:
        result = subprocess.run(
            [binary], input=prompt,
            capture_output=True, text=True,
            timeout=timeout, shell=(sys.platform == "win32"),
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if result.returncode != 0 and not stdout:
            return f"[Error] {stderr[:500]}"
        return stdout or stderr[:500]
    except subprocess.TimeoutExpired:
        return f"[Error] '{agent}' timed out after {timeout}s"
    except Exception as e:
        return f"[Error] {e}"


def run_command(command: str, timeout: int = 120) -> str:
    """Run a shell command. Returns stdout + stderr."""
    try:
        result = subprocess.run(
            command, shell=True,
            capture_output=True, text=True, timeout=timeout,
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if result.returncode != 0:
            return f"[Exit {result.returncode}]\n{out}\n{err}"[:2000]
        return out[:2000] or "(no output)"
    except subprocess.TimeoutExpired:
        return f"[Error] Command timed out after {timeout}s"
    except Exception as e:
        return f"[Error] {e}"


# ── MCP Server ─────────────────────────────────────────────────

def create_server() -> Server:
    """Create the MCP server with tool handlers."""
    if not MCP_OK:
        print("Error: mcp package not installed. Run: pip install mcp")
        sys.exit(1)

    app = Server("relayos-mcp")

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        agents = detect_agents()
        tools = [
            Tool(
                name="run_command",
                description="Execute a shell command on the local machine",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to run"},
                        "timeout": {"type": "integer", "default": 120},
                    },
                    "required": ["command"],
                },
            ),
        ]
        # Add one tool per available agent
        for a in agents:
            if a["available"]:
                tools.append(Tool(
                    name=f"ask_{a['name']}",
                    description=f"Ask {a['name']} AI agent to do a task. Free/cheap model — use for grunt work.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The task or question for the agent"},
                            "timeout": {"type": "integer", "default": 120},
                        },
                        "required": ["prompt"],
                    },
                ))
        return tools

    @app.call_tool()
    async def call_tool(req: CallToolRequest) -> list[TextContent]:
        name = req.params.name
        args = req.params.arguments or {}

        if name == "run_command":
            cmd = args.get("command", "")
            timeout = args.get("timeout", 120)
            result = run_command(cmd, timeout)
            return [TextContent(type="text", text=result)]

        # ask_<agent> tools
        for a in detect_agents():
            if name == f"ask_{a['name']}":
                prompt = args.get("prompt", "")
                timeout = args.get("timeout", 120)
                result = ask_agent(a["name"], prompt, timeout)
                return [TextContent(type="text", text=result)]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return app


def main():
    """Entry point: start MCP server over stdio."""
    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    app = create_server()
    asyncio.run(stdio_server(app))


if __name__ == "__main__":
    main()
