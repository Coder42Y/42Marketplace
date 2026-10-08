#!/usr/bin/env python3
"""Regression tests for build.py. Standard library only.

  python3 -m unittest discover -s <skill-dir>/scripts -p 'test_*.py'

Assertions check behaviour and field names, never message wording, so the same file works
for every language variant of build.py.

The golden test compares against references/chart-sample.html. After changing build.py or
assets/base.css on purpose, regenerate it:

  python3 scripts/build.py references/chart-sample.src.html -o references/chart-sample.html
"""
import contextlib
import io
import os
import re
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build  # noqa: E402

REF = os.path.join(HERE, "..", "references")


def run(body):
    ctx = build.Ctx()
    return build.build("<h1>t</h1>" + body, ctx), ctx


def chart(kind, spec):
    import json
    # "</" inside a <script> block would end it early; JSON allows "<\/" instead (see chart-spec.md)
    return '<script type="application/json" data-chart="%s">%s</script>' % (
        kind, json.dumps(spec, ensure_ascii=False).replace("</", "<\\/"))


BAR = {"title": "t", "note": "n"}
LINE = {"title": "t", "note": "n", "x": {"labels": ["a", "b", "c"]}}


class Golden(unittest.TestCase):
    def test_sample_builds_byte_identical(self):
        with open(os.path.join(REF, "chart-sample.src.html"), encoding="utf-8") as f:
            doc = build.build(f.read(), build.Ctx())
        with open(os.path.join(REF, "chart-sample.html"), encoding="utf-8") as f:
            self.assertEqual(doc, f.read())


class Scale(unittest.TestCase):
    def test_max_off_step_has_no_tick_above_max(self):
        doc, _ = run(chart("bar", dict(BAR, max=90, items=[{"name": "a", "value": 80}])))
        bottoms = [float(b) for b in re.findall(r'class="c-tick" style="bottom:([\d.]+)%', doc)]
        self.assertTrue(bottoms)
        self.assertTrue(all(b <= 100 for b in bottoms))
        self.assertNotIn(">100<", doc)

    def test_bar_value_over_max_fails(self):
        with self.assertRaisesRegex(build.BuildError, "max"):
            run(chart("bar", dict(BAR, max=50, items=[{"name": "a", "value": 80}])))

    def test_bar_ci_over_max_fails(self):
        with self.assertRaisesRegex(build.BuildError, "max"):
            run(chart("bar", dict(BAR, max=50, items=[{"name": "a", "value": 40, "ci": [30, 60]}])))

    def test_line_value_over_ymax_fails(self):
        with self.assertRaisesRegex(build.BuildError, "max"):
            run(chart("line", dict(LINE, y={"max": 100}, series=[{"name": "s", "values": [10, 200, 30]}])))

    def test_paired_value_over_max_fails(self):
        with self.assertRaisesRegex(build.BuildError, "max"):
            run(chart("bar", dict(BAR, max=10, categories=["x"], series=[{"name": "s", "values": [20]}])))

    def test_ticks_without_max_keep_highest_tick(self):
        doc, _ = run(chart("bar", dict(BAR, ticks=[25, 50, 75, 100], items=[{"name": "a", "value": 80}])))
        self.assertIn(">100<", doc)

    def test_negative_values_fail(self):
        with self.assertRaises(build.BuildError):
            run(chart("bar", dict(BAR, items=[{"name": "a", "value": -5}])))
        with self.assertRaises(build.BuildError):
            run(chart("line", dict(LINE, series=[{"name": "s", "values": [1, -2, 3]}])))
        with self.assertRaises(build.BuildError):
            run(chart("bar", dict(BAR, categories=["x"], series=[{"name": "s", "values": [-1]}])))


