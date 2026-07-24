# Anthropic 风格 — 完整设计令牌参考

> 提取自 https://www.anthropic.com/ 官网设计语言，适配小红书卡片使用。

## 设计理念

Anthropic 官网采用温暖的 editorial（编辑/杂志）风格：大量留白、衬线标题、暖色调米色背景、赤陶橙强调色。整体气质是「严肃但温暖」「专业但不冰冷」。

## 色彩令牌

### 基础色

| Token | 色值 | 用途 |
|-------|------|------|
| `--bg-primary` | `#FAF7F2` | 页面主背景（暖奶油色） |
| `--bg-surface` | `#FFFFFF` | 卡片/面板表面 |
| `--bg-elevated` | `#F5F0E8` | 代码块/提升区域背景 |
| `--bg-accent` | `#FDF2EC` | 强调区域背景（浅橙） |
| `--bg-cta` | `#1C1917` | CTA/深色区域背景 |

### 文字色

| Token | 色值 | 用途 |
|-------|------|------|
| `--text-primary` | `#1C1917` | 主文字（暖黑） |
| `--text-secondary` | `#57534E` | 副文字 |
| `--text-tertiary` | `#78716C` | 辅助说明文字 |
| `--text-muted` | `#A8A29E` | 极弱文字（页码、标签） |

### 强调色

| Token | 色值 | 用途 |
|-------|------|------|
| `--accent` | `#CC4B24` | 主强调（赤陶橙） |
| `--accent-dark` | `#9A3412` | 深强调（代码/标签内文字） |
| `--accent-bg` | `rgba(204,75,36,0.08)` | 强调背景 |
| `--accent-border` | `rgba(204,75,36,0.2)` | 强调边框 |

### 辅助功能色

| Token | 色值 | 用途 |
|-------|------|------|
| `--green` | `#0F766E` | 成功/正面标签 |
| `--green-bg` | `rgba(15,118,110,0.07)` | 绿色背景 |
| `--purple` | `#7C3AED` | 次要标签 |
| `--purple-bg` | `rgba(124,58,237,0.07)` | 紫色背景 |

### 边框

| Token | 色值 | 用途 |
|-------|------|------|
| `--border` | `#E7DDD0` | 标准边框（暖灰） |
| `--border-light` | `#F0EBE3` | 弱分隔线 |

## 字体系统

### 中英文混排优化字体栈

```css
/* 标题 — Editorial 衬线，英文 Georgia + 中文系统字体 */
font-family: Georgia, "Times New Roman", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", serif;

/* 正文 — 系统无衬线，中英文统一 */
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;

/* 代码 — 等宽字体，中文回落到 PingFang */
font-family: "SF Mono", "Fira Code", Consolas, "PingFang SC", monospace;
```

### 字体排版参数（1080×1440 画布）

| 元素 | 字号 | 字重 | 行高 | 间距 |
|------|------|------|------|------|
| 大标题 | 72-90px | 700 | 1.15-1.2 | letter-spacing: -0.8px |
| 斜体强调 | 同大标题 | 700 italic | — | — |
| 小标题 | 42-48px | 600 | 1.35 | — |
| 正文 | 36-40px | 400 | 1.65-1.7 | — |
| 辅助文字 | 30-34px | 400-500 | 1.55 | — |
| 标签/页码 | 28-32px | 500-600 | — | letter-spacing: 3-4px |
| 代码 | 30-32px | 400 | 1.7-1.8 | — |

## 组件样式

### 标签（Label）

```css
font-size: 30px;
font-weight: 600;
letter-spacing: 4px;
text-transform: uppercase;
color: #CC4B24;
display: flex;
align-items: center;
gap: 16px;
/* 前置圆点 */
::before { width: 16px; height: 16px; border-radius: 50%; background: #CC4B24; }
```

### 药丸标签（Pill）

```css
font-size: 30px;
color: #78716C;
border: 1px solid #E7DDD0;
border-radius: 56px;
padding: 12px 32px;
background: #FFFFFF;
```

### 白色卡片

```css
background: #FFFFFF;
border: 1px solid #E7DDD0;
border-radius: 22px;
padding: 36px 42px;
```

### 强调卡片

```css
background: #FDF2EC;
border: 1px solid rgba(204,75,36,0.25);
border-radius: 22px;
padding: 36px 42px;
```

### 代码块

```css
font-family: "SF Mono", "Fira Code", Consolas, "PingFang SC", monospace;
font-size: 30px;
color: #44403C;
background: #F5F0E8;
border-radius: 12px;
padding: 14px 24px;
```

### 强调代码（inline）

```css
font-family: "SF Mono", "Fira Code", Consolas, "PingFang SC", monospace;
font-size: 30px;
color: #CC4B24;
background: #FDF2EC;
border-radius: 8px;
padding: 3px 12px;
```

### 左侧强调栏（Callout）

```css
background: #FDF2EC;
border-left: 8px solid #CC4B24;
padding: 36px 42px;
border-radius: 0 16px 16px 0;
```

### 步骤编号

```css
width: 72px;
height: 72px;
border-radius: 50%;
border: 3px solid #CC4B24;
color: #CC4B24;
font-size: 32px;
font-weight: 700;
display: flex;
align-items: center;
justify-content: center;
background: #FAF7F2;
```

### CTA 区域（深色底部）

```css
background: #1C1917;
border-radius: 28px;
padding: 42px 48px;
/* 内部文字 */
color: #FAF7F2;
font-family: Georgia, serif;
font-style: italic;
```

### 分隔线

```css
/* 短装饰线 */
width: 100px;
height: 4px;
background: #CC4B24;

/* 完整分隔 */
height: 1px;
background: #E7DDD0;

/* 弱分隔 */
border-bottom: 1px solid #F0EBE3;
```

## 页码/进度

```css
font-size: 30px;
color: #A8A29E;
letter-spacing: 3px;
font-weight: 500;
/* 格式：01 / 08 */
```

## 布局原则（1080×1440 画布）

- 卡片内边距：80-100px 左右、80-90px 上下
- 元素间距：使用 flexbox gap，36-56px 为常见间距
- 文字段落间距：44-56px
- 边框圆角：22px（卡片）、56px（药丸）、12px（代码块）
- 大量留白，不要塞满——空间本身就是设计元素
