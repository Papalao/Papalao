"""Product catalog. The Simba store is the only source of truth for what a character may sell.

A character never invents a product or a price: every post must reference SKUs that exist
here, and any price it prints must match the catalog (see compliance.py).
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price: float
    currency: str
    category: str
    unit: str = "item"
    image: str = ""


@dataclass
class Store:
    name: str
    whatsapp_e164: str
    payment_note: str
    store_url: str = ""
    products: list[Product] = field(default_factory=list)

    def get(self, sku: str) -> Product | None:
        return next((p for p in self.products if p.sku == sku), None)

    def slice(self, categories: list[str] | None) -> list[Product]:
        if not categories:
            return list(self.products)
        return [p for p in self.products if p.category in categories]

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False) + "\n")

    @classmethod
    def load(cls, path: str | Path) -> "Store":
        data = json.loads(Path(path).read_text())
        data["products"] = [Product(**p) for p in data.get("products", [])]
        return cls(**data)


_KV = re.compile(r'(\w+)\s*:\s*(?:"([^"]*)"|([\d.]+))')


def _js_const(html: str, name: str) -> str | None:
    m = re.search(rf'const\s+{name}\s*=\s*"([^"]*)"', html)
    return m.group(1) if m else None


def import_simba_coffee(html: str, store_url: str = "") -> Store:
    """Read the menu, export grades, LIPA number and WhatsApp line out of simba-coffee/index.html."""
    menu = re.search(r"const\s+CAFE\s*=\s*\[(.*?)\];", html, re.S)
    if not menu:
        raise ValueError("CAFE menu array not found in store HTML")

    products: list[Product] = []
    for obj in re.findall(r"\{([^{}]*)\}", menu.group(1)):
        kv = {k: (s if n == "" else n) for k, s, n in _KV.findall(obj)}
        products.append(Product(
            sku=kv["code"], name=kv["name"], price=float(kv["price"]), currency="TZS",
            category=kv.get("cat", "menu"), unit="cup", image=kv.get("img", ""),
        ))

    grades = re.search(r"const\s+EXPORT_PRODUCTS\s*=\s*\[(.*?)\];", html, re.S)
    per_kg = re.search(r'id="pricePerKg"[^>]*value="([\d.]+)"|name="pricePerKg"[^>]*value="([\d.]+)"', html)
    usd_kg = float(next(g for g in per_kg.groups() if g)) if per_kg else 0.0
    if grades:
        for g in re.findall(r'"([^"]+)"', grades.group(1)):
            products.append(Product(
                sku=f"export-{g.lower()}", name=f"Tanzanian green coffee, grade {g}", price=usd_kg,
                currency="USD", category="export", unit="kg",
            ))

    lipa = _js_const(html, "LIPA_NUMBER") or ""
    return Store(
        name="Simba Coffee",
        whatsapp_e164=_js_const(html, "WHATSAPP_E164") or "",
        payment_note=f"LIPA Namba {lipa}".strip(),
        store_url=store_url,
        products=products,
    )
