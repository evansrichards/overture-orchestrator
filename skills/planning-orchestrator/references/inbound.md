# Inbound flow, triage, and outbound delivery

Publishing is push. The return path — comments, answers, page edits, stakeholder
reactions — is **pull-based and durable**: no daemon, no live sync, no merge.

## The inbox

Inbound material lands in `proposals/<slug>/inbox/` as discrete items and is
triaged at interaction points (`attach`, `status`).

An inbox item is **anything requiring the author's judgment**:

- a Confluence page comment,
- a pasted Teams reply,
- a Figma comment (design critique happens in Figma, not Confluence — manual
  paste in v1),
- a detected page edit (from the dirty-page guard),
- a stale-question nudge.

### Item format — `inbox/<ts>-<short-slug>.md`

```yaml
---
received: 2026-08-17T10:04:00Z
from: <person>
channel: confluence-comment    # confluence-comment | teams | email | figma |
                               # page-edit | nudge | verbal
provenance: public             # public | private
about: D-007                   # optional: the record or section it concerns
state: new                     # new | triaged | dismissed
---

<the content, verbatim>
```

**Capture provenance at intake, not later.** Who it came from and via what
channel is what powers attribution (`publishing.md`) and the position-consent
default (`records.md`). Reconstructing it after the fact is guesswork, and
guessing wrong here is the one mistake that burns candor.

## Triage

On `attach` / `status`, walk each `state: new` item, propose the corresponding
action, and route the choice through `AskUserQuestion`:

| Proposed action | Effect |
|---|---|
| **Record an answer** | `decide` — settles the record the item concerns |
| **Open a follow-up** | `question` — a new `Q-` record with an assignee |
| **Revise a section** | Edit `proposal.md` / the relevant record |
| **Record a position** | Add to `positions` on a contested record, with the item's provenance and consent state |
| **Dismiss** | Mark `state: dismissed` with a reason |

Every resolution appends `inbox.triaged` (or `inbox.dismissed`) and adds the
sender to `contributed_by` on any record the item shaped.

In v1, items arrive **manually** — "here's what the PM said," pasted into
`attach`. The triage machinery is identical regardless of transport, which is
exactly what makes the automated transports below incremental rather than
architectural. Do not reshape triage to accommodate a future transport.

## Deferred inbound transports (v2 — do not build in v1)

- **`pull-comments`** — at `attach` / `status` / pre-`publish`, fetch the page's
  comments and version via MCP, diff against `.config.yml`, and convert new
  comments and edit-deltas into inbox items. Polling at moments the user is
  already engaged: 80% of "watch the live doc" with zero infrastructure.
- **Scheduled ambient poll** — a cron-driven headless session checks watched
  pages and writes new inbox items **as commits to the workspace repo**,
  optionally posting a digest to a Teams self-chat. Events land as artifacts, not
  notifications.
- **Webhooks** — require a hosted receiver. Out of scope for a personal tool.

For notification without opening a session **today**, the zero-build answer is
**Confluence native page-watch email**. It lands outside the system, and that is
fine for the interim — say so rather than building something.

Stale-question nudges are a degenerate case of the same machinery: `status` flags
questions open longer than `staleness.open_question_days` and offers to draft a
follow-up via `ask`.

## Outbound delivery (`ask`)

The org uses Microsoft Teams, which shapes the options.

### v1: clipboard, always

Present the approved draft for the user to paste into Teams, email, or anywhere.
Zero integration, works everywhere.

### v1 optional: place as a Confluence comment

When the proposal has a published page and the question concerns it, `ask` may
post the drafted question as a **page comment** — with **explicit confirmation
each time**, since this is a public action.

This is often *better* than a DM: the question is durable and visible to other
stakeholders, and the answer returns through the same comment-ingestion path as
everything else — a closed loop entirely inside the system. Offer it when the
conditions hold.

Append `comment.placed` on confirmation.

### Teams API integration — deliberately not planned

Microsoft Graph can send chat messages but has **no draft primitive for chats**.
Integration would mean sending directly on the user's behalf, violating the
never-auto-send rule; it also requires org app registration and admin consent.

Clipboard is not a compromise here — it is the correct Teams answer. If the user
asks for Teams integration, explain this rather than treating it as a backlog
item.
