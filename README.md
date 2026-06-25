# relayos-mcp

**Claude Code 即 AI 团队指挥。** 你说需求，我规划分工，免费终端干重活。

## 一句话

```
你 -> Claude Code(我) -> MCP tools -> mimo / opencode / 本地命令
                    |
              我负责计划、分配、审核
              免费模型负责执行
              花最少的钱,干最高质量的活
```

## 安装

```bash
pip install relayos-mcp[mcp]
```

## 验证

```bash
relay-task agents
```

应该看到 `[ok] mimo`、`[ok] opencode`、`[ok] claude` 等。

## 配置 Claude Code

在 `~/.claude/settings.json` 中添加：

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

重启后我就能调用这些工具：

| 工具 | 用途 | 成本 |
|------|------|------|
| `run_command` | 执行 Shell 命令 | 免费 |
| `ask_mimo` | 问 Mimo AI | 免费 |
| `ask_opencode` | 问 OpenCode AI | 免费 |
| `ask_claude` | 问 Claude (如果装了) | 收费 |

## 工作流程

```
你: "审查这个 PR，跑测试，修 bug"
 |
我: 分析 PR -> 发现需要:
    |- ask_mimo("审查 security 问题")     <- 免费
    |- run_command("pytest tests/")      <- 免费
    |- 我自己修 bug + 代码 review         <- Claude 负责
 |
你: 收到最终报告
```

## 原则

- **省钱**：单调工作让免费模型做，Claude 只做决策和审核
- **省时**：并行派活，不用等我一个个做完
- **质量**：我负责规划分工和质量把关
