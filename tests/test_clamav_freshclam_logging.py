import re
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_FILE = REPO_ROOT / "roles" / "clamav" / "tasks" / "main.yml"


class FreshclamLoggingNormalizationTests(unittest.TestCase):
    def _load_comment_out_task(self):
        tasks = yaml.safe_load(TASKS_FILE.read_text(encoding="utf-8"))
        for task in tasks:
            if task.get("name") == "Comment out pre-existing active freshclam logging directives":
                return task["loop"], task["ansible.builtin.replace"]["replace"]
        self.fail("Expected freshclam logging normalization task was not found.")

    def test_mixed_active_and_commented_directives_normalize_idempotently(self):
        regexes, replacement = self._load_comment_out_task()
        config = (
            "#UpdateLogFile /var/log/clamav/already-commented.log\n"
            "  # LogRotate no\n"
            "# LogFileMaxSize 1M\n"
            "UpdateLogFile /var/log/clamav/active.log\n"
            "  LogRotate no\n"
            "LogFileMaxSize 2M\n"
        )

        normalized_once = config
        for pattern in regexes:
            normalized_once = re.sub(pattern, replacement, normalized_once, flags=re.MULTILINE)

        normalized_twice = normalized_once
        for pattern in regexes:
            normalized_twice = re.sub(pattern, replacement, normalized_twice, flags=re.MULTILINE)

        self.assertEqual(normalized_once, normalized_twice)
        self.assertIn("#UpdateLogFile /var/log/clamav/already-commented.log", normalized_once)
        self.assertIn("  # LogRotate no", normalized_once)
        self.assertIn("# LogFileMaxSize 1M", normalized_once)
        self.assertIn("# UpdateLogFile /var/log/clamav/active.log", normalized_once)
        self.assertIn("  # LogRotate no", normalized_once)
        self.assertIn("# LogFileMaxSize 2M", normalized_once)


if __name__ == "__main__":
    unittest.main()
