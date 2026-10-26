


import asyncio, importlib.util, io, json, os, shutil, sqlite3, sys, tempfile, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import translator_engine as te

FAILS = []
def check(name, cond):
    print(("  [OK]   " if cond else "  [FAIL] ") + name)
    if not cond:
        FAILS.append(name)


print("1. FTB '&' formatting codes")
src = "&eHello &7world&r"
prot, toks = te.protect_placeholders(src)
check("&e &7 &r protected", "&e" not in prot and "&7" not in prot and "&r" not in prot and len(toks) == 3)
check("restored exactly", te.restore_placeholders(prot, toks) == src)
check("Q&A / R&D left alone", te.protect_placeholders("Q&A and R&D")[1] == [])
check("&#RRGGBB protected", te.protect_placeholders("&#ff00aaTitle")[1] == ["&#ff00aa"])
check("broken code '&Срочное' is detected",
      not te.validate_technical_consistency("&eUrgent Missive", "&Срочное сообщение"))
check("intact code passes", te.validate_technical_consistency("&eUrgent Missive", "&eСрочное сообщение"))
check("literal backslash-& kept", te.restore_placeholders(*te.protect_placeholders("&6Combat \\& Gear")) == "&6Combat \\& Gear")


print("2. SNBT round trip")
snbt = '{id: "1A", "minecraft:stone": 1b, "my key": {a: [I; 1, 2, 3]}, title: \'Hi\'}'
d = te.parse_snbt(snbt)
out = te.serialize_snbt(d)
try:
    d2 = te.parse_snbt(out); ok = True
except Exception as e:
    ok = False; print(e)
check("quoted keys with ':' survive", ok and "minecraft:stone" in d2 and '"minecraft:stone"' in out)
check("[I; ...] prefix preserved", "[I; 1, 2, 3]" in out)
orig = te.parse_snbt("{a: {title: 'One'}, b: ['x', 'y']}")
mod = te.parse_snbt("{a: {title: 'Eins'}, b: ['x', 'z']}")
n = te._revert_snbt_paths(orig, mod, {"$.a.title", "$.b[1]"})
check("leaf revert restores only the named leaves", n == 2 and str(mod["a"]["title"]) == "One" and str(mod["b"][1]) == "y")


print("3. stale-copy audit")
rows = [
    (1, "Oxygen Cans(Common)", "Кислородные баллоны (общие)"),
    (2, "Mekanism", "Меканизм"),
    (3, "Fuel is hard to get; it requires venturi", "Топливо трудно достать; для него нужна вентури"),
    (4, "The Moon", "Кислородные баллоны (общие)"),
    (5, "Soul Crafting", "&eТри охотника"),
    (6, "Raster Light Gray Stained Glass", "Растровое светло-серое стекло"),
    (7, "Raster Light Gray Stained Glass Pane", "Растровое светло-серое стекло"),
    (8, "Has 5 slots", "Имеет 7 слотов"),
]
sus = te.find_stale_copy_suspects(rows)
check("stale copy flagged, original kept", 4 in sus and 1 not in sus)
check("foreign formatting code flagged", 5 in sus)
check("legit variant not flagged", 7 not in sus)
check("invented number flagged", 8 in sus)
check("spelled-out number is NOT flagged", te.translation_alignment_problem("Scales with all 3 elements", "Масштабируется со всеми тремя элементами") is None)
check("1,000 vs 1 000 is the same number", te.translation_alignment_problem("Stores 1,000 units", "Хранит 1 000 единиц") is None)

real_db = HERE / "global_translations.db"
if real_db.exists():


    try:
        c = sqlite3.connect(str(real_db))
        rr = c.execute("select id, original_text, translated_text from translations order by id").fetchall()
        s = te.find_stale_copy_suspects(rr)
        print(f"     (info) global cache: {len(s)} of {len(rr)} rows look suspicious to the heuristics "
              f"({100 * len(s) / max(1, len(rr)):.1f}%); a few percent is normal for a clean cache")
    except Exception as exc:
        print("     (info) could not read global_translations.db:", exc)


print("4. official-RU scope / ru_RU.json")
tmp = Path(tempfile.mkdtemp())
def mkjar(name, files):
    p = tmp / name
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("fabric.mod.json", json.dumps({"id": name.split(".")[0], "name": name}))
        for k, v in files.items():
            z.writestr(k, v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))
    return p
