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
            "printf '%s\\n' \"${TEST_JOURNAL_LINES:-}\"\n",
        )

        self.env = os.environ.copy()
        self.env["PATH"] = f"{self.fake_bin}:{self.env.get('PATH', '')}"
        self.env["CLAMAV_DOWNLOADS_DIR"] = str(self.downloads_dir)
        self.env["CLAMAV_QUARANTINE_DIR"] = str(self.quarantine_dir)
        self.env["CLAMAV_LOG_DIR"] = str(self.log_dir)
        self.env["TEST_DOWNLOADS_DIR"] = str(self.downloads_dir)
        self.env["TEST_QUARANTINE_DIR"] = str(self.quarantine_dir)

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

    def test_uses_latest_non_empty_rotated_freshclam_log(self):
        (self.log_dir / "freshclam.log").write_text("", encoding="utf-8")
        rotated_log = self.log_dir / "freshclam.log.1"
        rotated_log.write_text(
            "old line\n"
            "Mon May 11 19:07:36 2026 -> Database test passed.\n"
            "Mon May 11 19:07:36 2026 -> bytecode.cvd updated (version: 339, sigs: 80, f-level: 90, builder: nrandolp)\n"
            "Mon May 11 19:07:36 2026 -> WARNING: Clamd was NOT notified: Can't connect to clamd through /run/clamav/clamd.ctl: No such file or directory\n",
            encoding="utf-8",
        )
        os.utime(rotated_log, None)

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Database test passed.", result.stdout)
        self.assertIn("bytecode.cvd updated", result.stdout)
        self.assertIn("WARNING: Clamd was NOT notified", result.stdout)
        self.assertIn("ClamAV on-access scanning is working correctly.", result.stdout)

    def test_falls_back_to_journal_when_no_freshclam_log_has_content(self):
        (self.log_dir / "freshclam.log").write_text("", encoding="utf-8")
        self.env["TEST_JOURNAL_LINES"] = (
            "line one\n"
            "line two\n"
            "line three"
        )

        result = self._run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(" --- latest antivirus update log", result.stdout)
        self.assertIn("line one", result.stdout)
        self.assertIn("line two", result.stdout)
        self.assertIn("line three", result.stdout)


if __name__ == "__main__":
    unittest.main()
