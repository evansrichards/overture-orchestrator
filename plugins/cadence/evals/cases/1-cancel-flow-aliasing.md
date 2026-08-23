# Eval 1 — Cancel-flow aliasing

**Command under test:** `/cadence commit` (Full-tier interview + scenario
modeling + confirmation artifact).

## Input

User (engineering lead) says:

> We need to enable online cancellation for Plan X members by Aug 24. PM
> pinged me on Slack — the VP of Product wants it live before the renewal
> window. Priya's going to take it. Can you set up the commitment?

Workspace state the case assumes:

- `config/team.yaml` roster contains `priya` (focus_factor 0.8).
- `history/cycle-times.jsonl` has ~12 size-M cross-team items with a median
  around 9 working days and a wide tail (supports a p85 near 2 weeks beyond
  p50).
- No prior scenario records for cancellation.
- The product spec (linked in the request thread) mentions: state-specific
  cancellation flows, retention offers at cancel time, and cancellation-reason
  analytics.

Realistic detail the interview should elicit if it probes well (the
"engineer's head" the fixture simulates):

- The smallest version meeting Aug 24 is a **restrictive default flow** — one
  generic path, no retention offers, partial analytics.
- The version the stakeholder likely pictures is the **full state-specific
  flow + retention offers + full analytics** — which forecasts around Oct 5
  at p85, missing the deadline by ~6 weeks.
- A middle option (restrictive flow + full analytics) forecasts ~Aug 31 —
  slips ~1wk.
- Deferred-scope sizes: retention offers ~3wk follow-on; full analytics ~1wk
  follow-on.
- Risks of the restrictive option: retention-offer revenue loss during the
  gap; blind spot on cancellation reasons until analytics lands.

## Pass criteria (spec §14.1)

The interview must surface, in its output:

- **(a)** Full vs. restrictive flow **options with forecasts** — a scenario
  record with at least the full/restrictive pair (an A/B/C set like §5.2 is
  the target shape), each option carrying scope, forecast_p85, and a verdict
  against Aug 24.
- **(b)** The **analytics deferral** — analytics appears explicitly as
  deferred (or partial) scope in the deadline-meeting option, and deferred
  items are queued as follow-on queue items linked to the scenario.
- **(c)** A **confirmation artifact naming the chosen option** — a drafted
  stakeholder message of the §9.5 shape: option name, date, scope including
  the outs, deferrals with sizes, "Reply to confirm."

## Fail conditions

- **FAIL if a commitment record is created with scope still ambiguous** —
  "online cancellation" never pinned to explicit ins/outs, or no scenario
  option named in the record.
- Fail if the confirmation draft omits the option name or the deferred items.
- Fail if the scenario is treated as closed without a named `chosen_by` and a
  linked stakeholder reply.
