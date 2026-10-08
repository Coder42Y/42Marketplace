#!/usr/bin/env python3
"""design-html 构建脚本:把 design.src.html 渲染成单文件 design.html。

  python3 build.py design.src.html            # 输出同目录的 design.html
  python3 build.py design.src.html --shot     # 另外截桌面图、手机图,并检查手机宽度

design.src.html 只写 <main> 里的内容。图表写成
  <script type="application/json" data-chart="entities|stat|bar|line|table|arch">{...}</script>
格式见 references/chart-spec.md。只用 Python 3 标准库。
退出码:0 成功;1 构建失败;2 构建成功但手机上页面横向溢出。
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
import tempfile
import urllib.parse
from pathlib import Path

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
COLOR_MODES = ["entity", "ramp"] + list(COLORS)
ORIENTS = ["auto", "v", "h"]

LOCK = ('<svg width="18" height="22" viewBox="0 0 18 22" aria-hidden="true">'
        '<path d="M4 10V7a5 5 0 0 1 10 0v3" fill="none" stroke="currentColor" stroke-width="2"/>'
        '<rect x="1" y="10" width="16" height="11" rx="2" fill="currentColor"/></svg>')

# type 和 data-chart 的先后顺序、单双引号都不限
BLOCK_RE = re.compile(
    r'<script\b(?=[^>]*\btype\s*=\s*["\']application/json["\'])'
    r'(?=[^>]*\bdata-chart\s*=\s*["\'](\w+)["\'])[^>]*>(.*?)</script>', re.S | re.I)


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


# ---------------------------------------------------------------- 校验与数值工具

def show(v):
    return json.dumps(v, ensure_ascii=False)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def num(v, where, field, allow_none=False):
    """数值字段:必须是非负的数;allow_none 时 null 表示没法测。"""
    if v is None and allow_none:
        return None
    if not is_num(v):
        raise BuildError("%s 的 %s 必须是数字,现在是 %s" % (where, field, show(v)))
    if v < 0:
        raise BuildError("%s 的 %s 是负数 %s,暂不支持负值" % (where, field, show(v)))
    return v


def as_list(v, where, field, nonempty=True):
    if not isinstance(v, list):
        raise BuildError("%s 的 %s 必须是数组 [...]" % (where, field))
    if nonempty and not v:
        raise BuildError("%s 的 %s 不能为空" % (where, field))
    return v


def as_obj(v, where, field):
    if not isinstance(v, dict):
        raise BuildError("%s 的 %s 必须是对象 {...}" % (where, field))
    return v


def need(spec, keys, where):
    as_obj(spec, where, "这一项")
    for k in keys:
        if spec.get(k) in (None, ""):
            raise BuildError("%s 缺少必填字段 \"%s\"" % (where, k))


def pick_enum(v, allowed, where, field):
    if v not in allowed:
        raise BuildError("%s 的 %s 不认识 %s,可选:%s" % (where, field, show(v), ", ".join(allowed)))
    return v


def fmt(v, unit="", prefix=""):
    if v is None:
        return "—"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = "{:,}".format(v) if abs(v) >= 1000 else str(v)
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


def scale(mx, ticks, maxv, where, field="max"):
    """返回 (满量程, 刻度)。数据超过给定的满量程直接报错,刻度不超过满量程。"""
    if mx is not None:
        mx = num(mx, where, field)
        if mx <= 0:
            raise BuildError("%s 的 %s 必须大于 0" % (where, field))
        if maxv > mx + 1e-9:
            raise BuildError("%s 有值 %s 超过 %s %s;调大 %s,或者去掉它让脚本自动取整"
                             % (where, fmt(maxv), field, fmt(mx), field))
        top, auto = mx, nice_scale(mx)[1]
    else:
        top, auto = nice_scale(maxv)
    if ticks is not None:
        auto = [num(t, where, "ticks") for t in as_list(ticks, where, "ticks")]
        if mx is None:
            top = max([top] + auto)
    return top, [t for t in auto if 0 < t <= top + 1e-9]


def pct(v, top):
    return round(max(0.0, min(100.0, v / top * 100.0)), 2)


def head(spec, cid):
    return ('<figure class="c-chart" role="group" aria-labelledby="%s">'
            '<figcaption class="c-head"><h3 id="%s">%s</h3><p>%s</p></figcaption>'
            % (cid, cid, esc(spec["title"]), esc(spec["note"])))


# ---------------------------------------------------------------- 各图表

def render_entities(spec, ctx, where):
    if not isinstance(spec, dict):
        raise BuildError("%s entities 应该是 {\"名字\": \"颜色\"}" % where)
    for name, key in spec.items():
        if not isinstance(key, str) or key not in COLORS:
            raise BuildError("%s 实体「%s」的颜色 %s 不存在,可选:%s" % (where, name, key, ", ".join(COLORS)))
        ctx.entities[name] = key
    return ""


def render_stat(spec, ctx, where, cid):
    need(spec, ["title", "note", "items"], where)
    out = [head(spec, cid), '<div class="c-stats">']
    for it in as_list(spec["items"], where, "items"):
        as_obj(it, where, "items[]")
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
    need(spec, ["categories", "series"], where)
    cats = as_list(spec["categories"], where, "categories")
    series = as_list(spec["series"], where, "series")
    unit, prefix = spec.get("unit", ""), spec.get("prefix", "")
    vals = []
    for s in series:
        need(s, ["name", "values"], where + " 的某个系列")
        vs = as_list(s["values"], where, "series[].values")
        if len(vs) != len(cats):
            raise BuildError("%s「%s」有 %d 个值,categories 有 %d 个" % (where, s["name"], len(vs), len(cats)))
        if s.get("notes") is not None and len(as_list(s["notes"], where, "series[].notes")) != len(cats):
            raise BuildError("%s「%s」的 notes 要和 categories 一样长(%d 个)" % (where, s["name"], len(cats)))
        vals += [v for v in (num(v, where, "series[].values", allow_none=True) for v in vs) if v is not None]
    top = scale(spec.get("max"), None, max(vals) if vals else 0, where)[0]
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
    if spec.get("categories") is not None or spec.get("series") is not None:
        return render_paired(spec, ctx, where, cid)
    groups = as_list(spec.get("groups") or [{"items": spec.get("items")}], where, "groups")
    unit, prefix = spec.get("unit", ""), spec.get("prefix", "")
    mode = pick_enum(spec.get("colors", "entity"), COLOR_MODES, where, "colors")
    orient = pick_enum(spec.get("orient", "auto"), ORIENTS, where, "orient")
    vals = []
    for g in groups:
        as_obj(g, where, "groups[]")
        for it in as_list(g.get("items"), where, "items"):
            need(it, ["name"], where + " 的某根柱子")
            if "value" not in it:
                raise BuildError('%s「%s」缺少 value;没法测请写 "value": null' % (where, it["name"]))
            v = num(it.get("value"), where, "「%s」的 value" % it["name"], allow_none=True)
            if v is not None:
                vals.append(v)
            ci = it.get("ci")
            if ci is not None:
                ci = [num(c, where, "「%s」的 ci" % it["name"]) for c in as_list(ci, where, "ci")]
                if len(ci) != 2 or v is None or not (ci[0] <= v <= ci[1]):
                    raise BuildError("%s「%s」的 ci %s 必须是 [下限, 上限] 并包含 value %s" % (where, it["name"], show(ci), show(v)))
                vals.append(ci[1])
    top, ticks = scale(spec.get("max"), spec.get("ticks"), max(vals) if vals else 0, where)
    total = sum(len(g["items"]) for g in groups)
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


def x_positions(x, n, where, X0, W):
    if x.get("values") is None:
        return [X0 + i * (W - X0) / (n - 1) for i in range(n)]
    xv = as_list(x["values"], where, "x.values")
    if len(xv) != n:
        raise BuildError("%s x.values 和 x.labels 数量不一致" % where)
    if not all(is_num(v) for v in xv):
        raise BuildError("%s x.values 必须都是数字" % where)
    if any(b <= a for a, b in zip(xv, xv[1:])):
        raise BuildError("%s x.values 必须严格递增" % where)
    if pick_enum(x.get("scale", "linear"), ["linear", "log"], where, "x.scale") == "log":
        if xv[0] <= 0:
            raise BuildError("%s x.values 在对数刻度下必须都大于 0" % where)
        xv = [math.log10(v) for v in xv]
    return [X0 + (v - xv[0]) / (xv[-1] - xv[0]) * (W - X0) for v in xv]


def phone_labels(show, labels):
    """手机上显示的横轴标签:从桌面显示的标签里均匀挑 3–4 个,首尾必留。"""
    want = 3 if max(len(str(l)) for l in labels) >= 6 else 4
    if len(show) <= want:
        return set(show)
    return {show[int(round(k * (len(show) - 1) / (want - 1)))] for k in range(want)}


def render_line(spec, ctx, where, cid):
    need(spec, ["title", "note", "x", "series"], where)
    x, y = as_obj(spec["x"], where, "x"), as_obj(spec.get("y") or {}, where, "y")
    labels = as_list(x.get("labels"), where, "x.labels")
    n = len(labels)
    if n < 2:
        raise BuildError("%s x.labels 至少要 2 个" % where)
    W, H, X0 = 400.0, 240.0, 36.0
    xs = x_positions(x, n, where, X0, W)
    unit, prefix = y.get("unit", ""), y.get("prefix", "")
    series = as_list(spec["series"], where, "series")
    allv = []
    for s in series:
        need(s, ["name", "values"], where + " 的某条线")
        vs = as_list(s["values"], where, "series[].values")
        if len(vs) != n:
            raise BuildError("%s「%s」有 %d 个值,x 轴有 %d 个标签" % (where, s["name"], len(vs), n))
        got = [v for v in (num(v, where, "「%s」的 values" % s["name"], allow_none=True) for v in vs) if v is not None]
        if not got:
            raise BuildError("%s「%s」全是空值" % (where, s["name"]))
        allv += got
    thr = spec.get("threshold")
    if thr is not None:
        as_obj(thr, where, "threshold")
        allv.append(num(thr.get("value"), where, "threshold.value"))
    top, ticks = scale(y.get("max"), y.get("ticks"), max(allv), where, "y.max")
    Y = lambda v: round(H - v / top * H, 1)
    svg = ['<svg viewBox="0 0 400 240" role="img" aria-label="%s">' % esc(spec["title"])]
    svg.append('<g style="stroke:var(--grid)" stroke-width="1">')
    for t in ticks:
        svg.append('<line x1="%s" x2="400" y1="%s" y2="%s"/>' % (X0, Y(t), Y(t)))
    svg.append("</g>")
    svg.append('<line x1="%s" x2="400" y1="240" y2="240" style="stroke:var(--axis)" stroke-width="1"/>' % X0)
    if thr is not None:
        svg.append('<line x1="%s" x2="400" y1="%s" y2="%s" style="stroke:var(--axis)" stroke-width="1" stroke-dasharray="4 4"/>'
                   % (X0, Y(thr["value"]), Y(thr["value"])))
    ends, dots = [], []
    svg.append('<g fill="none" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">')
    for s in series:
        vs = s["values"]
        mark, ink = ctx.color(s["name"], s.get("color"), where)
        seg = []
        for i, v in enumerate(vs + [None]):
            if v is not None:
                seg.append("%s,%s" % (round(xs[i], 1), Y(v)))
            elif seg:
                if len(seg) > 1:
                    svg.append('<polyline style="stroke:var(%s)" points="%s"/>' % (mark, " ".join(seg)))
                else:
                    cx, cy = seg[0].split(",")
                    svg.append('<circle cx="%s" cy="%s" r="3" style="fill:var(%s)" stroke="none"/>' % (cx, cy, mark))
                seg = []
        last = max(i for i, v in enumerate(vs) if v is not None)
        dots.append('<circle cx="%s" cy="%s" r="4.5" style="fill:var(%s);stroke:var(--bg)" stroke-width="2"/>'
                    % (round(xs[last], 1), Y(vs[last]), mark))
        ends.append([Y(vs[last]) / H * 100, vs[last], s["name"], ink])
    svg.append("</g>")
    svg.extend(dots)
    svg.append("</svg>")
    if thr is not None:
        ends.append([Y(thr["value"]) / H * 100, None, thr.get("label", ""), "--text-2"])
    ends.sort(key=lambda e: e[0])
    GAP = 7.0
    for i in range(1, len(ends)):
        if ends[i][0] - ends[i - 1][0] < GAP:
            ends[i][0] = ends[i - 1][0] + GAP
    # 往下推到图外的标签再往回收,保证都在绘图区内
    if ends and ends[-1][0] > 100:
        ends[-1][0] = 100.0
        for i in range(len(ends) - 2, -1, -1):
            ends[i][0] = max(0.0, min(ends[i][0], ends[i + 1][0] - GAP))
    ylab = "".join('<div class="c-y" style="top:%s%%">%s</div>' % (round(100 - pct(t, top), 2), esc(fmt(t, unit, prefix)))
                   for t in ticks)
    step = max(1, math.ceil(n / 6))
    show = [i for i in range(n) if i % step == 0]
    if show[-1] != n - 1:
        if (n - 1) - show[-1] < step * 0.6:
            show.pop()
        show.append(n - 1)
    mshow = phone_labels(show, labels)
    xl = []
    for i in show:
        if i == n - 1:
            xl.append('<span class="last">%s</span>' % esc(labels[i]))
        else:
            xl.append('<span class="%s" style="left:%s%%">%s</span>' % ("" if i in mshow else "mh", round(xs[i] / W * 100, 2), esc(labels[i])))
    endh = "".join('<div style="top:%s%%;color:var(%s)"><b>%s</b>%s</div>' % (round(t, 2), ink, esc(fmt(v, unit, prefix)), esc(nm))
                   if v is not None else '<div class="thr" style="top:%s%%"><b><i></i></b>%s</div>' % (round(t, 2), esc(nm))
                   for t, v, nm, ink in ends)
    out = [head(spec, cid), '<div class="c-line">',
           '<div class="c-lplot">%s%s</div>' % ("".join(svg), ylab),
           '<div class="c-ends">%s</div>' % endh,
           '<div class="c-x">%s</div><div></div>' % "".join(xl)]
    if x.get("title"):
        out.append('<div class="c-axis">%s</div>' % esc(x["title"]))
    out.append("</div></figure>")
    return "".join(out)


NUM_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def cell_num(c):
    """从格子文本里取出 (单位, 数值);单位是数字前后的文字,如 ¥、%、ms。"""
    v = c.get("v") if isinstance(c, dict) else c
    t = "" if v is None else str(v)
    m = NUM_RE.search(t)
    if not m:
        return None
    return (t[:m.start()].strip(), t[m.end():].strip()), float(m.group(0).replace(",", ""))


def row_best(r, cells, ncols, ctx, where):
    if r.get("best") is not None:
        b = r["best"] if isinstance(r["best"], list) else [r["best"]]
        for i in b:
            if not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < ncols:
                raise BuildError("%s 行「%s」的 best %s 不是有效的列序号(0–%d)" % (where, r["name"], show(i), ncols - 1))
        return set(b)
    better = r.get("better")
    if better is None:
        ctx.warn("%s 行「%s」没写 better 或 best,没有标最优" % (where, r["name"]))
        return set()
    pick_enum(better, ["high", "low"], where, "better")
    nums = [(i, cell_num(c)) for i, c in enumerate(cells)]
    nums = [(i, p) for i, p in nums if p is not None]
    if len(nums) < 2:
        ctx.warn("%s 行「%s」解析不出数字,没有标最优;请用 best 指定列序号" % (where, r["name"]))
        return set()
    if len({p[0] for _, p in nums}) > 1:
        ctx.warn("%s 行「%s」各格单位不一致,没有标最优;请统一单位或用 best 指定列序号" % (where, r["name"]))
        return set()
    target = (max if better == "high" else min)(p[1] for _, p in nums)
    return {i for i, p in nums if p[1] == target}


def render_table(spec, ctx, where, cid):
    need(spec, ["title", "note", "columns", "rows"], where)
    cols = as_list(spec["columns"], where, "columns")
    for c in cols:
        need(c, ["name"], where + " 的某一列")
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
    for r in as_list(spec["rows"], where, "rows"):
        need(r, ["name", "cells"], where + " 的某一行")
        cells = as_list(r["cells"], where, "cells")
        if len(cells) != len(cols):
            raise BuildError("%s 行「%s」有 %d 格,表头有 %d 列" % (where, r["name"], len(cells), len(cols)))
        best = row_best(r, cells, len(cols), ctx, where)
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


# ---------------------------------------------------------------- 架构图

TONES = ["blue", "green", "orange", "violet", "gray"]
FLOWS = {"main": "--flow-main", "out": "--flow-out", "in": "--flow-in"}
LEGEND_KEYS = ["dash"] + list(FLOWS) + TONES
A_PAD, A_MINW, A_H1, A_H2 = 18, 136, 44, 60   # 节点左右内边距、最小宽、单行高、双行高
A_CGAP, A_RGAP = 56, 44                       # 列间距、行间距
A_ZPAD, A_ZTOP, A_ZGAP, A_EDGE = 20, 40, 24, 4  # 分组内边距、分组顶部标题区、分组间距、画布留边
A_HOP = 6                                     # 交叉处小弧半径


def text_w(s, size):
    """估算文字宽度(px)。中文按 1em,ASCII 按字形宽窄估,宁宽勿窄。"""
    w = 0.0
    for ch in str(s):
        if ch in " .,:;|!il'`ijt()[]":
            w += 0.34
        elif ch.isascii() and ch.isupper():
            w += 0.68
        elif ch.isascii():
            w += 0.58
        else:
            w += 1.0
    return w * size


def cell_of(v, where, field):
    if (not isinstance(v, list) or len(v) != 2
            or not all(isinstance(x, int) and not isinstance(x, bool) and x >= 0 for x in v)):
        raise BuildError("%s 的 %s 必须是 [列, 行],两个从 0 开始的整数,现在是 %s" % (where, field, show(v)))
    return tuple(v)


def between(a, b):
    """a、b 之间(不含两端)的整数。"""
    lo, hi = sorted((a, b))
    return range(lo + 1, hi)


ROUTES = ["hv", "vh", "vhv", "hvh"]


def arch_route(a, b, occupied, where, ea, eb, want=None):
    """在网格上列出一条边所有不穿过节点的走法,每种是 (形状, (起点所在边, 终点所在边))。

    同行、同列走直线;否则依次试 L 形(hv 先横后竖、vh 先竖后横)和 Z 形
    (vhv 在起点下/上方的行间空隙里横穿、hvh 在起点右/左侧的列间空隙里竖穿)。
    want 指定走法时只试那一种。
    """
    (c1, r1), (c2, r2) = a, b
    if want is not None and (r1 == r2 or c1 == c2):
        raise BuildError("%s「%s」→「%s」两端同行或同列,走直线,不用写 route" % (where, ea, eb))
    if r1 == r2:
        if any((c, r1) in occupied for c in between(c1, c2)):
            raise BuildError("%s「%s」→「%s」同一行,但中间隔着别的节点;调整 at 空出一条通道" % (where, ea, eb))
        return [("h", ("R", "L") if c2 > c1 else ("L", "R"))]
    if c1 == c2:
        if any((c1, r) in occupied for r in between(r1, r2)):
            raise BuildError("%s「%s」→「%s」同一列,但中间隔着别的节点;调整 at 空出一条通道" % (where, ea, eb))
        return [("v", ("B", "T") if r2 > r1 else ("T", "B"))]
    h, v = ("R", "L") if c2 > c1 else ("L", "R"), ("B", "T") if r2 > r1 else ("T", "B")
    tries = {
        # 经过的格子;拐角格也算
        "hv": ([(c, r1) for c in between(c1, c2)] + [(c2, r1)] + [(c2, r) for r in between(r1, r2)], (h[0], v[1])),
        "vh": ([(c1, r) for r in between(r1, r2)] + [(c1, r2)] + [(c, r2) for c in between(c1, c2)], (v[0], h[1])),
        "vhv": ([(c2, r) for r in between(r1, r2)], v),
        "hvh": ([(c, r2) for c in between(c1, c2)], h),
    }
    ok = [(shape, tries[shape][1]) for shape in ([want] if want else ROUTES)
          if not any(p in occupied for p in tries[shape][0])]
    if ok:
        return ok
    if want:
        raise BuildError("%s「%s」→「%s」按 route %s 走会穿过别的节点;换一种 route 或调整 at" % (where, ea, eb, want))
    raise BuildError("%s「%s」→「%s」所有折线走法都会穿过别的节点;调整 at,让两端同行、同列,或空出拐角" % (where, ea, eb))


def simplify(pts):
    """去掉重复点和共线的中间点。"""
    out = []
    for p in pts:
        if out and p == out[-1]:
            continue
        if len(out) >= 2 and (out[-2][0] == out[-1][0] == p[0] or out[-2][1] == out[-1][1] == p[1]):
            out[-1] = p
            continue
        out.append(p)
    return out


def hop_path(pts, cuts):
    """把折线点列写成 path;cuts[i] 是第 i 段上要跨过去的交叉点坐标。"""
    d = ["M%g %g" % pts[0]]
    for i in range(1, len(pts)):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i]
        horiz = y0 == y1
        sign = 1 if (x1 > x0 if horiz else y1 > y0) else -1
        for t in sorted(cuts.get(i - 1, []), key=lambda t: t * sign):
            if horiz:
                d.append("L%g %g A%d %d 0 0 %d %g %g" % (t - sign * A_HOP, y0, A_HOP, A_HOP, 1 if sign > 0 else 0, t + sign * A_HOP, y0))
            else:
                d.append("L%g %g A%d %d 0 0 %d %g %g" % (x0, t - sign * A_HOP, A_HOP, A_HOP, 1 if sign > 0 else 0, x0, t + sign * A_HOP))
        d.append("L%g %g" % (x1, y1))
    return " ".join(d)


def arch_svg(spec, nodes, zones, edges, key, ctx, where, cid):
    """按 key("at" 桌面 / "m" 手机)给出的网格坐标排版,返回 (svg, 画布宽)。"""
    # 空行空列压掉,只保留先后顺序
    cmap = {c: i for i, c in enumerate(sorted({n[key][0] for n in nodes}))}
    rmap = {r: i for i, r in enumerate(sorted({n[key][1] for n in nodes}))}
    pos = {n["id"]: (cmap[n[key][0]], rmap[n[key][1]]) for n in nodes}
    occupied = {}
    for n in nodes:
        if pos[n["id"]] in occupied:
            raise BuildError("%s「%s」和「%s」的 %s 都是 %s" % (where, occupied[pos[n["id"]]]["name"], n["name"], key, list(pos[n["id"]])))
        occupied[pos[n["id"]]] = n
    ncol = max(p[0] for p in pos.values()) + 1
    nrow = max(p[1] for p in pos.values()) + 1

    # 分组外框 = 成员节点的格子范围;框里不能有别的节点,框和框不能重叠
    box = {}
    for z in zones:
        cells = [pos[n["id"]] for n in nodes if n.get("zone") == z["id"]]
        if not cells:
            continue
        c0, c1 = min(c for c, _ in cells), max(c for c, _ in cells)
        r0, r1 = min(r for _, r in cells), max(r for _, r in cells)
        for (c, r), n in occupied.items():
            if c0 <= c <= c1 and r0 <= r <= r1 and n.get("zone") != z["id"]:
                raise BuildError("%s「%s」落在分组「%s」的框里但不属于它;调整 %s,让每个分组占一块连续的矩形"
                                 % (where, n["name"], z["name"], key))
        for zid, (a0, a1, b0, b1) in box.items():
            if a0 <= c1 and c0 <= a1 and b0 <= r1 and r0 <= b1:
                raise BuildError("%s 分组「%s」和「%s」的框重叠了;调整 %s" % (where, zones_by_id(zones)[zid]["name"], z["name"], key))
        box[z["id"]] = (c0, c1, r0, r1)

    # 网格上列出每条边的可行走法,再挑重叠最少、交叉最少、拐弯最少的组合
    options = [arch_route(pos[e["from"]], pos[e["to"]], occupied, where, e["_a"]["name"], e["_b"]["name"], e.get("route"))
               for e in edges]

    def segs(pts):
        return [(pts[j], pts[j + 1]) for j in range(len(pts) - 1)]

    def geometry(routes):
        # 列宽、行高、间距
        sub_any = any(n.get("sub") for n in nodes)
        H = A_H2 if sub_any else A_H1
        colw = [A_MINW] * ncol
        for n in nodes:
            c = pos[n["id"]][0]
            colw[c] = max(colw[c], int(math.ceil(max(text_w(n["name"], 15), text_w(n.get("sub") or "", 13)) + 2 * A_PAD)))
        # 分组标题要能放进第一列中线左边,从顶上居中进框的线才不会压到它
        zmap_ = zones_by_id(zones)
        for zid, bx in box.items():
            colw[bx[0]] = max(colw[bx[0]], int(math.ceil(2 * (text_w(zmap_[zid]["name"], 14) + 26 - A_ZPAD))))

        def zgap(i, lo_ix, hi_ix, axis_top=False):
            ends = sum(1 for bx in box.values() if bx[hi_ix] == i)
            starts = sum(1 for bx in box.values() if bx[lo_ix] == i + 1)
            if not (ends or starts):
                return 0, 0
            return ends * A_ZPAD + starts * (A_ZTOP if axis_top else A_ZPAD) + A_ZGAP, ends + starts

        cgap = []
        for c in range(ncol - 1):
            g, k = zgap(c, 0, 1)
            g = max(A_CGAP, g)
            for e, (shape, _) in zip(edges, routes):
                if shape == "h" and e.get("label") and sorted((pos[e["from"]][0], pos[e["to"]][0])) == [c, c + 1]:
                    g = max(g, int(math.ceil(text_w(e["label"], 13))) + 24 + k * A_ZPAD)
            cgap.append(g)
        rgap = []
        for r in range(nrow - 1):
            g = max(A_RGAP, zgap(r, 2, 3, True)[0])
            for e, (shape, _) in zip(edges, routes):
                if shape == "v" and e.get("label") and sorted((pos[e["from"]][1], pos[e["to"]][1])) == [r, r + 1]:
                    # 竖线旁的标签要落在两个分组框之间的空白里,不压框线和分组标题
                    g = max(g, sum(A_ZPAD for bx in box.values() if bx[3] == r)
                            + sum(A_ZTOP for bx in box.values() if bx[2] == r + 1) + 28)
            rgap.append(g)
        x0 = A_EDGE + (A_ZPAD if any(bx[0] == 0 for bx in box.values()) else 0)
        y0 = A_EDGE + (A_ZTOP if any(bx[2] == 0 for bx in box.values()) else 0)
        xs, ys = [x0], [y0]
        for c in range(ncol - 1):
            xs.append(xs[-1] + colw[c] + cgap[c])
        for r in range(nrow - 1):
            ys.append(ys[-1] + H + rgap[r])

        def rect(nid):
            c, r = pos[nid]
            return xs[c], ys[r], colw[c], H

        def free_span(i, axis):
            """第 i 和 i+1 列(axis=0)或行(axis=1)之间、去掉分组框内边距和标题区以后的空白。"""
            if axis == 0:
                lo = xs[i] + colw[i] + (A_ZPAD if any(bx[1] == i for bx in box.values()) else 0)
                hi = xs[i + 1] - (A_ZPAD if any(bx[0] == i + 1 for bx in box.values()) else 0)
            else:
                lo = ys[i] + H + (A_ZPAD if any(bx[3] == i for bx in box.values()) else 0)
                hi = ys[i + 1] - (A_ZTOP if any(bx[2] == i + 1 for bx in box.values()) else 0)
            return lo, hi

        # Z 形线在起点旁边的空隙里穿行;同一条空隙里有几根就均匀错开
        channel, lanes = {}, {}
        for i, (e, (shape, _)) in enumerate(zip(edges, routes)):
            (c1, r1), (c2, r2) = pos[e["from"]], pos[e["to"]]
            if shape == "vhv":
                channel[i] = (1, r1 if r2 > r1 else r1 - 1)
            elif shape == "hvh":
                channel[i] = (0, c1 if c2 > c1 else c1 - 1)
            else:
                continue
            lanes.setdefault(channel[i], []).append(i)
        lane_at = {}
        for (axis, gi), lst in lanes.items():
            lo, hi = free_span(gi, axis)
            for k, i in enumerate(lst):
                lane_at[i] = round(lo + (hi - lo) * (k + 1) / (len(lst) + 1), 1)

        # 同一条边上挂多根线时均匀错开端口,按另一端的位置排序,减少交叉
        ports = {}
        for i, (e, (_, (sa, sb))) in enumerate(zip(edges, routes)):
            ports.setdefault((e["from"], sa), []).append((i, e["to"]))
            ports.setdefault((e["to"], sb), []).append((i, e["from"]))
        port_at = {}
        for (nid, side), lst in ports.items():
            x, y, w, h = rect(nid)
            if side in "LR":
                lst.sort(key=lambda t: (pos[t[1]][1], pos[t[1]][0]))
                for k, (i, _) in enumerate(lst):
                    port_at[(i, nid)] = (x if side == "L" else x + w, round(y + h * (k + 1) / (len(lst) + 1), 1), side)
            else:
                lst.sort(key=lambda t: (pos[t[1]][0], pos[t[1]][1]))
                for k, (i, _) in enumerate(lst):
                    port_at[(i, nid)] = (round(x + w * (k + 1) / (len(lst) + 1), 1), y if side == "T" else y + h, side)

        def nudge(p, gap=2):
            """端点离节点留 2px,箭头尖不压边框。"""
            x, y, side = p
            return {"L": (x - gap, y), "R": (x + gap, y), "T": (x, y - gap), "B": (x, y + gap)}[side]

        lines = []
        for i, (e, (shape, (sa, sb))) in enumerate(zip(edges, routes)):
            pa, pb = port_at[(i, e["from"])], port_at[(i, e["to"])]
            na, nb = len(ports[(e["from"], sa)]), len(ports[(e["to"], sb)])
            if shape in ("h", "v"):
                k = 1 if shape == "h" else 0   # 横线对齐 y,竖线对齐 x
                if pa[k] != pb[k]:
                    if nb == 1:
                        pb = tuple(pa[k] if j == k else pb[j] for j in range(3))
                    elif na == 1:
                        pa = tuple(pb[k] if j == k else pa[j] for j in range(3))
                A, B = nudge(pa), nudge(pb)
                if A[k] == B[k]:
                    pts = [A, B]
                elif shape == "h":
                    xm = round((A[0] + B[0]) / 2, 1)
                    pts = [A, (xm, A[1]), (xm, B[1]), B]
                else:
                    ym = round((A[1] + B[1]) / 2, 1)
                    pts = [A, (A[0], ym), (B[0], ym), B]
            elif shape == "hv":
                A, B = nudge(pa), nudge(pb)
                pts = [A, (B[0], A[1]), B]
            elif shape == "vh":
                A, B = nudge(pa), nudge(pb)
                pts = [A, (A[0], B[1]), B]
            elif shape == "vhv":
                A, B, m = nudge(pa), nudge(pb), lane_at[i]
                pts = [A, (A[0], m), (B[0], m), B]
            else:
                A, B, m = nudge(pa), nudge(pb), lane_at[i]
                pts = [A, (m, A[1]), (m, B[1]), B]
            lines.append(simplify(pts))

        # 线和线:共线重叠要警告;十字交叉时后画的那条跨小弧
        cuts, overlaps = [dict() for _ in lines], []
        for i, pi in enumerate(lines):
            for j in range(i):
                for si, (p, q) in enumerate(segs(pi)):
                    for (u, v) in segs(lines[j]):
                        ph, uh = p[1] == q[1], u[1] == v[1]
                        if ph == uh:
                            a_ = 1 if ph else 0
                            if p[a_] == u[a_] and min(max(p[1 - a_], q[1 - a_]), max(u[1 - a_], v[1 - a_])) - max(min(p[1 - a_], q[1 - a_]), min(u[1 - a_], v[1 - a_])) > 0:
                                overlaps.append((i, j))
                            continue
                        h1, h2, vv1, vv2 = (p, q, u, v) if ph else (u, v, p, q)
                        X, Y = vv1[0], h1[1]
                        if (min(h1[0], h2[0]) + A_HOP < X < max(h1[0], h2[0]) - A_HOP
                                and min(vv1[1], vv2[1]) + A_HOP < Y < max(vv1[1], vv2[1]) - A_HOP):
                            cuts[i].setdefault(si, []).append(X if ph else Y)

        score = len(overlaps) * 1000 + sum(len(c) for cut in cuts for c in cut.values()) * 10 + sum(len(p) - 2 for p in lines)
        return dict(xs=xs, ys=ys, colw=colw, H=H, lines=lines, cuts=cuts, overlaps=overlaps, score=score,
                    free_span=free_span, routes=routes)

    pick = [0] * len(edges)
    g = geometry([o[0] for o in options])
    for _ in range(2):
        for i, opts in enumerate(options):
            for k in range(len(opts)):
                if k == pick[i]:
                    continue
                trial = pick[:i] + [k] + pick[i + 1:]
                t = geometry([o[j] for o, j in zip(options, trial)])
                if t["score"] < g["score"]:
                    pick, g = trial, t
    xs, ys, colw, H, lines, cuts, routes, free_span = (g[k] for k in ("xs", "ys", "colw", "H", "lines", "cuts", "routes", "free_span"))
    for i, j in g["overlaps"]:
        ctx.warn("%s「%s」→「%s」和「%s」→「%s」的线有一段重叠;调整 at 或用 route 换走法"
                 % (where, edges[i]["_a"]["name"], edges[i]["_b"]["name"], edges[j]["_a"]["name"], edges[j]["_b"]["name"]))

    def rect(nid):
        c, r = pos[nid]
        return xs[c], ys[r], colw[c], H

    W = xs[-1] + colw[-1] + (A_ZPAD if any(bx[1] == ncol - 1 for bx in box.values()) else 0) + A_EDGE
    Ht = ys[-1] + H + (A_ZPAD if any(bx[3] == nrow - 1 for bx in box.values()) else 0) + A_EDGE
    label = spec.get("label") or spec["caption"]
    out = ['<svg viewBox="0 0 %d %d" style="max-width:%dpx" role="img" aria-label="%s">' % (W, Ht, W, esc(label))]

    colors = sorted({e.get("flow") or "" for e in edges})
    out.append("<defs>")
    for f in colors:
        out.append('<marker id="%s-ah%s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="10" markerHeight="10" '
                   'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M2 1.5 9 5 2 8.5" class="a-ah" '
                   'style="stroke:var(%s)"/></marker>' % (cid, f, FLOWS.get(f, "--a-line")))
    out.append("</defs>")

    zmap = zones_by_id(zones)
    for zid, (c0, c1, r0, r1) in box.items():
        bx, by = xs[c0] - A_ZPAD, ys[r0] - A_ZTOP
        bw, bh = xs[c1] + colw[c1] + A_ZPAD - bx, ys[r1] + H + A_ZPAD - by
        # 从顶上进框的竖线会穿过分组标题:标题往右挪到线的右边
        tw = text_w(zmap[zid]["name"], 14)
        lx = bx + 16
        for x_ in sorted(p[0] for pts in lines for p, q in segs(pts)
                         if p[0] == q[0] and min(p[1], q[1]) < by + A_ZTOP and max(p[1], q[1]) > by):
            if lx - 8 < x_ < lx + tw + 8:
                lx = x_ + 10
        if lx + tw > bx + bw - 8:
            ctx.warn("%s 分组「%s」的标题被进框的线挡住了;调整 at 或缩短分组名" % (where, zmap[zid]["name"]))
        out.append('<g class="a-z"><rect x="%g" y="%g" width="%g" height="%g" rx="12"/><text x="%g" y="%g">%s</text></g>'
                   % (bx, by, bw, bh, lx, by + 25, esc(zmap[zid]["name"])))

    for i, (e, pts) in enumerate(zip(edges, lines)):
        f = e.get("flow") or ""
        attrs = ' marker-end="url(#%s-ah%s)"' % (cid, f)
        if e.get("both"):
            attrs += ' marker-start="url(#%s-ah%s)"' % (cid, f)
        style = "stroke:var(%s)" % FLOWS.get(f, "--a-line")
        out.append('<path class="a-e%s" d="%s" style="%s"%s/>' % (" dash" if e.get("dash") else "", hop_path(pts, cuts[i]), style, attrs))

    def free_mid(i, axis):
        return sum(free_span(i, axis)) / 2

    for e, pts, (shape, _) in zip(edges, lines, routes):
        if not e.get("label"):
            continue
        (p, q) = max(segs(pts), key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
        if p[1] == q[1]:
            a_, b_ = sorted((pos[e["from"]][0], pos[e["to"]][0]))
            mx = free_mid(a_, 0) if shape == "h" and b_ - a_ == 1 else (p[0] + q[0]) / 2
            out.append('<text class="a-lab" x="%g" y="%g" text-anchor="middle">%s</text>' % (mx, p[1] - 8, esc(e["label"])))
        else:
            a_, b_ = sorted((pos[e["from"]][1], pos[e["to"]][1]))
            my = free_mid(a_, 1) if shape == "v" and b_ - a_ == 1 else (p[1] + q[1]) / 2
            out.append('<text class="a-lab" x="%g" y="%g" dominant-baseline="central">%s</text>' % (p[0] + 8, my, esc(e["label"])))

    for n in nodes:
        x, y, w, h = rect(n["id"])
        cx, cy = x + w / 2, y + h / 2
        t = ('<text class="t" x="%g" y="%g">%s</text><text class="s" x="%g" y="%g">%s</text>'
             % (cx, cy - 10, esc(n["name"]), cx, cy + 11, esc(n["sub"])) if n.get("sub")
             else '<text class="t" x="%g" y="%g">%s</text>' % (cx, cy, esc(n["name"])))
        out.append('<g class="a-n t-%s"><rect x="%g" y="%g" width="%g" height="%g" rx="6"/>%s</g>' % (n["_tone"], x, y, w, h, t))
    out.append("</svg>")
    return "".join(out), W


def zones_by_id(zones):
    return {z["id"]: z for z in zones}


def arch_legend(legend):
    items = []
    for k, text in legend.items():
        if k == "dash":
            mark = '<svg width="28" height="10" aria-hidden="true"><line x1="1" y1="5" x2="27" y2="5" class="a-e dash" style="stroke:var(--a-line)"/></svg>'
        elif k in FLOWS:
            mark = '<svg width="28" height="10" aria-hidden="true"><line x1="1" y1="5" x2="27" y2="5" class="a-e" style="stroke:var(%s)"/></svg>' % FLOWS[k]
        else:
            mark = '<svg width="20" height="14" aria-hidden="true" class="a-n t-%s"><rect x="0.5" y="0.5" width="19" height="13" rx="3"/></svg>' % k
        items.append("<span>%s%s</span>" % (mark, esc(text)))
    return '<div class="a-legend">%s</div>' % "".join(items)


def render_arch(spec, ctx, where, cid):
    need(spec, ["caption", "nodes"], where)
    zones = as_list(spec.get("zones") or [], where, "zones", nonempty=False)
    zmap = {}
    for z in zones:
        need(z, ["id", "name"], where + " 的某个分组")
        if z["id"] in zmap:
            raise BuildError("%s 分组 id「%s」重复了" % (where, z["id"]))
        if z.get("tone") is not None:
            pick_enum(z["tone"], TONES, where, "分组「%s」的 tone" % z["name"])
        zmap[z["id"]] = z
    nodes = as_list(spec["nodes"], where, "nodes")
    nmap = {}
    for n in nodes:
        need(n, ["id", "name", "at"], where + " 的某个节点")
        if n["id"] in nmap:
            raise BuildError("%s 节点 id「%s」重复了" % (where, n["id"]))
        n["at"] = cell_of(n["at"], where, "「%s」的 at" % n["name"])
        if n.get("m") is not None:
            n["m"] = cell_of(n["m"], where, "「%s」的 m" % n["name"])
        if n.get("zone") is not None and n["zone"] not in zmap:
            raise BuildError("%s「%s」的 zone「%s」没有在 zones 里声明" % (where, n["name"], n["zone"]))
        if n.get("tone") is not None:
            pick_enum(n["tone"], TONES, where, "「%s」的 tone" % n["name"])
        n["_tone"] = n.get("tone") or (zmap[n["zone"]].get("tone") if n.get("zone") else None) or "gray"
        nmap[n["id"]] = n
    has_m = [n for n in nodes if n.get("m") is not None]
    if has_m and len(has_m) != len(nodes):
        raise BuildError("%s 只有部分节点写了 m(手机版坐标);要么都写,要么都不写" % where)
    legend = as_obj(spec.get("legend") or {}, where, "legend")
    for k in legend:
        pick_enum(k, LEGEND_KEYS, where, "legend 的键")
    edges = as_list(spec.get("edges") or [], where, "edges", nonempty=False)
    for e in edges:
        need(e, ["from", "to"], where + " 的某条连线")
        for end in ("from", "to"):
            if e[end] not in nmap:
                raise BuildError("%s 连线的 %s「%s」不是已声明的节点 id" % (where, end, e[end]))
        if e["from"] == e["to"]:
            raise BuildError("%s 连线「%s」→「%s」首尾是同一个节点" % (where, e["from"], e["to"]))
        if e.get("flow") is not None:
            pick_enum(e["flow"], list(FLOWS), where, "连线的 flow")
        if e.get("route") is not None:
            pick_enum(e["route"], ROUTES, where, "连线的 route")
        e["_a"], e["_b"] = nmap[e["from"]], nmap[e["to"]]
        if e.get("label") and text_w(e["label"], 13) > 90:
            ctx.warn("%s「%s」→「%s」的线上标签「%s」太长;线上只写协议、端口这类短词,解释写进 caption"
                     % (where, e["_a"]["name"], e["_b"]["name"], e["label"]))

    # 图里有含义的线型、颜色都要在图例里
    if any(e.get("dash") for e in edges) and "dash" not in legend:
        ctx.warn('%s 用了虚线,但 legend 里没写 "dash" 的含义' % where)
    for f in sorted({e["flow"] for e in edges if e.get("flow")}):
        if f not in legend:
            ctx.warn('%s 用了 flow「%s」,但 legend 里没写它的含义' % (where, f))
    for n in nodes:
        zt = zmap[n["zone"]].get("tone") if n.get("zone") else None
        if n["_tone"] != (zt or "gray") and n["_tone"] not in legend:
            ctx.warn("%s「%s」的颜色 %s 和所在分组不同,legend 里要写 %s 表示什么" % (where, n["name"], n["_tone"], n["_tone"]))

    for z in zones:
        if not any(n.get("zone") == z["id"] for n in nodes):
            ctx.warn("%s 分组「%s」没有节点,不画" % (where, z["name"]))

    desk, W = arch_svg(spec, nodes, zones, edges, "at", ctx, where, cid)
    out = ['<figure class="diagram arch">']
    if has_m:
        mob, _ = arch_svg(spec, nodes, zones, edges, "m", ctx, where + "(手机版)", cid + "m")
        out.append(desk.replace("<svg ", '<svg class="only-desktop" ', 1))
        out.append(mob.replace("<svg ", '<svg class="only-mobile" ', 1))
    elif W > 440:
        # 手机上缩到 0.8 倍以下字就太小了:改成横滑,并提示补手机版坐标
        out.append('<div class="scroll-x">%s</div>' % desk.replace(
            'style="max-width:%dpx"' % W, 'style="max-width:%dpx;min-width:%dpx"' % (W, int(W * 0.8)), 1))
        ctx.warn("%s 宽 %dpx,手机上要横滑;给每个节点加 m(手机版坐标)排成纵向更好读" % (where, W))
    else:
        out.append(desk)
    if legend:
        out.append(arch_legend(legend))
    out.append("<figcaption>%s</figcaption></figure>" % esc(spec["caption"]))
    return "".join(out)


RENDER = {"entities": render_entities, "stat": render_stat, "bar": render_bar, "line": render_line,
          "table": render_table, "arch": render_arch}
# 写错字段类型时渲染函数可能抛出的异常,统一转成带位置的 BuildError
SHAPE_ERRORS = (TypeError, ValueError, KeyError, AttributeError, IndexError, ZeroDivisionError)


# ---------------------------------------------------------------- 组装与截图

def build(src_text, ctx):
    if re.search(r"<(html|head|body)\b", src_text, re.I):
        raise BuildError("design.src.html 只写 <main> 里面的内容,不要写 <html>/<head>/<body>")
    styles = re.findall(r"(<style[^>]*>.*?</style>)", src_text, re.S)
    body = re.sub(r"<style[^>]*>.*?</style>", "", src_text, flags=re.S)
    blocks = list(BLOCK_RE.finditer(body))
    # 先收集 entities,保证后面所有图按声明取色
    for i, m in enumerate(blocks):
        if m.group(1) == "entities":
            try:
                render_entities(parse(m, i), ctx, "第 %d 个图表块" % (i + 1))
            except SHAPE_ERRORS as e:
                raise BuildError("第 %d 个图表块(entities)格式不对(%s: %s)" % (i + 1, type(e).__name__, e))

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
        try:
            return RENDER[kind](parse(m, i - 1), ctx, where, "c%d" % ctx.n)
        except SHAPE_ERRORS as e:
            raise BuildError("%s 格式不对(%s: %s),对照 references/chart-spec.md 检查字段类型" % (where, type(e).__name__, e))

    body = BLOCK_RE.sub(sub, body)
    if re.search(r"\bdata-chart\s*=", body):
        raise BuildError('有图表块没被识别,请写成 <script type="application/json" data-chart="类型">…</script>')
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    title = html.unescape(re.sub(r"<[^>]+>", "", h1.group(1))).strip() if h1 else "design"
    if not h1:
        ctx.warn("没有 <h1>,<title> 暂用 design")
    with open(CSS_PATH, encoding="utf-8") as f:
        css = f.read()
    extra = "".join(styles)
    doc = ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
           '<title>%s</title>\n<style>\n%s</style>\n%s</head>\n<body>\n<main>\n%s\n</main>\n</body>\n</html>\n'
           % (esc(title), css, extra, body.strip()))
    if re.search(r"-gradient\s*\(|<(linear|radial)Gradient\b", doc, re.I):
        ctx.warn("输出里出现了 gradient,规定全文不用渐变")
    return doc


def parse(m, i):
    try:
        return json.loads(m.group(2))
    except json.JSONDecodeError as e:
        hint = ";字符串里有 </script> 时要写成 <\\/script>" if e.msg.startswith("Unterminated string") else ""
        raise BuildError("第 %d 个图表块(%s)JSON 解析失败:块内第 %d 行第 %d 列,%s%s"
                         % (i + 1, m.group(1), e.lineno, e.colno, e.msg, hint))


def find_chrome():
    for p in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(p):
            return p
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    return None


def shoot(out_path):
    """截桌面图和手机图。返回手机宽度下的 scrollWidth;截不了图时返回 None。"""
    chrome = find_chrome()
    if not chrome:
        print("⚠ 没找到 Chrome/Chromium,跳过截图")
        return None
    out = Path(out_path).resolve()
    src = urllib.parse.quote(out.name)
    fd, probe_name = tempfile.mkstemp(prefix="_probe-", suffix=".html", dir=str(out.parent))
    os.close(fd)
    probe = Path(probe_name)
    base = [chrome, "--headless", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files"]
    try:
        probe.write_text('<iframe id="m" src="%s" style="border:0;width:375px;height:800px"></iframe>'
                         '<iframe id="d" src="%s" style="border:0;width:1440px;height:800px"></iframe>'
                         '<script>onload=function(){var m=document.getElementById("m").contentDocument.documentElement,'
                         'e=document.getElementById("d").contentDocument.documentElement;'
                         'document.title="sw="+m.scrollWidth+";mh="+m.scrollHeight+";dh="+e.scrollHeight}</script>'
                         % (src, src), encoding="utf-8")
        dom = subprocess.run(base + ["--virtual-time-budget=3000", "--dump-dom", probe.as_uri()],
                             capture_output=True, text=True, timeout=60).stdout
        m = re.search(r"sw=(\d+);mh=(\d+);dh=(\d+)", dom)
        if not m:
            print("⚠ 没量到页面尺寸,跳过截图")
            return None
        sw, mh, dh = (int(g) for g in m.groups())
        mh, dh = min(mh + 40, 16000), min(dh + 40, 16000)
        dpng, mpng = out.parent / "desktop.png", out.parent / "mobile.png"
        for png in (dpng, mpng):
            if png.is_file():
                png.unlink()
        subprocess.run(base + ["--window-size=1440,%d" % dh, "--screenshot=%s" % dpng, out.as_uri()],
                       capture_output=True, timeout=60)
        probe.write_text('<body style="margin:0"><iframe src="%s" style="border:0;width:375px;height:%dpx"></iframe></body>'
                         % (src, mh), encoding="utf-8")
        subprocess.run(base + ["--window-size=400,%d" % mh, "--screenshot=%s" % mpng, probe.as_uri()],
                       capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("⚠ 截图超时,跳过截图")
        return None
    except OSError as e:
        print("⚠ 截图写不进 %s(%s),跳过截图" % (out.parent, e))
        return None
    finally:
        if probe.exists():
            probe.unlink()
    if not (dpng.is_file() and mpng.is_file()):
        print("⚠ Chrome 没有写出截图,跳过截图")
        return None
    ok = "✓" if sw == 375 else "✗ 手机上页面横向溢出,检查宽表格、宽图或过长的图表标签"
    print("截图:%s  %s" % (dpng.name, mpng.name))
    print("手机宽度:sw=%d %s" % (sw, ok))
    return sw


def main():
    ap = argparse.ArgumentParser(description="把 design.src.html 构建成单文件 design.html")
    ap.add_argument("src")
    ap.add_argument("-o", "--out", help="输出路径,默认同目录 design.html")
    ap.add_argument("--shot", action="store_true", help="构建后截桌面图和手机图,并检查手机宽度")
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.src)), "design.html")
    ctx = Ctx()
    try:
        try:
            with open(a.src, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            raise BuildError("读不到 %s(%s)" % (a.src, getattr(e, "strerror", None) or e))
        doc = build(text, ctx)
        try:
            with open(out, "w", encoding="utf-8") as f:
                f.write(doc)
        except OSError as e:
            raise BuildError("写不进 %s(%s)" % (out, e.strerror or e))
    except BuildError as e:
        print("✗ 构建失败:" + str(e), file=sys.stderr)
        sys.exit(1)
    kinds = "、".join("%s×%d" % (k, v) for k, v in ctx.counts.items()) or "无图表"
    print("✓ 已生成 %s(%s)" % (out, kinds))
    for w in ctx.warnings:
        print("⚠ " + w)
    if a.shot:
        sw = shoot(out)
        if sw is not None and sw != 375:
            sys.exit(2)


if __name__ == "__main__":
    main()
