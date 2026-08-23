# `intake` — new work arrives

New work enters the queue here: routine items, handoffs from Overture, and —
the case this command exists for — **injections** claiming a top rank. Intake
decides the interview tier, runs it, computes displacement, and drafts the
impact statement. It never silently absorbs work into the queue.

## Procedure

1. **Classify the tier** (`probes.md` → Trigger tiers). Ask one question if
   unclear: *"Is anyone outside the team relying on a date for this?"*
   - **None** (sub-day): append the item to the queue at the tail with a
     one-line record, append a ledger note if rank matters, done. No
     interview.
   - **Lite**: exactly three questions — scope ins/outs, dependency profile,
     top assumption — then write the record.
   - **Full**: continue below; if it is a stakeholder-visible commitment with
     scope-vs-deadline tension, run the whole of `commit.md` instead (intake
     hands off to it).

2. **Assemble context** (`probes.md` → Context assembly): request thread,
   spec, prior scenarios, cycle-time profile, probe library.

3. **Run the interview** (`probes.md` → Probe families): generic family
   always; environment-diff family whenever the work changes who or what can
   reach production; context-aware probes for everything assembled in step 2.

   **Refusals that hold regardless of urgency:**
   - Do not write a commitment record while any scope term in the request is
     still undefined ("cancellation", "supported", "launched" — pin each one
     to explicit ins/outs).
   - Do not record an estimate revision without a causal ledger event.

4. **Draft the record.** Commitment record per
   `shared/record-schemas/commitment-record.v1.schema.json`: frontmatter plus
   a prose body with the scope summary (explicit ins AND outs) and links.
   Unblock answers become typed `preconditions` with owners and forecasts.

5. **Forecast.** Seeded basis in Phase 2: walk the actual calendar (roster ×
   focus factors × overlay × reservations) against the seeded per-(size,
   dependency_profile) duration guesses. Label `basis: seeded`. Report p50
   and p85.

## Injections (rank-claiming work)

An injection is any intake that wants a rank above queued or in-flight work.

1. **Name the approver first.** Ask: *"Who is approving this placement at
   rank N?"*

   > **REFUSE to proceed without a named placement approver.** A person's
   > name — not "product", not "leadership", not a standing priority policy.
   > No approver, no cascade: the item can be *recorded* at the tail as
   > ordinary intake, but nothing is displaced and no dates move. Say exactly
   > that.

2. **Compute displacement.** Queue-shift arithmetic plus a calendar re-walk
   for every item at or below the insertion rank: new p50/p85 per item, shift
   in days.

3. **Draft the impact statement** before anything is written:

   > Accepting **[item]** at **P1** pushes **A** ~2wks (Sept 18 → Oct 2) and
   > **B** ~1wk (Oct 9 → Oct 16). Approver: **[name]**.

   Present it to the user (the lead) for confirmation via `AskUserQuestion` —
   confirm / adjust rank / record-at-tail-instead.

4. **On confirm, atomically:**
   - Append an `injection` event (`approved_by`, `displaced[]` with shifts).
   - Append one `estimate_revised` event per displaced item, each with
     `reason_event` pointing at the injection event.
   - Update the displaced records' `rank` and `forecast`.
   - Write the new item's record.
   - Queue fan-out drafts in `out/drafts/` — one per displaced item with an
     external surface, in the ledger-traceable house style
     (`privacy.md` → What may leave): *"Timeline updated [date]: shifted
     ~2wks by [item] (prioritized by [name])."* Nothing is posted; `publish`
     owns approval.

## Handoffs from Overture

An approved Overture proposal arrives as a handoff packet (markdown today; a
commitment-record stub once the emission TODO in
`shared/record-schemas/README.md` lands). Treat it as pre-assembled context —
scope, assumptions, and stakeholders come loaded — then run the tier decision
normally. A handoff with an external deadline is Full tier: Overture aligned
the proposal; intake still de-aliases the *commitment*.
