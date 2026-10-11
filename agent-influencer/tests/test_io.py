"""Planner and publishers against fakes: no API key, no network."""
import json
from datetime import date
from types import SimpleNamespace

import pytest

from influencer import brain, cli
from influencer.publish import Http, PublishError
from influencer.publish.instagram import Instagram
from influencer.publish.tiktok import TikTok
from influencer.queue import Queue, enqueue_plan


class FakeStream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


class FakeClient:
    def __init__(self, message):
        self.calls = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))
        self.message = message

    def _stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeStream(self.message)


def _message(text="", stop_reason="end_turn"):
    usage = SimpleNamespace(input_tokens=900, cache_read_input_tokens=2100, cache_creation_input_tokens=0,
                            output_tokens=7000)
    return SimpleNamespace(stop_reason=stop_reason, stop_details=None, model=brain.MODEL, usage=usage,
                           content=[SimpleNamespace(type="text", text=text)])


def test_plan_week_sends_cached_structured_request(kibo, store, raw_post):
    client = FakeClient(_message(json.dumps({"posts": [raw_post]})))
    posts, usage = brain.plan_week(kibo, store, date(2026, 10, 12), "won: taste tests", "", client=client)
    assert posts == [raw_post] and usage["cache_read_input_tokens"] == 2100
    call = client.calls[0]
    assert call["fallbacks"] == "default" and "server-side-fallback-2026-07-01" in call["betas"]
    assert call["output_config"]["format"]["schema"] is brain.PLAN_SCHEMA
    assert call["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "2026" not in call["system"][0]["text"], "dates in the system prompt would break caching"
    assert "won: taste tests" in call["messages"][0]["content"]


@pytest.mark.parametrize("stop", ["refusal", "max_tokens"])
def test_plan_week_raises_on_bad_stop(kibo, store, stop):
    with pytest.raises(brain.PlanError):
        brain.plan_week(kibo, store, date(2026, 10, 12), client=FakeClient(_message("", stop)))


class FakeResp:
    def __init__(self, body, status=200):
        self.body, self.status_code, self.text = body, status, json.dumps(body)

    def json(self):
        return self.body


class FakeSession:
    """Answers by URL substring, records every call."""

    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def _answer(self, method, url, kw):
        self.calls.append((method, url, kw))
        for key, bodies in self.routes.items():
            if key in url:
                return FakeResp(bodies.pop(0) if isinstance(bodies, list) else bodies)
        raise AssertionError(f"unexpected {method} {url}")

    def get(self, url, **kw):
        return self._answer("GET", url, kw)

    def post(self, url, **kw):
        return self._answer("POST", url, kw)


def _post(**extra):
    return {"id": "kibo-x", "final_caption": "caption\n🤖 AI", "media_url": "https://cdn.example/v.mp4",
            "skus": ["latte"], "uses_ai_visuals": True, **extra}


def test_instagram_reel_flow_waits_for_container():
    s = FakeSession({
        "/media_publish": {"id": "MEDIA1"},
        "/123/media": {"id": "C1"},
        "/C1": [{"status_code": "IN_PROGRESS"}, {"status_code": "FINISHED"}],
        "/MEDIA1": {"permalink": "https://instagram.com/reel/abc"},
    })
    ig = Instagram("123", "tok", Http(session=s, sleep=lambda _: None))
    assert ig.publish(_post(), dry_run=True)["kind"] == "REELS" and not s.calls
    res = ig.publish(_post(), dry_run=False)
    assert res == {"media_id": "MEDIA1", "permalink": "https://instagram.com/reel/abc"}
    create = s.calls[0][2]["data"]
    assert create["media_type"] == "REELS" and create["video_url"].endswith("v.mp4")


def test_instagram_error_container_raises():
    s = FakeSession({"/123/media": {"id": "C1"}, "/C1": {"status_code": "ERROR"}})
    with pytest.raises(PublishError):
        Instagram("123", "tok", Http(session=s, sleep=lambda _: None)).publish(_post(), dry_run=False)


def test_tiktok_unaudited_direct_post_is_private_and_labelled():
    s = FakeSession({
        "creator_info": {"data": {"privacy_level_options": ["PUBLIC_TO_EVERYONE", "SELF_ONLY"]}, "error": {"code": "ok"}},
        "video/init": {"data": {"publish_id": "P1"}, "error": {"code": "ok"}},
    })
    tt = TikTok("tok", mode="direct", audited=False, http=Http(session=s))
    res = tt.publish(_post(), dry_run=False)
    info = s.calls[-1][2]["json"]["post_info"]
    assert res["publish_id"] == "P1" and info["privacy_level"] == "SELF_ONLY"
    assert info["is_aigc"] is True and info["brand_organic_toggle"] is True


def test_tiktok_inbox_mode_sends_only_the_video():
    s = FakeSession({"inbox/video/init": {"data": {"publish_id": "P2"}, "error": {"code": "ok"}}})
    res = TikTok("tok", mode="inbox", http=Http(session=s)).publish(_post(), dry_run=False)
    assert res == {"publish_id": "P2", "mode": "inbox"} and list(s.calls[0][2]["json"]) == ["source_info"]


def test_publish_command_never_double_posts(tmp_path, monkeypatch, kibo, store, raw_post):
    q = Queue(tmp_path / "posts")
    post = enqueue_plan(q, kibo, store, date(2026, 10, 12), [raw_post])[0]
    q.transition(post["id"], "approved", media_url="https://cdn.example/v.mp4",
                 published={"instagram": {"media_id": "already"}})
    sent = []

    class Recorder:
        def __init__(self, name):
            self.name = name

        def publish(self, p, dry_run=True):
            sent.append((self.name, dry_run))
            return {"ok": self.name}

    monkeypatch.setattr(cli, "_client", lambda platform, persona_id: Recorder(platform))
    args = ["--data", str(tmp_path), "publish", "--live", "--now", "2026-10-12T08:00:00+03:00"]
    assert cli.main(args) == 0
    assert sent == [("tiktok", False)]
    done = q.get(post["id"])
    assert done["status"] == "published" and set(done["published"]) == {"instagram", "tiktok"}
    cli.main(args)
    assert sent == [("tiktok", False)], "a second cron run must not publish again"


def test_order_command_extracts_code_from_message(tmp_path, kibo, store, raw_post, capsys):
    post = enqueue_plan(Queue(tmp_path / "posts"), kibo, store, date(2026, 10, 12), [raw_post])[0]
    msg = f"Habari, nataka caramel latte. Code {post['code']}"
    assert cli.main(["--data", str(tmp_path), "order", "10000", "--message", msg]) == 0
    assert f"order {post['code']} 10,000 TZS" in capsys.readouterr().out


def test_each_character_uses_its_own_account(monkeypatch):
    monkeypatch.setenv("IG_USER_ID_KILI", "999")
    monkeypatch.setenv("IG_ACCESS_TOKEN_KILI", "kili-token")
    monkeypatch.setenv("IG_USER_ID", "111")
    monkeypatch.setenv("TIKTOK_ACCESS_TOKEN_KIBO", "kibo-tt")
    assert Instagram.for_persona("kili").user_id == "999"
    assert Instagram.for_persona("kibo").user_id == "111"
    assert TikTok.for_persona("kibo").token == "kibo-tt"