class Malformed(unittest.TestCase):
    """Bad input must surface as BuildError, never as a raw Python exception."""

    def assertBuildError(self, body):
        with self.assertRaises(build.BuildError):
            run(body)

    def test_string_value(self):
        self.assertBuildError(chart("bar", dict(BAR, items=[{"name": "a", "value": "41%"}])))

    def test_string_max(self):
        self.assertBuildError(chart("bar", dict(BAR, max="100", items=[{"name": "a", "value": 4}])))

    def test_bool_value(self):
        self.assertBuildError(chart("bar", dict(BAR, items=[{"name": "a", "value": True}])))

    def test_line_all_null(self):
        self.assertBuildError(chart("line", dict(LINE, series=[{"name": "s", "values": [None, None, None]}])))

    def test_line_no_series(self):
        self.assertBuildError(chart("line", dict(LINE, series=[])))

    def test_threshold_without_value(self):
        self.assertBuildError(chart("line", dict(LINE, threshold={"label": "x"}, series=[{"name": "s", "values": [1, 2, 3]}])))

    def test_paired_notes_too_short(self):
        self.assertBuildError(chart("bar", dict(BAR, categories=["x", "y"], series=[{"name": "s", "values": [1, None], "notes": [None]}])))

    def test_paired_no_series(self):
        self.assertBuildError(chart("bar", dict(BAR, categories=["x"], series=[])))

    def test_table_columns_as_strings(self):
        self.assertBuildError(chart("table", {"title": "t", "note": "n", "columns": ["a", "b"], "rows": [{"name": "r", "cells": ["1", "2"]}]}))

    def test_stat_items_not_list(self):
        self.assertBuildError(chart("stat", {"title": "t", "note": "n", "items": {"label": "a"}}))

    def test_stat_items_empty(self):
        self.assertBuildError(chart("stat", {"title": "t", "note": "n", "items": []}))

    def test_entities_wrong_shape(self):
        self.assertBuildError(chart("entities", {"a": ["blue"]}))

    def test_misspelled_value_key(self):
        self.assertBuildError(chart("bar", dict(BAR, items=[{"name": "a", "val": 41}])))

    def test_explicit_null_value_is_allowed(self):
        doc, _ = run(chart("bar", dict(BAR, items=[{"name": "a", "value": None}, {"name": "b", "value": 2}])))
        self.assertIn('aria-label="', doc)

    def test_unknown_enum_values(self):
        self.assertBuildError(chart("bar", dict(BAR, colors="rainbow", items=[{"name": "a", "value": 1}])))
        self.assertBuildError(chart("bar", dict(BAR, orient="diagonal", items=[{"name": "a", "value": 1}])))

    def test_best_out_of_range(self):
        self.assertBuildError(chart("table", {"title": "t", "note": "n", "columns": [{"name": "a"}], "rows": [{"name": "r", "best": 3, "cells": ["1"]}]}))


class XValues(unittest.TestCase):
    def line(self, xv, scale=None):
        x = {"labels": ["a", "b", "c"], "values": xv}
        if scale:
            x["scale"] = scale
        return chart("line", dict(LINE, x=x, series=[{"name": "s", "values": [1, 2, 3]}]))

    def test_unsorted_fails(self):
        with self.assertRaisesRegex(build.BuildError, "x.values"):
            run(self.line([1, 100, 10]))

    def test_equal_ends_fails(self):
        with self.assertRaisesRegex(build.BuildError, "x.values"):
            run(self.line([5, 5, 5]))

    def test_log_nonpositive_fails(self):
        with self.assertRaisesRegex(build.BuildError, "x.values"):
            run(self.line([0, 10, 100], "log"))

    def test_log_ok(self):
        doc, _ = run(self.line([1, 10, 100], "log"))
        self.assertIn("<polyline", doc)


class Blocks(unittest.TestCase):
    def test_header_tag_is_allowed(self):
        doc, _ = run("<header>intro</header>")
        self.assertIn("<header>intro</header>", doc)

    def test_full_document_is_rejected(self):
        with self.assertRaises(build.BuildError):
            build.build("<html><body><h1>t</h1></body></html>", build.Ctx())

    def test_attribute_order_and_quotes(self):
        body = ("<script data-chart='bar' type='application/json'>"
                '{"title": "t", "note": "n", "items": [{"name": "a", "value": 1}]}</script>')
        doc, _ = run(body)
        self.assertIn('class="c-chart"', doc)
        self.assertNotIn("data-chart", doc)

    def test_unrecognised_block_fails(self):
        with self.assertRaisesRegex(build.BuildError, "data-chart"):
            run('<script type="text/json" data-chart="bar">{}</script>')


