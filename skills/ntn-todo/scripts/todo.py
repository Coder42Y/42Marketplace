#!/usr/bin/env python3
# ntn-todo: 查询与管理 Notion 待办列表 + "工作进度同步"页维护
# 通用版:自动发现 data_source + schema,首次引导(CLI 检测 + 模板搭建),本周进度概览 sync。
# 依赖: ntn CLI (~/.local/bin/ntn) 已 keychain 登录
import json, os, subprocess, sys, datetime, time

CONFIG_DIR = os.path.expanduser("~/.config/ntn-todo")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
TODAY = datetime.date.today().isoformat()
OVERVIEW_PAGE_TITLE = "工作进度同步"


def ntn(*args):
    """调用 ntn CLI,返回解析后的 JSON。"""
    try:
        r = subprocess.run(["ntn", *args], capture_output=True, text=True, check=True)
        return json.loads(r.stdout)
    except FileNotFoundError:
        print("❌ ntn 未安装。安装: curl -fsSL https://ntn.dev | bash"); sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("❌ ntn 调用失败: %s" % (e.stderr or e.stdout)[:300]); sys.exit(1)
    except json.JSONDecodeError:
        print("❌ 解析 ntn 输出失败。可能未登录,运行 ntn whoami 检查。"); sys.exit(1)


