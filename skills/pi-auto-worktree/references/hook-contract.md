# Claude Code worktree 相关 hook 契约

来源：https://code.claude.com/docs/en/hooks.md 、https://code.claude.com/docs/en/worktrees.md（2026-09 查阅）。

## SessionStart

- matcher 取值：`startup` / `resume` / `clear` / `compact`。本 skill 只挂 `startup`，所以 `--continue` / `--resume` 不触发。
- stdin JSON 含 `cwd`、`session_id`、`hook_event_name` 等。
- 向模型注入上下文的返回格式：

```json
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"..."}}
```

## WorktreeCreate（仅非 git 目录时被 EnterWorktree / --worktree 调用）

- 不支持 matcher，只支持 `type: command`。
- stdin JSON：`name`（worktree 标识，非路径）、`cwd`、`session_id`、`hook_event_name`。
- 返回：**stdout 最后一行非空内容 = 新工作区绝对路径**；其余输出必须走 stderr。退出码非 0 视为创建失败。

## WorktreeRemove

- stdin JSON：`worktree_path`（即 WorktreeCreate 返回的路径）、`cwd`。
- 无决策权，不需要返回内容；失败只在 debug 模式记录。

## EnterWorktree 工具（模型侧）

- `name` 模式：cwd 必须是 git 仓库（或已配 WorktreeCreate hook）；创建在 `<repo>/.claude/worktrees/<name>`，退出会话时 harness 询问 keep/remove。
- `path` 模式：进入一个已在 `git worktree list` 里的 worktree；首次从启动目录进入时允许指向嵌套子仓库（多仓库工作区）。harness 会要求用户确认一次，且退出时不会自动清理。
- `worktree.baseRef` setting：`fresh`（默认，基于 `origin/<默认分支>`）或 `head`（基于本地 HEAD）。
