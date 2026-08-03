---
name: ntn-todo
description: >-
  查询与管理 Notion 待办列表 + 维护"工作进度同步"页本周进度概览。用户说"拉我的 notion 待办"、
  "我的 todo"、"ntn todo"、"看看待办"、"过期任务"、"同步本周进度"、"更新工作进度同步"等时使用。
  通用版:首次自动引导(CLI 检测 + 复用现有页或按模板搭建),零配置适配任意含 status 字段的待办库。
---

# ntn-todo

查询 Notion 待办列表 + 维护"工作进度同步"页本周进度概览。**通用版**:首次自动引导,不硬编码任何 id/字段名。

## 前置依赖
- `ntn` CLI(`~/.local/bin/ntn`,安装 `curl -fsSL https://ntn.dev | bash`)已 keychain 登录(`ntn whoami` 检查)
- 待办库分享给 ntn integration(库 `···` -> Connections -> 添加 integration)

## 首次运行(自动引导)
任何查询/sync 命令首次运行时自动 `ensure_ready`:
1. **检测 ntn CLI**:`ntn --version`(3s 超时,轻量)。未装则提示安装并退出。
2. **onboarding**:search "工作进度同步" 页
   - 找到 -> 自动复用(记录 page_id + heading/callout block id + setup data_source),`onboarded=true`
   - 没找到 -> 提示 `setup-template`(按模板搭建)或 `setup`(仅配置现有库)并退出

后续命令不再引导(`onboarded=true` 存于 config)。

## 用法

```bash
python3 scripts/todo.py [open|overdue|done|all|sync|setup|setup-template|onboard|config|reset]
```

| 命令 | 含义 |
|------|------|
| `open`(默认)| 未完成(进行中 -> 待办) |
| `overdue` | 未完成中已过期(DDL < 今天) |
| `done` | 已完成 |
| `all` | 全部 |
| `sync` | 更新本周进度概览(标题日期 + callout 摘要) |
| `setup [N]` | 配置现有待办库 |
| `setup-template [parent_page_id]` | 按模板搭建"工作进度同步"页 |
| `onboard` | 手动重跑首次引导 |
| `config` / `reset` | 查看配置 / 清除重置 |

查询输出按 status 分组排序(**进行中 -> 待办 -> 已完成**),组内 Priority + DDL,自动标注 `⚠️过期` / `⭐今日`。**默认只列属性、不读正文**(避免输出过长);看正文需用户主动 ask(`ntn pages get <page-id>`)。**直接把输出展示给用户**,附一两句要点。

## sync:本周进度概览维护
`sync` 更新"工作进度同步"页的两个 block:
- heading_2 标题 ->「📊 本周进度概览（本周一/日 - 今天/日）」
- callout ->「最后更新:时间 · 本周完成N 进行中M 待办K 过期L · 由 CC + ntn 自动维护」

进度统计:一次 query all 本地算。本周完成 = complete 组且 `last_edited_time` 在本周;过期 = 未完成且 DDL < 今天。block id 首次 sync 时从页面 children 定位并缓存到 config。

## 模板搭建 `setup-template`
按现有"工作进度同步"页结构创建(中文 schema,与现有一致):
- 页面"工作进度同步":引言 quote + divider + H2 + callout + 说明 paragraph
- database「ToDo List」:Task(title) / Status(💡待开始·🔥进行中·✅已完成·📦归档,带 group) / Priority(P0-2) / Type(feat·bug·dev) / DDL
- block 顺序:quote -> divider -> heading_2 -> database -> callout -> paragraph(database 创建后自动在 heading 后)
- parent:默认 workspace 根;无权限则传 `setup-template <parent_page_id>`
- ⚠️ chart view 自动创建当前不支持(API body 格式限制),搭建后在 Notion UI 给 database 加 chart view(柱状图,按 Status 分组)

## 工作原理(不硬编码)
- **data_source_id**:复用现有页时从 page 的 child_database 匹配 data_source 的 parent.database_id;模板搭建时 GET database 的 `data_sources` 字段(无索引延迟)
- **字段名**:按 Notion 字段类型自动识别(title/status/date/select);状态分组用 Notion 原生 `to-do`/`in_progress`/`complete`,跨中英文 schema 通用
- **排序**:status 分组(进行中->待办->已完成),Python 端排序(Notion API sorts 不支持按 group 自定义顺序)
- **config**:`~/.config/ntn-todo/config.json`(data_source_id / fields / status_groups / overview_page_id / heading_id / callout_id / onboarded)

## 典型流程
1. 默认 `python3 scripts/todo.py`(首次自动 onboard,之后 open)展示给用户,点出过期/今日/进行中重点
2. 用户要更新本周概览 -> `python3 scripts/todo.py sync`
3. 看某条正文 -> `ntn pages get <page-id>`(page id 需 query 取,或用户指定)
4. 更新状态 -> `ntn api v1/pages/<page-id> -X PATCH -d '{"properties":{"Status":{"status":{"name":"✅ 已完成"}}}}'`

## 分享给别人
1. 对方装 ntn CLI + `ntn login`
2. 待办库分享给对方 integration
3. 给本 skill 目录(含 SKILL.md + scripts/todo.py + .claude-plugin/plugin.json + README.md,**不含 config**--对方首次自动生成)
4. 对方首次运行自动引导:有"工作进度同步"页则复用,没有则 `setup-template` 搭建

## CC 决策点指导(用 AskUserQuestion)
首次引导遇到决策点(脚本打印提示并退出)时,CC 用 AskUserQuestion 问用户:
- **CLI 未装**(`ntn --version` 失败)-> 问"是否安装 ntn CLI?";同意则跑 `curl -fsSL https://ntn.dev | bash`,再提示对方 `ntn login`
- **未找到"工作进度同步"页** -> 问"按模板搭建(setup-template)还是配置现有库(setup)?"

## 排错
- `没找到含 status 字段的 data_source`:库没分享给 integration,或用 checkbox 非 status 类型(后者需改成 status)
- `invalid_request_url` / 查询为空:data_source_id 失效(库重建),`reset` 重新发现
- `未找到'工作进度同步'页`:首次无该页,`setup-template` 搭建或 `onboard` 重试
- chart view 创建失败:已知限制,Notion UI 手动加
- 未登录:`ntn whoami` 检查,失败则 `ntn login`
