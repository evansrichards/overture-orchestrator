# Workspace: layout, config, event log, git topology

## Layout

```
planning/
  index.md                      # workspace index: all proposals + status
  .workspace.yml                # workspace defaults (publish target, caps, paths)
  .onboarding.yml               # per-command usage counts, concepts introduced
  catalog.jsonl                 # GENERATED on publish — settled records index
  context/                      # canon: durable shared considerations
    apps/<app>.md
    domains/<domain>.md
    teams/<squad>.md
    business.md                 # objectives / non-objectives (optional)
    glossary.md                 # promoted canonical definitions
  library/                      # distilled external / pre-orchestrator docs
  proposals/
    <slug>/
      proposal.md               # the publishable artifact source
      decisions/                # one file per decision record
      assumptions/              # one file per assumption record
      evidence.md               # evidence records
      assets/                   # images, design snapshots
      questions.md              # GENERATED view of open question-type records
      definitions.md            # proposal-local glossary
      descoped.md               # out-of-scope bucket — captured, not forgotten
      todos.md
      inbox/                    # inbound items awaiting triage
      handoff/                  # engineer deep-context pointers
      context/                  # PRIVATE. Politics, optics, candid notes.
      .events.jsonl             # append-only local event log
      .config.yml               # publish target, audiences, tags, last publish
```

One directory per proposal, keyed by slug (kebab-case, derived from the frame).
`index.md` is what makes `attach` fast and what makes concurrent proposals
legible.

`questions.md` and `catalog.jsonl` are **generated views** — never hand-edit
them; regenerate from the records. Everything else is source.

## The private zone

`proposals/<slug>/context/` is private by construction:

- It is **gitignored** out of the workspace repo (`references/privacy.md` covers
  enforcement). It never touches a remote.
- The publish path, the `ask` path, the leak-check subagent brief, and catalog
  generation have **no read access** to it.
- There is no inline "mark this paragraph private" mechanism anywhere else.
  Mixing zones inside one file is the exact failure mode this design prevents —
  if the user asks for inline privacy tagging, redirect them to the zone.

A missing overlay (fresh machine, overlay not restored) is **not an error**.
Draft without private context and note the absence once; never fail the command.

## `planning/.workspace.yml`

Workspace-level defaults. Not hand-edited — written by the first-run wizard and
amended by `status`-surfaced config proposals.

```yaml
version: 1
repo:
  remote: git@github.com:<enterprise-org>/<workspace-repo>.git
  private_overlay: gitignored          # gitignored | separate-local-repo
publish:
  default_target: confluence           # confluence | local
  confluence:
    space: <SPACE-KEY>
    parent_page_id: "<id>"
  local:
    dir: rendered/
reader_cost:
  ask_cap_per_person: 3                # publish warns above this
  require_scoped_ask: true             # every audience ask needs a time estimate
staleness:
  consideration_file_days: 90
  evidence_days: 90
  open_question_days: 14               # drives nudges
onboarding:
  narration_threshold: 3
```

## `proposals/<slug>/.config.yml`

```yaml
version: 1
slug: invitations-flow
title: Invitations flow revival
frame_type: problem                    # problem | opportunity | decision-needed | exploration
maturity: socializing                  # draft|socializing|in-review|decided|superseded
decided_outcome: null                  # approved | rejected | shelved  (when decided)
tags:
  apps: [accounts, login]
  domains: [authentication]
  realms: [provider, group-admin]
audiences:
  - name: Product
    people: [<person>]
    ask: "Sign-off on §3 scope"
    estimate: "10 min"
  - name: Design
    people: [<person>]
    ask: "Resolve Q-004"
    estimate: "15 min"
publish:
  target: confluence
  space: <SPACE-KEY>
  page_id: "<id>"                      # null until first publish
  last_published:
    at: 2026-08-10T09:12:00Z
    page_version: 7
    content_hash: "sha256:<hex>"
leak_denylist:                         # merged with tag-derived entries at run time
  topics: []
  names: []
imported_from:                         # provenance for --from-descoped / --from-existing
  kind: null                           # descoped | existing | null
  ref: null
```

Every configuration key past the frame is **optional with a sensible default**.
`init` must never feel like a form — see `interaction.md`.

## `planning/.onboarding.yml`

```yaml
version: 1
command_usage: { frame: 4, decide: 11, assume: 2 }
concepts_introduced: [frame, decide, decider]
tour_completed: false
```

## Event log — `proposals/<slug>/.events.jsonl`

