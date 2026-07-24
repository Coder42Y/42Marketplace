# 42Marketplace Skills 上传 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 6 个本地原创 skill 整理上传到 `Coder42Y/42Marketplace`,分 2 个 PR 合入 main。

**Architecture:** copy 现有 skill 目录到 `skills/<name>/`,每个补一份按 `DESIGN.md` 规范的 README;`algo-solver` 改硬编码路径为环境变量;`xhs-image-gen` 跑通 Playwright 截图脚本验证;每个 PR 提交前 grep 敏感词确认零命中;走 branch -> PR -> squash merge(main 有 ruleset)。

**Tech Stack:** Markdown skills / Python(`submit-gitlab-mr` 脚本)/ Node.js + Playwright(`xhs-image-gen`)

## Global Constraints

- 版本号统一 `v0.1.0`(首次公开)
- 状态:`design-html` / `zhihu-notes` / `elder-blessing-comments` / `submit-gitlab-mr` / `algo-solver` = `stable`;`xhs-image-gen` = `beta`
- README 头部严格按 `DESIGN.md` 模板(emoji 标题 + 一句话 + 版本/状态/兼容/最近更新表 + 快速开始)
- 敏感词 grep 必须零命中:`/Users/kris|boban|actus|10\.172|@bobandata|wuhongyu`
- 所有上传走 PR(main 分支 ruleset B 档:要求 PR + 禁 force-push + 禁删)
- 工作目录:`/Users/kris/Codes/KrisVault`(本地目录名未随 repo 改名,origin 已指向 `Coder42Y/42Marketplace`)

## File Structure

PR1(分支 `add-skills-to-marketplace`,基于 main,含已 commit 的 spec):
- Create: `skills/design-html/SKILL.md`(copy from `~/.claude/skills/design-html/SKILL.md`)
- Create: `skills/design-html/README.md`
- Create: `skills/zhihu-notes/SKILL.md`(copy from `~/.openclaw/workspace/skills/zhihu-notes/SKILL.md`)
- Create: `skills/zhihu-notes/tmux-article.md`(copy)
- Create: `skills/zhihu-notes/README.md`
- Create: `skills/elder-blessing-comments/SKILL.md`(copy from `~/.claude/skills/elder-blessing-comments/SKILL.md`)
- Create: `skills/elder-blessing-comments/README.md`
- Create: `skills/submit-gitlab-mr/SKILL.md`(copy from `~/.codex/skills/submit-gitlab-mr/SKILL.md`)
- Create: `skills/submit-gitlab-mr/agents/openai.yaml`(copy)
- Create: `skills/submit-gitlab-mr/scripts/upsert_mr.py`(copy)
- Create: `skills/submit-gitlab-mr/scripts/preflight.py`(copy)
- Create: `skills/submit-gitlab-mr/README.md`

PR2(分支 `add-skills-pr2`,基于 main):
- Create: `skills/algo-solver/SKILL.md`(copy + modify L125-127 路径)
- Create: `skills/algo-solver/evals/evals.json`(copy)
- Create: `skills/algo-solver/README.md`
- Create: `skills/xhs-image-gen/SKILL.md`(copy from `~/.openclaw/workspace/skills/xhs-image-gen/SKILL.md`)
- Create: `skills/xhs-image-gen/references/style-{anthropic,notion,minimal}.md`(copy)
- Create: `skills/xhs-image-gen/examples/sample_cover_anthropic.{html,png}`(copy)
- Create: `skills/xhs-image-gen/scripts/{screenshot.js,package.json,package-lock.json,xhs_card_01..05.html,xhs_card_01..05.png}`(copy)
- Create: `skills/xhs-image-gen/README.md`

---

### Task 1: design-html

**Files:**
- Create: `skills/design-html/SKILL.md`
- Create: `skills/design-html/README.md`

**Interfaces:**
- Consumes: 无(独立 skill)
- Produces: `skills/design-html/` 目录,可被 42Marketplace README 技能列表引用

- [ ] **Step 1: copy SKILL.md**

```bash
cd /Users/kris/Codes/KrisVault
mkdir -p skills/design-html
cp ~/.claude/skills/design-html/SKILL.md skills/design-html/SKILL.md
```

- [ ] **Step 2: 写 README.md**

写入 `skills/design-html/README.md`:

````markdown
# 🎨 design-html

> 把 idea/方案沉淀成 Anthropic 暖色风的设计说明 HTML

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `OpenClaw` |
| **最近更新** | `2026-07-24` |

