<div align="center">

<img src="logo.svg" width="120" alt="logo">

# 🎯 42 Marketplace

为 Claude Code + Codex 打造的开源 skill 集合

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Codex-blue.svg)](#)
[![Type](https://img.shields.io/badge/type-skill%20collection-purple.svg)](#skills)

简体中文 ｜ [English](./README.en.md)

</div>

---

## Why 42 Marketplace?

每个 skill 是一个即拷即用的**能力包**--给 AI 装上特定技能,一句话触发。纯 prompt 的零依赖,带脚本的注明前置,挑你需要的软链进 skills 目录即可。不绑定框架,不改你的工作流。

## Features

- 📦 **即拷即用** - 纯 prompt skill 零依赖,clone 下来软链即用
- 🎯 **CC + Codex 通用** - 都是 SKILL.md 格式,两个端都能加载
- 🧪 **实战沉淀** - 每个 skill 都在真实工作流里用过、打磨过,不是 demo
- 🔓 **开源 MIT** - 随便用随便改

## Quickstart

### 方式一:CC plugin marketplace(推荐,`/plugins` 里可见)

本仓库已注册为 Claude Code plugin marketplace。在 Claude Code 会话里:

```
/plugin marketplace add Coder42Y/42Marketplace
/plugin install algo-solver@42marketplace   # 按需逐个装
/reload-plugins
```

装后在 `/plugins` 的 installed marketplace 能看到 `42marketplace`。skill 走 plugin namespace(如 `/algo-solver:...`),也可直接自然语言触发。

### 方式二:standalone 软链(不走 `/plugins`,skill 名短无 namespace)

clone + 软链所有 skill(`${s%/}` 去尾斜杠,避免软链目标带尾斜杠):

**Claude Code:**

```bash
git clone https://github.com/Coder42Y/42Marketplace.git ~/42Marketplace && mkdir -p ~/.claude/skills && for s in ~/42Marketplace/skills/*/; do ln -sf "${s%/}" ~/.claude/skills/; done
```

**Codex:**

```bash
git clone https://github.com/Coder42Y/42Marketplace.git ~/42Marketplace && mkdir -p ~/.codex/skills && for s in ~/42Marketplace/skills/*/; do ln -sf "${s%/}" ~/.codex/skills/; done
```

更新(软链自动跟随):`cd ~/42Marketplace && git pull`

## How it works

每个 skill 是一个 `SKILL.md` 文件(加可选脚本/资源)。软链到 `~/.claude/skills/` 或 `~/.codex/skills/` 后,Claude Code / Codex 在对话中自动识别,根据你的话触发对应 skill。

仓库 clone 在 `~/42Marketplace`,所有 skill 软链过去。更新只要 `cd ~/42Marketplace && git pull`,软链自动跟随最新版本,不用重装。想只装某几个,把 Quickstart 的 `for` 循环换成单独软链 `skills/<name>` 即可。

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
