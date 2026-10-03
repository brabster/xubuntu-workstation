#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ANSIBLE_REQUIREMENTS_PATH = REPO_ROOT / "roles" / "requirements.yml"


def run_command(*command: str) -> str | None:
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        stderr = (error.stderr or "").strip()
        message = stderr or f"exit code {error.returncode}"
        print(f"Command failed ({' '.join(command)}): {message}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print(f"Command not found ({' '.join(command)})", file=sys.stderr)
        return None
    return completed.stdout.strip()


def parse_os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"')
    return values


def parse_pip_freeze(output: str | None) -> list[dict[str, str]]:
    packages: list[dict[str, str]] = []
    if not output:
        return packages

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "==" not in stripped:
            continue
        name, version = stripped.split("==", 1)
        packages.append(
            {
                "ecosystem": "pypi",
                "name": name,
                "version": version,
                "purl": f"pkg:pypi/{quote(name.lower(), safe='')}" f"@{quote(version, safe='')}",
            }
        )
    return packages


def parse_ansible_collections(output: str | None) -> list[dict[str, str]]:
    if not output:
        return []

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return []

    packages: list[dict[str, str]] = []
    for collection_root in data.values():
        if not isinstance(collection_root, dict):
            continue
        for collection_name, details in collection_root.items():
            if not isinstance(details, dict):
                continue
            version = details.get("version")
            if not isinstance(version, str) or not version:
                continue
            packages.append(
                {
                    "ecosystem": "ansible-galaxy",
                    "name": collection_name,
                    "version": version,
                    "purl": build_ansible_collection_purl(collection_name, version),
                }
            )
    return packages


def parse_declared_ansible_collections(
    path: Path = DEFAULT_ANSIBLE_REQUIREMENTS_PATH,
) -> set[str] | None:
    try:
        import yaml
    except ModuleNotFoundError:
        print(f"PyYAML not available while reading declared Ansible collections from {path}", file=sys.stderr)
        return None

    if not path.exists():
        print(f"Declared Ansible collection file not found: {path}", file=sys.stderr)
        return None

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as error:
        print(f"Failed to parse declared Ansible collections from {path}: {error}", file=sys.stderr)
        return None

    collections = data.get("collections", [])
    if not isinstance(collections, list):
        print(f"Declared Ansible collections in {path} are not a list", file=sys.stderr)
        return None

    declared: set[str] = set()
    for item in collections:
        if isinstance(item, str) and item:
            declared.add(item.lower())
            continue
        if isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str) and name:
                declared.add(name.lower())
    return declared


def filter_ansible_collections(
    packages: list[dict[str, str]],
    declared_collection_names: set[str] | None,
) -> list[dict[str, str]]:
    if declared_collection_names is None:
        return packages
    return [package for package in packages if package["name"].lower() in declared_collection_names]


def build_ansible_collection_purl(collection_name: str, version: str) -> str:
    namespace, _, name = collection_name.partition(".")
    if not namespace or not name:
        raise ValueError("Ansible collection names must use namespace.name format")
    name_parts = [quote(part.lower(), safe="") for part in name.split(".") if part]
    if not name_parts:
        raise ValueError("Ansible collection names must have a non-empty name component")
    return f"pkg:generic/{quote(namespace.lower(), safe='')}/{'/'.join(name_parts)}@{quote(version, safe='')}"


def collect_packages() -> list[dict[str, str]]:
    declared_ansible_collections = parse_declared_ansible_collections()
    packages = []
    packages.extend(parse_pip_freeze(run_command(sys.executable, "-m", "pip", "freeze", "--all")))
    packages.extend(
        filter_ansible_collections(
            parse_ansible_collections(
                run_command("ansible-galaxy", "collection", "list", "--format", "json")
            ),
            declared_ansible_collections,
        )
    )

    deduplicated: dict[tuple[str, str, str], dict[str, str]] = {}
    for package in packages:
        key = (
            package["ecosystem"],
            package["name"],
            package["version"],
        )
        deduplicated[key] = package

    return sorted(
        deduplicated.values(),
        key=lambda package: (
            package["ecosystem"],
            package["name"],
            package["version"],
        ),
    )


