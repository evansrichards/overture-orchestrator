# Consideration files, canon, precedent, and the library

Past work informs new proposals through **three distinct mechanisms with
different loading behavior**. Conflating them is the primary rot vector for
systems like this, so keep the distinction structural.

| Mechanism | Loading | Holds |
|---|---|---|
| **Canon** | Always loaded, per tags | What the workspace has *committed to* |
| **Precedent** | Retrieved on demand, **never** auto-loaded | Everything that ever settled anywhere |
| **Library** | Retrieved like precedent | Distilled external / historical docs |

---

## Consideration files (canon)

Lightweight markdown owned by teams and domains, holding the considerations that
otherwise require *"get an engineer on a call."*

**Format: bare lists.** Do's and don'ts, "in case of X, ask <person>",
constraints, realm/channel implications. Deliberately low-ceremony so they
actually get maintained. Resist turning them into documents.

```markdown
---
owner: <person/role>
last_reviewed: 2026-07-02
implicates: [accounts, login]        # apps/services this domain touches
tags: [authentication, sso]
---

# Authentication

## Constraints
- Provider-realm accounts cannot use account codes.
- SSO sessions do not survive a realm switch.

## In case of…
- Anything touching group-admin invites → ask <person>.

## Proposals here usually forget
- The group-admin realm.
- That deprecating a flow needs a provider-realm migration path.
```

That last section is what sharpens the assumption miner (`records.md`).

### Resolution — transitive

When `init` (or a later edit) tags apps or domains:

1. Load the tagged files.
2. Load domain files implicated by those apps, and app files implicated by those
   domains — e.g. a proposal touching the **login app** also pulls
   `domains/authentication.md`. Domain files know which apps/services they
   implicate via `implicates:`.
3. Follow transitively; stop at cycles.

### Effect

- Considerations are **injected during drafting**.
- The review pass **annotates the proposal with unaddressed considerations** —
  *"this doesn't address the group-admin realm."* This is the "call avoided"
  mechanism; run it, don't just load the files.

### Governance and cold start

Seeded firsthand for accounts, login, and authentication. **Team ownership comes
later, after the value is demonstrated** — do not propose team ownership during
the pilot. Each file has an `owner` and `last_reviewed`; flag files stale beyond
`staleness.consideration_file_days` rather than trusting them silently.

Business context — objectives and non-objectives — lives in
`planning/context/business.md`: same mechanism, no special machinery.

---

## Precedent — `catalog.jsonl`

Everything that ever settled in any past proposal — definitions, decisions,
descoped items — indexed in `planning/catalog.jsonl`, **regenerated on every
publish** from record frontmatter.

At pilot scale, lookup is a `grep` over this file. **No retrieval
infrastructure** — if you are reaching for embeddings, the pilot has not proven
enough yet.

```json
{"id":"DEF-002","proposal":"invitations-flow","type":"definition","term":"invitation","state":"settled","date":"2026-03-14","tags":["accounts","authentication"],"summary":"A pending grant of access to an account, addressed to an email.","path":"proposals/invitations-flow/decisions/DEF-002-invitation.md"}
```

**Privacy rule:** the catalog indexes **publishable artifacts only** — settled
records, definitions, descoped items, library entries. It **never** indexes any
`context/` zone (`privacy.md` → Cross-proposal contamination).

### Term-triggered lookup

When a proposal uses or `define`s a term with no canonical entry, grep the
catalog. On a hit, ask:

> *"You defined **invitation** in `invitations-flow` (settled 2026-03) as X."*
> **Import (Recommended)** / **Redefine here** / **Ignore**

- **Import** records provenance and links — never duplicates.
- **Redefine** records an explicit **divergence note** saying what differs and
  why (`definition.diverged`).
- A **second import** of the same definition triggers the **promotion prompt** —
  repeated reuse is the evidence that a term belongs in canon.

Users never retype a definition. They either import it or deliberately diverge.

### Conflicting precedents

When past proposals settled **different** definitions for the same term, present
**all of them** with proposal names and dates. The user's selection is recorded as
the **tiebreak** and **immediately triggers the promotion prompt**.

A conflict surfacing is exactly the moment canon should absorb the term, so the
conflict never recurs. Do not quietly pick the most recent one.

### Related-proposal import at `init` (v2)

The new proposal's app/domain/realm tags are matched against `index.md`; related
proposals are offered via `multiSelect`. Importing brings in their settled
definitions and surfaces their decisions **as precedent, not constraint** —
rendered to the drafting agent with explicit framing that *a past decision
informs but does not bind*.

Without that framing, old decisions exert silent gravity on proposals that should
be free to re-litigate them. If you implement any part of this early, keep the
framing.

---

## Library — distilled external docs

Pre-orchestrator proposals, existing Confluence pages, and other historical docs
enter through a **distill pass** (`init --from-existing` uses the same machinery):

1. Read the source.
2. Extract **decisions, definitions, and constraints** into standard record
   format under `planning/library/<source-slug>/`.
3. Record the source URL, retrieval date, and original author.
4. Index in the catalog like everything else.

**Distill, don't dump.** Raw historical docs are the main source of stale,
contradictory context — pasting one into the workspace imports its rot. If a
source is too messy to distill confidently, extract what is clear, and list what
you could not resolve as open questions rather than guessing.
