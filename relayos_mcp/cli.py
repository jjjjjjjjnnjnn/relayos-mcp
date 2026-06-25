"""CLI — direct calls without MCP server."""

from __future__ import annotations

import sys
import shutil
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  relay-task ask <agent> <prompt>    Ask an AI agent")
        print("  relay-task run <command>           Run a shell command")
        print("  relay-task agents                  List available agents")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "agents":
        for name in ["mimo", "opencode", "claude", "codex"]:
            path = shutil.which(name)
            mark = "[ok]" if path else "[..]"
            print(f"{mark} {name:<12} {path or 'not found'}")
        return

    if cmd == "ask":
        if len(sys.argv) < 4:
            print("Usage: relay-task ask <agent> <prompt>")
            sys.exit(1)
        agent = sys.argv[2]
        prompt = " ".join(sys.argv[3:])
        binary = shutil.which(agent)
        if not binary:
            print(f"Error: '{agent}' not found in PATH", file=sys.stderr)
            sys.exit(1)
        import subprocess as sp
        result = sp.run([binary], input=prompt, capture_output=True, text=True,
                        timeout=120, shell=(__import__('sys').platform == "win32"))
        out = (result.stdout or "").strip() or (result.stderr or "").strip()
        print(out)
        sys.exit(result.returncode)

    if cmd == "run":
        command = " ".join(sys.argv[2:])
        import subprocess as sp
        result = sp.run(command, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        out = (result.stdout or "").strip() or (result.stderr or "").strip() or f"(exit {result.returncode})"
        print(out[:2000])
        sys.exit(result.returncode)

    print(f"Unknown command: {cmd}")
    sys.exit(1)


if __name__ == "__main__":
    main()