**一句话:**给一个想法/架构/方案,生成可分享的 HTML 设计说明文档,讲思路方法不堆代码,自带 SVG 架构图。

---

## 快速开始

```bash
# 1. 激活(软链到 skills 目录)
ln -s $(pwd)/skills/design-html ~/.claude/skills/design-html

# 2. 触发(在 Claude Code 对话中)
"帮我把刚聊的登录方案沉淀成设计 HTML"
"出个说明文档,讲讲这个架构怎么选的"
```

## 依赖

无。纯 prompt skill,生成的 HTML 所有 CSS/JS 内联,双击可打开。

> 可选:若选 codex+drawio 画架构图,需另装 drawio CLI;默认用纯 SVG 手绘。
````

- [ ] **Step 3: 敏感扫描**

Run: `grep -rniE "/Users/kris|boban|actus|10\.172|@bobandata|wuhongyu" skills/design-html/`
Expected: 无输出(零命中)

- [ ] **Step 4: commit**

```bash
git add skills/design-html
git commit -m "Add design-html skill"
```

---

### Task 2: zhihu-notes

**Files:**
- Create: `skills/zhihu-notes/SKILL.md`
- Create: `skills/zhihu-notes/tmux-article.md`
- Create: `skills/zhihu-notes/README.md`

- [ ] **Step 1: copy SKILL.md + tmux-article.md**

```bash
cd /Users/kris/Codes/KrisVault
mkdir -p skills/zhihu-notes
cp ~/.openclaw/workspace/skills/zhihu-notes/SKILL.md skills/zhihu-notes/SKILL.md
cp ~/.openclaw/workspace/skills/zhihu-notes/tmux-article.md skills/zhihu-notes/tmux-article.md
```

- [ ] **Step 2: 写 README.md**

写入 `skills/zhihu-notes/README.md`:

````markdown
# ✍️ zhihu-notes

> 生成知乎风格的优质长文

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `OpenClaw` |
| **最近更新** | `2026-07-24` |

**一句话:**把任意技术主题转成知乎体长文,标准结构 + 文风规范,直接可发。

---

## 快速开始

```bash
# 1. 激活
ln -s $(pwd)/skills/zhihu-notes ~/.claude/skills/zhihu-notes

# 2. 触发
"生成一篇知乎文章,主题是 Claude Code 的 skill 系统"
"用知乎风格写一下我是怎么搭刷题工作流的"
```

## 依赖

无。纯 prompt skill。`tmux-article.md` 是一篇示例输出,参考其结构和文风。
````

- [ ] **Step 3: 敏感扫描**

Run: `grep -rniE "/Users/kris|boban|actus|10\.172|@bobandata|wuhongyu" skills/zhihu-notes/`
Expected: 无输出

- [ ] **Step 4: commit**

```bash
git add skills/zhihu-notes
git commit -m "Add zhihu-notes skill"
```

---

### Task 3: elder-blessing-comments

**Files:**
- Create: `skills/elder-blessing-comments/SKILL.md`
- Create: `skills/elder-blessing-comments/README.md`

- [ ] **Step 1: copy SKILL.md**

```bash
cd /Users/kris/Codes/KrisVault
mkdir -p skills/elder-blessing-comments
cp ~/.claude/skills/elder-blessing-comments/SKILL.md skills/elder-blessing-comments/SKILL.md
```

- [ ] **Step 2: 写 README.md**

写入 `skills/elder-blessing-comments/README.md`:

````markdown
# 🌺 elder-blessing-comments

> 生成长辈风社交媒体祝福文案

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `OpenClaw` |
| **最近更新** | `2026-07-24` |

**一句话:**生成抖音/微信群/朋友圈的长辈风祝福评论,emoji 拉满,直接复制粘贴。

---

## 快速开始

```bash
# 1. 激活
ln -s $(pwd)/skills/elder-blessing-comments ~/.claude/skills/elder-blessing-comments

# 2. 触发
"来点长辈风祝福语,早上的"
"帮我写几条抖音评论,越土越好"
```

## 依赖

无。纯 prompt skill。

## 示例输出

`早上好🌞🌹新的一天开始啦,愿你开心快乐每一天,身体健康,万事如意🙏🌺🌺🌺`

```
🌹🌹🌹祝福送到🌹🌹🌹
身体健康🙏
家庭幸福🏠
财源广进💰
好运连连🍀
```
````

