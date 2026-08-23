# Cadence — Execution Orchestrator Spec

> Working name: **Cadence** (placeholder — rename freely). Sibling to **Overture** (planning orchestrator). Overture plans and publishes proposals; Cadence tracks execution: commitments, capacity, injections, displacement, and the ledger that explains every date change.

## 1. Purpose

Cadence is a Claude Code–driven orchestrator for a software team's execution state. It exists to solve four recurring problems:

1. **Silent displacement.** New top-priority work gets injected; in-flight timelines slip; nobody updates or communicates the delay, and the team later looks slow.
2. **Commitment aliasing.** An engineer says "yes" meaning the minimal interpretation; a stakeholder hears "yes" meaning the full-featured one. The gap surfaces months later as a broken promise.
3. **Implied scope activation.** A small request silently activates large obligations (e.g., "enable cancellation for plan X" → first un-flagged launch → regulated-state rules attach). Neither party knew they were asking for / committing to it.
4. **Estimate indefensibility.** Story points measure technical complexity, but delivery time is dominated by coordination cost. Estimates can't be defended because they aren't grounded in measured history.

Cadence's answer: an **append-only ledger** as the source of truth, **forecasts from measured cycle times** instead of points, a **structured interview** that de-aliases every externally-visible commitment, and **human-approved fan-out** of timeline updates to external surfaces (Jira, Confluence).

## 2. Design principles

- **Core is tool-agnostic; adapters translate.** The domain core (records, ledger, forecaster, interview) knows nothing about Jira/Confluence. Adapters `sync-in` external state and `publish-out` rendered views. Portability between companies is a requirement; the core must survive any org's tool choices.
- **The ledger is authoritative; external tools are projections.** Jira comments and Confluence timeline blocks are *rendered views* of ledger events, never the record itself.
- **Dates never "slip" — conditions change.** Every timeline change must reference a ledger event: an injection, a capacity reservation, or a broken assumption. No orphan date changes.
- **Human-in-the-loop on all publishes.** Cadence drafts; the lead approves; posts go out under the lead's identity, not a bot's.
- **Record raw, model later.** Log fine-grained raw data (per-item timing, tags); keep models coarse. Any future model can be built from raw history retroactively; the reverse is impossible.
- **Boring output is credible output.** Published updates are factual, attributed, neutral. "Timeline updated [date]: shifted ~2wks by [item] (prioritized by [name])." No editorializing.
- **Privacy is architectural.** Two-tier visibility (team-internal vs. external) is enforced by the publish pipeline, not by discipline. Per-person data never leaves the repo.

## 3. Relationship to Overture

- Overture's terminal artifact (a published proposal: scope, estimates, assumptions, stakeholders) becomes Cadence's **commitment record** at t=0. Define the handoff as a file-format contract, not a code dependency.
- Cadence reuses Overture's Confluence publish pipeline conventions (lift, don't rewrite).
- They remain separate tools: Overture runs in bursts (draft → align → publish, done); Cadence runs continuously (events → recompute → fan out). Do not merge. Extract a shared core only if/when duplication actually hurts.

## 4. Workspace structure

```
cadence/
  config/
    team.yaml            # roster: id, focus_factor (only)
    calendar.yaml        # absence/oncall overlay, half-day granularity
    adapters.yaml        # external tool config (jira project, confluence space, page mappings)
    reservations.yaml    # recurring capacity reservations
  queue/
    <item-id>.md         # commitment records (YAML frontmatter + prose)
  scenarios/
    <scenario-id>.md     # scenario records (option modeling for scoped commitments)
  ledger/
    events.jsonl         # append-only event log — THE authoritative record
  history/
    cycle-times.jsonl    # per-item raw timing history (feeds forecaster)
  probes/
    library.md           # team-local accreted probe patterns (see §9.4)
  out/
    drafts/              # pending publish drafts awaiting approval
```

**Access:** private repo, team members only. See §11 (privacy rules) before adding anyone.

## 5. Record types

### 5.1 Commitment record (`queue/<item-id>.md`)

