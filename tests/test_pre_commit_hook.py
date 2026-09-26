import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_SOURCE = REPO_ROOT / ".githooks" / "pre-commit"


class PreCommitHookTests(unittest.TestCase):
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

        (self.repo / "roles" / "example" / "tasks").mkdir(parents=True, exist_ok=True)
        (self.repo / "roles" / "example" / "tasks" / "main.yml").write_text("- debug: msg='one'\n", encoding="utf-8")
        (self.repo / "workstation.yml").write_text("- hosts: all\n", encoding="utf-8")
        (self.repo / "test.yml").write_text("- hosts: all\n", encoding="utf-8")
        self._git("add", "roles/example/tasks/main.yml", "workstation.yml", "test.yml")
        self._git("commit", "-m", "seed")

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

    def test_hook_lints_fixed_targets_when_scoped_file_staged(self):
        scoped_file = self.repo / "roles" / "example" / "tasks" / "main.yml"
        scoped_file.write_text("- debug: msg='two'\n", encoding="utf-8")
        self._git("add", "roles/example/tasks/main.yml")

        result = self._run_hook()

        self.assertEqual(result.returncode, 0)
        lint_args = self.lint_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lint_args, ["--offline", "roles", "workstation.yml", "test.yml"])

    def test_unstaged_unrelated_scoped_file_does_not_block_commit(self):
        staged_file = self.repo / "roles" / "example" / "tasks" / "main.yml"
        staged_file.write_text("- debug: msg='two'\n", encoding="utf-8")
        self._git("add", "roles/example/tasks/main.yml")

        other_scoped_file = self.repo / "test.yml"
        other_scoped_file.write_text("- hosts: all\n  gather_facts: false\n", encoding="utf-8")

        result = self._run_hook()

        self.assertEqual(result.returncode, 0)

    def test_unstaged_edit_in_staged_scoped_file_blocks_commit(self):
        staged_file = self.repo / "roles" / "example" / "tasks" / "main.yml"
        staged_file.write_text("- debug: msg='two'\n", encoding="utf-8")
        self._git("add", "roles/example/tasks/main.yml")
        staged_file.write_text("- debug: msg='three'\n", encoding="utf-8")

        result = self._run_hook()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unstaged changes detected in scoped Ansible files", result.stderr)

    def test_metadata_only_change_does_not_trigger_unstaged_content_guard(self):
        staged_file = self.repo / "roles" / "example" / "tasks" / "main.yml"
        staged_file.write_text("- debug: msg='two'\n", encoding="utf-8")
        self._git("add", "roles/example/tasks/main.yml")
        staged_file.chmod(staged_file.stat().st_mode | stat.S_IXUSR)

        result = self._run_hook()

        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
