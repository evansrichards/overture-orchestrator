# Changelog

Notable changes to this repo. The plugin manifests intentionally omit
`version` — installs track the git commit SHA, so `/plugin update` picks up
every entry here as soon as it lands on `main`. Entries are dated, newest
first.

## 2026-08-23 — Cadence onboarding (`/cadence tour`)

### Added

- **`/cadence tour`** — Cadence's onboarding entry point, mirroring
  Overture's pattern: a one-screen-per-stop concept walk (ledger-is-truth,
  the private data repo, interview tiers, the config surface, the working
  loop, what's stubbed), and a **guided Phase 0 walkthrough** when no
  workspace exists yet — it checklists the privacy conversation, template
  copy, config fill-in, and first ledger events, and *validates* the copied
  workspace against the template and schemas, but never creates it (repo
  creation and the §11 conversation stay human acts). A bare `/cadence`
  offers the tour once.
- **Echo teaching with narration decay** for Cadence: natural language maps
  to subcommands with the mapping narrated until fluency (usage counts in
  the workspace's `.onboarding.yml`, threshold 3), and each refusal rule is
  taught the first time it bites rather than front-loaded.

Note: `tour` is an addition beyond the spec's §10 command suite, added by
request; the spec is unchanged.

## 2026-08-23 — Monorepo restructure + Cadence scaffold

**No action needed for existing Overture users.** The marketplace name
(`overture`), the plugin name (`overture-orchestrator`), and the install
commands are unchanged; `/plugin update` follows the new layout automatically.
Overture's behavior is unchanged — this was a pure relocation.

### Changed

- Restructured the repo into an orchestrator monorepo. Overture moved intact
  from the repo root to `plugins/overture/` (history preserved via `git mv`);
  the marketplace manifest stays at the root and now lists both plugins.

### Added

- **Cadence** (`plugins/cadence/`, installable as
  `cadence-orchestrator@overture`) — execution orchestrator scaffold per
  `cadence-spec.md`, covering Phase 0–1 support and Phase 2 command skeletons:
  - Full interview prompts for `/cadence intake`, `/cadence commit`,
    `/cadence reserve` (tiered interviews, probe families, refusal
    invariants, confirmation artifacts).
  - Simple implementations of `/cadence status` and `/cadence delivered`.
  - Stubs with spec references for `/cadence publish`, `/cadence review`,
    `/cadence sync` — `publish` already carries the approval gate and the
    rule that per-person data never renders to any adapter output.
  - `workspace-template/` to copy into your separate private team data repo.
  - Eval fixtures for the five spec §14 scenarios.
- `shared/record-schemas/` — the Overture → Cadence handoff contract as
  versioned JSON Schemas (v1): commitment record, scenario record, ledger
  events, cycle-time record.
- `cadence-spec.md` — the Cadence source specification, at the repo root.
- This changelog.

## 2026-08-18 — Triggering eval suite

- Added `evals/` (now `plugins/overture/evals/`): 20 realistic trigger/near-miss
  queries run headless against the plugin, and fixed two bugs it found.

## 2026-08 — Initial release

- Overture: planning orchestrator plugin — proposal workspace, decision
  records, batched questions, structurally private context zone, leak-checked
  one-way Confluence publishing. Command renamed `/plan` → `/overture` to
  avoid colliding with Claude Code's plan mode.