```yaml
id: cancel-flow-plan-x
title: Online cancellation for Plan X members
status: in_flight            # queued | in_flight | delivered | deferred
rank: 3                      # position in the authoritative queue
size: M                      # S | M | L — coarse, deliberately
work_type: build             # build | design | coordinate
dependency_profile: cross-team   # self-contained | needs-review | cross-team | needs-legal
owner: priya
external_deadline: 2026-08-24    # only if a real external date exists
deadline_authority: "VP Product, via PM (Slack 7/28)"
scenario: scenarios/cancel-flow-aug24.md   # link if commitment is scoped (§5.2)
assumptions:
  - id: a1
    text: "No preemption of Priya before Aug 21"
  - id: a2
    text: "API team delivers cancel endpoint by Aug 10"
  - id: a3
    text: "Restrictive default flow satisfies CA/NY requirements without legal review"
preconditions:                 # typed blockers with owners (§9.3)
  - text: "Legal confirms restrictive flow OK for regulated states"
    owner: legal@
    forecast: 2026-08-05
    status: open
forecast:
  p50: 2026-08-14
  p85: 2026-08-21
  basis: "team median, size M, cross-team profile (n=12)"
```

Prose body: scope summary (explicit ins AND outs), links to spec/thread.

### 5.2 Scenario record (`scenarios/<id>.md`)

For any commitment where scope was negotiated against a deadline. The record that kills "wait, I thought we were getting the full version."

```yaml
id: cancel-flow-aug24
target: Online cancellation for Plan X members
deadline: 2026-08-24 (external, hard)
options:
  A:
    scope: Full state-specific flow + retention offers + full analytics
    forecast_p85: 2026-10-05
    verdict: misses deadline
  B:
    scope: Restrictive default flow; no retention offers; partial analytics
    forecast_p85: 2026-08-21
    verdict: meets deadline
    deferred:
      - retention offers (~3wk follow-on)     # becomes a queue item
      - full analytics (~1wk follow-on)       # becomes a queue item
    risks:
      - retention-offer revenue loss during gap
      - blind spot on cancellation reasons until analytics lands
  C:
    scope: B + full analytics
    forecast_p85: 2026-08-31
    verdict: slips ~1wk
chosen: B
chosen_by: "[stakeholder name]"
chosen_on: 2026-07-30
confirmation: "link to confirmation message + stakeholder reply"
```

**Rules:** `deferred` scope items become first-class queue items linked back to the scenario (they can themselves be displaced later, generating their own ledger history — the system composes). A scenario is not closed until `chosen_by` is a named human and `confirmation` links their explicit reply.

### 5.3 Ledger events (`ledger/events.jsonl`)

Append-only. One JSON object per line. Event types:

```jsonc
{"type":"injection","ts":"...","item":"...","rank_inserted":1,
 "approved_by":"NAME","displaced":[{"item":"...","shift_days":10}]}

{"type":"capacity_reservation","ts":"...","who":["evan","marcus"],
 "amount_days":2,"window":"2026-09-08..2026-09-09",
 "reason":"security updates (elevated from baseline)","approved_by":"evan",
 "impact":[{"item":"...","old":"2026-09-18","new":"2026-09-22"}]}

{"type":"assumption_broken","ts":"...","item":"...","assumption_id":"a2",
 "source":"API team slipped to Aug 17"}

{"type":"estimate_revised","ts":"...","item":"...","old_p85":"...","new_p85":"...",
 "reason_event":"<ts/index of causal event>"}   // MUST reference a causal event

{"type":"started","ts":"...","item":"..."}
{"type":"delivered","ts":"...","item":"...","scope_delta":"none | ref to scenario"}

{"type":"precondition_resolved","ts":"...","item":"...","precondition":"..."}
```

**Invariant:** every `estimate_revised` references a causal event. The agent must refuse to record an orphan date change.

### 5.4 Cycle-time history (`history/cycle-times.jsonl`)

Written automatically on `delivered`:

```jsonc
{"item":"...","owner":"priya","size":"M","work_type":"build",
 "dependency_profile":"cross-team","forecast_p50_days":9,"actual_days":13,
 "started":"...","delivered":"...","preempted_days":2}
```

