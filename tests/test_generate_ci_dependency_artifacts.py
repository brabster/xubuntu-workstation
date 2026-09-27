import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".github" / "scripts" / "generate_ci_dependency_artifacts.py"
SPEC = importlib.util.spec_from_file_location("generate_ci_dependency_artifacts", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class GenerateCiDependencyArtifactsTests(unittest.TestCase):
    def test_collect_packages_deduplicates_stable_package_identity(self):
        original_parse_pip_freeze = MODULE.parse_pip_freeze
        original_parse_dpkg_query = MODULE.parse_dpkg_query
        original_parse_ansible_collections = MODULE.parse_ansible_collections
        original_run_command = MODULE.run_command

        try:
            MODULE.parse_pip_freeze = lambda output: [
                {
                    "ecosystem": "pypi",
                    "name": "ansible-lint",
                    "version": "26.9.0",
                    "purl": "pkg:pypi/ansible-lint@26.9.0",
                },
                {
                    "ecosystem": "pypi",
                    "name": "ansible-lint",
                    "version": "26.9.0",
                    "purl": "pkg:pypi/ansible-lint@26.9.0",
                },
            ]
            MODULE.parse_dpkg_query = lambda output: []
            MODULE.parse_ansible_collections = lambda output: []
            MODULE.run_command = lambda *command: ""

            packages = MODULE.collect_packages()
        finally:
            MODULE.parse_pip_freeze = original_parse_pip_freeze
            MODULE.parse_dpkg_query = original_parse_dpkg_query
            MODULE.parse_ansible_collections = original_parse_ansible_collections
            MODULE.run_command = original_run_command

        self.assertEqual(
            packages,
            [
                {
                    "ecosystem": "pypi",
                    "name": "ansible-lint",
                    "version": "26.9.0",
                    "purl": "pkg:pypi/ansible-lint@26.9.0",
                }
            ],
        )

    def test_parse_pip_freeze_keeps_versioned_packages_only(self):
        packages = MODULE.parse_pip_freeze(
            "\n".join(
                [
                    "ansible-lint==26.9.0",
                    "editable @ file:///tmp/local-project",
                    "# comment",
                    "",
                    "PyYAML==6.0.2",
                ]
            )
        )

        self.assertEqual(
            packages,
            [
                {
                    "ecosystem": "pypi",
                    "name": "ansible-lint",
                    "version": "26.9.0",
                    "purl": "pkg:pypi/ansible-lint@26.9.0",
                },
                {
                    "ecosystem": "pypi",
                    "name": "PyYAML",
                    "version": "6.0.2",
                    "purl": "pkg:pypi/pyyaml@6.0.2",
                },
            ],
        )

    def test_parse_ansible_collections_flattens_collection_versions(self):
        packages = MODULE.parse_ansible_collections(
            json.dumps(
                {
                    "/usr/share/ansible/collections": {
                        "community.general": {"version": "10.0.1"},
                        "ansible.posix": {"version": "2.1.0"},
                    }
                }
            )
        )

        self.assertEqual(
            packages,
            [
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "community.general",
                    "version": "10.0.1",
                    "purl": "pkg:generic/community/general@10.0.1",
                },
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "ansible.posix",
                    "version": "2.1.0",
                    "purl": "pkg:generic/ansible/posix@2.1.0",
                },
            ],
        )

    def test_build_spdx_document_describes_all_packages(self):
        manifest = {
            "generated_at": "2026-09-27T21:30:00Z",
            "github": {
                "github_repository": "brabster/xubuntu-workstation",
                "github_run_id": "12345",
                "github_run_attempt": "2",
            },
            "packages": [
                {
                    "ecosystem": "pypi",
                    "name": "ansible-lint",
                    "version": "26.9.0",
                    "purl": "pkg:pypi/ansible-lint@26.9.0",
                },
                {
                    "ecosystem": "deb",
                    "name": "git",
                    "version": "1:2.34.1",
                    "architecture": "amd64",
                    "purl": "pkg:deb/git@1%3A2.34.1?arch=amd64",
                },
            ],
        }

        document = MODULE.build_spdx_document("ansible-lint", manifest)

        self.assertEqual(document["spdxVersion"], "SPDX-2.3")
        self.assertEqual(document["documentDescribes"], ["SPDXRef-Package-1", "SPDXRef-Package-2"])
        self.assertEqual(len(document["relationships"]), 2)
        self.assertEqual(document["packages"][1]["summary"], "Architecture: amd64")
        self.assertEqual(
            document["documentNamespace"],
            "https://github.com/brabster/xubuntu-workstation/actions/runs/12345/attempts/2/sbom/"
            "ansible-lint/2026-09-27T21%3A30%3A00Z",
        )

    def test_build_spdx_document_requires_list_packages(self):
        with self.assertRaisesRegex(TypeError, "manifest packages must be a list"):
            MODULE.build_spdx_document(
                "ansible-lint",
                {
                    "generated_at": "2026-09-27T21:30:00Z",
                    "github": {},
                    "packages": "not-a-list",
                },
            )

    def test_build_spdx_document_requires_packages_field(self):
        with self.assertRaisesRegex(TypeError, "manifest packages field is required"):
            MODULE.build_spdx_document(
                "ansible-lint",
                {
                    "generated_at": "2026-09-27T21:30:00Z",
                    "github": {},
                },
            )

    def test_build_spdx_document_requires_string_github_namespace_parts(self):
        with self.assertRaisesRegex(TypeError, "manifest github_run_id must be a string when present"):
            MODULE.build_spdx_document(
                "ansible-lint",
                {
                    "generated_at": "2026-09-27T21:30:00Z",
                    "github": {
                        "github_repository": "brabster/xubuntu-workstation",
                        "github_run_id": 12345,
                        "github_run_attempt": "2",
                    },
                    "packages": [],
                },
            )

    def test_build_spdx_document_requires_generated_at_field(self):
        with self.assertRaisesRegex(TypeError, "manifest generated_at field is required"):
            MODULE.build_spdx_document(
                "ansible-lint",
                {
                    "github": {},
                    "packages": [],
                },
            )

    def test_write_reports_outputs_manifest_and_sbom_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            original_collect_packages = MODULE.collect_packages
            original_collect_manifest = MODULE.collect_manifest

            try:
                packages = [
                    {
                        "ecosystem": "pypi",
                        "name": "ansible-lint",
                        "version": "26.9.0",
                        "purl": "pkg:pypi/ansible-lint@26.9.0",
                    }
                ]
                MODULE.collect_packages = lambda: packages
                MODULE.collect_manifest = lambda job_name, manifest_packages: {
                    "generated_at": "2026-09-27T21:30:00Z",
                    "github": {},
                    "job_name": job_name,
                    "packages": manifest_packages,
                }

                manifest_path, sbom_path = MODULE.write_reports(Path(tmp_dir), "local-check")
            finally:
                MODULE.collect_packages = original_collect_packages
                MODULE.collect_manifest = original_collect_manifest

            self.assertTrue(manifest_path.exists())
            self.assertTrue(sbom_path.exists())
            self.assertEqual(json.loads(manifest_path.read_text(encoding="utf-8"))["job_name"], "local-check")
            self.assertEqual(json.loads(sbom_path.read_text(encoding="utf-8"))["spdxVersion"], "SPDX-2.3")


if __name__ == "__main__":
    unittest.main()
