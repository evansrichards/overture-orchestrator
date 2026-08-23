# Records: decisions, assumptions, evidence, definitions, descope

**Decisions are the atomic unit.** Questions, definitions, and scope changes are
all decision-shaped: proposed → contested → settled. One lifecycle, many views.
Resist adding a second state machine for anything.

## Decision records

One file per record in `proposals/<slug>/decisions/`. Frontmatter is the
contract; the body is prose context.

```yaml
---
id: D-007
title: Invitation acceptance requires no account code
state: proposed          # proposed | contested | deferred | settled | superseded
type: decision           # decision | definition | scope-change | question-resolution
decider: <person/role>   # REQUIRED once contested
assignee: <person/role>  # for open questions
positions:               # only while contested
  - holder: <person/role>
    summary: ...
    provenance: public          # public | private
    consent_to_attribute: false
decided_by: null
decided_on: null
decide_by: 2026-09-01           # optional deadline; drives nudges + render urgency
blocks: [D-004]                 # decisions gated on this one
rests_on: [A-002, A-003]        # assumptions this decision depends on
supported_by: [E-001]           # evidence citations
pending: null                   # only when state=deferred: the assumption under test
supersedes: null
contributed_by: []              # accumulated from inbox provenance
tags: [accounts, authentication]
---

## Context
Why this is being decided; what forced it.

## Options considered
- **A — …** …
- **B — …** …

## Choice
…

## Consequences
…
```

Template: `templates/decision.md`.

### The four types

| Type | Prefix | Is | Renders in |
|---|---|---|---|
| `decision` | `D-` | A committed choice | Open decisions, then settled (collapsed) |
| `question-resolution` | `Q-` | An open question — a decision in `proposed` with an **assignee** | Open questions with assignee, decider, decide-by |
| `definition` | `DEF-` | A term's meaning (§Definitions below) | Contested → open questions area; settled → glossary |
| `scope-change` | `SC-` | A descope, whose payload moves content to `descoped.md` | Descoped (collapsed) |

A decision **"resolved by experiment"** is not new machinery: set
`state: deferred` and point `pending` at the assumption under test.

### State transitions

```
proposed ──▶ contested ──▶ settled ──▶ superseded
    │            │            ▲
    └────────────┴──▶ deferred┘        (deferred requires `pending: A-###`)
