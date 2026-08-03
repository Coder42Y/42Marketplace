# ntn-todo

查询与管理 Notion 待办列表 + 维护"工作进度同步"页本周进度概览。

## 功能
- **待办查询**:`open`(未完成) / `overdue`(已过期) / `done`(已完成) / `all`(全部),按 status 分组排序(进行中 -> 待办 -> 已完成),组内 Priority + DDL,标注 ⚠️过期 / ⭐今日
- **本周进度概览 sync**:更新"工作进度同步"页的标题日期范围 + callout 进度摘要(本周完成 / 进行中 / 待办 / 过期)
- **首次自动引导**:检测 ntn CLI + 复用现有"工作进度同步"页,或按模板搭建(页面 + ToDo List database + 进度概览区块)
- **通用不硬编码**:自动发现 data_source + 字段 schema,按 Notion 原生 status group(to-do / in_progress / complete) 判定未完成,适配任意含 status 字段的待办库,适合分享

## 前置依赖
- `ntn` CLI 已装(`curl -fsSL https://ntn.dev | bash`)且已登录(`ntn login` / `ntn whoami` 检查)
- 待办库在 Notion 里分享给 ntn integration(库 `···` -> Connections -> 添加)

## 用法

```bash
python3 scripts/todo.py [open|overdue|done|all|sync|setup|setup-template|onboard|config|reset]
```

| 命令 | 含义 |
|------|------|
| `open`(默认)| 未完成(进行中 -> 待办) |
| `overdue` | 未完成中已过期 |
| `done` | 已完成 |
| `all` | 全部 |
| `sync` | 更新本周进度概览(标题日期 + callout 摘要) |
| `setup [N]` | 配置现有待办库 |
| `setup-template [parent_page_id]` | 按模板搭建"工作进度同步"页 |
| `onboard` | 手动重跑首次引导 |
| `config` / `reset` | 查看配置 / 清除重置 |

首次运行 `open` 或 `sync` 自动引导(CLI 检测 + 复用/搭建页)。配置缓存于 `~/.config/ntn-todo/config.json`。

## 字段约定(模板搭建)
`Task`(title) / `Status`(💡待开始 · 🔥进行中 · ✅已完成 · 📦归档) / `Priority`(P0/P1/P2) / `Type`(feat/bug/dev) / `DDL`(date)

复用现有库时字段名按类型自动识别,不要求与此完全一致。

## 分享给别人
1. 对方装 ntn CLI + `ntn login`
2. 待办库分享给对方 integration
3. 给本 skill 目录(含 SKILL.md + scripts/todo.py + .claude-plugin/plugin.json + README.md,**不含 config**--对方首次自动生成)
4. 对方首次运行 `python3 scripts/todo.py` 自动发现待办库;无"工作进度同步"页可 `setup-template` 搭建

## 已知限制
- chart view 自动创建不支持(Notion API body 限制),搭建后在 Notion UI 手动添加柱状图
- 待办库需用 status 类型字段(非 checkbox)
