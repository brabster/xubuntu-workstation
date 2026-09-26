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

    def test_previous_managed_block_is_removed_before_reinsertion(self):
        tasks = self._load_tasks()
        for task in tasks:
            if task.get("name") == "Remove previous managed freshclam logging block before normalization":
                blockinfile = task["ansible.builtin.blockinfile"]
                self.assertEqual("absent", blockinfile.get("state"))
                self.assertEqual(
                    "# {mark} ANSIBLE MANAGED FRESHCLAM LOGGING",
                    blockinfile.get("marker"),
                )
                return
        self.fail("Expected managed freshclam cleanup task was not found.")


if __name__ == "__main__":
    unittest.main()
