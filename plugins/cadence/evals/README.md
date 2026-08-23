# Cadence evals

The five regression scenarios from `cadence-spec.md` §14, kept as fixtures
the interview prompts are **written against**. There is no runner yet — the
Overture trigger-eval harness tests triggering, not behavior, and these test
behavior: does the interview surface what it must, and does the agent refuse
what it must refuse.

Each case file has:

- **Input** — the request as a user would actually state it, plus the
  workspace state the scenario assumes.
- **Pass criteria** — what the interview/agent must produce, as written in
  spec §14.
- **Fail conditions** — the specific defect the case exists to catch.

The two cancel-flow cases (1–2) carry full realistic detail from the spec's
worked example (§5.1–5.2) because they exercise the highest-value prompts:
scope de-aliasing and implied scope activation.

When a prompt in `../skills/execution-orchestrator/references/` changes, walk
each case against the new prompt by hand (or with a headless session) and
check every pass criterion. A criterion you can't check from the transcript
is a prompt bug — the prompts must force their evidence into the open.

| # | Case | Refusal / mechanism under test |
|---|---|---|
| 1 | `cases/1-cancel-flow-aliasing.md` | scope de-aliasing; no record with ambiguous scope |
| 2 | `cases/2-implied-scope-activation.md` | environment-diff probes; reachability → precondition |
| 3 | `cases/3-security-reservation.md` | impact deltas; double-count guard; publish batch |
| 4 | `cases/4-orphan-date-change.md` | refuse `estimate_revised` without causal event |
| 5 | `cases/5-injection-without-approver.md` | refuse cascade without named approver |
