import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
UPDATE_TEMPLATE = REPO_ROOT / "roles" / "updates" / "files" / "update.j2"


class UpdateScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.log_file = self.root / "update.log"
        self.state_dir = self.root / "state"
        self.state_dir.mkdir()
        script = UPDATE_TEMPLATE.read_text(encoding="utf-8")
        script = script.replace(
            "/var/log/xubuntu-workstation-update.log", str(self.log_file)
        )
        script = script.replace(
            "/var/lib/xubuntu-workstation-update", str(self.state_dir)
        )
        script = script.replace("{{ username }}", "tester")
        script = script.replace("{{ user_update_script }}", "/home/tester/update")
        self.script_path = self.root / "update"
        self.script_path.write_text(script, encoding="utf-8")
        self.script_path.chmod(0o755)

        self._write_command(
            "apt-get",
            'printf "apt-get %s\\n" "$*"\n[ "${FAIL_APT:-}" != yes ]',
        )
        self._write_command("snap", 'printf "snap %s\\n" "$*"\n')
        self._write_command("fwupdmgr", 'printf "fwupdmgr %s\\n" "$*"\n')
        self._write_command(
            "timeout",
            'shift 2\nshift\nexec "$@"\n',
        )
        self._write_command("runuser", 'printf "runuser %s\\n" "$*"\n')

    def _write_command(self, name, body):
        command = self.bin_dir / name
        command.write_text(f"#!/bin/sh\n{body}", encoding="utf-8")
        command.chmod(0o755)

    def _run_script(self, fail_apt=False):
        environment = os.environ.copy()
        environment["PATH"] = f"{self.bin_dir}:{environment['PATH']}"
        environment["FAIL_APT"] = "yes" if fail_apt else "no"
        return subprocess.run(
            ["/bin/sh", str(self.script_path)],
            check=False,
            env=environment,
            capture_output=True,
            text=True,
        )

    def test_success_records_completion_and_runs_user_hook_as_user(self):
        result = self._run_script()

        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.log_file.read_text(encoding="utf-8")
        self.assertIn("--with-new-pkgs upgrade", output)
        self.assertIn("fwupdmgr update --assume-yes", output)
        self.assertIn("runuser --user tester -- /home/tester/update", output)
        self.assertIn("=== Update completed at ", output)
        self.assertTrue((self.state_dir / "last-success").is_file())

    def test_failed_package_command_returns_failure_and_records_it(self):
        result = self._run_script(fail_apt=True)

        self.assertEqual(result.returncode, 1)
        output = self.log_file.read_text(encoding="utf-8")
        self.assertIn("=== Update FAILED at ", output)
        self.assertIn("(exit 1)", output)
        self.assertNotIn("Snap updates", output)
        self.assertFalse((self.state_dir / "last-success").exists())


if __name__ == "__main__":
    unittest.main()
