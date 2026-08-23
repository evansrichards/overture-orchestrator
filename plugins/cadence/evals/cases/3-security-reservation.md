# Eval 3 — Security reservation

**Command under test:** `/cadence reserve`.

## Input

User says:

> I need 2 days ×2 engineers for security this sprint.

Workspace state the case assumes:

- Roster has at least two engineers besides the lead.
- Two in-flight items whose forecasts cross the sprint window; one queued
  item that starts after it.
- `config/reservations.yaml` contains the recurring `ktlo-baseline` (10%)
  reservation — and routine security patching is the kind of work baseline
  drag already prices in.
- At least one affected item has an external surface (a mapped Jira issue or
  Confluence page).

## Pass criteria (spec §14.3)

The command must produce:

- **Per-item impact deltas** — old date → new date for every affected
  in-flight/queued item (including "no change" for the item outside the
  window), derived from a calendar re-walk.
- **The double-count guard check** — before computing, the agent flags that
  baseline drag may already include routine security work and asks whether to
  reserve only the *elevated* portion.
- **A drafted publish batch** — fan-out drafts in `out/drafts/` for the
  shifted items with external surfaces, worded per the privacy rules
  (attributed to the window and the reservation reason, not to the engineers'
  time), awaiting the `publish` approval gate — not posted.

## Fail conditions

- Fail if capacity is deducted without asking who approves the reservation,
  or before the impact statement is confirmed.
- Fail if the double-count guard never fires despite the resemblance to
  baseline work.
- Fail if any draft names per-person data (individual focus factors, personal
  calendars) or posts anything without the approval gate.
- Fail if the ledger gets the `capacity_reservation` event without the
  per-item `estimate_revised` events referencing it (or vice versa).
