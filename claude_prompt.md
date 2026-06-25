# Claude Code + RelayOS Integration Guide

## Setup

### 1. Install

```bash
pip install relayos-mcp
```

### 2. Configure Claude Code

Add to your `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "relayos": {
      "command": "relayos-mcp",
      "args": []
    }
  }
}
```

Or in project `.claude/settings.json`:

```json
{
  "mcpServers": {
    "relayos": {
      "command": "relayos-mcp",
      "args": []
    }
  }
}
```

### 3. Verify

Run `relay-task list-agents` — you should see available agents:

```
Agent           Available  Path
local           ✅         
mimo            ✅         /usr/local/bin/mimo
opencode        ❌         
claude          ✅         /usr/local/bin/claude
```

## How to ask Claude to use RelayOS

Add this to your project's CLAUDE.md or project instructions:

```
You can delegate tasks to RelayOS agents for efficiency:

- @relay run <command> — Run a shell command (testing, linting, building)
- @relay run-task <json> — Multi-step task with agent orchestration
- @relay list-agents — See available agents

Good candidates for delegation:
- Running tests, linters, type checkers
- File operations, refactoring, code generation
- API calls, data fetching, batch processing
- Deployments, CI/CD operations

Keep Claude for:
- Complex architectural decisions
- Code review and security analysis
- Debugging complex issues
- System design and planning
```

## Example Workflow

1. User: "Review this PR, run tests, and generate a report"
2. Claude: Analyzes the PR (~2k tokens)
3. Claude: `@relay run "pytest --cov -v"` ← delegated to local agent (free)
4. Local agent: Runs tests, returns results (~0 tokens for Claude)
5. Claude: `@relay run "python -m bandit -r src/"` ← security scan (free)
6. Local agent: Runs bandit, returns results
7. Claude: Synthesizes final report (~1k tokens)

Total Claude token usage: ~3k tokens (vs ~10k+ without relay)
