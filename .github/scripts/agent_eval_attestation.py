import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = REPO_ROOT / "evals" / "kb.json"
ATTESTATION_PATH = REPO_ROOT / "evals" / "agent-eval-attestation.json"
AGENT_SYSTEM_FILES = (
    "AGENTS.md",
    ".github/copilot-instructions.md",
    ".github/scripts/agent_eval_attestation.py",
    ".github/workflows/copilot-setup-steps.yml",
    ".github/workflows/kb_evals.yml",
    ".githooks/pre-commit",
    "evals/kb.json",
    "evals/README.md",
    "requirements-dev.txt",
    "roles/requirements.yml",
    "tests/test_kb_evals.py",
)
AGENT_SYSTEM_DIRECTORIES = (
    ".devcontainer",
    ".githooks",
    ".github/agents",
    ".github/instructions",
    ".github/prompts",
    "docs/wiki",
    "prompts",
)


def load_cases(repo_root=REPO_ROOT):
    cases_path = repo_root / "evals" / "kb.json"
    return json.loads(cases_path.read_text(encoding="utf-8"))["cases"]


def agent_system_files(repo_root=REPO_ROOT):
    files = set(AGENT_SYSTEM_FILES)
    for directory in AGENT_SYSTEM_DIRECTORIES:
        path = repo_root / directory
        if path.is_dir():
            files.update(
                candidate.relative_to(repo_root).as_posix()
                for candidate in path.rglob("*")
                if candidate.is_file()
            )
        else:
            files.add(directory)
    files.discard("evals/agent-eval-attestation.json")
    return sorted(files)


def agent_system_digest(repo_root=REPO_ROOT):
    digest = hashlib.sha256()
    for relative_path in agent_system_files(repo_root):
        path = repo_root / relative_path
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        if path.is_file():
            content = path.read_bytes()
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
        else:
            digest.update(b"MISSING")
        digest.update(b"\0")
    return digest.hexdigest()


def build_attestation(repo_root=REPO_ROOT):
    return {
        "agent_system_sha256": agent_system_digest(repo_root),
        "result": "pass",
        "cases": [case["id"] for case in load_cases(repo_root)],
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_attestation(attestation, repo_root=REPO_ROOT):
    if not isinstance(attestation, dict):
        return ["attestation must be a JSON object"]

    errors = []
    if attestation.get("agent_system_sha256") != agent_system_digest(repo_root):
        errors.append("attestation is stale: agent-system inputs have changed")
    if attestation.get("result") != "pass":
        errors.append("attestation result must be 'pass'")
    expected_cases = [case["id"] for case in load_cases(repo_root)]
    if attestation.get("cases") != expected_cases:
        errors.append("attestation cases must list every current evaluation case")
    evaluated_at = attestation.get("evaluated_at")
    try:
        timestamp = datetime.fromisoformat(evaluated_at)
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError
    except (TypeError, ValueError):
        errors.append(
            "attestation evaluated_at must be a timezone-aware ISO 8601 timestamp"
        )
    return errors


def record_attestation(output_path=ATTESTATION_PATH, repo_root=REPO_ROOT):
    attestation = build_attestation(repo_root)
    output_path.write_text(
        json.dumps(attestation, indent=2) + "\n",
        encoding="utf-8",
    )
    return attestation


def confirm_evaluation_passed():
    response = input(
        "Have you run and passed every current behavioral evaluation case? [y/N] "
    )
    return response.strip().casefold() in ("y", "yes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate existing evidence instead of recording a passing evaluation",
    )
    args = parser.parse_args()
    if not args.check:
        if not confirm_evaluation_passed():
            raise SystemExit("Behavioral evaluation attestation was not recorded.")
        record_attestation(ATTESTATION_PATH, REPO_ROOT)
        print(f"Wrote behavioral eval evidence to {ATTESTATION_PATH}")
        return

    attestation = json.loads(ATTESTATION_PATH.read_text(encoding="utf-8"))
    errors = validate_attestation(attestation)
    if errors:
        for error in errors:
            print(f"::error::{error}")
        raise SystemExit(1)
    print("Behavioral eval evidence matches the current agent system.")


if __name__ == "__main__":
    main()
