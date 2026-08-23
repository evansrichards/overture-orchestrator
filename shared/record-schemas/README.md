# Record schemas — the Overture → Cadence handoff contract

The two orchestrators share a **file-format contract, not a code dependency**
(cadence-spec.md §3). This directory is that contract, as JSON Schema
(draft 2020-12), versioned.

**Overture emits a commitment record as its terminal artifact; Cadence
consumes and mutates it.** When a proposal is approved and crosses into
execution, its scope, estimates, assumptions, and stakeholders become a
Cadence queue item at t=0. From then on the record belongs to Cadence: status,
rank, forecast, and preconditions change only alongside ledger events.

## The schemas

| Schema | Validates | Lives in the data repo as |
| ------ | --------- | ------------------------- |
| `commitment-record.v1.schema.json` | YAML frontmatter of a queue item | `queue/<item-id>.md` |
| `scenario-record.v1.schema.json` | YAML frontmatter of a scenario (option modeling) | `scenarios/<id>.md` |
| `ledger-event.v1.schema.json` | one JSON line of the append-only ledger (all 7 event types) | `ledger/events.jsonl` |
| `cycle-time-record.v1.schema.json` | one JSON line of raw timing history | `history/cycle-times.jsonl` |

Two spec invariants are encoded structurally, not just documented: an
`injection` event **requires** `approved_by` (no cascade without a named
placement approver), and an `estimate_revised` event **requires**
`reason_event` (no orphan date changes — dates never slip, conditions change).

Notes for validators:

- The `.md` records are markdown with YAML frontmatter; parse the frontmatter
  to a JSON object first (dates as ISO strings, not native date objects).
- `format` assertions (`date`, `date-time`) are annotations by default in
  draft 2020-12 — enable format validation in your validator if you want them
  enforced.

## Versioning

Schemas are versioned in the filename (`*.v1.schema.json`). A **breaking
change is a new `v2` file**, never an edit to `v1` — the private data repos
validating against these outlive any single version. Additive, non-breaking
clarifications may amend `v1` (they cannot invalidate a previously-valid
record, since v1 records must keep validating).

## Status of the handoff (TODO)

Overture does **not** yet emit this format. Its `handoff` subcommand currently
exports readable markdown and deliberately deferred schema alignment "until a
real proposal crosses the boundary"
(`plugins/overture/skills/planning-orchestrator/references/publishing.md` →
"`handoff` export (approved proposals)"). This contract is that boundary.

**TODO:** when the first real proposal crosses into Cadence, extend Overture's
`handoff` procedure —
`plugins/overture/skills/planning-orchestrator/references/commands.md` →
"`handoff`" — to also emit a `commitment-record` frontmatter stub (id, title,
owner, assumptions carried over from validated/open assumption records;
`status: queued`; size/work_type/dependency_profile left to the intake
interview) alongside its markdown handoff packet. Until then, `/cadence
intake` creates commitment records from the handoff packet by interview.
