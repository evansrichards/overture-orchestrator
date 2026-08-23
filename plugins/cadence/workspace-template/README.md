# Cadence workspace template

Copy this folder's contents into your team's **separate private data repo**
(as a `cadence/` directory, or as the repo root). It never lives in the plugin
repo, and nothing in it should ever be public: the queue, ledger, history, and
config it will accumulate are team-internal by design.

Before adding anyone to that repo, read the privacy rules
(`cadence-spec.md` §11 in the plugin repo) and state the covenant to the
existing team — per-person data (cycle times, focus factors, forecast deltas)
never leaves the repo and is firewalled from performance reviews.

```
config/           # roster, calendar overlay, adapters, recurring reservations
queue/            # commitment records — one <item-id>.md per queue item
scenarios/        # scenario records — option modeling for scoped commitments
ledger/           # events.jsonl — append-only, THE authoritative record
history/          # cycle-times.jsonl — raw per-item timing, feeds the forecaster
probes/           # library.md — your team's accreted interview probes
out/drafts/       # pending publish drafts awaiting approval
```

First steps (Phase 0): fill in `config/team.yaml` with honest focus-factor
guesses, pick the authoritative external queue, and start appending ledger
events **manually today** — history cannot be backfilled.

The `.gitkeep` files exist only so git keeps the empty directories; delete
each one once its directory has real content.
