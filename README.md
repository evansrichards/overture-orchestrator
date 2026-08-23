# Overture & Cadence

A monorepo of two sibling Claude Code plugins — orchestrators for the two
halves of a software team's planning-to-delivery arc. The repo is also its own
plugin marketplace (`overture`), so installing either plugin is two commands.

| Plugin | What it does |
| ------ | ------------ |
| [`plugins/overture`](plugins/overture/README.md) | **Planning orchestrator.** Draft, align on, and publish cross-functional proposals. |
| [`plugins/cadence`](plugins/cadence/README.md) | **Execution orchestrator.** Commitments, capacity, injections, and the ledger behind every date change. |

## Overture

Overture is a proposal workspace for speculative, cross-functional work —
proposals that may never ship, or never even be sent. It drafts, gathers
decisions, assumptions, and evidence, batches its questions so several
proposals can run concurrently, and publishes one-way to Confluence with a
leak-check verifier on every outbound path. Candid notes live in a private
zone the publish pipeline structurally cannot read. Its terminal artifact — an
approved proposal with scope, estimates, assumptions, and stakeholders — is
the handoff point where Cadence picks up. Spec:
[`plugins/overture/docs/spec.md`](plugins/overture/docs/spec.md).

## Cadence

Cadence tracks execution: an append-only ledger as the source of truth for
every timeline change, forecasts computed from measured cycle times instead of
story points, a structured interview that de-aliases every externally-visible
commitment (what exactly was promised, to whom, by when, minus what), and
human-approved fan-out of timeline updates to Jira and Confluence. Dates never
"slip" — conditions change, and each change references the ledger event that
caused it: an injection, a capacity reservation, or a broken assumption. Spec:
[`cadence-spec.md`](cadence-spec.md).

## Code here, data elsewhere

**This repo is portable code only** — schemas, commands, prompts, adapters.
Nothing org-specific, nothing sensitive.

All workspace data lives in a **separate private team repo** that you create
from Cadence's [`workspace-template/`](plugins/cadence/workspace-template/):
queue records, the ledger, cycle-time history, calendar and roster config, and
the accreted probe library. Overture's `planning/` workspace likewise lives in
a repo of your choosing. The privacy rules for the Cadence data repo — what
may never leave it, and the team covenant required before adding anyone — are
in [`cadence-spec.md`](cadence-spec.md) §11.

The two plugins share one file-format contract, not code:
[`shared/record-schemas/`](shared/record-schemas/README.md) defines the
commitment record Overture emits at handoff and Cadence consumes at t=0.

## Install

```bash
/plugin marketplace add evansrichards/overture-orchestrator
/plugin install overture-orchestrator@overture   # planning
/plugin install cadence-orchestrator@overture    # execution
```

Updates track the git SHA — `/plugin update` picks up every pushed commit. See
[`CHANGELOG.md`](CHANGELOG.md) for what changed.

## Layout

```
.claude-plugin/marketplace.json   # this repo is the marketplace
plugins/
  overture/                       # planning orchestrator (plugin root)
  cadence/                        # execution orchestrator (plugin root)
shared/
  record-schemas/                 # the Overture → Cadence handoff contract (v1)
cadence-spec.md                   # Cadence source specification
CHANGELOG.md
```

Each plugin's own README covers its usage, layout, and development checks.

## License

MIT — see [LICENSE](LICENSE).
