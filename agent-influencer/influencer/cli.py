"""Operator commands. Run `python -m influencer --help`.

Weekly loop:  plan -> review -> (film/render, set media) -> approve -> publish (cron) -> order/stats -> report -> plan
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from .catalog import Store, import_simba_coffee
from .compliance import blocking, check
from .metrics import Ledger, learnings, scoreboard
from .persona import Persona, system_prompt
from .publish import PublishError
from .queue import Queue, enqueue_plan
from .tracking import extract_codes

ROOT = Path(__file__).resolve().parent.parent


def _personas(directory: Path) -> dict[str, Persona]:
    return {p.id: p for p in (Persona.load(f) for f in sorted(directory.glob("*.yaml")))}


def _client(platform: str, persona_id: str):
    from .publish.instagram import Instagram
    from .publish.tiktok import TikTok
    return {"instagram": Instagram, "tiktok": TikTok}[platform].for_persona(persona_id)


def _next_monday(today: date) -> date:
    return today + timedelta(days=(7 - today.weekday()) % 7 or 7)


def cmd_import_catalog(a) -> int:
    store = import_simba_coffee(Path(a.html).read_text(), store_url=a.store_url)
    store.save(a.out)
    print(f"{len(store.products)} products -> {a.out} (WhatsApp {store.whatsapp_e164}, {store.payment_note})")
    return 0


def cmd_plan(a) -> int:
    persona, store = Persona.load(a.persona), Store.load(a.catalog)
    start = date.fromisoformat(a.start) if a.start else _next_monday(date.today())
    queue, ledger = Queue(Path(a.data) / "posts"), Ledger(a.data)
    lessons = learnings(scoreboard(queue.all(persona=persona.id), ledger), persona.id)
    if a.show_prompt:
        from .brain import week_request
        print(system_prompt(persona, store), "\n\n---\n", week_request(persona, start, lessons, a.notes))
        return 0

    from .brain import PlanError, plan_week
    try:
        posts, usage = plan_week(persona, store, start, lessons, a.notes)
    except PlanError as exc:
        print(f"plan failed: {exc}", file=sys.stderr)
        return 1
    saved = enqueue_plan(queue, persona, store, start, posts)
    flagged = sum(1 for p in saved if any(i.startswith("[block]") for i in p["issues"]))
    print(f"{len(saved)} drafts for {persona.id}, week of {start} ({flagged} blocked by compliance). usage: {json.dumps(usage)}")
    return 0


def cmd_review(a) -> int:
    for p in Queue(Path(a.data) / "posts").all(status=a.status, persona=a.persona):
        mark = "BLOCKED" if any(i.startswith("[block]") for i in p["issues"]) else "ok"
        print(f"\n== {p['id']}  {p['scheduled_at'][:16]}  {'+'.join(p['platforms'])}  {p['format']}  [{mark}]")
        print(f"   hook: {p['hook_text']}  |  skus: {', '.join(p['skus']) or '-'}  |  code: {p['code']}")
        if a.full:
            for b in p["script"]:
                print(f"   {b['t']:>8}  {b['visual']}  // {b['voice']}  [{b['on_screen']}]")
            print("   real shots:", "; ".join(p["real_shots"]))
            print("   AI shots:  ", "; ".join(p["ai_shots"]))
            print("   caption:\n     " + p["final_caption"].replace("\n", "\n     "))
        for i in p["issues"]:
            print(f"   {i}")
    return 0


def cmd_approve(a) -> int:
    queue = Queue(Path(a.data) / "posts")
    personas, store = _personas(Path(a.personas)), Store.load(a.catalog)
    post = queue.get(a.id)
    if a.media:
        post["media_url"], post["media_urls"] = a.media[0], a.media
    issues = check(post, personas[post["persona"]], store)
    if blocking(issues):
        print("cannot approve:\n" + "\n".join(str(i) for i in issues), file=sys.stderr)
        return 1
    queue.transition(a.id, "approved", media_url=post["media_url"], media_urls=post.get("media_urls", []),
                     issues=[str(i) for i in issues])
    print(f"approved {a.id}" + ("" if post["media_url"] else " (no media yet: set it before publish time)"))
    return 0


def cmd_reject(a) -> int:
    Queue(Path(a.data) / "posts").transition(a.id, "rejected", reject_reason=a.reason)
    print(f"rejected {a.id}")
    return 0


def cmd_publish(a) -> int:
    queue = Queue(Path(a.data) / "posts")
    now = datetime.fromisoformat(a.now) if a.now else datetime.now().astimezone()
    personas = _personas(Path(a.personas))
    # autonomy=auto personas skip human review: their clean drafts are treated as approved.
    candidates = queue.all(status="approved") + [
        p for p in queue.all(status="draft")
        if personas[p["persona"]].autonomy == "auto" and not any(i.startswith("[block]") for i in p["issues"])]
    due = [p for p in candidates if datetime.fromisoformat(p["scheduled_at"]) <= now]
    if not due:
        print("nothing due")
    for post in due:
        if not post.get("media_url"):
            print(f"skip {post['id']}: no media_url")
            continue
        results = dict(post.get("published", {}))
        for platform in post["platforms"]:
            if platform in results:  # already live: never double-post after a crash
                continue
            try:
                res = _client(platform, post["persona"]).publish(post, dry_run=not a.live)
            except PublishError as exc:
                print(f"FAIL {post['id']} {platform}: {exc}")
                if a.live:
                    queue.transition(post["id"], "failed", published=results, error=str(exc))
                break
            print(f"{'LIVE' if a.live else 'DRY '} {post['id']} {platform}: {json.dumps(res, ensure_ascii=False)[:300]}")
            if a.live:
                results[platform] = res
                queue.transition(post["id"], "approved", published=results)  # checkpoint per platform
        else:
            if a.live:
                queue.transition(post["id"], "published", published=results)
    return 0


def cmd_order(a) -> int:
    ledger = Ledger(a.data)
    codes = [a.code] if a.code else extract_codes(a.message or "", [p.code_prefix for p in _personas(Path(a.personas)).values()])
    if not codes:
        print("no order code found", file=sys.stderr)
        return 1
    known = {p["code"] for p in Queue(Path(a.data) / "posts").all()}
    for code in codes:
        row = ledger.add_order(code, a.amount, a.currency, a.note)
        print(f"order {row['code']} {row['amount']:,.0f} {row['currency']}" + ("" if row["code"] in known else "  (unknown code)"))
    return 0


def cmd_stats(a) -> int:
    ledger, queue = Ledger(a.data), Queue(Path(a.data) / "posts")
    if a.pull:
        for p in queue.all(status="published"):
            media_id = p.get("published", {}).get("instagram", {}).get("media_id")
            if media_id:
                try:
                    ledger.add_stats(p["id"], "instagram", _client("instagram", p["persona"]).insights(media_id))
                    print(f"pulled instagram stats for {p['id']}")
                except PublishError as exc:
                    print(f"stats failed for {p['id']}: {exc}")
        return 0
    stats = {k: float(v) for k, v in (kv.split("=", 1) for kv in a.values)}
    ledger.add_stats(a.id, a.platform, stats)
    print(f"stats saved for {a.id} {a.platform}: {stats}")
    return 0


def cmd_report(a) -> int:
    rows = scoreboard(Queue(Path(a.data) / "posts").all(persona=a.persona), Ledger(a.data))
    if not rows:
        print("no published posts yet")
        return 0
    print(f"{'post':32} {'format':18} {'orders':>6} {'revenue':>12} {'views':>8} {'save+share':>10}")
    for r in rows:
        print(f"{r['id']:32} {r['format'][:18]:18} {r['orders']:>6} {r['revenue']:>12,.0f} {r['views']:>8,} {r['save_share_rate']:>10.1%}")
    if a.persona:
        print("\nLearnings fed to next plan:\n" + learnings(rows, a.persona))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="influencer", description=__doc__)
    ap.add_argument("--data", default=str(ROOT / "data"))
    ap.add_argument("--personas", default=str(ROOT / "personas"))
    ap.add_argument("--catalog", default=str(ROOT / "catalog" / "simba_coffee.json"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("import-catalog", help="read products from the Simba store page")
    s.add_argument("--html", required=True)
    s.add_argument("--store-url", default="")
    s.add_argument("--out", default=str(ROOT / "catalog" / "simba_coffee.json"))
    s.set_defaults(fn=cmd_import_catalog)

    s = sub.add_parser("plan", help="write next week's posts for one character")
    s.add_argument("--persona", required=True, help="path to personas/<id>.yaml")
    s.add_argument("--start", help="YYYY-MM-DD, default next Monday")
    s.add_argument("--notes", default="", help="this week's push, events, stock, offers already approved")
    s.add_argument("--show-prompt", action="store_true", help="print the prompt, do not call the API")
    s.set_defaults(fn=cmd_plan)

    s = sub.add_parser("review", help="list posts with compliance results")
    s.add_argument("--status", default="draft")
    s.add_argument("--persona")
    s.add_argument("--full", action="store_true")
    s.set_defaults(fn=cmd_review)

    s = sub.add_parser("approve", help="approve a draft, optionally attaching hosted media URLs")
    s.add_argument("id")
    s.add_argument("--media", nargs="*", default=[])
    s.set_defaults(fn=cmd_approve)

    s = sub.add_parser("reject")
    s.add_argument("id")
    s.add_argument("--reason", required=True)
    s.set_defaults(fn=cmd_reject)

    s = sub.add_parser("publish", help="publish due approved posts (dry-run unless --live); run from cron")
    s.add_argument("--live", action="store_true")
    s.add_argument("--now", help="override clock, ISO datetime")
    s.set_defaults(fn=cmd_publish)

    s = sub.add_parser("order", help="record a WhatsApp sale against a post code")
    s.add_argument("amount", type=float)
    s.add_argument("--code")
    s.add_argument("--message", help="paste the customer's WhatsApp message; the code is extracted")
    s.add_argument("--currency", default="TZS")
    s.add_argument("--note", default="")
    s.set_defaults(fn=cmd_order)

    s = sub.add_parser("stats", help="record post stats manually, or --pull from Instagram")
    s.add_argument("id", nargs="?")
    s.add_argument("platform", nargs="?", choices=["instagram", "tiktok"])
    s.add_argument("values", nargs="*", help="views=1200 saved=40 shares=12")
    s.add_argument("--pull", action="store_true")
    s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("report", help="revenue per post and the learnings for next week")
    s.add_argument("--persona")
    s.set_defaults(fn=cmd_report)

    a = ap.parse_args(argv)
    return a.fn(a)
