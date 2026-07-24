# 🎨 design-html

> 把 idea/方案沉淀成 Anthropic 暖色风的设计说明 HTML —— 讲思路方法,不堆代码,自带 SVG 架构图。

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `Codex` |
| **License** | `MIT` |
| **最近更新** | `2026-07-24` |

---

## Why

刚和同事聊完一个架构、领导聊完一个方案、自己想清楚一个 idea,需要一份能直接发出去、打开就能看的说明文档 —— 但又不想堆代码、写 Markdown 又不够直观。`design-html` 把对话沉淀成一份带架构图、Anthropic 暖色排版的独立 HTML 文件,讲清"为什么这么选",而不是"代码怎么写"。

## Features

- **思路优先**:8 节骨架(是什么 → 整体长什么样 → 关键选择 → 设计坚持 → 流程 → 第一版做什么 → 风险 → 接下来),讲方法不堆 SQL/正则/JSON。
- **自带架构图**:横向泳道 SVG,色弱安全高对比度三色箭头,带流光动画;节点 ≤10 时默认纯 SVG 手绘。
- **Anthropic 暖色排版**:棕橙主色 + 暖米底,标题渐变、决策卡 hover 上浮、章节视口淡入。
- **独立 HTML 输出**:所有 CSS/JS/SVG 内联,双击可打开,不依赖任何外部资源。
- **三种画图方式可选**:纯 SVG(动画好)/ codex+drawio(可二次编辑)/ Mermaid(快速预览),给用户选不替他决定。

## Quickstart

```bash
# 1. 软链到 skills 目录(Claude Code)
ln -s $(pwd)/skills/design-html ~/.claude/skills/design-html

# 2. Codex 用户:把整个 skills 目录软链到 ~/.codex/skills/
```

触发(在 Claude Code / Codex 对话中):

> "帮我把刚聊的登录方案沉淀成设计 HTML"
> "出个说明文档,讲讲这个架构怎么选的"
> "把刚才的 idea 整理成设计页"

输出:`./design.html` —— 双击即可在浏览器打开。

## Usage

**典型场景**

- 架构方案评审:`"把我们刚定的多 Agent 调度架构出个设计说明"`
- idea 备忘:`"把今天想的 XX 沉淀一下,带架构图"`
- 方案交付:`"做个设计 HTML 给我发给领导"`
- 复盘文档:`"把这个迭代的设计决策整理成 HTML"`

**架构图画法选择**(skill 第一次会问你)

| 方式 | 适用 |
|---|---|
| 纯 SVG 手绘(默认) | 节点 ≤10,需要动画和精致排版 |
| codex + drawio | 节点 >10,需要可二次编辑的 `.drawio` 源文件 |
| Mermaid | 快速预览草稿,不需要动画 |

**典型产物结构**

```
.
├── design.html         # 主文档(双击打开)
├── architecture.svg    # 架构图源(若用 SVG 手绘)
└── architecture.drawio # drawio 源(若用 drawio)
```

## 依赖

无 —— 纯 prompt skill,生成的 HTML 所有 CSS/JS/SVG 内联,双击可打开。

> 可选:若选 codex+drawio 画架构图,需另装 drawio CLI;默认用纯 SVG 手绘,无需任何依赖。

## License

MIT
