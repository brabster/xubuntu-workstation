import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_FILE = REPO_ROOT / ".github" / "workflows" / "test_install.yml"


class InstallWorkflowTests(unittest.TestCase):
    def test_debug_info_reads_standard_os_release(self):
        workflow = yaml.safe_load(WORKFLOW_FILE.read_text(encoding="utf-8"))
        steps = workflow["jobs"]["test_install"]["steps"]
        debug_step = next(step for step in steps if step.get("name") == "debug info")

        self.assertEqual("cat /etc/os-release", debug_step["run"].strip())


if __name__ == "__main__":
    unittest.main()
