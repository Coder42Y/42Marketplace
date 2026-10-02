# 🎨 design-html

> 把 idea/方案沉淀成暖白底克制风的设计说明 HTML —— 讲思路不堆代码,多图少字,数据用图表说话,手机可读。

| | |
|:---|:---|
| **版本** | `v0.5.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `Codex` |
| **License** | `MIT` |
| **最近更新** | `2026-10-02` |

---

## Why

刚和同事聊完一个架构、领导聊完一个方案、自己想清楚一个 idea,需要一份能直接发出去、打开就能看的说明文档 —— 但又不想堆代码、写 Markdown 又不够直观。`design-html` 把对话沉淀成一份带多张图、暖白底克制排版的独立 HTML 文件,讲清"为什么这么选",而不是"代码怎么写"。

## Features

- **只管输出质量**:不规定推理流程和章节骨架,内容怎么组织由模型按内容判断。
- **多图少字**:结构、流向、对比能画就画,整体架构图是底线;走线不穿卡片、一色一义、同级来源汇流成一个箭头。
- **数据图与对比表**:图标题写结论、灰字写口径;直接标注代替图例,同一实体各图同色,主角深色、旧版同色系浅色;对比表推荐列打框、每行最优高亮。配色经过色弱和对比度校验。
- **渲染脚本**:模型只写图表数据(JSON),`scripts/build.py` 负责坐标、刻度、标签避让、手机布局和截图自检。同一份素材的 A/B 测试里,生成时间中位数少约 35%,事实错误和手机端观感都优于手写。
- **克制排版**:暖白底 + 单一强调色,全文无渐变;大标题用 `项目-主题-文档类型` 这类名词短语,不写口语。
- **移动端可读**:375px 下页面整体不横滑;柱子多时手机上自动改横向,宽示意图换纵向版本,对比表带滑动提示。
- **交付前自检**:`build.py --shot` 一条命令出桌面 + 手机截图并检查手机宽度,亲眼看过再交付。

## Quickstart

```bash
# 1. 软链到 skills 目录(Claude Code)
ln -s $(pwd)/skills/design-html ~/.claude/skills/design-html

# 2. Codex 用户:把整个 skills 目录软链到 ~/.codex/skills/
```

触发(在 Claude Code / Codex 对话中):

> "帮我把刚聊的登录方案沉淀成设计 HTML"
> "出个说明文档,讲讲这个架构怎么选的"
> "把刚才的 idea 整理成设计页"

输出:`./design.html` —— 双击即可在浏览器打开。源文件 `design.src.html` 留在同目录,改完重新运行 `python3 scripts/build.py design.src.html` 即可。

## Usage

**典型场景**

- 架构方案评审:`"把我们刚定的多 Agent 调度架构出个设计说明"`
- idea 备忘:`"把今天想的 XX 沉淀一下,带架构图"`
- 方案交付:`"做个设计 HTML 给我发给领导"`
- 复盘文档:`"把这个迭代的设计决策整理成 HTML"`

**画图方式**:示意图内联 SVG 手绘,太复杂时改用 drawio 导出 SVG 嵌入;数据图和对比表写成 JSON 数据块,由 `scripts/build.py` 渲染。格式见 `references/chart-spec.md`,示例见 `references/chart-sample.src.html`。

**典型产物结构**

```
.
├── design.src.html     # 源文件:正文 + 手绘示意图 + 图表数据
├── design.html         # 构建产物(双击打开,发这个)
└── architecture.drawio # drawio 源(若用 drawio)
```

## 依赖

- **python3**(3.7+,只用标准库):运行 `scripts/build.py`
- **Google Chrome / Chromium**(可选):`--shot` 截图自检用;没有就跳过截图

生成的 `design.html` 所有 CSS/SVG 内联,双击可打开,不依赖任何东西。

> 可选:若用 drawio 画架构图,需另装 drawio CLI;默认用纯 SVG 手绘。

## License

MIT
