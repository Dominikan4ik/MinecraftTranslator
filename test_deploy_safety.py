

import json, os, shutil, sys, tempfile, types
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
import translator_engine as te


def check(name, cond):
    print(("[OK]   " if cond else "[FAIL] ") + name)
    if not cond:
        raise AssertionError(name)


def raises(exc, fn):
    try:
        fn()
    except exc as e:
        return e
    except BaseException as e:
        print("   unexpected", repr(e)); return None
    return None


def tree(root):
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None)
            for p in sorted(root.rglob("*")) if "Translation_Backups" not in p.parts}


def make_pack(td):
    mp = Path(td) / "Моя сборка с пробелами" / "minecraft"
    for rel, data in {"config/a.json": b"A", "config/b.json": b"B", "kubejs/c.js": b"C",
                      "options.txt": b"lang:en_us\n", "mods/x.jar": b"JARDATA" * 1000}.items():
        f = mp / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes(data)
    return mp



with tempfile.TemporaryDirectory() as td:
    mp = make_pack(td)
    existing = [mp / "config/a.json", mp / "config/b.json", mp / "kubejs/c.js", mp / "options.txt", mp / "mods/x.jar"]
    new = [mp / "kubejs/assets/мод/lang/ru_ru.json", mp / "resourcepacks/Modpack_Auto_Rus.zip"]
    before = tree(mp)
    allf = existing + new
    for n in range(0, len(allf) + 1):
        backup = Path(td) / f"bk{n}"
        ds.make_backup(mp, backup, allf, new, [mp / "mods/x.jar"])

        def deploy(n=n):
            for i, p in enumerate(allf):
                if i == n:
                    raise OSError("disk full (injected)")
                p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b"TRANSLATED")
            raise OSError("disk full (injected)")
        logs = []
        err = raises(OSError, lambda: ds.deploy_with_rollback(mp, backup, deploy, logs.append))
        check(f"N={n}: original deploy error is preserved", err is not None and "injected" in str(err))
        check(f"N={n}: tree identical to pre-deploy state (restored/removed/new dirs gone)", tree(mp) == before)


with tempfile.TemporaryDirectory() as td:
    mp = make_pack(td)
    files = [mp / "config/a.json", mp / "config/b.json", mp / "kubejs/c.js"]
    backup = Path(td) / "bk"
    ds.make_backup(mp, backup, files, [])
    (backup / "config/a.json").write_bytes(b"CORRUPTED")
    def deploy():
        for p in files: p.write_bytes(b"T")
        raise ValueError("ORIGINAL")
    err = raises(ds.DeployRollbackFailed, lambda: ds.deploy_with_rollback(mp, backup, deploy))
    check("original error survives a failed rollback (message, __cause__)",
          err is not None and str(err).startswith("ORIGINAL") and isinstance(err.__cause__, ValueError)
          and isinstance(err.rollback_error, ds.RestoreError))
    check("rollback failure is reported with the backup path", str(backup) in str(err))
    check("a hash-corrupt backup copy is NOT written over the target", (mp / "config/a.json").read_bytes() == b"T")
    check("restore continued past the failure (b restored)", (mp / "config/b.json").read_bytes() == b"B")
    check("restore continued past the failure (c restored)", (mp / "kubejs/c.js").read_bytes() == b"C")
    e = raises(ds.RestoreError, lambda: ds.restore_backup(mp, backup))
    check("RestoreError lists failing entry", e is not None and any("a.json" in x for x in e.errors))


with tempfile.TemporaryDirectory() as td:
    mp = make_pack(td); f = mp / "config/a.json"
    backup = Path(td) / "bk"; ds.make_backup(mp, backup, [f], [])
    man = backup / ds.MANIFEST_NAME
    good = man.read_text(encoding="utf-8")
    for label, text in [("truncated json", good[:40]), ("empty", ""), ("not an object", "[1,2]"),
                        ("files has wrong type", json.dumps({"files": [1], "new_files": []})),
                        ("new_files wrong type", json.dumps({"files": {}, "new_files": "x"}))]:
        man.write_text(text, encoding="utf-8")
        check(f"manifest {label}: RestoreError, nothing touched",
              raises(ds.RestoreError, lambda: ds.restore_backup(mp, backup)) is not None and f.read_bytes() == b"A")
    man.unlink()
    check("missing manifest: RestoreError", raises(ds.RestoreError, lambda: ds.restore_backup(mp, backup)) is not None)
    for evil in ["../outside.txt", "/etc/passwd", "C:\\Windows\\x", "a/../../b"]:
        man.write_text(json.dumps({"files": {}, "new_files": [evil]}), encoding="utf-8")
        outside = Path(td) / "outside.txt"; outside.write_text("keep")
        e = raises(ds.RestoreError, lambda: ds.restore_backup(mp, backup))
        check(f"path traversal {evil!r} rejected", e is not None and outside.exists())
    man.write_text(json.dumps({"files": {"config/a.json": {"sha256": "0" * 64}}, "new_files": []}), encoding="utf-8")
    f.write_bytes(b"CHANGED")
    check("backup file missing -> error, target untouched",
          raises(ds.RestoreError, lambda: ds.restore_backup(mp, backup)) is not None and f.read_bytes() == b"CHANGED")


