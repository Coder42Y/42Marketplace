# 📱 xhs-image-gen

> 小红书图文卡片生成器

| | |
|:---|:---|
| **版本** | `v0.1.0` |
| **状态** | `beta` |
| **兼容** | `Claude Code`, `Codex` |
| **最近更新** | `2026-07-24` |

**一句话:**把文案/文章/主题转成 1-10 张小红书风格 PNG 卡片,3 种风格(anthropic/notion/minimal),HTML 是中间产物,最终交付 PNG。

---

## 前置依赖

- **Node.js** >= 18
- **Playwright** + chromium(首次按下面命令安装)

## 快速开始

```bash
# 1. 激活
ln -s $(pwd)/skills/xhs-image-gen ~/.claude/skills/xhs-image-gen

# 2. 首次安装依赖
cd skills/xhs-image-gen/scripts && npm install && npx playwright install chromium

# 3. 触发
"把这篇文章生成小红书图文,用 anthropic 风格"
"做3个职场沟通技巧的小红书图片,notion 风"
```

## 脚本

- `scripts/screenshot.js` -- Playwright 批量截图,HTML -> PNG
  - 用法:`node scripts/screenshot.js xhs_card_*.html [--clean] [--output-dir <dir>]`

## 风格

- `references/style-anthropic.md` -- 暖米色 + 衬线 + 赤陶橙
- `references/style-notion.md` -- 白底 + 图标化 + 扁平
- `references/style-minimal.md` -- 纯黑白灰 + 零圆角

`examples/sample_cover_anthropic.html` 是示例封面卡,浏览器打开查看预期效果。

> 状态为 beta:依赖 Playwright + chromium,安装较重。功能已验证可用,后续补完整测试。