```

Rules, enforced on every write:

- Entering `contested` **requires a `decider`**. If none is set, ask via
  `AskUserQuestion` with options drawn from the audience list ("Who settles
  this?"). A contested record without a decider is **unowned** and `status`
  flags it. This is the minimum viable slice of DACI — a decider per contested
  decision, and no more. Do not build a full RACI.
- Entering `settled` **requires** either ingested input from the decider (inbox
  provenance) or an explicit `decided_by` plus a note of the form
  `decided in <meeting>, <date>`. Never settle on the drafting agent's own
  judgment.
- `superseded` requires the superseding record to set `supersedes: <old-id>`.
  When recording a decision that conflicts with an earlier one, prompt for
  supersession rather than silently contradicting the record.
- Every transition appends `decision.state_changed` (plus `decision.settled` /
  `decision.superseded` where applicable).

### Positions and consent

`positions` exists only while `contested`. `provenance: public` means the
position arrived through a public channel (a page comment, a group thread) —
those may be attributed by name. `provenance: private` renders **anonymized**
("one reviewer holds…") unless `consent_to_attribute: true`.

The leak-check verifier independently flags any named position lacking a consent
basis. Attributing a position someone has not taken publicly is
position-laundering; it burns candor exactly once.

## Assumption records

A proposal's assumptions are its load-bearing walls. In agent-assisted drafting,
the sharpest question a reader has is *"what has and hasn't been considered."*
So assumptions are first-class records, never a prose section.

One file per record in `proposals/<slug>/assumptions/`:

```yaml
---
id: A-003
statement: Group admins receive invitations by email
state: stated       # stated | validating | validated | invalidated | accepted-risk
criticality: ...    # what breaks if this is wrong
test: ...           # how it will be / was validated (plan, experiment, evidence link)
owner: <person/role>
supported_by: [E-002]
---
```

Rendered as **Key Assumptions**, near the top of the doc.

**The live-assumption mechanism:** because decisions declare `rests_on`, an
assumption flipping to `invalidated` automatically flags every dependent decision
for review. On any `assumption.state_changed` to `invalidated`, walk the
decisions whose `rests_on` includes that ID and surface them at the next
interaction point. This is what keeps assumptions live instead of ritual — do not
skip it.

### Assumption mining

Runs on demand (`assume --mine`) and automatically during `publish --dry-run`.

1. Read `proposal.md` and the settled decisions.
2. Load the consideration files matching the proposal's tags — they sharpen the
   miner by teaching it which assumptions proposals in that territory tend to
   hide (`context-and-catalog.md`).
3. Surface **implicit** assumptions the text depends on but never states — e.g.
   *"this assumes the account-code flow can be deprecated for the provider
   realm."* Existing `A-` records are not candidates; skip anything already
   stated.
4. Present candidates via `AskUserQuestion` with `multiSelect: true`:
   **record / reject / already covered**.
5. Recorded candidates become `A-` records with `state: stated`; append
   `assumption.mined`.

The author cannot see their own water. The miner exists to see it for them — so
bias toward surfacing a candidate that might be obvious over staying silent.

## Evidence records

Quantitative claims rot silently in long-lived docs. Any load-bearing claim
("38% of invites expire") is an evidence record. Sections in
`proposals/<slug>/evidence.md`:

```markdown
### E-001 — 38% of invitations expire unaccepted
- **Source:** <query or dashboard link>
- **Pulled:** 2026-08-04
- **Owner:** <person/role>
- **Note:** rolling 90-day window, provider realm excluded
```

Decisions and assumptions cite evidence via `supported_by`. `status` flags
evidence older than `staleness.evidence_days` **that is still cited by an active
(non-settled, non-superseded) decision** — stale evidence under a dead decision
is noise, not a finding.

This is what gives data science a reason to trust — and contribute to — these
documents. When a claim appears in drafting with no evidence record, offer to
create one rather than letting the number float.

## Definitions

Definitions are decision records with `type: definition` and a two-tier scope.

**1. Proposal-local.** `define <term>` creates an entry in `definitions.md`
backed by a `DEF-` record. States: proposed → contested → settled. Competing
definitions render side by side with holders named.

**2. Durable / canonical.** On `define`, **before** creating anything:

1. Check `planning/context/glossary.md` and the loaded consideration files.
   - **Canonical hit** → **import** (link, don't duplicate) and lint the proposal
     for usage inconsistent with the canonical meaning.
2. No canonical entry → check `catalog.jsonl` for precedent
   (`context-and-catalog.md` → term-triggered lookup).
3. Neither → create a new local definition.

When a local definition settles and looks durable, `decide` prompts to **promote**
it to `planning/context/glossary.md`. A second import of the same definition also
triggers the promotion prompt — repeated reuse is the evidence that a term
belongs in canon.

**Rendering:** contested definitions render in the **open-questions area**, not an
appendix — an unsettled definition blocks downstream decisions. Settled
definitions render as a compact glossary with first-use markers; long glossaries
use Confluence expands.

**Anti-goal — no terminology policing.** The lint fires only when (a) the proposal
contradicts its own settled definition, or (b) it contradicts a canonical one.
Casual synonyms pass untouched. The purpose is catching **false agreement**, not
style enforcement. If you are about to flag a wording preference, don't.

## The descope bucket

Nothing is deleted during scope negotiation. `descope` performs, in order:

1. Create an `SC-` scope-change record capturing the reason.
2. Move the content verbatim into `descoped.md` under that record's ID.
3. Ask (via `AskUserQuestion`, as a follow-up step) **what would trigger
   revival** — record it on the entry.
4. Append `descope.moved`.

```markdown
### SC-002 — Bulk invitation import
- **Removed:** 2026-08-11 · **Reason:** no validated demand in provider realm
- **Revival trigger:** a provider asks for >50-seat onboarding
- **Content:** <the moved section, verbatim>
```

Descoped items can seed new proposals: `init --from-descoped <id>` carries the
content and the revival trigger into the new proposal's frame, and appends
`descope.revived`.
