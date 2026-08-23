# `status` — render current execution state

Read-only. Reads the workspace, renders, changes nothing (no ledger event —
nothing changed).

## Procedure

1. Read all of `queue/*.md`, open scenario records they link, the tail of
   `ledger/events.jsonl`, and the listing of `out/drafts/`.
2. Render, in this order:
   - **Queue** by rank: id, title, status, owner, size/dependency_profile,
     p50/p85 **with basis string** (a forecast without its basis is not
     shown), external deadline + authority where present.
   - **Open preconditions** across all items: text, owner, forecast date —
     flag any past forecast (these are shifting their dependent items; if the
     causal event hasn't been written yet, say so and offer to write it).
   - **Unconfirmed scenarios**: any commitment whose scenario lacks
     `chosen_by`/`confirmation` — the promise is not yet closed.
   - **Pending drafts** in `out/drafts/` awaiting `publish`.
3. Keep the rendering factual and compact — this is the team-internal view,
   so per-person data (focus factors, personal history) may inform it, but
   prefer item-level facts; the habit protects the publish path.
