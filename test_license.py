

import re, shutil, sys, tempfile, types, zipfile
from pathlib import Path

try:
    import tkinter
except ImportError:
    class _A:
        def __init__(s, *a, **k): pass
        def __getattr__(s, n): return _A()
        def __call__(s, *a, **k): return _A()
    m = types.ModuleType("tkinter"); m.Tk = _A
    for n in ("ttk", "messagebox", "filedialog", "font"):
        sub = types.ModuleType("tkinter." + n); sub.__getattr__ = lambda k: _A
        setattr(m, n, sub); sys.modules["tkinter." + n] = sub
    sys.modules["tkinter"] = m

import deploy_safety as ds
import gui_app
import license_texts as L
import translator_engine as te


def check(name, cond):
    print(("[OK]   " if cond else "[FAIL] ") + name)
    if not cond:
        raise AssertionError(name)


HERE = Path(__file__).resolve().parent
CYR = re.compile(r"[А-Яа-яЁё]")


ru_file = (HERE / "LICENSE_RU.txt").read_bytes()
en_file = (HERE / "LICENSE_EN.txt").read_bytes()
check("LICENSE_RU.txt on disk == embedded bytes", ru_file == L.license_bytes()["LICENSE_RU.txt"])
check("LICENSE_EN.txt on disk == embedded bytes", en_file == L.license_bytes()["LICENSE_EN.txt"])
check("files are UTF-8 with BOM and CRLF (Notepad-safe)", ru_file.startswith(b"\xef\xbb\xbf") and b"\r\n" in ru_file and b"\n" not in ru_file.replace(b"\r\n", b""))
check("RU file is signed [RU], EN file is signed [EN] in the first line",
      L.RU_TEXT.splitlines()[0].startswith("[RU]") and L.EN_TEXT.splitlines()[0].startswith("[EN]"))
check("RU text is Russian, EN text has no Cyrillic at all", CYR.search(L.RU_TEXT) and not CYR.search(L.EN_TEXT))
sec_ru = re.findall(r"^(\d+)\. ", L.RU_TEXT, re.M); sec_en = re.findall(r"^(\d+)\. ", L.EN_TEXT, re.M)
check("both versions have the same sections 1..11 in order", sec_ru == sec_en == [str(i) for i in range(1, 12)])
check("both versions carry version, author and no template brackets",
      all("MTFUL) 1.1" in t and "Dominikan4ik" in t and "[Dominikan4ik]" not in t for t in (L.RU_TEXT, L.EN_TEXT)))
for kw_ru, kw_en in [("КАК ЕСТЬ", "AS IS"), ("Mojang Studios", "Mojang Studios"), ("Результат работы Программы", "Output of the Software")]:
    check(f"both versions contain: {kw_en}", kw_ru in L.RU_TEXT and kw_en in L.EN_TEXT)
bullets = lambda t: len(re.findall(r"^- ", t, re.M))
check("same number of list items in both versions", bullets(L.RU_TEXT) == bullets(L.EN_TEXT) == 10)


with tempfile.TemporaryDirectory() as td:
    src = Path(td) / "rp"; (src / "assets/mod/lang").mkdir(parents=True); (src / "assets/mod/lang/ru_ru.json").write_text("{}", encoding="utf-8")
    z = Path(td) / "pack.zip"
    n = te.build_resourcepack_zip(src, z, 15, extra_files=L.license_bytes())
    with zipfile.ZipFile(z) as zf:
        names = zf.namelist()
        check("pack zip: licence files at the root next to pack.mcmeta", {"pack.mcmeta", "LICENSE_RU.txt", "LICENSE_EN.txt"} <= set(names))
        check("pack zip: licence bytes intact", zf.read("LICENSE_EN.txt") == L.license_bytes()["LICENSE_EN.txt"])
        check("pack zip: translation assets still there", "assets/mod/lang/ru_ru.json" in names and n == 1)
        check("pack zip: valid zip", zf.testzip() is None)
    te.build_resourcepack_zip(src, z, 15, extra_files={"../evil.txt": b"x", "a/b.txt": b"x", "pack.mcmeta": b"x"})
    with zipfile.ZipFile(z) as zf:
        check("pack zip: unsafe/duplicate extra names ignored", set(zf.namelist()) == {"pack.mcmeta", "assets/mod/lang/ru_ru.json"})
    te.build_resourcepack_zip(src, z, 15)
    with zipfile.ZipFile(z) as zf:
        check("pack zip: without extra_files nothing changes", "LICENSE_RU.txt" not in zf.namelist())


