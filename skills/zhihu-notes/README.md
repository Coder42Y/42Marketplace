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
