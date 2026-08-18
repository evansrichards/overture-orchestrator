# The public/private boundary and the leak-check verifier

Two mechanisms, layered. The first prevents leaks; the second catches what
prevention cannot — inference.

## 1. Structural separation

Private material lives **only** in `proposals/<slug>/context/`. The publish
pipeline cannot read it.

- **Structural, not behavioral.** The private zone is unreachable by the publish
  path, not filtered out of it. Filtering fails silently; unreachability does not.
- **No inline privacy tagging exists.** There is deliberately no "mark this
  paragraph private" mechanism in publishable files. Mixing zones inside one file
  is the failure mode this design exists to prevent. If asked for inline tagging,
  explain the zone and decline to add it.
- Private context **may** inform drafting locally. The boundary applies to
  anything that leaves the repo — rendered pages, outbound drafts, subagent
  briefs, `catalog.jsonl`, and the handoff packet.

### The denylist for the publish path

When running `publish`, `ask`, or catalog generation, treat these as unreadable:

```
planning/proposals/*/context/**
```

Do not `cat`, `grep`, `Read`, glob, or otherwise open anything under that path
while on those paths, and do not carry summaries of it forward from earlier in
the session into a rendered artifact.

### Git enforcement

`planning/proposals/*/context/` must be gitignored (`workspace.md` → Git
topology). Verify before a proposal's first publish:

```bash
git check-ignore -q planning/proposals/<slug>/context && echo IGNORED || echo "NOT IGNORED — STOP"
```

If it is not ignored, stop and fix `.gitignore` before writing anything private
there. This check is cheap; the failure is unrecoverable once pushed.

## 2. The leak-check verifier

**The drafting agent never verifies its own output.** Before *any* publish or any
outbound `ask`, a **separate agent session** reviews the rendered output.

### What the verifier receives — and only this

1. The **rendered artifact** (the exact text about to be published or sent).
2. A **topics/names denylist** — a list of subjects and people, *never the
   private content itself*.

Passing private content to the verifier would defeat the entire design. If you
cannot construct the brief without quoting the private zone, the answer is a
better denylist entry, not a looser brief.

### The denylist is hybrid

| Source | How |
|---|---|
| Auto-derived | Frontmatter `tags:` on files in `proposals/<slug>/context/` — **the tags only, never the bodies** |
| Manual | Entries seeded during the skippable `init` configuration step, editable any time |

Merge `.config.yml` → `leak_denylist` with the tag-derived set at run time.

Private context files should therefore carry tags:

```yaml
---
tags: [reorg, vendor-negotiation, headcount, <person-name>]
---
```

### What the verifier flags

1. **Direct leaks** — denylisted topics or names appearing in the output.
2. **Inferable leaks** — phrasing that implies a denylisted topic without naming
   it ("this phrasing implies the reorg"). This is the harder and more valuable
   half; a verifier that only string-matches is not doing its job.
3. **Unconsented named positions** — any named position lacking a consent basis
   (`records.md` → Positions and consent).

### Verifier brief (use this shape)

> You are a leak-check verifier. You are given (a) a document about to be
> published, and (b) a denylist of topics and names. You have **not** been given
> the private material behind that denylist, and you must not ask for it.
>
> Flag every place the document (1) names or describes a denylisted topic or
> person, (2) implies one strongly enough that an informed reader would infer it,
> or (3) attributes a position to a named person without stating a public basis
> for that attribution.
>
> Return **structured data only** — do not attempt to ask the user anything.
> For each flag: `{id, severity: high|medium|low, kind: direct|inferred|consent,
> quote, why, suggested_rewording}`.
>
> Return an empty list if the document is clean. Do not soften a real flag, and
> do not invent flags to appear thorough.

### Resolving flags — main session only

`AskUserQuestion` is unavailable in subagents, so the verifier returns flags as
data and the **main session** presents resolution options, one question per flag
(batched up to 4 per call):

| Option | Meaning |
|---|---|
| **Rephrase (Recommended)** | Apply the verifier's `suggested_rewording` — put the actual proposed text in the option description so the user can judge it without asking |
| **Remove** | Drop the passage |
| **Override with justification** | Publish as-is; the justification is recorded on the `leakcheck.resolved` event |

**Publish blocks on unresolved flags.** Append `leakcheck.flagged` when flags come
back and `leakcheck.resolved` per resolution. If the user abandons mid-resolution,
publish does not proceed — record `publish.blocked` and leave the queue intact.

## Cross-proposal contamination

`catalog.jsonl` indexes publishable artifacts only — settled records,
definitions, descoped items. It **never** indexes any `context/` zone.

The reason is subtle and worth holding onto: cross-proposal retrieval that
surfaced proposal A's private notes inside proposal B's drafting session would
never leave the machine — but it can be paraphrased into B's public doc in ways
the leak-checker cannot trace, because B's denylist is derived from B's private
zone, not A's. Keep the catalog clean at generation time.