def make_env(td):
    root = Path(td); mp = root / "Сборка с пробелами" / "minecraft"
    (mp / "mods").mkdir(parents=True); (mp / "options.txt").write_text("lang:en_us\n")
    (mp / "mods" / "keep.jar").write_bytes(b"JAR")
    saved = {k: getattr(te, k) for k in ("TRANSLATED_MODPACK_DIR", "RESOURCEPACK_DIR")}
    te.TRANSLATED_MODPACK_DIR = root / "Translated_Modpack"
    te.RESOURCEPACK_DIR = root / "rp"
    (te.RESOURCEPACK_DIR / "assets/mod/lang").mkdir(parents=True)
    (te.RESOURCEPACK_DIR / "assets/mod/lang/ru_ru.json").write_text('{"a": "б"}', encoding="utf-8")
    app = object.__new__(gui_app.TranslatorApp)
    app._queue_log = lambda *_: None
    app._patch_jars_enabled = lambda _m: False
    app._lang_overlay_targets = lambda _m, _r: {}
    app._backup_root = lambda _m: root / "Translation_Backups" / "t1"
    return root, mp, app, saved


def tree(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None)
            for p in sorted(root.rglob("*")) if "Translation_Backups" not in p.parts}


result = types.SimpleNamespace(generic_json_sources=[], lang_json_sources=[])
with tempfile.TemporaryDirectory() as td:
    root, mp, app, saved = make_env(td)
    try:
        te.clear_cancel()
        before = tree(mp)
        lic_dir = mp / L.FOLDER_NAME
        targets = app._collect_deploy_targets(mp, result)
        check("licence files are in the backup plan as NEW files (rollback will remove them)",
              all((lic_dir / n) in targets["new_files"] and (lic_dir / n) in targets["files"] for n in L.license_files()))
        check("licence is NOT placed into mods/ or config/", not any("mods" in p.parts or "config" in p.parts
              for p in targets["files"] if p.name.startswith("LICENSE")))


        backup = app._make_backup(mp, result)
        orig = te.enable_resourcepack_in_options
        def boom(*a, **k):
            raise OSError("injected after the pack was built")
        te.enable_resourcepack_in_options = boom
        try:
            err = None
            try:
                ds.deploy_with_rollback(mp, backup, lambda: app._deploy_outputs(mp, result))
            except OSError as e:
                err = e
        finally:
            te.enable_resourcepack_in_options = orig
        check("failure during deploy surfaces as the original error", err is not None and "injected" in str(err))
        check("rollback removed pack, licence files AND the new MinecraftTranslator folder", tree(mp) == before and not lic_dir.exists())


        shutil.rmtree(root / "Translation_Backups", ignore_errors=True)
        backup = app._make_backup(mp, result)
        app._deploy_outputs(mp, result)
        check("deploy writes both licence files", all((lic_dir / n).read_bytes() == L.license_bytes()[n] for n in L.license_files()))
        with zipfile.ZipFile(mp / "resourcepacks" / app.PACK_ZIP_NAME) as zf:
            check("deployed resource pack contains both licence files", {"LICENSE_RU.txt", "LICENSE_EN.txt"} <= set(zf.namelist()))
        check("other files untouched (mods/keep.jar)", (mp / "mods" / "keep.jar").read_bytes() == b"JAR")


        stamp = {n: (lic_dir / n).stat().st_mtime_ns for n in L.license_files()}
        app._deploy_outputs(mp, result)
        check("second deploy leaves identical licence files untouched",
              all((lic_dir / n).stat().st_mtime_ns == stamp[n] for n in stamp))


        (lic_dir / "LICENSE_EN.txt").write_text("OLD LICENCE")
        t2 = app._collect_deploy_targets(mp, result)
        check("existing licence file is backed up before being replaced",
              (lic_dir / "LICENSE_EN.txt") in t2["files"] and (lic_dir / "LICENSE_EN.txt") not in t2["new_files"])
        app._deploy_outputs(mp, result)
        check("outdated licence file is refreshed", (lic_dir / "LICENSE_EN.txt").read_bytes() == L.license_bytes()["LICENSE_EN.txt"])


        shutil.rmtree(lic_dir)
        app.EMBED_LICENSE = False
        check("EMBED_LICENSE=False: no licence targets", app._license_targets(mp) == [])
        app._deploy_outputs(mp, result)
        with zipfile.ZipFile(mp / "resourcepacks" / app.PACK_ZIP_NAME) as zf:
            check("EMBED_LICENSE=False: nothing written, pack has no licence", not lic_dir.exists() and "LICENSE_RU.txt" not in zf.namelist())
    finally:
        for k, v in saved.items(): setattr(te, k, v)

print("LICENSE TESTS OK")
