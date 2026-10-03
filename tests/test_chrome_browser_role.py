import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
CHROME_TASKS = REPO_ROOT / "roles" / "chrome_browser" / "tasks" / "tasks.yml"
CHROME_DEB = "/tmp/google-chrome-stable_current_amd64.deb"


class ChromeBrowserRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = yaml.safe_load(CHROME_TASKS.read_text(encoding="utf-8"))

    def _task(self, name):
        for task in self.tasks:
            if task.get("name") == name:
                return task
        self.fail(f"Task not found: {name}")

    def test_fetches_latest_stable_package_from_google_over_https(self):
        fetch_task = self._task("Fetch Chrome Browser")
        download = fetch_task["ansible.builtin.get_url"]

        self.assertEqual(
            download["url"],
            "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",
        )
        self.assertEqual(download["dest"], CHROME_DEB)

    def test_apt_installs_local_deb_without_manual_alsa_preinstall(self):
        install_task = self._task("Install Chrome")

        self.assertEqual(install_task["ansible.builtin.apt"]["deb"], CHROME_DEB)
        self.assertFalse(
            any(
                "libasound2" in str(task)
                for task in self.tasks
            )
        )


if __name__ == "__main__":
    unittest.main()
