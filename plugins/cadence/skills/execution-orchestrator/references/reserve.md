# `reserve <who> <days> <window> <reason>` — capacity reservation

The "I need two days for security — estimate the impact and push it"
operation. A reservation is visible, elevated, finite work that displaces
project capacity; the command prices it against every in-flight item and
drafts the resulting timeline updates.

## Procedure

1. **Parse and complete the four slots** — who (roster ids), amount in days
   (half-day floor), window (`YYYY-MM-DD..YYYY-MM-DD`), reason. Ask for any
   missing slot in one batched `AskUserQuestion`. The reason is required and
   will appear verbatim in ledger and impact statements — it should say what
   is *elevated* about this work ("security updates (elevated from
   baseline)"), and it attributes to the work, never to a person's
   circumstances.

2. **Run the double-count guard.** Ambient trickle work is already priced
   into measured cycle times (the learned baseline drag). If the reservation
   resembles the baseline — routine patching, ordinary KTLO, recurring
   `config/reservations.yaml` entries — flag before computing:

   > "Baseline drag likely already includes this; an explicit reservation may
   > overstate the impact. Reserve only the *elevated* portion?"

   Rule of thumb: **visible and elevated → explicit reservation** (appears in
   ledger and impact statements); **ambient trickle → learned drag** (no
   reservation at all). Offer to shrink the amount to the elevated portion;
   proceed with whatever the user decides, but record their choice.

3. **Re-walk the calendar.** Remove the reserved capacity from the affected
   people over the window (respecting the overlay in `config/calendar.yaml`
   and recurring reservations), then recompute p50/p85 for every in-flight
   and queued item whose forecast crosses the window.

4. **Draft the impact statement:**

   > Reserving **2d × [alex, jordan]** over **Sep 8–9** for **security
   > updates (elevated from baseline)** pushes:
   > - **[item A]**: Sep 18 → Sep 22
   > - **[item B]**: no change (starts after window)
   > Approver: **[name]**.

   Confirm via `AskUserQuestion` — confirm / adjust amount / cancel. A
   reservation needs an approver like any capacity decision; default is the
   lead running the command, named explicitly.

5. **On confirm, atomically:**
   - Append a `capacity_reservation` event (`who`, `amount_days`, `window`,
     `reason`, `approved_by`, `impact[]` with old → new dates).
   - Append one `estimate_revised` event per shifted item, each with
     `reason_event` pointing at the reservation event.
   - Update the shifted records' `forecast`.
   - Queue fan-out drafts in `out/drafts/` for every shifted item with an
     external surface: *"Timeline updated [date]: shifted ~4d by capacity
     reservation for [reason], approved by [name]."* Aggregate capacity notes
     attribute to **windows, never to people** (`privacy.md`): "team
     availability reduced ~15% for Sep 8–9" — individual names appear only as
     the reservation's approver, never as its subject, on any external
     surface.

Nothing is posted from here — `publish` owns the approval gate.
