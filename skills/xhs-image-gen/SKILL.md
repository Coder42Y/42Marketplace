---
name: xhs-image-gen
description: >
  This skill should be used when the user asks to generate Xiaohongshu/RedNote
  visual cards, such as "生成小红书图文", "小红书卡片", "小红书图片", "小红书封面",
  "做小红书图", "XHS cards", "RedNote images", or wants to convert text, articles,
  or topics into styled HTML card images for social media posting.
---

# 小红书图文卡片生成器

将文案、文章或主题内容转化为 1-10 张小红书风格的图文卡片（PNG 图片）。

HTML 是中间产物，最终交付物是 PNG 图片。

## 工作流

### Step 1：解析输入

**支持以下输入形式：**
- 文件路径：读取文件内容（markdown、txt、文章）
- Obsidian URL：解析 `obsidian://open?vault=...&file=...` 链接，定位到实际文件路径
- 直接文案：用户直接输入文字内容
- 主题词：如「今日星座运势」，根据主题自行发挥内容

**参数解析：**
- `--style <风格名>` 指定视觉风格（见风格列表）
- `--layout <布局名>` 指定布局方式（见布局列表）
- `--ratio <比例>` 指定图片比例（见下方尺寸规范，默认 `3:4`）
- 无参数时，根据内容智能选择最适合的风格和布局

### Step 2：内容规划

将内容分解为 1-10 个卡片，每张卡片对应一个核心点：
- **第 1 张**：封面卡（标题 + 副标题 + 吸睛元素）
- **中间张**：内容卡（每张聚焦 1 个核心观点）
- **最后 1 张**（可选）：总结/行动卡

**分卡原则：**
- 内容短（200字内）→ 1-2 张
- 内容中等（500字内）→ 3-5 张
- 内容长（500字以上）→ 5-10 张
- 保持每张卡片信息量适中，避免文字过密

### Step 3：生成 HTML（中间产物）

为每张卡片生成一个独立 HTML 文件，命名为 `xhs_card_01.html`、`xhs_card_02.html`……

> HTML 文件是中间缓存，不是最终交付物。

**卡片尺寸规范（小红书平台标准）：**

| 比例 | 尺寸 | 说明 |
|------|------|------|
| **3:4 竖版**（默认） | 1080×1440px | 推荐，占屏面积最大 |
| 1:1 方形 | 1080×1080px | 产品展示/文字配图 |
| 4:3 横版 | 1200×900px | 风景/全景 |

> 小红书整篇笔记只支持一种图片比例，默认使用 3:4 竖版。

**排版注意：**
- 所有字号、间距参数按 1080px 宽度画布设计
- 具体数值因风格而异，生成前务必读取对应的 `references/style-*.md`

**生成要求：**
1. 使用选定的风格和布局（读取对应的 `references/style-*.md` 获取完整设计令牌）
2. 所有样式内联（`<style>` 标签内）
3. 使用 emoji 增加活泼感
4. 包含小红书常见元素：话题标签、互动引导语

### Step 4：截图生成 PNG 图片（最终交付物）

执行本 skill 目录下的 `scripts/screenshot.js` 将所有 HTML 批量转为 PNG。

> **路径说明：** 本 skill 的根目录即包含此 SKILL.md 的目录。所有相对路径（`scripts/`、`references/`、`examples/`）均相对于此目录。

**首次使用需安装依赖：**
```bash
cd {skill-root}/scripts && npm install && npx playwright install chromium
```

**截图命令：**
```bash
node {skill-root}/scripts/screenshot.js <output-dir>/xhs_card_*.html --clean
```

其中 `{skill-root}` 为本 SKILL.md 所在目录的绝对路径。

**脚本行为：**
- 自动检测每个 HTML 的画布尺寸（从 body 的 width/height）
- 并行处理所有文件
- 输出同名 .png 到同目录
- 加 `--clean` 自动删除中间 HTML
- 加 `--output-dir <dir>` 可指定 PNG 输出目录

**清理：** 截图完成后删除中间 HTML 文件（仅保留 PNG）。

### Step 5：生成小红书文案

在 PNG 输出目录下生成 `小红书文案.md`，包含发布时所需的文字内容：

