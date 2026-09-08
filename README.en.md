<div align="center">

<img src="logo.svg" width="120" alt="42 Marketplace logo">

# 🎯 42 Marketplace

An open-source skill collection for Claude Code, Codex, and pi

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Codex%20%7C%20pi-blue.svg)](#skills)
[![Type](https://img.shields.io/badge/type-skill%20collection-purple.svg)](#skills)

[简体中文](./README.md) ｜ English

</div>

---

## Why 42 Marketplace?

Each skill is a ready-to-use **capability pack**, triggered by a natural-language request. Pure-prompt skills have zero dependencies; scripted skills document their prerequisites. Install only what you need.

Most skills use the shared `SKILL.md` format. Launchers, hooks, and tool integrations may be platform-specific: check each skill's README first.

## Features

- 📦 **Selective installation** — Clone and symlink pure-prompt skills.
- 🎯 **Multiple platforms** — Claude Code, Codex, and pi, with platform-specific skills clearly labeled.
- 🧪 **Practical iteration** — Skill docs state maturity and verification scope; experimental features are labeled.
- 🔓 **MIT** — Use and modify freely.

## Quickstart

### Option 1: Claude Code plugin marketplace

Run inside Claude Code and install plugins individually:

```text
/plugin marketplace add Coder42Y/42Marketplace
/plugin install algo-solver@42marketplace
/reload-plugins
```

Find `42marketplace` in `/plugins` after installation. Skills use plugin namespaces and can also be triggered in natural language.

> `cc-auto-worktree` requires its `scripts/install.sh` after plugin installation. `pi-auto-worktree` is pi-only and is not listed in the CC plugin catalog.

### Option 2: Standalone skills for Claude Code / Codex

Clone once; update an existing checkout instead of cloning again:

```bash
git clone https://github.com/Coder42Y/42Marketplace.git ~/42Marketplace
```

Choose your platform and a compatible skill. Replace `algo-solver` below with the skill you need.

**Claude Code:**

```bash
mkdir -p ~/.claude/skills
ln -s ~/42Marketplace/skills/algo-solver ~/.claude/skills/algo-solver
```

**Codex:**

```bash
mkdir -p ~/.codex/skills
ln -s ~/42Marketplace/skills/algo-solver ~/.codex/skills/algo-solver
```

If the destination exists, inspect it rather than overwriting it. Do not bulk-install platform-specific skills into other agents.

### Option 3: Automatic worktrees for pi

Clone the repository as above, then install the pi launcher, skill, and naming extension:

```bash
bash ~/42Marketplace/skills/pi-auto-worktree/scripts/install.sh
export PATH="$HOME/.local/bin:$PATH"
hash -r
```

Run `pi` from your main Git checkout. Non-Git directories are strictly skipped. See [pi-auto-worktree](./skills/pi-auto-worktree/) for prerequisites, naming, and session recovery.

### Updates

```bash
git -C ~/42Marketplace pull --ff-only
```

The standalone installations above use symlinks and follow source updates. Restart the relevant agent to load changes. Update CC plugin installations through the plugin manager instead.

## How it works

A skill contains `SKILL.md` plus optional scripts and assets. Agents discover skills and load their instructions on demand.

Ordinary skills can be symlinked directly; platform-specific features may require setup. For example, `cc-auto-worktree` registers a Claude Code hook, while `pi-auto-worktree` creates and enters a worktree before launching pi. They are not interchangeable.

## Usage

After installation, use natural-language requests:

```text
“Turn this login idea into a design HTML”             → design-html
“Explain LeetCode 300, longest increasing subsequence” → algo-solver
“Make Xiaohongshu cards from this article”            → xhs-image-gen
“Submit an MR for me”                                → submit-gitlab-mr
```

## Skills

### Platform-specific

- 🌳 [cc-auto-worktree](./skills/cc-auto-worktree/) — **Claude Code only**: enter an isolated worktree in new sessions; run its installer after adding the skill.
- 🌱 [pi-auto-worktree](./skills/pi-auto-worktree/) — **pi only**: isolate before startup, name the branch and session from the first task, skip non-Git directories, and keep directory paths stable. `beta`

### General skills and tool integrations

A shared format does not mean zero dependencies. Check each skill's README for compatibility and prerequisites.

- 🎨 [design-html](./skills/design-html/) — Turn an idea into an Anthropic warm-tone design HTML document.
- ✍️ [zhihu-notes](./skills/zhihu-notes/) — Generate Zhihu-style long-form articles.
- 🌺 [elder-blessing-comments](./skills/elder-blessing-comments/) — Generate elder-style Chinese blessing comments.
- 🔀 [submit-gitlab-mr](./skills/submit-gitlab-mr/) — Submit GitLab merge requests with glab CLI.
- 🧮 [algo-solver](./skills/algo-solver/) — Explain algorithms with Python 3 and Java solutions.
- 📱 [xhs-image-gen](./skills/xhs-image-gen/) — Generate Xiaohongshu image cards. `beta`
- 🎯 [daily-pulse](./skills/daily-pulse/) — Daily hot topics and on-demand queries.
- 🔍 [deep-repo-research](./skills/deep-repo-research/) — Research GitHub / GitLab repositories into structured reports.
- 📝 [ntn-todo](./skills/ntn-todo/) — Manage Notion tasks and weekly progress, with guided first-time setup.
- 🎬 [vid2report](./skills/vid2report/) — Turn Bilibili / YouTube videos into structured research reports.

### Separate repositories

- 🛡️ [vps-proxy-deploy](https://github.com/Coder42Y/vps-proxy-deploy) — Safely deploy a relay on a VPS, including Hysteria2 / VLESS.

## Contributing

1. Place skills in `skills/<name>/` and standalone tools in `tools/<name>/`.
2. Include `SKILL.md` (agent instructions) and `README.md` (user documentation) for each skill.
3. Follow [`DESIGN.md`](./DESIGN.md) and document platforms, dependencies, and verification scope.

## License

[MIT](./LICENSE)

## Privacy

Published code and docs should not contain personal information, API keys, tokens, passwords, or private configuration. Review and sanitize before committing; exclude personal files with `.gitignore`.
