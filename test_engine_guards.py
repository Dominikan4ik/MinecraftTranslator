


import asyncio, tempfile, time, types
from pathlib import Path
import translator_engine as te


def check(name, cond):
    print(("[OK]   " if cond else "[FAIL] ") + name)
    if not cond:
        raise AssertionError(name)



V = te.validate_technical_consistency
cases = [
    ("uuid kept", "Owner 123e4567-e89b-12d3-a456-426614174000 here", "Владелец 123e4567-e89b-12d3-a456-426614174000 здесь", True),
    ("uuid transliterated", "Owner 123e4567-e89b-12d3-a456-426614174000", "Владелец 123е4567-е89б-12д3-а456-426614174000", False),
    ("hex id kept", "Quest 27B28A53F0EFE604 done", "Квест 27B28A53F0EFE604 выполнен", True),
    ("hex id transliterated (FTB Quests bug)", "Quest 27B28A53F0EFE604 done", "Квест 27Б28А53Ф0ЭФЕ604 выполнен", False),
    ("namespace kept", "Use minecraft:iron_ingot to craft", "Используйте minecraft:iron_ingot для создания", True),
    ("namespace case changed", "Use minecraft:iron_ingot", "Используйте Minecraft:iron_ingot", False),
    ("namespace dropped", "Use minecraft:iron_ingot", "Используйте железный слиток", False),
    ("url kept", "Wiki: https://example.com/a/b?x=1 now", "Вики: https://example.com/a/b?x=1 сейчас", True),
    ("url host swapped", "Download https://example.com/f.zip", "Скачать https://evil.example/f.zip", False),
    ("url trailing dot", "See https://example.com/a.", "См. https://example.com/a.", True),
    ("url in parens", "(see https://example.com/a)", "(см. https://example.com/a)", True),
    ("file path kept", "Edit assets/mod/lang/en_us.json file", "Измените assets/mod/lang/en_us.json файл", True),
    ("%s kept", "You have %s items", "У вас %s предметов", True),
    ("%s dropped", "You have %s items", "У вас предметов", False),
    ("%1$s %2$s reordered", "%1$s killed %2$s", "%2$s был убит %1$s", True),
    ("{player} kept", "Hello {player}!", "Привет, {player}!", True),
    ("{player} translated", "Hello {player}!", "Привет, {игрок}!", False),
    ("section codes kept", "§aGreen §lBold§r text", "§aЗелёный §lЖирный§r текст", True),
    ("section codes reordered", "§l§nTitle", "§n§lЗаголовок", True),
    ("section code lost", "§aGreen text", "Зелёный текст", False),
    ("&-codes kept", "&6Gold &rreset", "&6Золото &rсброс", True),
    ("Salt & Pepper", "Salt & Pepper", "Соль и перец", True),
    ("Q&A", "Q&A section", "Раздел вопросов и ответов", True),
    ("ratio 1:1", "Ratio is 1:1 here", "Соотношение 1:1 здесь", True),
    ("time 5:30", "Starts at 5:30 pm", "Начинается в 5:30 вечера", True),
    ("Note:use (no space after colon)", "Note:use this", "Примечание: используйте это", True),
    ("big number kept", "Cost 10000000 coins", "Стоимость 10000000 монет", True),
    ("big number grouped by space (formatting, allowed)", "Cost 10000000 coins", "Стоимость 10 000 000 монет", True),
    ("big number grouped by comma (allowed)", "Cost 10000000 coins", "Стоимость 10,000,000 монет", True),
    ("big number changed", "Cost 10000000 coins", "Стоимость 10000001 монет", False),
    ("big number dropped", "Cost 10000000 coins", "Стоимость монет", False),
    ("JSON text component", '{"text":"Hello","color":"red"}', '{"text":"Привет","color":"red"}', True),
    ("JSON with namespace id", '{"id":"minecraft:stone","Count":1}', '{"id":"minecraft:stone","Count":1}', True),
    ("SNBT \\n escape kept", "Line one\\nLine two", "Строка один\\nСтрока два", True),
    ("KubeJS ${name}", "Hi ${name}", "Привет ${name}", True),
    ("&#RRGGBB kept", "&#FF0000Red text", "&#FF0000Красный текст", True),
    ("&#RRGGBB case changed", "&#ff0000Red", "&#FF0000Красный", False),
]
for name, o, t, exp in cases:
    check(f"validator: {name}", V(o, t) is exp)


