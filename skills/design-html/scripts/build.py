#!/usr/bin/env python3
"""design-html 构建脚本:把 design.src.html 渲染成单文件 design.html。

  python3 build.py design.src.html            # 输出同目录的 design.html
  python3 build.py design.src.html --shot     # 另外截桌面图、手机图,并检查手机宽度

design.src.html 只写 <main> 里的内容。图表写成
  <script type="application/json" data-chart="entities|stat|bar|line|table">{...}</script>
格式见 references/chart-spec.md。只用 Python 3 标准库。
"""
import argparse
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(HERE, "..", "assets", "base.css")

MAIN = ["blue", "green", "orange", "violet"]
COLORS = {}
for _k in MAIN:
    COLORS[_k] = ("--" + _k, "--" + _k + "-ink")
    COLORS[_k + "-lt"] = ("--" + _k + "-lt", "--" + _k + "-ink")
COLORS["gray"] = ("--gray", "--text-2")
COLORS["gray-lt"] = ("--gray-lt", "--text-2")
for _i in range(1, 6):
    COLORS["red-%d" % _i] = ("--red-%d" % _i, "--red-ink")

LOCK = ('<svg width="18" height="22" viewBox="0 0 18 22" aria-hidden="true">'
        '<path d="M4 10V7a5 5 0 0 1 10 0v3" fill="none" stroke="currentColor" stroke-width="2"/>'
        '<rect x="1" y="10" width="16" height="11" rx="2" fill="currentColor"/></svg>')

BLOCK_RE = re.compile(r'<script\s+type="application/json"\s+data-chart="(\w+)"\s*>(.*?)</script>', re.S)


class BuildError(Exception):
    pass


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


class Ctx:
    def __init__(self):
        self.entities = {}
        self.warnings = []
        self.counts = {}
        self.n = 0

    def warn(self, msg):
        self.warnings.append(msg)

    def color(self, name, explicit=None, where=""):
        key = explicit or self.entities.get(name)
        if key is None:
            used = {v.replace("-lt", "") for v in self.entities.values()}
            free = [c for c in MAIN if c not in used]
            key = free[0] if free else "gray-lt"
            self.entities[name] = key
            self.warn("%s「%s」没有在 entities 里声明,自动配成 %s" % (where, name, key))
        if key not in COLORS:
            raise BuildError("%s「%s」的颜色 %s 不存在,可选:%s" % (where, name, key, ", ".join(COLORS)))
        return COLORS[key]


# ---------------------------------------------------------------- 数值工具

def fmt(v, unit="", prefix=""):
    if v is None:
        return "—"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = "{:,}".format(v) if abs(v) >= 10000 else str(v)
    return prefix + s + unit


def nice_scale(maxv, want=4):
    if maxv <= 0:
        return 1.0, [1.0]
    raw = maxv / want
    mag = 10 ** math.floor(math.log10(raw))
    step = mag
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if step * want >= maxv - 1e-9:
            break
    top = math.ceil(maxv / step - 1e-9) * step
    n = int(round(top / step))
    return top, [round(step * i, 10) for i in range(1, n + 1)]


def pct(v, top):
    return round(max(0.0, min(100.0, v / top * 100.0)), 2)


def need(spec, keys, where):
    for k in keys:
        if spec.get(k) in (None, ""):
            raise BuildError("%s 缺少必填字段 \"%s\"" % (where, k))


def head(spec, cid):
    return ('<figure class="c-chart" role="group" aria-labelledby="%s">'
            '<figcaption class="c-head"><h3 id="%s">%s</h3><p>%s</p></figcaption>'
            % (cid, cid, esc(spec["title"]), esc(spec["note"])))


# ---------------------------------------------------------------- 各图表

def render_entities(spec, ctx, where):
    if not isinstance(spec, dict):
        raise BuildError("%s entities 应该是 {\"名字\": \"颜色\"}" % where)
    for name, key in spec.items():
        if key not in COLORS:
            raise BuildError("%s 实体「%s」的颜色 %s 不存在,可选:%s" % (where, name, key, ", ".join(COLORS)))
        ctx.entities[name] = key
    return ""


