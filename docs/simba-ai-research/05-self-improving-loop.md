# The self-improving loop: what Karpathy's autoresearch teaches Simba

Andrew Ng's framing in the bookmarked lecture: "Agent, Harness, Feedback, Loops, Graphs,
Self-Improving Systems." Karpathy shipped the smallest working version of the last step.

## Source

- **karpathy/autoresearch** (GitHub, released 7 March 2026, 66k+ stars within a month):
  https://github.com/karpathy/autoresearch
- Fortune, "The Karpathy Loop: 700 experiments, 2 days" (17 March 2026):
  https://fortune.com/2026/03/17/andrej-karpathy-loop-autonomous-ai-agents-future/

## The loop, exactly as built

| Element | autoresearch | Why it matters |
|---|---|---|
| One editable file | The agent may edit `train.py` only. `prepare.py` is frozen. | Blast radius is bounded. Every change is reviewable as one diff. |
| Fixed budget per experiment | Exactly 5 minutes wall-clock per run | Runs are comparable whatever the agent changed. About 12 per hour, 100 overnight. |
| One metric | Validation bits per byte, lower is better | No judgement call about whether a change "helped". |
| Commit or revert | Improved: commit. Did not: revert. Repeat. | The repository itself is the memory of what worked. |
| Human steering file | `program.md`, plain Markdown the human edits | The operator shapes strategy without touching code. Karpathy calls it "research org code". |
| Result | 700 experiments in two days, 20 stacked improvements, time-to-GPT-2 from 2.02 h to 1.80 h | Small, additive, measured wins compound. |

The model does not change itself. It changes the system around itself so the next run
is better. That is the whole idea.

## Simba mapping: one hillclimb per engine

Simba has the ingredients and none of the loop. `llm_usage_logs`, an `eval` module,
production outcome data (tasks closed, drafts sent versus killed, signals that became
tasks) and one operator who reviews a morning brief.

| autoresearch | Simba equivalent |
|---|---|
| `train.py` | One engine's prompt plus gate thresholds, in one file per engine (e.g. `evidence-closure.prompt.md`, `thread-gate.rules.json`) |
| `prepare.py` | Frozen replay set: last 30 days of real messages and their true outcomes, sampled once, stored |
| 5-minute run | Replay the engine over the frozen set on Haiku or Sonnet via Batch API; minutes, cents |
| val_bpb | One number per engine: closure precision and recall, draft send rate, planner-signal to task conversion, brief truthfulness |
| commit / revert | Change is kept only if the metric improves and no guard metric (false closures, wrong-contact drafts) worsens |
| `program.md` | `SIMBA_ENGINE_GOALS.md`: Anton's plain-language rules, e.g. "never close a payment task without an amount in the evidence" |

## Why this is the highest-leverage thing in this whole research

- The sense-making audit found the loop leaks at six joints, each fixed by hand after a
  six-reader code audit. A per-engine metric would have shown "2,110 signals, 0 tasks" on
  day one, for free.
- Every future prompt tweak today is a guess deployed to production. With a replay set it
  becomes an experiment with a number.
- Cost: a replay of 1,000 messages through Haiku 4.5 at `low` effort via Batch is well
  under one dollar. It can run nightly.

## Order of work

| Step | Effort | Output |
|---|---|---|
| Freeze a replay set: 1,000 WhatsApp messages with ground-truth labels (was it a task? was it answered? did the contact confirm?) | half day, mostly SQL | `eval/replay/2026-09.jsonl` |
| Metric script per engine, run against the replay set | half day | one number per engine in the morning connector report |
| Nightly job: propose one change to one engine file, replay, keep or revert, write a one-line note | 1 day | the loop exists |
| `SIMBA_ENGINE_GOALS.md` as the human steering file | 1 h | Anton steers without code |

Guardrails from the same source: one editable surface per engine, a fixed budget, a hard
metric, and a human-owned instruction file. Skip any of the four and the loop drifts.