a = mkjar("moda.jar", {"assets/moda/lang/en_us.json": {"k.milk": "Milk", "k.axe": "Iron Battle Axe"},
                       "assets/moda/lang/ru_ru.json": {"k.milk": "Молоко", "k.axe": "Железный боевой топор"}})
b = mkjar("modb.jar", {"assets/modb/lang/en_us.json": {"k.milk": "Milk"}})
c = mkjar("modc.jar", {"assets/modc/lang/en_us.json": {"block.palm_slab": "Palm Slab", "block.new": "Blue Lamp"},
                       "assets/modc/lang/ru_RU.json": {"block.palm_slab": "Пальмовая плита"}})
res = te.AnalysisResult()
for jar in (a, b, c):
    te.analyze_jar(jar, res)
uniq = te.get_unique_translatable_texts(res, te.CONF_LOW)
check("Milk of mod B is still translated (A's native RU must not block it)", "Milk" in uniq)
check("A's own native-RU key is not sent", "Iron Battle Axe" not in uniq)
check("ru_RU.json key is not sent to Google", "Palm Slab" not in uniq)
check("key without any RU is sent", "Blue Lamp" in uniq)
te.RESOURCEPACK_DIR = tmp / "pack"
te.TRANSLATED_MODPACK_DIR = tmp / "tm"
rep = {"errors": []}
te.write_lang_json_sources(res, {"Milk": "Молоко (Google)", "Blue Lamp": "Синяя лампа"}, rep)
outc = json.loads((tmp / "pack/assets/modc/lang/ru_ru.json").read_text(encoding="utf-8"))
check("ru_RU.json content copied into our lowercase ru_ru.json", outc.get("block.palm_slab") == "Пальмовая плита")
check("new key translated next to it", outc.get("block.new") == "Синяя лампа")
outb = json.loads((tmp / "pack/assets/modb/lang/ru_ru.json").read_text(encoding="utf-8"))
check("mod B gets its Milk", outb.get("k.milk") == "Молоко (Google)")
outa = json.loads((tmp / "pack/assets/moda/lang/ru_ru.json").read_text(encoding="utf-8"))
check("official values are copied into our pack (game may ignore the mod's file)", outa.get("k.milk") == "Молоко" and outa.get("k.axe") == "Железный боевой топор")


print("5. stale-page simulation (old engine vs fixed engine)")
def load_orig():
    spec = importlib.util.spec_from_file_location("translator_engine_orig", HERE / "translator_engine.orig.py")
    m = importlib.util.module_from_spec(spec); sys.modules['translator_engine_orig'] = m; spec.loader.exec_module(m); return m

import re as _re
def make_fake(mod, wrong_digit_item=None):
    class Fake(mod.GoogleTranslateEngine):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.prev = ""; self.n = 0
        async def _browser_translate(self, payload):
            self.n += 1
            ids = _re.findall(r"MTX(\d{6})\s*:", payload)
            fresh = []
            for line in payload.split("\n"):
                m = _re.match(r"(MTX\d{6}):\s*(.*)", line)
                if m:
                    t = m.group(2)
                    if wrong_digit_item and t == wrong_digit_item and "STALE_ONCE" not in self.__dict__:
                        self.STALE_ONCE = 1
                        fresh.append(f"{m.group(1)}: Совсем другой текст 99")
                    else:
                        fresh.append(f"{m.group(1)}: RU({t})")
                else:
                    fresh[-1] += "\n" + line
            fresh = "\n".join(fresh) if ids else "RU(" + payload + ")"

            use_stale = self.prev and ids and self.n % 2 == 0 and all(f"MTX{i}:" in self.prev for i in ids)
            out = self.prev if use_stale else fresh
            if ids:
                self.prev = fresh
            return out
    return Fake

async def run(mod, texts, **kw):
    mod.async_playwright = object()
    mod.BATCH_SIZE = 220
    cache = mod.TranslationCache(tmp / f"c_{mod.__name__}_{len(kw)}.db")
    eng = make_fake(mod, **kw)(cache, None, {})
    async def _noop(): return None
    eng._rate.acquire = _noop
    mod.BASE_BACKOFF = 0
    out = await eng.translate_many(texts)
    return out, eng

texts = [f"Item number {i} of the long list" if i % 3 else f"Quest title {i}" for i in range(7, 70)]
if (HERE / "translator_engine.orig.py").exists():
    old = load_orig()
    out_old, _ = asyncio.run(run(old, texts))
    bad_old = sum(1 for t in texts if out_old[t].translated != f"RU({t})")