def render_stat(spec, ctx, where, cid):
    need(spec, ["title", "note", "items"], where)
    out = [head(spec, cid), '<div class="c-stats">']
    for it in spec["items"]:
        out.append('<div class="c-stat"><div class="k">%s</div><div class="v">%s</div>%s</div>' % (
            esc(it.get("label")), esc(it.get("value")),
            '<div class="d">%s</div>' % esc(it["sub"]) if it.get("sub") else ""))
    out.append("</div></figure>")
    return "".join(out)


def bar_color(ctx, it, mode, ii, n, where):
    if it.get("color"):
        return ctx.color(it["name"], it["color"], where)
    if mode == "ramp":
        step = 3 if n == 1 else 1 + int(round(ii * 4 / (n - 1)))
        return COLORS["red-%d" % step]
    if mode in COLORS:
        return COLORS[mode]
    return ctx.color(it["name"], None, where)


def render_vbars(groups, ctx, where, top, ticks, unit, prefix, mode):
    has_head = any(g.get("name") for g in groups)
    cols = ["minmax(%dpx, %sfr)" % (72 if gi == 0 else 48, len(g["items"]) + (0.6 if gi == 0 else 0))
            for gi, g in enumerate(groups)]
    out = ['<div class="c-bars" style="grid-template-columns:%s">' % " ".join(cols)]
    row = 1
    if has_head:
        for gi, g in enumerate(groups):
            out.append('<div class="c-ghead" style="grid-row:1;grid-column:%d">%s%s</div>' % (
                gi + 1, esc(g.get("name") or ""), "<span>%s</span>" % esc(g["sub"]) if g.get("sub") else ""))
        row = 2
    for gi, g in enumerate(groups):
        p = ['<div class="c-plot%s" style="grid-row:%d;grid-column:%d">' % (" ticked" if gi == 0 else "", row, gi + 1)]
        for t in ticks:
            p.append('<div class="c-gl" style="bottom:%s%%"></div>' % pct(t, top))
        if gi == 0:
            for t in ticks:
                p.append('<div class="c-tick" style="bottom:%s%%">%s</div>' % (pct(t, top), esc(fmt(t, unit, prefix))))
        p.append('<div class="c-cols">')
        n = len(g["items"])
        for ii, it in enumerate(g["items"]):
            v = it.get("value")
            if v is None:
                p.append('<div class="c-col"><div class="c-na" role="img" aria-label="无数据">%s</div></div>' % LOCK)
                continue
            mark, ink = bar_color(ctx, it, mode, ii, n, where)
            ci = it.get("ci")
            p.append('<div class="c-col" style="--v:%s;--c:var(%s);--ink:var(%s)"><div class="c-bar"></div>'
                     % (pct(v, top), mark, ink))
            if ci:
                p.append('<div class="c-ci" style="--lo:%s;--hi:%s"></div>' % (pct(ci[0], top), pct(ci[1], top)))
            p.append('<div class="c-val" style="--top:%s"><span>%s</span></div></div>'
                     % (pct(ci[1], top) if ci else pct(v, top), esc(fmt(v, unit, prefix))))
        p.append("</div></div>")
        out.append("".join(p))
    for gi, g in enumerate(groups):
        lab = ['<div class="c-labels%s" style="grid-row:%d;grid-column:%d">' % (" ticked" if gi == 0 else "", row + 1, gi + 1)]
        for it in g["items"]:
            lab.append("<div>%s%s</div>" % (esc(it["name"]), "<span>%s</span>" % esc(it["sub"]) if it.get("sub") else ""))
        lab.append("</div>")
        out.append("".join(lab))
    out.append("</div>")
    return "".join(out)


