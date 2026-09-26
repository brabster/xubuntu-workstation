import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import get_ansible_lint_version as galv


class GetAnsibleLintVersionTests(unittest.TestCase):
    def test_extracts_version_without_v_prefix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Path(tmpdir) / ".pre-commit-config.yaml"
            config.write_text(
                "repos:\n"
                "  - repo: https://github.com/ansible/ansible-lint\n"
                "    rev: v26.9.0\n"
                "    hooks:\n"
                "      - id: ansible-lint\n",
                encoding="utf-8",
            )

            version = galv.ansible_lint_version(config)

        self.assertEqual(version, "26.9.0")


if __name__ == "__main__":
    unittest.main()