else:
    bad_old = None
    print("     (translator_engine.orig.py not found: skipping the old-engine comparison)")
out_new, eng_new = asyncio.run(run(te, texts))
bad_new = sum(1 for t in texts if out_new[t].translated != f"RU({t})")
print(f"     wrong translations: old engine = {bad_old}, fixed engine = {bad_new}")
if bad_old is not None:
    check("old engine reproduces the bug (sanity of the simulation)", bad_old > 0)
check("fixed engine: every string got ITS OWN translation", bad_new == 0)
check("fixed engine: marker ids never repeat between requests",
      len(set(eng_new._alloc_marker_ids(5)) | set(eng_new._alloc_marker_ids(5))) == 10)

target = "Costs 5 gold coins to craft"
out_g, eng_g = asyncio.run(run(te, [target, "Plain text one", "Plain text two"], wrong_digit_item=target))
target = "Costs 5 gold coins to craft"
check("alignment guard re-requests a wrong-but-fresh answer", out_g[target].translated == f"RU({target})"
      and eng_g.stats["alignment_rechecks"] >= 1)

print("2b. FTB layout tags")
check("{@pagebreak} is not translatable", te.classify_string("description", "{@pagebreak}")[0] is False)
check("{image:...} is not translatable", te.classify_string("description", "{image:ftbquests:textures/x.png width:100}")[0] is False)
check("normal prose in braces-free text still translatable", te.classify_string("description", "Open the chest.")[0] is True)

print("2d. JSON text components inside SNBT strings")
src = "{quests: [{id: 'AAAA1111BBBB2222', description: ['{\"text\":\"Hello there\",\"color\":\"gold\"}', 'Plain line']}]}"
d3 = te.parse_snbt(src); res3 = te.AnalysisResult()
res3.snbt_sources.append({"path": "z", "rel": "z.snbt", "kind": "FTBQUESTS", "data": d3})
te.TRANSLATED_MODPACK_DIR = tmp / "tm3"
rep3 = {"errors": []}
te.write_snbt_sources(res3, {"Hello there": "Привет", "Plain line": "Простая строка"}, rep3)
o3 = (tmp / "tm3" / "z.snbt").read_text(encoding="utf-8")
check("text component translated, nothing reverted", "Привет" in o3 and "Простая строка" in o3 and not rep3["errors"])
check("colour kept", "gold" in o3)

check("Java object dump is not translatable", te.classify_string("x", "cincinnasite_EquipmentSlot[name=pickaxe, category=TOOLS]")[0] is False)

print("2c. names Google leaves unchanged")
for nm in ("Sgt. Peppers Lonely Hearts Club", "Pr. Projectile Hostile Spawn", "Mekanism", "Bronze Age"):
    check(f"name accepted: {nm}", te.looks_like_untranslatable_name(nm))
for pr in ("Open the chest to get your reward.", "Good start! Now you are ready to generate mana.",
           "increases the speed at which you break blocks"):
    check(f"prose NOT a name: {pr[:30]}", not te.looks_like_untranslatable_name(pr))


print("6. legacy cache quarantine")
import time as _time
te.INVALID_CACHE_ENTRIES_PATH = tmp / "invalid.json"
te.TRANSLATION_CONFLICTS_PATH = tmp / "conf.json"
g = te.GlobalTranslationCache(tmp / "g.db")
g.conn.execute("DELETE FROM translations")
g.conn.commit()
g.put("Old good string", "Старая строка", context="", mod_id="m")
g.put("Manual one", "Ручной перевод", quality_status=te.QUALITY_MANUAL, source=te.SOURCE_MANUAL)
g.conn.execute("UPDATE translations SET created_at=?", (te.LEGACY_CACHE_CUTOFF - 1000,))
g.conn.commit()
g.put("Fresh string", "Свежая строка")
r = g.audit_stale_copies()
check("strict audit rejects old machine rows", r["rejected"] == 1 and g.lookup("Old good string") is None)
check("manual row survives", g.lookup("Manual one") == "Ручной перевод")
check("fresh row survives", g.lookup("Fresh string") == "Свежая строка")
check("audit runs only once", g.audit_stale_copies()["skipped"])
g.close()
loc = te.TranslationCache(tmp / "l.db")
loc.put("Old", "Старый")
loc.conn.execute("UPDATE translations SET created_at=?", (te.LEGACY_CACHE_CUTOFF - 5,))
loc.put("New", "Новый")
loc.conn.commit()
r = te.audit_local_cache(loc)
check("local strict audit removes only legacy rows", r["removed"] == 1 and loc.get("Old") is None and loc.get("New") == "Новый")
check("local backup file written", (tmp / "l.db.pre_fix_backup.db").exists())
loc.close()