def hbar(v, ci, top, mark, ink, label, note=None):
    if v is None:
        return '<span class="c-hna" role="img" aria-label="无数据">%s%s</span>' % (LOCK, "<small>%s</small>" % esc(note) if note else "")
    s = ['<div class="c-hbar" style="width:%s%%;background:var(%s)"></div>' % (pct(v, top), mark)]
    edge = pct(v, top)
    if ci:
        s.append('<div class="c-hci" style="left:%s%%;width:%s%%"></div>' % (pct(ci[0], top), round(pct(ci[1], top) - pct(ci[0], top), 2)))
        edge = pct(ci[1], top)
    s.append('<span class="c-hval" style="left:calc(%s%% + 8px);color:var(%s)">%s</span>' % (edge, ink, label))
    return "".join(s)


def render_hbars(groups, ctx, where, top, unit, prefix, mode):
    out = ['<div class="c-hbars">']
    for g in groups:
        if g.get("name"):
            out.append('<div class="c-hgroup">%s%s</div>' % (esc(g["name"]), "<span>%s</span>" % esc(g["sub"]) if g.get("sub") else ""))
        n = len(g["items"])
        for ii, it in enumerate(g["items"]):
            v = it.get("value")
            mark, ink = bar_color(ctx, it, mode, ii, n, where) if v is not None else ("--gray", "--text-2")
            out.append('<div class="c-hrow"><div class="c-hlab">%s%s</div><div class="c-htrack">%s</div></div>' % (
                esc(it["name"]), "<span>%s</span>" % esc(it["sub"]) if it.get("sub") else "",
                hbar(v, it.get("ci"), top, mark, ink, esc(fmt(v, unit, prefix)))))
    out.append("</div>")
    return "".join(out)


def render_paired(spec, ctx, where, cid):
    """多个实体在同一组类目上对比:每个类目一行,行内每个实体一根细横条。"""
    cats, series = spec["categories"], spec["series"]
    unit, prefix = spec.get("unit", ""), spec.get("prefix", "")
    vals = []
    for s in series:
        need(s, ["name", "values"], where + " 的某个系列")
        if len(s["values"]) != len(cats):
            raise BuildError("%s「%s」有 %d 个值,categories 有 %d 个" % (where, s["name"], len(s["values"]), len(cats)))
        vals += [v for v in s["values"] if v is not None]
    top = spec.get("max") or nice_scale(max(vals) if vals else 1)[0]
    colors = [ctx.color(s["name"], s.get("color"), where) for s in series]
    key = "".join('<span><i style="background:var(%s)"></i>%s%s</span>' % (m, esc(s["name"]), '<em>%s</em>' % esc(s["sub"]) if s.get("sub") else "")
                  for s, (m, _) in zip(series, colors))
    out = [head(spec, cid), '<div class="c-hkey">%s</div><div class="c-hbars paired">' % key]
    for ci_, c in enumerate(cats):
        name, sub = (c.get("name"), c.get("sub")) if isinstance(c, dict) else (c, None)
        out.append('<div class="c-hrow"><div class="c-hlab">%s%s</div><div class="c-hstack">' % (esc(name), "<span>%s</span>" % esc(sub) if sub else ""))
        for s, (mark, ink) in zip(series, colors):
            v = s["values"][ci_]
            note = (s.get("notes") or [None] * len(cats))[ci_]
            bar = hbar(v, None, top, mark, ink, esc(fmt(v, unit, prefix)), note)
            out.append('<div class="c-htrack thin" title="%s">%s</div>' % (esc(s["name"]), bar))
        out.append("</div></div>")
    out.append("</div></figure>")
    return "".join(out)


