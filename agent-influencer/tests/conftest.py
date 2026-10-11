from pathlib import Path

import pytest

from influencer.catalog import Product, Store
from influencer.persona import Persona

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def store() -> Store:
    return Store(
        name="Simba Coffee", whatsapp_e164="+255655966666", payment_note="LIPA Namba 6121 3863",
        store_url="https://example.com/simba",
        products=[
            Product("latte", "Latte (Iced/Hot)", 8000, "TZS", "classic", "cup"),
            Product("caramel-latte", "Caramel Latte", 10000, "TZS", "signature", "cup"),
            Product("export-aa", "Tanzanian green coffee, grade AA", 8.4, "USD", "export", "kg"),
        ],
    )


@pytest.fixture
def kibo() -> Persona:
    return Persona.load(ROOT / "personas" / "kibo.yaml")


@pytest.fixture
def raw_post() -> dict:
    """A post exactly as the planner returns it."""
    return {
        "day": 1, "slot": 0, "platforms": ["tiktok", "instagram"], "format": "ai_cant_taste",
        "pillar": "Kibo can't taste", "skus": ["caramel-latte"],
        "hook_text": "Describe this taste to a robot",
        "hook_voice": "Nimeambiwa hii ni tamu sana. Nieleze!",
        "script": [{"t": "0-1.5s", "visual": "Kibo pressed against the glass", "voice": "Nieleze!",
                    "on_screen": "Describe it"}],
        "ai_shots": ["Kibo leaning on the counter, LED eyes as spirals"],
        "real_shots": ["Close-up caramel drizzle on iced latte, with consent customer sip"],
        "caption": "Caramel Latte, TZS 10,000. Kibo still can't taste it 😭", "hashtags": ["#DarEsSalaam", "#IcedLatte"],
        "comment_prompt": "Describe caramel to a robot in 3 words", "sound": "upbeat amapiano, CML",
        "uses_ai_visuals": True, "hypothesis": "Taste-test reactions + price on screen drive orders",
    }
