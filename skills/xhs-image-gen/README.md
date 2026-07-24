# 📱 xhs-image-gen

> 把文案/文章/主题转成 1-10 张小红书风格 PNG 卡片,3 种风格可选。HTML 是中间产物,最终交付 PNG。

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `beta` |
| **兼容** | `Claude Code`, `Codex` |
| **License** | MIT |

## Why

把长文、笔记或一个主题词,直接做成 1-10 张小红书风格图文卡片,免去排版、裁图、加标签的重复劳动。HTML 是中间产物,真正的成品是 PNG,传图就能发。

适合技术博主、知识分享、读书笔记、产品种草等场景 —— 一句"做小红书图"就能拿到可上传的素材。

## Features

- **3 种风格** — `anthropic`(暖米色 + 衬线 + 赤陶橙)/ `notion`(白底 + 图标化 + 扁平)/ `minimal`(纯黑白灰 + 零圆角)
- **4 种布局** — `sparse` 疏朗型 / `balanced` 均衡型 / `list` 列表型 / `flow` 流程型
- **批量产出** — 一次生成 1-10 张卡片(短文 1-2 张 / 中等 3-5 张 / 长文 5-10 张)
- **Playwright 截图** — `scripts/screenshot.js` 批量 HTML → PNG,支持 `--clean` 自动清理中间 HTML
- **3 种比例** — 默认 3:4 竖版(1080×1440),可选 1:1 方形 / 4:3 横版

## Quickstart

```bash
# 1. 软链到对应 agent 的 skills 目录(选一个)
ln -s $(pwd)/skills/xhs-image-gen ~/.claude/skills/xhs-image-gen     # Claude Code
ln -s $(pwd)/skills/xhs-image-gen ~/.codex/skills/xhs-image-gen       # Codex

# 2. 首次安装依赖(Node 依赖 + chromium 浏览器)
cd skills/xhs-image-gen/scripts && npm install && npx playwright install chromium

# 3. 在 Claude Code / Codex 对话里直接说
"把这篇文章生成小红书图文,用 anthropic 风格"
"做 3 个职场沟通技巧的小红书图片,notion 风"
```

跑完会在工作目录得到 N 张 PNG + 1 份 `小红书文案.md`,直接传图发笔记。

## Usage

**风格选择**

| 内容类型 | 推荐风格 |
|:---|:---|
| 技术 / AI / 产品 / 教程 | `anthropic` |
| 知识 / 职场 / 效率 / 笔记 | `notion` |
| 商务 / 科技 / 设计 | `minimal` |

**布局选择**

| 内容类型 | 推荐布局 |
|:---|:---|
| 列举型内容 | `list` |
| 步骤 / 教程 | `flow` 或 `list` |
| 故事 / 情感 | `sparse` 或 `balanced` |

**示例**

```
"把 posts/ai-future.md 做成小红书卡片,用 anthropic 风格,flow 布局"
"用 notion 风格生成 3 个职场沟通技巧的小红书图片"
"极简风格做一组小红书封面,内容是 content.txt"
```

**手动截图(脚本直调)**

```bash
node scripts/screenshot.js xhs_card_*.html --clean
# --output-dir <dir>    指定 PNG 输出目录
# --clean               截图后自动删除中间 HTML
```

## 前置依赖

- **Node.js** >= 18
- **Playwright** + chromium —— 首次按 Quickstart 第 2 步安装(`npm install` + `npx playwright install chromium`)

## License

MIT
