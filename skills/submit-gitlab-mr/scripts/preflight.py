#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


TARGETS = ("dev", "main", "master")


class PreflightError(Exception):
    pass


def git(repo: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise PreflightError(detail or f"git {' '.join(arguments)} failed")
    return result


def ref_exists(repo: Path, ref: str) -> bool:
    return git(repo, "show-ref", "--verify", "--quiet", ref, check=False).returncode == 0


def is_ancestor(repo: Path, older: str, newer: str) -> bool:
    return git(repo, "merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def choose_target(repo: Path, candidates: list[dict]) -> tuple[str | None, list[str]]:
    if not candidates:
        return None, []
    minimum = min(candidate["distance"] for candidate in candidates)
    tied = [candidate for candidate in candidates if candidate["distance"] == minimum]
    if len(tied) == 1:
        return tied[0]["name"], []

    maximal = []
    for candidate in tied:
        ref = f"origin/{candidate['name']}"
        if not any(
            other["name"] != candidate["name"]
            and is_ancestor(repo, ref, f"origin/{other['name']}")
            for other in tied
        ):
            maximal.append(candidate["name"])
    return (maximal[0], []) if len(maximal) == 1 else (None, maximal)


def inspect_repository(repo: Path, explicit_target: str | None = None) -> dict:
    repo = repo.resolve()
    origin = git(repo, "remote", "get-url", "origin", check=False)
    if origin.returncode != 0 or not origin.stdout.strip():
        raise PreflightError("an origin remote is required")
    source = git(repo, "branch", "--show-current").stdout.strip()
    if not source:
        raise PreflightError("detached HEAD is not eligible for an MR")
    if source in TARGETS:
        raise PreflightError("the source branch cannot also be an MR target")
    if explicit_target is not None and explicit_target not in TARGETS:
        raise PreflightError("target must be dev, main, or master")

    candidates = []
    for name in TARGETS:
        ref = f"refs/remotes/origin/{name}"
        if not ref_exists(repo, ref):
            continue
        base = git(repo, "merge-base", "HEAD", f"origin/{name}", check=False)
        if base.returncode != 0:
            continue
        merge_base = base.stdout.strip()
        distance = int(git(repo, "rev-list", "--count", f"{merge_base}..HEAD").stdout)
        candidates.append({"name": name, "merge_base": merge_base, "distance": distance})

    if explicit_target is not None:
        target, ambiguous = explicit_target, []
    else:
        target, ambiguous = choose_target(repo, candidates)

    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all").stdout
    return {
        "head": git(repo, "rev-parse", "HEAD").stdout.strip(),
        "source": source,
        "target": target,
        "target_confident": target is not None,
        "ambiguous_targets": ambiguous,
        "candidates": candidates,
        "dirty": bool(status),
        "source_tracking_ref": (
            f"origin/{source}"
            if ref_exists(repo, f"refs/remotes/origin/{source}")
            else None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect local state for a fast GitLab MR")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--target", choices=TARGETS)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_repository(Path(args.repo), args.target)))
        return 0
    except (OSError, PreflightError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
