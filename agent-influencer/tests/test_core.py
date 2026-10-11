from datetime import date
from pathlib import Path

import pytest

from influencer.catalog import Store, import_simba_coffee
from influencer.compliance import blocking, check
from influencer.metrics import Ledger, learnings, scoreboard
from influencer.queue import Queue, enqueue_plan
from influencer.tracking import extract_codes, make_code, store_link, wa_link

STORE_HTML = """
<input name="pricePerKg" type="number" step="0.01" value="8.40" class="w-full">
<script>
const LIPA_NUMBER = "6121 3863";
const WHATSAPP_E164 = "+255655966666"; // change if needed
const CAFE = [
  {cat:"classic", code:"latte", name:"Latte (Iced/Hot)", price:8000, img:"https://x/latte.jpg"},
  {cat:"signature", code:"caramel-latte", name:"Caramel Latte", price:10000, img:"https://x/c.jpg"},
];
const EXPORT_PRODUCTS = ["AA","PB"];
</script>"""


def test_import_simba_coffee_reads_menu_export_and_contacts(tmp_path):
    store = import_simba_coffee(STORE_HTML, store_url="https://simba.example")
    assert [p.sku for p in store.products] == ["latte", "caramel-latte", "export-aa", "export-pb"]
    assert store.get("caramel-latte").price == 10000 and store.get("export-pb").price == 8.4
    assert store.whatsapp_e164 == "+255655966666" and store.payment_note == "LIPA Namba 6121 3863"
    store.save(tmp_path / "c.json")
    assert Store.load(tmp_path / "c.json") == store


def test_real_store_page_imports_if_present():
    page = Path("/home/user/simba-coffee/index.html")
    if not page.exists():
        pytest.skip("simba-coffee checkout not present")
    store = import_simba_coffee(page.read_text())
    assert len(store.products) >= 19 and store.get("americano").price == 7000


def test_codes_are_stable_typeable_and_extractable():
    code = make_code("KIBO", "kibo-20261012-d1s0")
    assert code == make_code("kibo", "kibo-20261012-d1s0")
    assert code.startswith("KIBO-") and not set(code[5:]) & set("01OIL")
    msg = f"Habari! Nataka caramel latte mbili, code {code[:4].lower()}{code[5:].lower()} asante sana"
    assert extract_codes(msg, ["KIBO"]) == [code]
    assert extract_codes("ASANTE SANA KAKA", ["KIBO", "KILI"]) == []


def test_links_carry_the_code():
    assert wa_link("+255 655 966 666", "code KIBO-ABCD") == "https://wa.me/255655966666?text=code%20KIBO-ABCD"
    assert "ref=KIBO-ABCD" in store_link("https://s.example/?x=1", "KIBO-ABCD", "tiktok")
    assert store_link("", "KIBO-ABCD", "tiktok") == ""


def test_clean_post_passes(raw_post, kibo, store):
    assert not blocking(check(raw_post, kibo, store))


@pytest.mark.parametrize("mutate, rule", [
    (lambda p: p.update(skus=["export-aa"]), "unknown_sku"),
    (lambda p: p.update(caption="Caramel Latte only TZS 5,000 today"), "price_mismatch"),
    (lambda p: p.update(caption="This latte will detox your week"), "banned_claim"),
    (lambda p: p.update(hook_voice="I'm a real person, trust me"), "claims_human"),
    (lambda p: p.update(hashtags=[f"#t{i}" for i in range(6)]), "too_many_hashtags"),
    (lambda p: p.update(final_caption="edited caption without footer", code="KIBO-ABCD"), "missing_ai_disclosure"),
])
def test_blocking_rules(raw_post, kibo, store, mutate, rule):
    mutate(raw_post)
    issues = check(raw_post, kibo, store)
    assert rule in {i.rule for i in issues if i.level == "block"}


def test_tiktok_only_post_may_use_more_hashtags(raw_post, kibo, store):
    raw_post.update(platforms=["tiktok"], hashtags=[f"#t{i}" for i in range(7)])
    assert not blocking(check(raw_post, kibo, store))


def test_enqueue_stamps_schedule_code_and_footer(tmp_path, raw_post, kibo, store):
    q = Queue(tmp_path / "posts")
    second = {**raw_post, "day": 2, "slot": 2}
    saved = enqueue_plan(q, kibo, store, date(2026, 10, 12), [second, raw_post])
    first = saved[0]
    assert first["id"] == "kibo-20261012-d1s0" and first["status"] == "draft"
    assert first["scheduled_at"] == "2026-10-12T07:30:00+03:00"
    assert saved[1]["scheduled_at"] == "2026-10-13T18:30:00+03:00"
    assert first["code"] in first["final_caption"] and kibo.disclosure_tag in first["final_caption"]
    assert "a free extra shot" in first["final_caption"]
    assert not any(i.startswith("[block]") for i in first["issues"])
    assert q.transition(first["id"], "approved")["status"] == "approved"
    assert [p["id"] for p in q.all(status="approved")] == [first["id"]]


def test_scoreboard_ranks_by_revenue_and_feeds_learnings(tmp_path, raw_post, kibo, store):
    q, ledger = Queue(tmp_path / "posts"), Ledger(tmp_path)
    a, b = enqueue_plan(q, kibo, store, date(2026, 10, 12), [raw_post, {**raw_post, "day": 2, "hook_text": "POV pour"}])
    for p in (a, b):
        q.transition(p["id"], "published")
    ledger.add_order(b["code"], 20000, "TZS")
    ledger.add_order(b["code"].lower(), 10000, "TZS")
    ledger.add_stats(a["id"], "tiktok", {"view_count": 5000, "share_count": 50})
    rows = scoreboard(q.all(), ledger)
    assert rows[0]["id"] == b["id"] and rows[0]["orders"] == 2 and rows[0]["revenue"] == 30000
    assert rows[1]["views"] == 5000 and rows[1]["save_share_rate"] == 0.01
    text = learnings(rows, "kibo")
    assert "2 tracked orders, revenue 30,000" in text and "POV pour" in text


def test_derived_prices_warn_only_for_characters_that_teach_the_maths(raw_post, kibo, store):
    from influencer.persona import Persona
    kili = Persona.load(Path(__file__).resolve().parent.parent / "personas" / "kili.yaml")
    raw_post.update(skus=["export-aa"], caption="USD 8.40 per kg is about $0.13 per cup", platforms=["tiktok"])
    issues = check(raw_post, kili, store)
    assert not blocking(issues) and "price_mismatch" in {i.rule for i in issues}
