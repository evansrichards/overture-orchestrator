# `commit <item>` — the full commitment interview

For stakeholder-visible commitments: someone outside the team will rely on a
date. This is the de-aliasing machine — its product is not a record but
**armor**: named options, a defensible forecast, and a confirmation message
the stakeholder must answer. Run it only at Full tier (`probes.md` → Trigger
tiers).

## Procedure

1. **Assemble context** (`probes.md` → Context assembly). Do not start the
   interview cold.

2. **Interview** (`probes.md` → Probe families) — all three families:
   - Generic: pin every scope term to explicit ins/outs; smallest-version vs.
     pictured-version gap; assumptions; 2×-risk; definition of done;
     unblock/precondition probes.
   - Environment-diff: reachability, first-un-flagged-launch exemptions,
     prototype-vs-production shape.
   - Context-aware: spec-diff, history, and — always, before finishing — the
     **aliasing check**: which named option does the "yes" refer to?

   **Refusal:** no commitment record is written while any scope term remains
   undefined. If the engineer can't pin a term, that term becomes a
   precondition or an explicit OUT — never an ambiguity in the record.

3. **Model scenarios** when scope is negotiated against a deadline (it almost
   always is at this tier). Write a scenario record
   (`shared/record-schemas/scenario-record.v1.schema.json`):
   - **At least two real options** — typically: the full version the
     stakeholder pictures (A), the smallest version meeting the date (B), and
     a middle option (C). For each: scope in one sentence, forecast_p85 from
     a calendar walk, verdict against the deadline in plain words.
   - Every **deferred** scope item in an option becomes a first-class queue
     item linked back to the scenario — deferrals are queued work, not
     footnotes, and they can themselves be displaced later.
   - Name the **risks** the cheaper options carry (revenue gap, blind spots).

4. **Present the options** to the user, get the recommendation they'll take
   to the stakeholder. The *stakeholder*, not the engineer, is `chosen_by` —
   the record stays open until a named human chooses.

5. **Draft the confirmation artifact** (this step is mandatory — it is the
   de-aliasing mechanism):

   > "Committing to **Option B** by **Aug 24**: restrictive default flow, no
   > retention offers, partial analytics. Retention offers (~3wk) and full
   > analytics (~1wk) are deferred and queued as follow-ons. Reply to
   > confirm."

   House rules: names the chosen **option**, the **date**, the scope **in one
   breath including the outs**, and each deferral with its follow-on size. No
   editorializing. The draft goes in `out/drafts/` — the human sends it
   (nothing is auto-sent), and the interview extracts specificity from the
   engineer so the confirmation can extract agreement from the stakeholder.

6. **Write the records and events:**
   - Commitment record: scenario link, assumptions, preconditions, forecast
     with basis string.
   - Scenario record: options; `chosen`/`chosen_by`/`chosen_on`/`confirmation`
     stay unset until the stakeholder's reply exists.
   - Ledger: append the appropriate events (`started` when work begins;
     precondition edges per `intake.md`).

7. **Close the loop later.** When the stakeholder replies, set `chosen_by`,
   `chosen_on`, and `confirmation` (link to the reply). A scenario is **not
   closed** — and the commitment is not `confirmed` — until `chosen_by` is a
   named human and `confirmation` links their explicit reply.

## Tone

The interview gives, not just takes. Surface what the engineer gets out of
each answer as you go: "that gap is now named in the options, so it can't
surface as a broken promise later"; "this basis string is what makes the date
defensible in the room." If answers turn pro-forma, stop and shorten.
