# 42Marketplace Skills 上传设计

- 日期:2026-07-24
- 作者:Kris
- 状态:已确认,待实现

## 背景

`Coder42Y/42Marketplace`(原 KrisVault)是个人开源 skill 集合仓,现有 3 个 skill(daily-pulse / deep-repo-research / vid2report)和 1 个 tool(centos-claude-statusline)。本地另有大量 skills 分散在 `~/.claude/skills/`、`~/.openclaw/workspace/skills/`、`~/.codex/skills/` 等处,需筛选出原创、通用、无公司/个人敏感信息的,脱敏后上传分享。

## 目标

把本地原创、通用、成熟的 skills 按 42Marketplace 开源质量标准(通用、无个人/公司痕迹、文档齐全、能独立运行)整理上传,分 2 个 PR 合入 main。

## 范围

### 纳入(6 个)

| skill | 来源 | 处置 |
|---|---|---|
| design-html | `~/.claude/skills/` | 原样 + 补 README |
| zhihu-notes | `~/.openclaw/workspace/skills/` | 补 README + 示例 |
| elder-blessing-comments | `~/.claude/skills/` | 补 README + 示例 |
| submit-gitlab-mr | `~/.codex/skills/` | 补 README + glab 前置说明(代码已通用) |
| algo-solver | `~/.claude/skills/` | 改硬编码路径为可配置 + README |
| xhs-image-gen | `~/.openclaw/workspace/skills/` | 补依赖说明 + 跑通验证 + README |

### 排除

- **已在其他公开 repo**:`verify-closure` / `attribute-rootcause` / `four-stage-install` -> 已在 `four-gate-ai-workflow`(public)
- **非原创**:Matt Pocock pack ×12、Obsidian 官方配套 ×5、academic-pptx / drawio-skill / find-skills / resume-tailoring、tencent-channel-community(腾讯官方)、shushu-internship-tool(第三方项目)、paper-spine ×12(`WUBING2023/PaperSpine`,非本人)
- **公司耦合**:`code-self-review`(数字员工专用,规范从公司 GitLab 同步)
- **半成品**:`run-smoke-tests`、`caveman`

## 设计

### 目录结构

6 个 skill 放 `skills/<name>/`,与现有并列:

```
42Marketplace/skills/
├── daily-pulse/             (已有)
├── deep-repo-research/      (已有)
├── vid2report/              (已有)
├── design-html/             (PR1)
├── zhihu-notes/             (PR1)
├── elder-blessing-comments/ (PR1)
├── submit-gitlab-mr/        (PR1)
├── algo-solver/             (PR2)
└── xhs-image-gen/           (PR2)
```

### PR 计划

main 分支已有 ruleset(B 档:要求 PR + 禁 force-push + 禁删),所有上传走 branch -> PR -> squash merge。

- **PR1(轻量整理,4 个)**:`design-html` / `zhihu-notes` / `elder-blessing-comments` / `submit-gitlab-mr`。只补 README + 轻量清理,代码基本不动。
- **PR2(需改代码/验证,2 个)**:`algo-solver`(改路径)/ `xhs-image-gen`(验证依赖)。

### 各 skill 清理清单

#### PR1

**design-html**
- 搬入:`SKILL.md`(单文件)
- 清理:无敏感点(grep 零命中)
- README:按 `DESIGN.md` 模板,状态 `stable`,零依赖
- 版本:`v0.1.0`

**zhihu-notes**
- 搬入:`SKILL.md` + `tmux-article.md`(辅助示例)
- 清理:无敏感点
- README:`stable`,附 `tmux-article.md` 作示例输出
- 版本:`v0.1.0`

**elder-blessing-comments**
- 搬入:`SKILL.md`
- 清理:无敏感点
- README:`stable`,补示例输出
- 版本:`v0.1.0`

**submit-gitlab-mr**
- 搬入:`SKILL.md` + `agents/openai.yaml` + `scripts/upsert_mr.py` + `scripts/preflight.py`
- 清理:无敏感点(已 grep 确认无 `boban`/`actus`/IP/邮箱/token 硬编码)。glab 调用走 `--repo` 参数 + glab 自身认证,与具体 GitLab 实例解耦。
- 普适性:`agents/openai.yaml` 保留(Codex 端兼容,无害)。README 说明前置依赖 `glab` CLI + `glab auth login`(任何 GitLab 实例均可)。
- README:`stable`
- 版本:`v0.1.0`
- 验证:`python scripts/preflight.py --help` + `python scripts/upsert_mr.py --help` 确认无 import 错误

#### PR2

**algo-solver**
- 搬入:`SKILL.md` + `evals/evals.json`
- 改动:`SKILL.md` L125/L127 硬编码 `/Users/kris/Codes/Algorithm/` -> 环境变量 `ALGO_NOTES_DIR`(默认 `./algo-notes`)。文字改为"笔记默认落在 `./algo-notes/`,可用 `ALGO_NOTES_DIR` 环境变量覆盖"。
- README:`stable`,说明双语言输出(Python3 + Java)
- 版本:`v0.1.0`
- 验证:改路径后跑 `evals/evals.json` 确认不破

**xhs-image-gen**
- 搬入:`SKILL.md` + `references/{style-minimal,style-anthropic,style-notion}.md` + `examples/sample_cover_anthropic.{html,png}` + `scripts/{screenshot.js, package.json, package-lock.json, xhs_card_01..05.html, xhs_card_01..05.png}`
- 清理:无敏感点(grep 命中的 `Token` 是设计色值术语,非 API token)
- README:`beta`,说明依赖 Node.js + Playwright + chromium
- 版本:`v0.1.0`
- 验证:新目录 `npm ci` + `node scripts/screenshot.js` 跑通一张卡片

### README 规范

所有新 skill 的 README 按 `DESIGN.md` 头部模板,示例(`design-html`):

````markdown
# 🎨 design-html

> 用 Anthropic 暖色风生成设计说明 HTML

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `OpenClaw` |
| **最近更新** | `2026-07-24` |

**一句话:**给一段需求或草稿,生成 Anthropic 官网风格的暖色设计说明 HTML。

---

## 快速开始

```bash
# 1. 激活(软链到 skills 目录)
ln -s $(pwd)/skills/design-html ~/.claude/skills/design-html

# 2. 触发(在 Claude Code 对话中)
"帮我生成一个登录页的设计说明 HTML"
```
````

## 验证策略

- `algo-solver`:改路径后跑 `evals/evals.json`
- `xhs-image-gen`:`npm ci` + `node scripts/screenshot.js` 跑通
- `submit-gitlab-mr`:`preflight.py --help` + `upsert_mr.py --help`
- 纯 prompt 3 个(`design-html` / `zhihu-notes` / `elder-blessing`):文档齐全即可
- 每个 PR 提交前:`grep -rniE "/Users/kris|boban|actus|10\.172|@bobandata|wuhongyu" skills/<name>/` 确认零命中

## 非目标

- 不迁移 paper-spine(非本人项目,`WUBING2023/PaperSpine`)
- 不迁移四闸门(已在 `four-gate-ai-workflow` public repo)
- 不深度重构 `xhs-image-gen`(只补文档 + 验证,不补完整测试套件)
- 不改 42Marketplace 现有 3 个 skill 的 README(它们已符合规范)

## 风险

- `xhs-image-gen` 的 Playwright + chromium 依赖对用户较重 -> 标 `beta` 明示,README 给出完整安装步骤
- `submit-gitlab-mr` 依赖 glab CLI -> README 明确前置,且说明不限 GitLab 实例(自建/官方皆可)