with tempfile.TemporaryDirectory() as td:
    mp = make_pack(td); f = mp / "config/a.json"; n = mp / "kubejs/new.js"
    backup = Path(td) / "bk"; (backup / "config").mkdir(parents=True)
    shutil.copy2(f, backup / "config/a.json")
    (backup / ds.MANIFEST_NAME).write_text(json.dumps({"existing_files": ["config/a.json"], "new_files": ["kubejs/new.js"]}))
    f.write_bytes(b"X"); n.write_bytes(b"N")
    ds.restore_backup(mp, backup)
    check("v1 manifest restore works", f.read_bytes() == b"A" and not n.exists())


with tempfile.TemporaryDirectory() as td:
    mp = make_pack(td); f = mp / "config/a.json"
    backup = Path(td) / "bk"; ds.make_backup(mp, backup, [f], [])
    s1 = ds.restore_backup(mp, backup); s2 = ds.restore_backup(mp, backup)
    check("restore of untouched state is a no-op (already_ok)", s1["already_ok"] == 1 and s2["restored"] == 0)
    d = mp / "kubejs" / "precious"; d.mkdir(); (d / "user.txt").write_text("mine")
    (backup / ds.MANIFEST_NAME).write_text(json.dumps({"files": {}, "new_files": ["kubejs/precious"]}))
    e = raises(ds.RestoreError, lambda: ds.restore_backup(mp, backup))
    check("directory listed as new file is NOT deleted", e is not None and (d / "user.txt").read_text() == "mine")


with tempfile.TemporaryDirectory() as td:
    mp = make_pack(td); outside = Path(td) / "outside"; outside.mkdir(); (outside / "secret.txt").write_text("S")
    try:
        os.symlink(outside, mp / "linked", target_is_directory=True); can_link = True
    except (OSError, NotImplementedError):
        can_link = False
    if can_link:
        t = mp / "linked" / "secret.txt"
        e = raises(ds.BackupError, lambda: ds.make_backup(mp, Path(td) / "bk", [t], []))
        check("deploy target behind symlinked dir refused at backup time", e is not None and not (Path(td) / "bk").exists())
        os.symlink(mp / "config/a.json", mp / "config/link.json")
        e = raises(ds.BackupError, lambda: ds.make_backup(mp, Path(td) / "bk2", [mp / "config/link.json"], []))
        check("deploy target that is a symlink file refused", e is not None)
        (Path(td) / "bk3").mkdir()
        (Path(td) / "bk3" / ds.MANIFEST_NAME).write_text(json.dumps({"files": {}, "new_files": ["linked/secret.txt"]}))
        e = raises(ds.RestoreError, lambda: ds.restore_backup(mp, Path(td) / "bk3"))
        check("restore never deletes through a symlink", e is not None and (outside / "secret.txt").exists())
    else:
        print("[SKIP] symlink tests (cannot create symlinks here; needs Windows/dev-mode check)")


with tempfile.TemporaryDirectory() as td:
    mp = make_pack(td); files = [mp / "config/a.json", mp / "config/b.json", mp / "kubejs/c.js"]
    calls = {"n": 0}
    def cancel_after_two():
        calls["n"] += 1; return calls["n"] > 2
    bk = Path(td) / "bk"
    check("mid-backup cancel raises", raises(RuntimeError, lambda: ds.make_backup(mp, bk, files, [], cancelled=cancel_after_two)) is not None)
    check("mid-backup cancel removes partial backup", not bk.exists())
    check("originals untouched by backup", (mp / "config/a.json").read_bytes() == b"A")


with tempfile.TemporaryDirectory() as td:
    root = Path(td); mp = make_pack(td)
    saved = {k: getattr(te, k) for k in ("TRANSLATED_MODPACK_DIR", "RESOURCEPACK_DIR")}
    try:
        te.TRANSLATED_MODPACK_DIR = root / "Translated_Modpack"
        te.RESOURCEPACK_DIR = root / "rp"
        for rel in ("config/a.json", "config/b.json", "kubejs/new/n.js", "kubejs/c.js"):
            p = te.TRANSLATED_MODPACK_DIR / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b"TR")
        app = object.__new__(gui_app.TranslatorApp)
        app._queue_log = lambda *_: None
        app._patch_jars_enabled = lambda _m: False
        app._lang_overlay_targets = lambda _m, _r: {}
        result = types.SimpleNamespace(generic_json_sources=[], lang_json_sources=[])
        app._backup_root = lambda _m: root / "Translation_Backups" / "t1"
        before = tree(mp)
        te.clear_cancel()
        backup = app._make_backup(mp, result)
        real_copy2 = shutil.copy2; count = {"n": 0}
        def flaky(src, dst, *a, **k):
            count["n"] += 1
            if count["n"] == 3: raise OSError("injected on 3rd copy")
            return real_copy2(src, dst, *a, **k)
        gui_app.shutil.copy2 = flaky
        try:
            err = raises(OSError, lambda: gui_app.deploy_safety.deploy_with_rollback(
                mp, backup, lambda: app._deploy_outputs(mp, result)))
        finally:
            gui_app.shutil.copy2 = real_copy2
        check("GUI deploy: injected failure surfaces as original error", err is not None and "injected" in str(err))
        check("GUI deploy: modpack identical to pre-deploy state", tree(mp) == before)
    finally:
        for k, v in saved.items(): setattr(te, k, v)

print("DEPLOY SAFETY TESTS OK")
