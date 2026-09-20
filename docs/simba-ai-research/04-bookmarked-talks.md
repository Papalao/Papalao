# The bookmarked talks, verified

The X bookmarks in the screenshots point at five ideas. Here is where each one really
lives, how long it is, what to take from it, and what it changes in Simba.

Verification note: YouTube, anthropic.com and claude.com could not be opened from this
environment. URLs were cross-checked against search results, official session pages and
playlists. Items marked **unverified upload** are third-party re-uploads whose original
course or channel could not be confirmed; the content is real, the framing in the tweet
is the uploader's.

## 1. Andrej Karpathy

| Item | Where | Length | Status |
|---|---|---|---|
| Stanford lecture behind the "10% LLM, 30% Prompt, 50% Agent, 70% Loop, 100% Graph" tweet | https://www.youtube.com/watch?v=XdbpCM4yGyE (published 14 Aug 2026) | about 1 h | **unverified upload**; the progression is the uploader's summary, not Karpathy's slide |
| "Software Is Changing (Again)", Y Combinator AI Startup School | https://www.youtube.com/watch?v=LCEmiRjPEtQ ; YC page https://www.ycombinator.com/library/MW-andrej-karpathy-software-is-changing-again | 40 min, 17 Jun 2025 | verified, official YC channel |
| autoresearch repo | https://github.com/karpathy/autoresearch | repo, 7 Mar 2026 | verified, opened directly |
| LLM Wiki gist (ingest, query, lint over a persistent Markdown wiki) | https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f | gist, 4 Apr 2026 | verified |

Takeaways:

- **The prompt is a program.** Version it, test it, review it like code. *Simba: engine
  prompts live inline in TypeScript today. Move each to its own file with a changelog.*
- **Inner loop versus outer loop.** The model learns from context at runtime (inner). You
  improve prompts, tools and evals from logs (outer). Design both. *Simba has neither loop
  instrumented; section 05 builds the outer one.*
- **Never let unverified output become state.** A cheap verifier after every consequential
  step: a rule, a second call, or a human. *Simba: the brief printed a query limit as a
  count for months. One rule check would have caught it.*
- **Autonomy slider.** Start with draft-and-approve, widen autonomy per intent as evals prove
  it. *Simba's auto-send rules table has 0 rows. That is the slider at zero for every
  contact. Define three positions (draft, send-with-delay, send) per contact and intent.*
- **Persist state outside the model.** "Anterograde amnesia" is the default. *Simba: the
  2.5M-row memory table is the wrong shape for this; see the memory rows in section 06.*
- **Make data agent-readable.** Structured price lists, policies and contacts, not PDFs.
  *Simba: a Markdown wiki per venture, in the shape of the LLM Wiki gist, is cheaper to
  maintain than vector memory and easier to audit.*

## 2. Andrew Ng

| Item | Where | Length | Status |
|---|---|---|---|
| Stanford session behind the "Prompting will be dead in 6 months" tweet | https://www.youtube.com/watch?v=9EuNUe-CJRM | about 2 h | **unverified upload**, clickbait title. Circulating chapter map: 9:14 first working agent, 33:11 loops, 1:02:46 loops to graphs, 1:30:15 self-modifying agents, 1:49:05 orchestration layer |
| "The Future of AI Agents with Andrew Ng", LangChain Interrupt 2026 | https://www.youtube.com/watch?v=OaRhpwz_TGM | talk | verified |
| DeepLearning.AI "Agentic AI" course | https://www.deeplearning.ai/courses/agentic-ai/ | self-paced, raw Python | verified, announced 7 Oct 2025 |

Takeaways:

- **Get a first agent running end to end in minutes, then iterate.** Do not architect up
  front.
- **Past two or three loops, make the control flow an explicit graph** with typed edges so
  it is testable. *Simba's sense-making loop is eight stages wired by cron timing and shared
  tables. Drawing it as a graph with typed events between nodes is what exposed the six
  leaks. Build it that way.*
- **Disciplined error analysis is the skill.** Read 20 to 50 failed traces, bucket by step,
  fix the worst bucket first. Component-level evals per step, not only end to end.
- **Self-improvement under a completion gate.** Agents may propose prompt changes; evals
  decide whether they land.

## 3. Anthropic, Code with Claude 2026

| Item | Where | Length | Status |
|---|---|---|---|
| "The prompting playbook", Margot van Laar, Anthropic London, 19 May 2026 | https://www.youtube.com/watch?v=G2B0YWuJUgI ; session page https://claude.com/code-with-claude/session/ldn-the-prompting-playbook | 33 min | verified, official Claude channel |
| "How we Claude Code", Jason Schwartz (the "how Anthropic uses Claude every day" session) | https://www.youtube.com/watch?v=IlqJqcl8ONE | talk, 23 May 2026 | verified |
| The "4-hour course" in the tweet | SF playlist https://www.youtube.com/playlist?list=PLmWCw1CzcFim2obQ-w3ohbULOfwp5lApR ; London playlist https://www.youtube.com/playlist?list=PLmWCw1CzcFilPJdvw6scjHjbBripZWFps | playlists | no single 4-hour video exists; the tweet's chapter titles are a third-party compilation |

Takeaways from the prompting playbook (worked examples: a telco support bot that broke
after a model migration; a retail staff-scheduling agent built from scratch):

- **Evals first.** Separate "model behaviour changed" (fixable by prompt) from real
  capability gaps. Include control cases.
