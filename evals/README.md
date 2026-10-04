# Knowledge base evaluations

`kb.json` is a small behavioral regression set of representative questions
about the repository knowledge base. Each case records expected evidence
pages and short evidence excerpts that should support an answer.

Run the offline evidence checks with:

```sh
python3 -m unittest discover -s tests -p 'test_kb_evals.py'
```

The CI `kb_evals` workflow runs two separate checks:

- `evals` checks that each case still points to a knowledge page
  containing its expected evidence. It does not run an agent.
- `agent_eval_attestation` requires a current behavioral evaluation record
  when an agent-system file changes. An agent or human must run every case as
  a separate prompt against the current agent system and verify the response
  against the cited source evidence.

For applicable pull requests, add exactly one block to the PR description:

```html
<!-- agent-eval-attestation
{
  "head_sha": "<full current PR head SHA>",
  "result": "pass",
  "cases": "all",
  "evaluator": "@reviewer",
  "runtime": "agent/runtime and model used"
}
-->
```

The workflow checks that the block is valid, says all cases passed, names the
evaluator and runtime, and matches the current PR head SHA. A new commit makes
the attestation stale; edit the PR description after rerunning the cases to
restore the check. The workflow uses only read-only pull-request metadata and
does not call a model or need model credentials. Its API token is exposed only
to the step that reads changed-file metadata, and checkout credentials are not
persisted.

This is an auditable human/agent attestation, not proof that the evaluation
actually ran or an automated judgment of answer quality. A required human
reviewer must verify the recorded evaluation before merge. Configure
`kb_evals / agent_eval_attestation` as a required status check in repository
rulesets/branch protection.

Add a case when an important repository question should remain answerable.
Keep each evidence excerpt short and specific to the expected source so the
integrity check detects meaningful knowledge loss rather than incidental
wording edits.
