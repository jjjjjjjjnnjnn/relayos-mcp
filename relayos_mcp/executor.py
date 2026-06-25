"""Task execution engine — runs actions via RelayOS CLI providers."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import time
import uuid
from typing import Optional

from relayos_mcp.schema import TaskAction, TaskDef, TaskResult, validate_task

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Execute task actions through available CLI agents."""

    def __init__(self):
        self._results: list[TaskResult] = []

    def detect_agents(self) -> list[dict]:
        """Detect available CLI agents on this system."""
        agents = []
        for binary_name in ["mimo", "opencode", "claude", "codex"]:
            path = shutil.which(binary_name)
            agents.append({
                "name": binary_name,
                "available": path is not None,
                "path": path or "",
                "type": "cli",
            })
        # Always include "local" (runs commands directly)
        agents.insert(0, {"name": "local", "available": True, "path": "", "type": "local"})
        return agents

    def execute(self, task: dict) -> list[TaskResult]:
        """Execute a task dict and return results for each action."""
        valid, msg = validate_task(task)
        if not valid:
            return [TaskResult(
                task_id="validation-error",
                action_index=0, agent="system",
                success=False, error=msg,
            )]

        task_id = task.get("id", f"task-{uuid.uuid4().hex[:8]}")
        results = []

        for i, action_def in enumerate(task["actions"]):
            action = TaskAction(**{k: v for k, v in action_def.items() if k in
                                    ["agent", "command", "timeout", "retry", "input", "env"]})
            result = self._run_action(task_id, i, action)
            results.append(result)

        self._results.extend(results)
        return results

    def _run_action(self, task_id: str, index: int, action: TaskAction) -> TaskResult:
        """Run a single action, with retries."""
        last_error = ""
        for attempt in range(max(1, action.retry)):
            start = time.time()
            try:
                output, error, success = self._invoke(action)
                duration = int((time.time() - start) * 1000)
                return TaskResult(
                    task_id=task_id, action_index=index,
                    agent=action.agent, success=success,
                    output=output, error=error,
                    duration_ms=duration, retries=attempt,
                )
            except Exception as e:
                last_error = str(e)
                time.sleep(1)  # Backoff before retry

        return TaskResult(
            task_id=task_id, action_index=index,
            agent=action.agent, success=False,
            error=f"Failed after {action.retry} retries: {last_error}",
        )

    def _invoke(self, action: TaskAction) -> tuple[str, str, bool]:
        """Invoke the action on the specified agent."""
        if action.agent == "local":
            return self._run_local(action)
        else:
            return self._run_cli(action)

    def _run_local(self, action: TaskAction) -> tuple[str, str, bool]:
        """Run a command directly on the local shell."""
        try:
            result = subprocess.run(
                action.command, shell=True,
                capture_output=True, text=True,
                timeout=action.timeout,
                cwd=action.env.get("cwd"),
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            success = result.returncode == 0
            return stdout, stderr if not success else "", success
        except subprocess.TimeoutExpired:
            return "", f"Command timed out after {action.timeout}s", False
        except Exception as e:
            return "", str(e), False

    def _run_cli(self, action: TaskAction) -> tuple[str, str, bool]:
        """Run via a CLI tool (mimo, opencode, claude)."""
        binary = shutil.which(action.agent)
        if not binary:
            return "", f"CLI '{action.agent}' not found in PATH", False

        # Pipe the command as a prompt via stdin (works for all CLI tools)
        prompt = action.input or action.command
        try:
            result = subprocess.run(
                [binary], input=prompt,
                capture_output=True, text=True,
                timeout=action.timeout,
                shell=sys.platform == "win32",
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            success = result.returncode == 0
            return stdout, stderr if not success else "", success
        except subprocess.TimeoutExpired:
            return "", f"CLI '{action.agent}' timed out after {action.timeout}s", False
        except Exception as e:
            return "", str(e), False

    def last_results(self) -> list[TaskResult]:
        """Get results from the last execution."""
        return list(self._results)
