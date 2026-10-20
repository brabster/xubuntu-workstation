import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml
from jinja2 import Environment


REPO_ROOT = Path(__file__).resolve().parents[1]
SLACK_TASKS = REPO_ROOT / "roles" / "slack" / "tasks" / "main.yml"
SLACK_KEY = REPO_ROOT / "roles" / "slack" / "files" / "slack-packagecloud.asc"


class SlackRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = yaml.safe_load(SLACK_TASKS.read_text(encoding="utf-8"))

    def _task(self, name):
        for task in self.tasks:
            if task.get("name") == name:
                return task
        self.fail(f"Task not found: {name}")

    def test_existing_keyring_is_revalidated_before_skip(self):
        inspect_task = self._task("Inspect installed Slack keyring fingerprint")
        self.assertEqual(inspect_task.get("when"), "slack_keyring_stat.stat.exists")

        validity_task = self._task("Set Slack keyring validity fact")
        validity_expr = validity_task["ansible.builtin.set_fact"]["slack_keyring_is_valid"]
        self.assertIn("slack_keyring_stat.stat.exists", validity_expr)
        self.assertIn("slack_installed_pubkey_count | default(0)", validity_expr)
        self.assertIn("DB085A08CA13B8ACB917E0F6D938EC0D038651BD", validity_expr)

        bootstrap_task = self._task("Install Slack Packagecloud signing key")
        self.assertEqual(bootstrap_task.get("when"), "not slack_keyring_is_valid")

    def test_same_fingerprint_keyring_requires_current_certifications(self):
        stat_task = self._task("Check whether Slack keyring is already installed")
        self.assertEqual("sha256", stat_task["ansible.builtin.stat"]["checksum_algorithm"])
        keyring = subprocess.run(
            ["gpg", "--dearmor"], input=SLACK_KEY.read_bytes(),
            capture_output=True, check=True,
        ).stdout
        checksum = hashlib.sha256(keyring).hexdigest()
        validity_expr = self._task("Set Slack keyring validity fact")[
            "ansible.builtin.set_fact"
        ]["slack_keyring_is_valid"]
        self.assertIn(
            f"(slack_keyring_stat.stat.checksum | default('')) == '{checksum}'",
            validity_expr,
        )
        is_valid = Environment().compile_expression(validity_expr.strip()[2:-2])
        facts = {
            "slack_keyring_stat": {"stat": {"exists": True, "checksum": checksum}},
            "slack_installed_pubkey_count": 1,
            "slack_installed_fingerprints": [
                "DB085A08CA13B8ACB917E0F6D938EC0D038651BD"
            ],
        }
        self.assertTrue(is_valid(**facts))
        facts["slack_keyring_stat"]["stat"]["checksum"] = "obsolete-keyring"
        self.assertFalse(is_valid(**facts))
        facts["slack_keyring_stat"]["stat"] = {"exists": False}
        self.assertFalse(is_valid(**facts))

    def test_vendored_key_has_valid_sha512_certifications(self):
        with tempfile.TemporaryDirectory() as home:
            subprocess.run(
                ["gpg", "--homedir", home, "--import", str(SLACK_KEY)],
                capture_output=True, check=True,
            )
            result = subprocess.run(
                ["gpg", "--homedir", home, "--with-colons", "--check-sigs",
                 "DB085A08CA13B8ACB917E0F6D938EC0D038651BD"],
                capture_output=True, text=True, check=True,
            )
        signatures = [
            line.split(":") for line in result.stdout.splitlines()
            if line.startswith("sig:")
        ]
        self.assertEqual(2, len(signatures))
        self.assertEqual({"13x", "18x"}, {sig[10] for sig in signatures})
        for sig in signatures:
            self.assertEqual("!", sig[1])
            self.assertEqual("10", sig[15])

    def test_bootstrap_block_checks_single_expected_fingerprint(self):
        bootstrap_task = self._task("Install Slack Packagecloud signing key")
        stage_task = next(
            subtask
            for subtask in bootstrap_task["block"]
            if subtask.get("name") == "Stage vendored Slack Packagecloud GPG key candidate"
        )
        self.assertEqual(stage_task["ansible.builtin.copy"]["src"], "slack-packagecloud.asc")

        fingerprint_assert = next(
            subtask
            for subtask in bootstrap_task["block"]
            if subtask.get("name") == "Assert Slack Packagecloud GPG key matches expected fingerprint"
        )

        assertions = fingerprint_assert["ansible.builtin.assert"]["that"]
        self.assertIn("slack_gpg_pubkey_count == 1", assertions)
        self.assertIn("slack_gpg_fingerprints | length >= 1", assertions)
        self.assertIn(
            "slack_gpg_fingerprints[0] == 'DB085A08CA13B8ACB917E0F6D938EC0D038651BD'",
            assertions,
        )

    def test_repository_changes_trigger_explicit_cache_refresh(self):
        repository_task = self._task("Add Slack APT repository")
        self.assertEqual(repository_task.get("register"), "slack_apt_source")

        apt_list_task = self._task("Check for cached Slack apt metadata")
        self.assertEqual(apt_list_task["ansible.builtin.find"]["paths"], "/var/lib/apt/lists")

        bootstrap_refresh = self._task("Refresh apt package metadata for Slack bootstrap")
        self.assertEqual(
            bootstrap_refresh.get("when"),
            "(not slack_keyring_is_valid) or slack_apt_source.changed or slack_apt_list_files.matched == 0",
        )

        stale_refresh = self._task("Refresh apt package metadata for stale Slack cache")
        self.assertEqual(
            stale_refresh.get("when"),
            "slack_keyring_is_valid and (not slack_apt_source.changed) and slack_apt_list_files.matched > 0",
        )


if __name__ == "__main__":
    unittest.main()
