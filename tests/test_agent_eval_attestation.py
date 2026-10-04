import importlib.util
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".github" / "scripts" / "validate_agent_eval_attestation.py"
SPEC = importlib.util.spec_from_file_location("validate_agent_eval_attestation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


HEAD_SHA = "a" * 40
CHANGED_AGENT_FILE = ["docs/wiki/steering/session-workflow.md"]


def attestation(**overrides):
    values = {
        "head_sha": HEAD_SHA,
        "result": "pass",
        "cases": "all",
        "evaluator": "@reviewer",
        "runtime": "Copilot coding agent",
    }
    values.update(overrides)
    return "<!-- agent-eval-attestation\n" + json.dumps(values) + "\n-->"


class AgentEvalAttestationTests(unittest.TestCase):
    def test_unrelated_changes_do_not_require_attestation(self):
        self.assertEqual(
            MODULE.validate_attestation(["roles/firefox/tasks/main.yml"], "", HEAD_SHA),
            [],
        )

    def test_all_agent_system_paths_require_attestation(self):
        paths = [
            "AGENTS.md",
            ".github/copilot-instructions.md",
            ".github/workflows/copilot-setup-steps.yml",
            ".github/agents/reviewer.agent.md",
            ".github/instructions/python.instructions.md",
            ".github/prompts/review.prompt.md",
            ".githooks/pre-commit",
            ".devcontainer/devcontainer.json",
            "docs/wiki/README.md",
            "evals/kb.json",
            "prompts/00-feature-prompt.md",
            "requirements-dev.txt",
            "roles/requirements.yml",
        ]

        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(MODULE.requires_attestation([path]))

    def test_agent_system_change_requires_current_passing_full_attestation(self):
        self.assertEqual(
            MODULE.validate_attestation(
                CHANGED_AGENT_FILE, attestation(), HEAD_SHA
            ),
            [],
        )

    def test_missing_attestation_fails_for_agent_system_change(self):
        errors = MODULE.validate_attestation(CHANGED_AGENT_FILE, "", HEAD_SHA)

        self.assertIn("PR body must contain exactly one agent eval attestation block", errors)

    def test_stale_head_sha_fails(self):
        errors = MODULE.validate_attestation(
            CHANGED_AGENT_FILE,
            attestation(head_sha="b" * 40),
            HEAD_SHA,
        )

        self.assertIn("agent eval attestation head_sha must match the current PR head", errors)

    def test_failed_or_partial_eval_fails(self):
        errors = MODULE.validate_attestation(
            CHANGED_AGENT_FILE,
            attestation(result="fail", cases=["agent-bootstrap"]),
            HEAD_SHA,
        )

        self.assertIn("agent eval attestation result must be 'pass'", errors)
        self.assertIn("agent eval attestation cases must be 'all'", errors)

    def test_empty_evaluator_or_runtime_fails(self):
        errors = MODULE.validate_attestation(
            CHANGED_AGENT_FILE,
            attestation(evaluator=" ", runtime=""),
            HEAD_SHA,
        )

        self.assertIn("agent eval attestation evaluator must be a non-empty string", errors)
        self.assertIn("agent eval attestation runtime must be a non-empty string", errors)

    def test_invalid_json_fails(self):
        errors = MODULE.validate_attestation(
            CHANGED_AGENT_FILE,
            "<!-- agent-eval-attestation {invalid} -->",
            HEAD_SHA,
        )

        self.assertIn("agent eval attestation block must contain valid JSON", errors)


if __name__ == "__main__":
    unittest.main()
