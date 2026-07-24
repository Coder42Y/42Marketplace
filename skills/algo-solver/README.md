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
