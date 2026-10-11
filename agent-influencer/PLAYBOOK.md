# AI-character channels on the Simba store: the money plan

Two openly-AI characters, each running one Instagram and one TikTok account, selling real Simba
Coffee products. Every post carries its own WhatsApp order code, so every shilling is traced back to
the post that earned it, and next week's plan is written from what sold.

| | **Kibo** (channel 1) | **Kili** (channel 2) |
|---|---|---|
| Who | AI robot barista, Dar es Salaam, Swahili + English | AI coffee-trader robot, English, global |
| Sells | Cafe menu, TZS 3,000 to 14,000 (19 items) | Green coffee for export, AA / AB / PB / FAQ / RB, per kg |
| Buyer | Dar 18 to 34, orders today | Small roasters and cafe owners abroad |
| Hook | "I can't taste coffee, so you taste it for me" | "Tanzanian grades explained in 30 seconds" |
| Cadence | TikTok 2/day, Instagram 1/day | 1/day both |
| Win looks like | 1+ tracked order a day by day 30 | 2 to 4 qualified WhatsApp leads a month |

## Five decisions and why

1. **Openly AI, stylised robot, never a fake human.** Meta asks for an "AI info" label on photorealistic
   AI video and realistic audio, and TikTok asks for its AI-generated label on realistic AI content.
   A fake human who gets exposed loses the audience overnight. A robot is cheap to keep consistent
   from post to post, and being AI becomes the joke that sells the product. It is the Duolingo-owl
   playbook with Lil Miquela's openness.
2. **Real product footage, AI character around it.** Real drinks convert, rendered drinks don't. The
   store page currently shows Unsplash stock photos. Shoot every menu item before launch: showing stock
   photos as your drinks is misleading, and customers notice.
3. **Checkout stays WhatsApp + LIPA Namba.** TikTok Shop is not live in any African market, and the
   Simba store already turns a cart into a WhatsApp order. Don't build a new checkout.
4. **One code per post, with a perk.** People only quote a code if it gets them something (Kibo: a free
   extra shot, Kili: a free 1 kg sample). That small cost buys you revenue per post, and revenue per post
   is the only number the loop learns from.
5. **A human approves every post for the first 4 weeks.** `autonomy: review` in the persona file. Switch a
   character to `auto` only after 4 clean weeks. Compliant drafts then publish on schedule.

## Unit economics (replace the assumptions with your numbers)

