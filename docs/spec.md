# Planning Orchestrator — Specification

**Status:** Draft v0.1 · **Owner:** Evan Richards · **Last updated:** 2026-08-17

---

## 1. Purpose

A command-driven agent skill suite for drafting, aligning, and publishing proposals of any kind — product, design, engineering, project, or organizational. It exists to get multiple stakeholders (PMs, designers, engineers, leadership) aligned faster and with higher-quality discussion, while producing a durable, readable record of the problem, the reasoning, the decisions, and the open questions.

It is the *upstream sibling* of the engineering orchestrator (the GitHub blackboard system). The planning orchestrator owns speculative, cross-functional work — proposals that may never ship, or never even be sent. Once a proposal is approved and is engineering work, it hands off downstream.

**Non-goals:** This is not a project management tool, a ticketing system, or a knowledge base. It does not track execution. It does not replace conversations — it raises the floor of the conversations that happen.

## 2. Design principles

1. **Markdown in a repo is the source of truth. Confluence is a render target.** Publishing is one-way and idempotent. This avoids the bidirectional-sync tarpit and makes every artifact durable, diffable, and agent-readable.
2. **Structural privacy, not behavioral privacy.** Private context is unreachable by the publish path, not filtered out of it. A verifier session guards against inference leaks.
3. **Attention is the scarce resource.** Commands queue locally and batch; all questions to the human are delivered through Claude Code's `AskUserQuestion` tool in batched, multi-step flows (§7.2); the user can run several proposals concurrently without rapid context switching.
4. **Short documents, deep context.** The rendered artifact answers "what problem, what approach, how far along, what do you need from me" within one screen. Everything else is reachable, not present.
5. **Decisions are the atomic unit.** Questions, definitions, and scope changes are all decision-shaped: proposed → contested → settled. One lifecycle, many views.
6. **Extensible over complete.** 80% of the value from 20% of the machinery. Pilot solo first; org rollout only after the core loop proves out.
7. **Alignment is co-authored.** A polished doc that arrives fully-formed reads as a fait accompli and produces resistance, not alignment. The system makes contribution visible (attribution flows from inbox provenance onto records; the rendered doc credits shapers) and publishes early at `socializing` maturity with open questions assigned to named people — deliberate seams, not gaps.
8. **Reader cost is a budget.** The tool makes producing proposals cheap; it must not export the cost to reviewers. Every publish states a scoped, time-estimated ask per audience; publish warns when outstanding asks for any one person exceed a cap; the workspace tracks stakeholder load across concurrent proposals.

## 3. System boundaries

| Concern | Planning orchestrator | Engineering orchestrator |
|---|---|---|
| Input | An idea, problem, or opportunity | An approved proposal, epic, or technical task |
| Artifacts | Proposal docs, decision records, glossaries, consideration files | Issues, PRs, verification plans, labels |
| Medium | Local markdown repo → Confluence | GitHub blackboard |
| Verification | Leak-check + review sessions | Automated / agent / human / monitor checks |
| Exit | Proposal approved, rejected, or shelved | Code shipped and verified |

**Handoff:** An approved proposal exports a *handoff packet* — the settled decisions, constraints, settled definitions, and links to the proposal repo — consumable as seed context by the engineering orchestrator. Small technical tasks (maintenance, security bumps, tweaks) skip planning entirely and enter the engineering orchestrator directly.

## 4. Workspace structure

```
planning/
  index.md                      # workspace index: all proposals + status
  catalog.jsonl                 # GENERATED: all settled decision records &
                                #   definitions across proposals (see §10)
  context/                      # durable, shared consideration files (see §8)
    apps/
      accounts.md
      login.md
    domains/
      authentication.md
      analytics.md
    teams/
      <squad>.md
    glossary.md                 # promoted, canonical definitions
  library/                      # distilled external/pre-orchestrator docs (§10.3)
  proposals/
    <slug>/
      proposal.md               # the publishable artifact source
      decisions/                # one file per decision record
      assumptions/              # one file per assumption record (§5.4)
      evidence.md               # evidence records (§5.5)
      assets/                   # images, design snapshots (§13)
      questions.md              # open questions (each decision-shaped)
      definitions.md            # proposal-local glossary
      descoped.md               # the out-of-scope bucket — captured, not forgotten
      todos.md
      inbox/                    # inbound items awaiting triage (§12)
      handoff/                  # engineer deep-context pointers (links, notes)
      context/                  # PRIVATE. Politics, optics, candid notes.
      .events.jsonl             # append-only local event log
      .config.yml               # publish target, audiences, realm tags,
                                #   last-published page version + content hash
```

