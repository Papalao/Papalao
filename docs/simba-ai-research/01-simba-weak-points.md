# Simba AI: measured weak points that the research must address

Source of truth: three production audits published 3, 15 and 16 September 2026
(Probe Sweep, Meeting Notes Failure Map, Sense-Making Loop Failure Map). Every
number below was checked against the live Postgres or backend logs, not inferred.

## What Simba is

- NestJS + Prisma + Postgres, multi-tenant (6 tenants), 1,655 API routes, 112 web pages.
- Channels: WhatsApp (Baileys, two lines), Telegram, Gmail, Outlook, SMS, WeChat, web.
- AI layer: `llm.chat()` cascade Gemini (agy CLI, 2 slots) -> Claude (CLI), ~2,500 calls/day.
- Dozens of cron-driven "engines": message intake, observation engine, milestone radar,
  evidence-closure, task follow-up drafts, reply-brain, dossiers, morning/evening brief,
  approval queue, thread gate, meeting recorder, goal progress, night batch.
- Memory: 2.5M-row memory table that nothing recalls from, plus vector memory and
  weekly re-read dossiers.

## The failure pattern, in one line

Simba is a set of independent cron loops sharing one LLM rail, with state held in RAM
and no end-to-end contract between stages. The loop leaks at the joints, not in one place.

## Ranked weak points and what each needs from the outside world

| # | Weak point (measured) | Root cause class | What to learn |
|---|---|---|---|
| 1 | LLM rail: Gemini queue p50 8.8 h, 49% timeouts, every engine spends its wall-clock budget waiting | No bounded queue, no deadline, no rung demotion, LLM via CLI not API | Harness engineering, model routing, prompt caching, batch API |
| 2 | 2,110 "planner" WhatsApp signals classified, 0 tasks created | Stage writes an event nobody consumes; no contract per stage | Graph/loop design, contracts between nodes, end-to-end evals |
| 3 | Follow-up drafts: 203 killed vs 16 sent in 14 days | Loop with no exit condition, drafts carry no task link, freshness counts Simba's own sends | Loop termination, evidence, human-in-the-loop design |
| 4 | Evidence-closure judges 2 of 1,500 tasks/hour, erases its own audit | Over-strict gate, non-idempotent writes, RAM running flag | Idempotency, durable execution, eval of judge precision/recall |
| 5 | Meeting pipeline: recording stuck in RECORDING forever, 245 retries on a 401 | State machine not owned by DB, watchdog reads RAM, error classes conflated | Durable workflows, status machines, error taxonomy |
| 6 | Watermarks and sessions live in RAM, replay on every deploy | `sync_cursors` exists but unused | Checkpointing, event sourcing |
| 7 | Memory: 2.5M rows written, near-zero recall; dossiers weekly re-read, no outcome events | Write-heavy, read-never memory; no event log | Agent memory architectures, context engineering |
| 8 | Brief prints query limits as counts, reads tables nobody writes | No truth check on generated summaries | Evals for generated reports, grounding |
| 9 | 1,655 routes, 6 tenants, unclear which features are paid for | Feature sprawl vs revenue | Vertical AI monetization, feature ROI |

## Constraints that shape every recommendation

- One operator (Anton). Fixes must be hours, not weeks.
- Runs on one VPS with blue-green Docker deploys; every deploy clears RAM.
- Cost matters: 2,500 LLM calls/day today, target is more work for less spend.
- Revenue matters more than architecture purity.
