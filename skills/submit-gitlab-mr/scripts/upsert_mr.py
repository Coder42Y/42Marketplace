#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


class UpsertError(Exception):
    pass


def read_literal(path: str) -> str:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return file.read()


def read_title(path: str) -> str:
    title = read_literal(path)
    if title.endswith("\r\n"):
        title = title[:-2]
    elif title.endswith(("\r", "\n")):
        title = title[:-1]
    if not title.strip() or "\r" in title or "\n" in title:
        raise UpsertError("title must be a nonempty single line")
    if len(title) > 72:
        raise UpsertError("title must not exceed 72 characters")
    return title


def fences_are_balanced(description: str) -> bool:
    fence_is_open = False
    for line in description.splitlines():
        stripped_line = line.strip()
        if not stripped_line.startswith("```"):
            continue
        if not fence_is_open:
            fence_is_open = True
        elif set(stripped_line) == {"`"}:
            fence_is_open = False
        else:
            return False
    return not fence_is_open


def read_description(path: str) -> str:
    description = read_literal(path)
    if not description.strip():
        raise UpsertError("description must not be empty")
    if not fences_are_balanced(description):
        raise UpsertError("description contains an unbalanced triple-backtick fence")
    return description


def run_glab(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["glab", *arguments],
            shell=False,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or str(error)
        raise UpsertError(f"glab failed: {detail}") from error


def list_merge_requests(repo: str, source: str, target: str) -> list[dict]:
    result = run_glab(
        [
            "mr",
            "list",
            "--repo",
            repo,
            "--source-branch",
            source,
            "--target-branch",
            target,
            "--output",
            "json",
        ]
    )
    try:
        merge_requests = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise UpsertError("glab mr list returned invalid JSON") from error
    if not isinstance(merge_requests, list):
        raise UpsertError("glab mr list JSON must be an array")
    return merge_requests


def upsert_merge_request(
    repo: str,
    source: str,
    target: str,
    title: str,
    description: str,
    assignees: list[str],
    reviewers: list[str],
) -> dict:
    merge_requests = list_merge_requests(repo, source, target)
    common_arguments = [
        "--repo",
        repo,
        "--title",
        title,
        "--description",
        description,
    ]
    for assignee in assignees:
        common_arguments.extend(["--assignee", assignee])
    for reviewer in reviewers:
        common_arguments.extend(["--reviewer", reviewer])

    if not merge_requests:
        run_glab(
            [
                "mr",
                "create",
                "--source-branch",
                source,
                "--target-branch",
                target,
                *common_arguments,
                "--yes",
            ]
        )
    elif len(merge_requests) == 1:
        iid = merge_requests[0].get("iid")
        if iid is None:
            raise UpsertError("matching merge request has no iid")
        run_glab(["mr", "update", str(iid), *common_arguments, "--yes"])
    else:
        raise UpsertError("multiple opened merge requests match source and target branches")

    final_merge_requests = list_merge_requests(repo, source, target)
    if len(final_merge_requests) != 1:
        raise UpsertError("expected exactly one opened merge request after upsert")
    return final_merge_requests[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update one open GitLab MR")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--title-file", required=True)
    parser.add_argument("--description-file", required=True)
    parser.add_argument("--assignee", action="append", default=[])
    parser.add_argument("--reviewer", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = upsert_merge_request(
            args.repo,
            args.source,
            args.target,
            read_title(args.title_file),
            read_description(args.description_file),
            args.assignee,
            args.reviewer,
        )
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, UpsertError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
