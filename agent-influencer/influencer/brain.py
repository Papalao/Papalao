"""The planner: one Claude call per character per week returns every post as validated JSON.

Cost shape: the persona + catalog system prompt is stable and cached; only the week, the
learnings from last week's sales and the operator's notes change between calls.
"""
from __future__ import annotations

import json
import os
from datetime import date

import anthropic

from .catalog import Store
from .persona import Persona, system_prompt

MODEL = os.environ.get("INFLUENCER_MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("INFLUENCER_EFFORT", "high")

_SCRIPT_BEAT = {
    "type": "object",
    "properties": {
        "t": {"type": "string", "description": "time range, e.g. 0-1.5s"},
        "visual": {"type": "string"},
        "voice": {"type": "string"},
        "on_screen": {"type": "string"},
    },
    "required": ["t", "visual", "voice", "on_screen"],
    "additionalProperties": False,
}

POST_SCHEMA = {
    "type": "object",
    "properties": {
        "day": {"type": "integer", "description": "1 = first day of the week"},
        "slot": {"type": "integer", "description": "index into the posting times, 0 = first"},
        "platforms": {"type": "array", "items": {"type": "string", "enum": ["instagram", "tiktok"]}},
        "format": {"type": "string"},
        "pillar": {"type": "string"},
        "skus": {"type": "array", "items": {"type": "string"}},
        "hook_text": {"type": "string", "description": "on-screen text in the first 1.5 s, max 8 words"},
        "hook_voice": {"type": "string"},
        "script": {"type": "array", "items": _SCRIPT_BEAT},
        "ai_shots": {"type": "array", "items": {"type": "string"},
                     "description": "prompts for AI-generated character shots, matching the visual bible"},
        "real_shots": {"type": "array", "items": {"type": "string"},
                       "description": "shots to film for real at the store, phone vertical"},
        "caption": {"type": "string"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "comment_prompt": {"type": "string", "description": "pinned first comment that invites replies"},
        "sound": {"type": "string", "description": "mood of a Commercial Music Library sound, or 'original voice'"},
        "uses_ai_visuals": {"type": "boolean"},
        "hypothesis": {"type": "string", "description": "one line: why this should sell or grow, so we can learn"},
    },
    "required": ["day", "slot", "platforms", "format", "pillar", "skus", "hook_text", "hook_voice", "script",
                 "ai_shots", "real_shots", "caption", "hashtags", "comment_prompt", "sound",
                 "uses_ai_visuals", "hypothesis"],
    "additionalProperties": False,
}

PLAN_SCHEMA = {
    "type": "object",
    "properties": {"posts": {"type": "array", "items": POST_SCHEMA}},
    "required": ["posts"],
    "additionalProperties": False,
}


class PlanError(RuntimeError):
    pass


def week_request(persona: Persona, start: date, learnings: str = "", notes: str = "") -> str:
    p = persona.posting
    times = ", ".join(p.get("times_local", []))
    return f"""Plan the week starting {start.isoformat()} ({start.strftime('%A')}).

Write exactly {p['posts_per_week']} posts across 7 days. Posting times (slots) are: {times}.
Every post goes to tiktok. Put "instagram" on the {p['instagram_per_week']} strongest posts as well
(carousels are Instagram only). Follow the pillar shares. Start at least two recurring series.

<last_week_results>
{learnings or "No data yet: this is the launch week. Optimise for follows and the first orders."}
</last_week_results>

<operator_notes>
{notes or "None."}
</operator_notes>"""


def plan_week(
    persona: Persona,
    store: Store,
    start: date,
    learnings: str = "",
    notes: str = "",
    client: anthropic.Anthropic | None = None,
) -> tuple[list[dict], dict]:
    """Return (posts, usage). Raises PlanError on refusal or truncated output."""
    client = client or anthropic.Anthropic()
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": PLAN_SCHEMA}},
        system=[{"type": "text", "text": system_prompt(persona, store), "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": week_request(persona, start, learnings, notes)}],
    ) as stream:
        message = stream.get_final_message()

    if message.stop_reason == "refusal":
        details = getattr(message, "stop_details", None)
        raise PlanError(f"model declined the plan: {getattr(details, 'explanation', '') or 'no explanation'}")
    if message.stop_reason == "max_tokens":
        raise PlanError("plan was cut off at max_tokens; lower posts_per_week or raise max_tokens")

    text = next((b.text for b in message.content if b.type == "text"), "")
    try:
        posts = json.loads(text)["posts"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise PlanError(f"plan was not valid JSON: {exc}") from exc

    u = message.usage
    usage = {
        "model": message.model,
        "input_tokens": u.input_tokens,
        "cache_read_input_tokens": u.cache_read_input_tokens or 0,
        "cache_creation_input_tokens": u.cache_creation_input_tokens or 0,
        "output_tokens": u.output_tokens,
    }
    return posts, usage
