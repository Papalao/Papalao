"""Attribution: every post gets its own order code, so a WhatsApp sale can be traced to the post that made it.

Flow: the caption tells viewers to quote the code on WhatsApp for a perk -> the customer messages
the store line with the code -> Simba's WhatsApp intake (or the operator) calls `extract_codes` on the
message and records the order against the post. Revenue per post is what the learning loop optimises.
"""
from __future__ import annotations

import hashlib
import re
from urllib.parse import quote, urlencode, urlsplit, urlunsplit, parse_qsl

from .catalog import Store
from .persona import Persona

# Crockford-style alphabet without 0/O/1/I/L so codes survive being typed on a phone.
_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
CODE_RE = re.compile(r"\b([A-Z]{2,8})[-\s]?([2-9A-HJKMNP-Z]{4})\b")


def make_code(prefix: str, post_id: str) -> str:
    digest = int.from_bytes(hashlib.sha256(post_id.encode()).digest()[:8], "big")
    chars = []
    for _ in range(4):
        digest, r = divmod(digest, len(_ALPHABET))
        chars.append(_ALPHABET[r])
    return f"{prefix.upper()}-{''.join(chars)}"


def extract_codes(text: str, prefixes: list[str]) -> list[str]:
    """Find order codes in a customer message. Tolerates lower case and a missing dash.

    Prefixes are required: without them ordinary Swahili ("ASANTE SANA") would parse as a code.
    """
    wanted = {p.upper() for p in prefixes}
    found = []
    for prefix, tail in CODE_RE.findall(text.upper()):
        if prefix not in wanted:
            continue
        code = f"{prefix}-{tail}"
        if code not in found:
            found.append(code)
    return found


def wa_link(e164: str, text: str) -> str:
    return f"https://wa.me/{re.sub(r'[^0-9]', '', e164)}?text={quote(text)}"


def store_link(store_url: str, code: str, platform: str) -> str:
    if not store_url:
        return ""
    parts = urlsplit(store_url)
    query = dict(parse_qsl(parts.query))
    query.update({"ref": code, "utm_source": platform, "utm_medium": "social", "utm_campaign": code})
    return urlunsplit(parts._replace(query=urlencode(query)))


def cta_footer(persona: Persona, store: Store, code: str) -> str:
    """Appended to every caption by the system, never written by the model."""
    perk = f" for {persona.code_perk}" if persona.code_perk else ""
    return (
        f"🛒 Order on WhatsApp {store.whatsapp_e164} (link in bio). Say code {code}{perk}.\n"
        f"{persona.disclosure_tag}"
    )