def render_bar(spec, ctx, where, cid):
    need(spec, ["title", "note"], where)
    if spec.get("categories") or spec.get("series"):
        need(spec, ["categories", "series"], where)
        return render_paired(spec, ctx, where, cid)
    groups = spec.get("groups") or [{"items": spec.get("items") or []}]
    unit, prefix = spec.get("unit", ""), spec.get("prefix", "")
    mode = spec.get("colors", "entity")
    vals = []
    for g in groups:
        if not g.get("items"):
            raise BuildError("%s 有一组没有 items" % where)
        for it in g["items"]:
            need(it, ["name"], where + " 的某根柱子")
            v, ci = it.get("value"), it.get("ci")
            if v is not None:
                vals.append(v)
            if ci:
                if len(ci) != 2 or v is None or not (ci[0] <= v <= ci[1]):
                    raise BuildError("%s「%s」的 ci %s 必须是 [下限, 上限] 并包含 value %s" % (where, it["name"], ci, v))
                vals.append(ci[1])
    if spec.get("max"):
        top, ticks = spec["max"], nice_scale(spec["max"])[1]
    else:
        top, ticks = nice_scale(max(vals) if vals else 1)
    if spec.get("ticks"):
        ticks = spec["ticks"]
    total = sum(len(g["items"]) for g in groups)
    orient = spec.get("orient", "auto")
    if total > 10:
        ctx.warn("%s 有 %d 根柱子,考虑拆图或合并成「其他」" % (where, total))
    out = [head(spec, cid)]
    if orient == "h":
        out.append(render_hbars(groups, ctx, where, top, unit, prefix, mode))
    elif orient == "v" or total <= 4:
        out.append(render_vbars(groups, ctx, where, top, ticks, unit, prefix, mode))
    else:
        # 柱子多:桌面竖向,手机自动换成横向,标签不会被挤碎
        out.append('<div class="c-v2h">%s</div><div class="c-h4m">%s</div>' % (
            render_vbars(groups, ctx, where, top, ticks, unit, prefix, mode),
            render_hbars(groups, ctx, where, top, unit, prefix, mode)))
    out.append("</figure>")
    return "".join(out)


