"""The learning loop: orders and platform stats per post -> a scoreboard -> plain-language learnings
that go into next week's plan. Revenue is the metric; views and saves only break ties.

Same discipline as the nightly hillclimb in docs/simba-ai-research/05: one number, fixed
window, keep what wins, drop what doesn't.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

ORDER_FIELDS = ["at", "code", "amount", "currency", "note"]


class Ledger:
    def __init__(self, root: str | Path = "data"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.orders_path = self.root / "orders.csv"
        self.stats_path = self.root / "stats.jsonl"

    def add_order(self, code: str, amount: float, currency: str, note: str = "") -> dict:
        row = {"at": datetime.now().astimezone().isoformat(timespec="seconds"), "code": code.upper(),
               "amount": amount, "currency": currency, "note": note}
        new = not self.orders_path.exists()
        with self.orders_path.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=ORDER_FIELDS)
            if new:
                w.writeheader()
            w.writerow(row)
        return row

    def orders(self) -> list[dict]:
        if not self.orders_path.exists():
            return []
        with self.orders_path.open() as f:
            return [{**r, "amount": float(r["amount"])} for r in csv.DictReader(f)]

    def add_stats(self, post_id: str, platform: str, stats: dict) -> None:
        with self.stats_path.open("a") as f:
            f.write(json.dumps({"at": datetime.now().astimezone().isoformat(timespec="seconds"),
                                "post_id": post_id, "platform": platform, "stats": stats}) + "\n")

    def latest_stats(self) -> dict[tuple[str, str], dict]:
        latest: dict[tuple[str, str], dict] = {}
        if self.stats_path.exists():
            for line in self.stats_path.read_text().splitlines():
                rec = json.loads(line)
                latest[(rec["post_id"], rec["platform"])] = rec["stats"]
        return latest


def _num(v) -> float:
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def scoreboard(posts: list[dict], ledger: Ledger) -> list[dict]:
    by_code: dict[str, list[dict]] = {}
    for o in ledger.orders():
        by_code.setdefault(o["code"], []).append(o)
    stats = ledger.latest_stats()

    rows = []
    for p in posts:
        if p["status"] != "published":
            continue
        views = saves = shares = 0.0
        for platform in p.get("platforms", []):
            s = stats.get((p["id"], platform), {})
            views += _num(s.get("views") or s.get("view_count") or s.get("reach"))
            saves += _num(s.get("saved"))
            shares += _num(s.get("shares") or s.get("share_count"))
        orders = by_code.get(p["code"], [])
        rows.append({
            "id": p["id"], "persona": p["persona"], "format": p.get("format", ""), "pillar": p.get("pillar", ""),
            "hook": p.get("hook_text", ""), "hypothesis": p.get("hypothesis", ""), "code": p["code"],
            "orders": len(orders), "revenue": sum(o["amount"] for o in orders),
            "views": int(views), "save_share_rate": round((saves + shares) / views, 4) if views else 0.0,
        })
    rows.sort(key=lambda r: (r["revenue"], r["orders"], r["save_share_rate"], r["views"]), reverse=True)
    return rows


def learnings(rows: list[dict], persona: str, top: int = 3) -> str:
    """What the planner reads next week. Plain text, facts only."""
    mine = [r for r in rows if r["persona"] == persona]
    if not mine:
        return ""

    def line(r: dict) -> str:
        return (f"- [{r['format']} / {r['pillar']}] hook \"{r['hook']}\": {r['orders']} orders, revenue {r['revenue']:,.0f}, "
                f"{r['views']:,} views, save+share rate {r['save_share_rate']:.1%}. Bet was: {r['hypothesis']}")

    total_rev = sum(r["revenue"] for r in mine)
    total_orders = sum(r["orders"] for r in mine)
    by_format: dict[str, float] = {}
    for r in mine:
        by_format[r["format"]] = by_format.get(r["format"], 0) + r["revenue"]
    fmt = ", ".join(f"{k}: {v:,.0f}" for k, v in sorted(by_format.items(), key=lambda kv: -kv[1]))
    return "\n".join([
        f"{len(mine)} posts published, {total_orders} tracked orders, revenue {total_rev:,.0f}.",
        f"Revenue by format: {fmt}.",
        "Winners (make more like these, vary the hook):",
        *[line(r) for r in mine[:top]],
        "Losers (do not repeat the hook or angle):",
        *[line(r) for r in mine[-top:] if r not in mine[:top]],
    ])
