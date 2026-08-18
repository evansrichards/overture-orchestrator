# Interaction model — `AskUserQuestion`

**Attention is the scarce resource.** The user should be able to run several
proposals concurrently without rapid context switching. That is the whole point
of this protocol.

Every question the orchestrator asks goes through Claude Code's built-in
`AskUserQuestion` tool — never free-text interrogation in the transcript.
Free-text stays available through the tool's built-in "Other" option, so nothing
is lost by making structured choice the default.

## Tool constraints — design inputs, not choices

- 1–4 questions per call; 2–4 options per question.
- Each question needs a `header` (≤12 chars) and full question text.
- `multiSelect: true` allows multiple answers.
- The user can always type a custom response ("Other").
- **Not available in subagents.** All interviewing runs in the main session.

That last constraint has a direct architectural consequence: the leak-check
verifier subagent **returns structured flags as data**, and the *main* session
presents resolution options. The verifier never prompts. See `privacy.md`.

## Batching rules

### 1. Interaction points, not interruptions

Commands append questions-for-the-user to the event log (`question.queued`)
rather than asking immediately. `--now` overrides and asks inline.

The queue drains at exactly these points:

- the end of a command that **requires** input to proceed,
- `attach`,
- `status`,
- `publish`.

Nowhere else. A command that can complete without an answer completes, queues,
and moves on.

### 2. Multi-step flows

When draining, group queued questions into sequential `AskUserQuestion` calls of
up to 4 questions each:

1. Order by dependency — a question whose *options* depend on an earlier answer
   goes in a later call.
2. Pack independent questions greedily into the earliest call.
3. **Target: resolve a typical session's pending input in 1–3 steps.** If you
   are heading for a fourth step, drop the lowest-value questions back onto the
   queue rather than spending the user's attention.

### 3. Question authoring

`AskUserQuestion` is for **decision trees and clarifying questions** — places
where alignment between agent and user is the point.

**Keep free-text (do not enumerate):** the frame statement itself, novel design
directions, and anything where offering options would anchor the user on the
agent's guesses. Enumerating a genuinely open question is worse than asking it
plainly.

Within structured questions:

- Options must be **genuinely distinct courses of action**, not paraphrases of
  one another.
- When you have a recommendation, it goes **first**, with `(Recommended)`
  appended to the label.
- Descriptions carry the trade-off, not restated labels.
- `multiSelect` for naturally plural inputs: realm/app tagging at `init`,
  selecting descoped items to revive, choosing which consideration files apply,
  accepting mined assumptions.
- **No meta-questions.** Never ask "is this plan good?", "should I proceed?", or
  "does this look right?" Interaction points surface real decisions only.

### 4. Answers are events

Every response appends `interview.answered` with the question, **the options
presented**, and the selection. Interview history is replayable and auditable
like every other state change.

## Mapping to the data model

`AskUserQuestion`'s shape mirrors the decision record's shape:

| Tool | Record |
|---|---|
| Options presented | `## Options considered` |
| Selection | `## Choice` |
| Option descriptions | Trade-offs feeding `## Consequences` |

So when an interview answer settles a decision — `decide`, a contested `define`,
a `descope` confirmation — **create the record directly from the tool call**. The
alternatives are captured for free, and that is precisely the provenance the
decision history needs. Never throw away the rejected options.

## Per-command usage

| Command | Role |
|---|---|
| `init` | Multi-step interview: framing type → publish target → audiences → realms/apps (`multiSelect`, options from the consideration-file index) → leak-denylist seeding. **Every step past the frame is individually skippable.** |
| `decide` | Known options become the choice set; selection and rejected options populate the record |
| `define` (contested) | Competing definitions as options, holders named in descriptions |
| `descope` | Confirmation, then "what would trigger revival" as a follow-up step |
| `assume --mine` | Mined candidates, `multiSelect`: record / reject / already covered |
| `question` / contested `decide` | "Who settles this?" — options from the audience list |
| `publish` | Per leak-check flag: rephrase (Recommended, with the proposed rewording in the description) / remove / override-with-justification |
| `attach` / `status` | Drain point for the queued backlog and the inbox |

## `init` must never feel like a form

This is the rule that makes or breaks first use. Concretely:

- The **frame is the only required step.** Everything after it is skippable.
- Every configuration question carries a skip path — either an explicit
  "Skip / decide later" option or a sensible default stated in the description.
- Skipped steps get defaults from `.workspace.yml` and resurface later through
  `status` config-debt reporting, never through a blocking re-ask.
- If the user skips three steps in a row, **stop interviewing** and go to work.
  They are telling you something.
