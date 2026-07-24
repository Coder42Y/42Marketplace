[简体中文](./README.md) | English

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Codex-blue.svg)](#)
[![Type](https://img.shields.io/badge/type-skill%20collection-purple.svg)](#skills)

# 🎯 42 Marketplace

> An open-source skill collection for Claude Code + Codex

## Why 42 Marketplace?

Each skill is a ready-to-use **capability pack** -- it gives your AI a specific skill, triggered by a single phrase. Pure-prompt ones have zero dependencies; scripted ones note their prerequisites. Pick what you need, symlink it into your skills directory, done. No framework lock-in, no workflow rewrite.

A skill is fundamentally a `SKILL.md` file (plus optional scripts/assets), recognized by both Claude Code and Codex. Symlink it into your skills directory and the AI loads it at the right moment -- you just trigger it in natural language.

## Features

- 📦 **Drop-in** - Pure-prompt skills are zero-dependency; clone and symlink
- 🎯 **CC + Codex** - All SKILL.md format, loadable by both Claude Code and Codex
- 🧪 **Battle-tested** - Every skill is used and polished in real workflows, not demos
- 🔓 **MIT** - Use and modify freely

## Quickstart

Clone the repo:

```bash
git clone https://github.com/Coder42Y/42Marketplace.git ~/42Marketplace
```

Symlink the skill you want into Claude Code or Codex (pick as needed, replace `<name>`):

```bash
mkdir -p ~/.claude/skills && ln -s ~/42Marketplace/skills/<name> ~/.claude/skills/<name>
```

```bash
mkdir -p ~/.codex/skills && ln -s ~/42Marketplace/skills/<name> ~/.codex/skills/<name>
```

## Usage

Once installed, trigger a skill in natural language:

```text
"Turn this login idea into a design HTML"             -> design-html
"Explain LeetCode 300, longest increasing subsequence" -> algo-solver
"Make Xiaohongshu cards from this article"            -> xhs-image-gen
"Submit a MR for me"                                  -> submit-gitlab-mr
```

## Skills

- 🎨 [design-html](./skills/design-html/) - Turn an idea into an Anthropic warm-tone design HTML doc
- ✍️ [zhihu-notes](./skills/zhihu-notes/) - Zhihu-style long-form article generator
- 🌺 [elder-blessing-comments](./skills/elder-blessing-comments/) - Elder-style Chinese blessing comments
- 🔀 [submit-gitlab-mr](./skills/submit-gitlab-mr/) - GitLab MR submission (glab CLI)
- 🧮 [algo-solver](./skills/algo-solver/) - Algorithm problem explanation (Python3 + Java)
- 📱 [xhs-image-gen](./skills/xhs-image-gen/) - Xiaohongshu card images `beta`
- 🎯 [daily-pulse](./skills/daily-pulse/) - Daily hot topics push + on-demand query
- 🔍 [deep-repo-research](./skills/deep-repo-research/) - Research GitHub/GitLab repos into structured reports
- 🎬 [vid2report](./skills/vid2report/) - Turn Bilibili/YouTube videos into structured research reports
- 🛡️ [vps-proxy-deploy](https://github.com/Coder42Y/vps-proxy-deploy) - Safely deploy a relay on a VPS (Hysteria2/VLESS etc.) ↗ separate repo

## Contributing

1. Skills go in `skills/<name>/`, standalone tools in `tools/<name>/`
2. Each skill has `SKILL.md` (skill definition) and `README.md` (user docs)
3. Follow the design system in [`DESIGN.md`](./DESIGN.md)

## License

MIT

## Privacy

All published code and docs are sanitized: no personal info, API keys, tokens, or private configs. Personal files are excluded via `.gitignore`.
