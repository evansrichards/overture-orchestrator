# `sync` — pull external state (STUB)

> **Phase 3 stub** (`cadence-spec.md` §13, §10). No adapters are built.
> Until then: say it's stubbed; the manual equivalent is the user pasting
> current Jira ranks/statuses, which you then diff against the queue records
> following the rules below.

## What is specified now

- **Direction: in only.** `sync` pulls Jira rank/status and (optionally) the
  team calendar feed. It never pushes — outbound is `publish`'s job, behind
  its approval gate. Calendar sync is one-way in, never out (spec §11).
- **Core wins on conflict; drift is surfaced, not silently merged.** The
  output is a drift report: "Jira has [item] at rank 2; the queue has it at
  rank 4", "Jira says In Progress; no `started` event exists." For each line,
  offer the two honest resolutions — record a ledger event that explains the
  external state (an injection someone made in Jira is still an injection,
  and still needs a named approver), or queue a corrective draft for
  `publish` so the projection matches the ledger again.
- Never rewrite a queue record to match an external tool without the ledger
  event that explains the change (non-negotiable #2).

## TODO (Phase 3)

- Jira adapter: read rank/status for mapped issues (`config/adapters.yaml`).
- Calendar adapter: one-way absence import at half-day granularity, typed,
  reason-free.
- Drift report rendering + resolution flow as above.