print("5b. echoed names vs echoed prose")
class EchoFake(te.GoogleTranslateEngine):
    ECHO = {"Sgt. Peppers Lonely Hearts Club", "Bronze Age", "Open the chest to get your reward."}
    async def _browser_translate(self, payload):
        outl = []
        for line in payload.split("\n"):
            m = _re.match(r"(MTX\d{6}):\s*(.*)", line)
            if m:
                outl.append(f"{m.group(1)}: " + (m.group(2) if m.group(2) in self.ECHO else f"RU({m.group(2)})"))
        return "\n".join(outl)
te.async_playwright = object()
cache5 = te.TranslationCache(tmp / "c5.db")
eng5 = EchoFake(cache5, None, {})
async def _noop5(): return None
eng5._rate.acquire = _noop5
names = ["Sgt. Peppers Lonely Hearts Club", "Bronze Age", "Open the chest to get your reward.", "Iron Sword", "Gold Pickaxe", "Silver Helmet"]
out5 = asyncio.run(eng5.translate_many(names))
check("echoed names are accepted as they are", out5["Bronze Age"].status == "translated" and out5["Bronze Age"].translated == "Bronze Age")
check("echoed prose is still a failure", out5["Open the chest to get your reward."].translated is None)
check("normal strings translated", out5["Iron Sword"].translated == "RU(Iron Sword)")
check("names do not trip the breaker", eng5.stats["circuit_breaker_trips"] == 0 and eng5.stats["identity_accepted"] == 2)
check("name is remembered in local cache", cache5.get("Bronze Age") == "Bronze Age")

print("7. invisible sources: nested jars, pack zips, FancyMenu, glyphs")
prot, toks = te.protect_placeholders("§f聾§r Armor")
check("icon glyph is protected from Google", "聾" not in prot and "聾" in "".join(toks))
check("%n% and ** protected", te.protect_placeholders("**Did you know?**%n%Hi")[0].count("__PH") == 3)
mc = tmp / "mc"
(mc / "mods").mkdir(parents=True)
(mc / "config/paxi/resourcepacks").mkdir(parents=True)
(mc / "config/fancymenu/customization").mkdir(parents=True)
(mc / "config/fancymenu/assets").mkdir(parents=True)
nested = io.BytesIO()
with zipfile.ZipFile(nested, "w") as z:
    z.writestr("fabric.mod.json", json.dumps({"id": "prominentbase", "name": "Base"}))
    z.writestr("assets/prominent/lang/en_us.json", json.dumps({"item.boots": "Plague Lord's Boots"}))
with zipfile.ZipFile(mc / "mods/prominent.jar", "w") as z:
    z.writestr("fabric.mod.json", json.dumps({"id": "prominent_global", "name": "Prominent"}))
    z.writestr("META-INF/jars/prominentbase-4.1.1.jar", nested.getvalue())
with zipfile.ZipFile(mc / "config/paxi/resourcepacks/Tips.zip", "w") as z:
    z.writestr("pack.mcmeta", "{}")
    z.writestr("assets/custom-tooltip-api/lang/en_us.json", json.dumps({"cta.text.set_bonus": "Wear full set for set bonus:"}))
    z.writestr("assets/a_overrides/lang/en_us.json", json.dumps({"attribute.name.generic.armor": "§f聾§r Armor"}, ensure_ascii=False))
    z.writestr("assets/minecraft/lang/en_us.json", json.dumps({"menu.singleplayer": "Singleplayer"}))
(mc / "config/fancymenu/customization/Menu.txt").write_text(
    "customization-meta {\n  identifier = main\n}\n"
    "element {\n  element_type = custom_button\n  label = Singleplayer\n  description = Report an Issue or Bug\n}\n"
    "element {\n  element_type = text\n  source_mode = direct\n  source = **Did you know?**\n}\n"
    "element {\n  element_type = image\n  source_mode = local\n  source = config/fancymenu/assets/logo.png\n}\n", encoding="utf-8")
(mc / "config/fancymenu/assets/tips.txt").write_text("Some say that the portal at the End is a someone.\n\nBring food with you.\n", encoding="utf-8")