Raw and fine-grained; models stay coarse (§7).

## 6. Capacity model

### 6.1 Roster (`config/team.yaml`)

```yaml
team:
  - id: evan
    role: lead
    focus_factor: 0.5     # fraction of nominal day converting to project work
  - id: priya
    focus_factor: 0.8
  - id: marcus
    focus_factor: 0.7
```

**Deliberately absent:** skill ratings, execution profiles, velocity multipliers. Per-person forecasting emerges from measured history (§7), not asserted config. `focus_factor` values are seeded as honest guesses and revised via the adaptation loop (§8).

### 6.2 Calendar overlay (`config/calendar.yaml`)

```yaml
absences:
  - who: priya
    from: 2026-09-14
    to: 2026-09-25
    type: pto            # pto | partial | oncall — NEVER reasons
holidays: [2026-09-07]
oncall:
  - who: marcus
    window: 2026-08-31..2026-09-06
    focus_factor_override: 0.4
```

- **Half-day is the minimum unit.** Sub-half-day absence (appointments, slow sick mornings) is intentionally untracked — the learned drag coefficient (§8) absorbs it.
- **No reasons, ever.** `type: partial`, not "doctor's appointment."
- Optional adapter: one-way sync **in** from a team Outlook/Google calendar. Never sync out.

### 6.3 Capacity reservations

One-off (via the reservation command, §10) or recurring:

```yaml
# config/reservations.yaml
recurring:
  - name: ktlo-baseline
    fraction: 0.10        # 10% of each sprint
    applies_to: team
```

**Double-count guard:** ambient trickle work is already priced into measured cycle times. When a reservation is created for work resembling the baseline (e.g., routine security patching), the agent flags: "baseline drag likely already includes this; explicit reservation may overstate impact. Reserve only the *elevated* portion?" Rule of thumb: **visible and elevated → explicit reservation (appears in ledger and impact statements); ambient trickle → learned drag.**

## 7. Forecasting

