#!/usr/bin/env python3
"""Pull one day's Claude Code sessions for a project out of ~/.claude/projects.

Scans every session touched that day (all project dirs) and sorts them into:
  - matched:   the project dir name or the session cwd contains --project
  - mentioned: started elsewhere (e.g. ~/Codes) but that day's messages and
               tool calls mention --keyword at least --min-mentions times
  - other:     everything else, listed by title only
Matched and mentioned sessions get one condensed text file each (user messages,
including ones typed while the agent was busy, plus substantial assistant
replies; subagent chatter dropped). Messages already seen in an earlier file
(resumed / forked sessions) are written only once. Read index.md first, then
only the session files you need.

Usage:
  extract_day.py --date 2026-10-12 --project my-app-workspace --keyword my-app --out DIR
  (--date defaults to today in the machine's local timezone; --keyword defaults to --project)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.expanduser("~/.claude/projects")
SKIP_USER_PREFIXES = ("<task-notification", "<local-command", "<command-name>/clear")
OUT_NAME = re.compile(r"^\d{4}-[0-9a-f]{8}\.txt$")


def local_window(day: str) -> tuple[str, str]:
    """UTC bounds of a local calendar day; adds the day before converting so DST days are right."""
    d = datetime.fromisoformat(day)
    fmt = lambda x: x.astimezone().astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    return fmt(d), fmt(d + timedelta(days=1))


def to_local(ts: str) -> str:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%H:%M")


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text"
        )
    return ""


def tool_inputs(content) -> str:
    if not isinstance(content, list):
        return ""
    return " ".join(
        json.dumps(x.get("input", {}), ensure_ascii=False)
        for x in content if isinstance(x, dict) and x.get("type") == "tool_use"
    )


def user_text(d: dict) -> str:
    """Text the user typed: a normal user turn, or a prompt queued while the agent was busy."""
    if d.get("type") == "user":
        if d.get("isMeta"):
            return ""
        txt = text_of((d.get("message") or {}).get("content")).strip()
        if d.get("isCompactSummary"):
            return "[compact summary of EARLIER work, not this day's]\n" + txt[:800]
        return txt
    att = d.get("attachment")
    if d.get("type") == "attachment" and isinstance(att, dict) and att.get("type") == "queued_command" \
            and att.get("commandMode", "prompt") == "prompt":
        p = att.get("prompt")
        return ("[typed while the agent was working] " + p.strip()) if isinstance(p, str) and p.strip() else ""
    return ""


def condense(path, lo, hi, a, keyword, project, seen):
    title = ai_title = branch = cwd = ""
    mentions, cwd_hit, shared = 0, False, 0
    first = last = None
    lines: list[str] = []
    for raw in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(d, dict):
            continue
        t = d.get("type")
        if t == "custom-title":
            title = d.get("customTitle") or title
            continue
        if t == "ai-title":
            ai_title = d.get("aiTitle") or ai_title
            continue
        if d.get("isSidechain"):
            continue
        ts = d.get("timestamp")
        if not isinstance(ts, str) or not (lo <= ts[:19] < hi):
            continue
        uid = d.get("uuid")
        if uid and uid in seen:
            shared += 1
            continue
        if uid:
            seen.add(uid)
        c = d.get("cwd") or ""
        cwd = c or cwd
        cwd_hit = cwd_hit or project in c
        branch = d.get("gitBranch") or branch
        content = (d.get("message") or {}).get("content")
        if t == "assistant":
            body = text_of(content).strip()
            mentions += (body + tool_inputs(content)).lower().count(keyword)
            if len(body) < a.ai_min:
                continue
            lines.append(f"\n--- AI {to_local(ts)}\n{body[:a.cap]}")
        else:
            body = user_text(d)
            if not body or body.startswith(SKIP_USER_PREFIXES) or "Subagent hand-back" in body:
                continue
            mentions += body.lower().count(keyword)
            if body.startswith("Base directory for this skill:"):
                body = body.splitlines()[0] + "  [skill body omitted]"
            lines.append(f"\n=== USER {to_local(ts)}\n{body[:a.cap]}")
        first = first or ts
        last = ts
    return title or ai_title, branch, cwd, first, last, lines, mentions, cwd_hit, shared


def valid_date(s: str) -> str:
    try:
        return date.fromisoformat(s).isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError("use YYYY-MM-DD, e.g. 2026-10-12")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", type=valid_date, default=date.today().isoformat())
    ap.add_argument("--project", required=True, help="substring of the project dir / cwd, e.g. my-app-workspace")
    ap.add_argument("--keyword", help="content keyword for sessions started elsewhere (default: --project)")
    ap.add_argument("--min-mentions", type=int, default=10)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ai-min", type=int, default=200, help="drop assistant texts shorter than this")
    ap.add_argument("--cap", type=int, default=4000, help="truncate each message to this many chars")
    a = ap.parse_args()

    lo, hi = local_window(a.date)
    keyword = (a.keyword or a.project).lower()
    day_start = datetime.fromisoformat(a.date).astimezone().timestamp()
    os.makedirs(a.out, exist_ok=True)
    for old in os.listdir(a.out):  # drop files from an earlier run so only this day's remain
        if OUT_NAME.match(old) or old == "index.md":
            os.remove(os.path.join(a.out, old))

    groups = {"matched": [], "mentioned": [], "other": []}
    seen: set[str] = set()
    files = [p for p in glob.glob(os.path.join(ROOT, "*", "*.jsonl")) if os.path.getmtime(p) >= day_start]
    for path in sorted(files, key=os.path.getmtime):  # older file first, so forks dedupe into the original
        title, branch, cwd, first, last, lines, mentions, cwd_hit, shared = condense(
            path, lo, hi, a, keyword, a.project, seen)
        if not lines:
            continue
        title = title or "(untitled)"
        if a.project in os.path.basename(os.path.dirname(path)) or cwd_hit:
            group, why = "matched", "dir/cwd"
        elif mentions >= a.min_mentions:
            group, why = "mentioned", f"{mentions}× '{keyword}'"
        else:
            groups["other"].append((first, f"| {to_local(first)}–{to_local(last)} | {title} | {cwd} |"))
            continue
        sid = os.path.basename(path)[:-6]
        name = f"{to_local(first).replace(':', '')}-{sid[:8]}.txt"
        note = f"; {shared} msgs already in an earlier file (resume/fork)" if shared else ""
        with open(os.path.join(a.out, name), "w", encoding="utf-8") as f:
            f.write(f"# {title}\nsession {sid}\ncwd {cwd}\nbranch {branch}\n"
                    f"active {to_local(first)}–{to_local(last)} (local)\nmatch {why}{note}\n")
            f.write("\n".join(lines))
        size = sum(len(x) for x in lines)
        users = sum(1 for x in lines if x.startswith("\n=== USER"))
        groups[group].append((first, f"| {to_local(first)}–{to_local(last)} | {title} | {branch or cwd} | "
                                     f"{why}{note} | {users} | {size // 1000}k | {name} |"))

    def table(rows, empty):
        return "\n".join(r for _, r in sorted(rows)) or empty

    head = "| active | title | branch / cwd | match | user msgs | text | file |\n|---|---|---|---|---|---|---|\n"
    none7 = "| (none) | | | | | | |"
    with open(os.path.join(a.out, "index.md"), "w", encoding="utf-8") as f:
        f.write(f"# Sessions on {a.date} for '{a.project}' (local time {datetime.now().astimezone().strftime('%z')})\n\n")
        f.write("Same title + overlapping time = one session resumed or forked; treat as one work line.\n"
                "The session generating this report is probably the latest one whose last user message asks for a report; skip it.\n\n")
        f.write("## Matched (project dir or cwd)\n\n" + head + table(groups["matched"], none7) + "\n\n")
        f.write(f"## Started elsewhere but mention '{keyword}' — check whether this is project work\n\n"
                + head + table(groups["mentioned"], none7) + "\n\n")
        f.write("## Other sessions that day (title only, no file)\n\n| active | title | cwd |\n|---|---|---|\n"
                + table(groups["other"], "| (none) | | |") + "\n")
    print(open(os.path.join(a.out, "index.md"), encoding="utf-8").read())


if __name__ == "__main__":
    main()
