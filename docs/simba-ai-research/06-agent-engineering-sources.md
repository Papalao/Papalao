# Agent engineering sources: what to read, what to change in Simba

Fifteen primary sources from 2025 to 2026, chosen because the people who built the systems
wrote them. Each row ends with the Simba change it justifies. Ratings: MUST, WORTH, SKIP
if short on time.

Verification note: URLs were matched by exact title in search results; anthropic.com,
openai.com, manus.im, youtube.com and arxiv.org could not be fetched from this environment.
Only GitHub pages were opened directly.

## Context engineering

| # | Source | Format | Rating |
|---|---|---|---|
| 1 | **Context Engineering for AI Agents: Lessons from Building Manus**, Yichao "Peak" Ji, Manus co-founder, 18 Jul 2025. https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus | Blog, 15 min | MUST |
| 2 | **Effective context engineering for AI agents**, Anthropic Applied AI, 29 Sep 2025. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | Blog, 20 min | MUST |
| 3 | **Context Engineering for Agents**, Lance Martin (LangChain) on Latent Space, 11 Sep 2025. https://www.youtube.com/watch?v=_IlTcWciEC4 and notes https://rlancemartin.github.io/2025/06/23/context_engineering/ | Video, 57 min | WORTH |
| 4 | **12-Factor Agents**, Dex Horthy (HumanLayer), AI Engineer World's Fair, Jun 2025. https://www.youtube.com/watch?v=8kMaTybvDUw and https://github.com/humanlayer/12-factor-agents | Talk 17 min + repo | MUST |

Takeaways and Simba mapping:

- **Cache hit rate is the production metric** (Manus). Agents run about 100:1 input to
  output tokens; cached input is a fraction of the price. Byte-stable prefix, no timestamps
  in the system prompt, append-only history, deterministic JSON key order. *Simba: reply-brain
  and draft prompts get a frozen prefix; the connector report shows cache-read ratio per engine.*
- **Never add or remove tools mid-session** (Manus). Mask tool choice instead. *Simba: one
  tool list per lane, fixed.*
- **File system as restorable context** (Manus, Anthropic). Store big tool outputs, keep a
  reference in the window. *Simba: dossier text and meeting transcripts referenced by id,
  loaded on demand, not pasted into every call.*
- **Keep failed actions in context** (Manus) so the model stops repeating them. *Simba: the
  follow-up loop that killed 203 drafts never told the drafter why the last one was killed.*
- **Right altitude prompts** (Anthropic): heuristics in labeled sections, not brittle if/else
  or vague slogans. *Simba: the evidence-closure two-keyword gate is a brittle rule; rewrite
  as a judged heuristic with examples.*
- **Four moves: write, select, compress, isolate** (Martin). Prune at the tool boundary; raw
  tool results are the biggest bloat. *Simba: message-intake passes whole threads; select the
  last N turns plus the contact block.*
- **Own your control flow** (Horthy). Most production agents are deterministic code with a
  few LLM steps. Small agents of 3 to 10 steps, stateless-reducer design, launch/pause/resume.
  *Simba is already this shape. The missing piece is the reducer state living in the database
  (see section 03) and "contact a human" as a first-class tool call, not a killed draft.*

## Harness, loops, SDK guides

| # | Source | Format | Rating |
|---|---|---|---|
| 5 | **A Practical Guide to Building Agents**, OpenAI, Apr 2025. https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf | PDF, 34 pages | WORTH |
| 6 | **Building agents with the Claude Agent SDK**, Anthropic, 29 Sep 2025. https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk ; companion talk Barry Zhang, **How We Build Effective Agents**, AI Engineer Summit Feb 2025, https://www.youtube.com/watch?v=D7_ipDqhtwk | Blog 15 min, talk | WORTH |
| 7 | **Harness engineering: leveraging Codex in an agent-first world**, Ryan Lopopolo, OpenAI, 11 Feb 2026. https://openai.com/index/harness-engineering/ | Blog, 15 min | WORTH |

