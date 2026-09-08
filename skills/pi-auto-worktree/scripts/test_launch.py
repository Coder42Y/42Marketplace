#!/usr/bin/env python3
import concurrent.futures
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("launcher", Path(__file__).with_name("launch.py"))
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)
try:
    launcher.real_pi()
    HAVE_PI = True
except RuntimeError:
    HAVE_PI = False


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pi-worktree-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo with spaces"
        self.root.mkdir()
        self.env = patch.dict(os.environ, {"PI_AUTO_WORKTREE": "1"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def repo(self, commit=True):
        launcher.git(self.root, "init", "-b", "main")
        launcher.git(self.root, "config", "user.email", "test@example.invalid")
        launcher.git(self.root, "config", "user.name", "Test")
        if commit:
            (self.root / "src").mkdir()
            (self.root / "src" / "file").write_text("committed")
            launcher.git(self.root, "add", ".")
            launcher.git(self.root, "commit", "-m", "initial")

    def count(self):
        return launcher.git(self.root, "worktree", "list", "--porcelain").count("worktree ")

    def test_non_repo_including_parent_with_child_repo(self):
        self.assertEqual(launcher.prepare(self.root, []), (self.root, []))
        self.repo()
        parent = self.root.parent
        self.assertEqual(launcher.prepare(parent, []), (parent, []))
        self.assertFalse((parent / ".pi").exists())

    def test_new_sessions_and_dirty_original(self):
        self.repo()
        (self.root / "src" / "file").write_text("dirty")
        (self.root / "untracked").write_text("keep")
        before = launcher.git(self.root, "status", "--porcelain")
        one, _ = launcher.prepare(self.root, [])
        two, _ = launcher.prepare(self.root, [])
        self.assertNotEqual(one, two)
        self.assertEqual(self.count(), 3)
        self.assertEqual((one / "src" / "file").read_text(), "committed")
        self.assertFalse((one / "untracked").exists())
        self.assertEqual(launcher.git(self.root, "status", "--porcelain"), before)
        self.assertEqual(launcher.git(one, "rev-parse", "HEAD"), launcher.git(self.root, "rev-parse", "HEAD"))

    def test_subdirectory_and_linked_skip(self):
        self.repo()
        path, _ = launcher.prepare(self.root / "src", [])
        self.assertEqual(path.name, "src")
        self.assertEqual(launcher.prepare(path, []), (path, []))
        self.assertEqual(self.count(), 2)

    def test_opt_out(self):
        self.repo()
        with patch.dict(os.environ, {"PI_AUTO_WORKTREE": "0"}):
            self.assertEqual(launcher.prepare(self.root, []), (self.root, []))
        for folder in (".pi", ".claude"):
            marker = self.root / folder / "no-auto-worktree"
            marker.parent.mkdir(exist_ok=True)
            marker.touch()
            self.assertEqual(launcher.prepare(self.root / "src", ["hello"])[0], self.root / "src")
            marker.unlink()
        self.assertEqual(self.count(), 1)

    def test_resume_and_non_session_commands(self):
        self.repo()
        for args in (["-c"], ["--resume"], ["--session", "old.jsonl"], ["--fork", "id"],
                     ["--help"], ["--version"], ["update"], ["install", "x"],
                     ["--list-models"], ["--export", "x"], ["--model"]):
            self.assertEqual(launcher.prepare(self.root, args), (self.root, args))
        self.assertEqual(self.count(), 1)

    def test_empty_and_bare(self):
        self.repo(commit=False)
        self.assertEqual(launcher.prepare(self.root, []), (self.root, []))
        bare = self.root.parent / "bare.git"
        launcher.git(self.root, "init", "--bare", str(bare))
        self.assertEqual(launcher.prepare(bare, []), (bare, []))

    def test_arg_semantics(self):
        self.repo()
        (self.root / "ext.ts").touch()
        bypass, args = launcher.parse_args(["--name", "update", "-e", "./ext.ts", "@src/file", "--", "--help"], self.root)
        self.assertFalse(bypass)
        self.assertEqual(args[3], str(self.root / "ext.ts"))
        self.assertEqual(args[4], "@" + str(self.root / "src" / "file"))
        self.assertEqual(args[-1], "--help")

    def test_explicit_names(self):
        self.repo()
        for args, prefix in ((["--name", "Fix Login Timeout"], "fix-login-timeout-"),
                             (["-n", "修复登录"], "修复登录-"),
                             (["--name=../../bad.lock@{x}"], "bad-lock-x-")):
            path, forwarded = launcher.prepare(self.root, args)
            self.assertTrue(path.name.startswith(prefix), path.name)
            self.assertEqual(forwarded, args)
            import json
            metadata = Path(launcher.git(path, "rev-parse", "--absolute-git-dir")) / "pi-auto-worktree.json"
            self.assertTrue(json.loads(metadata.read_text())["named"])
        self.assertIsNone(launcher.explicit_name(["--", "--name", "literal"]))
        self.assertIsNone(launcher.explicit_name(["--system-prompt", "--name", "literal"]))

    @unittest.skipUnless(HAVE_PI, "需要原生 pi；可设置 PI_AUTO_WORKTREE_REAL_PI")
    def test_naming_extension(self):
        self.repo()
        probe = self.root.parent / "name-probe.ts"
        extension = Path(launcher.__file__).parents[1] / "extensions" / "auto-worktree-name.ts"
        import json
        probe.write_text('import naming from ' + json.dumps(str(extension)) + ';\n' + r'''
import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {readFileSync, existsSync, writeFileSync} from "node:fs";
export default function(pi) {
  pi.on("session_start", async (_event, ctx) => {
    const git = (...args) => execFileSync("git", ["-C", ctx.cwd, ...args], {encoding:"utf8"}).trim();
    const hooks = {}; let tool; let title;
    const fake = {
      on: (event, fn) => hooks[event] = fn,
      registerTool: value => tool = value,
      getActiveTools: () => tool ? [tool.name] : [],
      getSessionName: () => title,
      setSessionName: value => title = value,
    };
    try {
      naming(fake);
      await hooks.session_start({}, ctx);
      assert.ok(tool);
      assert.match((await hooks.before_agent_start({systemPrompt:"base"})).systemPrompt, /name_worktree_task/);
      const old = git("branch", "--show-current");
      const head = git("rev-parse", "HEAD");
      const cwd = ctx.cwd;
      const file = git("rev-parse", "--absolute-git-dir") + "/pi-auto-worktree.json";
      const suffix = JSON.parse(readFileSync(file, "utf8")).suffix;
      await assert.rejects(() => tool.execute("1", {slug:"../evil",title:"bad"}, null, null, ctx));
      // A collision must not overwrite an existing branch.
      git("branch", `pi/fix-login-timeout-${suffix}`);
      await assert.rejects(() => tool.execute("2", {slug:"fix-login-timeout",title:"修复登录超时"}, null, null, ctx));
      assert.equal(git("branch", "--show-current"), old);
      git("branch", "-d", `pi/fix-login-timeout-${suffix}`);
      await tool.execute("3", {slug:"fix-login-timeout",title:"修复登录超时"}, null, null, ctx);
      assert.equal(git("branch", "--show-current"), `pi/fix-login-timeout-${suffix}`);
      assert.equal(title, "修复登录超时");
      assert.equal(git("rev-parse", "HEAD"), head);
      assert.equal(ctx.cwd, cwd);
      assert.ok(existsSync(cwd));
      assert.equal(await hooks.before_agent_start({systemPrompt:"base"}), undefined);
      await tool.execute("4", {slug:"other-task",title:"other"}, null, null, ctx);
      assert.equal(git("branch", "--show-current"), `pi/fix-login-timeout-${suffix}`);
      tool = undefined;
      naming(fake);
      await hooks.session_start({reason:"reload"}, ctx);
      assert.equal(tool, undefined); // Reload/resume must not rename again.
      writeFileSync(process.env.PI_WT_PROBE, "NAMING_PROBE_OK");
      process.exit(0);
    } catch (error) { console.error(error); process.exit(1); }
  });
}
''')
        result = subprocess.run(["python3", launcher.__file__, "-p", "--no-session",
            "--no-extensions", "-e", str(probe), "--no-skills", "--no-approve", "probe"],
            cwd=self.root, env={**os.environ, "PI_OFFLINE": "1", "PI_WT_PROBE": str(probe) + ".ok"}, text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(Path(str(probe) + ".ok").read_text(), "NAMING_PROBE_OK")

    def test_parallel_start(self):
        self.repo()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            paths = list(pool.map(lambda _: launcher.prepare(self.root, [])[0], range(4)))
        self.assertEqual(len(set(paths)), 4)
        self.assertEqual(self.count(), 5)

    def test_creation_failure_does_not_fall_back(self):
        self.repo()
        original = launcher.git
        def failing(cwd, *args):
            if args[:2] == ("worktree", "add"):
                raise RuntimeError("simulated failure")
            return original(cwd, *args)
        with patch.object(launcher, "git", failing):
            with self.assertRaisesRegex(RuntimeError, "simulated failure"):
                launcher.prepare(self.root, [])

    @unittest.skipUnless(HAVE_PI, "需要原生 pi；可设置 PI_AUTO_WORKTREE_REAL_PI")
    def test_real_pi_initializes_in_worktree(self):
        self.repo()
        probe = self.root.parent / "probe.ts"
        output = self.root.parent / "probe.json"
        probe.write_text('import {writeFileSync} from "node:fs";\n'
            'export default function(pi) { pi.on("session_start", (_event, ctx) => {\n'
            'writeFileSync(process.env.PI_WT_PROBE, JSON.stringify({cwd:ctx.cwd, process:process.cwd(), '
            'session:ctx.sessionManager.getCwd(), prompt:ctx.getSystemPrompt(), tools:pi.getActiveTools()})); process.exit(0); }); }\n')
        env = {**os.environ, "PI_OFFLINE": "1", "PI_WT_PROBE": str(output)}
        result = subprocess.run(["python3", str(Path(launcher.__file__)), "-p", "--no-session",
            "--no-extensions", "-e", str(Path(launcher.__file__).parents[1] / "extensions" / "auto-worktree-name.ts"),
            "-e", str(probe), "--no-skills", "--no-approve", "probe"],
            cwd=self.root, env=env, text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        import json
        data = json.loads(output.read_text())
        self.assertIn("/.pi/worktrees/", data["cwd"])
        self.assertEqual(data["cwd"], data["process"])
        self.assertEqual(data["cwd"], data["session"])
        self.assertIn(data["cwd"], data["prompt"])
        self.assertIn("name_worktree_task", data["tools"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
