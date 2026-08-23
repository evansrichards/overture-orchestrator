# Onboarding — tour, first run, and echo teaching

Cadence onboards in two distinct situations: **no workspace yet** (Phase 0 —
a guided checklist that stops short of creating anything) and **workspace
exists, user is new** (the tour plus echo teaching that decays as fluency
grows). Detect which one applies before choosing a path: run the workspace
parent walk (`workspace.md` → Locating it) first.

## `tour` — the concept walk

Give the tour on `/cadence tour`, and offer it once when a bare `/cadence`
runs with no usage history (see State, below). Keep it to one screen per
stop, in usage order, each stop anchored to the command where the concept
first bites:

1. **The ledger is the record.** `ledger/events.jsonl` is append-only and
   authoritative; Jira and Confluence are rendered views of it. Dates never
   "slip" — conditions change, and every date change references the event
   that caused it. This is why the agent will sometimes refuse: an estimate
   revision with no causal event, or an injection with no named approver,
   isn't strictness for its own sake — it's what keeps every published
   timeline defensible.
2. **Your data lives in *your* private repo.** The plugin ships no workspace
   and never creates one. Per-person data (cycle times, focus factors)
   never leaves that repo and never renders to any external surface.
3. **Interviews are tiered so they stay cheap.** Sub-day work: log and go.
   Ordinary multi-day work: three questions. Only stakeholder-visible dates
   get the Full interview — and its output is armor for you (named options,
   a defensible forecast, a confirmation message), not paperwork.
4. **Config is deliberately small.** `team.yaml` is ids and focus factors
   only; `calendar.yaml` is half-day, typed, reason-free; recurring
   reservations live in `reservations.yaml`; everything else is learned
   from measured history, not asserted.
5. **The working loop:** `intake` when work arrives → `commit` when someone
   outside the team relies on a date → `status` to see the queue with
   defensible forecasts → `delivered` to close and bank cycle-time history
   → `publish` to fan out approved drafts. `reserve` when capacity leaves
   the sprint. `review` and `sync` join in later phases.
6. **What's stubbed today** (`SKILL.md` → Build-phase discipline): publish,
   review, and sync — say what the manual equivalent is when they come up.

End the tour by asking (via `AskUserQuestion`) whether a workspace exists
yet; route to the Phase 0 walkthrough if not, or offer a first `intake` /
`status` if it does.

## Phase 0 walkthrough (no workspace yet)

A guided checklist, not a wizard: **never create the data repo or any part
of the workspace** — Phase 0 begins with the team privacy conversation, a
human act (`privacy.md` → Standing rules). Walk the user through, one step
at a time, explaining *why* before *what*:

1. **The privacy conversation.** Before the repo exists, the team hears the
   §11 covenant: what will be recorded, that per-person data never leaves
   the repo, that it is firewalled from performance reviews, and that any
   member can invoke the covenant. Ask the user to confirm this
   conversation has happened — if it hasn't, stop here and offer talking
   points from `privacy.md`; the rest of the checklist waits.
2. **Create the private repo** (them, not you) and copy the plugin's
   `workspace-template/` into it. Point at the template's README.
3. **Fill in `config/team.yaml`** — roster ids and honest focus-factor
   guesses. Explain that guesses are fine: the adaptation loop revises them
   from measured history, and git history is the audit trail.
4. **Skim `calendar.yaml` and `reservations.yaml`** — confirm the rules
   read back correctly: half-day floor, no reasons, elevated-vs-ambient.
5. **Pick the authoritative external queue** (usually a Jira project) and
   record it in `adapters.yaml`. The rank there must be kept real.
6. **Start the ledger today.** History cannot be backfilled. Offer to
   append the first events from what the user tells you — current in-flight
   items as records with `started` events.

**Validate, don't scaffold:** once the user says the workspace exists, run
the parent walk to find it, check the tree against `workspace.md` → Layout,
and validate any records already present against `shared/record-schemas/`.
Report what's missing or malformed as a checklist, and offer fixes
file-by-file — inside their workspace, with their confirmation.

## Echo teaching

The user never has to memorize subcommands. Map natural language to the
action, perform it, and narrate the mapping once:

> We just got a P1 from the VP → `/cadence intake` (injection). Before I can
> compute displacement I need the named placement approver.

Narration **decays**. Track usage counts in `.onboarding.yml` at the
workspace root (create it lazily on first use; one YAML map of subcommand →
count). After the threshold (default 3 uses of a subcommand), stop
explaining that mapping. Slash commands are accelerators for the fluent,
never prerequisites for the new.

## Teach at the moment it bites

Don't front-load concepts; explain each rule the first time it fires, then
let the count decay it like any narration:

| First time this happens | Teach |
|---|---|
| An injection arrives | Why a named approver is required before anything cascades |
| A date needs to move | Why the revision must reference a causal event |
| A Full interview starts | The tier rules — and that the output is armor, not compliance |
| A reservation resembles baseline work | The double-count guard and elevated-vs-ambient |
| A draft is queued | Nothing auto-sends; `publish` gates everything; what may never appear externally |
| A delivery closes | Why the cycle-time record matters (it feeds every future forecast) |

If a taught rule keeps surprising the user after the decay threshold, the
teaching failed — say the rule again in one line and point at the reference,
rather than re-running the lesson.

## State

`.onboarding.yml` (workspace root, lazily created):

```yaml
tour_offered: true          # bare /cadence offers the tour only once
usage:                      # narration decay counters
  intake: 4
  commit: 1
narration_threshold: 3      # per-subcommand; user-adjustable
```

Usage counts are workspace-level, so a team shares fluency — that is
deliberate (the narration is about the tool, not the person). Nothing in
this file is per-person data, but it lives in the private repo like
everything else.
