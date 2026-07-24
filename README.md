简体中文 | [English](./README.en.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Codex-blue.svg)](#)
[![Type](https://img.shields.io/badge/type-skill%20collection-purple.svg)](#skills)

# 🎯 42 Marketplace

> 为 Claude Code + Codex 打造的开源 skill 集合

## Why 42 Marketplace?

每个 skill 是一个即拷即用的**能力包**--给 AI 装上特定技能,一句话触发。纯 prompt 的零依赖,带脚本的注明前置,挑你需要的软链进 skills 目录即可。不绑定框架,不改你的工作流。

skill 本质是一个 `SKILL.md` 文件(加可选脚本/资源),Claude Code 和 Codex 都认这个格式。软链进各自的 skills 目录后,AI 会在合适的时机自动加载,你只需用自然语言触发。

## Features

- 📦 **即拷即用** - 纯 prompt skill 零依赖,clone 下来软链即用
- 🎯 **CC + Codex 通用** - 都是 SKILL.md 格式,两个端都能加载
- 🧪 **实战沉淀** - 每个 skill 都在真实工作流里用过、打磨过,不是 demo
- 🔓 **开源 MIT** - 随便用随便改

## Quickstart

clone 仓库:

```bash
git clone https://github.com/Coder42Y/42Marketplace.git ~/42Marketplace
```

软链你用的那个 skill 到 Claude Code 或 Codex(按需选,`<name>` 换成 skill 名):

```bash
mkdir -p ~/.claude/skills && ln -s ~/42Marketplace/skills/<name> ~/.claude/skills/<name>
```

```bash
mkdir -p ~/.codex/skills && ln -s ~/42Marketplace/skills/<name> ~/.codex/skills/<name>
```

## Usage

装好后,对 AI 用自然语言触发:

```text
"帮我沉淀一下这个登录方案的设计 HTML"   -> design-html
"讲一下力扣 300 最长递增子序列"         -> algo-solver
"把这篇文章生成小红书图文"              -> xhs-image-gen
"帮我提个 MR"                          -> submit-gitlab-mr
```

## Skills

- 🎨 [design-html](./skills/design-html/) - 把 idea 沉淀成 Anthropic 暖色风设计说明 HTML
- ✍️ [zhihu-notes](./skills/zhihu-notes/) - 知乎风格长文生成
- 🌺 [elder-blessing-comments](./skills/elder-blessing-comments/) - 长辈风祝福文案
- 🔀 [submit-gitlab-mr](./skills/submit-gitlab-mr/) - GitLab MR 提交(glab CLI)
- 🧮 [algo-solver](./skills/algo-solver/) - 算法题解(Python3 + Java)
- 📱 [xhs-image-gen](./skills/xhs-image-gen/) - 小红书图文卡片 `beta`
- 🎯 [daily-pulse](./skills/daily-pulse/) - 每日热点推送 + 按需查询
- 🔍 [deep-repo-research](./skills/deep-repo-research/) - 自动调研 GitHub/GitLab 仓库生成报告
- 🎬 [vid2report](./skills/vid2report/) - B站/YouTube 视频转结构化研究报告
- 🛡️ [vps-proxy-deploy](https://github.com/Coder42Y/vps-proxy-deploy) - 在 VPS 上安全部署网络中转(Hysteria2/VLESS 等)↗ 独立仓

## Contributing

1. skill 放 `skills/<name>/`,独立工具放 `tools/<name>/`
2. 每个 skill 含 `SKILL.md`(技能定义)和 `README.md`(用户文档)
3. 遵循 [`DESIGN.md`](./DESIGN.md) 的设计规范

## License

MIT

## 隐私

本仓公开的代码和文档均经过清理,不含个人信息、API key / token / 密码、私有配置。个人文件通过 `.gitignore` 排除。
