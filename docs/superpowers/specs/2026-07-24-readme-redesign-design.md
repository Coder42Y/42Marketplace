# 42Marketplace README 重设计 spec

- 日期:2026-07-24
- 状态:已认可,待实现
- 分支:readme-redesign

## 背景

42Marketplace(`Coder42Y/42Marketplace`)根 README 当前 157 行、中英双份上下堆叠,排版单调无层次(用户反馈"太丑")。同时定位调整:从 Claude Code + OpenClaw 改为 Claude Code + Codex。

## 目标

1. 重设计根 README 排版:**极简 skill 列表 + 吸引人的说明 + 蓝色语言切换**(不再上下堆叠中英)
2. 定位调整:CC + OpenClaw -> CC + Codex
3. 各 skill README 兼容字段 OpenClaw -> Codex(**符合现实,不虚标**)

## 设计

### 根 README 新结构(c-v3 定稿,ark-vision 验证通过)

`README.md`(中文版)结构:

1. **语言切换**:顶部一行 `简体中文 | [English](./README.en.md)`(English 蓝色链接,加粗突出全局导航)
2. **标题**:`🎯 42 Marketplace`(大字加粗)
3. **一句话定位**:`为 Claude Code + Codex 打造的开源 skill 集合`
4. **吸引人说明**(1 段 + 4 条特色 bullet):
   - 段:每个 skill 是即拷即用的能力包,给 AI 装上特定技能,一句话触发。纯 prompt 的零依赖,带脚本的注明前置。不绑定框架,不改工作流。
   - bullet:📦 即拷即用(纯 prompt 零依赖)/ 🎯 CC+Codex 通用(SKILL.md 格式)/ 🧪 实战沉淀(非 demo)/ 🔓 开源 MIT
5. **Skills 极简列表**:每行 `emoji [skill名](链接) - 一句话`,9 个 skill(含已有 3 个),xhs 标 `beta` 文字 badge
6. **安装**:
   ```
   ln -s skills/<name> ~/.claude/skills/   # Claude Code
   ln -s skills/<name> ~/.codex/skills/    # Codex
   ```
7. 贡献/隐私:精简保留末尾

### 双语方案:两文件互链(参考 Vue/Vite 等权威做法)

- `README.md`(中文,主):顶部 `简体中文 | [English](./README.en.md)`
- `README.en.md`(英文,新建):顶部 `[简体中文](./README.md) | English`
- GitHub 默认显示 `README.md`(中文),点 English 跳 `README.en.md`
- **去掉当前"上下中英双份堆叠"**(当前 157 行减半)

### 各 skill README 兼容字段改法

兼容字段 `Claude Code`, `OpenClaw` -> `Claude Code`, `Codex`。涉及文件:

- `skills/design-html/README.md`
- `skills/zhihu-notes/README.md`
- `skills/elder-blessing-comments/README.md`
- `skills/submit-gitlab-mr/README.md`(当前兼容 `Claude Code, OpenClaw, Codex`,去掉 OpenClaw)
- `skills/algo-solver/README.md`
- `skills/xhs-image-gen/README.md`
- `skills/daily-pulse/README.md`(当前 `OpenClaw >= 0.5.0`,见下方特殊处理)
- `skills/deep-repo-research/README.md`
- `skills/vid2report/`(SKILL.md,无 README 兼容字段则跳过)

### "符合现实"的兼容判定

- skill 都是 SKILL.md 格式,CC/Codex 都识别(理论通用)
- **未逐一在两端实测**,兼容字段标 `Claude Code`, `Codex`,**不标版本号**(避免像 daily-pulse 原 `OpenClaw >= 0.5.0` 那样虚标)
- **daily-pulse 特殊**:核心 skill(预抓取+评分)通用,但 cron 定时推送功能依赖 OpenClaw cron。兼容字段标 `Claude Code`, `Codex`,但在 README 注明"cron 推送需 OpenClaw"(符合现实,不删 OpenClaw 依赖说明)
- 根 README 说明里"CC + Codex 通用"指 SKILL.md 格式通用,不保证每个 skill 都在 Codex 实测过

## 范围

- 重写根 `README.md`(中文版 c-v3 结构)+ 新建 `README.en.md`(英文版)
- 改各 skill README 兼容字段 OpenClaw -> Codex(含已有 3 个)
- daily-pulse 保留 cron 的 OpenClaw 依赖说明

## 非目标

- 不改 skill 功能/实现(SKILL.md / 脚本不动)
- 不改 `DESIGN.md`(规范,本次不动)
- 不改 daily-pulse 等内部历史 docs(`docs/superpowers/` 下的旧 spec/plan,OpenClaw 引用保留)
- 不改 `submit-gitlab-mr` 的 `agents/openai.yaml`(Codex 配置,保留)

## 验证

- 根 README 渲染(GitHub)视觉干净(ark-vision 已验证 c-v3:层次清晰/留白舒适/吸引力好)
- 语言切换链接工作(`README.md` <-> `README.en.md`)
- 各 skill 兼容字段无 OpenClaw 残留(grep,除 daily-pulse cron 说明)
- 兼容字段符合现实(无虚标版本)