Takeaways and Simba mapping:

- **Prototype on the most capable model, then downgrade per step while watching evals**
  (OpenAI). *Simba did the reverse: cheapest rung first, no eval. Section 02's three lanes
  fix the routing; section 05's replay set supplies the eval.*
- **Single agent plus tools first; multi-agent only when prompts become unmanageable**
  (OpenAI, Anthropic). *Simba's dozens of engines are effectively many agents sharing one
  rail. Merge intake, thread gate and planner into one classifier call with a structured output.*
- **Layered guardrails and tool risk ratings** (OpenAI): read, write, irreversible. Human
  handoff on retry thresholds and any high-risk action. *Simba's probe sweep already
  classifies routes as side-effect-free or not. Reuse that classification as the tool
  risk rating for the agent layer.*
- **Gather context, act, verify, repeat** (Anthropic). Verify with rules first, LLM judge
  only for fuzzy criteria. *Simba: the brief printed "Missed: 20" for months. A rule check
  (count equals printed count) would have caught it.*
- **The harness is the product, the model is swappable** (Lopopolo). Encode rules as
  mechanical guardrails with error messages that say how to fix. *Simba: the 401-retried-245-
  times bug is a missing error taxonomy, not a model problem.*

## Evals and observability

| # | Source | Format | Rating |
|---|---|---|---|
| 8 | **Demystifying evals for AI agents**, Anthropic, Jan 2026. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | Blog, 25 min | MUST |
| 9 | **Why AI evals are the hottest new skill for product builders**, Hamel Husain and Shreya Shankar on Lenny's Podcast, 25 Sep 2025. https://www.youtube.com/watch?v=BsWxPI9UM4c and FAQ https://hamel.dev/blog/posts/evals-faq/ | Video, 90 min | MUST |

Takeaways and Simba mapping:

- **Grade end state, not transcripts** (Anthropic): "task exists", "escalation flag set".
  *Simba: planner signal to task conversion is an end-state metric. It was zero for months.*
- **Report pass^k, not pass@k** (Anthropic). Customer-facing reliability is consistency.
- **Start with 20 to 50 tasks from real failures; keep capability evals separate from
  regression evals that must stay near 100%** (Anthropic). *Simba: the 80 findings from the
  six-reader audit are the first regression set.*
- **Error analysis before tooling** (Husain, Shankar): read about 100 real traces, write
  failure notes, group into a taxonomy, count. Binary pass/fail with a written critique beats
  1 to 5 scales. One domain expert sets the bar. *Simba: Anton reads 100 killed drafts and
  labels why. That taxonomy drives the next prompt, and it is a Saturday morning of work.*
- **Build an LLM judge only for the top one or two failure modes; validate against human
  labels first.** *Simba: the evidence-closure judge was never validated against Anton's
  own closures.*

## Memory

| # | Source | Format | Rating |
|---|---|---|---|
| 10 | **Memory Blocks: The Key to Agentic Context Management**, Letta (MemGPT team), 14 May 2025. https://www.letta.com/blog/memory-blocks/ ; talk by Charles Packer, 2 Jul 2025, https://www.youtube.com/watch?v=sgD-sw0RW78 ; Mem0 paper https://arxiv.org/abs/2504.19413 ; Anthropic memory tool and context editing https://www.anthropic.com/news/context-management | Blog, talk, paper | WORTH |

Takeaways and Simba mapping:

- **Labeled, size-capped memory blocks always in context** (`customer`, `open_issues`,
  `business_policies`) versus archival memory retrieved on demand. Character caps are the
  cost control. *Simba: this is the dossier done right. One block per contact, capped, edited
  by the agent through an explicit tool, read on every reply.*
- **Extract, then ADD/UPDATE/DELETE** (Mem0) instead of appending everything. Mem0 reports
  more than 90% token savings versus full context. *Simba's 2.5M-row memory table is
  append-only and never read. Stop writing rows nobody reads; write block updates instead.*