def render_line(spec, ctx, where, cid):
    need(spec, ["title", "note", "x", "series"], where)
    x, y = spec["x"], spec.get("y") or {}
    labels = x.get("labels") or []
    n = len(labels)
    if n < 2:
        raise BuildError("%s x.labels 至少要 2 个" % where)
    W, H, X0 = 400.0, 240.0, 36.0
    if x.get("values"):
        xv = x["values"]
        if len(xv) != n:
            raise BuildError("%s x.values 和 x.labels 数量不一致" % where)
        f = (lambda v: math.log10(v)) if x.get("scale") == "log" else (lambda v: v)
        lo, hi = f(xv[0]), f(xv[-1])
        xs = [X0 + (f(v) - lo) / (hi - lo) * (W - X0) for v in xv]
    else:
        xs = [X0 + i * (W - X0) / (n - 1) for i in range(n)]
    unit, prefix = y.get("unit", ""), y.get("prefix", "")
    allv = [v for s in spec["series"] for v in s.get("values", []) if v is not None]
    thr = spec.get("threshold")
    if thr:
        allv.append(thr["value"])
    top, ticks = (y["max"], y.get("ticks") or nice_scale(y["max"])[1]) if y.get("max") else nice_scale(max(allv))
    if y.get("ticks"):
        ticks = y["ticks"]
    Y = lambda v: round(H - v / top * H, 1)
    svg = ['<svg viewBox="0 0 400 240" role="img" aria-label="%s">' % esc(spec["title"])]
    svg.append('<g style="stroke:var(--grid)" stroke-width="1">')
    for t in ticks:
        svg.append('<line x1="%s" x2="400" y1="%s" y2="%s"/>' % (X0, Y(t), Y(t)))
    svg.append("</g>")
    svg.append('<line x1="%s" x2="400" y1="240" y2="240" style="stroke:var(--axis)" stroke-width="1"/>' % X0)
    if thr:
        svg.append('<line x1="%s" x2="400" y1="%s" y2="%s" style="stroke:var(--axis)" stroke-width="1" stroke-dasharray="4 4"/>'
                   % (X0, Y(thr["value"]), Y(thr["value"])))
    ends, dots = [], []
    svg.append('<g fill="none" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">')
    for s in spec["series"]:
        need(s, ["name", "values"], where + " 的某条线")
        vs = s["values"]
        if len(vs) != n:
            raise BuildError("%s「%s」有 %d 个值,x 轴有 %d 个标签" % (where, s["name"], len(vs), n))
        mark, ink = ctx.color(s["name"], s.get("color"), where)
        seg = []
        for i, v in enumerate(vs + [None]):
            if v is not None:
                seg.append("%s,%s" % (round(xs[i], 1), Y(v)))
            elif seg:
                if len(seg) > 1:
                    svg.append('<polyline style="stroke:var(%s)" points="%s"/>' % (mark, " ".join(seg)))
                seg = []
        last = max((i for i, v in enumerate(vs) if v is not None), default=None)
        if last is None:
            raise BuildError("%s「%s」全是空值" % (where, s["name"]))
        dots.append('<circle cx="%s" cy="%s" r="4.5" style="fill:var(%s);stroke:var(--bg)" stroke-width="2"/>'
                    % (round(xs[last], 1), Y(vs[last]), mark))
        ends.append([Y(vs[last]) / H * 100, vs[last], s["name"], ink])
    svg.append("</g>")
    svg.extend(dots)
    svg.append("</svg>")
    if thr:
        ends.append([Y(thr["value"]) / H * 100, None, thr.get("label", ""), "--text-2"])
    ends.sort(key=lambda e: e[0])
    GAP = 7.0
    for i in range(1, len(ends)):
        if ends[i][0] - ends[i - 1][0] < GAP:
            ends[i][0] = ends[i - 1][0] + GAP
    ylab = "".join('<div class="c-y" style="top:%s%%">%s</div>' % (round(100 - pct(t, top), 2), esc(fmt(t, unit, prefix)))
                   for t in ticks)
    thr_html = ""
    step = max(1, math.ceil(n / 6))
    show = [i for i in range(n) if i % step == 0]
    if show[-1] != n - 1:
        if (n - 1) - show[-1] < step * 0.6:
            show.pop()
        show.append(n - 1)
    mcount = 3 if max(len(str(l)) for l in labels) >= 6 else 4
    mstep = max(1, math.ceil((n - 1) / (mcount - 1)))
    mshow = {i for i in range(0, n, mstep)} | {n - 1}
    if n - 1 - max(i for i in mshow if i != n - 1) < mstep * 0.6:
        mshow.discard(max(i for i in mshow if i != n - 1))
    xl = []
    for i in show:
        mh = "" if i in mshow else " mh"
        if i == n - 1:
            xl.append('<span class="last">%s</span>' % esc(labels[i]))
        else:
            xl.append('<span class="%s" style="left:%s%%">%s</span>' % (mh.strip(), round(xs[i] / W * 100, 2), esc(labels[i])))
    endh = "".join('<div style="top:%s%%;color:var(%s)"><b>%s</b>%s</div>' % (round(t, 2), ink, esc(fmt(v, unit, prefix)), esc(nm))
                   if v is not None else '<div class="thr" style="top:%s%%"><b><i></i></b>%s</div>' % (round(t, 2), esc(nm))
                   for t, v, nm, ink in ends)
    out = [head(spec, cid), '<div class="c-line">',
           '<div class="c-lplot">%s%s%s</div>' % ("".join(svg), ylab, thr_html),
           '<div class="c-ends">%s</div>' % endh,
           '<div class="c-x">%s</div><div></div>' % "".join(xl)]
    if x.get("title"):
        out.append('<div class="c-axis">%s</div>' % esc(x["title"]))
    out.append("</div></figure>")
    return "".join(out)


NUM_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def cell_num(c):
    t = c.get("v") if isinstance(c, dict) else c
    m = NUM_RE.search(str(t or ""))
    return float(m.group(0).replace(",", "")) if m else None


