# Overture

**A proposal workspace for speculative, cross-functional work** — proposals that
may never ship, or never even be sent.

Overture is a Claude Code plugin for drafting, aligning on, and publishing
proposals of any kind: product, design, engineering, project, or organizational.
It exists to get stakeholders aligned faster and with better discussion, and to
leave a durable, readable record of the problem, the reasoning, the decisions,
and the open questions.

It is the **upstream sibling** of engineering workflow tooling. When a proposal
is approved and becomes engineering work, it hands off downstream. Small
technical tasks — maintenance, security bumps, tweaks — skip planning entirely.

**Not** a project manager, a ticket system, or a knowledge base. It does not
track execution. It does not replace conversations — it raises their floor.

## Install

```bash
/plugin marketplace add evansrichards/overture-orchestrator
/plugin install overture-orchestrator@overture
```

The repo is its own marketplace, so the two commands are all it takes.

## Use

You never have to memorize a command. Say what you mean —

> *"I'm assuming group admins get invitations by email."*

— and the agent records it and narrates the mapping (`→ /overture assume. A-004
created.`). Narration decays once you're fluent. The slash commands are
accelerators, not prerequisites.

| Stage | Commands |
| ----- | -------- |
| **Start** | `/overture init` · `/overture attach <slug>` · `/overture frame <statement>` |
| **Build** | `/overture question` · `decide` · `define` · `assume` · `evidence` · `todo` · `descope` |
| **Align** | `/overture ask <person>` · `/overture status` · `/overture publish [--dry-run]` |
| **Finish** | `/overture handoff` |
| **Meta** | `/overture help` · `/overture tour` |

Global flag `--now` asks queued questions immediately instead of batching them
to the next interaction point.

## The five ideas

1. **Markdown in a git repo is the source of truth. Confluence is a render
   target.** Publishing is one-way and idempotent — no bidirectional-sync
   tarpit. A dirty-page guard means a human's direct page edit can never be
   silently clobbered.
2. **Structural privacy, not behavioral privacy.** Candid notes live in a
   private zone the publish path *cannot read* — unreachable, not filtered. A
   separate verifier session leak-checks every outbound artifact against a
   topics/names denylist, and never sees the private material itself.
3. **Decisions are the atomic unit.** Questions, definitions, and scope changes
   are all decision-shaped: proposed → contested → settled. One lifecycle, many
   views.
4. **Attention is the scarce resource.** Commands queue and batch; questions
   reach you through `AskUserQuestion` in 1–3 grouped steps, so several
   proposals can run concurrently without context-switching.
5. **Reader cost is a budget.** Making proposals cheap to write must not export
   the cost to reviewers. Every publish states a scoped, time-estimated ask per
   audience, and warns when one person's outstanding asks pile up.

## Layout

```
.claude-plugin/
  marketplace.json               # makes this repo directly installable
  plugin.json                    # the plugin manifest
skills/
  planning-orchestrator/
    SKILL.md                     # light top-level skill: invariants + routing
    references/                  # deep protocol, loaded only when relevant
      workspace.md               #   layout, config, event log, git topology
      records.md                 #   decisions, assumptions, evidence, definitions
      commands.md                #   per-subcommand procedures
      interaction.md             #   AskUserQuestion protocol and batching
      privacy.md                 #   private zone + leak-check verifier
      publishing.md              #   render order, dirty-page guard, handoff
      inbound.md                 #   inbox, triage, outbound delivery
      context-and-catalog.md     #   consideration files, canon, precedent
      onboarding.md              #   echo teaching, first run
      templates/                 #   record and document templates
commands/
  overture.md                        # the /overture dispatcher
hooks/
  hooks.json                     # SessionStart rehydration (auto-loaded)
  planning-rehydrate.sh
docs/
  spec.md                        # the source specification
```

`SKILL.md` is deliberately light (~230 tokens always-on). The references are
progressive disclosure for the agent: its context economy mirrors the human's
learning curve.

## The workspace it manages

Overture operates on a `planning/` directory in a git repo of your choosing —
separate from this one. That workspace holds proposals, decision records,
assumptions, evidence, a glossary, and shared consideration files. `/overture init`
scaffolds it and walks you through setup.

Placement is decided by radioactivity, not repo ownership:

| Material | Home |
| -------- | ---- |
| Proposals, decisions, definitions, canon, event logs | Enterprise org **private repo** |
| Private `context/` zones — politics, optics, candid notes | **Never-remote local overlay**, gitignored |

See [`docs/spec.md`](docs/spec.md) §11 for the full reasoning, including the
residual risks it does *not* solve.

## Hooks

One hook, auto-loaded from `hooks/hooks.json`:

| Event | What it does |
| ----- | ------------ |
| `SessionStart` | Reports pending inbox items and unowned contested decisions across a `planning/` workspace. |

It is **silent by default** — no output, exit 0 — unless a `planning/index.md`
workspace exists in or above the working directory *and* something is actually
pending. Sessions unrelated to proposal work never notice it.

## Scope

The plugin implements **v1** of [the spec](docs/spec.md), with one deliberate
divergence: the spec writes the command as `/plan`, which this ships as
`/overture` to avoid colliding with Claude Code's plan mode.

Deferred items (v2) are listed in `SKILL.md` so the agent declines them rather
than improvising: automated comment pull, scheduled ambient polling,
related-proposal import, audience-variant renders beyond the exec summary,
Figma ingestion, and shared context-repo extraction.

Permanently out of scope: bidirectional Confluence sync, auto-sending any
communication, ticket creation, and real-time collaboration.

## Develop

```bash
claude plugin validate .                      # marketplace + resolved plugin
claude plugin validate ./skills               # skill components
sh -n hooks/planning-rehydrate.sh             # hook syntax
python3 scripts/check-references.py           # internal cross-references
```

Triggering is checked separately, since `validate` never reads a description:
[`evals/`](evals/README.md) runs 20 realistic queries — 9 that should fire the
plugin, 11 near-misses that shouldn't — through a headless session. It costs
real money (~$1.50 a run), so it isn't in CI; run it whenever you change a
description or add a command.

A `version: No version specified` warning is expected — see Versioning. Don't
use `--strict`; it treats that intentional warning as an error.

### Versioning

The manifests intentionally omit `version`, so Claude Code tracks the git commit
SHA and `/plugin update` picks up every pushed commit. Switch to pinned releases
later with `claude plugin tag` if it ever needs them.

## License

MIT — see [LICENSE](LICENSE).