class Output(unittest.TestCase):
    def test_json_strings_are_escaped(self):
        doc, _ = run(chart("bar", dict(BAR, title="<script>alert(1)</script>", items=[{"name": "<b>x</b>", "value": 1}])))
        self.assertNotIn("<script>alert", doc)
        self.assertIn("&lt;script&gt;", doc)
        self.assertNotIn("<b>x</b>", doc)

    def test_title_not_double_escaped(self):
        doc = build.build("<h1>A &amp; B</h1>", build.Ctx())
        self.assertIn("<title>A &amp; B</title>", doc)

    def test_thousands_separator(self):
        doc, _ = run(chart("bar", dict(BAR, prefix="¥", items=[{"name": "a", "value": 5100}])))
        self.assertIn("¥5,100", doc)

    def test_gradient_word_in_prose_is_not_flagged(self):
        _, ctx = run("<p>gradient boosting</p>")
        self.assertFalse(any("gradient" in w for w in ctx.warnings))

    def test_style_attributes_are_kept(self):
        doc, _ = run('<style media="print">.x{color:red}</style>')
        self.assertIn('<style media="print">', doc)

    def test_isolated_point_between_nulls_is_drawn(self):
        doc, _ = run(chart("line", dict(LINE, x={"labels": ["a", "b", "c", "d", "e"]},
                                        series=[{"name": "s", "values": [1, None, 3, None, 5]}])))
        self.assertGreaterEqual(doc.count("<circle"), 3)

    def test_end_labels_stay_inside_plot(self):
        series = [{"name": "s%d" % i, "values": [5, 1, 0.1 * i]} for i in range(6)]
        doc, _ = run(chart("line", dict(LINE, y={"max": 10}, series=series)))
        ends = re.search(r'<div class="c-ends">(.*?)</div></div>|<div class="c-ends">(.*)', doc).group(0)
        tops = [float(t) for t in re.findall(r'top:([\d.-]+)%', ends)]
        self.assertTrue(tops)
        self.assertTrue(all(0 <= t <= 100 for t in tops), tops)

    def test_css_gradient_is_flagged(self):
        _, ctx = run('<style>.x{background:linear-gradient(red,blue)}</style>')
        self.assertTrue(any("gradient" in w for w in ctx.warnings))


class Table(unittest.TestCase):
    def table(self, row):
        return chart("table", {"title": "t", "note": "n", "columns": [{"name": "a"}, {"name": "b"}], "rows": [row]})

    def test_mixed_units_do_not_mark_best(self):
        doc, ctx = run(self.table({"name": "r", "better": "low", "cells": ["1.2s", "900ms"]}))
        self.assertNotIn('class="best"', doc)
        self.assertTrue(ctx.warnings)

    def test_same_units_mark_best(self):
        doc, _ = run(self.table({"name": "r", "better": "low", "cells": ["120ms", "900ms"]}))
        self.assertIn('class="best"', doc)

    def test_numeric_zero_cell_can_be_best(self):
        doc, _ = run(chart("table", {"title": "t", "note": "n", "columns": [{"name": "a"}, {"name": "b"}, {"name": "c"}],
                                     "rows": [{"name": "r", "better": "low", "cells": [0, 3, 6]}]}))
        first = re.search(r"<tbody><tr><th>r</th><td([^>]*)>", doc).group(1)
        self.assertIn("best", first)

    def test_row_without_better_or_best_warns(self):
        _, ctx = run(self.table({"name": "r", "cells": ["1", "2"]}))
        self.assertTrue(ctx.warnings)


class MobileLabels(unittest.TestCase):
    def test_phone_keeps_at_least_three_long_labels(self):
        for n in (4, 7, 10, 11, 12, 14, 17, 20, 23):
            labels = ["2026-%02d" % (i + 1) for i in range(n)]
            doc, _ = run(chart("line", dict(LINE, x={"labels": labels}, series=[{"name": "s", "values": list(range(1, n + 1))}])))
            xdiv = re.search(r'<div class="c-x">(.*?)</div>', doc).group(1)
            spans = re.findall(r"<span([^>]*)>", xdiv)
            visible = [s for s in spans if "mh" not in s]
            self.assertGreaterEqual(len(visible), 3, "n=%d" % n)


