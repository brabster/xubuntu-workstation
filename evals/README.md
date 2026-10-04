# Knowledge base evaluations

`kb.json` is a small regression set of representative questions about the
repository knowledge base. Each case records the expected evidence pages and
short evidence excerpts that should support an answer.

Run the offline evidence checks with:

```sh
python3 -m unittest discover -s tests -p 'test_kb_evals.py'
```

The CI `ansible_lint` workflow runs these checks with the existing Python
helper tests whenever `docs/wiki/` or `evals/` changes. The checks ensure the
evaluation cases still point to real knowledge pages and their expected
evidence has not disappeared. They do not run a language model or measure
answer quality. To assess an agent, ask each case question with the knowledge
base available and compare its cited sources and answer against the recorded
evidence.

Add a case when an important repository question should remain answerable.
Keep each evidence excerpt short and specific to the expected source so the
test detects meaningful knowledge loss rather than incidental wording edits.