te.MC_DIR = mc
te.RESOURCEPACK_DIR = tmp / "rp7"
te.TRANSLATED_MODPACK_DIR = tmp / "tm7"
res7 = te.run_analysis()
uniq7 = te.get_unique_translatable_texts(res7, te.CONF_LOW)
check("jar-in-jar item name found", "Plague Lord's Boots" in uniq7)
check("Paxi resource-pack zip lang found", "Wear full set for set bonus:" in uniq7)
check("glyph attribute name found", "§f聾§r Armor" in uniq7)
check("vanilla 'minecraft' namespace in a pack is skipped", "Singleplayer" in uniq7 and not any(
    s_["entry"].startswith("assets/minecraft/") for s_ in res7.lang_json_sources))
check("FancyMenu button label found", "Report an Issue or Bug" in uniq7)
check("FancyMenu text element found", "**Did you know?**" in uniq7)
check("FancyMenu image path NOT translated", not any("logo.png" in u for u in uniq7))
check("loading tips found", "Bring food with you." in uniq7)
tr7 = {u: "RU " + u for u in uniq7}
tr7["§f聾§r Armor"] = "§f聾§r Броня"
rep7 = {"errors": []}
te.write_lang_json_sources(res7, tr7, rep7)
te.write_config_sources(res7, tr7, rep7)
def jl(pth): return json.loads((te.RESOURCEPACK_DIR / pth).read_text(encoding="utf-8"))
check("nested jar output written under its own namespace", jl("assets/prominent/lang/ru_ru.json")["item.boots"] == "RU Plague Lord's Boots")
check("pack namespaces written", jl("assets/custom-tooltip-api/lang/ru_ru.json")["cta.text.set_bonus"].startswith("RU "))
check("glyph kept in translated attribute name", jl("assets/a_overrides/lang/ru_ru.json")["attribute.name.generic.armor"] == "§f聾§r Броня")
check("no vanilla namespace file written", not (te.RESOURCEPACK_DIR / "assets/minecraft/lang/ru_ru.json").exists())
menu = (te.TRANSLATED_MODPACK_DIR / "config/fancymenu/customization/Menu.txt").read_text(encoding="utf-8")
check("FancyMenu layout translated, structure intact", "label = RU Singleplayer" in menu and "description = RU Report an Issue or Bug" in menu
      and "source = RU **Did you know?**" in menu and "source = config/fancymenu/assets/logo.png" in menu and menu.count("{") == menu.count("}"))
tips = (te.TRANSLATED_MODPACK_DIR / "config/fancymenu/assets/tips.txt").read_text(encoding="utf-8")
check("tips translated line by line, blank line kept", tips.split("\n")[1] == "" and tips.split("\n")[2] == "RU Bring food with you.")
check("original FancyMenu file untouched", "RU" not in (mc / "config/fancymenu/customization/Menu.txt").read_text(encoding="utf-8"))

print("8. glossary for words Google leaves in English")
G = te.load_glossary()
cases = [
    ("Checkered Blackstone Tiles", "Клетчатая плитка Blackstone", "Клетчатая плитка чернита"),
    ("Angry Deepslate", "Злой Deepslate", "Злой глубинный сланец"),
    ("Creeper Dirt Carving", "Резьба по грязи Creeper", "Резьба по грязи крипера"),
    ("Purpur Shingle Slab", "Плита гонта Purpur", "Плита гонта пурпура"),
    ("Deepslate Plates", "Пластины Deepslate", "Пластины глубинного сланца"),
    ("The platform can build with any type of Blackstone", "Платформа может быть построена из Blackstone любого типа.", "Платформа может быть построена из чернита любого типа."),
    ("Sculk Bone Bricks Slabs", "Плиты из костяного кирпича Sculk", "Плиты из костяного кирпича скалка"),
]
for en, ru, want in cases:
    got = te.apply_glossary(en, ru, G)
    check(f"glossary: {ru!r}", got == want)
    if got != want:
        print("       got:", got)
check("term not in the English source is left alone", te.apply_glossary("Ghost Block", "Блок Creeper", G) == "Блок Creeper")
check("technical names untouched", te.apply_glossary("nether_ruby_slot", "Nether_ruby_slot", G) == "Nether_ruby_slot")
check("custom glossary entry (plain string)", te.apply_glossary("Cherry Table", "Стол Cherry", {"Cherry": {"nom": "вишня", "gen": "вишни"}}) == "Стол вишни")

print("9. damaged placeholders and colour-coded lines")
for bad in ("Привет __ PH0 __ мир __ph1__", "Привет __РН0__ мир __ PH1__"):
    check(f"distorted token restored: {bad!r}", te.restore_placeholders(bad, ["&c", "&r"]) == "Привет &c мир &r")

