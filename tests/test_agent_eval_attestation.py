import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".github" / "scripts" / "agent_eval_attestation.py"
SPEC = importlib.util.spec_from_file_location("agent_eval_attestation", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class AgentEvalAttestationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        (self.repo / "evals").mkdir()
        (self.repo / "AGENTS.md").write_text("Agent rules\n", encoding="utf-8")
        (self.repo / "evals" / "kb.json").write_text(
            json.dumps({"cases": [{"id": "case-one"}, {"id": "case-two"}]}),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_recorded_attestation_passes_for_current_agent_system(self):
        attestation = MODULE.build_attestation(self.repo)

        self.assertEqual(MODULE.validate_attestation(attestation, self.repo), [])

    def test_agent_system_change_makes_existing_attestation_stale(self):
        attestation = MODULE.build_attestation(self.repo)
        (self.repo / "AGENTS.md").write_text("Changed agent rules\n", encoding="utf-8")

        self.assertIn(
            "attestation is stale: agent-system inputs have changed",
            MODULE.validate_attestation(attestation, self.repo),
        )

    def test_new_agent_instruction_file_changes_digest(self):
        digest = MODULE.agent_system_digest(self.repo)
        instructions = self.repo / ".github" / "instructions"
        instructions.mkdir(parents=True)
        (instructions / "python.instructions.md").write_text("New instruction\n", encoding="utf-8")

        self.assertNotEqual(MODULE.agent_system_digest(self.repo), digest)

    def test_eval_instructions_change_makes_attestation_stale(self):
        attestation = MODULE.build_attestation(self.repo)
        readme = self.repo / "evals" / "README.md"
        readme.write_text("Evaluation instructions\n", encoding="utf-8")
        attestation["agent_system_sha256"] = MODULE.agent_system_digest(self.repo)
        readme.write_text("Changed evaluation instructions\n", encoding="utf-8")

        self.assertIn(
            "attestation is stale: agent-system inputs have changed",
            MODULE.validate_attestation(attestation, self.repo),
        )

    def test_attestation_file_does_not_change_its_own_digest(self):
        digest = MODULE.agent_system_digest(self.repo)
        (self.repo / "evals" / "agent-eval-attestation.json").write_text(
            '{"result":"pass"}\n',
            encoding="utf-8",
        )

        self.assertEqual(MODULE.agent_system_digest(self.repo), digest)

    def test_all_current_cases_must_be_listed(self):
        attestation = MODULE.build_attestation(self.repo)
        attestation["cases"] = ["case-one"]

        self.assertIn(
            "attestation cases must list every current evaluation case",
            MODULE.validate_attestation(attestation, self.repo),
        )

    def test_result_and_timestamp_are_required(self):
        attestation = MODULE.build_attestation(self.repo)
        attestation.update(
            {
                "result": "fail",
                "evaluated_at": None,
            }
        )

        errors = MODULE.validate_attestation(attestation, self.repo)

        self.assertIn("attestation result must be 'pass'", errors)
        self.assertIn("attestation evaluated_at must be a non-empty string", errors)

    def test_record_command_writes_evidence_file(self):
        output_path = self.repo / "evals" / "agent-eval-attestation.json"

        MODULE.record_attestation(output_path, self.repo)

        written = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(written["cases"], ["case-one", "case-two"])
        self.assertEqual(MODULE.validate_attestation(written, self.repo), [])


if __name__ == "__main__":
    unittest.main()
