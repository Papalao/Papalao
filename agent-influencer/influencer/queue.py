"""Post lifecycle, one JSON file per post: draft -> approved -> published (or rejected / failed).

State lives on disk, never in process memory, so a crash or redeploy loses nothing and a
publish that already happened is never repeated (see the idempotency check in publish()).
"""
from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .catalog import Store
from .compliance import check
from .persona import Persona
from .tracking import cta_footer, make_code

STATUSES = ("draft", "approved", "published", "rejected", "failed")


class Queue:
    def __init__(self, root: str | Path = "data/posts"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, post_id: str) -> Path:
        return self.root / f"{post_id}.json"

    def save(self, post: dict) -> dict:
        tmp = self.path(post["id"]).with_suffix(".tmp")
        tmp.write_text(json.dumps(post, indent=2, ensure_ascii=False) + "\n")
        tmp.replace(self.path(post["id"]))
        return post

    def get(self, post_id: str) -> dict:
        return json.loads(self.path(post_id).read_text())

    def all(self, status: str | None = None, persona: str | None = None) -> list[dict]:
        posts = [json.loads(p.read_text()) for p in sorted(self.root.glob("*.json"))]
        return [p for p in posts
                if (status is None or p["status"] == status) and (persona is None or p["persona"] == persona)]

    def transition(self, post_id: str, status: str, **fields) -> dict:
        if status not in STATUSES:
            raise ValueError(f"unknown status {status}")
        post = self.get(post_id)
        post.update(fields, status=status, updated_at=datetime.now().astimezone().isoformat(timespec="seconds"))
        return self.save(post)


def scheduled_at(persona: Persona, start: date, day: int, slot: int) -> str:
    times = persona.posting["times_local"]
    hh, mm = (int(x) for x in times[min(max(slot, 0), len(times) - 1)].split(":"))
    tz = ZoneInfo(persona.posting.get("timezone", "UTC"))
    when = datetime.combine(start + timedelta(days=max(day, 1) - 1), time(hh, mm), tzinfo=tz)
    return when.isoformat()


def enqueue_plan(queue: Queue, persona: Persona, store: Store, start: date, posts: list[dict]) -> list[dict]:
    """Stamp ids, schedule, tracked code and footer onto raw model posts, check them, save as drafts."""
    saved = []
    seen: dict[tuple[int, int], int] = {}
    for raw in sorted(posts, key=lambda p: (p["day"], p["slot"])):
        key = (raw["day"], raw["slot"])
        seen[key] = seen.get(key, 0) + 1
        post_id = f"{persona.id}-{start:%Y%m%d}-d{raw['day']}s{raw['slot']}" + (f"-{seen[key]}" if seen[key] > 1 else "")
        code = make_code(persona.code_prefix, post_id)
        tags = " ".join(t if t.startswith("#") else f"#{t}" for t in raw.get("hashtags", []))
        post = {
            **raw,
            "id": post_id,
            "persona": persona.id,
            "status": "draft",
            "code": code,
            "scheduled_at": scheduled_at(persona, start, raw["day"], raw["slot"]),
            "final_caption": f"{raw['caption'].strip()}\n\n{cta_footer(persona, store, code)}\n\n{tags}".strip(),
            "media_url": "",
            "published": {},
        }
        post["issues"] = [str(i) for i in check(post, persona, store)]
        saved.append(queue.save(post))
    return saved
