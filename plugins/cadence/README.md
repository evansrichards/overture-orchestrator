# Cadence

**An execution orchestrator** — the sibling of [Overture](../overture/README.md).
Overture plans and publishes proposals in bursts; Cadence runs continuously,
tracking commitments, capacity, injections, and displacement once work is in
flight.

> **Status: scaffold.** This plugin currently ships Phase 0–1 support and the
> Phase 2 command skeletons (spec §13): full interview prompts for `intake`,
> `commit`, and `reserve`; simple `status` and `delivered`; stubs for
> `publish`, `review`, `sync`. Spec: [`cadence-spec.md`](../../cadence-spec.md).

## Purpose

Cadence exists to solve four recurring problems (spec §1):

1. **Silent displacement** — new top-priority work gets injected, in-flight
   timelines slip, nobody communicates the delay, and the team later looks slow.
2. **Commitment aliasing** — an engineer's "yes" means the minimal
   interpretation; the stakeholder hears the full-featured one; the gap
   surfaces months later as a broken promise.
3. **Implied scope activation** — a small request silently activates large
   obligations (first un-flagged launch → regulated-state rules attach).
4. **Estimate indefensibility** — points measure complexity, but delivery time
   is dominated by coordination cost; estimates can't be defended because they
   aren't grounded in measured history.

Its answer: an **append-only ledger** as the source of truth, **forecasts from
measured cycle times**, a **structured interview** that de-aliases every
externally-visible commitment, and **human-approved fan-out** of timeline
updates to Jira/Confluence. Dates never "slip" — conditions change, and every
date change references the ledger event that caused it.

## The workspace lives elsewhere

**This plugin contains no workspace and never will.** All execution data lives
in a **separate private team repo** — team members only, governed by the
privacy rules below. This plugin documents the expected layout, validates
against it, and operates on it; copy
[`workspace-template/`](workspace-template/) into that repo to start.

Expected layout of the data repo (spec §4):

```
cadence/
  config/
    team.yaml            # roster: id, focus_factor (only)
    calendar.yaml        # absence/oncall overlay, half-day granularity
    adapters.yaml        # external tool config (jira project, confluence space, page mappings)
    reservations.yaml    # recurring capacity reservations
  queue/
    <item-id>.md         # commitment records (YAML frontmatter + prose)
  scenarios/
    <scenario-id>.md     # scenario records (option modeling for scoped commitments)
  ledger/
    events.jsonl         # append-only event log — THE authoritative record
  history/
    cycle-times.jsonl    # per-item raw timing history (feeds forecaster)
  probes/
    library.md           # team-local accreted probe patterns
  out/
    drafts/              # pending publish drafts awaiting approval
```

Record formats are validated against
[`shared/record-schemas/`](../../shared/record-schemas/README.md) — also the
handoff contract through which an approved Overture proposal becomes a
commitment record at t=0.

## Privacy rules the plugin enforces

These are constraints the publish path enforces structurally (spec §11), not
etiquette:

1. **Per-person data never leaves the data repo.** Cycle times, focus factors,
   forecast deltas, assignment-sensitivity views — no adapter may render any
   of it, ever.
2. **External surfaces receive only:** item-level dates, basis strings, event
   attributions (injection approvers, reservation reasons), and aggregate
   capacity notes ("team availability reduced ~15% for window") — attributed
   to windows, never to people.
3. **Calendar overlay is typed and reason-free** — half-day floor,
   `type: partial` not "doctor's appointment", one-way sync in, never out.
4. **Ledger attribution names decision-makers** (who approved an injection),
   not performers.
5. **Per-person data is firewalled from performance reviews.** A team
   covenant, stated at repo creation; any team member can invoke it.
6. **Adding any person to the data repo requires disclosing these rules to the
   existing team first.**

## Commands

| Command | State |
| ------- | ----- |
| `/cadence intake` | **Full prompt.** Tiered interview for new work; injections refuse to cascade without a named placement approver; displacement math + impact statement. |
| `/cadence commit <item>` | **Full prompt.** Full interview + scenario modeling + drafted stakeholder confirmation. |
| `/cadence reserve <who> <days> <window> <reason>` | **Full prompt.** Capacity reservation: calendar re-walk, per-item impact, double-count guard. |
| `/cadence status` | Simple: read workspace, render queue + forecasts + open preconditions + pending drafts. |
| `/cadence delivered <item>` | Simple: close item, append events, write cycle-time record, prompt for scope delta. |
| `/cadence publish` | **Stub** — approval-gate structure and the privacy firewall are already specified. |
| `/cadence review` | **Stub** — adaptation loop (spec §8). |
| `/cadence sync` | **Stub** — adapter pull, drift surfaced not merged (spec §10). |
| `/cadence tour` | Onboarding: the concept walk, plus a guided Phase 0 walkthrough when no workspace exists yet. |

## Install

```bash
/plugin marketplace add evansrichards/overture-orchestrator
/plugin install cadence-orchestrator@overture
```

## Getting started (Phase 0 — outside this repo)

Run **`/cadence tour`** for a guided version of the steps below — it walks
the concepts in usage order and checklists Phase 0 with you (it validates
your copied workspace, but never creates it: step 2 stays a human act).

1. Create the private team data repo; copy `workspace-template/` into it.
2. Have the team privacy conversation and state the §11 covenant at repo
   creation.
3. Pick the authoritative external queue (Jira) and keep its rank real.
4. Start appending ledger events manually today — history is the fuel for
   everything later and cannot be backfilled.

## License

MIT — see [LICENSE](../../LICENSE).
