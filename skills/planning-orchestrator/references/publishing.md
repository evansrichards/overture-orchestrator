# Publish pipeline, rendering, and handoff

**Short documents, deep context.** The rendered artifact answers *"what problem,
what approach, how far along, what do you need from me"* within one screen.
Everything else is reachable, not present.

## Pipeline

1. **Flush the event log** → regenerate `proposal.md` sections from records.
2. **`--dry-run` only:** run assumption mining (`records.md`).
3. **Dirty-page guard** (below). Blocks if a human edited the page.
4. **Render for target** — Confluence storage format via MCP; plain markdown for
   local/personal targets.
5. **Reader-cost lint** (below). Warns.
6. **Leak-check gate** (`privacy.md`). **Blocks.**
7. **Write the page.**
8. Regenerate `catalog.jsonl` and `planning/index.md`.
9. Append `publish.completed` with the page version and content hash.

Publish is **idempotent**: re-publishing fully regenerates the page. Never
attempt a partial or diff-based page update.

## The dirty-page guard

Because `publish` regenerates the page, a human edit made directly in Confluence
would be silently clobbered. That would make "markdown is the source of truth"
rude rather than safe.

After each write, record the page version and a content hash in `.config.yml`
(`publish.last_published`). On the **next** publish:

```
fetch current page version
   │
   ├─ version == last_published.page_version ──────────▶ proceed
   │
   └─ version differs
          │
          ├─ content_hash == last_published.content_hash ──▶ proceed
          │     (labels, restrictions, trivial metadata — not a content edit)
          │
          └─ content_hash differs ──▶ BLOCK
                 append `dirtypage.detected`
                 create an inbox item containing the human's edit
                 require triage: incorporate into source of truth,
                                 or consciously discard
                 then republish
```

This is optimistic concurrency. Do not offer a "force publish" that skips
triage — the whole value is that the human's edit cannot vanish silently.

## Reader-cost lint

**Reader cost is a budget.** This tool makes producing proposals cheap; it must
not export the cost to reviewers.

Warn (do not block) when:

- any audience's ask is **unscoped** — missing a concrete ask or a time estimate,
- any one person's **outstanding asks across all proposals** exceed
  `reader_cost.ask_cap_per_person`.

Report the warning with the person's name and their current outstanding count, so
the decision to send anyway is informed.

## Render order

The shape is fixed. Readers learn where their part lives by the document always
looking the same.

1. **Exec summary block** — first, paste-able into Teams, **three lines**: the
   ask, cost/effort, risk of inaction, decide-by date. This is the *only*
   audience-variant render in v1; execs consume summaries, not pages.
2. **Status banner** — maturity state plus per-audience "what I need from you"
   lines, each a **scoped, time-estimated ask**
   (e.g. *"PMs: sign-off on §3 scope — 10 min. Design: unresolved question Q-004 —
   15 min."*). This is the ten-second orientation requirement.
3. **Frame + approach** — within the first screen.
4. **Key Assumptions** — immediately after. A reader's first question of an
   agent-assisted proposal is *"what was and wasn't considered."*
5. **Business-case block** — impact / effort / success metrics, where relevant.
   Template section, **skippable, never mandatory ceremony.**
6. **Open decisions and questions** — with assignees, deciders, decide-by dates.
   Contested definitions render **here**, not in the glossary.
7. **Settled decisions** — collapsed.
8. **Glossary** — settled definitions, compact, with first-use markers.
9. **Descoped** — collapsed, with revival triggers.
10. **Deep-context pointer block** (§ Handoff packet).
11. **Changes since last publish** — collapsed.
12. **Attribution** — "Shaped by: …".
13. **Reader footer** (§ Reader onboarding).

### Maturity banner

`draft → socializing → in-review → decided (approved | rejected | shelved) → superseded`

**Publish early, at `socializing`.** A polished doc that arrives fully-formed
reads as a fait accompli and produces resistance, not alignment. Open questions
assigned to named people are **deliberate seams, not gaps** — alignment is
co-authored.

### Changes since last publish

Derived **entirely from the event log**, grouped by publish date: decisions
settled, questions opened and closed, scope moved, assumptions invalidated.
Returning readers are the most important audience and the easiest to lose.

### Attribution

Contributors accumulated from inbox provenance (`inbound.md`) render as
**"Shaped by: …"**. People defend documents with their name on them.

Subject to consent (`records.md` → Positions and consent): contribution via a
public channel may be credited by name; private-channel contribution needs
consent. When in doubt, ask before crediting — being named unexpectedly is its
own kind of leak.

### Media

- Images from `assets/` render inline.
- Design references pair a **living Figma link** with a **snapshot captured at
  decision time** (manual PNG attach in v1), so *"the design we approved"*
  survives the file mutating under the link. Never rely on the link alone for a
  decision record.

### Length heuristics

Long answer sets, settled decisions, and descoped content render inside
Confluence **expandable sections**. Short documents render flat — do not wrap a
five-line section in an expand.

## Reader onboarding

The most important audience never installs anything. The page onboards them:

- A short **footer** explains how to engage: *"Comment on this page — comments
  flow into the author's workflow. You need no tooling."*
- The **fixed shape** (exec summary → banner → asks → assumptions) teaches
  readers where their part lives.

If the doc reads as a machine artifact requiring special knowledge, adoption dies
at the first stakeholder. Render for a human who has never heard of this system.

## Handoff packet

### Deep-context pointer block (every publish, v1)

The rendered doc stays short; engineers who want everything get a **structured
list of links** — proposal repo, decision records, research, related repos —
formatted so a reader can point their own agent at it and get the full trade-off
history. Cheap to build, and it is the answer to *"engineers expect large context
but Confluence docs must stay small."*

Sourced from `proposals/<slug>/handoff/`.

### `handoff` export (approved proposals)

Readable markdown containing:

- the frame and final approach,
- **settled decisions** with their context and consequences,
- **constraints** surfaced from consideration files,
- **settled definitions**,
- **validated / accepted-risk assumptions**, and any still open,
- links back to the proposal repo.

Excludes: private context, contested positions, and anything unsettled beyond a
short "still open" list.

Schema alignment with downstream engineering tooling is **deliberately deferred**
until a real proposal crosses the boundary. Do not invent one now.

## Local target

When `publish.target: local`, render plain markdown into
`.workspace.yml` → `publish.local.dir`. The leak-check still runs — "local" means
a different render target, not a lower bar. The dirty-page guard does not apply.