class Shot(unittest.TestCase):
    def test_missing_screenshot_is_reported_as_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "design.html")
            with open(out, "w") as f:
                f.write("<p>x</p>")
            stale = [os.path.join(d, n) for n in ("desktop.png", "mobile.png")]
            for p in stale:
                with open(p, "w") as f:
                    f.write("stale")
            dom = mock.Mock(stdout="<title>sw=375;mh=100;dh=100</title>")
            # Chrome "runs" but never writes the PNGs: stale files must not pass as fresh ones
            with mock.patch.object(build, "find_chrome", return_value="chrome"), \
                    mock.patch.object(build.subprocess, "run", return_value=dom), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertIsNone(build.shoot(out))
            self.assertFalse(any(os.path.exists(p) for p in stale))

    def test_overflow_exits_with_code_2(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "design.src.html")
            with open(src, "w") as f:
                f.write("<h1>t</h1>")
            with mock.patch.object(build, "shoot", return_value=420), \
                    mock.patch.object(sys, "argv", ["build.py", src, "--shot"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    build.main()
            self.assertEqual(cm.exception.code, 2)

    def test_unreadable_or_unwritable_paths_exit_1(self):
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "latin1.src.html")
            with open(bad, "wb") as f:
                f.write("<h1>caf\xe9</h1>".encode("latin-1"))
            ok = os.path.join(d, "ok.src.html")
            with open(ok, "w") as f:
                f.write("<h1>t</h1>")
            for argv in (["build.py", os.path.join(d, "missing.src.html")],
                         ["build.py", bad],
                         ["build.py", ok, "-o", os.path.join(d, "no-such-dir", "design.html")]):
                with mock.patch.object(sys, "argv", argv), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as cm:
                        build.main()
                self.assertEqual(cm.exception.code, 1, argv)


def node(i, at, zone=None, **kw):
    return dict({"id": i, "name": i.upper(), "sub": "s", "at": at}, **({"zone": zone} if zone else {}), **kw)


def arch(nodes, edges=(), **kw):
    return chart("arch", dict({"caption": "c", "nodes": nodes, "edges": list(edges)}, **kw))


def rects(doc):
    return [tuple(map(float, m)) for m in re.findall(
        r'<g class="a-n[^"]*"><rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', doc)]


def segments(doc):
    """Axis-aligned segments of every edge path; hop arcs count as part of their segment."""
    out = []
    for d in re.findall(r'<path class="a-e[^"]*" d="([^"]+)"', doc):
        pts = [tuple(map(float, p)) for p in re.findall(r"[ML]([\d.]+) ([\d.]+)", d)]
        out += list(zip(pts, pts[1:]))
    return out


def crosses(seg, r, inset=1):
    (x1, y1), (x2, y2) = seg
    x, y, w, h = r
    return (min(x1, x2) < x + w - inset and max(x1, x2) > x + inset
            and min(y1, y2) < y + h - inset and max(y1, y2) > y + inset)


# 2x2 block whose diagonal edges cannot use an L shape: forces the Z routes
GRID = [node("a", [0, 0], "z"), node("b", [1, 0], "z"), node("c", [0, 1], "z"), node("d", [1, 1], "z"),
        node("u", [2, 0]), node("e", [0, 3])]
GRID_EDGES = [{"from": "a", "to": "c"}, {"from": "a", "to": "d"}, {"from": "c", "to": "b"},
              {"from": "d", "to": "b"}, {"from": "b", "to": "u", "label": "HTTPS"}, {"from": "e", "to": "c"}]


class Arch(unittest.TestCase):
    def test_renders_zones_nodes_and_arrows(self):
        doc, ctx = run(arch(GRID, GRID_EDGES, zones=[{"id": "z", "name": "线上", "tone": "green"}]))
        self.assertEqual(len(rects(doc)), len(GRID))
        self.assertEqual(doc.count('class="a-n t-green"'), 4)
        self.assertEqual(doc.count('class="a-n t-gray"'), 2)
        self.assertIn('class="a-z"', doc)
        self.assertIn(">HTTPS<", doc)
        self.assertEqual(len(re.findall(r'<path class="a-e', doc)), len(GRID_EDGES))
        self.assertIn('role="img"', doc)
        self.assertEqual(ctx.counts.get("arch"), 1)

    def test_lines_never_pass_through_nodes(self):
        doc, _ = run(arch(GRID, GRID_EDGES, zones=[{"id": "z", "name": "线上"}]))
        for seg in segments(doc):
            for r in rects(doc):
                self.assertFalse(crosses(seg, r), (seg, r))

    def test_no_two_lines_share_a_segment(self):
        _, ctx = run(arch(GRID, GRID_EDGES, zones=[{"id": "z", "name": "线上"}]))
        self.assertFalse([w for w in ctx.warnings if "重叠" in w], ctx.warnings)

    def test_crossing_gets_a_hop(self):
        doc, _ = run(arch(GRID, GRID_EDGES, zones=[{"id": "z", "name": "线上"}]))
        self.assertRegex(doc, r'<path class="a-e[^"]*" d="[^"]*A6 6')

    def test_blocked_route_fails(self):
        # a -> c has to pass b in the same row
        with self.assertRaises(build.BuildError):
            run(arch([node("a", [0, 0]), node("b", [1, 0]), node("c", [2, 0])], [{"from": "a", "to": "c"}]))

    def test_forced_route_is_used(self):
        nodes = [node("a", [0, 0]), node("b", [1, 1])]
        doc_hv, _ = run(arch(nodes, [{"from": "a", "to": "b", "route": "hv"}]))
        doc_vh, _ = run(arch(nodes, [{"from": "a", "to": "b", "route": "vh"}]))
        self.assertNotEqual(segments(doc_hv), segments(doc_vh))
        with self.assertRaises(build.BuildError):
            run(arch([node("a", [0, 0]), node("b", [1, 0])], [{"from": "a", "to": "b", "route": "hv"}]))

    def test_zone_must_be_a_clean_rectangle(self):
        with self.assertRaises(build.BuildError):
            run(arch([node("a", [0, 0], "z"), node("x", [1, 0]), node("b", [2, 0], "z")],
                     zones=[{"id": "z", "name": "z"}]))

    def test_bad_input_fails(self):
        for body in (arch([node("a", [0, 0]), node("b", [0, 0])]),                       # same cell
                     arch([node("a", [0, 0])], [{"from": "a", "to": "nope"}]),            # unknown id
                     arch([node("a", [0, 0], m=[0, 0]), node("b", [1, 0])]),              # m on some nodes only
                     arch([node("a", [0, -1])]),                                          # negative cell
                     arch([node("a", ["0", 0])]),                                         # string cell
                     arch([node("a", [0, 0], tone="pink")]),                              # unknown tone
                     arch([node("a", [0, 0], "nozone")]),                                 # undeclared zone
                     arch([node("a", [0, 0])], legend={"bogus": "x"})):
            with self.assertRaises(build.BuildError):
                run(body)

    def test_meaning_without_legend_warns(self):
        _, ctx = run(arch([node("a", [0, 0], "z"), node("b", [1, 0], "z", tone="gray")],
                          [{"from": "a", "to": "b", "dash": True, "flow": "out"}],
                          zones=[{"id": "z", "name": "z", "tone": "blue"}]))
        self.assertEqual(len(ctx.warnings), 3, ctx.warnings)   # dash, flow, gray node in a blue zone

    def test_empty_rows_and_columns_are_compressed(self):
        near, _ = run(arch([node("a", [0, 0]), node("b", [1, 1])], [{"from": "a", "to": "b"}]))
        far, _ = run(arch([node("a", [0, 0]), node("b", [4, 6])], [{"from": "a", "to": "b"}]))
        self.assertEqual(near, far)

    def test_label_widens_its_gap(self):
        def gap(label):
            doc, _ = run(arch([node("a", [0, 0]), node("b", [1, 0])], [{"from": "a", "to": "b", "label": label}]))
            (x1, _, w1, _), (x2, _, _, _) = rects(doc)
            return x2 - (x1 + w1)
        self.assertGreater(gap("一二三四五六"), gap("ssh"))

    def test_wide_diagram_scrolls_on_phones_unless_mobile_layout_given(self):
        wide = [node("n%d" % i, [i, 0]) for i in range(4)]
        doc, ctx = run(arch(wide))
        self.assertIn('class="scroll-x"', doc)
        self.assertTrue(ctx.warnings)
        for i, n in enumerate(wide):
            n["m"] = [0, i]
        doc, _ = run(arch(wide))
        self.assertIn('class="only-desktop"', doc)
        self.assertIn('class="only-mobile"', doc)
        self.assertNotIn('class="scroll-x"', doc)
        # marker ids stay unique when both layouts are in one page
        ids = re.findall(r'<marker id="([^"]+)"', doc)
        self.assertEqual(len(ids), len(set(ids)))


class MobileOverflow(unittest.TestCase):
    def test_long_end_labels_wrap_on_phones(self):
        with open(build.CSS_PATH, encoding="utf-8") as f:
            css = f.read()
        phone = css[css.index("@media (max-width: 560px)"):]
        self.assertRegex(phone, r"\.c-ends div \{[^}]*white-space: normal")
        self.assertRegex(phone, r"\.c-line \{[^}]*minmax\(0, 1fr\)")


if __name__ == "__main__":
    unittest.main()
