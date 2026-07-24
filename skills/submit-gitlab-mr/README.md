# 🔀 submit-gitlab-mr

> 一条命令完成 preflight + 冲突检查 + push + MR upsert,只卡 Git 冲突。

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `Codex`(通过 `agents/openai.yaml`) |
| **最近更新** | `2026-07-24` |

## Why

提 GitLab MR 的标准动作(preflight、fetch、冲突检查、push、upsert)被一个本地 skill 收口,只把 **Git 冲突** 当作唯一 gate,代码审查 / CI / lint / typecheck 全部留给项目自己的流程管。这样:

- 不重复跑项目已有的 CI(用 `git push --no-verify`)
- 不替你审查代码(只检查能否 merge)
- 不动你未提交的工作(从不 stash / clean / discard)

结果:提一个 MR 从几分钟压到 1 条命令,且安全边界清晰。

## Features

- **冲突检查** — 用 `git merge-tree --write-tree` 在不动 worktree 的前提下探测 conflict,exit code 即结论
- **幂等 upsert** — `upsert_mr.py` 自动判断新建还是更新同名 MR,重跑安全
- **保留 SSH** — 全部走 `git push` 而非 `glab mr create`,沿用你已有的 SSH/HTTPS 凭据
- **可回滚** — 默认不删源分支、不自动 merge;draft-only 模式只生成文案不推送
- **轻 gate** — 跳过 CI/lint/审查,只做 Git 层校验,与 `code-self-review` / CI 解耦

## Quickstart

```bash
# 1. 软链到 Claude Code(Codex 用户改 ~/.codex/skills)
ln -s $(pwd)/skills/submit-gitlab-mr ~/.claude/skills/submit-gitlab-mr

# 2. 前置:安装并登录 glab(只用来发 MR API,推送仍走 git)
brew install glab                       # 见 https://gitlab.com/gitlab-org/cli
glab auth login                         # 任何 GitLab 实例:自建或官方都行

# 3. 在 GitLab 仓库工作分支上触发(任选一句自然语言)
"帮我提个 MR"
"提交当前分支的 merge request"
"把这个分支推到 GitLab 并开 MR"
```

## Usage

提 MR 的标准流程(skill 内部 7 步):

1. **preflight** — `scripts/preflight.py` 推断 target(从 `dev` / `main` / `master` 中选 HEAD 距离 merge-base 最近者,平票优先包含他人的)
2. **fetch** — 一次定向 `git fetch origin refs/heads/<target>:...`
3. **conflict check** — `git merge-tree --write-tree`,exit `0` 继续 / `1` 报冲突路径并停
4. **behind 检查** — `HEAD..origin/<target>` 落后则报数,只问一次 merge / rebase / cancel
5. **文案** — 仓库里有 MR 模板就套模板,否则写简洁 title + description
6. **push** — `git push --no-verify -u origin <source>`,非快进直接停
7. **upsert MR** — `scripts/upsert_mr.py` 用临时 UTF-8 文件传 title/description,跑完清理,返回 MR URL + source/target/conflict 结果

**示例对话**

```text
> 我在 feat/skill-market-mvp-discovery 分支,帮我提个 MR 到 dev
[skill] preflight → target=dev, behind=0, conflict=none
[skill] push ok
[skill] MR upsert: https://gitlab.example.com/your-group/your-repo/-/merge_requests/1
```

**Draft-only 模式**:只产出 title/description,不 push 不建 MR,适合先在 IDE 改完再提。

## 前置依赖

- **`glab` CLI** — GitLab 官方命令行,只用来 `mr create/update` API
  ```bash
  brew install glab
  # 或: https://gitlab.com/gitlab-org/cli
  ```
- **`glab auth login`** — 登录任意 GitLab 实例(self-hosted / gitlab.com 都行)
- **Git + 已配置远端 SSH/HTTPS 凭据** — push 走 `git`,不依赖 glab
- **工作树干净或接受 uncommitted 变更不会被 stash** — skill 不会动你的未提交改动

## License

MIT
