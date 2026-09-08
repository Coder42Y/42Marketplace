#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pi-install-test-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.agent = self.home / "custom agent"
        self.real = self.home / "native-pi"
        self.real.write_text('#!/usr/bin/env python3\nimport os, json, sys\nprint(json.dumps({"cwd":os.getcwd(),"args":sys.argv[1:]}))\n')
        self.real.chmod(0o755)
        self.entry = self.home / ".local/bin/pi"
        self.entry.parent.mkdir(parents=True)
        self.entry.symlink_to(self.real)
        self.env = {**os.environ, "HOME": str(self.home), "PI_CODING_AGENT_DIR": str(self.agent),
                    "PI_AUTO_WORKTREE_REAL_PI": str(self.real), "PI_AUTO_WORKTREE": "1"}
        self.manage = Path(__file__).with_name("manage.py")

    def run_manage(self, action):
        return subprocess.run(["python3", str(self.manage), action], env=self.env,
                              text=True, capture_output=True, timeout=10)

    def test_install_launch_and_uninstall(self):
        self.assertEqual(self.run_manage("install").returncode, 0)
        self.assertEqual(self.run_manage("install").returncode, 0)
        env = dict(self.env)
        env.pop("PI_AUTO_WORKTREE_REAL_PI")
        result = subprocess.run([str(self.entry), "hello world"], cwd=self.home,
                                env=env, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"cwd": str(self.home), "args": ["hello world"]})
        self.assertFalse((self.home / ".pi/worktrees").exists())
        self.assertTrue((self.agent / "extensions/pi-auto-worktree-name.ts").is_symlink())
        self.assertEqual(self.run_manage("uninstall").returncode, 0)
        self.assertEqual(self.entry.resolve(), self.real)
        self.assertFalse((self.agent / "extensions/pi-auto-worktree-name.ts").exists())
        self.assertEqual(self.run_manage("uninstall").returncode, 0)

    def test_resource_conflict_leaves_original(self):
        resource = self.agent / "skills/pi-auto-worktree"
        resource.mkdir(parents=True)
        result = self.run_manage("install")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.entry.resolve(), self.real)
        self.assertTrue(resource.is_dir())
        self.assertFalse((self.agent / "pi-auto-worktree-install.json").exists())

    def test_uninstall_refuses_changed_entry(self):
        self.assertEqual(self.run_manage("install").returncode, 0)
        self.entry.unlink()
        self.entry.write_text("another launcher")
        self.assertNotEqual(self.run_manage("uninstall").returncode, 0)
        self.assertEqual(self.entry.read_text(), "another launcher")
        self.assertTrue((self.agent / "pi-auto-worktree-install.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