class TokenKiller(te.GoogleTranslateEngine):
    async def _browser_translate(self, payload):
        outl = []
        for line in payload.split("\n"):
            m = _re.match(r"(MTX\d{6}):\s*(.*)", line)
            if m:
                body = m.group(2)
                outl.append(f"{m.group(1)}: " + ("Сломанный текст без меток" if "__PH" in body else f"RU({body})"))
        return "\n".join(outl)
te.async_playwright = object()
cache9 = te.TranslationCache(tmp / "c9.db")
eng9 = TokenKiller(cache9, None, {})
async def _noop9(): return None
eng9._rate.acquire = _noop9
line = "&6Apotheosis allows you to &cmove, edit&r and manipulate spawners.&r"
out9 = asyncio.run(eng9.translate_many([line, "Plain sentence number two"]))
r9 = out9[line].translated or ""
check("colour line is translated even when Google destroys the codes", r9.startswith("&6RU(") and "manipulate spawners." in r9 and r9.endswith("&r"))
check("fallback counted and not cached", eng9.stats["plain_fallback"] == 1 and cache9.get(line) is None)
check("normal line untouched by fallback", out9["Plain sentence number two"].translated == "RU(Plain sentence number two)")



for _k, _v in [("name", "blaze"), ("name", "main"), ("name", "stone"),
               ("biomes", "minecraft:nether_wastes, minecraft:crimson_forest"),
               ("title", "circle"), ("name", "wither_skeleton")]:
    _should, _conf, _reason = te.classify_string(_k, _v)
    check(f"identifier {_k}={_v!r} is not translated", not _should)
for _k, _v in [("name", "Blaze"), ("description", "Cute little baby kitten bee."),
               ("name", "Flame Bee"), ("title", "no spaces allowed here")]:
    check(f"text {_k}={_v!r} still translatable", te.classify_string(_k, _v)[0])
_data = {"name": "blaze", "color": "#ff0000", "flower": "minecraft:blaze_rod", "desc": "A fiery bee."}
_n = te.apply_json_translations(_data, {"blaze": "пламя", "A fiery bee.": "Огненная пчела."})
check("honey JSON: id kept, text translated", _data["name"] == "blaze" and _data["desc"] == "Огненная пчела." and _n == 1)



for _k, _v in [("max_total_size", "35 GB"), ("size", "10 MB"), ("interval", "30 min"), ("x", "50%"), ("name", "100 RF/t")]:
    check(f"quantity {_v!r} is not translated", not te.classify_string(_k, _v)[0])
for _v in [")  )", "  EEd    dE   ", "G   BBBEFEBBB   G", " I I ", " ++               ++ ", "{", "|||||  {"]:
    check(f"layout row {_v!r} is not translated", not te.classify_string("name", _v)[0])
for _k, _v in [("title", "5 Levels"), ("name", "Advanced Assembly Table"), ("description", "NEW QUEST AVAILABLE")]:
    check(f"text {_v!r} still translatable", te.classify_string(_k, _v)[0])



import tempfile as _tf, zipfile as _zf, json as _json
_d = Path(_tf.mkdtemp())
(_d / "o").mkdir()
(_d / "o" / "options.txt").write_text("version:2586\nlang:en_us\nresourcePacks:[\"vanilla\",\"file/ERP-1.9.zip\"]\nincompatibleResourcePacks:[\"file/Modpack_Auto_Rus.zip\"]\n", encoding="utf-8")
check("pack_format 1.16.5", te.detect_pack_format(_d / "o") == 6)
(_d / "o2").mkdir(); (_d / "o2" / "options.txt").write_text("version:3463\n", encoding="utf-8")
check("pack_format 1.20", te.detect_pack_format(_d / "o2") == 15)
_r = _d / "res"; (_r / "assets" / "m" / "lang").mkdir(parents=True); (_r / "assets" / "m" / "tips").mkdir(parents=True)
(_r / "assets" / "m" / "lang" / "ru_ru.json").write_text('{"a":"Привет"}', encoding="utf-8")
(_r / "assets" / "m" / "tips" / "t.json").write_text('{"tip":"Совет"}', encoding="utf-8")
(_r / "pack.mcmeta").write_text('{"pack":{"pack_format":15}}', encoding="utf-8")
_zp = _d / "o" / "resourcepacks" / "Modpack_Auto_Rus.zip"
check("resource pack zip built", te.build_resourcepack_zip(_r, _zp, 6) == 2)
with _zf.ZipFile(_zp) as _z:
    check("pack.mcmeta has detected format", _json.loads(_z.read("pack.mcmeta"))["pack"]["pack_format"] == 6)
    check("pack holds lang and tips", {"assets/m/lang/ru_ru.json", "assets/m/tips/t.json"} <= set(_z.namelist()))