```markdown
# <吸睛标题>

<正文：概括内容要点，适合小红书阅读节奏，分段简短>

---

#标签1 #标签2 #标签3 ...
```

**文案要求：**
- **标题**：一行，带竖线或 emoji 分隔，吸引点击（如「Claude Code 安装指南｜国产大模型也能跑」）
- **正文**：提炼卡片核心内容，口语化，分段短小，适合手机阅读
- **推荐标签**：10-15 个相关话题标签，覆盖主题词、工具名、领域词

### Step 6：交付

告知用户：
1. 共生成了几张 PNG 图片和 1 个文案文件，列出完整文件路径
2. 图片可直接上传到小红书，文案复制到标题和正文区
3. 可用 `--style` 和 `--layout` 参数重新生成不同风格

---

## 风格（Style）列表

| 风格名 | 中文名 | 适合内容 | 设计参考 |
|--------|--------|----------|---------|
| `anthropic` | Anthropic 官网风 | 技术、AI、产品、教程 | 暖米色底 + 衬线标题 + 赤陶橙强调 |
| `notion` | Notion 风 | 笔记、学习、效率、职场 | 白底 + 无衬线 + 图标化列表 + 扁平 |
| `minimal` | 极简黑白 | 商务、设计、科技 | 纯黑白灰 + 细线条 + 大留白 + 零圆角 |

**默认选择逻辑：**
- 技术/AI/产品/教程类 → `anthropic`
- 知识/职场/效率类 → `notion`
- 商务/科技/设计类 → `minimal`

每种风格的完整设计令牌（色彩、字体、组件样式、布局参数）见对应的 `references/style-*.md` 文件。

---

## 布局（Layout）列表

| 布局名 | 中文名 | 特点 |
|--------|--------|------|
| `sparse` | 疏朗型 | 大留白，重点突出，视觉轻松 |
| `balanced` | 均衡型 | 图文平衡，标准卡片布局 |
| `list` | 列表型 | 竖向列举，步骤感强 |
| `flow` | 流程型 | 上下流程图感，适合教程步骤 |

**默认选择逻辑：**
- 列举型内容 → `list`
- 步骤/教程类 → `flow` 或 `list`
- 故事/情感类 → `sparse` 或 `balanced`

---

## 卡片必含元素

**封面卡（第 1 张）：**
- 醒目大标题（主要内容/吸引眼球的钩子）
- 1-2 行副标题或摘要
- 装饰性 emoji 或图形元素
- 底部页码（如 `01 / 08`）和提示语

**内容卡（中间张）：**
- 顶部：左侧分类标签 + 右侧页码
- 小标题 + 正文内容
- 适量 emoji 点缀
- 分隔线或图形装饰

**总结卡（最后 1 张，可选）：**
- 核心要点总结（3 条以内）
- 互动引导语（如「你有什么想法？评论区聊聊 →」）
- 话题标签（如 `#主题 #生活分享`）

---

## 示例用法

- "帮我把这篇文章生成小红书图文" + 粘贴文章内容
- "把 posts/ai-future.md 做成小红书卡片，用 anthropic 风格，flow 布局"
- "用 notion 风格生成3个职场沟通技巧的小红书图片"
- "极简风格做一组小红书封面，内容是 content.txt"

---

## 参考资源

### 风格设计令牌

生成卡片前，读取对应风格文件获取完整的色彩、字体、组件和布局规范：

- **`references/style-anthropic.md`** — 暖米色 + 衬线标题 + 赤陶橙，editorial 风格
- **`references/style-notion.md`** — 白底 + 图标化 + 属性行，结构化风格
- **`references/style-minimal.md`** — 纯黑白灰 + 细线条 + 零圆角，极简风格

### 截图脚本

- **`scripts/screenshot.js`** — Playwright 批量截图脚本，将 HTML 转为 PNG
- 首次使用：`cd {skill-root}/scripts && npm install && npx playwright install chromium`
- 用法：`node {skill-root}/scripts/screenshot.js xhs_card_*.html [--clean] [--output-dir <dir>]`

### 示例输出

- **`examples/sample_cover_anthropic.html`** — Anthropic 风格封面卡示例，用浏览器打开查看预期效果
