# Durable execution: engines that survive a deploy

Three of Simba's audited failures share one root cause: state that lives in RAM.

- Observation engine watermark starts from epoch 0 on every restart (`sync_cursors` exists,
  has no callers).
- Meeting recorder sessions and the abandoned-session watchdog live in an in-memory map;
  every blue-green deploy erases them, so TISEZA sat in RECORDING for a day.
- Evidence-closure's "running" flag and the Gladia job id are local variables.

The industry name for the fix is durable execution: every step of a workflow is journaled
to a store, and a crashed run resumes from the last completed step instead of from zero.

## What the sources say

| Source | Format | Core claim | Simba mapping |
|---|---|---|---|
| Inngest, "Durable Execution: The Key to Harnessing AI Agents in Production" (https://www.inngest.com/blog/durable-execution-key-to-harnessing-ai-agents) | Blog, primary | Each `step.run()` is checkpointed; on failure the function is re-invoked and skips to the first uncompleted step. Steps make retries idempotent by construction. | `finish(meetingId)` as steps: concat chunks, transcribe, minutes, memory, dossier event. A restart mid-transcription resumes at transcription. |
| AppScale, "Durable Execution for LLM Agents 2026: Temporal + LangGraph" (https://appscale.blog/en/blog/durable-execution-llm-agents-temporal-langgraph-checkpointing-2026) | Article | Temporal as the outer orchestration layer (durability, retries, long-running lifecycle), agent logic inside. LangGraph checkpointers only save state between nodes and are not durable execution on their own. | Cron engines become workflows with explicit steps; the LLM call is one step with its own retry policy and deadline. |
| Reactify, "Durable AI agents in 2026: Temporal, Inngest, DBOS, Restate" (https://www.reactify-solutions.com/articles/durable-ai-agents-2026) | Comparison | By late 2025 durable execution went mainstream: AWS Durable Functions, Cloudflare Workflows GA, Vercel Workflow DevKit. DBOS runs on plain Postgres. | Simba already runs Postgres. A Postgres-backed queue is the zero-new-infra option. |
| Zylos, "Durable Execution for AI Agent Runtimes: Checkpointing, Replay, and Recovery" (https://zylos.ai/research/2026-04-24-durable-execution-agent-runtimes/) | Research note | Recovery cost argument: a naive retry after a long crash restarts from zero; a checkpointed workflow restarts within minutes of the crash. | The 6-minute milestone radar budget is lost entirely today when one call hangs. |

The Inngest post could not be fetched from this environment (egress blocked), so its
takeaways above come from search summaries and the article's known structure. Read it
directly before quoting it.

## The pattern, stripped to what Simba needs

1. **State in the database, never in the process.** Watermarks in `sync_cursors`, status
   machines as a column with one writer and one vocabulary, job ids persisted the moment
   they are minted.
2. **Sweepers read the database, not RAM.** A cron that selects `status = 'RECORDING' AND
   last_chunk_at < now() - 10 min` finishes every abandoned meeting, whichever container
   started it. The Meeting Notes audit already specifies this.
3. **Steps are idempotent.** One merged write for close plus audit (evidence-closure
   erases its own audit today because two writes race). Chunk files keyed by
   `epoch+seq`, not blind-appended.
4. **Every step has a deadline and a typed failure.** A 401 is not a network blip. The
   drainer retried a 401 245 times. Classify errors: retryable, needs-human, permanent.
5. **One chokepoint per outcome.** Two meeting-finish paths built separately gave "tasks
   or memory depending on which button you pressed". One `finish()` both paths call.
6. **Leader election for crons during blue-green overlap.** Both containers run the
   2-minute watchdog during the switchover; a Postgres advisory lock keyed on the job
   name fixes it in five lines.

## Tooling choice for one VPS, one operator

| Option | Cost to adopt | Fit |
|---|---|---|
| Postgres-backed job queue (pg-boss or graphile-worker for Node) | Hours. No new service. | Best first step. Retries, scheduling, singleton jobs, all in the database Simba already has. |
| Inngest (hosted or self-hosted) | A day. New dependency, good NestJS story. | If the step-function ergonomics are wanted and one more service is acceptable. |
| Temporal | Days. Separate cluster, workers, SDK. | Overkill at Simba's scale today. Revisit past 10 tenants. |

Recommendation: pg-boss first. Convert the three worst offenders (meeting finish,
evidence-closure, observation engine) into idempotent jobs with persisted cursors. Measure
duplicates and stuck rows before and after.
