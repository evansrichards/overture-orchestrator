# Evals

## What this tests

A skill's `description` is its entire triggering mechanism, and its failure
modes are asymmetric:

- **Under-triggering is invisible.** The user gets an ordinary answer and never
  learns the skill existed. Nothing surfaces it.
- **Over-triggering is loud.** The skill fires on work it has no business in,
  and people learn to distrust it.

Neither shows up in `claude plugin validate` — that command validates manifests
and component structure and never reads the description at all. This suite is
the check that does.

`trigger-cases.json` holds 20 realistic queries: 9 that should trigger the
plugin and 11 near-misses that should not. The near-misses carry most of the
signal — they share vocabulary with the skill (*decide, status, descope,
publish, plan, align, Confluence*) but need something else. A negative set of
obviously-irrelevant queries would prove nothing.

## Running it

```bash
./run-trigger-eval.py                          # all cases, 1 run each
./run-trigger-eval.py --runs 3                 # majority vote, more reliable
./run-trigger-eval.py --case near-ticket       # one or more case ids
./run-trigger-eval.py --model claude-opus-5    # test a specific model
./run-trigger-eval.py --json results.json      # full results to a file
```

Each case runs `claude -p` headless with `--plugin-dir` pointing at this repo,
allows only the `Skill` tool, and caps the run at 2 turns — so each case is one
decision ("consult the plugin or not"), not a whole task. Exit code is 1 if any
case fails.

**The plugin has two doors** and either firing counts: the `planning-orchestrator`
skill fires on natural language, and the `overture` command fires when the model
reaches for `/overture` directly. Both route to the same place. An eval that
only matched the skill would report false negatives — it did, until that was
fixed.

## Cost

Roughly **$0.07–0.10 per case**, so a full 20-case run is about **$1.50**, and
`--runs 3` is about **$5**. That is why this is not wired into CI. Run it when
you change a description, add a command, or notice the skill firing somewhere it
shouldn't.

## Current state

Last measured 2026-08-18, single run per case unless noted:

| | Result |
|---|---|
| Should-trigger (recall) | **9 / 9** |
| Should-not-trigger | **10 / 11** |
| Overall | **19 / 20** |

Assembled incrementally while iterating on the descriptions; every case whose
behavior changed was re-run against the final configuration. A clean full-suite
baseline at `--runs 3` has not been run.

### Known failure: `near-descope-ticket`

> *"descope PROJ-4412 down to just the email template change, the rest can wait
> for next quarter"*

Fires the plugin, at **3/3 runs** — a firm over-trigger, not a borderline one.
Scoping a Jira ticket is engineering execution, which the spec puts explicitly
out of scope, so the plugin should stay quiet.

The cause is lexical: `descope` is a named subcommand, and the word pulls hard
enough that two rounds of description tightening did not overcome it. Adding a
third targeted clause risks overfitting the description to one query, which
makes it worse everywhere else — so it is recorded rather than chased.

The consequence is mild: the model consults the skill, reads that this is for
proposals and not tickets, and moves on. That costs ~2.4k tokens, not a wrong
answer — the better of the two failure modes.

Worth revisiting if the same lexical pull shows up on other subcommand names
(`status`, `publish`, `decide` all currently pass their near-misses).

## What this does not test

Triggering only — whether the plugin is consulted. It says nothing about whether
the skill then *behaves* correctly: whether it batches questions properly,
whether the leak-check actually blocks a publish, whether the private zone stays
unreachable. Those need a real proposal run end-to-end, which is the pilot, not
an eval.

It did, however, catch one behavioral bug on its very first run: `SKILL.md` said
to look for the workspace "from the cwd upward", and the model read that as
`find / -maxdepth 6`. The instruction now says explicitly that it is a parent
walk and not a search.

## Note on `claude plugin eval`

Claude Code ships a first-party eval runner (`claude plugin eval`, with
`evals/**/case.yaml` + `graders/*.md`). It is currently **early access** and
refuses to run, its schema is not in the shipped CLI bundle, and the docs page
404s — so this suite does not use it. If it opens up, the case set here ports
over directly; only the runner would be replaced.
