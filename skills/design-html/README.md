# 🎨 design-html

> 把 idea/方案沉淀成 Anthropic 暖色风的设计说明 HTML

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `Codex` |
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
