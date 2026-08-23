# CLAUDE.md

Guidance for Claude when working **in this repository**.

## What this repo is

An orchestrator monorepo that is also its own marketplace (`overture`),
hosting two sibling Claude Code plugins:

- **Overture** (`plugins/overture/`) — planning orchestrator, implementing
  [`plugins/overture/docs/spec.md`](plugins/overture/docs/spec.md).
- **Cadence** (`plugins/cadence/`) — execution orchestrator, implementing
  [`cadence-spec.md`](cadence-spec.md).

**This repo is the tool, not the workspace.** The `planning/` directory
Overture manages and the `cadence/` workspace Cadence manages both live in
*different* repos belonging to the user (Cadence's is a private team data
repo — `cadence-spec.md` §11). Never scaffold either workspace here. Nothing
org-specific or sensitive belongs anywhere in this repo.

## Where things go

| Change | File |
| ------ | ---- |
| Overture agent behavior, invariants, routing | `plugins/overture/skills/planning-orchestrator/SKILL.md` |
| Overture deep protocol for one concern | the matching `plugins/overture/skills/planning-orchestrator/references/*.md` |
| Overture record or document shape | `plugins/overture/skills/planning-orchestrator/references/templates/` |
| Overture command surface / dispatch | `plugins/overture/commands/overture.md` |
| Session rehydration | `plugins/overture/hooks/planning-rehydrate.sh` |
| Cadence agent behavior, invariants, routing | `plugins/cadence/skills/execution-orchestrator/SKILL.md` |
| Cadence interview prompts / per-command protocol | the matching `plugins/cadence/skills/execution-orchestrator/references/*.md` |
| Cadence command surface / dispatch | `plugins/cadence/commands/cadence.md` |
| Cadence workspace scaffold users copy out | `plugins/cadence/workspace-template/` |
| Overture → Cadence handoff contract | `shared/record-schemas/` (versioned; a breaking change means a v2, not an edit to v1) |

## Rules for edits

- **Keep each `SKILL.md` light.** They are loaded into every session. New
  detail belongs in a reference, reached through the routing table — that is
  the progressive-disclosure requirement (Overture spec §16.5), not a style
  preference. If you add a reference, add its row to the routing table.
- **The eight non-negotiables in Overture's `SKILL.md` are load-bearing.**
  Don't soften, reword, or relocate them without an explicit request. In
  particular: the private zone is unreachable rather than filtered; the
  drafting agent never verifies its own output; nothing is auto-sent.
- **Cadence's refusal invariants are load-bearing the same way:** no injection
  cascade without a named placement approver; no commitment record with an
  undefined scope term; no orphan estimate revision (every `estimate_revised`
  references a causal ledger event); per-person data never renders to any
  adapter output.
- **One lifecycle (Overture).** Questions, definitions, and scope changes are
  decision records with a `type`. Adding a second state machine is the failure
  mode this design exists to prevent.
- **One record of truth (Cadence).** The ledger is authoritative; external
  tools are projections. Don't add state that isn't derivable from ledger
  events plus config.
- **No shared framework.** `shared/` holds the record schemas and nothing
  else. Duplication between the plugins is acceptable; premature abstraction
  is not. Extract shared code only when duplication actually hurts and the
  user asks.
- **Respect each spec's v1/deferral split** (Overture `SKILL.md`'s v1 table;
  Cadence build phases, spec §13). Deferred items are deferred on purpose;
  implement one only when asked.
- Cross-references use the form `` `file.md` → Heading `` and must resolve.
- **Update `CHANGELOG.md`** (repo root, dated entries) for any user-visible
  change: command behavior, prompts, schemas, layout, install flow.

## Before claiming it works

Run these and report the actual output — don't assert success without it:

```bash
claude plugin validate .                              # marketplace + both plugins; `version` warning expected
claude plugin validate ./plugins/overture/skills      # Overture skill components
claude plugin validate ./plugins/cadence/skills       # Cadence skill components
sh -n plugins/overture/hooks/planning-rehydrate.sh    # hook syntax
python3 plugins/overture/scripts/check-references.py  # Overture cross-references
```

**If you change a `description`** — a skill's or a command's — run the
triggering eval (`plugins/overture/evals/README.md`) and report the numbers. A
description is the whole triggering mechanism, and nothing else in this repo
tests it. Tighten it against the near-miss cases as a set, never against one
failing query; overfitting a description to a single phrasing degrades it
everywhere else. (Cadence's eval fixtures in `plugins/cadence/evals/` test
interview behavior, not triggering; they have no runner yet.)

Note that `claude plugin validate` checks manifests and component structure —
it does **not** deeply verify skill frontmatter. The decisive check that a
skill, command, or hook is actually discovered is an install into an isolated
config:

```bash
export CLAUDE_CONFIG_DIR=$(mktemp -d)
claude plugin marketplace add "$PWD" && claude plugin install overture-orchestrator@overture
claude plugin install cadence-orchestrator@overture
claude plugin details overture-orchestrator   # inventory + token cost
claude plugin details cadence-orchestrator
```

Use an isolated `CLAUDE_CONFIG_DIR` so the real user config is untouched, and
delete it afterward.

## Guardrails

- `plugins/overture/docs/spec.md` and `cadence-spec.md` are source
  specifications and historical records. Don't rewrite either to match its
  implementation — if they diverge, say so and ask.
- **Known deliberate divergences:** the Overture spec writes the command as
  `/plan`; the plugin ships it as `/overture`, to avoid colliding with Claude
  Code's plan mode. The Cadence spec's §4 workspace tree lives in the separate
  private data repo — this repo documents and validates it, never contains it.
  The plugin also adds `/cadence tour` (onboarding), which the Cadence spec's
  §10 command suite does not define — a requested addition, not an oversight.
  Every other name follows the specs. Don't "fix" either side toward the
  other.
- Manifests intentionally omit `version` (updates track the git SHA;
  `CHANGELOG.md` is the human-readable record). Don't add one unless asked to
  switch to pinned releases.
- Confirm before outward actions: force-pushing, changing repo settings, or
  deleting branches.
