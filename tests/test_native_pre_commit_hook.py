import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_SOURCE = REPO_ROOT / ".githooks" / "pre-commit"


class NativePreCommitHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self._git("init")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test User")

        hook_dir = self.repo / ".githooks"
        hook_dir.mkdir(parents=True, exist_ok=True)
        hook_path = hook_dir / "pre-commit"
        hook_path.write_text(HOOK_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        self.fake_bin = self.repo / "fake-bin"
        self.fake_bin.mkdir(parents=True, exist_ok=True)
        self.lint_log = self.repo / "ansible-lint.log"
        fake_linter = self.fake_bin / "ansible-lint"
        fake_linter.write_text(
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' \"$@\" > \"${ANSIBLE_LINT_LOG}\"\n",
            encoding="utf-8",
        )
        fake_linter.chmod(fake_linter.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        self.env = os.environ.copy()
        self.env["PATH"] = f"{self.fake_bin}:{self.env.get('PATH', '')}"
        self.env["ANSIBLE_LINT_LOG"] = str(self.lint_log)

    def tearDown(self):
        self.tmp.cleanup()

    def _git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, text=True)

    def _run_hook(self):
        return subprocess.run(
            [str(self.repo / ".githooks" / "pre-commit")],
            cwd=self.repo,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def test_hook_rejects_unstaged_changes_for_staged_ansible_files(self):
        task_file = self.repo / "roles" / "example" / "tasks" / "main.yml"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text("- debug: msg='one'\n", encoding="utf-8")
        self._git("add", str(task_file.relative_to(self.repo)))
        task_file.write_text("- debug: msg='two'\n", encoding="utf-8")

        result = self._run_hook()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unstaged changes detected", result.stderr)

    def test_hook_lints_matching_staged_files(self):
        task_file = self.repo / "roles" / "example" / "tasks" / "main.yml"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text("- debug: msg='one'\n", encoding="utf-8")
        self._git("add", str(task_file.relative_to(self.repo)))

        result = self._run_hook()

        self.assertEqual(result.returncode, 0)
        lint_args = self.lint_log.read_text(encoding="utf-8").splitlines()
        self.assertIn("--offline", lint_args)
        self.assertIn(str(task_file.relative_to(self.repo)), lint_args)


if __name__ == "__main__":
    unittest.main()