async def fallback_test():
    saved = {k: getattr(te, k) for k in ("async_playwright", "REPORTS_DIR")}
    try:
        te.async_playwright = object()
        with tempfile.TemporaryDirectory() as td:
            te.REPORTS_DIR = Path(td)
            eng = te.GoogleTranslateEngine(type("C", (), {"get": lambda s, k: None, "put": lambda s, k, v: None})(), None)
            async def raw_bad(self, texts):
                return ["Владелец 27Б28А53Ф0ЭФЕ604 вошёл в игру сегодня"]
            async def raw_ok(self, texts):
                return ["Владелец 27B28A53F0EFE604 вошёл в игру сегодня"]
            src = "&cOwner 27B28A53F0EFE604 joined the game today"
            eng._translate_batch_raw = types.MethodType(raw_bad, eng)
            check("plain fallback rejects transliterated hex id", await eng._plain_fallback(src, "", "", ["&c"]) is None)
            check("plain fallback counted the rejection", eng.stats["technical_rejected"] == 1)
            eng._translate_batch_raw = types.MethodType(raw_ok, eng)
            r = await eng._plain_fallback(src, "", "", ["&c"])
            check("plain fallback accepts an intact hex id", r is not None and "27B28A53F0EFE604" in r and r.startswith("&c"))
    finally:
        for k, v in saved.items(): setattr(te, k, v)
asyncio.run(fallback_test())



class MemCache:
    def __init__(self): self.d = {}
    def get(self, k): return self.d.get(k)
    def put(self, k, v): self.d[k] = v


async def identity_guard(self, batch, translated):
    return translated


def mk_engine():
    eng = te.GoogleTranslateEngine(MemCache(), None)
    eng._guard_batch_alignment = types.MethodType(identity_guard, eng)
    return eng


def sentence(i):
    return f"This is a normal sentence number {i} with enough words in it"


async def run_with(raw, strings, *, max_suspect=1, cooldowns=(0.0,), batch_chars=3900, cancel_after=None):
    saved = {k: getattr(te, k) for k in ("MAX_CONSECUTIVE_SUSPECT_BATCHES", "CIRCUIT_BREAKER_COOLDOWNS",
                                          "async_playwright", "REPORTS_DIR", "BATCH_SIZE", "PROGRESS_CALLBACK")}
    prog = []
    try:
        te.configure_translation(1, batch_chars)
        te.MAX_CONSECUTIVE_SUSPECT_BATCHES = max_suspect
        te.CIRCUIT_BREAKER_COOLDOWNS = cooldowns
        te.async_playwright = object()
        te.set_progress_callback(lambda *a: prog.append(a))
        te.clear_cancel()
        with tempfile.TemporaryDirectory() as td:
            te.REPORTS_DIR = Path(td)
            eng = mk_engine()
            eng._translate_batch_raw = types.MethodType(raw, eng)
            t0 = time.monotonic()
            if cancel_after is None:
                out = await eng.translate_many(strings)
            else:
                task = asyncio.create_task(eng.translate_many(strings))
                await asyncio.sleep(cancel_after)
                te.request_cancel()
                out = await asyncio.wait_for(task, timeout=5)
            return eng, out, prog, time.monotonic() - t0
    finally:
        te.clear_cancel()
        for k, v in saved.items(): setattr(te, k, v)


def make_raw(n_echo, counter):
    async def raw(self, texts):
        counter["calls"] += 1
        return [t if i < n_echo else f"Русский перевод {i}" for i, t in enumerate(texts)]
    return raw


async def ratio_tests():
    strings = [sentence(i) for i in range(10)]
    for n_echo, expect_open in [(4, False), (5, True), (6, True)]:
        c = {"calls": 0}
        eng, out, _, _ = await run_with(make_raw(n_echo, c), strings)
        check(f"echo ratio {n_echo}/10 -> breaker {'OPEN' if expect_open else 'closed'} "
              f"(NOOP_BATCH_SUSPECT_RATIO={te.NOOP_BATCH_SUSPECT_RATIO})", eng._circuit_open is expect_open)
        check(f"echo ratio {n_echo}/10: every input has a result", all(s in out for s in strings))
        check(f"echo ratio {n_echo}/10: echoed lines are failed, never 'translated'",
              sum(1 for r in out.values() if r.status == "translated") == 10 - n_echo)
asyncio.run(ratio_tests())


async def healthy_between_failures():

    order = {"n": 0, "calls": 0}
    async def raw(self, texts):
        order["calls"] += 1; order["n"] += 1
        return list(texts) if order["n"] % 2 == 1 else [f"Русский перевод {i}" for i, _ in enumerate(texts)]
    strings = [sentence(i) for i in range(10)]
    eng, out, _, _ = await run_with(raw, strings, max_suspect=2, batch_chars=140)
    check("healthy batches between failures: several batches were really sent", order["calls"] >= 5)
    check("healthy batch resets the streak: breaker stays closed", not eng._circuit_open)
    check("streak counter is 0 or 1 at the end, never accumulated", eng._consecutive_suspect_batches <= 1)

    order2 = {"n": 0, "calls": 0}
    async def raw2(self, texts):
        order2["calls"] += 1
        return list(texts)
    eng2, out2, _, _ = await run_with(raw2, strings, max_suspect=2, batch_chars=140)
    check("two consecutive echo batches open the breaker", eng2._circuit_open)
    check("no request after the breaker opened (exactly 2 sent)", order2["calls"] == 2)