- **Skip graph memory for a small-business bot.** Not worth the complexity at this stage.
- **Anthropic memory tool plus auto-clearing stale tool results**: reported +39% on their
  agentic eval and 84% fewer tokens on a 100-turn task.

## Tool design

| # | Source | Format | Rating |
|---|---|---|---|
| 11 | **Writing effective tools for agents, with agents**, Anthropic, 11 Sep 2025. https://www.anthropic.com/engineering/writing-tools-for-agents | Blog, 15 min | MUST |

- **Fewer, higher-leverage tools.** `find_orders(query)` instead of `list` plus `get`. No
  one-to-one API wrappers. *Simba has 1,655 routes. The agent should see perhaps 15 tools.*
- **Namespace tools, return human-readable names and dates, offer concise or detailed
  response formats, paginate by default, make error messages actionable.**
- **Let the model run your tool evals and rewrite the descriptions.** Description wording
  alone moved benchmark scores materially.

## Self-improving loops

| # | Source | Format | Rating |
|---|---|---|---|
| 12 | **autoresearch**, Andrej Karpathy, 7 Mar 2026. https://github.com/karpathy/autoresearch | Repo | WORTH (full treatment in section 05) |
| 13 | **GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning**, Agrawal, Khattab et al. (DSPy team), ICLR 2026 oral. https://arxiv.org/abs/2507.19457 and https://github.com/gepa-ai/gepa | Paper + library | WORTH |

- **GEPA** samples trajectories, reflects in natural language on failures, proposes prompt
  edits, keeps a Pareto front. Reported to beat GRPO by about 6 points with up to 35x fewer
  rollouts. With 50 to 200 labeled examples and a scorer it rewrites a system prompt.
  *Simba: once the replay set from section 05 exists, GEPA is the off-the-shelf optimizer to
  run against it.*
- **Name clash to know about:** DSPy also ships an optimizer called SIMBA (Stochastic
  Introspective Mini-Batch Ascent). Unrelated to Simba AI. GEPA is the newer default.
- Ship optimized prompts as frozen artifacts. Re-run only when evals regress or the model
  changes.

## Multi-agent tradeoffs and cost

| # | Source | Format | Rating |
|---|---|---|---|
| 14 | **How we built our multi-agent research system**, Anthropic, 13 Jun 2025. https://www.anthropic.com/engineering/multi-agent-research-system | Blog, 20 min | WORTH |

- Multi-agent runs cost about 15x the tokens of chat; token use explained about 80% of
  quality variance. Default for a small-business assistant: single agent plus good tools.
- Scale effort to the query with explicit rules for how many tool calls a simple versus a
  complex request deserves.
- Checkpoint and resume on errors, let the model see the error, per-run budget caps and
  circuit breakers. About 20 real queries caught most issues early.

## Conference signal

| # | Source | Format | Rating |
|---|---|---|---|
| 15 | **AI Engineer World's Fair 2026** (29 Jun to 2 Jul 2026). swyx opening "Loopcraft: The Art of Stacking Loops"; Mike Krieger (Anthropic Labs) closing "How Anthropic Builds". Day 4 livestream https://www.youtube.com/watch?v=I2cbIws9j10 ; recap https://www.latent.space/p/aiewf26trends ; Harrison Chase, "Context Engineering Our Way to Long-Horizon Agents", Sequoia Training Data, 21 Jan 2026, https://sequoiacap.com/podcast/context-engineering-our-way-to-long-horizon-agents-langchains-harrison-chase | Video | SKIP if short on time |

- Three loops: inner (automation), outer (autonomy), meta (quality improvement from logs
  and feedback). The meta loop is sources 8, 12 and 13 combined.
- "The model is a commodity; the harness is the moat."
- Give an agent standing ownership of one area plus a feedback channel (Krieger). *Simba:
  one engine owns follow-ups end to end, and its metric is in the morning report.*

## If you only have two hours

Manus (1), the 12-Factor talk (4), Anthropic on evals (8), Anthropic on tools (11), then the
first 30 minutes of Husain and Shankar (9).
