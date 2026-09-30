# design-html 渲染脚本 设计

> 日期:2026-09-30 · 分支:`claude/design-html-charts-fcf71f`(并入 PR #15)

## 目标

把 design-html 里「每次都一样」的工作从模型手里拿走,交给脚本,缩短生成时间。

- 现状(v0.4 实测,同一份素材):约 12 分钟、26 次工具调用、约 15.5 万 token
- 耗时主要在:每次重写约 150 行 CSS、手算柱高/误差线/折线坐标/标签避让、截图发现错位后返工 2–3 轮
- 成功标准:同一份素材再跑一次,时间和 token 明显下降(预期 30–50%,以实测为准),图表质量不低于 v0.4

**不做**:架构图、流程图不预设,仍然手绘 SVG,因为每张图的结构都不同。

## 工作方式

```
模型写 design.src.html           python3 scripts/build.py design.src.html --shot
(正文 + 手绘示意图 + 图表 JSON)  ─────────────────────────────────────────────▶  design.html
                                   ① 套文档骨架,内联 assets/base.css              + desktop.png
                                   ② 把每个图表 JSON 渲染成静态 HTML/SVG          + mobile.png
                                   ③ 校验(实体名、必填字段、无 gradient)          + 输出 sw=375
                                   ④ --shot 时截桌面和手机图、量 scrollWidth
```

- `design.src.html` 只写 `<main>` 里面的内容,不写 `<head>`、不写基础 CSS。需要少量额外样式时,可以写一个 `<style>`,脚本会把它放到基础 CSS 后面
- 输出仍是单个静态 `design.html`,打开时不依赖 JS
- 只用 Python 3 标准库(json、re、html、math、subprocess),本机和 42 服务器都能跑

## 图表数据格式

图表写成 `<script type="application/json" data-chart="类型">…</script>`,放在正文中要出现的位置。共五种类型。

**entities:全文实体配色,写一次**

```json
{"混合 v2": "blue", "混合 v1": "blue-lt", "纯向量": "green", "BM25 v1": "gray"}
```

可选值:`blue` `green` `orange` `violet`,各自的 `-lt` 浅色版,`gray`,`red-1`…`red-4`。后面所有图表按名字取色,保证同一实体全文同色。图表里出现未声明的名字时,按 蓝→绿→橙→紫 自动分配,并打印警告。

**stat:数字卡**

```json
{"title": "换成混合检索 v2,召回率翻了将近一倍", "note": "500 条真实用户问题",
 "items": [{"label": "召回率@10", "value": "79%", "sub": "线上 BM25 为 41%"}]}
```

**bar:柱状图**

```json
{"title": "混合检索 v2 把召回率从 41% 提到 79%", "note": "召回率@10;细线为 95% 置信区间",
 "unit": "%", "max": 100,
 "groups": [
   {"name": "线上方案", "sub": "BM25 关键词检索",
    "items": [{"name": "BM25 v1", "sub": "2026-03", "value": 41, "ci": [37, 45]}]},
   {"name": "候选方案", "sub": "2026 年 6–8 月评测",
    "items": [{"name": "混合 v2", "sub": "2026-08", "value": 79, "ci": [75, 83]},
              {"name": "知识图谱", "sub": "图谱仅覆盖 12%,未评测", "value": null}]}]}
```

- `value: null` 画锁图标,表示无数据;`value: 0` 画贴底短线
- `max`、`ticks` 可省略,脚本按数据取整;只有一组时可以直接写 `items`,不写 `groups`
- `"colors": "ramp"`:这组柱子按红色阶由浅到深上色,用于程度递进的类别

**line:折线图**

```json
{"title": "混合 v2 多出的延迟来自 reranker,仍在 300ms 预算内", "note": "P95 延迟(毫秒)",
 "x": {"labels": ["1万", "10万", "100万", "1000万"], "title": "文档数(对数刻度)"},
 "y": {"max": 300, "unit": "ms"},
 "series": [{"name": "混合 v2", "values": [140, 150, 175, 230]},
            {"name": "BM25 v1", "values": [12, 18, 35, 80]}],
 "threshold": {"value": 300, "label": "产品上限 300ms"}}
```

- x 默认按标签等距排列;需要数值刻度时,写 `"x": {"values": [...], "scale": "log"}`
- 线尾标签按终值从高到低排列,间距不足时由脚本顺延;手机上改成图下的一列

**table:对比表**

```json
{"title": "混合 v2 在 6 项指标里拿下 3 项最优", "note": "底色为每行最优;蓝框为推荐方案",
 "columns": [{"name": "BM25 v1", "sub": "线上"}, {"name": "混合 v2", "sub": "推荐", "pick": true}],
 "rows": [{"name": "召回率@10", "sub": "500 条真实问题", "better": "high", "cells": ["41%", "79%"]},
          {"name": "P95 延迟", "better": "low", "cells": ["35ms", {"v": "175ms", "sub": "含 reranker"}]},
          {"name": "运维复杂度", "best": 0, "cells": ["低", "中"]}]}
```

- `pick` 列由脚本自动移到第一个数据列
- `better: high/low`:脚本从格子文本里解析数字,找出每行最优;解析不了(比如 低/中/高)时,用 `best` 指定列序号
- 表头方案名用实体的 `-ink` 色

## 文件

| 文件 | 内容 |
|---|---|
| `scripts/build.py` | 渲染和校验,约 300–400 行 |
| `assets/base.css` | tokens、排版、卡片、figure、图表、对比表、移动端,约 200 行 |
| `references/chart-spec.md` | 数据格式完整字段说明,附一个完整示例 |
| `references/chart-sample.src.html` | 样板源文件;`chart-sample.html` 改由它构建生成,保证样板和脚本始终一致 |
| `SKILL.md` | 第 3 节改成「数据图用 build.py」,只保留规则和一个最小示例;第 4 节 CSS 指向 base.css;第 6 节自检改为 `build.py --shot` |

## 错误处理

- JSON 解析失败:指出第几个图表块、错在第几行,不生成输出
- 缺少 `title` / `note`、`cells` 数量和列数不一致、`ci` 不包含 `value`:报错并退出
- 未声明的实体:自动分配颜色,打印警告
- `--shot` 找不到 Chrome/Chromium:只构建、不截图,打印提示

## 测试

1. 用样板源文件构建,和当前 `chart-sample.html` 对比截图,桌面和手机效果一致
2. 构造 4 个错误输入(坏 JSON、缺 title、列数不齐、未声明实体),确认报错信息能直接定位问题
3. A/B 测速:用同一份检索方案素材,让 subagent 按新 skill 生成,和 v0.4 的 12 分钟 / 26 次工具调用 / 15.5 万 token 对比,如实报告
4. 在 42 服务器上跑一次 `build.py`(不带 `--shot`),确认 Linux 下能用