asyncio.run(healthy_between_failures())


async def big_list_and_progress():
    c = {"calls": 0}
    strings = [sentence(i) for i in range(120)]
    eng, out, prog, _ = await run_with(make_raw(99, c), strings, batch_chars=300)
    check("big list: breaker opened", eng._circuit_open)
    check("big list: only the first batch hit the network", c["calls"] == 1)
    check("big list: all 120 inputs got a result", len(out) == 120 and all(s in out for s in strings))
    check("big list: nothing falsely 'translated'", not any(r.status == "translated" for r in out.values()))
    check("big list: aborted lines are counted", eng.stats["circuit_breaker_aborted"] > 0)
    tr = [p for p in prog if p[0] == "translation"]
    check("big list: progress finishes at total", tr and tr[-1][1] == tr[-1][2])
asyncio.run(big_list_and_progress())


async def cancel_in_cooldown():
    c = {"calls": 0}
    strings = [sentence(i) for i in range(30)]

    eng, out, prog, took = await run_with(make_raw(99, c), strings, max_suspect=3, cooldowns=(30.0,),
                                           batch_chars=300, cancel_after=0.5)
    check(f"cancel during cooldown returns promptly ({took:.1f}s, was up to 30-600s)", took < 4)
    check("cancel during cooldown: no new request after cancel", c["calls"] == 1)
    check("cancel during cooldown: every input has a (failed) result", len(out) == 30 and
          not any(r.status == "translated" for r in out.values()))
asyncio.run(cancel_in_cooldown())




async def retry_only_missing():
    saved = {k: getattr(te, k) for k in ("async_playwright", "REPORTS_DIR", "BASE_BACKOFF")}
    try:
        te.async_playwright = object(); te.BASE_BACKOFF = 0.0
        with tempfile.TemporaryDirectory() as td:
            te.REPORTS_DIR = Path(td)
            eng = mk_engine()
            sent = []
            async def fake_group(self, texts, group, legacy_single=False):
                sent.append(list(group))

                if len(sent) == 1:
                    return [f"OK{i}" if i != 2 else "" for i in group], False
                return [f"RETRY{i}" for i in group], False
            eng._translate_group = types.MethodType(fake_group, eng)
            texts = [f"text {i}" for i in range(5)]
            results = await eng._translate_batch_raw(texts)
            check("P1.1: first request carries the whole group", sent[0] == [0, 1, 2, 3, 4])
            check("P1.1: second request carries ONLY the unresolved line", sent[1] == [2])
            check("P1.1: already translated lines are not overwritten",
                  [results[i] for i in (0, 1, 3, 4)] == ["OK0", "OK1", "OK3", "OK4"] and results[2] == "RETRY2")
            check("P1.1: exactly two requests in total", len(sent) == 2)
    finally:
        for k, v in saved.items(): setattr(te, k, v)
asyncio.run(retry_only_missing())



async def stop_during_pauses():
    te.clear_cancel()
    t0 = time.monotonic()
    task = asyncio.create_task(te._interruptible_sleep(30))
    await asyncio.sleep(0.3); te.request_cancel()
    await asyncio.wait_for(task, 3)
    check(f"_interruptible_sleep wakes on Stop ({time.monotonic()-t0:.1f}s instead of 30s)", time.monotonic() - t0 < 3)
    te.clear_cancel()
    rl = te._RateLimiter() if hasattr(te, "_RateLimiter") else None
    rl.MIN_REQUEST_INTERVAL = 20.0
    await rl.acquire()
    t1 = time.monotonic()
    task = asyncio.create_task(rl.acquire())
    await asyncio.sleep(0.3); te.request_cancel()
    await asyncio.wait_for(task, 3)
    check(f"rate limiter wait is interrupted by Stop ({time.monotonic()-t1:.1f}s)", time.monotonic() - t1 < 3)
    te.clear_cancel()
    eng = mk_engine()
    eng._rate = rl
    called = []
    async def fake_browser(self, payload): called.append(payload); return "x"
    eng._browser_translate = types.MethodType(fake_browser, eng)
    te.request_cancel()
    r = await eng._one_request("hello")
    te.clear_cancel()
    check("no request is sent to Google after Stop", r == (None, False) and not called)
asyncio.run(stop_during_pauses())



