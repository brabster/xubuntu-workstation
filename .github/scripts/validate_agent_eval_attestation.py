import argparse
import json
import re
from pathlib import Path


AGENT_SYSTEM_PATHS = (
    "AGENTS.md",
    ".github/copilot-instructions.md",
    ".github/workflows/copilot-setup-steps.yml",
    ".githooks/pre-commit",
    "requirements-dev.txt",
    "roles/requirements.yml",
)
AGENT_SYSTEM_PREFIXES = (
    ".devcontainer/",
    ".githooks/",
    ".github/agents/",
    ".github/instructions/",
    ".github/prompts/",
    "docs/wiki/",
    "evals/",
    "prompts/",
)
ATTESTATION_PATTERN = re.compile(
    r"<!-- agent-eval-attestation\s*(.*?)\s*-->",
    re.DOTALL,
)


def requires_attestation(changed_files):
    return any(
        path in AGENT_SYSTEM_PATHS
        or path.startswith(AGENT_SYSTEM_PREFIXES)
        for path in changed_files
    )


def validate_attestation(changed_files, body, head_sha):
    if not requires_attestation(changed_files):
        return []

    matches = ATTESTATION_PATTERN.findall(body or "")
    if len(matches) != 1:
        return ["PR body must contain exactly one agent eval attestation block"]

    try:
        attestation = json.loads(matches[0])
    except json.JSONDecodeError:
        return ["agent eval attestation block must contain valid JSON"]

    if not isinstance(attestation, dict):
        return ["agent eval attestation must be a JSON object"]

    errors = []
    if attestation.get("head_sha") != head_sha:
        errors.append("agent eval attestation head_sha must match the current PR head")
    if attestation.get("result") != "pass":
        errors.append("agent eval attestation result must be 'pass'")
    if attestation.get("cases") != "all":
        errors.append("agent eval attestation cases must be 'all'")
    for field in ("evaluator", "runtime"):
        if not isinstance(attestation.get(field), str) or not attestation[field].strip():
            errors.append(f"agent eval attestation {field} must be a non-empty string")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, type=Path)
    parser.add_argument("--changed-files", required=True, type=Path)
    args = parser.parse_args()

    event = json.loads(args.event.read_text(encoding="utf-8"))
    pull_request = event.get("pull_request", {})
    changed_files = args.changed_files.read_text(encoding="utf-8").splitlines()
    errors = validate_attestation(
        changed_files,
        pull_request.get("body", ""),
        pull_request.get("head", {}).get("sha", ""),
    )

    if errors:
        for error in errors:
            print(f"::error::{error}")
        raise SystemExit(1)

    if requires_attestation(changed_files):
        print("Agent eval attestation is present and current.")
    else:
        print("No agent-system files changed; behavioral attestation is not required.")


if __name__ == "__main__":
    main()
