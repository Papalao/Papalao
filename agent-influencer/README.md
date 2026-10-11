# agent-influencer

AI-character Instagram and TikTok channels that sell from the Simba store. Read
[PLAYBOOK.md](PLAYBOOK.md) first for the business plan; this file covers running the engine.

```
store page ──import──> catalog ─┐
persona YAML ───────────────────┼──> plan (Claude) ──> drafts ──compliance──> review ──> approve + media
last week's sales ──learnings───┘                                                         │
WhatsApp order "code KIBO-M6D2" ──order──> ledger <──stats── platforms <──publish (cron)───┘
```

## What it does, what you do

| Engine | You |
|---|---|
| Writes the week per character: hook, beat-by-beat script, AI shot prompts, real shots to film, caption, at most 5 hashtags, pinned comment, sound mood | Film the real shots in one weekly batch, render the AI shots with your video tool, edit |
| Stamps a unique order code and perk, the AI disclosure and the schedule on every post | Approve or reject each post (`autonomy: review`) |
| Blocks unknown products, wrong prices, health claims, "I'm human", too many hashtags, a missing disclosure or code | Host the final video at a public HTTPS URL |
| Publishes on schedule through the official Instagram and TikTok APIs, never twice | Answer comments in character |
| Turns orders and stats into learnings that next week's plan reads | Log coded WhatsApp orders (or let Simba's intake do it) |

## Setup

```bash
cd agent-influencer
pip install -r requirements.txt
cp .env.example .env    # fill in keys; export them in your shell or cron
python -m influencer import-catalog --html ../../simba-coffee/index.html --store-url https://<your-store-url>
python -m pytest -q     # 25 tests, no network
```

## Weekly loop

```bash
# Sunday: plan (prints the prompt only with --show-prompt; costs nothing)
python -m influencer plan --persona personas/kibo.yaml --notes "Matcha push this week, rainy days"
python -m influencer plan --persona personas/kili.yaml
python -m influencer review --full

# After filming and rendering: approve with the hosted media (several URLs = Instagram carousel)
python -m influencer approve kibo-20261012-d1s0 --media https://cdn.example.com/kibo/d1s0.mp4
python -m influencer reject  kibo-20261012-d2s1 --reason "weak hook"

# Cron every 15 minutes. Drop --live to see what would be sent.
*/15 * * * * cd /path/agent-influencer && python -m influencer publish --live >> data/publish.log 2>&1

# Sales and stats
python -m influencer order 17000 --message "Habari, nataka latte mbili. code kibo m6d2"
python -m influencer stats --pull                                   # Instagram insights
python -m influencer stats kibo-20261012-d1s0 tiktok views=5400 shares=61 saved=33
python -m influencer report --persona kibo                          # what next week's plan will read
```

## Accounts and keys

| Variable | What |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API. The model is `claude-opus-5-5` at `high` effort; override with `INFLUENCER_MODEL` / `INFLUENCER_EFFORT`. About $0.50 per character per week. |
| `IG_USER_ID_<ID>`, `IG_ACCESS_TOKEN_<ID>` | Per character, e.g. `IG_USER_ID_KIBO`. Professional account, token with `instagram_business_content_publish` (Instagram API with Instagram Login). |
| `TIKTOK_ACCESS_TOKEN_<ID>` | Per character. TikTok developer app with the Content Posting API. Verify your media URL prefix in the TikTok portal (PULL_FROM_URL). |
| `TIKTOK_MODE` | `inbox` (default): video lands as a draft in the TikTok app, a human pastes the caption and posts. `direct`: posts straight away, but stays private until TikTok's audit passes. |
| `TIKTOK_AUDITED` | `true` only after the audit; then direct posts go public. |

## Plugging into Simba

- **WhatsApp intake:** `influencer.tracking.extract_codes(text, ["KIBO", "KILI"])` finds codes in an
  incoming message, case-insensitive, with or without the dash. Call it where Simba ingests WhatsApp
  messages and write `{code, amount}` to `data/orders.csv`, or call `python -m influencer order`.
- **Store page:** to tag web-cart orders too, pass the `?ref=` code into the WhatsApp order text in
  `simba-coffee/index.html` (separate repo, not changed here):
  ```js
  const REF = new URLSearchParams(location.search).get("ref") || "";
  // append to the cart's WhatsApp message:  + (REF ? `\nCode: ${REF}` : "")
  ```
- **New character or new store:** copy a persona YAML, set `categories` to the catalog slice it sells,
  and set its own `code_prefix`. For another store, write a catalog JSON with the same fields as
  `catalog/simba_coffee.json`.

## Files

| Path | What |
|---|---|
| `personas/*.yaml` | Character bible: voice, visual bible, pillars, formats, banned phrases, cadence, autonomy |
| `catalog/simba_coffee.json` | Products imported from the store page; the only things a character may sell |
| `influencer/brain.py` | The Claude call: structured JSON output, cached persona prompt, server-side refusal fallback |
| `influencer/compliance.py` | The rules gate |
| `influencer/tracking.py` | Order codes, WhatsApp links, the caption footer |
| `influencer/queue.py` | One JSON file per post in `data/posts/`, atomic writes, schedule |
| `influencer/publish/` | Instagram and TikTok publishers, dry-run by default |
| `influencer/metrics.py` | Orders ledger, stats, scoreboard, learnings |
| `data/` | Runtime state (git-ignored) |
