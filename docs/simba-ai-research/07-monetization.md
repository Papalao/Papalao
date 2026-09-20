# Making money with Simba: what the market says in 2026

Sources verified by at least two independent search hits. Numbers that come only from
aggregator blogs are marked *(secondary)*. Meta developer docs, YC, a16z and Gartner pages
could not be opened directly from this environment.

## Pricing models that work for AI agents

| Source | Format | Rating |
|---|---|---|
| **Vertical AI Agents Could Be 10X Bigger Than SaaS**, Y Combinator Lightcone (Tan, Friedman, Taggar, Hu), 22 Nov 2024. https://www.ycombinator.com/library/Lt-vertical-ai-agents-could-be-10x-bigger-than-saas | Video, 42 min | WORTH |
| **AI Is Upending SaaS Pricing**, a16z, Martin Casado and Scott Woody (Metronome), 18 Jul 2025. https://a16z.com/podcast/ai-is-upending-saas-pricing/ | Podcast | WORTH |
| **Pricing your AI product: lessons from 400+ companies**, Madhavan Ramanujam on Lenny's Podcast, 27 Jul 2025. https://www.lennysnewsletter.com/p/pricing-and-scaling-your-ai-product-madhavan-ramanujam | Podcast, 90 min | MUST for pricing |
| **Intercom Fin outcome pricing**: Sacra research 27 Apr 2026 https://sacra.com/c/intercom/ ; Salesforce acquisition release 15 Jun 2026 https://www.salesforce.com/news/press-releases/2026/06/15/salesforce-signs-definitive-agreement-to-acquire-fin/ ; HubSpot per-resolution pricing 14 Apr 2026 https://www.hubspot.com/company-news/hubspots-customer-agent-and-prospecting-agent-now-you-pay-when-the-task-is-complete | Research, press | MUST |

What they say:

- **Sell the work, not the tool.** The wedge is one boring, hated, expensive workflow in one
  vertical. The "10x SaaS" and "300 unicorns" numbers are venture hype; the wedge advice is
  not.
- **The value metric moves from seats to output.** Salesforce Agentforce at $2 per
  conversation, Zendesk seats at $115 per month. Hybrid pricing (platform fee plus usage or
  outcomes) is the default now. Pure outcome pricing needs a countable, attributable outcome
  and metering you must build.
- **95% of AI startups price the feature, not the job removed** (Ramanujam). Run the pilot
  as business-case creation with an agreed outcome metric, then charge on it. Anchor on the
  cost of the human it replaces.
- **Intercom Fin is the proof case.** $0.99 per resolved conversation, escalations free,
  50-outcome monthly minimum. Passed $100M ARR growing about 350%, around 8,000 customers,
  and Salesforce agreed to buy it for about $3.6B. They gave up around $60M of seat revenue
  to get there. HubSpot has since cut to $0.50 per resolution. The floor is falling.
- **Warning from the operators:** agent gross margins are far below SaaS. Grow fast or die
  on compute. Section 02 (caching, lanes, batch) is the margin.

## WhatsApp in East Africa: rules and costs that changed this year