def ensure_ntn_cli():
    """轻量检测 ntn CLI 是否可用(--version,3s 超时)。"""
    try:
        subprocess.run(["ntn", "--version"], capture_output=True, text=True, timeout=3, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


# ---------- 发现与分析 ----------

def search_data_sources():
    """列出所有共享给 integration 的 data_source,返回 list[dict]。"""
    out, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        d = ntn("api", "v1/search", "-d", json.dumps(body))
        for r in d.get("results", []):
            if r.get("object") == "data_source":
                title = "".join(x.get("plain_text", "") for x in r.get("title", []))
                out.append({
                    "id": r.get("id"),
                    "title": title or "(无标题)",
                    "properties": r.get("properties", {}),
                    "parent_db_id": (r.get("parent") or {}).get("database_id"),
                })
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return out


def search_pages(query):
    """按标题搜 page,返回 [(id, title, url)]。"""
    d = ntn("api", "v1/search", "-d", json.dumps({"query": query, "page_size": 20}))
    pages = []
    for r in d.get("results", []):
        if r.get("object") == "page":
            title = ""
            for v in r.get("properties", {}).values():
                if v.get("type") == "title":
                    title = "".join(x.get("plain_text", "") for x in v.get("title", []))
            pages.append((r.get("id"), title, r.get("url", "")))
    return pages


def analyze_properties(props):
    """从 data_source properties 提取字段映射 + 状态分组(按 Notion 原生 to-do/in_progress/complete)。"""
    fields, selects = {}, []
    groups = {"to-do": [], "in_progress": [], "complete": []}
    for name, p in props.items():
        t = p.get("type")
        if t == "title" and "title" not in fields:
            fields["title"] = name
        elif t == "status":
            fields["status"] = name
            sf = p.get("status", {}) or {}
            id2name = {o["id"]: o["name"] for o in sf.get("options", [])}
            for g in sf.get("groups", []):
                gn = (g.get("name") or "").lower()
                key = "complete" if "complete" in gn else ("in_progress" if "progress" in gn else "to-do")
                groups[key].extend(id2name.get(oid) for oid in g.get("option_ids", []) if id2name.get(oid))
        elif t == "date" and "ddl" not in fields:
            fields["ddl"] = name
        elif t == "select":
            selects.append(name)
            if "priority" in name.lower() or "优先" in name:
                fields["priority"] = name
    fields["selects"] = selects
    return fields, groups


def block_text(b):
    """提取 block 的纯文本预览。"""
    bt = b.get("type")
    obj = b.get(bt, {}) or {}
    rt = obj.get("rich_text") or obj.get("text") or []
    return "".join(x.get("plain_text", "") for x in rt)


def setup_from_overview_page(pid):
    """从"工作进度同步"页找 child database 的 data_source + heading/callout block id。"""
    d = ntn("api", "v1/blocks/%s/children" % pid)
    db_ids, heading_id, callout_id = [], None, None
    for b in d.get("results", []):
        bt = b.get("type")
        if bt == "child_database":
            db_ids.append(b.get("id"))
        elif bt == "heading_2" and "本周进度概览" in block_text(b):
            heading_id = b.get("id")
        elif bt == "callout" and "最后更新" in block_text(b):
            callout_id = b.get("id")
    if not db_ids:
        return None
    # 匹配 data_source (parent.database_id 在页面的 child_database ids 里)
    for s in search_data_sources():
        if s["parent_db_id"] in db_ids:
            fields, groups = analyze_properties(s["properties"])
            if "status" in fields:  # 确认是待办库
                return {
                    "data_source_id": s["id"], "database_name": s["title"],
                    "fields": fields, "status_groups": groups,
                    "overview_page_id": pid,
                    "overview_heading_id": heading_id, "overview_callout_id": callout_id,
                    "onboarded": True,
                }
    return None


# ---------- config ----------

def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------- 引导 ----------

def cmd_setup(pick=None):
    sources = search_data_sources()
    candidates = [s for s in sources
                  if any(x.get("type") == "title" for x in s["properties"].values())
                  and any(x.get("type") == "status" for x in s["properties"].values())]
    if not candidates:
        print("❌ 没找到含 status 字段的 data_source。请确认待办库已分享给 ntn integration。")
        return None
    if len(candidates) == 1 and pick is None:
        pick = 1
    if pick is None:
        print("找到多个候选待办库,运行 `python3 todo.py setup <编号>` 选择:\n")
        for i, s in enumerate(candidates, 1):
            print("  %d. %s  (id=%s)" % (i, s["title"], s["id"]))
        return None
    try:
        s = candidates[int(pick) - 1]
    except (ValueError, IndexError):
        print("❌ 编号无效。"); return None
    fields, groups = analyze_properties(s["properties"])
    cfg = load_config() or {}
    cfg.update({"data_source_id": s["id"], "database_name": s["title"],
                "fields": fields, "status_groups": groups})
    save_config(cfg)
    print("✅ 已配置待办库: %s" % s["title"])
    return cfg


def cmd_onboard():
    if not ensure_ntn_cli():
        print("❌ 未检测到 ntn CLI。")
        print("   安装: curl -fsSL https://ntn.dev | bash")
        print("   登录: ntn login")
        print("   完成后重新运行: python3 todo.py onboard")
        return None
    print("✅ ntn CLI 已就绪")
    cfg = load_config()
    if cfg and cfg.get("onboarded"):
        print("已完成首次引导。运行 `python3 todo.py reset` 可重置。")
        return cfg
    print("\n搜索'%s'页..." % OVERVIEW_PAGE_TITLE)
    pages = search_pages(OVERVIEW_PAGE_TITLE)
    overview = next((p for p in pages if OVERVIEW_PAGE_TITLE in p[1]), None)
    if overview:
        pid = overview[0]
        print("✅ 找到现有页面: %s (id=%s)" % (overview[1], pid))
        new_cfg = setup_from_overview_page(pid)
        if new_cfg:
            save_config(new_cfg)
            print("✅ 已关联待办库并完成引导。")
            return new_cfg
        print("⚠️ 该页未找到含 status 字段的待办库,改用 setup 选择。")
        cfg = cmd_setup()
        if cfg:
            cfg["onboarded"] = True
            save_config(cfg)
            print("✅ 已完成引导。")
            return cfg
    else:
        print("\n未找到'%s'页。" % OVERVIEW_PAGE_TITLE)
        print("  - 按模板搭建: python3 todo.py setup-template")
        print("  - 仅配置现有待办库: python3 todo.py setup")
    return None


def cmd_setup_template(parent_page_id=None):
    """按"工作进度同步"页模板搭建:页面 + ToDo List database + 进度概览区块。"""
    if not ensure_ntn_cli():
        print("❌ 未检测到 ntn CLI。请先安装: curl -fsSL https://ntn.dev | bash && ntn login")
        return
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    date_range = "%s/%s - %s/%s" % (monday.month, monday.day, today.month, today.day)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # 1. 创建页面
    parent = {"type": "page_id", "page_id": parent_page_id} if parent_page_id else {"type": "workspace", "workspace": True}
    try:
        page = ntn("api", "v1/pages", "-d", json.dumps({
            "parent": parent, "icon": {"emoji": "📊"},
            "properties": {"title": [{"text": {"content": OVERVIEW_PAGE_TITLE}}]},
        }))
    except SystemExit:
        print("❌ 创建页面失败。若 workspace 根无权限,请指定父页: python3 todo.py setup-template <parent_page_id>")
        return
    pid = page.get("id")
    print("✅ 创建页面: %s (id=%s)" % (OVERVIEW_PAGE_TITLE, pid))

    # 2. append 引言 + divider + heading_2
    ntn("api", "v1/blocks/%s/children" % pid, "-X", "PATCH", "-d", json.dumps({"children": [
        {"object": "block", "type": "quote", "quote": {"rich_text": [{"type": "text", "text": {"content": "这里跟踪我所有进行中 / 计划 / 已完成的工作。每周一回看一次。"}}]}},
        {"object": "block", "type": "divider", "divider": {}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📊 本周进度概览（%s）" % date_range}}]}},
    ]}))
    # 取 heading_2 id
    children = ntn("api", "v1/blocks/%s/children" % pid).get("results", [])
    heading_id = next((b["id"] for b in children if b.get("type") == "heading_2"), None)

    # 3. 创建 database(自动作为 page child 出现在 heading 后)
    db = ntn("api", "v1/databases", "-d", json.dumps({
        "parent": {"type": "page_id", "page_id": pid}, "icon": {"emoji": "📋"},
        "title": [{"text": {"content": "ToDo List"}}],
        "initial_data_source": {"properties": {
            "Task": {"type": "title", "title": {}},
            "Status": {"type": "status", "status": {"options": [
                {"name": "💡 待开始", "color": "gray", "group": "To-do"},
                {"name": "🔥 进行中", "color": "blue", "group": "In progress"},
                {"name": "✅ 已完成", "color": "green", "group": "Complete"},
                {"name": "📦 归档", "color": "default", "group": "Complete"},
            ]}},
            "Priority": {"type": "select", "select": {"options": [{"name": "P0", "color": "red"}, {"name": "P1", "color": "yellow"}, {"name": "P2", "color": "default"}]}},
            "Type": {"type": "select", "select": {"options": [{"name": "feat", "color": "blue"}, {"name": "bug", "color": "red"}, {"name": "dev", "color": "yellow"}]}},
            "DDL": {"type": "date", "date": {}},
        }},
    }))
    db_id = db.get("id")
    print("✅ 创建待办库: ToDo List (id=%s)" % db_id)

    # 4. append callout + 说明(database 之后)
    ntn("api", "v1/blocks/%s/children" % pid, "-X", "PATCH", "-d", json.dumps({"children": [
        {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": "最后更新：%s · 由 CC + ntn 自动维护" % now}}], "icon": {"emoji": "🕒"}}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "📝 下方「任务库」是完整数据,可增删改;在 Notion 里可添加 chart/board 等其他 view。"}}]}},
    ]}))
    children = ntn("api", "v1/blocks/%s/children" % pid).get("results", [])
    callout_id = next((b["id"] for b in children if b.get("type") == "callout"), None)

    # 5. 拿 data_source_id(GET database 的 data_sources 字段,无索引延迟)+ 模板固定 schema
    db_info = ntn("api", "v1/databases/%s" % db_id)
    ds_list = db_info.get("data_sources") or []
    if not ds_list:
        print("⚠️ 新库无 data_source。稍后运行 `python3 todo.py setup` 手动配置。")
        return
    ds_id = ds_list[0]["id"]
    # 模板固定 schema(创建时已指定中文状态 + group)
    fields = {"title": "Task", "status": "Status", "ddl": "DDL",
              "priority": "Priority", "selects": ["Priority", "Type"]}
    groups = {"to-do": ["💡 待开始"], "in_progress": ["🔥 进行中"], "complete": ["✅ 已完成", "📦 归档"]}
    cfg = {"data_source_id": ds_id, "database_name": "ToDo List",
           "fields": fields, "status_groups": groups,
           "overview_page_id": pid, "overview_heading_id": heading_id,
           "overview_callout_id": callout_id, "onboarded": True}
    # 尝试创建 chart view(失败不阻断)
    try:
        ntn("api", "v1/views", "-d", json.dumps({
            "database_id": db_id, "name": "任务状态分布",
            "type": "chart", "chart": {"type": "bar", "group_by": "status"},
        }))
        print("✅ 创建 chart view: 任务状态分布")
    except SystemExit:
        print("⚠️ chart view 创建失败(可手动在 Notion 里添加)。")
    save_config(cfg)
    print("\n✅ 模板搭建完成。运行 `python3 todo.py open` 查看待办,`python3 todo.py sync` 更新本周概览。")


# ---------- sync:本周进度概览维护 ----------

def weekly_summary(cfg):
    """统计本周完成/进行中/待办/过期(一次 query all 本地统计)。"""
    sid = cfg["data_source_id"]
    f = cfg["fields"]
    sg = cfg["status_groups"]
    sname, ddl_f = f.get("status"), f.get("ddl")
    monday = (datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())).isoformat()
    today_iso = TODAY
    try:
        d = ntn("api", "v1/data_sources/%s/query" % sid, "-d", json.dumps({"page_size": 100}))
    except SystemExit:
        return "统计不可用"
    done_w = in_prog = todo = overdue = 0
    for r in d.get("results", []):
        props = r.get("properties", {})
        s = (props.get(sname, {}).get("status") or {}).get("name", "")
        if s in sg["in_progress"]:
            in_prog += 1
        elif s in sg["to-do"]:
            todo += 1
        elif s in sg["complete"] and (r.get("last_edited_time", "")[:10] >= monday):
            done_w += 1
        if s in sg["to-do"] + sg["in_progress"] and ddl_f:
            ddl = (props.get(ddl_f, {}).get("date") or {}).get("start", "")
            if ddl and ddl < today_iso:
                overdue += 1
    return "本周完成%d 进行中%d 待办%d 过期%d" % (done_w, in_prog, todo, overdue)


def cmd_sync():
    cfg = load_config()
    if not cfg or not cfg.get("overview_page_id"):
        print("❌ 未配置'工作进度同步'页。运行 `python3 todo.py onboard` 或 `setup-template`。")
        return
    pid = cfg["overview_page_id"]
    heading_id = cfg.get("overview_heading_id")
    callout_id = cfg.get("overview_callout_id")
    # 首次 sync 缓存 block id
    if not heading_id or not callout_id:
        children = ntn("api", "v1/blocks/%s/children" % pid).get("results", [])
        for b in children:
            if b.get("type") == "heading_2" and "本周进度概览" in block_text(b):
                heading_id = b["id"]
            elif b.get("type") == "callout" and "最后更新" in block_text(b):
                callout_id = b["id"]
        cfg["overview_heading_id"] = heading_id
        cfg["overview_callout_id"] = callout_id
        save_config(cfg)
    if not heading_id or not callout_id:
        print("❌ 页面未找到'本周进度概览'标题或'最后更新'callout。请确认页面结构。")
        return
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    date_range = "%s/%s - %s/%s" % (monday.month, monday.day, today.month, today.day)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = weekly_summary(cfg)
    # PATCH heading_2
    ntn("api", "v1/blocks/%s" % heading_id, "-X", "PATCH", "-d", json.dumps({
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📊 本周进度概览（%s）" % date_range}}]},
    }))
    # PATCH callout
    callout_text = "最后更新：%s · %s · 由 CC + ntn 自动维护" % (now, summary)
    ntn("api", "v1/blocks/%s" % callout_id, "-X", "PATCH", "-d", json.dumps({
        "callout": {"rich_text": [{"type": "text", "text": {"content": callout_text}}], "icon": {"emoji": "🕒"}},
    }))
    print("✅ 已更新本周进度概览")
    print("   标题: 📊 本周进度概览（%s）" % date_range)
    print("   callout: %s" % callout_text)


# ---------- 查询 ----------

def ensure_ready():
    """查询/sync 前检查 CLI + onboarding。"""
    if not ensure_ntn_cli():
        print("❌ 未检测到 ntn CLI。安装: curl -fsSL https://ntn.dev | bash,然后 ntn login")
        print("   完成后运行: python3 todo.py onboard")
        return False
    cfg = load_config()
    if not cfg or not cfg.get("onboarded"):
        print("首次使用,开始引导...\n")
        cmd_onboard()
        cfg = load_config()
        if not cfg or not cfg.get("onboarded"):
            return False
    return True


def cmd_query(mode="open"):
    cfg = load_config()
    if not cfg:
        print("未配置。运行 `python3 todo.py onboard` 或 `setup`。")
        return
    sid = cfg["data_source_id"]
    f = cfg["fields"]
    sg = cfg["status_groups"]
    sname = f.get("status")
    open_opts = sg["to-do"] + sg["in_progress"]
    if mode == "overdue" and not f.get("ddl"):
        print("⚠️ 该库无 date 字段,overdue 不可用,改显未完成:\n")
        mode = "open"
    flt = {}
    if mode == "open" and open_opts:
        flt = {"or": [{"property": sname, "status": {"equals": o}} for o in open_opts]}
    elif mode == "done" and sg["complete"]:
        flt = {"or": [{"property": sname, "status": {"equals": o}} for o in sg["complete"]]}
    elif mode == "overdue" and open_opts:
        flt = {"and": [{"or": [{"property": sname, "status": {"equals": o}} for o in open_opts]},
                       {"property": f["ddl"], "date": {"before": TODAY}}]}
    body = {"page_size": 100}
    if flt:
        body["filter"] = flt
    d = ntn("api", "v1/data_sources/%s/query" % sid, "-d", json.dumps(body))
    render(d, cfg, mode)


def render(d, cfg, mode):
    rs = d.get("results", [])
    f = cfg["fields"]
    sg = cfg["status_groups"]
    title_f, status_f, ddl_f = f.get("title"), f.get("status"), f.get("ddl")
    selects, pri_f = f.get("selects", []), f.get("priority")
    group_order = {"in_progress": 0, "to-do": 1, "complete": 2}

    def gv(props, pname, typ):
        if not pname:
            return "-"
        p = props.get(pname, {})
        if typ == "title":
            return "".join(x.get("plain_text", "") for x in p.get("title", []))
        if typ == "status":
            s = p.get("status") or {}
            return s.get("name", "") or "-"
        if typ == "select":
            s = p.get("select")
            return s.get("name", "") if s else "-"
        if typ == "date":
            da = p.get("date")
            return da.get("start", "") if da else "-"
        return "-"

    def group_of(name):
        for g, opts in sg.items():
            if name in opts:
                return g
        return "to-do"

    def sort_key(r):
        props = r.get("properties", {})
        g = group_of(gv(props, status_f, "status"))
        pri = gv(props, pri_f, "select") if pri_f else "-"
        ddl = gv(props, ddl_f, "date") if ddl_f else "-"
        return (group_order.get(g, 9), pri if pri != "-" else "zzz", ddl if ddl != "-" else "9999-99-99")

    rs = sorted(rs, key=sort_key)
    print("📋 %s [%s]  共 %d 条  (has_more=%s)  今天 %s" % (cfg["database_name"], mode, len(rs), d.get("has_more"), TODAY))
    print()
    for i, r in enumerate(rs, 1):
        props = r.get("properties", {})
        parts = [gv(props, status_f, "status")] + [gv(props, s, "select") for s in selects] + [gv(props, title_f, "title")]
        ddl_v = gv(props, ddl_f, "date") if ddl_f else "-"
        flag = ""
        if ddl_v != "-" and ddl_v < TODAY:
            flag = "  ⚠️过期"
        elif ddl_v == TODAY:
            flag = "  ⭐今日"
        print("%2d. %s | DDL=%s%s" % (i, " | ".join(parts), ddl_v, flag))


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "open"
    # 引导/管理命令不需要 ensure_ready
    if cmd in ("open", "overdue", "done", "all", "sync", ""):
        if not ensure_ready():
            return
    if cmd == "setup":
        cmd_setup(args[1] if len(args) > 1 else None)
    elif cmd == "setup-template":
        cmd_setup_template(args[1] if len(args) > 1 else None)
    elif cmd == "onboard":
        cmd_onboard()
    elif cmd == "sync":
        cmd_sync()
    elif cmd == "config":
        cfg = load_config()
        print(json.dumps(cfg, ensure_ascii=False, indent=2) if cfg else "(未配置)")
    elif cmd == "reset":
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH); print("已清除配置。")
        else:
            print("无配置。")
    elif cmd in ("open", "overdue", "done", "all", ""):
        cmd_query(cmd or "open")
    else:
        print("用法: python3 todo.py [open|overdue|done|all|sync|setup|setup-template|onboard|config|reset]")
        print("  open(默认)      未完成(进行中->待办)")
        print("  overdue         未完成中已过期")
        print("  done            已完成")
        print("  all             全部")
        print("  sync            更新本周进度概览(标题日期+callout摘要)")
        print("  setup [N]       配置现有待办库")
        print("  setup-template  按模板搭建'工作进度同步'页")
        print("  onboard         首次引导(CLI 检测+复用/搭建页)")
        print("  config / reset  查看配置 / 清除重置")


if __name__ == "__main__":
    main()
