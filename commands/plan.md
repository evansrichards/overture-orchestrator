---
description: Planning orchestrator — draft, align on, and publish proposals. Usage `/plan <subcommand> [args]`, e.g. `/plan init`, `/plan decide "…"`, `/plan status`, `/plan publish --dry-run`. Run bare for the command map.
---

# `/plan $ARGUMENTS`

Dispatch to the **`planning-orchestrator`** skill. Load its `SKILL.md` first —
it holds the non-negotiables — then load only the reference the subcommand needs,
per the routing table there.

Paths below are relative to the skill directory
(`skills/planning-orchestrator/`), not to this command.

## Parse

`$ARGUMENTS` is `<subcommand> [args] [flags]`.

- **No arguments** → run `help`: the one-screen command map grouped by lifecycle
  stage, annotated with the user's own usage from `planning/.onboarding.yml`.
- **Unrecognized subcommand** → don't guess and don't invent a new one. Map it to
  the closest real subcommand and confirm via `AskUserQuestion`, or fall back to
  `help`.
- **Natural language instead of a subcommand** (`/plan I'm assuming admins get
  email invites`) → map it to the right subcommand, run it, and narrate the
  mapping once (echo teaching, `references/onboarding.md`).

## Subcommands

| Stage | Subcommands |
|---|---|
| Start | `init [--from-descoped <id>] [--from-existing <url\|path>]` · `attach <slug>` · `frame <statement>` |
| Build | `question <text> [--for <person>]` · `decide <text>` · `define <term>` · `assume <text> [--mine]` · `evidence <claim> --source <link>` · `todo <text>` · `descope <item> --reason <text>` |
| Align | `ask <person> <about>` · `status` · `publish [--dry-run]` |
| Finish | `handoff` |
| Meta | `help` · `tour` |

Global flag: **`--now`** — ask queued questions immediately instead of deferring
them to the next interaction point.

Full per-subcommand procedure: `references/commands.md`.

## Before running anything

1. Locate the workspace (`planning/index.md`, searching upward from cwd). None,
   and the user wants planning work → first-run wizard
   (`references/onboarding.md`). Never scaffold silently.
2. Resolve the proposal — the argument, else the attached one, else offer a
   picker from `planning/index.md`.
3. Append the subcommand's events before reporting the work as done.

## Hold these regardless of subcommand

- `publish` and `ask` **never** read `proposals/*/context/`, and both go through
  the leak-check verifier subagent first. Publish blocks on unresolved flags.
- Nothing is auto-sent. Placing a Confluence comment needs per-instance
  confirmation.
- Questions go through `AskUserQuestion`, batched — except genuinely open ones
  (the frame statement, novel design directions), which stay free-text.
- Descoping moves content to `descoped.md`; it never deletes.
