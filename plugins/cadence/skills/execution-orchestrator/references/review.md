# `review` — adaptation loop (STUB)

> **Phase 4 stub** (`cadence-spec.md` §13, §8). Runs quarterly or on demand
> once enough history exists. Until then: say it's stubbed, and offer the
> manual equivalent — read `history/cycle-times.jsonl` and present the
> forecast-vs-actual table by hand, following the rules below.

## What is specified now

- **Propose, never auto-apply.** Output is a set of *suggested* config
  revisions with evidence: "[owner]'s actuals run ~20% over forecast across
  n=9; suggest focus_factor 0.7 → 0.58, or investigate cause." The lead
  applies changes by editing config normally — git history is the audit
  trail.
- The residual gap between calendar-based capacity and actual throughput
  **is** the baseline drag; it needs no configuration and no proposal. It
  silently absorbs untracked KTLO, interrupts, and sub-half-day absence.
- Everything this command reads and writes is per-person data: **team- (or
  lead-) internal only, never rendered to any adapter output** (spec §11),
  and firewalled from performance reviews by the team covenant.

## TODO (Phase 4)

- Forecast-vs-actual deltas per (size, dependency_profile) class and per
  owner (≥ ~8–10 items before a personal distribution is preferred — §7).
- Basis-string switchover proposals: `seeded` → measured once a profile class
  reaches ~10 items.
- Estimate-accuracy split: assumptions-held vs. assumptions-broke — the cut
  that separates "slow team" from "thrashed team" (§12).
