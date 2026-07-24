# Minimal 极简黑白风格 — 完整设计令牌参考

> 受 Dieter Rams、Swiss Design 和现代极简主义影响，适配小红书卡片使用。

## 设计理念

极简黑白风格的核心是「少即是多」：纯黑白灰配色、细线条分隔、大量留白、字重对比构建层级。没有彩色、没有阴影、没有圆角（或极小圆角）。整体气质是「克制」「高级感」「专业」。

## 色彩令牌

### 基础色

| Token | 色值 | 用途 |
|-------|------|------|
| `--bg-primary` | `#FFFFFF` | 页面主背景 |
| `--bg-surface` | `#FAFAFA` | 次级区域背景 |
| `--bg-elevated` | `#F5F5F5` | 代码块/卡片背景 |
| `--bg-dark` | `#1A1A1A` | 深色反转区域 |
| `--bg-black` | `#000000` | 纯黑区域/CTA |

### 文字色

| Token | 色值 | 用途 |
|-------|------|------|
| `--text-primary` | `#1A1A1A` | 主文字 |
| `--text-secondary` | `#555555` | 副文字 |
| `--text-tertiary` | `#888888` | 辅助说明 |
| `--text-muted` | `#BBBBBB` | 极弱文字 |
| `--text-inverse` | `#FFFFFF` | 深色背景上的白色文字 |

### 强调

极简风格 **不使用彩色**。层级通过以下方式表达：
- 字重对比（300 vs 700）
- 字号对比（10px vs 28px）
- 黑白反转（白底黑字 ↔ 黑底白字）
- 线条粗细（0.5px vs 2px）

### 边框

| Token | 色值 | 用途 |
|-------|------|------|
| `--border` | `#E0E0E0` | 标准边框 |
| `--border-strong` | `#1A1A1A` | 粗边框/强调线 |
| `--border-light` | `#F0F0F0` | 弱分隔 |

## 字体系统

```css
/* 全局 — Helvetica Neue 系统字体栈 */
font-family: "Helvetica Neue", -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;

/* 标题和正文使用同一字体栈，靠字重区分 */

/* 代码 — 等宽 */
font-family: "SF Mono", "Fira Code", Consolas, "PingFang SC", monospace;
```

### 字体排版参数（1080×1440 画布）

| 元素 | 字号 | 字重 | 行高 | 特殊 |
|------|------|------|------|------|
| 大标题 | 72-90px | 700 | 1.1 | letter-spacing: -1px，全大写可选 |
| 小标题 | 38-42px | 600 | 1.3 | letter-spacing: 3px（大写时） |
| 正文 | 34-38px | 300-400 | 1.7 | 细字重是极简风特征 |
| 标签 | 28-32px | 500 | — | letter-spacing: 5px, text-transform: uppercase |
| 代码 | 30-32px | 400 | 1.6 | — |

**极简风特征：** 正文使用 `font-weight: 300`（light），与标题 700 形成强烈对比。

## 组件样式

### 大标题

```css
font-size: 80px;
font-weight: 700;
color: #1A1A1A;
line-height: 1.1;
letter-spacing: -1px;
/* 可选：text-transform: uppercase; letter-spacing: 5px; */
```

### 分类标签

```css
font-size: 28px;
font-weight: 500;
letter-spacing: 5px;
text-transform: uppercase;
color: #888888;
/* 无背景、无边框，纯文字 */
```

### 数字编号（大号装饰）

```css
font-size: 140px;
font-weight: 200;
color: #E0E0E0;
line-height: 1;
/* 超大超轻的数字作为装饰元素 */
```

### 白色卡片

```css
background: #FFFFFF;
border: 1px solid #E0E0E0;
padding: 42px 48px;
/* 无圆角或极小圆角 */
border-radius: 0;  /* 或 4px */
```

### 深色反转卡片

```css
background: #1A1A1A;
color: #FFFFFF;
padding: 42px 48px;
border-radius: 0;
```

### 代码块

```css
font-family: "SF Mono", "Fira Code", Consolas, "PingFang SC", monospace;
font-size: 30px;
color: #1A1A1A;
background: #F5F5F5;
padding: 18px 28px;
border-radius: 0;
border-left: 4px solid #1A1A1A;
```

### 分隔线

```css
/* 细线 */
height: 1px;
background: #E0E0E0;

/* 粗线（标题下） */
height: 4px;
background: #1A1A1A;
width: 90px;  /* 短线装饰 */

/* 全宽分隔 */
height: 1px;
background: #E0E0E0;
```

### 药丸标签

```css
font-size: 28px;
font-weight: 500;
letter-spacing: 3px;
text-transform: uppercase;
color: #1A1A1A;
border: 1px solid #1A1A1A;
border-radius: 0;  /* 方角是极简风特征 */
padding: 8px 28px;
```

### 引用/提示

```css
padding: 36px 48px;
border-left: 4px solid #1A1A1A;
font-size: 34px;
font-weight: 300;
color: #555555;
line-height: 1.7;
font-style: italic;
```

### CTA 按钮

```css
background: #1A1A1A;
color: #FFFFFF;
padding: 24px 56px;
border-radius: 0;
font-size: 30px;
font-weight: 500;
letter-spacing: 4px;
text-transform: uppercase;
```

## 布局原则（1080×1440 画布）

- 卡片内边距：90-108px 左右、85-100px 上下（比其他风格更大，强调留白）
- 元素间距：48-72px（宽松）
- **不用圆角**：border-radius: 0（极简风核心特征）
- **不用阴影**：完全扁平
- **不用渐变**：纯色
- **不用彩色**：仅黑白灰
- 对齐非常严格：所有元素左对齐，网格感强
- 装饰元素极少：只有线条和留白
- 页码使用 `01 / 08` 格式，细字重，靠右对齐
