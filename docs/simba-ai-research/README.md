# Simba AI improvement research

A watchlist and fix map for two people (Anton and Ilya) who want to learn from the best
2025 to 2026 material on production LLM agents and turn it into money with Simba.

Everything here is anchored to Simba's own measured defects from the September 2026 audits.
No source is included unless it changes a decision about Simba.

## Read in this order

| File | What it is | Time |
|---|---|---|
| [01-simba-weak-points.md](01-simba-weak-points.md) | The nine measured weak points, ranked, and what each needs from outside | 5 min |
| [04-bookmarked-talks.md](04-bookmarked-talks.md) | The X bookmarks, verified: Karpathy, Ng, Anthropic prompting playbook, Barry Zhang, the harness engineering cluster. One-week watch order for two people at the end. | 10 min to read, 4 h to watch |
| [07-monetization.md](07-monetization.md) | Pricing models, WhatsApp rules and costs in Africa in 2026, what earns revenue, the money plan | 10 min |
| [02-llm-rail-and-cost.md](02-llm-rail-and-cost.md) | From an 8.8-hour queue to seconds: three model lanes, caching, batch, cost per engine | 5 min |
| [05-self-improving-loop.md](05-self-improving-loop.md) | Karpathy's autoresearch loop turned into a nightly per-engine replay for Simba | 5 min |
| [03-durable-execution.md](03-durable-execution.md) | State in the database, sweepers that read it, idempotent steps, tooling for one VPS | 5 min |
| [06-agent-engineering-sources.md](06-agent-engineering-sources.md) | Fifteen primary sources on context, harness, evals, memory, tools, each mapped to a Simba change | 15 min to read |

## The ten videos and articles, ranked

| # | Watch or read | Min | The one idea | Simba change |
|---|---|---|---|---|
| 1 | Barry Zhang, How We Build Effective Agents. https://www.youtube.com/watch?v=D7_ipDqhtwk | 15 | Do not build agents for everything; agent = environment, tools, prompt | Mark each engine workflow or agent |
| 2 | Karpathy at YC, Software Is Changing (Again). https://www.youtube.com/watch?v=LCEmiRjPEtQ | 40 | Autonomy slider; verify before it becomes state | Three send positions per contact; rule checks on the brief |
| 3 | Margot van Laar, The prompting playbook. https://www.youtube.com/watch?v=G2B0YWuJUgI | 33 | Evals first, prompt hygiene, escalation must be acceptable | Prompt audit of the follow-up engine |
| 4 | Dex Horthy, 12-Factor Agents. https://www.youtube.com/watch?v=8kMaTybvDUw | 17 | Own the control flow; contact-a-human is a tool call | First engine contract |
| 5 | Husain and Shankar on evals. https://www.youtube.com/watch?v=BsWxPI9UM4c (first 30 min) | 30 | Read 100 traces, build a taxonomy, binary grades | Label 100 killed drafts |
| 6 | Anthropic, Demystifying evals for AI agents. https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | 25 | Grade end state; regression set from real failures | The 80 audit findings become the regression set |
| 7 | Manus, Context Engineering for AI Agents. https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus | 15 | Cache hit rate is the metric; keep failures in context | Frozen prompt prefixes; tell the drafter why the last draft died |
| 8 | Anthropic, Writing effective tools for agents. https://www.anthropic.com/engineering/writing-tools-for-agents | 15 | Few high-leverage tools, not API wrappers | 15 agent tools, not 1,655 routes |
| 9 | Ramanujam on pricing, Lenny's Podcast. https://www.lennysnewsletter.com/p/pricing-and-scaling-your-ai-product-madhavan-ramanujam | 90 | Price the job removed, not the feature | One countable outcome per market |
| 10 | Karpathy, autoresearch. https://github.com/karpathy/autoresearch | 10 | Fixed metric, fixed budget, one file, keep or revert | Nightly per-engine replay |

## The five moves that pay

1. **Make the follow-up engine send.** 203 drafts killed, 16 sent. Payment chasing is the
   only workflow with measured return in the market data, and Simba already has it built.
2. **Three lanes, caching, batch.** Latency from hours to seconds, and the margin that
   outcome pricing needs.
3. **Replay set and nightly hillclimb.** Every prompt change becomes a measured experiment.
4. **One countable outcome, hybrid price, Business API, distribution partner.** The
   monetization section, in that order.
5. **Freeze the route surface and log what paying tenants use.** Then cut.

## What was not done

- No VPS or production access was used. All Simba numbers come from the three published
  audits of 3, 15 and 16 September 2026.
- YouTube, anthropic.com, openai.com, manus.im and arxiv.org could not be opened from the
  research environment. URLs were verified by title match in search results and official
  session pages. Two long "Stanford" uploads (Karpathy, Ng) are third-party re-uploads and are
  marked as such.
