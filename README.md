# RelayOS MCP

**Turn Claude Code into an AI team lead.**

Claude handles complex decisions, code review, and architecture.  
RelayOS agents (mimo, opencode, local tools) execute the grunt work.  
Free models do the heavy lifting, Claude does the thinking.

## Install

```bash
pip install relayos-mcp
```

## Usage

### Option 1: CLI commands

```bash
# List available agents
relay-task list-agents

# Run a local command via relay
relay-task run "pytest tests/ -v"

# Execute a multi-step task
relay-task run-task '{
  "description": "Test and lint",
  "actions": [
    {"agent": "local", "command": "pytest tests/ -v"},
    {"agent": "mimo", "command": "Review the output"}
  ]
}'
```

### Option 2: MCP Server (Claude Code integration)

Configure Claude Code to use the RelayOS MCP server:

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

Then in Claude Code you can use:
- `relay_execute` — Run a command via any agent
- `relay_run_task` — Multi-step task with multiple agents
- `relay_list_agents` — See available agents

### Option 3: @relay commands (Claude Code prompt)

Add this to your Claude Code project instructions:

```
You can delegate tasks to RelayOS agents:
- @relay run <command> — Run a shell command via local agent
- @relay run-task <json> — Multi-step task with agent orchestration
- @relay list-agents — See available agents
- @relay status <task-id> — Check task progress

Use relay for: testing, linting, file operations, API calls, deployments.
Keep Claude for: complex decisions, code review, architecture, debugging.
```

## Architecture

```
Claude Code (decisions, review, architecture)
    │
    ├── MCP tools: relay_execute / relay_run_task / relay_list_agents
    │
    ▼
RelayOS MCP Server
    │
    ├── local agent — run shell commands
    ├── mimo agent — AI-powered task execution
    ├── opencode agent — code-aware CLI tasks
    └── claude agent — complex Claude-powered work
```

## Development

```bash
# Install in dev mode
pip install -e ".[mcp]"

# Run tests
pytest tests/
```