Append-only, one JSON object per line, never rewritten or reordered. This log is
what makes batching possible and what generates the "changes since last publish"
section.

```json
{"ts":"2026-08-18T14:22:05Z","event":"decision.settled","id":"D-007","actor":"evan","payload":{"choice":"No account code required","decided_by":"<person>","options_considered":["Require code","No code"]}}
```

Fields: `ts` (UTC ISO-8601), `event`, `id` (record id when applicable), `actor`,
`payload`.

**Event vocabulary** — use these names exactly; renderers and `status` key off them:

| Group | Events |
|---|---|
| Proposal | `proposal.created` `frame.set` `frame.revised` `maturity.changed` |
| Records | `decision.created` `decision.state_changed` `decision.settled` `decision.superseded` `decider.assigned` |
| Assumptions | `assumption.created` `assumption.state_changed` `assumption.mined` |
| Evidence | `evidence.created` `evidence.refreshed` `evidence.flagged_stale` |
| Definitions | `definition.created` `definition.imported` `definition.promoted` `definition.diverged` |
| Scope | `descope.moved` `descope.revived` `todo.added` `todo.done` |
| Inbound | `inbox.received` `inbox.triaged` `inbox.dismissed` |
| Outbound | `ask.drafted` `ask.delivered` `comment.placed` |
| Publish | `publish.started` `publish.blocked` `publish.completed` `dirtypage.detected` |
| Verify | `leakcheck.flagged` `leakcheck.resolved` |
| Interview | `question.queued` `interview.answered` |

`interview.answered` records the question, **the options presented**, and the
selection — interview history is replayable and auditable like every other state
change, and the presented options are exactly the "options considered" a
decision record needs.

**Queued questions** live as `question.queued` events with no matching
`interview.answered`. That set *is* the pending queue drained at interaction
points.

## Record IDs

Per-prefix counters, allocated by scanning existing records — never reused, never
renumbered.

| Prefix | Record | Home |
|---|---|---|
| `D-` | decision (`type: decision`) | `decisions/D-007-<slug>.md` |
| `Q-` | open question (`type: question-resolution`) | `decisions/Q-004-<slug>.md` |
| `DEF-` | definition (`type: definition`) | `decisions/DEF-002-<slug>.md` |
| `SC-` | scope change (`type: scope-change`) | `decisions/SC-001-<slug>.md` |
| `A-` | assumption | `assumptions/A-003-<slug>.md` |
| `E-` | evidence | section in `evidence.md` |

The prefix is a **readability view on `type`**, not a separate lifecycle — all
four decision prefixes share one state machine and one renderer. **IDs are
stable:** if a record's type changes (a question that resolves into a standing
decision), the ID does not change; add a `note` recording the reclassification.

## Git topology

Placement is decided by **radioactivity, not repo ownership**. "Private" in an
enterprise org still means readable by org owners, admins, and security tooling.

| Material | Home |
|---|---|
| Proposals (sans private zones), decisions, definitions, canon, library, event logs | Enterprise org **private repo** — contains nothing the author wouldn't defend if an admin read it |
| `proposals/*/context/` — politics, optics, candid notes | **Never-remote local overlay**: gitignored; optionally its own local-only git repo for history |
| Canon, once teams adopt it | Shared org-visible **context repo**, extracted post-pilot; consumed as submodule or sibling path. Deferred in v1. |

Workspace `.gitignore` must contain, and `init`/first-run must verify:

```gitignore
planning/proposals/*/context/
```

Verify with `git check-ignore -q planning/proposals/<slug>/context` before the
first `publish` of a proposal. If it is **not** ignored, stop and fix it before
writing anything private — this check is cheap and the failure is unrecoverable.

**Workspace-per-context:** personal projects get a separate workspace on personal
infrastructure. Work and personal material never share a repo in either
direction.

**Residual risk, stated honestly:** the work laptop is company property; any file
on it is reachable via device imaging or legal discovery. The mitigation is
editorial, not technical — keep the candid layer terse and professional enough to
be embarrassing, never damaging. Say this once during first-run setup; do not
repeat it at every write.

## `planning/index.md`

Regenerated on `publish` and on `status`. One row per proposal:

```markdown
| Proposal | Frame | Maturity | Open | Unowned | Next ask | Updated |
|---|---|---|---|---|---|---|
| [invitations-flow](proposals/invitations-flow/proposal.md) | problem | socializing | 3 | 1 | Design: Q-004 | 2026-08-17 |
```
