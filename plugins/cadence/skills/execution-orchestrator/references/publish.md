# `publish` — approval gate and fan-out (STUB)

> **Phase 3 stub** (`cadence-spec.md` §13). The adapter mechanics are not
> built. The approval-gate structure and the privacy firewall below are
> binding **now** — they shape every draft the other commands queue, and the
> manual fallback must honor them too.

## What is specified now

### Approval gate (structure is fixed)

1. List every draft in `out/drafts/`, grouped by target surface (Jira issue,
   Confluence page), each with the ledger event(s) it renders.
2. Present the batch for approval via `AskUserQuestion` — approve all /
   approve selected / hold. **Nothing posts without explicit approval in this
   step. No unattended publishes, ever.**
3. On approval, adapters post **under the lead's identity, not a bot's**,
   then move each draft to a sent/ archive with the post link, and append the
   publish to the ledger.

### Privacy firewall (binding on every adapter, spec §11)

**Per-person data never renders to any adapter output.** Before anything
leaves, verify each draft contains only:

- item-level dates and basis strings,
- event attributions — injection approvers, reservation reasons
  (decision-makers, never performers),
- aggregate capacity notes attributed to **windows, never to people**.

A draft containing cycle times, focus factors, forecast deltas, personal
calendar detail, or an assignment-sensitivity view is a defect: block it,
strip it, re-draft. Tone: factual, attributed, neutral, boring — every line
traces to a ledger event.

## Manual fallback (until Phase 3)

Render the approved drafts to the terminal for the lead to paste. The gate
and the firewall apply identically.

## TODO (Phase 3)

- Jira adapter: comment on mapped issues (`config/adapters.yaml`) — spec §12.
- Confluence adapter: per-project cumulative timeline blocks — spec §12; lift
  the pipeline **conventions** from Overture (one-way, idempotent,
  dirty-page-guarded render: `plugins/overture/skills/planning-orchestrator/references/publishing.md`),
  duplicating rather than importing — spec §3.
- Draft archive + ledger linkage on successful post.
