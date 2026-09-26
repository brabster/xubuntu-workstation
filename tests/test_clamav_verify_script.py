import gzip
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TEMPLATE = REPO_ROOT / "roles" / "clamav" / "templates" / "clamav-verify.sh.j2"


class ClamavVerifyScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.downloads_dir = self.root / "downloads"
        self.downloads_dir.mkdir()
        self.quarantine_dir = self.root / "quarantine"
        self.quarantine_dir.mkdir()
        self.log_dir = self.root / "logs"
        self.log_dir.mkdir()
        self.fake_bin = self.root / "bin"
        self.fake_bin.mkdir()
        self.script_path = self.root / "clamav-verify.sh"

        script = SCRIPT_TEMPLATE.read_text(encoding="utf-8").replace(
            "{{ clamav_quarantine_dir }}",
            str(self.quarantine_dir),
        )
        self.script_path.write_text(script, encoding="utf-8")
        self.script_path.chmod(self.script_path.stat().st_mode | stat.S_IXUSR)

        self._write_executable(
            "date",
            "#!/usr/bin/env bash\n"
            "if [ \"$1\" = \"+%s\" ]; then\n"
            "  printf '1234\\n'\n"
            "else\n"
            "  /bin/date \"$@\"\n"
            "fi\n",
        )
        self._write_executable(
            "runuser",
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "cmd=''\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  case \"$1\" in\n"
            "    -c)\n"
            "      cmd=\"$2\"\n"
            "      shift 2\n"
            "      ;;\n"
            "    *)\n"
            "      shift\n"
            "      ;;\n"
            "  esac\n"
            "done\n"
            "bash -lc \"$cmd\"\n"
            "if [ -n \"${TEST_QUARANTINE_DIR:-}\" ]; then\n"
            "  for file in \"${TEST_DOWNLOADS_DIR:-}\"/.health-check-*.txt; do\n"
            "    [ -e \"$file\" ] || continue\n"
            "    cp \"$file\" \"${TEST_QUARANTINE_DIR}/$(basename \"$file\")\"\n"
            "  done\n"
            "fi\n",
        )
        self._write_executable(
            "journalctl",
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [ -n \"${TEST_JOURNALCTL_ARGS_FILE:-}\" ]; then\n"
            "  printf '%s\\n' \"$@\" > \"$TEST_JOURNALCTL_ARGS_FILE\"\n"
            "fi\n"
            "if [ -n \"${TEST_JOURNAL_OUTPUT_FILE:-}\" ] && [ -f \"${TEST_JOURNAL_OUTPUT_FILE}\" ]; then\n"
            "  cat \"${TEST_JOURNAL_OUTPUT_FILE}\"\n"
            "fi\n",
        )

        self.env = os.environ.copy()
        self.env["PATH"] = f"{self.fake_bin}:{self.env.get('PATH', '')}"
        self.env["CLAMAV_DOWNLOADS_DIR"] = str(self.downloads_dir)
        self.env["CLAMAV_QUARANTINE_DIR"] = str(self.quarantine_dir)
        self.env["CLAMAV_LOG_DIR"] = str(self.log_dir)
        self.env["TEST_DOWNLOADS_DIR"] = str(self.downloads_dir)
        self.env["TEST_QUARANTINE_DIR"] = str(self.quarantine_dir)
        self.journal_output_file = self.root / "journal-output.log"
        self.journal_args_file = self.root / "journal-args.log"
        self.env["TEST_JOURNAL_OUTPUT_FILE"] = str(self.journal_output_file)
        self.env["TEST_JOURNALCTL_ARGS_FILE"] = str(self.journal_args_file)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_executable(self, name: str, content: str):
        path = self.fake_bin / name
        path.write_text(content, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def _run_script(self):
        return subprocess.run(
            [str(self.script_path), "tester"],
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_uses_first_rotated_freshclam_log_when_current_log_is_empty(self):
        (self.log_dir / "freshclam.log").write_text("", encoding="utf-8")
        rotated_log = self.log_dir / "freshclam.log.1"
        rotated_log.write_text(
            "old line\n"
            "Mon May 11 19:07:36 2026 -> Database test passed.\n"
            "Mon May 11 19:07:36 2026 -> bytecode.cvd updated (version: 339, sigs: 80, f-level: 90, builder: nrandolp)\n"
            "Mon May 11 19:07:36 2026 -> WARNING: Clamd was NOT notified: Can't connect to clamd through /run/clamav/clamd.ctl: No such file or directory\n",
            encoding="utf-8",
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Database test passed.", result.stdout)
        self.assertIn("bytecode.cvd updated", result.stdout)
        self.assertIn("WARNING: Clamd was NOT notified", result.stdout)
        self.assertIn("ClamAV on-access scanning is working correctly.", result.stdout)

    def test_prefers_current_freshclam_log_over_first_rotated_log(self):
        (self.log_dir / "freshclam.log").write_text(
            "skip me\n"
            "current line one\n"
            "current line two\n"
            "current line three\n",
            encoding="utf-8",
        )
        (self.log_dir / "freshclam.log.1").write_text(
            "skip me\n"
            "rotated line one\n"
            "rotated line two\n"
            "rotated line three\n",
            encoding="utf-8",
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("current line one", result.stdout)
        self.assertIn("current line two", result.stdout)
        self.assertIn("current line three", result.stdout)
        self.assertNotIn("rotated line one", result.stdout)

    def test_reports_when_first_rotated_log_is_blank(self):
        (self.log_dir / "freshclam.log").write_text("", encoding="utf-8")
        (self.log_dir / "freshclam.log.1").write_text("\n", encoding="utf-8")

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("No recent antivirus update log entries were found.", result.stdout)

    def test_uses_later_rotated_log_when_first_rotation_is_blank(self):
        (self.log_dir / "freshclam.log").write_text("", encoding="utf-8")
        (self.log_dir / "freshclam.log.1").write_text("\n", encoding="utf-8")
        (self.log_dir / "freshclam.log.2").write_text(
            "skip me\n"
            "later line one\n"
            "later line two\n"
            "later line three\n",
            encoding="utf-8",
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("later line one", result.stdout)
        self.assertIn("later line two", result.stdout)
        self.assertIn("later line three", result.stdout)

    def test_uses_compressed_rotated_log_when_plain_rotations_are_blank(self):
        (self.log_dir / "freshclam.log").write_text("", encoding="utf-8")
        (self.log_dir / "freshclam.log.1").write_text("\n", encoding="utf-8")
        with gzip.open(self.log_dir / "freshclam.log.2.gz", "wt", encoding="utf-8") as handle:
            handle.write(
                "skip me\n"
                "compressed line one\n"
                "compressed line two\n"
                "compressed line three\n"
            )

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("compressed line one", result.stdout)
        self.assertIn("compressed line two", result.stdout)
        self.assertIn("compressed line three", result.stdout)

    def test_reports_when_first_rotated_log_cannot_be_read(self):
        (self.log_dir / "freshclam.log").write_text("", encoding="utf-8")
        rotated_log = self.log_dir / "freshclam.log.1"
        rotated_log.write_text(
            "skip me\n"
            "hidden line one\n"
            "hidden line two\n"
            "hidden line three\n",
            encoding="utf-8",
        )
        rotated_log.chmod(0)
        self.addCleanup(
            lambda: rotated_log.exists()
            and rotated_log.chmod(stat.S_IRUSR | stat.S_IWUSR)
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("No recent antivirus update log entries were found.", result.stdout)
        self.assertEqual("", result.stderr)
        self.assertNotIn("hidden line one", result.stdout)

    def test_reports_when_no_recent_freshclam_log_lines_are_found(self):
        (self.log_dir / "freshclam.log").write_text("", encoding="utf-8")

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(" --- latest antivirus update log", result.stdout)
        self.assertIn("No recent antivirus update log entries were found.", result.stdout)

    def test_uses_current_boot_journal_when_logs_have_no_usable_entries(self):
        (self.log_dir / "freshclam.log").write_text("", encoding="utf-8")
        (self.log_dir / "freshclam.log.1").write_text("\n", encoding="utf-8")
        self.journal_output_file.write_text(
            "noise line\n"
            "Mon May 11 19:07:36 2026 -> daily.cld updated\n"
            "Mon May 11 19:07:36 2026 -> bytecode.cvd updated\n"
            "Mon May 11 19:07:36 2026 -> Database updated (431223 signatures)\n",
            encoding="utf-8",
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("daily.cld updated", result.stdout)
        self.assertIn("bytecode.cvd updated", result.stdout)
        self.assertIn("Database updated (431223 signatures)", result.stdout)
        self.assertEqual(
            self.journal_args_file.read_text(encoding="utf-8").splitlines(),
            ["-u", "clamav-freshclam", "--boot", "0", "--no-pager", "-o", "cat"],
        )

    def test_metacharacters_in_downloads_dir_do_not_trigger_shell_injection(self):
        marker = self.root / "injected"
        downloads_dir = self.root / "downloads' ; touch injected ; echo '"
        downloads_dir.mkdir()
        self.env["CLAMAV_DOWNLOADS_DIR"] = str(downloads_dir)
        self.env["TEST_DOWNLOADS_DIR"] = str(downloads_dir)

        result = subprocess.run(
            [str(self.script_path), "tester"],
            env=self.env,
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertFalse(marker.exists(), msg=result.stderr)


if __name__ == "__main__":
    unittest.main()