- **Prompt hygiene.** Delete copied, outdated and over-fitted instructions. Structure into
  role, policy, data, tone, output contract. *Simba: engines have accreted rules for months.
  A prompt audit per engine is a half-day job with immediate effect.*
- **Fix information withholding** caused by over-defensive rules: say when to share, not
  only when not to.
- **Move arithmetic and dates into tools.** *Simba: due dates, amounts in shillings, days
  overdue. Never let the model compute them.*
- **Make hand-off to a human explicitly acceptable.** One-sided cost language causes
  escalation failures. *Simba's follow-up loop killed 203 drafts and escalated none.*
- **Split complex prompts into draft, check, repair.**

## 4. "The right way to build AI agents in 14 minutes"

| Item | Where | Length | Status |
|---|---|---|---|
| "How We Build Effective Agents", Barry Zhang, Anthropic, AI Engineer Summit NYC | https://www.youtube.com/watch?v=D7_ipDqhtwk | 14:38, Feb 2025 | verified |
| Follow-up: "Don't Build Agents, Build Skills Instead", Zhang and Murag | https://www.youtube.com/watch?v=CEvIs9y1uog | 16 min, Dec 2025 | verified |
| The written version: "Building effective agents", Schluntz and Zhang | https://www.anthropic.com/engineering/building-effective-agents | blog, 19 Dec 2024 | verified |

Takeaways:

- **Do not build agents for everything.** Use them only when the task is complex, valuable,
  and the model can be given a verifiable feedback signal. *Most of Simba is workflows with a
  small agentic core. Name which parts are which.*
- **Agent = environment + tools + system prompt.** Iterate on those three before adding
  anything else.
- **Think like your agent.** Read the transcript with only the model's context. If you could
  not act correctly from it, neither can the model. *Simba: the drafter is never told why the
  previous draft was killed.*
- **Skills.** Package procedural knowledge (how we quote, refund policy, how we chase an
  invoice) as loadable files rather than one giant prompt.
- **Patterns from the article:** prompt chaining, routing, parallelization,
  orchestrator-workers, evaluator-optimizer. Simba's intake should be routing; follow-up
  should be evaluator-optimizer with a real evaluator.

## 5. "Harness Engineering: How to Build AI Agents That Don't Fall Apart"

An article with this exact title could not be found. The diagram in the screenshot
(Contract, Context, State, Tools, Permissions, Evidence, Recovery) matches a cluster of
2026 writing on the same theme:

| Item | Where | Status |
|---|---|---|
| Arize AI, "Harness Engineering: How to Build Reliable AI Agents" | https://arize.com/resources/harness-engineering/ | closest match; author not shown |
| OpenAI, "Harness engineering: leveraging Codex in an agent-first world", Ryan Lopopolo | https://openai.com/index/harness-engineering/ | verified, 11 Feb 2026 |
| Lilian Weng, "Harness Engineering for Self-Improvement" | https://lilianweng.github.io/posts/2026-07-04-harness/ | verified, 4 Jul 2026 |
| Birgitta Böckeler, martinfowler.com | https://martinfowler.com/articles/harness-engineering.html | verified |
| Zhong and Zhu, "AI Harness Engineering: A Runtime Substrate", arXiv 2605.13357 | https://arxiv.org/abs/2605.13357 | paper, May 2026 |

Consensus across them, and the Simba fix each implies:

| Harness element | Rule | Simba today | Change |
|---|---|---|---|
| Contract | Write outcome, scope, invariants, budget and escalation conditions before the run | Engines have a cron schedule and a prompt, no contract | One `contract.md` per engine: what done means, what it may touch, when it stops |
| Context | Assemble deliberately, smallest high-signal set | Whole threads pasted | Section 06 rows on selection |
| State | Owned by a store, resumable | RAM watermarks and sessions | Section 03 |
| Tools | Few, namespaced, with actionable errors | 1,655 routes | About 15 agent tools |
| Permissions | Enforced outside the model in deterministic code | Auto-send rules table empty, so everything is manual or nothing | Autonomy slider per contact and intent, enforced in code |
| Evidence | Prove success from system state, never from the model's summary | Brief trusts its own text | Rule checks on every generated number |
| Recovery | By side-effect class: reads retry, sends reconcile, everything checkpoints | 401 retried 245 times | Error taxonomy, bounded retries, reconciliation for sends |

Turn every production failure into one of three things: an eval case, a narrower tool, or
a checkpoint. The 80 findings from the September audit are the backlog for that.

## Watch order for two people, one week

| Day | Watch | Minutes | Then do |
|---|---|---|---|
| 1 | Barry Zhang, "How We Build Effective Agents" | 15 | List Simba's engines; mark each workflow or agent |
| 1 | Karpathy at YC, "Software Is Changing (Again)" | 40 | Define the three autonomy-slider positions |
| 2 | Margot van Laar, "The prompting playbook" | 33 | Prompt audit of one engine (follow-up drafts) |
| 3 | Dex Horthy, "12-Factor Agents" (section 06) | 17 | Write the first `contract.md` |
| 4 | Husain and Shankar on evals, first 30 min (section 06) | 30 | Label 100 killed drafts |
| 5 | Ng, Interrupt 2026 talk | 30 | Draw the sense-making loop as a graph with typed edges |
| 6 | Read: Anthropic "Demystifying evals", Manus context engineering | 45 | Freeze the replay set (section 05) |
| 7 | Skim the harness engineering cluster | 30 | Fill the harness table above for one engine |

The unverified two-hour uploads (Karpathy Stanford, Ng Stanford) are optional. The verified
shorter talks carry the same ideas.
