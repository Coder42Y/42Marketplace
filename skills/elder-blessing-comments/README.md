# 🌺 elder-blessing-comments

> 生成长辈风社交媒体祝福评论:抖音/微信群/朋友圈一键复制,emoji 拉满,土味祝福。

![version](https://img.shields.io/badge/version-v0.1.0-blue) ![status](https://img.shields.io/badge/status-stable-brightgreen) ![license](https://img.shields.io/badge/license-MIT-green) ![compat](https://img.shields.io/badge/compat-Claude%20Code%20%7C%20Codex-purple)

## Why

家族群、抖音评论区、朋友圈点赞,长辈爱发的那类祝福文案有固定配方:大量 🌹🙏☀️、对仗短句、真诚土味。手动凑既慢又容易写得不地道,这条 skill 把"长辈味配方"沉淀成可复用的 prompt,直接产出可复制粘贴的中文祝福。

## Features

- **emoji 拉满** — 每个 emoji 至少出现 3 次,绝不出现落单 emoji。
- **三档浓度** — 轻度长辈味 / 标准长辈味 / 爆改复制粘贴风,按"越土越好"逐级加码。
- **多场景模板** — 早上好、平安健康、发财好运、美女/帅哥评论、家族群整段复制。
- **复制即用** — 单行短评 / 多行块状,直接 Ctrl+C 进抖音/微信。
- **真诚不冒犯** — 走"可爱长辈"路线,不做年龄歧视、不夹带迷信话术。

## Quickstart

### 安装(软链,Claude Code / Codex 通用)

```bash
# Claude Code
ln -s $(pwd)/skills/elder-blessing-comments ~/.claude/skills/elder-blessing-comments

# Codex(按本地实际路径调整)
ln -s $(pwd)/skills/elder-blessing-comments ~/.codex/skills/elder-blessing-comments
```

> 依赖:无。纯 prompt skill,无需安装额外包。

### 触发

```text
"来点长辈风祝福语,早上的"
"帮我写几条抖音评论,越土越好"
"整段家族群复制粘贴的"
"给这条朋友圈写个长辈风点赞评论"
```

## Usage

| 你说 | 产出 |
|---|---|
| 早上好 | 太阳+茶+花+健康+好心情短句 |
| 美女/帅哥评论 | 夸赞+祝福+玫瑰+👍 组合 |
| 发财好运 | 💰 + 🍀 + 财源广进模板 |
| 家族群 | 多行块状,直接整段转发 |
| 抖音评论 | 短促有力,👍🌹🙏 三件套 |
| 越土越好 | 提高重复度+对仗+emoji 密度 |

### 示例输出

**单行短评**

```text
早上好🌞🌹新的一天开始啦,愿你开心快乐每一天,身体健康,万事如意🙏🌺🌺🌺
```

**家族群块状**

```text
🌹🌹🌹祝福送到🌹🌹🌹
身体健康🙏🙏🙏
家庭幸福🏠🏠🏠
财源广进💰💰💰
好运连连🍀🍀🍀
天天开心😄😄😄
万事如意🎉🎉🎉
```

**美女/帅哥评论**

```text
美女真漂亮🌹🌹气质优雅,笑容甜美,祝你青春永驻,幸福快乐每一天💖🌺👍👍👍
```

### 关键规则

- **每个 emoji 至少出现 3 次**(硬规则,出现单个 emoji 即不合格)。
- 默认中文回复;默认一次给 20 条;默认可直接复制粘贴。
- 不做:正式贺卡、商业文案、严肃慰问、年轻/极简风格。

## License

MIT
