# 🔀 submit-gitlab-mr

> 冲突检查 + 快速提交 GitLab MR

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `Codex` |
| **最近更新** | `2026-07-24` |

**一句话:**一条命令完成 preflight + 冲突检查 + push + MR upsert,只卡 Git 冲突这一个 gate,不做代码审查/CI。

---

## 前置依赖

- **glab CLI**(GitLab 官方命令行):`brew install glab` 或见 https://gitlab.com/gitlab-org/cli
- **登录**:`glab auth login`(任何 GitLab 实例均可:自建或官方)

## 快速开始

```bash
# 1. 激活
ln -s $(pwd)/skills/submit-gitlab-mr ~/.claude/skills/submit-gitlab-mr

# 2. 触发(在当前 GitLab 仓库的工作分支上)
"帮我提个 MR"
"提交当前分支的 merge request"
```

## 脚本

- `scripts/preflight.py` -- 推断 target 分支(dev/main/master 中 HEAD 到 merge-base 最近者)
- `scripts/upsert_mr.py` -- push + 创建/更新 MR(幂等 upsert)
- `agents/openai.yaml` -- Codex 端接口配置(可选,不影响 Claude Code/Codex 使用)

skill 只负责 Git 冲突检查这一个 gate;代码审查、CI、lint 由其他流程负责。
