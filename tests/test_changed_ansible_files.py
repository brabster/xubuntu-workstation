import os
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import changed_ansible_files as caf


class ChangedAnsibleFilesTests(unittest.TestCase):
    @patch("changed_ansible_files.git_paths")
    def test_selected_files_uses_ls_files_for_zero_sha(self, git_paths):
        caf.selected_files("push", caf.ZERO_SHA)
        git_paths.assert_called_once_with(["git", "ls-files", "-z", *caf.SCOPE_PATHS])

    @patch("changed_ansible_files.git_paths")
    def test_selected_files_uses_triple_dot_for_pull_request(self, git_paths):
        caf.selected_files("pull_request", "abc123")
        git_paths.assert_called_once_with(
            ["git", "diff", "--name-only", "-z", "abc123...HEAD", "--", *caf.SCOPE_PATHS]
        )

    @patch("changed_ansible_files.git_paths")
    def test_selected_files_uses_double_dot_for_push(self, git_paths):
        caf.selected_files("push", "abc123")
        git_paths.assert_called_once_with(
            ["git", "diff", "--name-only", "-z", "abc123..HEAD", "--", *caf.SCOPE_PATHS]
        )

    @patch("changed_ansible_files.git_paths")
    def test_selected_staged_files_uses_cached_diff(self, git_paths):
        caf.selected_staged_files()
        git_paths.assert_called_once_with(
            ["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMT", "--", *caf.SCOPE_PATHS]
        )

    def test_filter_ansible_files_excludes_deleted_and_non_scoped_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                Path("roles/example/tasks").mkdir(parents=True, exist_ok=True)
                Path("roles/example/tasks/main.yml").write_text("- hosts: all\n")
                Path("workstation.yaml").write_text("- hosts: all\n")
                filtered = list(
                    caf.filter_ansible_files(
                        [
                            "roles/example/tasks/main.yml",
                            "workstation.yaml",
                            "README.md",
                            "roles/example/tasks/deleted.yml",
                        ]
                    )
                )
            finally:
                os.chdir(original_cwd)

        self.assertEqual(filtered, ["roles/example/tasks/main.yml", "workstation.yaml"])

    @patch("changed_ansible_files.filter_ansible_files", return_value=["workstation.yml", "test.yml"])
    @patch("changed_ansible_files.selected_files", return_value=[])
    def test_main_supports_nul_output(self, _selected_files, _filter_ansible_files):
        with patch("sys.argv", ["changed_ansible_files.py", "--event-name", "push", "--null-output"]):
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                caf.main()
        self.assertEqual(stdout.getvalue(), "workstation.yml\0test.yml\0")


if __name__ == "__main__":
    unittest.main()
