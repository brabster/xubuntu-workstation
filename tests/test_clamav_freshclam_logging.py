import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_FILE = REPO_ROOT / "roles" / "clamav" / "tasks" / "main.yml"


class FreshclamLoggingNormalizationTests(unittest.TestCase):
    def _load_tasks(self):
        return yaml.safe_load(TASKS_FILE.read_text(encoding="utf-8"))

    def test_managed_logging_block_is_inserted_before_packaged_directives(self):
        tasks = self._load_tasks()
        for task in tasks:
            if task.get("name") == "Configure freshclam update logging":
                blockinfile = task["ansible.builtin.blockinfile"]
                self.assertEqual("BOF", blockinfile.get("insertbefore"))
                self.assertNotIn("insertafter", blockinfile)
                return
        self.fail("Expected freshclam logging block task was not found.")

    def test_no_global_logging_directive_rewrite_task_remains(self):
        tasks = self._load_tasks()
        for task in tasks:
            self.assertNotEqual(
                "Comment out pre-existing active freshclam logging directives",
                task.get("name"),
            )

    def test_previous_managed_block_cleanup_task_was_removed(self):
        tasks = self._load_tasks()
        for task in tasks:
            self.assertNotEqual(
                "Remove previous managed freshclam logging block before normalization",
                task.get("name"),
            )

    def test_parent_directory_for_configured_freshclam_log_is_ensured(self):
        tasks = self._load_tasks()
        for task in tasks:
            if task.get("name") == "Ensure parent directory for configured FreshClam log exists":
                file_task = task["ansible.builtin.file"]
                self.assertEqual("{{ clamav_freshclam_log_file | dirname }}", file_task.get("path"))
                self.assertEqual("directory", file_task.get("state"))
                self.assertEqual("0755", str(file_task.get("mode")))
                return
        self.fail("Expected configured FreshClam log parent-directory task was not found.")


if __name__ == "__main__":
    unittest.main()
