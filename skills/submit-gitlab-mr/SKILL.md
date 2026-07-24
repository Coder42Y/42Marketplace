---
name: submit-gitlab-mr
description: Use when the user wants to prepare, submit, create, or update a merge request for the current GitLab repository.
---

# Submit GitLab MR

Use the fastest safe path: one local preflight, one targeted fetch, one Git conflict check, then one push and MR upsert. Draft-only requests are read-only; submit/create/update requests authorize push and upsert.

The only gate this skill owns is the Git conflict check. Do not perform code review or commit-message review. Do not run lint, typecheck, tests, build, or other project checks. CI or a separate review skill owns those checks.

## Fast path

1. Run `scripts/preflight.py` relative to this skill. Target precedence is: user choice, an existing MR's target when updating, then local inference. Infer only `dev`, `main`, and `master`: choose the unique smallest HEAD-to-merge-base distance; on a tie prefer a candidate containing the others. Never use commit timestamps. Ask when refs are missing or the result is ambiguous.

2. Uncommitted changes are excluded by default. Only create a branch or commit files when the user explicitly asks. Never stash, clean, discard, or overwrite user work.

3. Perform one targeted fetch:

   ```bash
   git fetch --prune origin "refs/heads/<target>:refs/remotes/origin/<target>"
   ```

   Re-run preflight with `--target <target>`. Stop if source equals target or `origin/<target>...HEAD` is empty.

4. Check conflict once without changing the worktree:

   ```bash
   git merge-tree --write-tree --quiet "origin/<target>" HEAD
   ```

   Exit `0` continues. Exit `1` means conflict: report paths from the same command with `--name-only` and stop. Any other nonzero exit is an error.

5. Count `HEAD..origin/<target>`. If behind, report the exact behind count and ask once whether to merge, rebase, or cancel. Recommend rebase for an unpublished source and merge for a published source. Abort and stop on conflict. Published-source rebase requires explicit rewrite consent, fetching its remote SHA, rejecting unseen commits, and an exact `--force-with-lease=refs/heads/<source>:<sha>`. Continue only when HEAD contains the target tip.

6. Follow repository MR templates when present; otherwise write a concise title and description. Ask for assignee or reviewer only when requested. Draft-only mode returns the text and stops.

7. Push with `git push --no-verify -u origin <source>` so project checks are not repeated. On non-fast-forward rejection, stop. For a confirmed published rebase, combine `--no-verify` with the exact lease. Run `scripts/upsert_mr.py --help`, upsert using temporary UTF-8 files, remove them, and return the MR URL, source, target, and conflict/synchronization result. Never auto-merge or request source deletion.
