# 图表数据格式

图表在 `design.src.html` 里写成下面这种块,放在正文中图要出现的位置。`scripts/build.py` 会把它换成画好的图。完整示例见 `chart-sample.src.html`(构建结果是 `chart-sample.html`)。

```html
<script type="application/json" data-chart="bar">{ ... }</script>
```

除 `entities` 外,每种图都必须有 `title`(结论句)和 `note`(灰色口径)。

- 数值字段(`value`、`values`、`ci`、`max`、`ticks`、`threshold.value`)必须是数字,不能是带单位的字符串;暂不支持负值
- 给了 `max` 时,所有数值(含误差线上限、阈值)都不能超过它,否则构建失败
- JSON 字符串里如果出现 `</script>`,要写成 `<\/script>`,否则数据块会被提前截断

## entities:实体配色,全文写一次

```json
{"混合 v2": "blue", "混合 v1": "blue-lt", "纯向量": "green", "BM25 v1": "gray", "其他": "gray-lt"}
```

| 颜色 | 用途 |
|---|---|
| `blue` `green` `orange` `violet` | 家族主色,按这个顺序分配,推荐方案拿 `blue` |
| `blue-lt` 等 `-lt` | 同家族的旧版或配角 |
| `gray` | 线上现状、对照组 |
| `gray-lt` | 合并出来的「其他」 |
| `red-1` … `red-5` | 程度递进(一般用 bar 的 `"colors": "ramp"`,不用手配) |

图里出现没声明的名字,脚本按 蓝→绿→橙→紫 自动补,并打印警告。看到警告就回去补声明。

## stat:数字卡

| 字段 | 说明 |
|---|---|
| `items[]` | `label` 指标名,`value` 显示的数(字符串,自己带单位),`sub` 灰字补充(可选) |

## bar:柱状图

| 字段 | 说明 |
|---|---|
| `groups[]` | 分组。每组 `name` 组名、`sub` 灰色限定语(可选)、`items[]`。不分组时直接写顶层 `items` |
| `items[]` | `name` 类目名,`sub` 灰字(日期、备注、无数据的原因),`value` 数值,`ci` `[下限, 上限]`(可选),`color` 覆盖颜色(可选) |
| `unit` / `prefix` | 数值后缀 / 前缀,如 `"%"`、`"¥"` |
| `max` / `ticks` | 纵轴满量程和刻度,省略时自动取整 |
| `colors` | `"entity"`(默认,按实体取色)、`"ramp"`(每组内按红色阶由浅到深,只用于单个方案)、或一个颜色名(所有柱子同色) |
| `orient` | `"auto"`(默认:柱子 ≤ 4 根竖向;超过 4 根桌面竖向、手机自动横向)、`"v"` 只竖向、`"h"` 只横向(类目名很长时用) |

- `"value": null` 画锁图标,表示没法测;原因写在 `sub`
- `"value": 0` 画贴底短线并标 0,表示测了、结果是 0
- 柱子超过 10 根会警告:考虑拆图或合并成「其他」

**成对横条**:几个方案在同一组类目上逐项对比时,用 `categories` + `series`,不写 `groups` / `items`。每个类目一行,行内每个方案一根细横条,图顶自动加一行系列标注。

```json
{"title": "攻击越强，规则引擎越拦不住；分类模型 v2 在多轮诱导下绕过率仍只有 11%",
 "note": "绕过率，越低越好；每档 400 条攻击样本", "unit": "%",
 "categories": ["直接提问", "同义改写", "角色扮演", "多轮诱导", {"name": "编码混淆", "sub": "Base64、谐音字、拆字"}],
 "series": [
   {"name": "规则引擎 v3", "sub": "线上", "values": [2, 18, 35, 52, 71]},
   {"name": "分类模型 v2", "sub": "推荐", "values": [0, 3, 6, 11, null],
    "notes": [null, null, null, null, "测试集未标注完，下周补测"]}]}
```

| 字段 | 说明 |
|---|---|
| `categories[]` | 类目名,或 `{"name", "sub"}` |
| `series[]` | `name`、`sub`(可选,显示在系列标注里)、`values`(和类目等长,没法测写 `null`)、`notes`(可选,和类目等长,`null` 处显示的原因) |

## line:折线图

| 字段 | 说明 |
|---|---|
| `x.labels` | x 轴标签,默认等距排列;标签多时脚本自动隔几个显示一个 |
| `x.values` + `x.scale` | 需要按数值排布时用,`scale` 取 `"linear"` 或 `"log"`。`x.values` 必须严格递增,对数刻度下都要大于 0 |
| `x.title` | 轴标题(可选),如「文档数(对数刻度)」 |
| `y.max` / `y.ticks` / `y.unit` / `y.prefix` | 同 bar |
| `series[]` | `name`、`values`(和 `x.labels` 等长,没有数据的月份写 `null`)、`color`(可选) |
| `threshold` | `{"value": 3, "label": "业务要求 < 3%"}`,画成虚线,文字放在右侧标签列里,不会压到线 |

线尾标签按终值从高到低排,挤在一起时脚本自动顺延;手机上改成图下的一列,日期标签自动减到 3–4 个。

## table:对比表

| 字段 | 说明 |
|---|---|
| `columns[]` | `name`、`sub`(身份,如「推荐」「线上」)、`pick: true` 标推荐列(只能一个,脚本自动移到第一个数据列) |
| `rows[]` | `name`、`sub`(口径)、`cells`(和列数相等)、`better` 或 `best` |
| `cells[]` | 字符串,或 `{"v": "175ms", "sub": "含 reranker"}`;缺数据写 `"—"` |
| `better` | `"high"` / `"low"`:脚本从格子里解析数字,标出每行最优。同一行单位不一致(如 `1.2s` 和 `900ms`)时不标并警告,统一单位或改用 `best` |
| `best` | 列序号(按 `columns` 原顺序,从 0 开始),或序号数组。低/中/高这类解析不了数字的行用它 |

## 报错

构建失败时脚本会指出第几个图表块、哪个字段有问题,按提示改 `design.src.html` 再跑。每一行对比表都要写 `better` 或 `best`,漏写会警告。

改了 `scripts/build.py` 之后跑一遍测试:`python3 -m unittest discover -s scripts -p 'test_*.py'`。
