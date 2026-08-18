---
name: planning-orchestrator
description: >-
  Use when drafting, aligning on, or publishing a proposal of any kind — product,
  design, engineering, project, or organizational — and when working with a
  `planning/` proposal workspace. Triggers on "write/draft a proposal", "I need
  alignment on…", "log a decision / assumption / open question", "what's the
  status of <proposal>", "publish this to Confluence", "socialize this", "who
  decides this", "cut this from scope but don't lose it", "hand this off to
  engineering", and on any `/overture …` command. Keeps markdown in a git repo
  as the source of truth, keeps private context structurally unpublishable, and
  batches every question to the user through `AskUserQuestion`. Not for
  engineering execution — tickets, sprints, deploys, code review, or ADRs
  inside a codebase — and not for summarizing or reformatting a document that
  isn't a proposal.
---

# Planning orchestrator

A proposal workspace for speculative, cross-functional work — proposals that may
never ship, or never even be sent. Its job is to get stakeholders aligned faster
and with better discussion, and to leave a durable record of the problem, the
reasoning, the decisions, and the open questions.

It is the **upstream sibling** of engineering workflow tooling. When a proposal
is approved and becomes engineering work, it hands off downstream (`handoff`).
Small technical tasks skip planning entirely.

**Not** a project manager, ticket system, or knowledge base. It does not track
execution. It does not replace conversations — it raises their floor.

## The loop

```
init ──▶ frame ──▶ draft ⇄ question / decide / define / assume / evidence / descope
                    │
                    ├──▶ status ────────── drain queued questions, drain inbox
                    ├──▶ ask ───────────── leak-check ▶ draft ▶ human sends
                    ├──▶ publish ───────── flush ▶ render ▶ leak-check ▶ write
                    └──▶ handoff ───────── approved proposals only
```

## Before anything else

1. **Find the workspace.** Walk up the directory chain — cwd, then its parent,
   and so on to the filesystem root — checking each level for
   `planning/index.md`. This is a parent walk, not a search: never `find` across
   the filesystem for it. If no workspace turns up and the user is asking for
   planning work, run the first-run wizard — `references/onboarding.md`
   §First run. Never scaffold a workspace silently.
2. **Attach if a proposal is in play.** `references/commands.md` → `attach`.
   Never edit proposal files without loading the proposal's current state first.
3. **Read the private zone only for drafting.** `proposals/<slug>/context/` may
   inform your thinking locally. It must never reach a rendered artifact, an
   outbound draft, a subagent brief, or the catalog.

## Non-negotiables

These hold no matter which reference doc is loaded. Violating one is a defect,
not a judgment call.

| # | Invariant |
|---|---|
| 1 | **Markdown in the repo is the source of truth.** Confluence is a render target. Publishing is one-way and idempotent. Never treat the page as authoritative; ingest human page edits as inbox items instead (`references/inbound.md`). |
| 2 | **The private zone is structurally unreachable from the publish path.** Not filtered — unreachable. `proposals/*/context/` is never read, quoted, paraphrased, summarized, or passed to a subagent during `publish`, `ask`, or catalog generation. |
| 3 | **The drafting agent never verifies its own output.** Every `publish` and every `ask` goes through the leak-check verifier subagent first (`references/privacy.md`). Publish blocks on unresolved flags. |
| 4 | **Never auto-send anything.** `ask` drafts and hands to the human. The single exception is placing a Confluence page comment, which requires explicit per-instance confirmation. |
| 5 | **Every question to the user goes through `AskUserQuestion`** — batched, never as free-text interrogation — except genuinely open questions where enumerating options would anchor the user (`references/interaction.md`). |
| 6 | **Never attribute a named position without a consent basis.** Attributing "Sarah opposes this" before Sarah has said so publicly is position-laundering; it burns candor exactly once. |
| 7 | **Nothing is deleted during scope negotiation.** Cutting scope means `descope`, which moves content to `descoped.md` with the decision that removed it and a revival trigger. |
| 8 | **Every state change appends an event** to `proposals/<slug>/.events.jsonl` before you report it as done. `publish` and `status` are the flush points. |

## Which reference to load

Load only what the task needs. This table is the routing layer; the references
hold the executable protocol.

| Doing this | Load |
|---|---|
| Any `/overture` subcommand — exact procedure, flags, preconditions | `references/commands.md` |
| Creating/updating a decision, question, definition, assumption, evidence, descope entry | `references/records.md` |
| Scaffolding, file layout, `.config.yml`, event-log format, git/private-overlay setup | `references/workspace.md` |
| Asking the user anything; batching a question queue; interview design | `references/interaction.md` |
| Anything crossing the public boundary — `publish`, `ask`, the verifier brief, denylist | `references/privacy.md` |
| Rendering the artifact, Confluence write, dirty-page guard, reader-cost lint, handoff packet | `references/publishing.md` |
| Inbox triage, provenance, attribution, comment ingestion, outbound delivery | `references/inbound.md` |
| Consideration files, glossary, precedent lookup, `catalog.jsonl`, `library/` | `references/context-and-catalog.md` |
| First run, teaching a concept, `/overture help`, `/overture tour`, narration decay | `references/onboarding.md` |

Record and document templates live in `references/templates/`.

## Echo teaching

The user is never required to memorize commands — map their natural language to
the action, perform it, and narrate the mapping once:

> Recording that as an assumption → `/overture assume`. **A-004** created.

Narration **decays**: usage counts live in `planning/.onboarding.yml`. After the
threshold (default 3 uses), stop explaining that command. Slash commands are
accelerators for the fluent, never prerequisites for the new. Details and the
lifecycle-gated teaching schedule are in `references/onboarding.md`.

## Scope discipline (v1)

Build and operate the v1 surface only. If the user asks for something in the
deferred column, say it is deferred and offer the v1 path.

| v1 — in scope | Deferred (v2) |
|---|---|
| Git workspace + never-remote private overlay | Automated comment pull (`pull-comments`) |
| `init attach frame question decide define assume evidence todo descope ask status publish handoff help tour` | Scheduled ambient poll; webhooks |
| Assumption records + mining; evidence staleness | Related-proposal import at `init` |
| Decision rights; consent-gated attribution | Audience-variant renders beyond the exec summary |
| Idempotent publish + dirty-page guard + reader-cost lint | Figma comment ingestion; auto design snapshots |
| Leak-check verifier on publish and `ask` | Shared context repo extraction; team-owned files |
| Manual inbox ingestion + provenance triage | Handoff schema alignment with engineering tooling |
| Definitions import/promote; catalog + precedent lookup | |

**Permanently out of scope:** bidirectional Confluence sync, auto-sending any
communication, ticket creation, real-time collaboration, and server-side agent
environments that cannot hold the private zone.