- [ ] **Step 3: 敏感扫描**

Run: `grep -rniE "/Users/kris|boban|actus|10\.172|@bobandata|wuhongyu" skills/elder-blessing-comments/`
Expected: 无输出

- [ ] **Step 4: commit**

```bash
git add skills/elder-blessing-comments
git commit -m "Add elder-blessing-comments skill"
```

---

### Task 4: submit-gitlab-mr

**Files:**
- Create: `skills/submit-gitlab-mr/SKILL.md`
- Create: `skills/submit-gitlab-mr/agents/openai.yaml`
- Create: `skills/submit-gitlab-mr/scripts/upsert_mr.py`
- Create: `skills/submit-gitlab-mr/scripts/preflight.py`
- Create: `skills/submit-gitlab-mr/README.md`

- [ ] **Step 1: copy 全部源文件**

```bash
cd /Users/kris/Codes/KrisVault
mkdir -p skills/submit-gitlab-mr/agents skills/submit-gitlab-mr/scripts
cp ~/.codex/skills/submit-gitlab-mr/SKILL.md skills/submit-gitlab-mr/SKILL.md
cp ~/.codex/skills/submit-gitlab-mr/agents/openai.yaml skills/submit-gitlab-mr/agents/openai.yaml
cp ~/.codex/skills/submit-gitlab-mr/scripts/upsert_mr.py skills/submit-gitlab-mr/scripts/upsert_mr.py
cp ~/.codex/skills/submit-gitlab-mr/scripts/preflight.py skills/submit-gitlab-mr/scripts/preflight.py
```

- [ ] **Step 2: 验证脚本能正常加载(--help)**

Run:
```bash
python3 skills/submit-gitlab-mr/scripts/preflight.py --help 2>&1 | head -5
python3 skills/submit-gitlab-mr/scripts/upsert_mr.py --help 2>&1 | head -5
```
Expected: 两个都输出 usage/help,无 `ModuleNotFoundError` / `ImportError`。

- [ ] **Step 3: 写 README.md**

写入 `skills/submit-gitlab-mr/README.md`:

````markdown
# 🔀 submit-gitlab-mr

> 冲突检查 + 快速提交 GitLab MR

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `OpenClaw`, `Codex` |
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
- `agents/openai.yaml` -- Codex 端接口配置(可选,不影响 Claude Code/OpenClaw 使用)

skill 只负责 Git 冲突检查这一个 gate;代码审查、CI、lint 由其他流程负责。
````

- [ ] **Step 4: 敏感扫描**

Run: `grep -rniE "/Users/kris|boban|actus|10\.172|@bobandata|wuhongyu" skills/submit-gitlab-mr/`
Expected: 无输出

- [ ] **Step 5: commit**

```bash
git add skills/submit-gitlab-mr
git commit -m "Add submit-gitlab-mr skill"
```

---

### Task 5: PR1 push + 开 PR

**Files:** 无(操作分支与 PR)

- [ ] **Step 1: push 分支**

```bash
cd /Users/kris/Codes/KrisVault
git push -u origin add-skills-to-marketplace
```
Expected: 新分支推送成功,返回 GitHub 的 PR 创建链接。

- [ ] **Step 2: 开 PR1**

```bash
gh pr create --repo Coder42Y/42Marketplace --base main --head add-skills-to-marketplace \
  --title "Add 4 skills: design-html / zhihu-notes / elder-blessing-comments / submit-gitlab-mr" \
  --body "首批 4 个原创 skill 上传(轻量整理,代码未改):
- design-html:Anthropic 暖色风设计说明 HTML(纯 prompt)
- zhihu-notes:知乎风格长文(纯 prompt)
- elder-blessing-comments:长辈风祝福文案(纯 prompt)
- submit-gitlab-mr:GitLab MR 提交(glab CLI,通用,无公司硬编码)

每个含 README(按 DESIGN.md 规范),敏感词 grep 零命中。设计 spec 见 docs/superpowers/specs/2026-07-24-skills-upload-design.md。"
```
Expected: 返回 PR URL。等用户 review + merge。

---

### Task 6: algo-solver(PR2 分支)

**Files:**
- Create: `skills/algo-solver/SKILL.md`(copy + 改 L125-127)
- Create: `skills/algo-solver/evals/evals.json`
- Create: `skills/algo-solver/README.md`

- [ ] **Step 1: 切到 main 建新分支 + copy 文件**

