# Workspace layout and record formats

The workspace is a **separate private data repo** (team members only —
`privacy.md`). This plugin documents and validates the layout; it never
contains or creates it. Users scaffold it by copying the plugin's
`workspace-template/`.

## Locating it

Walk up from cwd looking for `cadence/config/team.yaml` at each level; if the
data repo uses its root as the workspace, `config/team.yaml` +
`ledger/` together mark it. Parent walk only — never search the filesystem.
Not found → point at `workspace-template/` and stop.

## Layout (spec §4)

```
config/
  team.yaml            # roster: id, focus_factor (only)
  calendar.yaml        # absence/oncall overlay — half-day floor, typed, reason-free
  adapters.yaml        # jira project, confluence space, page mappings
  reservations.yaml    # recurring capacity reservations
queue/<item-id>.md     # commitment records — YAML frontmatter + prose body
scenarios/<id>.md      # scenario records — option modeling
ledger/events.jsonl    # append-only event log — THE authoritative record
history/cycle-times.jsonl  # raw per-item timing (feeds forecaster)
probes/library.md      # accreted probe patterns (probes.md → Probe library accretion)
out/drafts/            # pending publish drafts awaiting approval
```

## Record formats

All formats are versioned JSON Schemas in the plugin monorepo's
`shared/record-schemas/` (v1) — commitment record, scenario record, ledger
event, cycle-time record. Validate frontmatter/lines against them before
writing; a record the schema rejects is a bug in the write, not in the
schema.

Ledger discipline:

- **Append-only.** Never edit or delete a line. A wrong event is corrected by
  a subsequent event, not by rewriting history.
- One JSON object per line; `ts` in ISO 8601. The `ts` (plus index when
  needed) is how `estimate_revised.reason_event` references its cause.
- Write the event **before** reporting the state change as done
  (non-negotiable #8).

## Config semantics (spec §6)

- `team.yaml`: id + focus_factor only. Refuse to add skill ratings or
  velocity fields — measured history covers it.
- `calendar.yaml`: half-day minimum unit; types `pto | partial | oncall`;
  **no reasons, ever**. One-way sync in, never out.
- `reservations.yaml`: recurring only; one-offs go through `reserve` into the
  ledger.