_info = te.enable_resourcepack_in_options(_d / "o", "Modpack_Auto_Rus.zip")
_opt = (_d / "o" / "options.txt").read_text(encoding="utf-8")
check("options.txt: pack enabled on top, other packs kept", 'resourcePacks:["vanilla","file/ERP-1.9.zip","file/Modpack_Auto_Rus.zip"]' in _opt)
check("options.txt: language ru_ru, no longer incompatible", "lang:ru_ru" in _opt and 'incompatibleResourcePacks:[]' in _opt)
te.enable_resourcepack_in_options(_d / "o", "Modpack_Auto_Rus.zip")
check("options.txt: idempotent", (_d / "o" / "options.txt").read_text(encoding="utf-8") == _opt)
(_d / "o3").mkdir(); te.enable_resourcepack_in_options(_d / "o3", "Modpack_Auto_Rus.zip")
check("options.txt created when missing", "lang:ru_ru" in (_d / "o3" / "options.txt").read_text(encoding="utf-8"))

_jar = _d / "m.jar"
with _zf.ZipFile(_jar, "w") as _z:
    _z.writestr("assets/m/lang/ru_ru.json", _json.dumps({"official": "Официальный", "same": "Same"}, ensure_ascii=False))
    _z.writestr("data/m/patchouli_books/b/ru_ru/entries/official.json", '{"name":"Официальная"}')
te.patch_jar_entries(
    _jar,
    {"assets/m/lang/ru_ru.json": _json.dumps({"official": "МОЙ", "same": "Тот же", "new": "Новый"}, ensure_ascii=False).encode()},
    {"data/m/patchouli_books/b/ru_ru/entries/official.json": b'{"name":"MINE"}',
     "data/m/patchouli_books/b/ru_ru/entries/new.json": b'{"name":"New"}'},
    {"assets/m/lang/ru_ru.json"})
with _zf.ZipFile(_jar) as _z:
    _lang = _json.loads(_z.read("assets/m/lang/ru_ru.json"))
    check("jar lang merge keeps the mod's official Russian", _lang["official"] == "Официальный")
    check("jar lang merge fills missing and English keys", _lang["same"] == "Тот же" and _lang["new"] == "Новый")
    check("patchouli: official Russian page not overwritten",
          _json.loads(_z.read("data/m/patchouli_books/b/ru_ru/entries/official.json"))["name"] == "Официальная")
    check("patchouli: missing Russian page added", "data/m/patchouli_books/b/ru_ru/entries/new.json" in _z.namelist())


_old_dirs = (te.PATCHOULI_OUTPUT_DIR, te.RESOURCEPACK_DIR, te.TRANSLATED_MODPACK_DIR)
te.PATCHOULI_OUTPUT_DIR, te.RESOURCEPACK_DIR, te.TRANSLATED_MODPACK_DIR = _d / "pat", _d / "rp", _d / "tm"
_res = te.AnalysisResult()
_res.generic_json_sources = [
    {"modid": "m", "jar": str(_jar), "entry": "data/m/patchouli_books/b/en_us/entries/x.json", "kind": "PATCHOULI",
     "data": {"name": "Hello world friend", "pages": [{"type": "text", "text": "Hello world friend"}]}},
    {"modid": "m", "jar": str(_jar), "entry": "assets/m/tips/t.json", "kind": "TIPS_JSON",
     "data": {"title": "Tip", "tip": "Hello world friend"}},
    {"modid": "m", "jar": "", "entry": "config/m/ctl.json", "kind": "CONFIG",
     "data": {"name": "Hello world friend"}},
]
_rep = {"errors": []}
te.write_generic_json_sources(_res, {"Hello world friend": "Привет, мир", "Tip": "Совет"}, _rep)
_p = te.PATCHOULI_OUTPUT_DIR / "data/m/patchouli_books/b/ru_ru/entries/x.json"
check("Patchouli output goes to ru_ru path", _p.exists() and _json.loads(_p.read_text(encoding="utf-8"))["name"] == "Привет, мир")
check("Patchouli source remembers jar entry for deployment",
      _res.generic_json_sources[0].get("deploy_entry") == "data/m/patchouli_books/b/ru_ru/entries/x.json")