def collect_manifest(job_name: str, packages: list[dict[str, str]]) -> dict[str, object]:
    os_release = parse_os_release()
    github = {
        key.lower(): value
        for key, value in {
            "GITHUB_REPOSITORY": os.environ.get("GITHUB_REPOSITORY"),
            "GITHUB_REF": os.environ.get("GITHUB_REF"),
            "GITHUB_SHA": os.environ.get("GITHUB_SHA"),
            "GITHUB_RUN_ID": os.environ.get("GITHUB_RUN_ID"),
            "GITHUB_RUN_ATTEMPT": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "GITHUB_JOB": os.environ.get("GITHUB_JOB"),
            "GITHUB_WORKFLOW": os.environ.get("GITHUB_WORKFLOW"),
            "RUNNER_OS": os.environ.get("RUNNER_OS"),
            "RUNNER_ARCH": os.environ.get("RUNNER_ARCH"),
        }.items()
        if value
    }

    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "job_name": job_name,
        "python": {
            "executable": sys.executable,
            "version": platform.python_version(),
            "pip_version": run_command(sys.executable, "-m", "pip", "--version"),
        },
        "tools": {
            "ansible": run_command("ansible", "--version"),
            "ansible_lint": run_command("ansible-lint", "--version"),
        },
        "system": {
            "platform": platform.platform(),
            "os_release": os_release,
        },
        "github": github,
        "package_count": len(packages),
        "packages": packages,
    }


def optional_string(value: object, field_name: str, default: str) -> str:
    if value is None:
        return default
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string when present")
    return value


def required_string(mapping: dict[str, object], field_name: str) -> str:
    value = mapping.get(field_name)
    if value is None:
        raise TypeError(f"{field_name} is required")
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if not value:
        raise ValueError(f"{field_name} must not be empty")
    return value


def build_spdx_document(job_name: str, manifest: dict[str, object]) -> dict[str, object]:
    if "packages" not in manifest:
        raise TypeError("manifest packages field is required")
    packages = manifest["packages"]
    if not isinstance(packages, list):
        raise TypeError("manifest packages must be a list")

    github = manifest.get("github", {})
    if not isinstance(github, dict):
        raise TypeError("manifest github metadata must be a mapping")
    repository = optional_string(github.get("github_repository"), "manifest github_repository", "local/local")
    run_id = optional_string(github.get("github_run_id"), "manifest github_run_id", "local")
    run_attempt = optional_string(github.get("github_run_attempt"), "manifest github_run_attempt", "1")
    if "generated_at" not in manifest:
        raise TypeError("manifest generated_at field is required")
    generated_at = manifest["generated_at"]
    if not isinstance(generated_at, str):
        raise TypeError("manifest generated_at must be a string")

    spdx_packages = []
    relationships = []
    document_describes = []
    package_fingerprint_parts = []

    for index, package in enumerate(packages, start=1):
        if not isinstance(package, dict):
            raise TypeError("manifest package entries must be mappings")
        package_name = required_string(package, "name")
        package_version = required_string(package, "version")
        package_purl = required_string(package, "purl")
        package_id = f"SPDXRef-Package-{index}"
        entry = {
            "name": package_name,
            "SPDXID": package_id,
            "versionInfo": package_version,
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "externalRefs": [
                {
                    "referenceCategory": "PACKAGE-MANAGER",
                    "referenceType": "purl",
                    "referenceLocator": package_purl,
                }
            ],
        }
        spdx_packages.append(entry)
        relationships.append(
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": package_id,
            }
        )
        document_describes.append(package_id)
        package_fingerprint_parts.append(
            {
                "name": package_name,
                "purl": package_purl,
                "version": package_version,
            }
        )

    package_fingerprint = hashlib.sha256(
        json.dumps(package_fingerprint_parts, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]

    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"xubuntu-workstation CI SBOM ({job_name})",
        "documentNamespace": (
            "https://github.com/"
            f"{quote(repository, safe='')}/actions/runs/{quote(run_id, safe='')}/"
            f"attempts/{quote(run_attempt, safe='')}/sbom/"
            f"{quote(job_name, safe='')}/{package_fingerprint}"
        ),
        "creationInfo": {
            "created": generated_at,
            "creators": ["Tool: .github/scripts/generate_ci_dependency_artifacts.py"],
        },
        "documentDescribes": document_describes,
        "packages": spdx_packages,
        "relationships": relationships,
    }


def write_reports(output_dir: Path, job_name: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    packages = collect_packages()
    manifest = collect_manifest(job_name, packages)
    spdx_document = build_spdx_document(job_name, manifest)

    manifest_path = output_dir / "resolved-versions.json"
    sbom_path = output_dir / "sbom.spdx.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sbom_path.write_text(json.dumps(spdx_document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path, sbom_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate resolved-version manifest and SPDX SBOM artifacts for a CI job."
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--job-name", required=True)
    args = parser.parse_args()

    manifest_path, sbom_path = write_reports(Path(args.output_dir), args.job_name)
    print(f"Wrote resolved versions to {manifest_path}")
    print(f"Wrote SPDX SBOM to {sbom_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
