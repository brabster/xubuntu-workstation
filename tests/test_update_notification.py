import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
NOTIFIER = (
    REPO_ROOT
    / "roles"
    / "updates"
    / "files"
    / "xubuntu-workstation-update-notify"
)


class UpdateNotificationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.cache_dir = self.root / "cache"
        self.notifications = self.root / "notifications"
        self.state_dir = self.root / "state"
        self.state_dir.mkdir()
        self.script = self.root / "notify"
        content = NOTIFIER.read_text(encoding="utf-8")
        content = content.replace(
            "/var/lib/xubuntu-workstation-update", str(self.state_dir)
        )
        content = content.replace(
            "/var/log/xubuntu-workstation-update.log", str(self.root / "update.log")
        )
        content = content.replace("reminder_interval=86400", "reminder_interval=1")
        self.script.write_text(content, encoding="utf-8")
        self.script.chmod(0o755)

        systemctl = self.bin_dir / "systemctl"
        systemctl.write_text(
            "#!/bin/sh\n"
            '[ "${SYSTEMCTL_FAIL:-}" = yes ] && exit 1\n'
            'case "$*" in\n'
            '  *ActiveState*) printf "%s\\n" "${UPDATE_ACTIVE_STATE:-inactive}" ;;\n'
            '  *Result*) printf "%s\\n" "${UPDATE_RESULT:-success}" ;;\n'
            '  *ExecMainStatus*) printf "%s\\n" "${UPDATE_EXIT_STATUS:-0}" ;;\n'
            "esac\n",
            encoding="utf-8",
        )
        systemctl.chmod(0o755)

        notify_send = self.bin_dir / "notify-send"
        notify_send.write_text(
            "#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$NOTIFICATIONS\"\n",
            encoding="utf-8",
        )
        notify_send.chmod(0o755)

    def _run_notifier(
        self, active="inactive", result="success", exit_status="0", fail_systemctl=False
    ):
        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{self.bin_dir}:{environment['PATH']}",
                "HOME": str(self.root),
                "XDG_CACHE_HOME": str(self.cache_dir),
                "DBUS_SESSION_BUS_ADDRESS": "unix:path=/tmp/test-bus",
                "DISPLAY": ":0",
                "NOTIFICATIONS": str(self.notifications),
                "UPDATE_ACTIVE_STATE": active,
                "UPDATE_RESULT": result,
                "UPDATE_EXIT_STATUS": exit_status,
                "SYSTEMCTL_FAIL": "yes" if fail_systemctl else "no",
            }
        )
        return subprocess.run(
            [str(self.script), "--once"],
            check=False,
            env=environment,
            capture_output=True,
            text=True,
        )

    def test_failure_notifications_are_deduplicated_until_reminder_is_due(self):
        first = self._run_notifier(active="failed", result="exit-code", exit_status="1")
        second = self._run_notifier(active="failed", result="exit-code", exit_status="1")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        notifications = self.notifications.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(notifications), 1)
        self.assertIn("Workstation updates failed", notifications[0])
        self.assertIn("next hourly run", notifications[0])

        notified_file = self.cache_dir / "xubuntu-workstation-update" / "last-notification"
        notified_file.write_text("failed:exit-code:1 1\n", encoding="utf-8")
        third = self._run_notifier(active="failed", result="exit-code", exit_status="1")

        self.assertEqual(third.returncode, 0, third.stderr)
        notifications = self.notifications.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(notifications), 2)

    def test_missing_success_record_notifies_that_updates_are_overdue(self):
        result = self._run_notifier()

        self.assertEqual(result.returncode, 0, result.stderr)
        notification = self.notifications.read_text(encoding="utf-8")
        self.assertIn("Workstation updates are overdue", notification)
        self.assertIn("last 26 hours", notification)

    def test_recent_success_does_not_notify(self):
        marker = self.state_dir / "last-success"
        marker.write_text("now\n", encoding="utf-8")

        result = self._run_notifier()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.notifications.exists())

    def test_status_query_failure_is_reported(self):
        result = self._run_notifier(fail_systemctl=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        notification = self.notifications.read_text(encoding="utf-8")
        self.assertIn("Cannot check workstation updates", notification)


if __name__ == "__main__":
    unittest.main()
