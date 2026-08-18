# Onboarding

**The tool is never taught; it is encountered** — one concept at a time, each at
the moment it earns its explanation. This is a Claude Code plugin, so onboarding
targets an agent-mediated experience: the user is never required to memorize
commands, because the agent maps natural language to them.

## Echo teaching

When the user expresses intent in natural language — *"I'm assuming group admins
get email invites"* — perform the action **and narrate the mapping**:

> Recording that as an assumption → `/overture assume`. **A-004** created.

Fluency forms by watching one's own intent get translated, in context.

**Narration decays per command.** Usage counts live in
`planning/.onboarding.yml`:

1. Before narrating, read `command_usage[<command>]`.
2. If it is below `onboarding.narration_threshold` (default 3), narrate; otherwise
   just do the thing.
3. Increment the count either way.

Slash commands are **accelerators for the fluent, never prerequisites for the
new**. Never tell the user they should have used a command.

## Lifecycle-gated progressive disclosure

The proposal maturity state machine doubles as the teaching schedule. Introduce a
concept only at the moment its motivation is self-evident:

| Concept | Introduced |
|---|---|
| `frame` | At `init` |
| `question` / `decide` | At the first ambiguity |
| `decider` | The first time a decision is contested |
| `evidence` | The first time a quantitative claim appears |
| Assumption mining | At the first `publish --dry-run` |
| Leak-check | **By its first firing** |
| Dirty-page guard | **By its first firing** |
| `descope` | The first time scope is cut |
| `handoff` | At approval |

Record each in `concepts_introduced` so it is explained once.

**Teaching a concept one moment before its motivation exists turns it into
ceremony.** When tempted to explain the leak-check pre-emptively during setup:
don't. Explain it when it flags something.

## First run

On first invocation with no workspace, run a multi-step `AskUserQuestion` wizard:

1. **Repo location + enterprise remote setup** — where the workspace repo lives.
2. **Private-overlay setup** — with a plain-language explanation of *why* it never
   leaves the machine, plus the honest residual-risk note
   (`workspace.md` → Git topology). Say it once, here.
3. **Confluence connection test** — verify the MCP transport actually writes
   before the user depends on it.
4. **Optional first consideration file.**

Then — **instead of a demo tutorial** — ask for *something small and real the
user currently needs alignment on*, and run the first proposal on it. Real work
teaches value, and value drives session two. Offer a throwaway sandbox proposal
only as a fallback.

Never scaffold a workspace without running this wizard.

## Configuration by observation

Per-proposal config is interview-based and skippable
(`interaction.md` → `init` must never feel like a form).

Above that, **observe patterns across proposals** and *propose* configuration
changes via `AskUserQuestion` rather than waiting for the user to discover a
settings file:

- a template section skipped three times → offer to drop it from the default,
- a constant publish space → offer to make it the workspace default,
- a recurring audience set → offer to save it as a preset.

Config debt surfaces in `status` like every other staleness.
**`.config.yml` is never hand-edited** — if the user wants to change something,
route it through the command that owns it.

## Reader onboarding

The most important audience for an alignment tool only ever *receives* documents
and installs nothing. Their onboarding is the rendered page itself
(`publishing.md` → Reader onboarding).

Later, teammate adoption routes through consideration files:
*"your knowledge keeps getting cited in my proposals — want to own the file?"* is
a stronger onramp than any tutorial. Watch for that moment; don't manufacture it.

## `help` and `tour`

- **`/overture help`** — one-screen command map grouped by lifecycle stage,
  annotated with the user's own usage from `.onboarding.yml`.
- **`/overture tour`** — opt-in guided walkthrough on a scratch proposal, for
  users who explicitly want it. **Never forced**; offer at most once per
  workspace, and record `tour_completed`.

## Session rehydration

Re-engagement is the forgotten half of onboarding. On session start in a
workspace, surface a one-line state summary:

> 3 inbox items on `invitations-flow`; one contested decision unowned.

The plugin ships a `SessionStart` hook that does exactly this and stays silent
when no `planning/` workspace is present.