def kubejs_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        mc = Path(td); (mc / "kubejs" / "client_scripts").mkdir(parents=True)
        src = ('ItemEvents.tooltip(e => {\n'
               '  Item.of("minecraft:diamond").displayName("Café du Monde — fresh \\u2615 coffee machine")\n'
               '  Item.of("minecraft:gold_ingot").displayName("Привет, this is a long shiny tooltip")\n'
               '})\n')
        (mc / "kubejs" / "client_scripts" / "t.js").write_text(src, encoding="utf-8")
        saved = te.MC_DIR; te.MC_DIR = mc
        try:
            res = te.AnalysisResult()
            te.analyze_kubejs(res)
        finally:
            te.MC_DIR = saved
        texts = [c.text for c in res.candidates]
        check("P0.1: candidates contain no mojibake (no 'Ã'/'Ð' chars)", texts and not any(("Ã" in x or "Ð" in x) for x in texts))
        check("P0.1: non-ASCII + escape decoded correctly", any(x == "Café du Monde — fresh ☕ coffee machine" for x in texts))
        if res.kubejs_script_sources:
            s = res.kubejs_script_sources[0]
            out = te.apply_kubejs_script_translation(s["raw"], s["matches"],
                                                     {"Café du Monde — fresh ☕ coffee machine": "Кофемашина «Кафе»"})
            check("P0.1: rewrite replaces the literal and keeps the rest of the file intact",
                  "Кофемашина «Кафе»" in out and '.displayName("Привет, this is a long shiny tooltip")' in out
                  and te.validate_kubejs_script_rewrite(s["raw"], out))
kubejs_roundtrip()




import json as _json, zipfile as _zf
async def mod_names_end_to_end():
    saved = {k: getattr(te, k) for k in ("MC_DIR", "async_playwright", "REPORTS_DIR", "PROTECTED_NAMES_PATH", "GLOSSARY_PATH")}
    try:
        with tempfile.TemporaryDirectory() as td:
            mc = Path(td) / "mc"; (mc / "mods").mkdir(parents=True)
            toml = ('modLoader="javafml"\n[[mods]]\nmodId="ftbultimine"\ndisplayName="FTB Ultimine"\n'
                    '[[mods]]\nmodId="mcwwindows"\ndisplayName="Macaw\'s Windows"\n')
            lang = {
                "key.categories.ftbultimine": "FTB Ultimine",
                "itemGroup.windows": "Macaw's Windows",
                "ftbultimine.info.base": "FTB Ultimine is %s",
                "ftbultimine.tip": "Hold the key to mine the whole vein",
            }
            with _zf.ZipFile(mc / "mods" / "ftbultimine.jar", "w") as z:
                z.writestr("META-INF/mods.toml", toml)
                z.writestr("assets/ftbultimine/lang/en_us.json", _json.dumps(lang))
            (Path(td) / "extra_names.txt").write_text("# my names\nSuper Brand Pack\n", encoding="utf-8")
            te.MC_DIR = mc; te.REPORTS_DIR = Path(td) / "rep"; te.async_playwright = object()
            te.PROTECTED_NAMES_PATH = Path(td) / "extra_names.txt"
            te.GLOSSARY_PATH = Path(td) / "no_glossary.json"
            res = te.run_analysis()
            texts = te.get_unique_translatable_texts(res)
            check("e2e: names read from mods.toml are registered", "FTB Ultimine" in te._PROTECTED_WHOLE and "Macaw's Windows" in te._PROTECTED_WHOLE)
            check("e2e: protected_names.txt is honoured", "Super Brand Pack" in te._PROTECTED_WHOLE)
            check("e2e: tab / key-category names are NOT queued for Google",
                  "FTB Ultimine" not in texts and "Macaw's Windows" not in texts)
            check("e2e: normal sentences with a name ARE queued",
                  "FTB Ultimine is %s" in texts and "Hold the key to mine the whole vein" in texts)

            eng = mk_engine()
            sent = []
            async def raw(self, payload_texts):
                sent.extend(payload_texts)
                out = []
                for p in payload_texts:

                    p = p.replace("FTB Ultimine", "FTB Ultimate")
                    out.append(p.replace("is", "это") if "__PH" in p else "Удерживайте клавишу, чтобы добыть всю жилу")
                return out
            eng._translate_batch_raw = types.MethodType(raw, eng)
            te.configure_translation(1, 3900)
            out = await eng.translate_many(["FTB Ultimine is %s", "Hold the key to mine the whole vein"])
            r = out["FTB Ultimine is %s"]
            check("e2e: Google never sees the mod name (placeholder sent instead)",
                  sent and not any("FTB Ultimine" in x for x in sent) and any("__PH" in x for x in sent))
            check("e2e: translated sentence keeps the exact mod name and %s",
                  r.status == "translated" and "FTB Ultimine" in r.translated and "%s" in r.translated)
    finally:
        te.set_protected_names([])
        for k, v in saved.items(): setattr(te, k, v)
asyncio.run(mod_names_end_to_end())

print("ENGINE GUARD TESTS OK")
