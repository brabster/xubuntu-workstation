import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_FILE = REPO_ROOT / ".github" / "workflows" / "test_install.yml"


class InstallWorkflowTests(unittest.TestCase):
    def test_ubuntu_images_run_without_cancelling_each_other(self):
        workflow = yaml.safe_load(WORKFLOW_FILE.read_text(encoding="utf-8"))
        strategy = workflow["jobs"]["test_install"]["strategy"]

        self.assertIs(strategy["fail-fast"], False)
        self.assertEqual(
            ["ubuntu:latest", "ubuntu:rolling"], strategy["matrix"]["image"]
        )

    def test_setup_user_uses_useradd_with_explicit_defaults(self):
        workflow = yaml.safe_load(WORKFLOW_FILE.read_text(encoding="utf-8"))
        steps = workflow["jobs"]["test_install"]["steps"]
        setup_step = next(step for step in steps if step.get("name") == "setup user")

        self.assertEqual(
            "useradd --create-home --user-group --shell /bin/bash --comment '' tester",
            setup_step["run"].splitlines()[0],
        )

    def test_debug_info_reads_standard_os_release(self):
        workflow = yaml.safe_load(WORKFLOW_FILE.read_text(encoding="utf-8"))
        steps = workflow["jobs"]["test_install"]["steps"]
        debug_step = next(step for step in steps if step.get("name") == "debug info")

        self.assertEqual("cat /etc/os-release", debug_step["run"].strip())

    def test_install_checks_fail_fast_and_query_sudo_permissions(self):
        workflow = yaml.safe_load(WORKFLOW_FILE.read_text(encoding="utf-8"))
        steps = workflow["jobs"]["test_install"]["steps"]
        check_step = next(step for step in steps if step.get("name") == "check")
        commands = check_step["run"].splitlines()

        self.assertEqual("set -euo pipefail", commands[0])
        self.assertIn('su - tester -c "python3 --version"', commands)
        self.assertIn("if sudo -l -U tester; then", commands)
        self.assertIn("visudo -c", commands)
        self.assertFalse(any("sudo -n" in command for command in commands))


if __name__ == "__main__":
    unittest.main()
