# `delivered <item>` — close an item

Closes a queue item and banks its history. The cycle-time record written here
is the fuel for every later forecasting phase — never skip it.

## Procedure

1. Load the item's record; confirm it is `in_flight` (if not, say so and
   stop — a `started` event may be missing; offer to backfill it with the
   real date, from the user, before proceeding).
2. **Prompt for scope delta vs. the commitment:** "Did what shipped match
   what was committed?" — `none`, or a reference to the scenario record
   explaining the difference. If scope changed and no scenario documents it,
   draft the scenario delta now; do not record `scope_delta` as prose in the
   event.
3. Append a `delivered` event (`item`, `scope_delta`).
4. **Write the cycle-time record** to `history/cycle-times.jsonl`
   (`shared/record-schemas/cycle-time-record.v1.schema.json`): owner, size,
   work_type, dependency_profile, forecast_p50_days as forecast at start,
   actual_days, started/delivered timestamps, preempted_days summed from
   displacement events affecting this item while in flight.
5. Update the record: `status: delivered`. Report the forecast-vs-actual
   delta to the user in one line (team-internal only — per-person deltas
   never leave the repo).
6. If the item had an external surface, queue a closing fan-out draft in
   `out/drafts/` (factual, boring: delivered date, scope delta if any).
