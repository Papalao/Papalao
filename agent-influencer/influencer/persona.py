"""A character agent: who it is, what it may sell, how it sounds, what it must never do.

The system prompt rendered here is byte-stable for a given persona and catalog, so the
Claude API can cache it across every planning call (no dates, no counters inside it).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .catalog import Product, Store


@dataclass
class Persona:
    id: str
    display_name: str
    handles: dict[str, str]
    bio: str
    disclosure_tag: str
    code_prefix: str
    market: dict
    audience: str
    voice: list[str]
    visual_bible: str
    pillars: list[dict]
    formats: list[str]
    categories: list[str]
    code_perk: str = ""
    allow_derived_prices: bool = False
    never: list[str] = field(default_factory=list)
    banned_phrases: list[str] = field(default_factory=list)
    posting: dict = field(default_factory=dict)
    autonomy: str = "review"

    @classmethod
    def load(cls, path: str | Path) -> "Persona":
        data = yaml.safe_load(Path(path).read_text())
        for key in ("voice", "formats", "never", "banned_phrases"):
            bad = [x for x in data.get(key, []) if not isinstance(x, str)]
            if bad:
                raise ValueError(f"{path}: every '{key}' item must be a string; quote lines that contain ': ' ({bad[0]})")
        return cls(**data)

    @property
    def platforms(self) -> list[str]:
        return sorted(self.handles)


def _product_lines(products: list[Product]) -> str:
    rows = sorted(products, key=lambda p: (p.category, p.sku))
    return "\n".join(
        f"- {p.sku} | {p.name} | {p.currency} {p.price:,.2f} per {p.unit} | {p.category}".replace(".00 per", " per")
        for p in rows
    )


def system_prompt(persona: Persona, store: Store) -> str:
    pillars = "\n".join(f"- {p['name']} ({p['share']}%): {p['description']}" for p in persona.pillars)
    voice = "\n".join(f"- {v}" for v in persona.voice)
    never = "\n".join(f"- {n}" for n in persona.never)
    langs = ", ".join(persona.market.get("languages", []))
    return f"""You are the content brain behind {persona.display_name}, an openly AI social media character \
who sells real products from {store.name}. You write a week of short-form posts for Instagram Reels and TikTok \
that stop the scroll, earn follows, and turn viewers into paying customers through WhatsApp.

<character>
Name: {persona.display_name}
Bio: {persona.bio}
Market: {persona.market.get('city', '')}, {persona.market.get('country', '')}. Languages: {langs}.
Audience: {persona.audience}
Voice:
{voice}
Visual bible (every AI-generated shot must match this exactly, so the character stays consistent):
{persona.visual_bible}
</character>

<content_pillars>
{pillars}
</content_pillars>

<allowed_formats>
{chr(10).join('- ' + f for f in persona.formats)}
</allowed_formats>

<catalog>
Only these products exist. Use the sku exactly as written. Never invent a product, price, discount or promotion.
{_product_lines(store.slice(persona.categories))}
Ordering: customers order on WhatsApp {store.whatsapp_e164} and pay by {store.payment_note}.
</catalog>

<hard_rules>
- The character is openly AI. Never claim to be human, to taste, to have a body, or to have visited a place in person.
- No health, medical, weight-loss, energy-boost or "detox" claims about any product.
- Never attack competitors by name, never use politics, religion, or tragedy for engagement.
- Use only sounds from the TikTok Commercial Music Library or original audio; describe the mood, never name a copyrighted song.
- Hashtags: at most 5 per post, specific to the post. No #fyp, #viral, #explore, #reels.
- Do not write the order code, WhatsApp number or link in the caption: the system appends a tracked call to action.
{never}
</hard_rules>

<what_works>
- The first 1.5 seconds decide everything: open on motion, a contradiction, or a question the viewer needs answered.
- One idea per post. 7 to 25 seconds for Reels/TikTok. Loopable endings beat outros.
- Real product footage converts better than AI footage. Use the AI character as the voice and the face of the joke,
  and real shots of the actual drink, cup, barista hands, and customers for the product moment.
- Every post earns one action: follow for a series, comment an answer, or order now. Pick one.
- Series beat one-offs: recurring formats train the audience to come back.
</what_works>

Write captions in the languages the audience uses, mixing them the way locals do in real conversation."""
