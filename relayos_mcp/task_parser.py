"""Parse @relay commands from Claude Code responses."""

from __future__ import annotations

import json
import re
from typing import Optional

from relayos_mcp.schema import TASK_SCHEMA, validate_task


def parse_relay_command(text: str) -> Optional[dict]:
    """Parse a @relay command from Claude Code output.

    Supports:
        @relay run <command>              → local shell command
        @relay run-task <json>            → full task definition
        @relay list-agents                → list available agents
        @relay status <task-id>           → query task status
    """
    text = text.strip()

    # @relay list-agents
    if re.match(r'^@relay\s+list-agents\s*$', text, re.IGNORECASE):
        return {"action": "list-agents"}

    # @relay status <id>
    m = re.match(r'^@relay\s+status\s+(\S+)\s*$', text, re.IGNORECASE)
    if m:
        return {"action": "status", "task_id": m.group(1)}

    # @relay run <command>
    m = re.match(r'^@relay\s+run\s+(.+)$', text, re.IGNORECASE)
    if m:
        return {
            "action": "run-task",
            "task": {
                "description": f"Run: {m.group(1)}",
                "actions": [{"agent": "local", "command": m.group(1)}],
            },
        }

    # @relay run-task <json>
    m = re.match(r'^@relay\s+run-task\s+(.+)$', text, re.IGNORECASE)
    if m:
        try:
            task = json.loads(m.group(1))
            valid, msg = validate_task(task)
            if valid:
                return {"action": "run-task", "task": task}
            return {"action": "error", "message": f"Invalid task: {msg}"}
        except json.JSONDecodeError as e:
            return {"action": "error", "message": f"Invalid JSON: {e}"}

    return None


def format_task_as_prompt(task: dict) -> str:
    """Format a task definition as a human-readable prompt for Claude."""
    lines = ["RelayOS Task:", f"  Description: {task.get('description', '(unnamed)')}"]
    for i, action in enumerate(task.get("actions", [])):
        lines.append(f"  Step {i+1}: [{action.get('agent','?')}] {action.get('command','')}")
    return "\n".join(lines)
