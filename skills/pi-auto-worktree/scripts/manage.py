#!/usr/bin/env python3
"""Install/uninstall only owned symlinks; never edit shell RC files or pi settings."""
import argparse
import json
import os
from pathlib import Path
import sys
from launch import agent_dir, real_pi


def exists(path):
    return path.exists() or path.is_symlink()


def install():
    package = Path(__file__).resolve().parents[1]
    agent = agent_dir()
    record = agent / "pi-auto-worktree-install.json"
    entry = Path.home() / ".local/bin/pi"
    backup = entry.with_name("pi.before-pi-auto-worktree")
    links = {
        str(entry): str(package / "scripts/launch.py"),
        str(agent / "skills/pi-auto-worktree"): str(package),
        str(agent / "extensions/pi-auto-worktree-name.ts"): str(package / "extensions/auto-worktree-name.ts"),
    }
    if record.exists():
        data = json.loads(record.read_text())
        if data.get("links") == links and all(Path(p).is_symlink() and os.readlink(p) == target for p, target in links.items()):
            print("pi-auto-worktree 已安装；软链自动跟随本地源码更新。")
            return
        raise RuntimeError("已有不同安装记录；请用旧安装的卸载脚本卸载后再安装。")
    executable = Path(real_pi()).resolve()
    if exists(backup):
        raise RuntimeError(f"备份已存在，拒绝覆盖：{backup}")
    if exists(entry) and entry.resolve() != executable:
        raise RuntimeError(f"{entry} 是其他启动器，拒绝覆盖；请先卸载原启动器。")
    for path in list(links)[1:]:
        if exists(Path(path)):
            raise RuntimeError(f"资源已存在，拒绝覆盖：{path}")
    # Avoid double registration when upgrading the original server-local prototype.
    if exists(agent / "extensions/auto-worktree-name.ts"):
        raise RuntimeError("检测到旧版 auto-worktree-name.ts；请先备份并移走旧命名扩展。")
    moved = False
    created = []
    try:
        agent.mkdir(parents=True, exist_ok=True)
        entry.parent.mkdir(parents=True, exist_ok=True)
        if exists(entry):
            entry.rename(backup)
            moved = True
            if executable == entry:
                executable = backup
        for path, target in links.items():
            link = Path(path)
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(target)
            created.append(link)
        data = {"version": 1, "real_pi": str(executable), "backup": str(backup) if moved else None, "links": links}
        with record.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
    except Exception:
        for link in reversed(created):
            link.unlink()
        if moved:
            backup.rename(entry)
        raise
    print("已安装 pi-auto-worktree。请确保 ~/.local/bin 位于 PATH 最前面，并执行 hash -r。")
    print("不修改 shell 配置；下次从主仓库启动 pi 时生效。")


def uninstall():
    record = agent_dir() / "pi-auto-worktree-install.json"
    if not record.exists():
        print("未找到安装记录，无需卸载。")
        return
    data = json.loads(record.read_text())
    links = data["links"]
    entry = Path.home() / ".local/bin/pi"
    for path, target in links.items():
        link = Path(path)
        if exists(link) and (not link.is_symlink() or os.readlink(link) != target):
            raise RuntimeError(f"路径已被其他程序修改，拒绝删除：{link}")
    backup = Path(data["backup"]) if data.get("backup") else None
    if backup and not exists(backup):
        raise RuntimeError(f"原入口备份缺失：{backup}")
    for path in links:
        if exists(Path(path)):
            Path(path).unlink()
    if backup:
        backup.rename(entry)
    record.unlink()
    print("已卸载并恢复原入口；所有 worktree、分支、会话和 Git 本地忽略规则均保留。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["install", "uninstall"])
    parser.add_argument("--real-pi", help="原生 pi 可执行文件路径")
    args = parser.parse_args()
    if args.real_pi:
        os.environ["PI_AUTO_WORKTREE_REAL_PI"] = args.real_pi
    try:
        install() if args.action == "install" else uninstall()
    except Exception as error:
        print(f"pi-auto-worktree: {error}", file=sys.stderr)
        sys.exit(1)
