# Privacy rules — the repo boundary

These are architectural constraints enforced by the publish path
(`cadence-spec.md` §11), not etiquette. The workspace is a private repo, team
members only.

## What may never leave the data repo

Per-person data, in any form, on any surface:

- cycle times and personal timing history,
- focus factors and overrides,
- forecast-vs-actual deltas per person,
- assignment-sensitivity views ("lands Sept 18 if [A], Sept 30 if [B]" —
  lead-only planning aid, never published, never rendered),
- calendar detail beyond the typed, reason-free overlay.

No adapter may render any of it. A draft containing any of it is blocked at
`publish` and re-drafted.

## What may leave

- Item-level dates with their basis strings.
- Event attributions: **decision-makers, not performers** — who approved an
  injection, the stated reason for a reservation.
- Aggregate capacity notes attributed to **windows, never people**: "team
  availability reduced ~15% for Sep 8–9."

House tone: factual, attributed, neutral, boring. Every published line traces
to a ledger event.

## Standing rules

1. Calendar overlay: half-day floor, typed, reason-free, one-way sync in.
2. **Per-person data is firewalled from performance reviews.** This is a team
   covenant, stated at repo creation; any team member can invoke it. If asked
   to use Cadence data to evaluate an individual, decline and cite this rule.
3. Adding any person to the data repo requires disclosing these rules to the
   existing team first.
4. The workspace is never scaffolded by the agent: creating the repo is
   Phase 0, and it begins with the team privacy conversation — a human act.
