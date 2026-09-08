import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { readFile, writeFile, open, unlink, rename } from "node:fs/promises";
import { join, resolve } from "node:path";

const exec = promisify(execFile);
async function git(cwd: string, ...args: string[]) {
  return (await exec("git", ["-C", cwd, ...args], { timeout: 10000 })).stdout.trim();
}
async function state(cwd: string) {
  const dir = await git(cwd, "rev-parse", "--absolute-git-dir");
  const file = join(dir, "pi-auto-worktree.json");
  const data = JSON.parse(await readFile(file, "utf8"));
  const root = await git(cwd, "rev-parse", "--show-toplevel");
  if (data.version !== 1 || resolve(data.path) !== resolve(root) ||
      !/^[a-f0-9]{10}$/.test(data.suffix) || typeof data.branch !== "string") {
    throw new Error("Invalid auto-worktree metadata");
  }
  return { file, data };
}

export default function (pi: ExtensionAPI) {
  let pending = false;
  pi.on("session_start", async (_event, ctx) => {
    pending = false;
    if (process.env.PI_AUTO_WORKTREE === "0") return;
    try {
      const { data } = await state(ctx.cwd);
      pending = !data.named && await git(ctx.cwd, "branch", "--show-current") === data.branch;
    } catch { return; } // Non-Git or non-owned worktree: strict no-op.
    if (!pending) return;
    pi.registerTool({
      name: "name_worktree_task",
      label: "Name worktree task",
      description: "Name this auto-created worktree branch and session from the first user task. Call once before task work. Does not move the directory or change files/commits. Keep names short and omit secrets.",
      parameters: Type.Object({
        slug: Type.String({ description: "Short English kebab-case task summary, e.g. fix-login-timeout", maxLength: 80 }),
        title: Type.String({ description: "Short readable session title, may be Chinese; no secrets", maxLength: 120 }),
      }),
      async execute(_id, params, _signal, _update, ctx) {
        if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(params.slug) || !params.title.trim() || /[\x00-\x1f\x7f]/.test(params.title)) {
          throw new Error("Use an English kebab-case slug and a non-empty, single-line title.");
        }
        const { file } = await state(ctx.cwd);
        // Cross-process lock: fail safely rather than rename twice in concurrent sessions.
        const lock = await open(file + ".lock", "wx");
        try {
          const { data } = await state(ctx.cwd);
          if (data.named) {
            pending = false;
            return { content: [{ type: "text", text: `Already named: ${data.branch}` }], details: {} };
          }
          const current = await git(ctx.cwd, "branch", "--show-current");
          if (current !== data.branch) {
            pending = false;
            throw new Error("Branch changed outside auto-worktree; refusing to overwrite your choice.");
          }
          const branch = `pi/${params.slug}-${data.suffix}`;
          await git(ctx.cwd, "check-ref-format", "--branch", branch);
          if (branch !== current) await git(ctx.cwd, "branch", "-m", current, branch);
          data.branch = branch;
          data.named = true;
          data.title = params.title.trim();
          // Atomic state replacement. If persistence fails, branch guard prevents a second rename.
          await writeFile(file + ".tmp", JSON.stringify(data), "utf8");
          await rename(file + ".tmp", file);
          pending = false;
          if (!pi.getSessionName()) pi.setSessionName(data.title);
          if (ctx.hasUI) ctx.ui.notify(`Worktree 分支：${branch}（目录保持不变）`, "info");
          return { content: [{ type: "text", text: `Branch: ${branch}\nWorktree directory unchanged: ${data.path}` }], details: { branch, path: data.path } };
        } finally {
          await lock.close();
          await unlink(file + ".lock");
        }
      },
    });
  });
  pi.on("before_agent_start", async (event) => {
    if (!pending || !pi.getActiveTools().includes("name_worktree_task")) return;
    return {
      systemPrompt: event.systemPrompt + "\n\n[auto-worktree] This session already has an isolated worktree with a temporary name. Before working on the first user request, call name_worktree_task once: summarize that task as a short English kebab-case slug and a readable session title. Omit secrets and personal identifiers. For greetings or unclear requests use a neutral name such as general-discussion. Do not ask the user to name it. The tool keeps a unique suffix and never moves the directory. Do not manually move/rename the worktree directory. If naming fails, report it briefly and continue the user's task in the existing worktree; do not force a rename.",
    };
  });
}
