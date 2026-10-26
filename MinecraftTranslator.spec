# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

ROOT = os.path.abspath(SPECPATH)
APP_NAME = os.environ.get("MT_APP_NAME", "MinecraftTranslator")
BROWSERS = os.environ.get("MT_BROWSERS_DIR", os.path.join(ROOT, ".build_playwright"))
VERSION_FILE = os.path.join(ROOT, "build_version_info.txt")

datas = [(os.path.join(ROOT, "glossary_ru.json"), ".")]
if os.path.isdir(BROWSERS):
    datas.append((BROWSERS, "playwright-browsers"))
binaries = []
hiddenimports = ["deploy_safety", "license_texts", "translator_engine", "json5"]
tmp_ret = collect_all("playwright")
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    [os.path.join(ROOT, "gui_app.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=VERSION_FILE if (sys.platform == "win32" and os.path.exists(VERSION_FILE)) else None,
)