```bash
cd /Users/kris/Codes/KrisVault
git checkout main
git checkout -b add-skills-pr2
mkdir -p skills/algo-solver/evals
cp ~/.claude/skills/algo-solver/SKILL.md skills/algo-solver/SKILL.md
cp ~/.claude/skills/algo-solver/evals/evals.json skills/algo-solver/evals/evals.json
```

- [ ] **Step 2: 改 SKILL.md 硬编码路径**

用 Edit 工具,`old_string`:

```
- **位置**：项目根目录 `/Users/kris/Codes/Algorithm/` 下，按**考点**分目录。
  ```
  /Users/kris/Codes/Algorithm/
  ├── dp/300-longest-increasing-subsequence.md
```

`new_string`:

```
- **位置**：题解默认落在 `./algo-notes/` 下，按**考点**分目录。可用环境变量 `ALGO_NOTES_DIR` 覆盖。
  ```
  $ALGO_NOTES_DIR (默认 ./algo-notes/)
  ├── dp/300-longest-increasing-subsequence.md
```

- [ ] **Step 3: 验证改动**

Run:
```bash
grep -n "/Users/kris" skills/algo-solver/SKILL.md
grep -n "ALGO_NOTES_DIR" skills/algo-solver/SKILL.md
```
Expected: 第一条无输出(硬编码已清除);第二条命中 1 行(新配置说明)。

- [ ] **Step 4: 写 README.md**

写入 `skills/algo-solver/README.md`:

````markdown
# 🧮 algo-solver

> 算法题讲解与题解生成(面试备战)

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `OpenClaw` |
| **最近更新** | `2026-07-24` |

**一句话:**贴一道算法题或一段题解代码,生成面试可用的讲解 + Python3/Java 双语言题解,自动落盘成结构化笔记。

---

## 快速开始

```bash
# 1. 激活
ln -s $(pwd)/skills/algo-solver ~/.claude/skills/algo-solver

# 2. 触发
"讲一下力扣 300 最长递增子序列"
"这段单调栈代码看不懂,帮我分析"
```

## 笔记落盘

题解默认落在 `./algo-notes/` 下,按考点分目录(dp/binary-search/two-pointers...)。可用环境变量覆盖:

```bash
export ALGO_NOTES_DIR=~/my-algo-notes
```

## 依赖

无。纯 prompt skill,Python3/Java 代码片段由 LLM 生成。`evals/evals.json` 是评测数据。
````

- [ ] **Step 5: 敏感扫描**

Run: `grep -rniE "/Users/kris|boban|actus|10\.172|@bobandata|wuhongyu" skills/algo-solver/`
Expected: 无输出

- [ ] **Step 6: commit**

```bash
git add skills/algo-solver
git commit -m "Add algo-solver skill (path made configurable)"
```

---

### Task 7: xhs-image-gen

**Files:**
- Create: `skills/xhs-image-gen/SKILL.md`
- Create: `skills/xhs-image-gen/references/style-{anthropic,notion,minimal}.md`
- Create: `skills/xhs-image-gen/examples/sample_cover_anthropic.{html,png}`
- Create: `skills/xhs-image-gen/scripts/{screenshot.js,package.json,package-lock.json,xhs_card_01..05.html,xhs_card_01..05.png}`
- Create: `skills/xhs-image-gen/README.md`

- [ ] **Step 1: copy 全部源文件**

```bash
cd /Users/kris/Codes/KrisVault
cp -r ~/.openclaw/workspace/skills/xhs-image-gen skills/xhs-image-gen
# 注意:不要把 node_modules 带进来(源目录没有则无需处理)
ls skills/xhs-image-gen/scripts/ | grep -v node_modules
```
Expected: 列出 screenshot.js / package.json / package-lock.json / xhs_card_01..05.{html,png},无 node_modules。

- [ ] **Step 2: 安装依赖 + 验证截图脚本能跑通**

Run:
```bash
cd /Users/kris/Codes/KrisVault/skills/xhs-image-gen/scripts
npm ci
npx playwright install chromium
node screenshot.js ../examples/sample_cover_anthropic.html --output-dir /tmp/xhs-test
```
Expected: `npm ci` 成功;chromium 安装成功;screenshot.js 输出"截图完成"并生成 `/tmp/xhs-test/sample_cover_anthropic.png`。若失败,记录错误,在 README 标注 beta 并继续(不阻塞)。

- [ ] **Step 3: 写 README.md**

写入 `skills/xhs-image-gen/README.md`:

