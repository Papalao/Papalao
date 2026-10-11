"""TikTok Content Posting API.

Two modes, set by TIKTOK_MODE:
- inbox (default): the video lands in the creator's TikTok inbox as a draft; a human adds the caption
  and taps Post. Works before TikTok's app audit and keeps a person on every public post.
- direct: posts straight to the profile. Until the app passes TikTok's audit, every direct post is
  forced to SELF_ONLY (private), so leave this off until the audit is through.

Media must be on a URL prefix you verified in the TikTok developer portal (PULL_FROM_URL).
"""
from __future__ import annotations

import os

from . import Http, PublishError

API = "https://open.tiktokapis.com/v2"


class TikTok:
    def __init__(self, token: str | None = None, mode: str | None = None, audited: bool | None = None,
                 http: Http | None = None):
        self.token = token or os.environ.get("TIKTOK_ACCESS_TOKEN", "")
        self.mode = mode or os.environ.get("TIKTOK_MODE", "inbox")
        self.audited = audited if audited is not None else os.environ.get("TIKTOK_AUDITED", "false") == "true"
        self.http = http or Http()

    @classmethod
    def for_persona(cls, persona_id: str) -> "TikTok":
        """Each character is its own account: TIKTOK_ACCESS_TOKEN_KIBO, falling back to unsuffixed."""
        return cls(os.environ.get(f"TIKTOK_ACCESS_TOKEN_{persona_id.upper()}"))

    def _post(self, path: str, body: dict) -> dict:
        resp = self.http.post(f"{API}{path}", json=body, headers={
            "Authorization": f"Bearer {self.token}", "Content-Type": "application/json; charset=UTF-8"})
        err = resp.get("error", {})
        if err.get("code") not in (None, "ok"):
            raise PublishError(f"TikTok {path}: {err}")
        return resp.get("data", {})

    def plan(self, post: dict) -> dict:
        info = {
            "title": post["final_caption"],
            "privacy_level": "PUBLIC_TO_EVERYONE" if self.audited else "SELF_ONLY",
            "disable_comment": False, "disable_duet": False, "disable_stitch": False,
            # Own-brand promotion must carry TikTok's "Promotional content" label.
            "brand_organic_toggle": bool(post.get("skus")),
            # TikTok's AI-generated content label.
            "is_aigc": bool(post.get("uses_ai_visuals")),
        }
        source = {"source": "PULL_FROM_URL", "video_url": post.get("media_url", "")}
        if self.mode == "inbox":
            return {"platform": "tiktok", "mode": "inbox", "source_info": source,
                    "note": "caption, AI label and promo toggle are set by hand in the TikTok app",
                    "caption_to_paste": post["final_caption"]}
        return {"platform": "tiktok", "mode": "direct", "post_info": info, "source_info": source}

    def publish(self, post: dict, dry_run: bool = True) -> dict:
        plan = self.plan(post)
        if dry_run:
            return {"dry_run": True, **plan}
        if not self.token:
            raise PublishError("TIKTOK_ACCESS_TOKEN must be set")
        if self.mode == "inbox":
            data = self._post("/post/publish/inbox/video/init/", {"source_info": plan["source_info"]})
            return {"publish_id": data["publish_id"], "mode": "inbox"}

        creator = self._post("/post/publish/creator_info/query/", {})
        if plan["post_info"]["privacy_level"] not in creator.get("privacy_level_options", []):
            plan["post_info"]["privacy_level"] = "SELF_ONLY"
        data = self._post("/post/publish/video/init/",
                          {"post_info": plan["post_info"], "source_info": plan["source_info"]})
        return {"publish_id": data["publish_id"], "mode": "direct",
                "privacy_level": plan["post_info"]["privacy_level"]}

    def status(self, publish_id: str) -> dict:
        return self._post("/post/publish/status/fetch/", {"publish_id": publish_id})

    def video_stats(self, video_ids: list[str]) -> dict:
        data = self._post("/video/query/?fields=id,view_count,like_count,comment_count,share_count",
                          {"filters": {"video_ids": video_ids}})
        return {v["id"]: v for v in data.get("videos", [])}
