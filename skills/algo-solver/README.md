# 🧮 algo-solver

> 贴一道算法题或一段题解代码,生成面试可用的讲解 + Python3/Java 双语言题解,自动落盘成结构化笔记。

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `Codex` |
| **依赖** | 无(纯 prompt skill,LLM 直接生成代码) |
| **最近更新** | `2026-07-24` |

## Why

面试算法题最常见的失败不是写不出,而是**讲不清**——心里有最优解,白板前一紧张,讲不出"为什么这么想到",被追问就卡壳。

`algo-solver` 强制每道题按同一套骨架产出(一句话题意 → 暴力解 → 关键观察 → 最优解 → 复杂度 → 边界 → follow-up),既练**面试讲思路的肌肉记忆**,又给**能直接默写的最优代码**。

## Features

- **双语言题解** — Python3 在前、Java 在后,贴 LeetCode 签名,可直接丢平台跑
- **解题 + 分析双模式** — 题目描述走解题模式,纯代码走分析模式(自动反推题意)
- **结构化笔记自动落盘** — 按考点分目录(dp / binary-search / two-pointers …),面试前按考点批量复习
- **讲解深度自适应** — 简单题讲快讲准,难题每步铺透 + 多列 follow-up
- **零依赖** — 纯 prompt,无运行时,无外部工具

## Quickstart

### 1. 软链到 Agent 技能目录

```bash
# Claude Code
ln -s ~/42Marketplace/skills/algo-solver ~/.claude/skills/algo-solver

# Codex(软链至对应 skills 目录即可,路径因安装方式而异)
ln -s ~/42Marketplace/skills/algo-solver ~/.codex/skills/algo-solver
```

### 2. 触发

贴一道题,直接讲:

```
讲一下力扣 300 最长递增子序列
```

贴一段代码,直接分析:

```
这段单调栈代码看不懂,帮我分析
```

Agent 会自动判断走解题模式还是分析模式,产出讲解 + 双语言代码,落盘到 `ALGO_NOTES_DIR`。

## Usage

### 解题模式(输入是题面)

直接贴题目描述 / 力扣链接 / 截图转述即可。固定骨架:

- **一句话题意** — 翻译本质,不照抄原题
- **思路** — 怎么讲给面试官:暴力 → 关键观察 → 最优
- **复杂度** — 时间 + 空间
- **代码** — Python3 在前、Java 在后,贴 LeetCode 签名,关键行内注释
- **边界 & 手动模拟** — dry run + 2-3 个边界 case
- **面试可能追问** — follow-up,提前想好

**示例触发**:

```
讲一下力扣 33 搜索旋转排序数组
```

### 分析模式(输入是题解代码)

贴一段代码(自己写的、抄来不懂的、面试复盘的),skill 会先**反推题意**,再按逻辑块讲解 + dry run + 复杂度 + 优化点。

**示例触发**:

```
这段 DP 代码看不太懂,帮我讲讲
```

> 拿不准模式时,直接问一句"你这是要我解题,还是讲解这段代码?"——猜错模式整篇都得重来。

## 落盘

题解默认落在 `./algo-notes/`,按**考点**分目录:

```
./algo-notes/
├── dp/300-longest-increasing-subsequence.md
├── binary-search/33-search-in-rotated-sorted-array.md
├── two-pointers/15-3sum.md
└── misc/   ← 考点不明确时先丢这里,别卡在分类上
```

自定义路径:

```bash
export ALGO_NOTES_DIR=~/my-algo-notes
```

**命名规则**:`{题号}-{英文短名}.md`,题号优先用平台题号(力扣题号优先)。解题模式与分析模式都按此规则保存,生成后立即写文件并在回复里告知路径。

## License

MIT
