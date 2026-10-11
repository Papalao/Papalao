"""Deterministic gate run on every post before a human sees it and again before publishing.

Rules first, model second: these checks are cheap, exact and never drift. A post with any
`block` issue cannot be approved; `warn` issues are shown to the reviewer.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .catalog import Store
from .persona import Persona

CAPTION_MAX = 2200          # Instagram caption limit; TikTok API title limit is 2,200 UTF-16 units too
IG_HASHTAG_MAX = 5          # Instagram caps hashtags at 5 per post/reel (rolled out from late 2025)
HOOK_WORDS_MAX = 8
GENERIC_TAGS = {"#fyp", "#foryou", "#foryoupage", "#viral", "#explore", "#reels", "#trending", "#instagood"}
HUMAN_CLAIMS = re.compile(r"\b(i am|i'm) (a )?(human|real person)\b|\bmimi ni binadamu\b", re.I)
PRICE_RE = re.compile(
    r"(?:(TZS|Tsh|TSh|USD|\$)\s?([\d][\d,]*(?:\.\d+)?)|([\d][\d,]*(?:\.\d+)?)\s?(?:/=|TZS|Tsh|USD))",
)


@dataclass(frozen=True)
class Issue:
    level: str  # "block" | "warn"
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.level}] {self.rule}: {self.detail}"


def _utf16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def check(post: dict, persona: Persona, store: Store) -> list[Issue]:
    issues: list[Issue] = []
    caption = post.get("caption", "")
    tags = [t if t.startswith("#") else f"#{t}" for t in post.get("hashtags", [])]
    full = post.get("final_caption") or caption
    text_fields = " ".join([caption, post.get("hook_text", ""), post.get("hook_voice", ""),
                            post.get("comment_prompt", "")] +
                           [f"{b.get('voice', '')} {b.get('on_screen', '')}" for b in post.get("script", [])])

    # Products and prices must come from the store.
    allowed = {p.sku for p in store.slice(persona.categories)}
    if not post.get("skus"):
        issues.append(Issue("warn", "no_product", "post sells nothing; fine for growth posts, keep them under 30%"))
    for sku in post.get("skus", []):
        if sku not in allowed:
            issues.append(Issue("block", "unknown_sku", f"{sku!r} is not in this character's catalog slice"))
    prices = {p.price for p in store.products if p.sku in post.get("skus", [])}
    for m in PRICE_RE.finditer(text_fields):
        raw = (m.group(2) or m.group(3) or "").replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            continue
        if value not in prices:
            # Characters that teach the maths (price per cup from price per kg) get a warning so a human checks it.
            level = "warn" if persona.allow_derived_prices else "block"
            issues.append(Issue(level, "price_mismatch", f"{m.group(0)!r} does not match the catalog price of the post's products"))

    # Claims the character must never make.
    lowered = text_fields.lower()
    for phrase in persona.banned_phrases:
        if re.search(rf"\b{re.escape(phrase.lower())}\b", lowered):
            issues.append(Issue("block", "banned_claim", f"uses {phrase!r}"))
    if HUMAN_CLAIMS.search(text_fields):
        issues.append(Issue("block", "claims_human", "the character is AI and must not claim to be human"))

    # Platform limits.
    if _utf16_len(full) > CAPTION_MAX:
        issues.append(Issue("block", "caption_too_long", f"{_utf16_len(full)} > {CAPTION_MAX} characters"))
    if "instagram" in post.get("platforms", []) and len(tags) > IG_HASHTAG_MAX:
        issues.append(Issue("block", "too_many_hashtags", f"{len(tags)} > {IG_HASHTAG_MAX} on Instagram"))
    lazy = sorted({t.lower() for t in tags} & GENERIC_TAGS)
    if lazy:
        issues.append(Issue("warn", "generic_hashtags", ", ".join(lazy)))
    if post.get("format", "").startswith("carousel") and "tiktok" in post.get("platforms", []):
        issues.append(Issue("warn", "carousel_on_tiktok", "carousels are planned as Instagram only"))

    # Disclosure and attribution live in the system-appended footer; make sure it survived edits.
    if post.get("final_caption"):
        if persona.disclosure_tag not in full:
            issues.append(Issue("block", "missing_ai_disclosure", "the AI disclosure line was removed"))
        if post.get("code") and post["code"] not in full:
            issues.append(Issue("block", "missing_order_code", "the tracked order code was removed"))

    # Craft checks that predict retention.
    if len(post.get("hook_text", "").split()) > HOOK_WORDS_MAX:
        issues.append(Issue("warn", "long_hook", f"hook over {HOOK_WORDS_MAX} words loses the first 1.5 s"))
    if post.get("uses_ai_visuals") and not post.get("ai_shots"):
        issues.append(Issue("warn", "ai_shots_missing", "marked as using AI visuals but no AI shot prompts"))
    return issues


def blocking(issues: list[Issue]) -> bool:
    return any(i.level == "block" for i in issues)
