import importlib.util
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".github" / "scripts" / "generate_ci_dependency_artifacts.py"
SPEC = importlib.util.spec_from_file_location("generate_ci_dependency_artifacts", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class GenerateCiDependencyArtifactsTests(unittest.TestCase):
    def test_run_command_returns_none_when_command_fails(self):
        self.assertIsNone(
            MODULE.run_command(
                "python3",
                "-c",
                "import sys; sys.stderr.write('boom\\n'); raise SystemExit(2)",
            )
        )

    def test_collect_packages_deduplicates_stable_package_identity(self):
        original_parse_pip_freeze = MODULE.parse_pip_freeze
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
            MODULE.parse_ansible_collections = lambda output: []
            MODULE.run_command = lambda *command: ""

            packages = MODULE.collect_packages()
        finally:
            MODULE.parse_pip_freeze = original_parse_pip_freeze
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
                        "namespace.foo.bar": {"version": "3.2.1"},
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
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "namespace.foo.bar",
                    "version": "3.2.1",
                    "purl": "pkg:generic/namespace/foo/bar@3.2.1",
                },
            ],
        )

    def test_parse_os_release_ignores_comments_and_blank_lines(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            os_release_path = Path(tmp_dir) / "os-release"
            os_release_path.write_text(
                "\n".join(
                    [
                        'NAME="Ubuntu"',
                        "",
                        "# comment",
                        'VERSION_ID="26.04"',
                        "ID=ubuntu",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            os_release = MODULE.parse_os_release(os_release_path)

        self.assertEqual(
            os_release,
            {
                "NAME": "Ubuntu",
                "VERSION_ID": "26.04",
                "ID": "ubuntu",
            },
        )

    def test_parse_declared_ansible_collections_reads_requirements_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            requirements_path = Path(tmp_dir) / "requirements.yml"
            requirements_path.write_text(
                "\n".join(
                    [
                        "---",
                        "collections:",
                        "  - name: ansible.posix",
                        "  - name: namespace.foo.bar",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            declared = MODULE.parse_declared_ansible_collections(requirements_path)

        self.assertEqual(declared, {"ansible.posix", "namespace.foo.bar"})

    def test_build_ansible_collection_purl_rejects_malformed_collection_names(self):
        for collection_name in ("invalid", "namespace."):
            with self.subTest(collection_name=collection_name):
                with self.assertRaisesRegex(
                    ValueError, "Ansible collection names must use namespace.name format"
                ):
                    MODULE.build_ansible_collection_purl(collection_name, "1.0.0")

    def test_collect_packages_filters_ansible_collections_to_declared_set(self):
        original_parse_pip_freeze = MODULE.parse_pip_freeze
        original_parse_ansible_collections = MODULE.parse_ansible_collections
        original_parse_declared_ansible_collections = MODULE.parse_declared_ansible_collections
        original_run_command = MODULE.run_command

        try:
            MODULE.parse_pip_freeze = lambda output: []
            MODULE.parse_ansible_collections = lambda output: [
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "ansible.posix",
                    "version": "2.1.0",
                    "purl": "pkg:generic/ansible/posix@2.1.0",
                },
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "community.general",
                    "version": "10.0.1",
                    "purl": "pkg:generic/community/general@10.0.1",
                },
            ]
            MODULE.parse_declared_ansible_collections = lambda path=MODULE.DEFAULT_ANSIBLE_REQUIREMENTS_PATH: {
                "ansible.posix"
            }
            MODULE.run_command = lambda *command: ""

            packages = MODULE.collect_packages()
        finally:
            MODULE.parse_pip_freeze = original_parse_pip_freeze
            MODULE.parse_ansible_collections = original_parse_ansible_collections
            MODULE.parse_declared_ansible_collections = original_parse_declared_ansible_collections
            MODULE.run_command = original_run_command

        self.assertEqual(
            packages,
            [
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "ansible.posix",
                    "version": "2.1.0",
                    "purl": "pkg:generic/ansible/posix@2.1.0",
                }
            ],
        )

    def test_collect_packages_keeps_all_ansible_collections_when_declarations_unavailable(self):
        original_parse_pip_freeze = MODULE.parse_pip_freeze
        original_parse_ansible_collections = MODULE.parse_ansible_collections
        original_parse_declared_ansible_collections = MODULE.parse_declared_ansible_collections
        original_run_command = MODULE.run_command

        try:
            MODULE.parse_pip_freeze = lambda output: []
            MODULE.parse_ansible_collections = lambda output: [
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "ansible.posix",
                    "version": "2.1.0",
                    "purl": "pkg:generic/ansible/posix@2.1.0",
                },
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "community.general",
                    "version": "10.0.1",
                    "purl": "pkg:generic/community/general@10.0.1",
                },
            ]
            MODULE.parse_declared_ansible_collections = (
                lambda path=MODULE.DEFAULT_ANSIBLE_REQUIREMENTS_PATH: None
            )
            MODULE.run_command = lambda *command: ""

            packages = MODULE.collect_packages()
        finally:
            MODULE.parse_pip_freeze = original_parse_pip_freeze
            MODULE.parse_ansible_collections = original_parse_ansible_collections
            MODULE.parse_declared_ansible_collections = original_parse_declared_ansible_collections
            MODULE.run_command = original_run_command

        self.assertEqual(
            packages,
            [
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "ansible.posix",
                    "version": "2.1.0",
                    "purl": "pkg:generic/ansible/posix@2.1.0",
                },
                {
                    "ecosystem": "ansible-galaxy",
                    "name": "community.general",
                    "version": "10.0.1",
                    "purl": "pkg:generic/community/general@10.0.1",
                },
            ],
        )

    def test_collect_manifest_includes_selected_github_metadata(self):
        with (
            mock.patch.object(MODULE, "parse_os_release", return_value={"ID": "ubuntu"}),
            mock.patch.object(
                MODULE,
                "run_command",
                side_effect=["pip 26.0 from /venv/lib/python/site-packages/pip", "ansible [core 2.18.0]", None],
            ),
            mock.patch.object(MODULE.platform, "platform", return_value="Linux-6.0"),
            mock.patch.object(MODULE.platform, "python_version", return_value="3.12.0"),
            mock.patch.dict(
                MODULE.os.environ,
                {
                    "GITHUB_REPOSITORY": "brabster/xubuntu-workstation",
                    "GITHUB_RUN_ID": "12345",
                    "GITHUB_RUN_ATTEMPT": "2",
                    "RUNNER_OS": "Linux",
                    "RUNNER_ARCH": "",
                },
                clear=True,
            ),
        ):
            manifest = MODULE.collect_manifest(
                "artifact-job",
                [
                    {
                        "ecosystem": "pypi",
                        "name": "ansible-lint",
                        "version": "26.9.0",
                        "purl": "pkg:pypi/ansible-lint@26.9.0",
                    }
                ],
            )

        self.assertEqual(manifest["job_name"], "artifact-job")
        self.assertEqual(manifest["package_count"], 1)
        self.assertEqual(manifest["system"]["os_release"], {"ID": "ubuntu"})
        self.assertEqual(manifest["system"]["platform"], "Linux-6.0")
        self.assertEqual(manifest["python"]["version"], "3.12.0")
        self.assertEqual(
            manifest["github"],
            {
                "github_repository": "brabster/xubuntu-workstation",
                "github_run_id": "12345",
                "github_run_attempt": "2",
                "runner_os": "Linux",
            },
        )
        self.assertEqual(manifest["tools"]["ansible"], "ansible [core 2.18.0]")
        self.assertIsNone(manifest["tools"]["ansible_lint"])

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
            ],
        }

        document = MODULE.build_spdx_document("ansible-lint", manifest)

        self.assertEqual(document["spdxVersion"], "SPDX-2.3")
        self.assertEqual(document["documentDescribes"], ["SPDXRef-Package-1"])
        self.assertEqual(len(document["relationships"]), 1)
        self.assertEqual(
            document["documentNamespace"],
            "https://github.com/brabster%2Fxubuntu-workstation/actions/runs/12345/attempts/2/sbom/"
            "ansible-lint/83d7bde572f501e0",
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

    def test_build_spdx_document_requires_package_name_version_and_purl(self):
        with self.assertRaisesRegex(TypeError, "purl is required"):
            MODULE.build_spdx_document(
                "ansible-lint",
                {
                    "generated_at": "2026-09-27T21:30:00Z",
                    "github": {},
                    "packages": [
                        {
                            "name": "ansible-lint",
                            "version": "26.9.0",
                        }
                    ],
                },
            )

    def test_build_spdx_document_requires_string_version(self):
        with self.assertRaisesRegex(TypeError, "version must be a string"):
            MODULE.build_spdx_document(
                "ansible-lint",
                {
                    "generated_at": "2026-09-27T21:30:00Z",
                    "github": {},
                    "packages": [
                        {
                            "name": "ansible-lint",
                            "version": 26,
                            "purl": "pkg:pypi/ansible-lint@26.9.0",
                        }
                    ],
                },
            )

    def test_build_spdx_document_rejects_empty_purl(self):
        with self.assertRaisesRegex(ValueError, "purl must not be empty"):
            MODULE.build_spdx_document(
                "ansible-lint",
                {
                    "generated_at": "2026-09-27T21:30:00Z",
                    "github": {},
                    "packages": [
                        {
                            "name": "ansible-lint",
                            "version": "26.9.0",
                            "purl": "",
                        }
                    ],
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
                    "package_count": len(manifest_packages),
                    "packages": manifest_packages,
                }

                manifest_path, sbom_path = MODULE.write_reports(Path(tmp_dir), "local-check")
            finally:
                MODULE.collect_packages = original_collect_packages
                MODULE.collect_manifest = original_collect_manifest

            self.assertTrue(manifest_path.exists())
            self.assertTrue(sbom_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            sbom = json.loads(sbom_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["job_name"], "local-check")
            self.assertEqual(manifest["package_count"], len(manifest["packages"]))
            self.assertEqual(sbom["spdxVersion"], "SPDX-2.3")
            self.assertEqual(len(sbom["documentDescribes"]), len(sbom["packages"]))


if __name__ == "__main__":
    unittest.main()
