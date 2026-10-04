import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI_ROOT = (REPO_ROOT / "docs" / "wiki").resolve()
EVALS_PATH = REPO_ROOT / "evals" / "kb.json"


class KnowledgeBaseEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(EVALS_PATH.read_text(encoding="utf-8"))["cases"]

    def test_cases_have_unique_ids_and_expected_evidence(self):
        case_ids = [case.get("id") for case in self.cases]

        self.assertTrue(self.cases)
        self.assertEqual(len(case_ids), len(set(case_ids)))

        for case in self.cases:
            with self.subTest(case=case.get("id")):
                self.assertTrue(case.get("question"))
                self.assertTrue(case.get("expected_evidence"))

    def test_expected_evidence_exists_in_knowledge_base(self):
        for case in self.cases:
            for evidence in case.get("expected_evidence", []):
                source = (REPO_ROOT / evidence["source"]).resolve()
                with self.subTest(case=case.get("id"), source=evidence["source"]):
                    self.assertTrue(
                        source.is_relative_to(WIKI_ROOT),
                        "evaluation sources must stay inside docs/wiki",
                    )
                    self.assertTrue(source.is_file(), "evaluation source does not exist")
                    content = source.read_text(encoding="utf-8").casefold()
                    self.assertIn(evidence["text"].casefold(), content)


if __name__ == "__main__":
    unittest.main()
