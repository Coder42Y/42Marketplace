# 🗓️ daily-report

> 把一天的 Claude Code session 整理成能在例会上直接念的进展汇报：白话一层，技术说明一层，产出单文件 HTML。

| | |
|:---|:---|
| **版本** | `v1.0.0` |
| **状态** | `beta` |
| **兼容** | `Claude Code` |
| **最近更新** | `2026-10-13` |

**一句话：**开每日例会前说一句「出个日报」，它会读当天跑过的 session，先和你对齐大纲，再写一份念得出来、被追问也答得上的 HTML 汇报。

---

## 快速开始

```bash
# 1. 安装（Claude Code）
ln -s ~/42Marketplace/skills/daily-report ~/.claude/skills/daily-report

# 2. 触发
"出个日报" / "总结一下今天的工作，拿去开例会" / "10 月 9 号 my-app 的例会稿"
```

视觉规范来自 [design-html](../design-html/)，建议一起安装。

---

## 特性

- **🔎 读真实 session** — 直接读本机 `~/.claude/projects` 的对话记录，按本地时区截出那一天；从别的目录启动、但在做这个项目的 session 也能找出来
- **🧭 先对齐再动笔** — 先给素材速览表、5 段大纲和几个要你拍板的问题，你点头后才写；说「直接出」可以跳过
- **🗣️ 两层写法** — 白话层能直接念，不出现内部代号；技术说明层写到模块名、根因、设计取舍和数字
- **✅ 核对现状** — 涉及 PR / issue 的用 `gh` 查现在的状态，对不上的在回复里提醒；调研类工作以产出的文档为准
- **🧹 去 AI 腔** — 内置中文版的写作规则：不用「赋能、闭环」这类词，不夸大成果，不凑排比

---

## 流程

1. **问清范围**：哪一天、哪个项目。你已经说清楚的就不问。
2. **拉 session**：`scripts/extract_day.py` 把那一天的 session 分成三组：项目内的、从别处启动但相关的、无关的。同一个 session 的分叉会合并。
3. **核对事实**：按工作类型来，查不到的标「未验证」。
4. **对齐大纲**：素材速览、5 段大纲、待拍板的问题。
5. **写 HTML**：从 `assets/skeleton.html` 开始，固定 5 段：开场一句话 / 做完了 / 进行中 / 需要协调·风险 / 明天。
6. **交付**：直接把 HTML 文件给你。需要局域网链接时，可选用 `scripts/publish.sh`。

---

## 文件

| 路径 | 作用 |
|------|------|
| `SKILL.md` | 完整流程 |
| `references/style.md` | 语言、粒度、长度规则 |
| `assets/skeleton.html` | 报告骨架：CSS、时间线、柱状图都已写好，换掉【】里的占位即可 |
| `scripts/extract_day.py` | 拉取某一天的 session，生成索引和精简文本 |
| `scripts/publish.sh` | 可选：复制到 `~/standup/` 并起一个局域网静态服务，不占用已有端口 |

---

## 前置依赖

- **Claude Code**：要读它保存在 `~/.claude/projects` 下的 session 记录，所以只支持 Claude Code
- **Python** `>= 3.9`，只用标准库
- **可选**：`gh` CLI，用来核对 PR / issue 状态；`publish.sh` 需要 `curl`

---

## 验证范围

在一位用户的真实 session 上跑过两轮 A/B，覆盖 4 个场景：session 多的一天、只有一个 session 的周末、先对齐大纲、范围不清楚。结构类自动检查全部通过，不用这个 skill 的对照组是 55%。session 多的一天大约要 9 分钟、30 万 token。

---

## License

MIT