def render_table(spec, ctx, where, cid):
    need(spec, ["title", "note", "columns", "rows"], where)
    cols = spec["columns"]
    order = list(range(len(cols)))
    picks = [i for i, c in enumerate(cols) if c.get("pick")]
    if len(picks) > 1:
        raise BuildError("%s 只能有一个 pick 列" % where)
    if picks:
        order = picks + [i for i in order if i != picks[0]]
    minw = 150 + 120 * len(cols)
    hint = '<p class="c-hint">左右滑动查看全部列 →</p>' if minw > 375 else ""
    out = [head(spec, cid), '%s<div class="c-tbl"><table class="c-cmp" style="min-width:%dpx"><thead><tr><th></th>' % (hint, minw)]
    for i in order:
        c = cols[i]
        key = ctx.entities.get(c["name"])
        style = ' style="color:var(%s)"' % COLORS[key][1] if key in MAIN else ""
        out.append('<th%s%s>%s%s</th>' % (' class="pick"' if c.get("pick") else "", style, esc(c["name"]),
                                          '<span class="sub">%s</span>' % esc(c["sub"]) if c.get("sub") else ""))
    out.append("</tr></thead><tbody>")
    for r in spec["rows"]:
        need(r, ["name", "cells"], where + " 的某一行")
        cells = r["cells"]
        if len(cells) != len(cols):
            raise BuildError("%s 行「%s」有 %d 格,表头有 %d 列" % (where, r["name"], len(cells), len(cols)))
        best = set()
        if r.get("best") is not None:
            b = r["best"]
            best = set(b if isinstance(b, list) else [b])
        elif r.get("better") in ("high", "low"):
            nums = [(i, cell_num(c)) for i, c in enumerate(cells)]
            nums = [(i, v) for i, v in nums if v is not None]
            if len(nums) >= 2:
                target = (max if r["better"] == "high" else min)(v for _, v in nums)
                best = {i for i, v in nums if v == target}
            else:
                ctx.warn("%s 行「%s」解析不出数字,没有标最优;请用 best 指定列序号" % (where, r["name"]))
        out.append('<tr><th>%s%s</th>' % (esc(r["name"]), '<span class="sub">%s</span>' % esc(r["sub"]) if r.get("sub") else ""))
        for i in order:
            c = cells[i]
            v, sub = (c.get("v"), c.get("sub")) if isinstance(c, dict) else (c, None)
            cls = [k for k, on in (("pick", cols[i].get("pick")), ("best", i in best), ("none", v in (None, "", "—"))) if on]
            out.append('<td%s>%s%s</td>' % (' class="%s"' % " ".join(cls) if cls else "",
                                            esc(v if v not in (None, "") else "—"),
                                            '<span class="sub">%s</span>' % esc(sub) if sub else ""))
        out.append("</tr>")
    out.append("</tbody></table></div></figure>")
    return "".join(out)


RENDER = {"entities": render_entities, "stat": render_stat, "bar": render_bar, "line": render_line, "table": render_table}


# ---------------------------------------------------------------- 组装与截图

def build(src_text, ctx):
    if re.search(r"<html|<head|<body", src_text, re.I):
        raise BuildError("design.src.html 只写 <main> 里面的内容,不要写 <html>/<head>/<body>")
    styles = re.findall(r"<style[^>]*>(.*?)</style>", src_text, re.S)
    body = re.sub(r"<style[^>]*>.*?</style>", "", src_text, flags=re.S)
    blocks = list(BLOCK_RE.finditer(body))
    # 先收集 entities,保证后面所有图按声明取色
    for i, m in enumerate(blocks):
        if m.group(1) == "entities":
            render_entities(parse(m, i), ctx, "第 %d 个图表块" % (i + 1))

    def sub(m, counter=[0]):
        counter[0] += 1
        i = counter[0]
        kind = m.group(1)
        where = "第 %d 个图表块(%s)" % (i, kind)
        if kind not in RENDER:
            raise BuildError("%s 类型不存在,可选:%s" % (where, ", ".join(RENDER)))
        if kind == "entities":
            return ""
        ctx.counts[kind] = ctx.counts.get(kind, 0) + 1
        ctx.n += 1
        return RENDER[kind](parse(m, i - 1), ctx, where, "c%d" % ctx.n)

    body = BLOCK_RE.sub(sub, body)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    title = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else "design"
    if not h1:
        ctx.warn("没有 <h1>,<title> 暂用 design")
    with open(CSS_PATH, encoding="utf-8") as f:
        css = f.read()
    extra = "".join("<style>%s</style>" % s for s in styles)
    doc = ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
           '<title>%s</title>\n<style>\n%s</style>\n%s</head>\n<body>\n<main>\n%s\n</main>\n</body>\n</html>\n'
           % (esc(title), css, extra, body.strip()))
    if "gradient" in doc.lower():
        ctx.warn("输出里出现了 gradient,规定全文不用渐变")
    return doc


