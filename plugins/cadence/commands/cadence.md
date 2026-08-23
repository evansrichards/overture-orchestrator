---
description: Execution orchestrator — commitments, capacity, injections, and the ledger behind every date change. Usage `/cadence <subcommand> [args]`, e.g. `/cadence intake`, `/cadence reserve sam 2 2026-09-08..2026-09-09 "security updates"`, `/cadence status`. Run bare for the command map. For tracking execution state — not for drafting proposals (/overture) or doing the engineering work itself.
---

# `/cadence $ARGUMENTS`

Dispatch to the **`execution-orchestrator`** skill. Load its `SKILL.md`
first — it holds the non-negotiables — then load only the reference the
subcommand needs, per the routing table there.

Paths below are relative to the skill directory
(`skills/execution-orchestrator/`), not to this command.

## Parse

`$ARGUMENTS` is `<subcommand> [args]`.

- **No arguments** → print the command map below with one-line descriptions
  and the current build-phase state (which commands are stubs).
- **Unrecognized subcommand** → don't guess and don't invent one. Map it to
  the closest real subcommand and confirm via `AskUserQuestion`.
- **Natural language instead of a subcommand** (`/cadence we just got a P1
  from the VP`) → map it to the right subcommand and run it, narrating the
  mapping once.

## Subcommands

| Subcommand | Reference | State |
|---|---|---|
| `intake` | `references/intake.md` | full interview |
| `commit <item>` | `references/commit.md` | full interview |
| `reserve <who> <days> <window> <reason>` | `references/reserve.md` | full interview |
| `status` | `references/status.md` | implemented |
| `delivered <item>` | `references/delivered.md` | implemented |
| `publish` | `references/publish.md` | stub — approval gate + privacy firewall binding |
| `review` | `references/review.md` | stub |
| `sync` | `references/sync.md` | stub |

## Hold these regardless of subcommand

- Every date change references a causal ledger event — **refuse orphan
  estimate revisions**.
- Injections **refuse to cascade without a named placement approver**.
- No commitment record with an undefined scope term.
- Nothing is auto-sent; drafts wait in `out/drafts/` for `publish`'s approval
  gate, and posts go out as the lead, never a bot.
- Per-person data never renders to any adapter output
  (`references/privacy.md`).
- Append the subcommand's ledger events before reporting the work as done.
