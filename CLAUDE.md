# CLAUDE.md

Guidance for Claude when working **in this repository**.

## What this repo is

A standalone Claude Code plugin (`overture-orchestrator`) that is also its own
marketplace (`overture`), implementing [`docs/spec.md`](docs/spec.md) — the
Planning Orchestrator specification.

**This repo is the tool, not the workspace.** The `planning/` directory the
plugin manages lives in a *different* repo belonging to the user. Never scaffold
a `planning/` workspace here.

## Where things go

| Change | File |
| ------ | ---- |
| Agent behavior, invariants, routing | `skills/planning-orchestrator/SKILL.md` |
| Deep protocol for one concern | the matching `references/*.md` |
| A record or document shape | `references/templates/` |
| Command surface / dispatch | `commands/overture.md` |
| Session rehydration | `hooks/planning-rehydrate.sh` |

## Rules for edits

- **Keep `SKILL.md` light.** It is loaded into every session. New detail belongs
  in a reference, reached through the routing table — that is the §16.5
  progressive-disclosure requirement, not a style preference. If you add a
  reference, add its row to the routing table.
- **The eight non-negotiables in `SKILL.md` are load-bearing.** Don't soften,
  reword, or relocate them without an explicit request. In particular: the
  private zone is unreachable rather than filtered; the drafting agent never
  verifies its own output; nothing is auto-sent.
- **One lifecycle.** Questions, definitions, and scope changes are decision
  records with a `type`. Adding a second state machine is the failure mode this
  design exists to prevent.
- **Respect the v1/v2 split** in `SKILL.md`. Deferred items are deferred on
  purpose; implement one only when asked.
- Cross-references use the form `` `file.md` → Heading `` and must resolve.

## Before claiming it works

Run these and report the actual output — don't assert success without it:

```bash
claude plugin validate .                      # exits 0; `version` warning expected
claude plugin validate ./skills               # skill components
sh -n hooks/planning-rehydrate.sh             # hook syntax
```

Note that `claude plugin validate` checks manifests and component structure — it
does **not** deeply verify skill frontmatter. The decisive check that a skill,
command, or hook is actually discovered is an install into an isolated config:

```bash
export CLAUDE_CONFIG_DIR=$(mktemp -d)
claude plugin marketplace add "$PWD" && claude plugin install overture-orchestrator@overture
claude plugin details overture-orchestrator   # inventory + token cost
```

Use an isolated `CLAUDE_CONFIG_DIR` so the real user config is untouched, and
delete it afterward.

## Guardrails

- `docs/spec.md` is the source specification and a historical record. Don't
  rewrite it to match the implementation — if they diverge, say so and ask.
- **Known deliberate divergence:** the spec writes the command as `/plan`; the
  plugin ships it as `/overture`, to avoid colliding with Claude Code's plan
  mode. Every other name follows the spec. Don't "fix" either side toward the
  other.
- Manifests intentionally omit `version` (updates track the git SHA). Don't add
  one unless asked to switch to pinned releases.
- Confirm before outward actions: force-pushing, changing repo settings, or
  deleting branches.
