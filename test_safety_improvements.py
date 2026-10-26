



import asyncio
import tempfile
import types
from pathlib import Path

import gui_app
import translator_engine as te


def check(name, condition):
    print(("[OK]   " if condition else "[FAIL] ") + name)
    if not condition:
        raise AssertionError(name)




class CacheProbe:
    def __init__(self):
        self.writes = []
    def put(self, key, value):
        self.writes.append((key, value))
    def get(self, key):
        return None

probe = CacheProbe()
engine_probe = te.GoogleTranslateEngine(probe, None)
engine_probe._commit_translation("Download https://example.com/file.zip", "Скачать https://evil.example/file.zip")
check("technical mismatch is rejected before local cache write", not probe.writes)
check("technical rejection is counted", engine_probe.stats["technical_rejected"] == 1)


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    saved = {
        "RESOURCEPACK_DIR": te.RESOURCEPACK_DIR,
        "TRANSLATED_MODPACK_DIR": te.TRANSLATED_MODPACK_DIR,
        "PATCHOULI_OUTPUT_DIR": te.PATCHOULI_OUTPUT_DIR,
        "FULL_LOG_PATH": te.FULL_LOG_PATH,
    }
    try:
        te.RESOURCEPACK_DIR = root / "resourcepack"
        te.TRANSLATED_MODPACK_DIR = root / "translated"
        te.PATCHOULI_OUTPUT_DIR = root / "patchouli"
        te.FULL_LOG_PATH = "test-log-already-started"
        for folder in (te.RESOURCEPACK_DIR, te.TRANSLATED_MODPACK_DIR, te.PATCHOULI_OUTPUT_DIR):
            folder.mkdir()
            (folder / "sentinel.txt").write_text("keep", encoding="utf-8")
        te.request_cancel()
        try:
            te.run_translation_job(reset_cancel=False)
            cancelled_early = False
        except RuntimeError:
            cancelled_early = True
        check("pending cancellation exits before analysis", cancelled_early)
        check("pending cancellation preserves old output folders", all((folder / "sentinel.txt").exists() for folder in (te.RESOURCEPACK_DIR, te.TRANSLATED_MODPACK_DIR, te.PATCHOULI_OUTPUT_DIR)))
    finally:
        te.clear_cancel()
        for key, value in saved.items():
            setattr(te, key, value)


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    modpack = root / "minecraft"
    modpack.mkdir()
    old = modpack / "config" / "settings.json"
    old.parent.mkdir()
    old.write_text('{"value":"original"}', encoding="utf-8")
    new = modpack / "kubejs" / "new_file.js"

    app = object.__new__(gui_app.TranslatorApp)
    backup_dir = root / "backup"
    app._backup_root = lambda _modpack: backup_dir
    app._collect_deploy_targets = lambda _modpack, _result: {
        "files": [old, new], "new_files": [new], "jars": []
    }
    te.clear_cancel()
    backup = app._make_backup(modpack, object())
    old.write_text('{"value":"translated"}', encoding="utf-8")
    new.parent.mkdir(parents=True)
    new.write_text("// newly deployed", encoding="utf-8")
    app._restore_backup(modpack, backup)
    check("rollback restores original file", old.read_text(encoding="utf-8") == '{"value":"original"}')
    check("rollback removes file absent before deploy", not new.exists())


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    modpack = root / "minecraft"
    modpack.mkdir()
    existing = modpack / "a.txt"
    existing.write_text("original", encoding="utf-8")
    backup_dir = root / "partial-backup"
    app = object.__new__(gui_app.TranslatorApp)
    app._backup_root = lambda _modpack: backup_dir
    app._collect_deploy_targets = lambda _modpack, _result: {
        "files": [existing], "new_files": [], "jars": []
    }
    te.request_cancel()
    try:
        app._make_backup(modpack, object())
        raised = False
    except RuntimeError:
        raised = True
    finally:
        te.clear_cancel()
    check("cancelled backup raises", raised)
    check("cancelled backup directory is removed", not backup_dir.exists())


