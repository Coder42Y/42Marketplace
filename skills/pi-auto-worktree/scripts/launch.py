#!/usr/bin/env python3
"""Create isolation BEFORE pi captures cwd. No model calls, no shell interpolation."""
import datetime
import json
import re
import unicodedata
import os
from pathlib import Path
import subprocess
import sys
import uuid

def agent_dir():
    return Path(os.environ.get("PI_CODING_AGENT_DIR", "~/.pi/agent")).expanduser().resolve()


def real_pi():
    """Use the installer record, an explicit override, or an unwrapped PATH entry."""
    override = os.environ.get("PI_AUTO_WORKTREE_REAL_PI")
    record = agent_dir() / "pi-auto-worktree-install.json"
    if override:
        candidates = [Path(override).expanduser()]
    elif record.exists():
        candidates = [Path(json.loads(record.read_text())["real_pi"])]
    else:
        candidates = [Path(directory) / "pi" for directory in os.get_exec_path()]
    for path in candidates:
        if path.is_file() and os.access(path, os.X_OK) and path.resolve().name != "launch.py":
            return str(path.absolute())
    raise RuntimeError("找不到原生 pi；先安装 pi，或设置 PI_AUTO_WORKTREE_REAL_PI=/path/to/pi")
VALUE_FLAGS = {
    "--provider", "--model", "--api-key", "--thinking", "--models", "--mode",
    "--session", "--fork", "--session-dir", "--name", "-n", "--tools", "-t",
    "--exclude-tools", "-xt", "--extension", "-e", "--skill", "--prompt-template",
    "--theme", "--system-prompt", "--append-system-prompt", "--tui-mode", "--use-theme",
    "--export",
}
PATH_FLAGS = {"--extension", "-e", "--skill", "--prompt-template", "--theme", "--session-dir"}
BYPASS = {"-h", "--help", "-v", "--version", "-c", "--continue", "-r", "--resume",
          "--session", "--fork", "--export", "--list-models"}
COMMANDS = {"install", "remove", "uninstall", "update", "list", "config"}


def git(cwd, *args):
    result = subprocess.run(["git", "-C", str(cwd), *args], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def parse_args(args, cwd):
    """Preserve CLI semantics; anchor explicit local inputs before changing cwd."""
    result = list(args)
    bypass = False
    positional = False
    literal = False
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--" and not literal:
            literal = True
            i += 1
            continue
        flag = arg.split("=", 1)[0]
        if not literal and flag in BYPASS:
            bypass = True
        if not literal and flag in VALUE_FLAGS:
            inline = "=" in arg
            j = i if inline else i + 1
            if j >= len(args):
                return True, result  # Let pi report invalid arguments without side effects.
            value = arg.split("=", 1)[1] if inline else args[j]
            if flag in PATH_FLAGS:
                path = Path(value).expanduser()
                if not path.is_absolute() and (flag == "--session-dir" or (cwd / path).exists()):
                    value = str((cwd / path).resolve())
                    result[j] = flag + "=" + value if inline else value
            i += 1 if inline else 2
            continue
        if literal or not arg.startswith("-"):
            if not positional and not literal and arg in COMMANDS:
                bypass = True
            positional = True
            if arg.startswith("@") and (cwd / arg[1:]).exists():
                result[i] = "@" + str((cwd / arg[1:]).resolve())
        i += 1
    return bypass, result


def explicit_name(args):
    i = 0
    name = None
    while i < len(args):
        arg = args[i]
        if arg == "--":
            break
        flag = arg.split("=", 1)[0]
        if flag in VALUE_FLAGS:
            inline = "=" in arg
            value = arg.split("=", 1)[1] if inline else (args[i + 1] if i + 1 < len(args) else "")
            if flag in {"--name", "-n"}:
                name = value.strip() or None
            i += 1 if inline else 2
        else:
            i += 1
    return name


def slugify(value):
    value = unicodedata.normalize("NFKC", value).lower().replace("_", "-")
    return re.sub(r"[^\w-]+", "-", value).strip("-")[:60].rstrip("-") or "task"


def prepare(cwd, args):
    bypass, anchored = parse_args(args, cwd)
    if bypass or os.environ.get("PI_AUTO_WORKTREE", "1") == "0":
        return cwd, args
    try:
        if git(cwd, "rev-parse", "--is-inside-work-tree") != "true":
            return cwd, args
        root = Path(git(cwd, "rev-parse", "--show-toplevel")).resolve()
    except (RuntimeError, FileNotFoundError):
        return cwd, args  # Non-repo (including multi-repo parent) is a strict no-op.
    for base in {cwd, root}:
        if any((base / config / "no-auto-worktree").exists() for config in (".pi", ".claude")):
            return cwd, args
    gitdir = Path(git(cwd, "rev-parse", "--absolute-git-dir")).resolve()
    common = Path(git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    if gitdir != common:
        return cwd, args  # Existing linked worktree: preserve explicit workspace.
    try:
        head = git(cwd, "rev-parse", "--verify", "HEAD^{commit}")
    except RuntimeError:
        print("[auto-worktree] 仓库尚无提交，跳过。", file=sys.stderr)
        return cwd, args
    title = explicit_name(args)
    suffix = uuid.uuid4().hex[:10]
    name = (slugify(title) + "-" if title else "s-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-")) + suffix
    target = root / ".pi" / "worktrees" / name
    # Local exclude only: never modify tracked .gitignore or make an automatic commit.
    exclude = common / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    with exclude.open("a+", encoding="utf-8") as stream:
        import fcntl
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        if "/.pi/worktrees/" not in stream.read().splitlines():
            stream.write("\n# pi auto-worktree\n/.pi/worktrees/\n")
    target.parent.mkdir(parents=True, exist_ok=True)
    git(root, "worktree", "add", "-b", "pi/" + name, str(target), head)
    metadata_dir = Path(git(target, "rev-parse", "--absolute-git-dir"))
    (metadata_dir / "pi-auto-worktree.json").write_text(json.dumps({
        "version": 1, "path": str(target), "branch": "pi/" + name,
        "suffix": suffix, "named": bool(title), "title": title,
    }), encoding="utf-8")
    # Keep the original subdirectory when it exists in committed HEAD.
    destination = target / cwd.relative_to(root)
    if not destination.is_dir():
        destination = target
    print(f"[auto-worktree] {destination}  (pi/{name})\n"
          "[auto-worktree] 基于本地 HEAD；不复制未提交/未跟踪文件，退出后保留。", file=sys.stderr)
    return destination, anchored


def main():
    try:
        executable = real_pi()
        cwd, args = prepare(Path.cwd().resolve(), sys.argv[1:])
        os.chdir(cwd)
    except Exception as error:
        # Never silently fall back to editing the main checkout after creation failure.
        print(f"[auto-worktree] 启动中止：{error}\n"
              "如需明确跳过，运行 PI_AUTO_WORKTREE=0 pi", file=sys.stderr)
        return 1
    os.execv(executable, [executable, *args])


if __name__ == "__main__":
    sys.exit(main())