- **One directory per proposal**, keyed by slug. `index.md` gives `attach` a fast picker and shows status across concurrent proposals.
- **`proposals/*/context/` is the private zone.** The publish path has no read access to it — structurally, not by convention (implemented via the skill's file-access rules and an explicit denylist in the publish command).
- The **event log** is what enables batching: every command appends events; `publish` and `status` are the flush points.

## 5. Data model

### 5.1 Artifact maturity

Every proposal carries a top-level maturity state, rendered as a status banner:

`draft → socializing → in-review → decided (approved | rejected | shelved) → superseded`

The banner includes a per-audience "what I need from you" line (e.g., "PMs: sign-off on §3 scope. Design: unresolved question Q4."). This is the ten-second orientation requirement.

### 5.2 Decision records

Every alignment point is a decision record with:

```yaml
id: D-007
title: Invitation acceptance requires no account code
state: proposed | contested | deferred | settled | superseded
type: decision | definition | scope-change | question-resolution
decider: <person/role>        # REQUIRED once contested; who has authority to settle.
                              #   A contested record without a decider is "unowned"
                              #   and flagged by status.
positions:                    # only while contested
  - holder: <person/role>
    summary: ...
    provenance: public | private   # public = arrived via public channel (page comment);
    consent_to_attribute: bool     #   private positions render anonymized unless consented
decided_by: ...
decided_on: ...
decide_by: ...                # optional deadline; drives nudges and render urgency
blocks: [D-004]               # optional; decisions gated on this one
rests_on: [A-002, A-003]      # assumptions this decision depends on (§5.4)
supported_by: [E-001]         # evidence citations (§5.5)
pending: A-007                # only when state=deferred: the assumption under test
context: ...                  # why, options considered, consequences
supersedes: D-003             # optional
contributed_by: [...]         # accumulated from inbox provenance (§12.1)
```

Questions are decisions in the `proposed` state with an assignee. Definitions are decisions with `type: definition` (§9). Descoping is a decision with `type: scope-change` whose payload moves content into `descoped.md`. A decision "resolved by experiment" is `state: deferred` with `pending` pointing at the assumption under test — no separate machinery. **One lifecycle, one renderer, one mental model.**

**Decision rights:** when a decision enters `contested` (or a question opens), the orchestrator prompts "who settles this?" via `AskUserQuestion`, options drawn from the audience list. Settling requires either ingested input from the decider (inbox provenance) or an explicit "decided in <meeting>, <date>" note. This is deliberately the minimum viable slice of DACI — a decider per contested decision — and no more.

### 5.3 The descope bucket

Nothing is deleted during scope negotiation. `descope` moves content to `descoped.md` with the decision that removed it and a note on what would trigger revival. Descoped items can seed new proposals (`init --from-descoped`).

### 5.4 Assumption records

A proposal's assumptions are its load-bearing walls — and in agent-assisted drafting, the sharpest question a reader has is "what has and hasn't been considered." Assumptions are therefore first-class records, not a prose section:

```yaml
id: A-003
statement: Group admins receive invitations by email
state: stated | validating | validated | invalidated | accepted-risk
criticality: ...              # what breaks if this is wrong
test: ...                     # how it will be / was validated (plan, experiment, evidence link)
owner: <person/role>
supported_by: [E-002]
```

Rendered as a **Key Assumptions** section near the top of the doc. Because decisions declare `rests_on`, an assumption flipping to `invalidated` automatically flags every dependent decision for review — the mechanism that keeps assumptions live instead of ritual.

**Assumption mining:** on demand (`/plan assume --mine`) and during `publish --dry-run`, a review pass reads the proposal and surfaces *implicit* assumptions the text depends on but never states ("this assumes the account-code flow can be deprecated for the provider realm"). Candidates are presented via `AskUserQuestion` (`multiSelect`: record / reject / already covered). Consideration files sharpen the miner: the accounts realm file teaches it which assumptions proposals in that territory tend to hide. The author cannot see their own water; the miner exists to see it for them.

### 5.5 Evidence records

Quantitative claims rot silently in long-lived docs. Any load-bearing claim ("38% of invites expire") is an evidence record: claim, source (query/dashboard link), pulled date, owner. Decisions and assumptions cite evidence via `supported_by`; `status` flags evidence older than a freshness threshold that is still cited by active decisions. This is what gives data science a reason to trust — and contribute to — these documents.

## 6. Public/private boundary

Two mechanisms, layered:

1. **Structural separation.** Private material lives only in `context/`. The publish pipeline cannot read it. There is no "mark this paragraph private" inline tagging in publishable files — mixing zones in one file is the failure mode this design exists to prevent.
2. **Leak-check verifier.** Before any publish or `ask` (outbound communication), a separate agent session reviews the rendered output. It receives only: (a) the rendered artifact, and (b) a *topics/names denylist* — never the private content itself. The denylist is hybrid: auto-derived from frontmatter tags on `context/` files, plus manual entries added during the `init` configuration flow (a skippable step — see §7.2) and editable any time after. It flags direct leaks and inferable ones ("this phrasing implies the reorg"). It also flags any **named position lacking a consent basis** (§5.2): attributing "Sarah opposes this" to a page before Sarah has said so publicly is position-laundering, and it burns candor exactly once. Publish blocks on unresolved flags. This mirrors the engineering orchestrator's rule: **the drafting agent never verifies its own output.** Because `AskUserQuestion` is unavailable in subagents, the verifier returns flags as structured data and the main session presents resolution options to the user (§7.2).

Private context still informs drafting (the orchestrator may read it while working locally); the boundary applies to anything that leaves the repo.

## 7. Command reference

All commands are Claude Code slash commands within the skill suite. All are batch-friendly: they append to the event log and defer questions to the next interaction point unless `--now` is passed.

| Command | Function |
|---|---|
| `/plan init [--from-descoped <id>] [--from-existing <url\|path>]` | Scaffold a new proposal. Interview establishes: framing (§7.1), publish target, audiences, realms/apps touched (which pulls consideration files, §8). `--from-existing` ingests a current doc/epic and restructures it. |
| `/plan attach <slug>` | Rehydrate an existing proposal: load state, summarize deltas since last session, list pending items. |
| `/plan frame <statement>` | Set or revise the problem/opportunity statement. Not always a "problem" — supports problem, opportunity, decision-needed, and exploration framings. Multiple proposals may share one frame. |
| `/plan question <text> [--for <person/role>]` | Log an open question as a decision record. If `--for`, drafts the outbound ask in the recipient's register (see `ask`). |
| `/plan decide <text>` | Record a decision: captures context, options considered, choice, consequences. Prompts for supersession if it conflicts with an earlier record. |
| `/plan define <term>` | Definitions subsystem entry point (§9). |
| `/plan assume <text> [--mine]` | Record an assumption (§5.4). `--mine` runs the assumption-mining review pass and presents candidates via `AskUserQuestion`. |
| `/plan evidence <claim> --source <link>` | Record an evidence citation (§5.5) with pull date and owner. |
| `/plan todo <text>` | Append to the task list. |
| `/plan descope <section\|item> --reason <text>` | Move content to the descope bucket via a scope-change decision. |
| `/plan ask <person> <about>` | Draft an outbound communication (Teams message, email, or Confluence comment) in the appropriate register for that audience. Runs the leak-check before presenting the draft. Delivery per §12.5. Never auto-sends. |
| `/plan status` | Render the maturity banner, open decisions/questions by assignee, unowned contested decisions, stale evidence under active decisions, staleness warnings, pending event-log items — and the **stakeholder load view**: outstanding asks per person across all concurrent proposals, so the fourth ask queued on the same PM is visible before it's sent. |
| `/plan publish [--dry-run]` | Flush the event log, regenerate the rendered artifact, run assumption mining (`--dry-run`) and the leak-check, apply the reader-cost lint (warn if any audience's ask is unscoped or any person's outstanding asks exceed the cap), write to the configured target. Idempotent: re-publish fully regenerates the page. |
| `/plan handoff` | (Approved proposals) Emit the handoff packet for the engineering orchestrator. |

### 7.1 Framing

`init` requires a frame before anything else can be added — a proposal without a stated problem/objective is the root cause of unreadable documents. Frames are revisable (`frame` command), and a frame revision is itself a decision record, so scope drift is visible in the history.

### 7.2 Interaction model (AskUserQuestion)

All questions the orchestrator asks the user are delivered via Claude Code's built-in `AskUserQuestion` tool — never as free-text prompts in the transcript. Free-text remains available to the user through the tool's built-in "Other" option, so nothing is lost by making structured choice the default.

**Tool constraints (design inputs, not choices):**

- 1–4 questions per call, 2–4 options per question; each question has a `header` (≤12 chars) and full question text; `multiSelect: true` allows multiple answers; users can always type a custom response.
- **Not available in subagents.** All interviewing must run in the main session. This has a direct architectural consequence for the leak-check verifier (§6): the verifier subagent returns structured flags as data; the *main* session then presents resolution choices to the user via `AskUserQuestion`. The verifier never prompts.

**Batching rules:**

1. **Interaction points, not interruptions.** Commands append questions-for-the-user to the event log rather than asking immediately (unless `--now`). The queue drains at defined interaction points: end of a command that requires input to proceed, `attach`, `status`, and `publish`.
2. **Multi-step flows.** When draining, the orchestrator groups queued questions into sequential `AskUserQuestion` calls of up to 4, ordered by dependency: questions whose options depend on earlier answers go in later calls. Independent questions are packed greedily into the earliest call. Target: resolve a typical session's pending input in 1–3 steps.
3. **Question authoring.** `AskUserQuestion` is for decision trees and clarifying questions — places where alignment between agent and user is the point. Truly open questions (the frame statement itself, novel design directions, anything where enumeration would anchor the user on the agent's guesses) stay free-text in the transcript. Within structured questions: options must be genuinely distinct courses of action, not paraphrases. When the orchestrator has a recommendation, it goes first with "(Recommended)" appended to the label. `multiSelect` is used for naturally plural inputs — realm/app tagging at `init`, selecting which descoped items to revive, choosing which consideration files apply. No meta-questions ("Is this plan good?"); interaction points only surface real decisions.
4. **Answers are events.** Every `AskUserQuestion` response is appended to the event log with the question, the options presented, and the selection — so interview history is replayable and auditable like every other state change.

**Mapping to the data model.** `AskUserQuestion`'s shape mirrors the decision record's shape: the options presented become the *options considered*, and the selection becomes the *choice*. When an interview answer settles a decision (`decide`, contested `define`, `descope` confirmation), the record is created directly from the tool call — the alternatives are captured for free, which is precisely the provenance the decision history needs.

**Per-command usage:**

| Command | AskUserQuestion role |
|---|---|
| `init` | Multi-step interview: framing type (problem / opportunity / decision-needed / exploration) → publish target → audiences → realms/apps touched (`multiSelect`, options sourced from the consideration-file index) → leak-check denylist seeding (manual adds on top of tag-derived entries). Every configuration step past the frame is individually skippable — `init` must never feel like a form; skipped steps get sensible defaults and can be revisited via `status`. |
| `decide` | When options are known, presents them as the choice set; the selection and rejected options populate the decision record |
| `define` (contested) | Competing definitions presented as options, holders named in descriptions |
| `descope` | Confirmation + "what would trigger revival" as a follow-up step |
| `publish` | Leak-check flag resolution: per flag — rephrase (recommended, with proposed rewording in the description) / remove / override-with-justification |
| `attach` / `status` | Drain point for the queued question backlog across the session |

## 8. Context skill files (domain considerations)

Lightweight markdown files owned by teams/domains, holding the considerations that otherwise require "get an engineer on a call":

- **Format:** bare lists — do's/don'ts, "in case of X, ask <person>", constraints, realm/channel implications. Deliberately low-ceremony so they get maintained.
- **Resolution:** When `init` (or a later edit) tags apps or domains, the orchestrator loads the matching files transitively — e.g., a proposal touching the login app also pulls `domains/authentication.md`. Domain files know which apps/services they implicate.
- **Effect:** Considerations are injected during drafting, and the review pass annotates the proposal with unaddressed considerations ("this doesn't address the group-admin realm").
- **Governance & cold start:** Seeded by Evan for accounts/login/auth from firsthand knowledge. Team ownership comes later, after the value is demonstrated. Each file has an owner and a last-reviewed date; the orchestrator flags files stale >90 days rather than trusting them silently.
- **Business context:** objectives/non-objectives can live in a `context/business.md` consideration file at the workspace level — same mechanism, no special machinery.

## 9. Definitions

Definitions are decision records (`type: definition`) with a two-tier scope:

1. **Proposal-local:** `define <term>` creates an entry in `definitions.md`. States: proposed → contested (competing definitions listed side by side with holders named) → settled.
2. **Durable/canonical:** On `define`, the orchestrator first checks `context/glossary.md` and relevant consideration files. If the term exists canonically, it **imports** (links, doesn't duplicate) and lints the proposal for usage inconsistent with the canonical meaning. If a local definition settles and appears durable, `decide` prompts to **promote** it to the workspace glossary.

**Rendering:** Contested definitions render in the open-questions area (an unsettled definition blocks downstream decisions — it is not appendix material). Settled definitions render as a compact glossary with first-use markers; long glossaries use Confluence expands.

**Anti-goal:** No terminology policing. The lint fires only on (a) the proposal contradicting its own settled definitions, or (b) contradiction of a canonical definition. Casual synonyms pass. The purpose is catching false agreement, not style enforcement.

## 10. Cross-proposal context: canon, precedent, library

Past work informs new proposals through three distinct mechanisms with different loading behavior. Conflating them is the primary rot vector for systems like this, so the distinction is structural.

### 10.1 Canon (always loaded)

What the workspace has *committed to*: `context/glossary.md` and the consideration files. Loaded automatically per tags at `init`. Kept small because promotion is deliberate — canon earns its context budget.

### 10.2 Precedent (retrieved on demand, never auto-loaded)

Everything that ever settled in any past proposal — definitions, decisions, descoped items — is indexed in `catalog.jsonl`, regenerated on every `publish` from decision-record frontmatter (term, type, tags, proposal, state, date). At pilot scale, lookup is a grep over this file. No retrieval infrastructure.

**Term-triggered lookup:** when a proposal uses or `define`s a term with no canonical entry, the orchestrator checks the catalog. On a hit, `AskUserQuestion`: *"You defined 'invitation' in invitations-flow (settled 2026-03) as X. Import (Recommended) / Redefine here / Ignore."* Import records provenance; redefine records an explicit divergence note. A second import of the same definition triggers a promotion prompt — repeated reuse is the evidence that a term belongs in canon. Users never retype a definition; they either import it or deliberately diverge from it. **Conflicting precedents:** when past proposals settled *different* definitions for the same term, lookup presents all of them with proposal names and dates; the user's selection is recorded as the tiebreak and immediately triggers the promotion prompt — a conflict surfacing is exactly the moment canon should absorb the term so the conflict never recurs.

**Related-proposal import at `init`:** the new proposal's app/domain/realm tags are matched against `index.md`; related proposals are offered via `multiSelect`. Importing brings in their settled definitions and surfaces their decisions **as precedent, not constraint** — rendered to the drafting agent with explicit framing that a past decision informs but does not bind. Without that framing, old decisions exert silent gravity on proposals that should be free to re-litigate them.

**Privacy rule:** the catalog indexes publishable artifacts only — settled records, definitions, descoped items. It never indexes any `context/` zone. Cross-proposal retrieval must not surface proposal A's private notes inside proposal B's drafting session; that pollution wouldn't leave the machine, but it can be paraphrased into B's public doc in ways the leak-checker cannot trace.

### 10.3 Library (distilled external docs)

Pre-orchestrator proposals, existing Confluence pages, and other historical docs enter via a distill pass (`init --from-existing` uses the same machinery): decisions, definitions, and constraints are extracted into standard record format under `library/`, and indexed in the catalog like everything else. **Distill, don't dump** — raw historical docs are the main source of stale, contradictory context.

## 11. Storage & repo topology

The workspace is a **git repository** — not loose local files. Git provides durability, multi-machine sync, history on every decision and definition (who changed canon, when, in what commit), and a governance mechanism for free: once consideration files are team-owned, changes to canon go through PRs.

**The seam is remote vs. never-remote.** Work product belongs on work infrastructure (a personal GitHub account is a policy/IP problem), but "private" in an enterprise org means private from colleagues by default — org owners and enterprise admins can access any repo, and security tooling typically indexes private repo content. So placement is decided by radioactivity, not by repo ownership:

| Material | Home |
|---|---|
| Proposals (sans private zones), decisions, definitions, canon, library, event logs | **Enterprise org private repo** — compliant, durable, synced; contains nothing the author wouldn't defend if read by an admin |
| Private `proposals/*/context/` zones (politics, optics, candid notes) | **Never-remote local overlay** — gitignored out of the workspace repo; optionally its own local-only git repo for history, backed up only to approved encrypted storage |
| Canon, once teams adopt it | **Shared context repo** (org-visible), extracted post-pilot; consumed via submodule or configured sibling path. Canon changes then go through PRs. |

This strengthens the §6 boundary: private context is not merely unreadable by the publish path — it never touches a remote at all. The orchestrator treats a missing overlay gracefully (fresh machine, overlay not restored yet): drafting proceeds without private context rather than failing.

**Residual risk, stated honestly:** the work laptop is company property; any file on it is reachable via device imaging or legal discovery. The mitigation is editorial, not technical — the candid layer should be terse and professional enough to be embarrassing, never damaging.

**Workspace-per-context:** personal projects get a separate workspace on personal infrastructure. Work and personal material never share a repo in either direction.

This resolves former open question Q2.

## 12. Inbound flow (pull model)

Publishing is push. The return path — comments, answers, page edits, stakeholder reactions — is **pull-based and durable**: no daemon, no live sync, no merge. Inbound material lands in the proposal's `inbox/` as discrete items and is triaged at interaction points.

### 12.1 The inbox

An inbox item is anything requiring the author's judgment: a Confluence comment, a pasted Teams reply, Figma comments (design critique happens in Figma, not Confluence — manual paste in v1), a detected page edit, a stale-question nudge. `attach` and `status` drain the inbox: the orchestrator triages each item and proposes the corresponding action — record an answer via `decide`, open a follow-up `question`, revise a section, or dismiss. Triage records **who each item came from and via what channel** (public/private); this provenance is what powers attribution (§ principle 7) and position-consent defaults (§5.2). Triage choices route through `AskUserQuestion`; every resolution is an event. In v1, items arrive manually ("here's what the PM said" pasted into `attach`) — the triage machinery is identical regardless of transport, which is what makes the automated transports below incremental rather than architectural.

### 12.2 On-demand pull (v2: `pull-comments`)

At `attach`/`status`/pre-`publish`, fetch the published page's comments and version via MCP, diff against the recorded state in `.config.yml`, and convert new comments and edit-deltas into inbox items. This is polling at moments the user is already engaged — 80% of "watch the live doc" with zero infrastructure.

### 12.3 The dirty-page guard (v1)

Because `publish` regenerates the page, a human edit made directly on Confluence would be silently clobbered. So `publish` records the page version and content hash after each write. On the next publish, a **version mismatch triggers a content-hash comparison**: if the hash also differs, publish blocks — forcing ingestion of the human's edit as an inbox item (incorporate into source of truth, or consciously discard) before republishing. Version-only bumps with identical content (labels, restrictions, trivial metadata) pass through without blocking. This is optimistic concurrency, and it's the mechanism that makes "markdown is the source of truth" safe rather than rude.

### 12.4 Ambient watching (optional layer, later)

For notification without opening a session, options in ascending order of build cost:

1. **Confluence native page-watch** — email notifications exist today, zero build; lands outside the system but covers the interim.
2. **Scheduled poll** — a cron-driven headless session (same pattern as existing scheduled-task tooling) checks watched pages and writes new inbox items as commits to the workspace repo, optionally posting a digest to a Teams self-chat. Because the workspace is a git repo, the poll's output is durable and auditable — same blackboard philosophy as the engineering orchestrator: events land as artifacts, not notifications.
3. **Webhooks** — require a hosted receiver; explicitly out of scope for a personal tool.

Stale-question nudges are a degenerate case of the same machinery: `status` (or the scheduled poll) flags questions open longer than N days and offers to draft a follow-up via `ask`.

### 12.5 Outbound delivery (`ask`)

The org uses Microsoft Teams, which shapes the delivery options:

- **v1: clipboard, always** — the drafted message is presented, approved, and copied for pasting into Teams, email, or anywhere. Zero integration, works everywhere.
- **v1 optional: place as Confluence comment** — when the proposal has a published page and the question concerns it, `ask` can (with explicit confirmation, since this is a public action) post the drafted question as a page comment. This is often *better* than a DM: the question is durable and visible to other stakeholders, and the answer returns through the same comment-ingestion path as everything else (§12.2) — a closed loop entirely inside the system.
- **Teams API integration: deliberately not planned.** Microsoft Graph can send chat messages but has no draft primitive for chats — integration would mean sending directly on the user's behalf, which violates the never-auto-send rule; it also requires org app registration and admin consent. Clipboard is not a compromise here; it is the correct Teams answer.

## 13. Publish pipeline & rendering

1. Flush event log → regenerate `proposal.md` sections.
2. Render for target (Confluence storage format via MCP; plain markdown for personal/local targets).
3. Rendering rules:
   - **Exec summary block first** (paste-able into Teams): the ask, cost/effort, risk of inaction, decide-by date — three lines. This is the sole audience-variant render in v1; execs consume summaries, not pages.
   - Status banner + per-audience "what I need from you" lines, each a scoped, time-estimated ask (§ principle 8).
   - Frame + approach within the first screen; **Key Assumptions** (§5.4) immediately after — a reader's first question of an agent-assisted proposal is "what was and wasn't considered."
   - Lightweight business-case block where relevant (impact / effort / success metrics for the proposal's subject) — template section, skippable, never mandatory ceremony.
   - Open decisions/questions with assignees, deciders, and decide-by dates; then settled decisions (collapsed), glossary, descoped (collapsed), then the **deep-context pointer block**.
   - **Changes since last publish** (collapsed): derived entirely from the event log — decisions settled, questions opened/closed, scope moved, grouped by publish date. Returning readers are the most important audience.
   - **Attribution:** contributors accumulated via inbox provenance render as "Shaped by: …" — people defend documents with their name on them.
   - **Media:** images from `assets/` render inline; design references pair a living Figma link with a **snapshot captured at decision time** (manual PNG attach in v1), so "the design we approved" survives the file mutating under the link.
   - Length heuristics: long answer sets, settled decisions, and descoped content render inside Confluence expandable sections; short documents render flat.
4. Leak-check gate (§6). Publish blocks on flags.
5. Write page; record publish event with content hash (enables cheap "did a human edit the page since we last published?" detection later, without full sync).

### 13.1 Engineer deep-context handoff

The rendered doc stays short; engineers who want everything get the `handoff/` block: a structured list of links (proposal repo, decision records, research, related repos) formatted so a reader can point their own agent at it and get the full trade-off history. This is a v1 requirement — it is cheap (it's a links block with structure) and it is the answer to "engineers expect large context but Confluence docs must stay small."

## 14. Scope

### v1 (pilot, solo)

- Git-backed workspace (enterprise private repo + never-remote local overlay, per §11)
- Workspace + proposal scaffolding, event log, `init/attach/frame/question/decide/define/assume/evidence/todo/descope/status`
- Assumption records + assumption mining; evidence records with staleness flagging
- Decision rights (`decider` on contested records) + consent-gated position attribution
- One-way idempotent `publish` to Confluence + local targets, with the dirty-page guard (§12.3), reader-cost lint, exec-summary block, and changes-since-last-publish section
- Structural private zone + leak-check verifier (incl. position-consent check) on publish and `ask`
- Consideration files for accounts, login, authentication (self-seeded); transitive resolution
- Definitions with import/promote; catalog generation on publish; term-triggered precedent lookup (§10.2)
- Inbox with manual ingestion + provenance-tracking triage at `attach`/`status` (§12.1); attribution rendering
- Maturity banner; descope bucket; deep-context pointer block; inline images from `assets/` with manual design snapshots
- `handoff` packet export (static markdown — no engineering-orchestrator automation yet)

### v2 (after pilot proves the loop)

- `pull-comments` on-demand ingestion (§12.2); scheduled ambient poll (§12.4)
- Related-proposal import at `init` (§10.2); `library/` distill pass hardening
- Stakeholder load view hardening (per-person ask budgets, cross-proposal); `decide_by`/`blocks` urgency rendering
- Further audience-variant rendering beyond the exec summary (engineer view, design view) — purely a render concern once the data model is stable
- Figma comment ingestion via API; automated design-snapshot capture
- `init --from-existing` wizard hardening for messy source docs
- Shared context repo extraction; team-owned consideration files + staleness workflows; glossary governance via PRs

### Out of scope (deliberate)

- Bidirectional Confluence sync / live merge of human edits
- Auto-sending any communication
- Jira/ticket creation (engineering orchestrator's job)
- Real-time collaboration; multi-user editing of the local repo
- Rovo custom agents as the drafting environment (server-side; cannot hold the private zone). Rovo MCP remains a candidate transport for publish/comment-read.

## 15. Open questions

- **Q1:** ~~Publish transport?~~ **Resolved:** spike both Confluence REST via MCP and Rovo MCP; pick on write fidelity (expands, status macros). Spike is the first implementation task after scaffolding.
- **Q2:** ~~Where does the workspace repo live?~~ **Resolved (§11):** enterprise org private repo for the workspace; private `context/` zones as a never-remote local overlay; shared context repo extracted post-pilot.
- **Q3:** ~~`ask` delivery?~~ **Resolved (§12.5):** clipboard always; optional Confluence-comment placement with confirmation. No Teams API integration (no draft primitive; would violate never-auto-send).
- **Q4:** ~~Handoff packet schema timing?~~ **Resolved:** defer until the first real handoff. The v1 `handoff` command exports readable markdown; schema alignment with the engineering orchestrator happens when a real proposal crosses that boundary.
- **Q5:** ~~Leak-check denylist curation?~~ **Resolved (§6):** hybrid — auto-derived from `context/` frontmatter tags plus manual entries seeded in the skippable `init` configuration flow, editable thereafter.
- **Q6:** ~~Dirty-page guard granularity?~~ **Resolved (§12.3):** version mismatch triggers hash comparison; block only when content actually changed.
- **Q7:** ~~Conflicting precedent definitions?~~ **Resolved (§10.2):** lookup shows all conflicting definitions with provenance; the selection is the tiebreak and immediately prompts promotion to canon.

## 16. Onboarding

**Principle: the tool is never taught; it is encountered — one concept at a time, each at the moment it earns its explanation.** This is a Claude Code plugin, so onboarding targets an agent-mediated experience: the user is never required to memorize commands, because the agent maps natural language to them.

### 16.1 Echo teaching (commands become second nature as a side effect)

When the user expresses intent in natural language ("I'm assuming group admins get email invites"), the orchestrator performs the action *and narrates the mapping*: "Recording that as an assumption → `/plan assume`. A-004 created." Fluency forms by watching one's own intent get translated in context. Narration **decays per-command**: usage counts live in workspace state (`.onboarding.yml`); after N uses of a command, the agent stops explaining it. Slash commands are accelerators for the fluent, never prerequisites for the new.

### 16.2 Lifecycle-gated progressive disclosure

The proposal maturity state machine doubles as the teaching schedule. Concepts are introduced only at the moment their motivation is self-evident: `frame` at init; `question`/`decide` at the first ambiguity; `decider` the first time a decision is contested; `evidence` the first time a quantitative claim appears; assumption mining at the first dry-run; the leak-check and dirty-page guard explained by their **first firing**, not in advance. Teaching a concept one moment before its motivation exists turns it into ceremony.

### 16.3 First run: interview, then real work

On first invocation with no workspace, a multi-step `AskUserQuestion` wizard: repo location + enterprise remote setup → private-overlay setup (with a plain-language explanation of why it never leaves the machine) → Confluence connection test → optional first consideration file. Then, instead of a demo tutorial, the wizard asks for **something small and real the user currently needs alignment on** and runs the first proposal on it — real work teaches value, and value drives session two. A throwaway sandbox proposal is offered only as fallback.

### 16.4 Configuration by observation

Per-proposal config is interview-based and skippable (§7.2). Above that, the orchestrator observes patterns across proposals — a template section skipped three times, a constant publish space, a recurring audience set — and *proposes* configuration changes via `AskUserQuestion` rather than waiting for the user to discover a settings file. Config debt surfaces in `status` like every other staleness. `.config.yml` is never hand-edited.

### 16.5 Plugin mechanics

- **SKILL.md as progressive disclosure for the agent:** a light top-level skill; deep protocol docs (leak-check, render rules, record schemas) in `references/`, loaded only when relevant. The agent's context economy mirrors the human's learning curve.
- **SessionStart hook:** rehydration for returning users — "3 inbox items on invitations-flow; one contested decision unowned." Re-engagement is the forgotten half of onboarding.
- **`/plan help`:** one-screen command map grouped by lifecycle stage, annotated with the user's own usage ("you haven't used `descope` yet — it captures out-of-scope ideas without losing them").
- **`/plan tour`:** opt-in guided walkthrough on a scratch proposal, for users who explicitly want it. Never forced.

### 16.6 Reader onboarding (the audience that never installs anything)

For an alignment tool, the most important audience only ever receives documents. The rendered page onboards them: a short footer explains how to engage ("comment on this page — comments flow into the author's workflow; you need no tooling"), and the document's fixed shape (exec summary → banner → asks → assumptions) teaches readers where their part lives. If the doc reads as a machine artifact requiring special knowledge, adoption dies at the first stakeholder. Later, teammate adoption routes through consideration files — "your knowledge keeps getting cited in my proposals; want to own the file?" is a stronger onramp than any tutorial.

## 17. Success criteria (pilot)

- Two real proposals (candidate: invitations flow revival) drafted and published through the system end-to-end.
- A stakeholder reads a published doc cold and can state the problem, approach, maturity, and their asked contribution without a walkthrough.
- At least one "call avoided": a consideration file surfaces a realm/channel constraint before review instead of during it.
- Zero private-context leaks (verified by manual audit of published pages against `context/`).
- Attention test: three concurrent proposals maintained without the tool demanding mid-flow context switches.