class MemoryCache:
    def __init__(self):
        self.data = {}
    def get(self, key):
        return self.data.get(key)
    def put(self, key, value):
        self.data[key] = value

async def breaker_test():
    old_values = {
        "MAX_CONCURRENT_REQUESTS": te.MAX_CONCURRENT_REQUESTS,
        "BATCH_SIZE": te.BATCH_SIZE,
        "MAX_CONSECUTIVE_SUSPECT_BATCHES": te.MAX_CONSECUTIVE_SUSPECT_BATCHES,
        "CIRCUIT_BREAKER_COOLDOWNS": te.CIRCUIT_BREAKER_COOLDOWNS,
        "async_playwright": te.async_playwright,
        "REPORTS_DIR": te.REPORTS_DIR,
    }
    try:
        te.configure_translation(4, 90)
        te.MAX_CONSECUTIVE_SUSPECT_BATCHES = 1
        te.CIRCUIT_BREAKER_COOLDOWNS = (0.0,)
        te.async_playwright = object()
        with tempfile.TemporaryDirectory() as td:
            te.REPORTS_DIR = Path(td)
            engine = te.GoogleTranslateEngine(MemoryCache(), None)
            calls = 0
            active = 0
            max_active = 0

            async def fake_raw(self, texts):
                nonlocal calls, active, max_active
                calls += 1
                active += 1
                max_active = max(max_active, active)
                await asyncio.sleep(0)
                active -= 1
                return list(texts)

            async def identity_guard(self, batch, translated):
                return translated

            engine._translate_batch_raw = types.MethodType(fake_raw, engine)
            engine._guard_batch_alignment = types.MethodType(identity_guard, engine)
            strings = [f"This is a normal sentence number {i} with enough words" for i in range(8)]
            out = await engine.translate_many(strings)
            check("breaker opens on a mass echo", engine._circuit_open)
            check("no later batch starts after breaker opens", calls == 1)
            check("batch work remains sequential", max_active == 1)
            check("all inputs receive a result", all(s in out for s in strings))
    finally:
        for key, value in old_values.items():
            setattr(te, key, value)

asyncio.run(breaker_test())


async def technical_result_test():
    saved = {
        "MAX_CONCURRENT_REQUESTS": te.MAX_CONCURRENT_REQUESTS,
        "BATCH_SIZE": te.BATCH_SIZE,
        "MAX_CONSECUTIVE_SUSPECT_BATCHES": te.MAX_CONSECUTIVE_SUSPECT_BATCHES,
        "CIRCUIT_BREAKER_COOLDOWNS": te.CIRCUIT_BREAKER_COOLDOWNS,
        "async_playwright": te.async_playwright,
        "REPORTS_DIR": te.REPORTS_DIR,
        "restore_placeholders": te.restore_placeholders,
    }
    try:
        te.configure_translation(1, 3900)
        te.MAX_CONSECUTIVE_SUSPECT_BATCHES = 3
        te.CIRCUIT_BREAKER_COOLDOWNS = (0.0,)
        te.async_playwright = object()
        with tempfile.TemporaryDirectory() as td:
            te.REPORTS_DIR = Path(td)
            cache = MemoryCache()
            engine = te.GoogleTranslateEngine(cache, None)
            async def fake_raw(self, texts):
                return ["Download __PH0__" for _ in texts]
            async def identity_guard(self, batch, translated):
                return translated
            engine._translate_batch_raw = types.MethodType(fake_raw, engine)
            engine._guard_batch_alignment = types.MethodType(identity_guard, engine)
            te.restore_placeholders = lambda _text, _tokens: "Скачать https://evil.example/file.zip"
            source = "Download https://example.com/file.zip"
            results = await engine.translate_many([source])
            check("technical token damage returns failed status", results[source].status == "failed" and results[source].translated is None)
            check("technical token damage is not cached", not cache.data)
    finally:
        for key, value in saved.items():
            setattr(te, key, value)

asyncio.run(technical_result_test())
print("SAFETY TESTS OK")
