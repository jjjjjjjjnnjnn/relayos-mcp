"""Task and result data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class TaskAction:
    """A single action within a task."""
    agent: str  # "mimo" | "claude" | "local" | "gpt4" | etc.
    command: str
    timeout: int = 120
    retry: int = 1
    input: str = ""
    env: dict[str, str] = field(default_factory=dict)


@dataclass
class TaskDef:
    """A complete task definition."""
    id: str
    description: str
    actions: list[TaskAction]
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of executing a task action."""
    task_id: str
    action_index: int
    agent: str
    success: bool
    output: str = ""
    error: str = ""
    duration_ms: int = 0
    retries: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# JSON Schema for task definition
TASK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "RelayOS Task",
    "description": "A task to be executed by RelayOS agents",
    "type": "object",
    "required": ["actions"],
    "properties": {
        "description": {"type": "string"},
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["agent", "command"],
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Agent to execute this action",
                        "enum": ["mimo", "claude", "opencode", "local", "gpt4", "gemini"],
                    },
                    "command": {
                        "type": "string",
                        "description": "Shell command or agent instruction",
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 120,
                        "description": "Timeout in seconds",
                    },
                    "retry": {
                        "type": "integer",
                        "default": 1,
                        "description": "Number of retries on failure",
                    },
                    "input": {
                        "type": "string",
                        "description": "Input data for the action",
                    },
                },
            },
        },
        "context": {
            "type": "object",
            "properties": {
                "cwd": {"type": "string"},
                "env": {"type": "object"},
            },
        },
    },
}


def validate_task(task: dict) -> tuple[bool, str]:
    """Validate a task dict against the schema."""
    if not isinstance(task, dict):
        return False, "Task must be a dict"
    if "actions" not in task or not isinstance(task["actions"], list):
        return False, "Task must contain an 'actions' list"
    if not task["actions"]:
        return False, "Task must have at least one action"
    for i, action in enumerate(task["actions"]):
        if not isinstance(action, dict):
            return False, f"Action {i}: must be a dict"
        if "agent" not in action:
            return False, f"Action {i}: missing 'agent'"
        if "command" not in action:
            return False, f"Action {i}: missing 'command'"
    return True, "OK"