| Source | What changed |
|---|---|
| Meta WhatsApp Business Platform pricing docs https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing ; explainers by 360dialog https://360dialog.com/blog/whatsapp-service-message-charging-october-2026/ and SendPulse https://sendpulse.com/blog/whatsapp-service-message-pricing | Per delivered template message since 1 Jul 2025. Nigeria card 1 Apr 2026: marketing $0.0516, utility $0.0067, authentication $0.0145. Kenya and Tanzania sit in the same "Rest of Africa" tier *(secondary)*. **From 1 Oct 2026 service replies inside the 24-hour window become billable** at the utility rate, 1,000 free per number per month. No payment method by 30 Sep 2026 means delivery stops. |
| Meta bans general-purpose AI chatbots on the Business API, effective 15 Jan 2026. Explainer https://respond.io/blog/whatsapp-general-purpose-chatbots-ban ; news https://techradar.com/ai-platforms-assistants/meta-will-ban-rival-ai-chatbots-from-whatsapp | Open-domain assistants (ChatGPT, Perplexity, Copilot) were removed. Bots scoped to support, orders, bookings, notifications and sales remain allowed. |
| Meta Business Agent (Meta's own bot) on token billing since 1 Aug 2026 *(secondary)* | About $2 per million tokens, roughly $0.04 to $0.05 per message. Meta is now both the toll collector and a subsidised competitor. |

What this means for Simba, bluntly:

- **Simba's WhatsApp runs on Baileys, not the Business API.** That means none of the
  per-message billing applies today, and all of the account-ban risk does. Baileys is an
  unofficial client. For Anton's own lines it is a calculated risk. For paying tenants it is
  a liability: a banned number takes their business channel down. Any sold WhatsApp product
  must move to the Business API through a provider, and be priced above the Meta toll.
- **Scope the bot to business workflows and say so in app review.** "Ask Simba anything"
  is exactly what Meta removed. "Simba sends your invoices, chases payments and books
  orders" is allowed.
- **Cost model:** an assistant sending 3,000 replies a month pays Meta roughly $13 a month
  at the Nigeria-tier utility rate. Price the tenant well above that. Steer long
  conversations to Telegram or web, where the toll is zero.

## What African and emerging-market operators actually charge

| Operator | Source | Product and price | Lesson |
|---|---|---|---|
| Sukhiba (Kenya) | https://techpoint.africa/2024/08/27/kenyas-sukhiba-connect-extension/ | B2B reorder plus M-Pesa inside WhatsApp; 35,000+ SMEs ordering; live in Kenya, Tanzania, Uganda, Rwanda, Nigeria | One job (reorder and pay). Not a business OS. |
| tappi with M-Pesa (Kenya) | https://techpoint.africa/2024/10/22/tappi-solution-grow-mpesa-businesses/ | KSh 1,350 (about $11) a month bundle; claims 90% retention, 1.5-month payback; distributed by Safaricom to 650,000 M-Pesa merchants | Distribution partner beats product breadth. |
| InvoChatng (Nigeria) | https://businessday.ng/opinion/article/invochatng-aiforsme-brings-invoicing-payments-and-record-keeping-to-whatsapp-for-nigerian-smes/ | Plain-language sale becomes PDF invoice plus payment link in WhatsApp | That single flow is the whole product. |
| Jio Haptik (India) | https://tecknexus.com/jio-haptik-whatsapp-ai-agents-for-smbs-from-%E2%82%B910000/ | About ₹10,000 for 2,000 conversations, roughly ₹35 each | Conversation-bundle pricing is understood by SMEs. Ignore its conversion-lift claims. |
| Kenya bespoke bot market *(secondary)* | | KES 5,000 to 25,000 per month run fees, KES 25,000 to 200,000 setup | The floor for a done-for-you bot. Payments via M-Pesa Daraja STK push; Vodacom Tanzania has opened M-Pesa APIs. |

## What earns revenue and what is vanity

| Source | Finding |
|---|---|
| **The GenAI Divide: State of AI in Business 2025**, MIT NANDA, Jul 2025. https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf | 95% of pilots showed no profit-and-loss impact. Over half of budgets went to sales and marketing bots; measurable return came from back-office automation: invoicing, procurement, admin. Tools are abandoned when they do not retain context or learn from feedback. |
| **Gartner: over 40% of agentic AI projects cancelled by end of 2027**, 25 Jun 2025. https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027 | Causes: cost, unclear value, weak risk controls. Of thousands of vendors only about 130 have real agents. Value appears where an agent completes a countable task. |
| **Tidemark 2025 Vertical and SMB SaaS Benchmark**, with Stripe, Q4 2025. https://www.tidemarkcap.com/vskp-chapter/2025-vertical-smb-saas-benchmark-report | Median AI attach rate went from 22% to 59% in a year. Companies selling AI grow about 8 points faster. Fintech and payments is the number one second product for 45% of vertical SaaS companies. |

The MIT finding indicts Simba's memory directly: 2.5M rows written and never surfaced in
the workflow is dead weight of exactly the kind that gets a tool abandoned.

## Cost control sources (complements section 02)

- **Don't Break the Cache**, Lumer et al. (PwC), arXiv 2601.06007, Jan 2026.
  https://arxiv.org/abs/2601.06007 . Across 500 agent sessions with 10k-token system prompts,
  caching cut cost 41 to 80% and time to first token 13 to 31%. Dynamic content goes at the
  end; a dynamic block mid-context invalidates the cache and can raise latency.
- **RouteLLM**, LMSYS, Jul 2024. https://www.lmsys.org/blog/2024-07-01-routellm/ . 85% cost
  cut at 95% of top-model quality by sending only 14 to 26% of calls to the strong model.
  Benchmark-based and dated; for Simba a deterministic intent router beats a learned one.
- Anthropic's own reported agent numbers: loops 2.5 to 3.7x cheaper at 81 to 90% cache hit
  rates; a small triage agent's bill fell 83% from caching alone. Haiku answered lookup
  questions at about a tenth of Opus cost at 63% versus 92% accuracy: fine for CRUD and
  lookups, not for finance reasoning.

## The money plan, in order

1. **Pick one countable outcome per market and price it.** Candidates from Simba's own
   modules: "invoice sent and paid via M-Pesa", "payment chased to confirmation", "tender
   packet drafted and submitted". Hybrid: $10 to $30 a month base plus a per-outcome fee,
   priced above the Meta toll. Intercom charges $0.99 per resolution in the US; East African
   SME willingness sits nearer the tappi bundle at $11 a month, so the outcome fee must be
   small and the base must carry the margin.
2. **Back office before front office.** Payment chasing, procurement, bookkeeping had the
   only measured return in the MIT data. Simba's follow-up engine, once it actually sends
   (section 01, weak point 3), is that product.
3. **Move sold WhatsApp traffic off Baileys** and onto the Business API through a provider
   before selling it to anyone. Scope to workflows for Meta's app review.
4. **Find a distribution partner** in the tappi and Safaricom pattern: a mobile-money
   operator, a bank's SME desk, or an accounting firm with SME clients. Worth more than any
   new module.
5. **Freeze the 1,655-route surface.** Log which routes paying tenants hit for 30 days. Hide
   or delete the rest. The cost-per-engine column from section 02 makes this a data decision.
6. **Fix caching before touching model choice.** It is the larger and safer saving.

## What to ignore

- "3 websites that make $100k a month" style content: unverifiable, sells courses.
- Vendor conversion-lift claims (Haptik's "2025%").
- The "10x SaaS" total addressable market framing. The wedge advice from the same talk is
  the useful part.
