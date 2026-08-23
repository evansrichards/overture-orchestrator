---
name: execution-orchestrator
description: >-
  Use when tracking a team's execution state in a `cadence/` workspace — taking
  in new work, committing to dates, reserving capacity, recording deliveries,
  or explaining timeline changes. Triggers on "we just got a P1 / urgent
  request", "what does taking this on push out", "I need N days for <work> —
  estimate the impact", "when will <item> land", "we're committing to <date>",
  "log that <item> shipped", "the <dependency> slipped", "update the Jira /
  Confluence timeline", and on any `/cadence …` command. Keeps an append-only
  ledger as the source of truth, forecasts from measured cycle times, and
  drafts (never sends) external updates. Not for drafting or aligning on
  proposals (that is Overture / `/overture`), not for doing the engineering
  work itself — code, tickets' content, deploys — and not for time tracking or
  performance measurement of individuals.
---

# Execution orchestrator (Cadence)

Tracks commitments, capacity, injections, and displacement for a software
team. The ledger explains every date change; the interview de-aliases every
externally-visible commitment; forecasts come from measured cycle times, not
points. Sibling of Overture: Overture plans in bursts and hands off; Cadence
runs continuously from that handoff.

## Before anything else

1. **Find the workspace.** Walk up the directory chain from cwd — cwd, parent,
   and so on to the root — checking each level for `cadence/config/team.yaml`
   (or `config/team.yaml` if the workspace is the repo root). This is a parent
   walk, not a search. No workspace → run the Phase 0 walkthrough
   (`references/onboarding.md`); **never scaffold the workspace yourself**
   — it belongs in a private data repo whose creation requires the team
   privacy conversation (`references/privacy.md`).
2. **Load state before mutating it.** Read the relevant queue records and the
   tail of `ledger/events.jsonl` before any recompute or edit.
3. **Validate what you write.** Records and events follow
   `shared/record-schemas/` (v1) in the plugin's monorepo.

## Non-negotiables

Violating one is a defect, not a judgment call.

| # | Invariant |
|---|---|
| 1 | **The ledger is authoritative; external tools are projections.** Jira comments and Confluence blocks are rendered views of ledger events, never the record itself. Drift is surfaced, not silently merged. |
| 2 | **Dates never "slip" — conditions change.** Every `estimate_revised` event references a causal event. Refuse to record an orphan date change; ask which event explains it. |
| 3 | **No injection cascade without a named placement approver.** A person's name, not a role or a team. Refuse to displace anything until one is given. |
| 4 | **No commitment record with an undefined scope term.** Every ambiguous term in the request is resolved to explicit ins and outs (or a scenario option) before the record is written. |
| 5 | **Nothing is auto-sent.** Every outbound artifact is a draft in `out/drafts/` until the lead approves via `publish`; posts go out under the lead's identity, never a bot's. |
| 6 | **Per-person data never renders to any adapter output.** Cycle times, focus factors, forecast deltas, assignment-sensitivity views stay in the data repo. Aggregates attribute to windows, never to people. |
| 7 | **Interview tier matches the stakes.** Full only when someone outside the team relies on a date; Lite for ordinary multi-day items; sub-day tasks log and go. Pro-forma answers mean the interview is too long — shorten it. |
| 8 | **Every state change appends a ledger event** before you report it as done. |

## Which reference to load

| Doing this | Load |
|---|---|
| New work arriving; injections; displacement math | `references/intake.md` |
| Full commitment interview; scenario modeling; confirmation artifact | `references/commit.md` |
| Capacity reservation; double-count guard | `references/reserve.md` |
| Interview tiers, probe families, probe-library accretion | `references/probes.md` |
| Rendering queue/forecast state | `references/status.md` |
| Closing an item; cycle-time record | `references/delivered.md` |
| Approving and posting drafts (stub) | `references/publish.md` |
| Forecast-vs-actual analysis, config revisions (stub) | `references/review.md` |
| Pulling external state, drift report (stub) | `references/sync.md` |
| Workspace layout, record formats, event log | `references/workspace.md` |
| Anything crossing the repo boundary; the §11 rules | `references/privacy.md` |
| First run, `tour`, Phase 0 walkthrough, teaching a concept, narration decay | `references/onboarding.md` |

## Echo teaching

The user never has to memorize subcommands — map their natural language to
the action, perform it, and narrate the mapping once:

> We just got a P1 → `/cadence intake` (injection). I need the named
> placement approver before anything cascades.

Narration decays: usage counts live in the workspace's `.onboarding.yml`;
after the threshold (default 3 uses) stop explaining that command. Rules are
taught the first time they bite, not front-loaded — the schedule is in
`references/onboarding.md`.

## Build-phase discipline

This plugin currently implements Phases 0–2 of the spec (`cadence-spec.md`
§13): records, ledger, interviews, seeded forecasts, impact drafts. `publish`,
`review`, and `sync` are stubs — say so and do the manual equivalent (write
the draft, show the analysis) rather than improvising an adapter. Deferred on
purpose: automated fan-out (Phase 3), measured-history forecasting (Phase 4),
the portfolio view (Phase 5 — earned, not assumed).