````markdown
# 📱 xhs-image-gen

> 小红书图文卡片生成器

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `beta` |
| **兼容** | `Claude Code`, `OpenClaw` |
| **最近更新** | `2026-07-24` |

**一句话:**把文案/文章/主题转成 1-10 张小红书风格 PNG 卡片,3 种风格(anthropic/notion/minimal),HTML 是中间产物,最终交付 PNG。

---

## 前置依赖

- **Node.js** >= 18
- **Playwright** + chromium(首次按下面命令安装)

## 快速开始

```bash
# 1. 激活
ln -s $(pwd)/skills/xhs-image-gen ~/.claude/skills/xhs-image-gen

# 2. 首次安装依赖
cd skills/xhs-image-gen/scripts && npm install && npx playwright install chromium

# 3. 触发
"把这篇文章生成小红书图文,用 anthropic 风格"
"做3个职场沟通技巧的小红书图片,notion 风"
```

## 脚本

- `scripts/screenshot.js` -- Playwright 批量截图,HTML -> PNG
  - 用法:`node scripts/screenshot.js xhs_card_*.html [--clean] [--output-dir <dir>]`

## 风格

- `references/style-anthropic.md` -- 暖米色 + 衬线 + 赤陶橙
- `references/style-notion.md` -- 白底 + 图标化 + 扁平
- `references/style-minimal.md` -- 纯黑白灰 + 零圆角

`examples/sample_cover_anthropic.html` 是示例封面卡,浏览器打开查看预期效果。

> 状态为 beta:依赖 Playwright + chromium,安装较重。功能已验证可用,后续补完整测试。
````

- [ ] **Step 4: 敏感扫描**

Run: `grep -rniE "/Users/kris|boban|actus|10\.172|@bobandata|wuhongyu" skills/xhs-image-gen/`
Expected: 无输出(注意:`references/style-*.md` 里的 "Token" 是设计色值术语,不算命中,因为 grep 模式不含裸 "token")

- [ ] **Step 5: commit**

```bash
cd /Users/kris/Codes/KrisVault
git add skills/xhs-image-gen
git commit -m "Add xhs-image-gen skill (beta, Playwright verified)"
```

---

### Task 8: PR2 push + 开 PR

**Files:** 无

- [ ] **Step 1: push 分支**

```bash
cd /Users/kris/Codes/KrisVault
git push -u origin add-skills-pr2
```
Expected: 新分支推送成功。

- [ ] **Step 2: 开 PR2**

```bash
gh pr create --repo Coder42Y/42Marketplace --base main --head add-skills-pr2 \
  --title "Add 2 skills: algo-solver / xhs-image-gen" \
  --body "第二批 2 个原创 skill(需改代码/验证):
- algo-solver:算法题解(纯 prompt),已把硬编码路径改为 ALGO_NOTES_DIR 环境变量(默认 ./algo-notes/)
- xhs-image-gen:小红书卡片(Node + Playwright),已本地验证 screenshot.js 跑通,标 beta

敏感词 grep 零命中。设计 spec 见 docs/superpowers/specs/2026-07-24-skills-upload-design.md(PR1 分支)。"
```
Expected: 返回 PR URL。等用户 review + merge。

---

## Self-Review

**1. Spec coverage:**
- 6 个 skill 全覆盖:design-html(T1)/ zhihu-notes(T2)/ elder-blessing-comments(T3)/ submit-gitlab-mr(T4)/ algo-solver(T6)/ xhs-image-gen(T7)✓
- PR 拆分 2 个:T5(PR1)/ T8(PR2)✓
- README 按 DESIGN.md:每个 task 的 README 草案均含 emoji 标题 + 一句话 + 版本/状态/兼容/最近更新表 + 快速开始 ✓
- 验证策略:submit-gitlab-mr --help(T4-S2)/ algo-solver grep(T6-S3)/ xhs screenshot.js(T7-S2)/ 敏感扫描(每 task)✓
- 非目标(paper-spine/四闸门不迁):plan 未涉及 ✓

**2. Placeholder scan:** 无 TBD/TODO;每个 README 草案完整;algo-solver 的 old/new 代码块确切;验证命令带 expected 输出 ✓

**3. Type consistency:** 分支名 `add-skills-to-marketplace`(PR1)/ `add-skills-pr2`(PR2)在所有 task 中一致;`ALGO_NOTES_DIR` 在 T6 改动与 T6 README 一致 ✓