def parse(m, i):
    try:
        return json.loads(m.group(2))
    except json.JSONDecodeError as e:
        raise BuildError("第 %d 个图表块(%s)JSON 解析失败:块内第 %d 行第 %d 列,%s"
                         % (i + 1, m.group(1), e.lineno, e.colno, e.msg))


def find_chrome():
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(mac):
        return mac
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        p = shutil.which(name)
        if p:
            return p
    return None


def shoot(out_path):
    chrome = find_chrome()
    if not chrome:
        print("⚠ 没找到 Chrome/Chromium,跳过截图")
        return
    d = os.path.dirname(os.path.abspath(out_path))
    name = os.path.basename(out_path)
    stem = os.path.splitext(name)[0]
    probe = os.path.join(d, "_probe.html")
    with open(probe, "w", encoding="utf-8") as f:
        f.write('<iframe id="m" src="%s" style="border:0;width:375px;height:800px"></iframe>'
                '<iframe id="d" src="%s" style="border:0;width:1440px;height:800px"></iframe>'
                '<script>onload=function(){var m=document.getElementById("m").contentDocument.documentElement,'
                'e=document.getElementById("d").contentDocument.documentElement;'
                'document.title="sw="+m.scrollWidth+";mh="+m.scrollHeight+";dh="+e.scrollHeight}</script>' % (name, name))
    base = [chrome, "--headless", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files"]
    try:
        dom = subprocess.run(base + ["--virtual-time-budget=3000", "--dump-dom", "file://" + probe],
                             capture_output=True, text=True, timeout=60).stdout
        m = re.search(r"sw=(\d+);mh=(\d+);dh=(\d+)", dom)
        if not m:
            print("⚠ 没量到页面尺寸,跳过截图")
            return
        sw, mh, dh = (int(g) for g in m.groups())
        mh, dh = min(mh + 40, 16000), min(dh + 40, 16000)
        dpng, mpng = os.path.join(d, "desktop.png"), os.path.join(d, "mobile.png")
        subprocess.run(base + ["--window-size=1440,%d" % dh, "--screenshot=" + dpng, "file://" + os.path.abspath(out_path)],
                       capture_output=True, timeout=60)
        with open(probe, "w", encoding="utf-8") as f:
            f.write('<body style="margin:0"><iframe src="%s" style="border:0;width:375px;height:%dpx"></iframe></body>' % (name, mh))
        subprocess.run(base + ["--window-size=400,%d" % mh, "--screenshot=" + mpng, "file://" + probe],
                       capture_output=True, timeout=60)
    finally:
        if os.path.exists(probe):
            os.remove(probe)
    ok = "✓" if sw == 375 else "✗ 手机上页面横向溢出,检查宽表格/宽图"
    print("截图:%s  %s" % (os.path.basename(dpng), os.path.basename(mpng)))
    print("手机宽度:sw=%d %s" % (sw, ok))


def main():
    ap = argparse.ArgumentParser(description="把 design.src.html 构建成单文件 design.html")
    ap.add_argument("src")
    ap.add_argument("-o", "--out", help="输出路径,默认同目录 design.html")
    ap.add_argument("--shot", action="store_true", help="构建后截桌面图和手机图,并检查手机宽度")
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.src)), "design.html")
    ctx = Ctx()
    try:
        with open(a.src, encoding="utf-8") as f:
            doc = build(f.read(), ctx)
    except BuildError as e:
        print("✗ 构建失败:" + str(e), file=sys.stderr)
        sys.exit(1)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    kinds = "、".join("%s×%d" % (k, v) for k, v in ctx.counts.items()) or "无图表"
    print("✓ 已生成 %s(%s)" % (out, kinds))
    for w in ctx.warnings:
        print("⚠ " + w)
    if a.shot:
        shoot(out)


if __name__ == "__main__":
    main()
