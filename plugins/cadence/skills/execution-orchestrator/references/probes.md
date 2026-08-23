# Interview tiers and probe families

The interview machinery shared by `intake.md` and `commit.md`. Its purpose is
de-aliasing: making the thing being promised explicit enough that engineer and
stakeholder are picturing the same object.

## Trigger tiers (anti-fatigue — hard rule)

The trigger question is **"is anyone outside the team relying on a date?"** —
not "does a ticket exist."

| Tier | Trigger | Interview |
|---|---|---|
| **Full** | External deadline OR stakeholder-visible commitment | All probe families + scenario modeling + confirmation artifact (`commit.md`) |
| **Lite** | Ordinary queue item, multi-day | Exactly 3 questions: scope ins/outs, dependency profile, top assumption |
| **None** | Sub-day tasks | Log and go — no questions |

Never run a Full interview on a Lite item because it "seems thorough." If
engineers start giving pro-forma answers, the interview has failed; shorten
it. The interview must **give, not just take**: its output is armor for the
engineer — the confirmation message, the options, the defensible forecast. If
it only records answers, it is compliance theater and people will route
around it.

## Context assembly (do this BEFORE asking anything)

**Context assembly is the hard part, not the question list.** Cold questions
get shallow answers; loaded questions get real ones. Before a Full interview,
load:

1. The request thread / message, verbatim.
2. Any spec or design doc linked from it.
3. Related prior scenario records (`scenarios/`) — same feature area, same
   stakeholder, same deadline pressure.
4. Relevant cycle-time profiles from `history/cycle-times.jsonl` — the
   distribution for this (size, dependency_profile) class.
5. The team's probe library, `probes/library.md` — run every matching
   `trigger → check` pattern.

Only then interview. Ask questions batched through `AskUserQuestion` where
options can be enumerated; leave genuinely open questions (scope framing,
"what are you assuming") as free text.

## Probe families

Use these verbatim-in-spirit — adapt the bracketed slots to the actual
request, don't paraphrase the intent away.

### Generic (always available)

- "The request says **'[term]'**. What is explicitly IN: which plans / states /
  entry points / user segments? What is explicitly OUT?"
- "What's the **smallest version** satisfying the literal ask? What version do
  you suspect the stakeholder **pictures**? If they differ, that gap is the
  commitment risk — name it."
- "What are you **assuming exists or works** that you haven't verified?" →
  each answer becomes an entry in the record's `assumptions` list.
- "What would make this take **2× as long**? How likely is that?"
- "**'Done' means:** shipped to prod? Behind a flag? With analytics?
  Announced?"
- "**What needs to be done to unblock this work? Whose calendar does that sit
  on?**" → each answer becomes a typed precondition record (owner, forecast,
  status) with a dependency edge in the queue. An unresolved precondition past
  its forecast automatically shifts the dependent item and writes the causal
  ledger event.

### Environment-diff (catches implied scope activation)

- "Who can **reach** this once it ships that can't today? What obligations
  attach to those users, segments, or geographies?"
- "Is this the **first time we do [X] outside an experiment / flag / limited
  cohort**? What did the experiment's constraints exempt us from — compliance,
  scale, a11y, localization, analytics contracts?"
- "What does this assume exists in **production shape** that currently exists
  only in **prototype shape**?"

### Context-aware (when artifacts are loaded)

- **Spec-diff:** "The spec mentions **[X]** in §N; your scope summary doesn't.
  Deliberate exclusion or oversight?"
- **History:** "The ledger shows **[profile]** items running **[N]wks over
  median**. This matches that profile — same risk here?"
- **Aliasing check:** "You said yes to **[date]**. The request said
  **'[ambiguous term]'**. Which scenario option does your yes refer to? That
  option name goes in the commitment record and the confirmation message."

## Probe library accretion

When an interview catches something real, append the pattern to the
workspace's `probes/library.md` as one `trigger → check` line
(`touches cancellation → state-rule check`). Patterns only — no project
details, no names. Tell the user you added it. Over time this file becomes
the org's portable interviewing IP.