check("Patchouli no longer written as loose en_us file", not (te.TRANSLATED_MODPACK_DIR / "data").exists())
check("tips JSON goes to the resource pack",
      _json.loads((te.RESOURCEPACK_DIR / "assets/m/tips/t.json").read_text(encoding="utf-8"))["tip"] == "Привет, мир")
_cfg = (te.TRANSLATED_MODPACK_DIR / "config/m/ctl.json").read_text(encoding="utf-8")
check("config JSON is ASCII-only (no mojibake on cp1251 readers)", _cfg.isascii() and _json.loads(_cfg)["name"] == "Привет, мир")
te.PATCHOULI_OUTPUT_DIR, te.RESOURCEPACK_DIR, te.TRANSLATED_MODPACK_DIR = _old_dirs



for _v in ["minecraft:zombie minecraft:overworld magistuarmory:rustedchainmail_helmet magistuarmory:rusted_bastardsword",
           "minecraft:wither_skeleton 0.3 magistuarmory:sallet magistuarmory:steel_zweihander",
           "minecraft:piglin_brute minecraft:zombified_piglin minecraft:golden_helmet", "#forge:ores/iron, minecraft:stone"]:
    check(f"id list {_v[:40]!r} not translated", not te.classify_string("value", _v)[0])
for _v in ["See minecraft:stone for details", "Give the player a diamond sword", "note: hello world"]:
    check(f"sentence {_v!r} still translatable", te.classify_string("description", _v)[0])



_v = Path(_tf.mkdtemp())
(_v / "inst" / "minecraft" / "mods").mkdir(parents=True)
(_v / "inst" / "mmc-pack.json").write_text(_json.dumps({"components": [{"uid": "net.minecraft", "version": "1.18.2"}]}), encoding="utf-8")
check("version from mmc-pack.json", te.detect_mc_version(_v / "inst" / "minecraft") == "1.18.2")
check("pack_format 1.18.2 = 8 without options.txt", te.detect_pack_format(_v / "inst" / "minecraft") == 8)
(_v / "j" / "mods").mkdir(parents=True)
for _n in ["a-1.17.1-2.0.jar", "b_1.17.1.jar", "c-fabric-1.17-3.jar", "lib-9.0.jar"]:
    (_v / "j" / "mods" / _n).write_bytes(b"x")
check("version from mod jar names", (te.detect_mc_version(_v / "j") or "").startswith("1.17"))
check("pack_format 1.17 = 7", te.detect_pack_format(_v / "j") == 7)
check("pack_format 1.14 = 4, 1.15 = 5", te._pack_format_from_version_string("1.14.4") == 4 and te._pack_format_from_version_string("1.15.2") == 5)
(_v / "k").mkdir(); (_v / "k" / "options.txt").write_text("version:1976\n", encoding="utf-8")
check("options.txt 1.14.4 dataVersion -> 4", te.detect_pack_format(_v / "k") == 4)
check("unknown instance falls back to default", te.detect_pack_format(_v / "nothing") == te.DEFAULT_PACK_FORMAT)

_old_dirs = (te.PATCHOULI_OUTPUT_DIR, te.RESOURCEPACK_DIR, te.TRANSLATED_MODPACK_DIR)
te.PATCHOULI_OUTPUT_DIR, te.RESOURCEPACK_DIR, te.TRANSLATED_MODPACK_DIR = _v / "pat", _v / "rp", _v / "tm"
_res = te.AnalysisResult()
_res.generic_json_sources = [{"modid": "m", "jar": "x.jar", "kind": "PATCHOULI",
                              "entry": "assets/m/patchouli_books/b/en_us/entries/x.json", "data": {"name": "Hello world friend"}}]
te.write_generic_json_sources(_res, {"Hello world friend": "Привет, мир"}, {"errors": []})
check("use_resource_pack book goes to the resource pack, not a JAR",
      (te.RESOURCEPACK_DIR / "assets/m/patchouli_books/b/ru_ru/entries/x.json").exists() and not te.PATCHOULI_OUTPUT_DIR.exists())
te.PATCHOULI_OUTPUT_DIR, te.RESOURCEPACK_DIR, te.TRANSLATED_MODPACK_DIR = _old_dirs

shutil.rmtree(tmp, ignore_errors=True)
print()
print("ALL OK" if not FAILS else f"FAILED: {FAILS}")
sys.exit(1 if FAILS else 0)