**No story points anywhere in the core.** (Adapters may map to/from points if the org's ritual demands it.)

- Item duration model: `duration = execution(size, owner history) + coordination(dependency_profile)`. Execution compresses with skill and agent leverage; coordination does not. This is why the `dependency_profile` field is load-bearing.
- Forecasts are computed by walking the **actual calendar** (roster × focus factors × overlay × reservations) against sampled cycle times:
  - Cold start: seed per-(size, dependency_profile) duration guesses in config; label all forecasts `basis: seeded`.
  - Warm (≥ ~10 items in a profile class): sample from team-wide historical distribution for (size, dependency_profile). Report p50 and p85.
  - Per-person (≥ ~8–10 items for an owner): prefer the owner's personal distribution for the execution component.
- Every published forecast carries its `basis` string (e.g., "team median, size M, cross-team, n=12") — this is what makes estimates defensible.
- **Assignment-sensitivity view** (later phase): "lands Sept 18 if Evan, Sept 30 if Priya." **Private to lead only. Never published, never rendered to any external surface.** It is a planning aid for the speed-vs-growth assignment tradeoff, not a leaderboard.

## 8. Adaptation loop

- On every `delivered`: write cycle-time record; compute forecast-vs-actual delta.
- Quarterly or on `/cadence review`: propose (never auto-apply) config revisions — e.g., "Marcus's actuals run ~20% over forecast across n=9; suggest focus_factor 0.7 → 0.58, or investigate cause." Lead approves via normal config edit (git history = audit trail).
- The residual gap between calendar-based capacity and actual throughput **is** the baseline drag; it needs no configuration. It silently absorbs untracked KTLO, interrupts, and sub-half-day absence.

## 9. The commitment interview

### 9.1 Trigger tiers (anti-fatigue — this is a hard rule)

| Tier | Trigger | Interview |
|---|---|---|
| Full | External deadline OR stakeholder-visible commitment | All probe families + scenario modeling + confirmation artifact |
| Lite | Ordinary queue item, multi-day | 3 questions: scope ins/outs, dependency profile, top assumption |
| None | Sub-day tasks | Log and go |

The trigger question is "is anyone outside the team relying on a date?" — not "does a ticket exist." If engineers start giving pro-forma answers, the interview has failed; shorten it.

### 9.2 Probe families

**Generic (always available):**
- "The request says '[term]'. What is explicitly IN: which plans / states / entry points / user segments?"
- "What's the smallest version satisfying the literal ask? What version do you suspect the stakeholder pictures? If they differ, that gap is the commitment risk — name it."
- "What are you assuming exists or works that you haven't verified?" → assumptions list
- "What would make this take 2× as long? How likely?"
- "'Done' means: shipped to prod? Behind a flag? With analytics? Announced?"
- **"What needs to be done to unblock this work? Whose calendar does that sit on?"** → precondition records

**Environment-diff (catches implied scope activation):**
- "Who can *reach* this once it ships that can't today? What obligations attach to those users, segments, or geographies?"
- "Is this the first time we do [X] outside an experiment / flag / limited cohort? What did the experiment's constraints exempt us from — compliance, scale, a11y, localization, analytics contracts?"
- "What does this assume exists in production shape that currently exists only in prototype shape?"

**Context-aware (when artifacts are loaded — spec, thread, prior scenarios, cycle-time profiles):**
- Spec-diff: "The spec mentions [X] in §N; your scope summary doesn't. Deliberate exclusion or oversight?"
- History: "Ledger shows [profile] items running [N]wks over median. This matches that profile — same risk?"
- Aliasing check: "You said yes to [date]. The request said '[ambiguous term]'. Which scenario option does your yes refer to? That option name goes in the commitment record and the confirmation message."

**Context assembly is the hard part, not the question list.** Before a Full interview, the agent loads: the request thread, any spec, related prior scenario records, and relevant cycle-time profiles. Cold questions get shallow answers; loaded questions get real ones.

### 9.3 Preconditions

Unblock answers become typed records (owner, forecast, status) with a dependency edge in the queue. An unresolved precondition past its forecast automatically shifts the dependent item's date and writes the causal ledger event.

### 9.4 Probe library accretion

When an interview catches something real, append the pattern to `probes/library.md`:
`touches cancellation → state-rule check` · `touches PII → privacy review` · `first un-flagged launch → a11y audit`. Over time this becomes org-specific — and portable — IP at the level of *question patterns*, not answers.

### 9.5 Confirmation artifact (the de-aliasing mechanism)

Full-tier interviews end with a **drafted stakeholder confirmation**:

> "Committing to **Option B** by **Aug 24**: restrictive default flow, no retention offers, partial analytics. Retention offers (~3wk) and full analytics (~1wk) are deferred and queued as follow-ons. Reply to confirm."

The interview extracts specificity from the engineer; the confirmation extracts agreement from the stakeholder. A commitment record is not `confirmed` until the stakeholder's reply is linked. **The interview must give, not just take:** its output is armor (the confirmation message, the options, the forecast) — if it only records answers, it's compliance theater and people will route around it.

## 10. Command suite (Claude Code)

- `/cadence intake` — new work arrives. Runs tiered interview. For injections: **refuses to proceed without a named priority-placement approver.** Computes displacement (queue shift arithmetic + calendar re-walk). Drafts impact statement: "Accepting this at P1 pushes A ~2wks (Sept 18→Oct 2), B ~1wk. Approver: ___." On confirm: writes `injection` event, updates records, queues fan-out drafts.
- `/cadence reserve <who> <days> <window> <reason>` — capacity reservation. Re-walks calendar, drafts impact across in-flight items, checks double-count guard, on confirm writes event + queues fan-out. (This is the "I need two days for security — estimate the impact and push it" operation.)
- `/cadence commit <item>` — full interview + scenario modeling + confirmation artifact for a stakeholder-visible commitment.
- `/cadence status` — render current queue, projected dates (with basis strings), open preconditions, pending drafts.
- `/cadence publish` — present all pending drafts in `out/drafts/` for batch approval; on approval, adapters post to Jira/Confluence under the lead's identity.
- `/cadence delivered <item>` — close item, write cycle-time record, prompt for scope_delta vs. commitment.
- `/cadence review` — adaptation loop: forecast-vs-actual analysis, proposed config revisions.
- `/cadence sync` — pull external state via adapters (Jira rank/status, calendar feed); report drift between external state and core records; core wins on conflict, drift is surfaced not silently merged.

## 11. Privacy rules (enforced by the publish pipeline)

1. Per-person data (cycle times, focus factors, forecast deltas, assignment-sensitivity views) **never leaves the repo**. No adapter may render it.
2. External surfaces receive only: item-level dates, basis strings, event attributions (injection approvers, reservation reasons), and aggregate capacity notes ("team availability reduced ~15% for window") — attributed to windows, never to people.
3. Calendar overlay: half-day floor, typed, reason-free, one-way sync in.
4. Ledger attribution names **decision-makers** (who approved an injection), not performers.
5. Per-person data is firewalled from performance reviews. This is a team covenant, stated at repo creation, and any team member can invoke it.
6. Adding any person to the repo requires disclosing §11 to the existing team first.

## 12. Rendered views (adapter outputs)

- **Per-project timeline block** (Confluence page / Jira epic): cumulative, generated history — "Original: 3wks (Jun 2). +2wks (Jun 18): displaced by X, prioritized by A. +4d (Jul 7): API dependency slipped (assumption a2)." Every line traces to a ledger event.
- **Portfolio page** (later phase): current queue with projected dates; displacement history per project; injection sources per quarter; estimate accuracy **when assumptions held vs. broke** — the cut that separates "slow team" from "thrashed team."
- Tone rules: factual, attributed, neutral, boring. Drafts always pass the approval gate; posts go out as the lead.

## 13. Build phases

- **Phase 0 — Substrate (now):** repo structure, config files, team privacy conversation (§11 covenant), pick the authoritative external queue (Jira) and keep its rank real. Start appending ledger events **manually today** — history is the fuel for everything later and cannot be backfilled.
- **Phase 1 — Ledger + records, no automation (~2 wks manual):** commitment records, scenario records, hand-written events. Validates the schema and — critically — tests whether the artifact changes conversations before any code exists. If the manual version doesn't change conversations, the automated one won't.
- **Phase 2 — Interview + cascade math:** `/cadence intake`, `/cadence commit`, `/cadence reserve`. Seeded forecasts. Impact statements. Environment-diff probes go in the prompt on day one.
- **Phase 3 — Fan-out:** adapters + `/cadence publish` with approval gate. Reuse Overture's Confluence pipeline.
- **Phase 4 — Forecast hardening:** cycle-time-based forecasting as history accumulates (basis strings switch from `seeded` to measured). Adaptation loop live.
- **Phase 5 (earned, not assumed) — Portfolio view:** the leadership-facing artifact. Only after Phases 1–4 have produced honest data.

## 14. Eval cases

Maintain these as regression tests for the interview prompt:

1. **Cancel-flow aliasing:** request "enable online cancellation for Plan X by Aug 24." Interview must surface: (a) full vs. restrictive flow options with forecasts, (b) analytics deferral, (c) a confirmation artifact naming the chosen option. Fail if a commitment record is created with scope still ambiguous.
2. **Implied scope activation:** same request. Environment-diff probes must elicit that this is the first un-flagged launch and that regulated-state users become reachable → precondition record for state-rule check. Fail if reachability question is never posed.
3. **Security reservation:** "I need 2 days ×2 engineers for security this sprint." Must produce per-item impact deltas, the double-count guard check, and a drafted publish batch.
4. **Orphan date change:** attempt to revise an estimate with no causal event. Agent must refuse and ask which event explains it.
5. **Injection without approver:** attempt intake of a P1 injection with no named placement approver. Agent must refuse to cascade.

## 15. Non-goals (v1)

- No skill taxonomies, velocity multipliers, or per-person skill config (measured history covers it — §7).
- No dependency graphing beyond precondition edges; no Monte Carlo beyond p50/p85 sampling.
- No automatic re-estimation intelligence — the agent drafts, humans decide.
- No bot-identity posting; no unattended publishes.
- No personal-life mode. Portability means clean adapters and config, nothing more.
