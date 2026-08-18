# Command reference — operational procedures

All commands are batch-friendly: they append to the event log and defer questions
to the next interaction point unless `--now` is passed
(`interaction.md` → Batching rules).

**Every command ends by appending its events.** A command that reports success
without having written its events has not run.

---

## `init [--from-descoped <id>] [--from-existing <url|path>]`

Scaffold a new proposal.

1. **Frame first.** A proposal without a stated problem or objective is the root
   cause of unreadable documents. Ask for the frame as **free text** (not
   enumerated — it would anchor the user), then classify its type via
   `AskUserQuestion`: problem / opportunity / decision-needed / exploration.
2. Derive the slug (kebab-case) from the frame; confirm it if ambiguous.
3. Create `proposals/<slug>/` per `workspace.md` § Layout, including empty
   `context/`, `inbox/`, `handoff/`, `assets/`.
4. Verify the private zone is gitignored (`privacy.md` → Git enforcement).
5. Run the skippable configuration interview — publish target → audiences →
   realms/apps touched (`multiSelect`, options sourced from the
   consideration-file index) → leak-denylist seeding. **Every step is skippable.**
6. Load matching consideration files transitively
   (`context-and-catalog.md`).
7. Write `.config.yml`, append `proposal.created` + `frame.set`, add the row to
   `planning/index.md`.

**`--from-descoped <id>`** — pull the descoped entry's content and revival
trigger from the source proposal's `descoped.md` into the new frame; append
`descope.revived` on the source.

**`--from-existing <url|path>`** — run the distill pass
(`context-and-catalog.md` → Library): extract decisions, definitions, and
constraints into standard records. **Distill, don't dump** — never paste the
source document wholesale into `proposal.md`.

---

## `attach <slug>`

Rehydrate an existing proposal. This is an interaction point — it drains.

1. Load `.config.yml`, `proposal.md`, records, and the tail of `.events.jsonl`.
2. **Summarize deltas since the last session** — what changed, what settled.
3. **Drain the inbox** (`inbound.md` → Triage).
4. **Drain the queued question backlog** (`interaction.md` → Batching rules).
5. Report pending items: open questions by assignee, unowned contested
   decisions, invalidated assumptions with dependent decisions, stale evidence.

With no `<slug>`, show `planning/index.md` as a picker.

---

## `frame <statement>`

Set or revise the problem/opportunity statement. Supports problem, opportunity,
decision-needed, and exploration framings — it is not always a "problem."

A **frame revision is itself a decision record** (`type: decision`), so scope
drift is visible in the history. Append `frame.revised`, never overwrite silently.

Multiple proposals may share one frame; that is allowed and worth noting in
`index.md` when it happens.

---

## `question <text> [--for <person/role>]`

Log an open question as a `Q-` record: `type: question-resolution`,
`state: proposed`, `assignee: <person/role>`.

- Set `decide_by` if the user gives a deadline.
- If it is contested from the start, get a `decider` (`records.md`).
- With `--for`, also draft the outbound ask in that recipient's register — same
  path as `ask`, including the leak-check.

---

## `decide <text>`

Record a decision.

1. If the options are known, present them via `AskUserQuestion` — the presented
   options become `## Options considered`, the selection becomes `## Choice`
   (`interaction.md` → Mapping to the data model).
2. Capture context, options, choice, and consequences.
3. **Check for conflict** with earlier records. If it contradicts one, prompt for
   supersession and set `supersedes:` rather than leaving two live records that
   disagree.
4. If it settles a `Q-` record, transition that record rather than creating a
   duplicate.
5. If it settles a definition that looks durable, prompt to **promote** it to
   `planning/context/glossary.md`.
6. Verify the settling basis (`records.md` → State transitions). Never settle on
   your own judgment.

---

## `define <term>`

Definitions subsystem entry point. Resolution order — canon, then precedent, then
new — is in `records.md` § Definitions. Never let the user retype a definition
that already exists: they either **import** it or **deliberately diverge**, and
divergence is recorded as an explicit note.

---

## `assume <text> [--mine]`

Record an assumption (`records.md` → Assumption records). `--mine` runs the
assumption-mining review pass and presents candidates via `AskUserQuestion` with
`multiSelect`.

---

## `evidence <claim> --source <link>`

Record an evidence citation with pull date and owner. If the claim is already in
the draft as a bare number, link the record to it.

---

## `todo <text>`

Append to `todos.md`. The one genuinely lightweight command — do not interview,
do not classify, just append and move on.

---

## `descope <section|item> --reason <text>`

Move content to the descope bucket via a scope-change record. Full procedure in
`records.md` § The descope bucket. **Never delete the content.**

---

## `ask <person> <about>`

Draft an outbound communication in the appropriate register for that audience.

1. Compose the draft (Teams message, email, or Confluence comment).
2. **Run the leak-check** (`privacy.md`) — outbound counts as leaving the repo.
3. Present the draft for approval.
4. Deliver per `inbound.md` § Outbound delivery. **Never auto-send.**
5. Append `ask.drafted`, then `ask.delivered` once the user confirms it went out.

Before drafting, check the stakeholder load: if this person already has
`reader_cost.ask_cap_per_person` outstanding asks across all proposals, say so
and let the user decide whether to send anyway.

---

## `status`

The workspace dashboard, and an interaction point. Render:

1. **Maturity banner** with the per-audience "what I need from you" lines.
2. **Open decisions and questions by assignee**, with deciders and decide-by
   dates; overdue items first.
3. **Unowned contested decisions** — contested with no `decider`.
4. **Invalidated assumptions** and every decision that `rests_on` them.
5. **Stale evidence** older than the threshold *and still cited by an active
   decision*.
6. **Staleness warnings** — consideration files not reviewed in
   `staleness.consideration_file_days`; questions open longer than
   `staleness.open_question_days` (offer to draft a follow-up via `ask`).
7. **Config debt** — skipped configuration that now matters; observed patterns
   worth proposing (`onboarding.md` → Configuration by observation).
8. **Stakeholder load view** — outstanding asks per person **across all
   concurrent proposals**, so the fourth ask queued on the same PM is visible
   before it is sent.

Then drain the inbox and the question queue.

---

## `publish [--dry-run]`

Full pipeline in `publishing.md`. Order is not negotiable:

```
flush events ─▶ regenerate proposal.md ─▶ [--dry-run: assumption mining]
   ─▶ dirty-page guard ─▶ render for target ─▶ reader-cost lint
   ─▶ LEAK-CHECK (blocks) ─▶ write page ─▶ regenerate catalog.jsonl + index.md
   ─▶ record publish event with content hash
```

`--dry-run` runs everything except the write, and additionally runs assumption
mining. Publish is **idempotent** — re-publishing fully regenerates the page.

---

## `handoff`

Approved proposals only. Emit the handoff packet for downstream engineering work:
settled decisions, constraints, settled definitions, and links to the proposal
repo — consumable as seed context. v1 exports **readable markdown**; schema
alignment waits for the first real handoff. See `publishing.md` § Handoff packet.

If the proposal is not `decided (approved)`, say so and stop.

---

## `help`

One-screen command map grouped by lifecycle stage, annotated with the user's own
usage from `.onboarding.yml` — e.g. *"you haven't used `descope` yet — it
captures out-of-scope ideas without losing them."* Not a man page.

---

## `tour`

Opt-in guided walkthrough on a scratch proposal. **Never forced**, never
suggested more than once per workspace.
