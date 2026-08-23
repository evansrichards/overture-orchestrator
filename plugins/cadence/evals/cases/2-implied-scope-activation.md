# Eval 2 — Implied scope activation

**Command under test:** `/cadence commit` (environment-diff probe family).
Same request as eval 1; this case checks a different probe family, so it can
run as a continuation of eval 1's interview or standalone.

## Input

Same request:

> We need to enable online cancellation for Plan X members by Aug 24. PM
> pinged me on Slack — the VP of Product wants it live before the renewal
> window. Priya's going to take it.

Additional workspace/world state the case assumes (what the environment-diff
probes should dig out of the engineer):

- Cancellation currently exists only **behind an experiment flag** for a
  limited cohort (~2% of members, no regulated-state members in the cohort).
- Shipping this un-flagged is the **first un-flagged cancellation launch** —
  the experiment's cohort constraints exempted the team from state-specific
  cancellation rules (e.g. CA/NY requirements), full a11y review, and the
  analytics contract with the data team.
- Once un-flagged, **members in regulated states can reach the flow** for the
  first time. Whether the restrictive default flow satisfies CA/NY
  requirements without legal review is unverified — in the spec's worked
  example this is exactly assumption a3 and the open legal precondition
  (§5.1).

## Pass criteria (spec §14.2)

The environment-diff probes must elicit:

- That this is the **first un-flagged launch** and what the experiment's
  constraints exempted the team from.
- That **regulated-state users become reachable** once it ships → obligations
  attach.
- A **precondition record for a state-rule check** — typed, with an owner
  (e.g. `legal@`), a forecast date, `status: open` — attached to the
  commitment record, plus the corresponding assumption (restrictive flow OK
  for regulated states) in the assumptions list.

Bonus (probe-library accretion, §9.4): the pattern
`touches cancellation → state-rule check` is offered for
`probes/library.md`.

## Fail conditions

- **FAIL if the reachability question is never posed** — "who can reach this
  once it ships that can't today?" (or a faithful variant) must appear in the
  interview.
- Fail if the first-un-flagged-launch exemptions question is skipped.
- Fail if the legal check ends up as prose in the scope summary instead of a
  typed precondition with an owner.
