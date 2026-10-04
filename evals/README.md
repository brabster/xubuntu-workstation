# Knowledge base evaluations

`kb.json` is a small behavioral regression set of representative questions
about the repository agent system. Each case records an expected answer,
evidence sources, and short evidence excerpts that should support the answer.

Run the offline evidence checks with:

```sh
python3 -m unittest discover -s tests -p 'test_kb_evals.py'
```

The CI `kb_evals` workflow runs corpus-integrity checks on pull requests and
merge-queue groups. On pull requests, it also validates the behavioral
attestation against the current agent-system inputs. Behavioral evaluation is
checked on each pull request before it enters the merge queue; the synthetic
combined merge-group tree is not separately attested.

The workflow checks that each case still points to a repository source
containing its expected evidence. It does not run an agent.

When an agent-system change is ready for behavioral evaluation, run every case
as a separate prompt in the current agent session. Compare each response with
its `expected_answer` and verify its claims against `expected_evidence`. After
all cases pass, write the evidence file:

```sh
python3 .github/scripts/agent_eval_attestation.py record \
  --evaluator "human:<id>" \
  --runtime "<agent/runtime and model>"
```

Commit `evals/agent-eval-attestation.json` with the system change. The file
records the case IDs, evaluator, runtime, time, result, and SHA-256 digest of
the agent-system inputs. CI recomputes the digest on every pull request; a
change to monitored inputs makes the evidence stale until the cases are run
again and the file is regenerated. The attestation file is excluded from its
own digest, so it can be generated and committed alongside the changes. No PR
comment, CI secrets, or model/API calls are needed.

This is an auditable human/agent attestation, not proof that the evaluation
actually ran or an automated judgment of answer quality. A required human
reviewer must verify the recorded evaluation before merge. Configure
`kb_evals / evals` as a required status check in repository rulesets/branch
protection. Its attestation step runs for each pull request before merge.

When running the behavioral cases, compare the agent's answer to
`expected_answer` and verify its claims against `expected_evidence`. The
automated integrity test checks that each evidence excerpt still exists in a
repository source, including agent instructions such as `AGENTS.md`.

Add a case when an important agent-system question should remain answerable.
Keep each evidence excerpt short and specific to the expected source so the
integrity check detects meaningful knowledge loss rather than incidental
wording edits.
