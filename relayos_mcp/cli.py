"""RelayOS MCP CLI — direct task execution without MCP."""

from __future__ import annotations

import json
import sys

from relayos_mcp.executor import TaskExecutor
from relayos_mcp.task_parser import parse_relay_command


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: relay-task <command> [args]")
        print("  relay-task list-agents")
        print('  relay-task run "pytest -v"')
        print('  relay-task run-task \'{"actions": [...]}\'')
        sys.exit(1)

    executor = TaskExecutor()
    cmd = sys.argv[1]

    if cmd == "list-agents":
        agents = executor.detect_agents()
        print(f"{'Agent':<15} {'Available':<10} Path")
        print("-" * 50)
        for a in agents:
            mark = "✅" if a["available"] else "❌"
            print(f"{a['name']:<15} {mark:<10} {a['path']}")
        return

    if cmd == "run":
        command = " ".join(sys.argv[2:])
        if not command:
            print("Usage: relay-task run <command>")
            sys.exit(1)
        results = executor.execute({"actions": [{"agent": "local", "command": command}]})
        for r in results:
            if r.success:
                print(r.output)
            else:
                print(f"Error: {r.error}", file=sys.stderr)
                sys.exit(1)
        return

    if cmd == "run-task":
        task_json = " ".join(sys.argv[2:])
        if not task_json.startswith("{"):
            # Read from stdin
            task_json = sys.stdin.read()
        try:
            task = json.loads(task_json)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
        results = executor.execute(task)
        for r in results:
            status = "✅" if r.success else "❌"
            print(f"{status} [{r.agent}] {r.duration_ms}ms")
            if r.output:
                print(f"   Output: {r.output[:200]}")
            if r.error:
                print(f"   Error: {r.error[:200]}", file=sys.stderr)
        if not all(r.success for r in results):
            sys.exit(1)
        return

    if cmd == "status":
        print("Status: not implemented yet")
        return

    print(f"Unknown command: {cmd}")
    sys.exit(1)


if __name__ == "__main__":
    main()