| Line | Kibo, per month | Notes |
|---|---|---|
| Claude planning | about $2 | One call per character per week. The persona prompt is cached. |
| AI character clips | $50 to $150 | Your video tool. This is the real cost; cap it. |
| Real footage | $0 | One 2-hour phone shoot a week, batch everything |
| Perk cost | ~TZS 1,000 per order | Assumption: the cost of one extra shot |
| Average order | ~TZS 17,000 | Assumption: two drinks at the menu average of TZS 8,580 |
| Gross profit per order | ~TZS 9,000 | Assumption: 60% margin, minus the perk |
| **Break-even** | **~30 tracked orders a month, about 1 a day** | At $100 spend, roughly TZS 260,000 (rate ~2,600 TZS per USD, check today's rate) |

Kili: one 60 kg bag at the store's $8.40/kg is about $500 of revenue. One small roaster reordering
quarterly covers a year of production costs. **Fix the store before Kili goes live:** every export grade
shows the same $8.40/kg default. AA and PB must be priced above FAQ and RB, or Kili will quote one price
for every grade.

## Fastest cash: sell the engine, not just the coffee

Own channels take 60 to 90 days to compound. The quickest money is the same engine sold as a
done-for-you "AI character channel" to other Dar businesses: cafes, restaurants, salons, boutiques.

- Kibo's first 30 days of numbers are your case study.
- Kenyan bespoke WhatsApp bots run KES 5,000 to 25,000 a month plus KES 25,000 to 200,000 setup
  (`docs/simba-ai-research/07-monetization.md`, secondary source). Price above a bot: it is a channel
  that sells.
- Your marginal cost per client is a persona YAML, a catalog JSON, about $2 of Claude a month, their
  video budget, and about 2 hours a week of review.
- Once Kibo has an engaged local audience, other brands pay for placements. Use the platforms'
  paid-partnership labels.

## 30-day launch

**Days 1 to 2: setup**
1. Create both pairs of accounts with the same handle. Instagram: professional account (Creator or
   Business). TikTok: Business account, which gives you the bio link and the API, and limits you to the
   Commercial Music Library. That is fine: the planner only asks for library sounds.
2. Write the bio from the persona file. Put a `wa.me` link with a pre-filled "Hi Kibo" in the bio.
3. Character sheet: generate the character in about 10 poses and expressions from `visual_bible`. Keep
   the best one as the reference image for every later generation.
4. Shoot every menu item for real (9:16 and 4:5, daylight). Replace the stock photos on the store too.
5. Whoever answers WhatsApp logs coded orders: `python -m influencer order 17000 --message "<paste>"`.
6. Apply for API access: a Meta app with `instagram_business_content_publish`, and a TikTok developer
   app with the Content Posting API. Use inbox mode now, and submit the audit on day 1, because direct
   posting stays private until the audit passes.

**Week 1: launch**
- Sunday: `plan` for both characters. Review, reject what's weak, note what to film.
- Monday: one 2-hour batch shoot of every `real_shots` line. Render the week. Host the videos. Approve.
- Cron publishes on schedule. Answer every comment within the hour, in character. Comments are the
  cheapest reach there is.

**Weeks 2 to 4: the loop**
- Every Sunday: `stats --pull` (Instagram), enter TikTok numbers from the app with `stats`, then run
  `report --persona kibo`. Next `plan` reads those learnings automatically.
- Make more of the formats with revenue. Drop the bottom two hooks every week.

**Day 30 gate.** Continue a channel if it has 10 or more tracked orders (Kibo) or 2 or more qualified
leads (Kili), or saves plus shares above 2% of views. Otherwise change the concept, not the posting time.

## What to measure

- **North star:** tracked revenue per channel per week (`report`).
- **Leading:** 3-second hold and average watch time (in-app analytics), saves plus shares per view,
  profile visits to WhatsApp clicks, and comments.
- **Cost:** spend per tracked order. Untracked orders exist too, so treat the tracked number as a floor.

## Risks that kill accounts or money, and the fix

| Risk | Fix |
|---|---|
| No AI label | Bio disclosure plus a footer on every caption (the compliance gate blocks posts without it). On TikTok direct posts, `is_aigc` is set through the API. In inbox mode and on Instagram, toggle the label in the app. |
| Bot behaviour: auto-follow, auto-like, bought followers, engagement pods | Not built and never add it. That is how new accounts get shadowbanned. The engine only uses the official publishing APIs. |
| Copyrighted music | Commercial Music Library or original voice only. The planner never names songs. |
| Health claims ("boosts energy", "detox") | Banned phrases block the post. Add more per persona. |
| Filming customers | Written consent from every person in the taste-test series. The planner marks shots "with consent". |
| WhatsApp order line ban | If Simba answers that number through Baileys (unofficial), the line can be banned just when orders spike. Move it to the WhatsApp Business API before scaling (doc 07). |
| Tanzania licensing | TCRA's Online Content Regulations (2020, amended 2022 and 2025) license online content service providers. It is unclear whether a brand's social accounts with no news content need one. Get a one-hour local legal opinion before running paid promotion. |
| Customer data | The ledger stores code, amount and date only, never phone numbers. Keep it that way under Tanzania's Personal Data Protection Act 2022. |
| Lion King look-alike | "Simba" plus a cartoon lion invites a Disney dispute. The characters are robots; the lion appears only as a paw logo. |
| One price for every export grade | Fix the store before Kili goes live (see Unit economics). |

## Sources

- Instagram publishing limit of 100 API posts per 24 h, and the container flow: [Meta content publishing docs](https://developers.facebook.com/documentation/instagram-platform/content-publishing)
- TikTok unaudited clients are forced to private: [TikTok Direct Post reference](https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post), [bundle.social on the audit](https://bundle.social/blog/tiktok-api-approval)
- Instagram's 5-hashtag cap: [Social Media Today](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/)
- TikTok AI labels: [TikTok labeling announcement via NBC](https://www.nbcnewyork.com/news/national-international/tiktok-to-start-labeling-ai-generated-content-as-technology-becomes-more-universal/5399109); Meta AI disclosure: [NBC News](https://www.nbcnews.com/tech/facebook-instagram-to-label-ai-made-images-rcna137379)
- TikTok business accounts limited to the Commercial Music Library: [Soundstripe](https://www.soundstripe.com/blogs/why-can-i-only-use-commercial-sounds-on-tiktok) (vendor source)
- TikTok Shop markets, none in Africa: [PhotonPay list](https://www.photonpay.com/hk/blog/article/tiktok-shop-available-countries) (secondary)
- TCRA licensing: [Bowmans](https://bowmanslaw.com/insights/tanzania-amendments-to-the-regulations-under-the-electronic-and-postal-communications-act/), [Daily News](https://dailynews.co.tz/tcra-sounds-a-warning-to-unlicensed-online-service-providers/)
