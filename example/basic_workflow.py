"""Example: basic workflow with RelayOS MCP."""

import json

from relayos_mcp.executor import TaskExecutor


def main():
    """Demo: scan project and run tests using local agent."""
    executor = TaskExecutor()

    print("=== Available Agents ===")
    for agent in executor.detect_agents():
        mark = "✅" if agent["available"] else "❌"
        print(f"  {mark} {agent['name']}")

    print("\n=== Running: list files ===")
    results = executor.execute({
        "description": "List project structure",
        "actions": [
            {"agent": "local", "command": "ls -la", "timeout": 10},
        ],
    })
    for r in results:
        print(f"  [{r.agent}] {r.duration_ms}ms")
        if r.output:
            print(f"  {r.output[:300]}")

    print("\n=== Multi-step task: check system ===")
    results = executor.execute({
        "description": "System check",
        "actions": [
            {"agent": "local", "command": "python --version", "timeout": 10},
            {"agent": "local", "command": "pip list 2>/dev/null | head -5", "timeout": 10},
        ],
    })
    for r in results:
        status = "✅" if r.success else "❌"
        print(f"  {status} Step {r.action_index+1} [{r.agent}] {r.duration_ms}ms")
        if r.output:
            print(f"    {r.output[:200]}")


if __name__ == "__main__":
    main()
