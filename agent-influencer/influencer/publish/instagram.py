"""Instagram Content Publishing API: create container -> wait for FINISHED -> media_publish.

Needs a professional (Business/Creator) account and a token with instagram_content_publish
(Instagram API with Instagram Login: host graph.instagram.com, scope instagram_business_content_publish).
Media must be at a public HTTPS URL; Meta fetches it. Limit: 100 API-published posts per 24 h.
"""
from __future__ import annotations

import os

from . import Http, PublishError

HOST = os.environ.get("IG_GRAPH_HOST", "https://graph.instagram.com")
VERSION = os.environ.get("IG_GRAPH_VERSION", "v24.0")


class Instagram:
    def __init__(self, user_id: str | None = None, token: str | None = None, http: Http | None = None):
        self.user_id = user_id or os.environ.get("IG_USER_ID", "")
        self.token = token or os.environ.get("IG_ACCESS_TOKEN", "")
        self.http = http or Http()
        self.base = f"{HOST}/{VERSION}"

    @classmethod
    def for_persona(cls, persona_id: str) -> "Instagram":
        """Each character is its own account: IG_USER_ID_KIBO / IG_ACCESS_TOKEN_KIBO, falling back to unsuffixed."""
        sfx = f"_{persona_id.upper()}"
        return cls(os.environ.get("IG_USER_ID" + sfx), os.environ.get("IG_ACCESS_TOKEN" + sfx))

    def _container(self, **params) -> str:
        body = self.http.post(f"{self.base}/{self.user_id}/media", data={**params, "access_token": self.token})
        return body["id"]

    def _wait(self, container_id: str, tries: int = 30, every: float = 10.0) -> None:
        for _ in range(tries):
            status = self.http.get(f"{self.base}/{container_id}",
                                   params={"fields": "status_code", "access_token": self.token})
            code = status.get("status_code")
            if code == "FINISHED":
                return
            if code in ("ERROR", "EXPIRED"):
                raise PublishError(f"container {container_id} {code}: {status}")
            self.http.sleep(every)
        raise PublishError(f"container {container_id} not ready after {tries * every:.0f}s")

    def plan(self, post: dict) -> dict:
        """What would be sent, without sending it."""
        urls = [u for u in (post.get("media_urls") or [post.get("media_url")]) if u]
        if not urls:
            raise PublishError(f"{post['id']} has no media_url; render and host the video first")
        kind = "CAROUSEL" if len(urls) > 1 else ("IMAGE" if urls[0].lower().endswith((".jpg", ".jpeg", ".png")) else "REELS")
        return {"platform": "instagram", "kind": kind, "media": urls, "caption": post["final_caption"]}

    def publish(self, post: dict, dry_run: bool = True) -> dict:
        plan = self.plan(post)
        if dry_run:
            return {"dry_run": True, **plan}
        if not (self.user_id and self.token):
            raise PublishError("IG_USER_ID and IG_ACCESS_TOKEN must be set")

        caption, urls = plan["caption"], plan["media"]
        if plan["kind"] == "CAROUSEL":
            children = []
            for url in urls:
                is_image = url.lower().endswith((".jpg", ".jpeg", ".png"))
                child = self._container(is_carousel_item="true",
                                        **({"image_url": url} if is_image else {"media_type": "VIDEO", "video_url": url}))
                self._wait(child)
                children.append(child)
            container = self._container(media_type="CAROUSEL", children=",".join(children), caption=caption)
        elif plan["kind"] == "IMAGE":
            container = self._container(image_url=urls[0], caption=caption)
        else:
            container = self._container(media_type="REELS", video_url=urls[0], caption=caption, share_to_feed="true")
        self._wait(container)

        media_id = self.http.post(f"{self.base}/{self.user_id}/media_publish",
                                  data={"creation_id": container, "access_token": self.token})["id"]
        link = self.http.get(f"{self.base}/{media_id}", params={"fields": "permalink", "access_token": self.token})
        return {"media_id": media_id, "permalink": link.get("permalink", "")}

    def insights(self, media_id: str) -> dict:
        """Reel/post metrics. Metric names change between Graph versions; adjust IG_METRICS if Meta renames them."""
        metrics = os.environ.get("IG_METRICS", "reach,views,saved,shares,comments,likes,total_interactions")
        body = self.http.get(f"{self.base}/{media_id}/insights", params={"metric": metrics, "access_token": self.token})
        return {m["name"]: (m.get("values") or [{}])[0].get("value", m.get("total_value", {}).get("value"))
                for m in body.get("data", [])}
