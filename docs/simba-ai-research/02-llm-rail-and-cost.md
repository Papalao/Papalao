# The LLM rail: from an 8.8-hour queue to seconds, at lower cost

Simba's single biggest measured defect is the rail, not any one engine. Every engine
with a wall-clock budget spends it waiting for a Gemini CLI slot, then drops its work.
Phase 1 (bounded queues, rung demotion) is live. This section is what comes after.

## Diagnosis in one table

| Today | Problem | Industry pattern |
|---|---|---|
| LLM calls go through CLIs (agy, Claude CLI), two slots each | No concurrency beyond 2, no cache reuse, exec-timeout only starts after the wait, cost invisible per call | Call the API directly with an SDK, set concurrency per route, log `usage` per call |
| One cascade for every job (classify a WhatsApp line, judge closure evidence, write a dossier) | The 14,255 messages/month classification runs on the same rung as long-form dossier writing | Route by job: small model for high-volume classification, mid model for drafts, top model for judgement |
| Night batch, dossier regeneration, entity extraction run as live calls | They compete with reply-brain and the brief for the same slots | Batch API for anything that can wait an hour |
| System prompts and dossier context re-sent on every call | Full input price every time | Prompt caching on the stable prefix |

## Price facts (Anthropic first-party API, verified 2026-06)

| Model | Input $/1M | Output $/1M | Fit for Simba |
|---|---|---|---|
| Claude Haiku 4.5 | 1.00 | 5.00 | Message classification, thread gate, dedup, goal measurement text, language detect |
| Claude Sonnet 5 | 2.00 | 10.00 | Follow-up drafts, reply-brain, brief text, meeting minutes |
| Claude Opus 5 | 5.00 | 25.00 | Evidence-closure judge, dossier synthesis, milestone radar reasoning |

- Prompt caching: cached input reads are billed at roughly 10% of the base input price.
  Prefix must be stable byte for byte (tools, then system, then messages). A timestamp in
  the system prompt silently defeats it. Verify with `usage.cache_read_input_tokens`.
- Batch API: 50% off input and output, results within 24 h, usually much sooner.
  Stackable with caching.
- Effort control: `output_config.effort` from `low` to `max`. Classification and short
  chat routes run well at `low`; judgement at `high`.

## What this means for Simba, concretely

1. **Replace both CLI rungs with SDK calls.** The CLI is a developer tool, not a server
   rail. Direct API calls give per-route concurrency, typed errors, `usage` on every
   response, and caching. This alone removes the "exec timeout starts after the wait" bug.
2. **Three lanes, not one cascade.** Fast lane (Haiku, high concurrency) for intake,
   classification, thread gate. Draft lane (Sonnet) for anything a human reads. Judge lane
   (Opus) for closure decisions and dossiers. Each lane has its own bounded queue and
   deadline. A lane being slow no longer starves another.
3. **Move the night work to Batch.** Entity extraction for memory, weekly dossier rebuild,
   goal measurement narratives, evening checkpoint pre-computation. Submit at 01:00,
   collect at 05:00. Half price, zero contention with daytime chat.
4. **Cache the stable prefix.** Reply-brain system prompt, tool definitions, the contact's
   dossier summary. Put the volatile part (today's messages) after the last cache breakpoint.
5. **Log cost per engine.** `llm_usage_logs` already exists. Add model, input tokens,
   cached tokens, output tokens, and engine name. Then the morning connector report can
   show shillings per engine per day, and the 1,655-route question ("what is worth keeping")
   gets a cost column.

## Order of work

| Step | Effort | Expected effect |
|---|---|---|
| SDK client with three lanes and bounded queues, keep CLI as emergency fallback | 1 day | p50 latency from minutes/hours to seconds on every engine |
| Route intake and thread gate to Haiku at `low` effort | 2 h | Largest call volume moves to the cheapest lane |
| Batch API for night-batch jobs | half day | Night work off the live rail, 50% cheaper |
| Prompt caching on reply-brain and drafts | 2 h | Input cost on repeated context drops by most of its value |
| Cost per engine in the 07:20 connector report | 2 h | Visibility to kill or keep features by cost |

## Sources

- Anthropic model and pricing table, prompt caching and Batch API facts: Anthropic API
  documentation as bundled in the Claude API reference used for this research (June 2026
  snapshot). Live pages: https://docs.anthropic.com/en/docs/about-claude/pricing and
  https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- Third-party cost guides that agree on the caching and batch discounts (not primary, use
  for framing only): https://www.finout.io/blog/anthropic-api-pricing ,
  https://agentmarketcap.ai/blog/2026/04/06/prompt-caching-economics-2026-anthropic-google-agent-cost
