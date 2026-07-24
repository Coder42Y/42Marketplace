# Notion 风格 — 完整设计令牌参考

> 模仿 Notion 的界面设计语言，适配小红书卡片使用。

## 设计理念

Notion 风格强调「结构化」和「可读性」：白色干净背景、无衬线字体、图标化列表、卡片嵌套感。整体气质是「条理清晰」「轻量专业」。

## 色彩令牌

### 基础色

| Token | 色值 | 用途 |
|-------|------|------|
| `--bg-primary` | `#FFFFFF` | 页面主背景 |
| `--bg-surface` | `#F7F6F3` | 卡片/嵌套区域背景 |
| `--bg-elevated` | `#F1F0EE` | 代码块/高亮区域 |
| `--bg-hover` | `#E8E7E4` | 悬浮/激活态 |
| `--bg-accent` | `#E8F0FE` | 蓝色强调区域（浅蓝） |

### 文字色

| Token | 色值 | 用途 |
|-------|------|------|
| `--text-primary` | `#37352F` | 主文字（Notion 特征暖黑） |
| `--text-secondary` | `#6B6B6B` | 副文字 |
| `--text-tertiary` | `#9B9A97` | 辅助/占位符 |
| `--text-muted` | `#B4B4B0` | 极弱文字（页码、时间戳） |

### 强调色

| Token | 色值 | 用途 |
|-------|------|------|
| `--accent-blue` | `#2383E2` | 链接/主强调 |
| `--accent-red` | `#EB5757` | 重要标记 |
| `--accent-orange` | `#E9730C` | 次要强调/标签 |
| `--accent-green` | `#0F7B6C` | 成功/完成状态 |
| `--accent-purple` | `#9065B0` | 分类标签 |

### 内联高亮背景色

| Token | 色值 | 用途 |
|-------|------|------|
| `--highlight-yellow` | `rgba(255,212,0,0.14)` | 黄色高亮 |
| `--highlight-blue` | `rgba(35,131,226,0.14)` | 蓝色高亮 |
| `--highlight-pink` | `rgba(245,93,116,0.13)` | 粉色高亮 |
| `--highlight-gray` | `rgba(140,140,140,0.12)` | 灰色高亮 |

### 边框

| Token | 色值 | 用途 |
|-------|------|------|
| `--border` | `#E0E0E0` | 标准边框 |
| `--border-light` | `#EBEBEA` | 弱分隔线 |
| `--divider` | `#E9E9E7` | 水平分隔 |

## 字体系统

```css
/* 正文 — Notion 使用系统无衬线字体 */
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;

/* 标题 — 同正文，靠字号和字重区分层级 */
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;

/* 代码 — 等宽字体 */
font-family: "SFMono-Regular", "SF Mono", Menlo, Consolas, "PingFang SC", monospace;
```

### 字体排版参数（1080×1440 画布）

| 元素 | 字号 | 字重 | 行高 |
|------|------|------|------|
| 大标题（H1） | 72-84px | 700 | 1.2 |
| 小标题（H2/H3） | 42-48px | 600 | 1.3 |
| 正文 | 36-40px | 400 | 1.65 |
| 辅助文字 | 30-34px | 400 | 1.5 |
| 标签/属性名 | 28-32px | 500 | — |
| 代码 | 32-34px | 400 | 1.6 |

## 组件样式

### 页面标题

```css
font-size: 76px;
font-weight: 700;
color: #37352F;
line-height: 1.2;
/* 无衬线，纯靠字重和字号突出 */
```

### 属性行（Property Row）

```css
display: flex;
align-items: center;
gap: 24px;
padding: 12px 0;
border-bottom: 1px solid #EBEBEA;
```

```css
/* 属性名 */
font-size: 30px;
color: #9B9A97;
font-weight: 500;
min-width: 240px;
```

```css
/* 属性值 */
font-size: 34px;
color: #37352F;
font-weight: 400;
```

### 标签（Tag/Badge）

```css
font-size: 30px;
font-weight: 500;
padding: 6px 24px;
border-radius: 8px;
/* 根据颜色选择对应的 highlight 背景 */
background: rgba(35,131,226,0.14);
color: #2383E2;
```

### 列表项（带图标）

```css
display: flex;
align-items: flex-start;
gap: 24px;
padding: 18px 0;
```

```css
/* 列表图标（emoji 或符号） */
width: 56px;
font-size: 40px;
text-align: center;
flex-shrink: 0;
```

### 切换块/折叠块

```css
background: #F7F6F3;
border-radius: 10px;
padding: 28px 36px;
```

### 代码块

```css
font-family: "SFMono-Regular", Menlo, Consolas, "PingFang SC", monospace;
font-size: 32px;
color: #37352F;
background: #F7F6F3;
border-radius: 10px;
padding: 24px 36px;
line-height: 1.6;
```

### 行内代码

```css
font-family: "SFMono-Regular", Menlo, Consolas, "PingFang SC", monospace;
font-size: 32px;
color: #EB5757;
background: rgba(135,131,120,0.15);
border-radius: 8px;
padding: 3px 12px;
```

### 引用块（Callout）

```css
display: flex;
gap: 28px;
padding: 36px 42px;
background: #F7F6F3;
border-radius: 10px;
```

```css
/* 引用图标 */
font-size: 52px;
flex-shrink: 0;
```

### 分隔线

```css
height: 1px;
background: #E9E9E7;
margin: 24px 0;
```

## 布局原则（1080×1440 画布）

- 卡片内边距：72-96px 左右、70-85px 上下
- 元素间距：24-42px
- Notion 不使用大量留白，而是靠 **紧凑但有节奏** 的间距
- 圆角较小：8-10px（标签/代码块），不用大圆角
- 无阴影——Notion 风格完全扁平
- 层级靠 **背景色递进** 区分：白色 → #F7F6F3 → #F1F0EE
- 图标（emoji）作为列表前缀是核心视觉元素
