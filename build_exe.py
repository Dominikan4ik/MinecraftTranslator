# -*- coding: utf-8 -*-
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IS_WINDOWS = os.name == "nt"
APP_NAME = "MinecraftTranslator"
EXE_NAME = APP_NAME + (".exe" if IS_WINDOWS else "")
BROWSERS_DIR = ROOT / ".build_playwright"
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"
SPEC_FILE = ROOT / "MinecraftTranslator.spec"
VERSION_FILE = ROOT / "build_version_info.txt"
REQUIRED_FILES = (
    "gui_app.py", "translator_engine.py", "deploy_safety.py", "license_texts.py",
    "glossary_ru.json", "MinecraftTranslator.spec", "requirements.txt",
)
EXTRA_DIST_FILES = ("LICENSE_RU.txt", "LICENSE_EN.txt", "protected_names.txt")
TEST_TIMEOUT = 600
SMOKE_TIMEOUT = 420

TOTAL_STEPS = 8
_step = 0


def step(text: str) -> None:
    global _step
    _step += 1
    print(f"\n[{_step}/{TOTAL_STEPS}] {text}", flush=True)


def fail(message: str, hint: str = "") -> None:
    print(f"\nОШИБКА: {message}", flush=True)
    if hint:
        print(f"Что делать: {hint}", flush=True)
    raise SystemExit(1)


def run(cmd, env=None, timeout=None, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], cwd=str(cwd or ROOT), env=env, timeout=timeout)


def project_version() -> str:
    try:
        text = (ROOT / "CHANGES_RU.md").read_text(encoding="utf-8")
        found = re.findall(r"^##\s*Версия\s+(\d+(?:\.\d+)*)", text, re.MULTILINE)
        if found:
            return found[-1]
    except OSError:
        pass
    return "0.0.0"


def version_tuple(version: str) -> tuple:
    parts = [int(p) for p in re.findall(r"\d+", version)][:4]
    return tuple(parts + [0] * (4 - len(parts)))


def write_version_info(version: str) -> None:
    ft = version_tuple(version)
    text = (
        "VSVersionInfo(\n"
        f"  ffi=FixedFileInfo(filevers={ft}, prodvers={ft}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),\n"
        "  kids=[\n"
        "    StringFileInfo([StringTable('040904B0', [\n"
        "      StringStruct('CompanyName', 'Dominikan4ik'),\n"
        "      StringStruct('FileDescription', 'Minecraft Modpack Translator'),\n"
        f"      StringStruct('FileVersion', '{version}'),\n"
        "      StringStruct('InternalName', 'MinecraftTranslator'),\n"
        "      StringStruct('LegalCopyright', 'Copyright (c) 2026 Dominikan4ik. MTFUL 1.1'),\n"
        "      StringStruct('OriginalFilename', 'MinecraftTranslator.exe'),\n"
        "      StringStruct('ProductName', 'Minecraft Translator'),\n"
        f"      StringStruct('ProductVersion', '{version}')])]),\n"
        "    VarFileInfo([VarStruct('Translation', [1033, 1200])])\n"
        "  ]\n"
        ")\n"
    )
    VERSION_FILE.write_text(text, encoding="utf-8")


def find_browser_executable(root: Path):
    if not root.exists():
        return None
    for pattern in ("chrome.exe", "chrome", "headless_shell.exe", "headless_shell"):
        for candidate in root.rglob(pattern):
            if candidate.is_file():
                return candidate
    return None


def check_sources() -> None:
    step("Проверка файлов проекта")
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).exists()]
    if missing:
        fail("не хватает файлов: " + ", ".join(missing), "распакуйте архив целиком и запустите сборку из его папки")
    if sys.version_info < (3, 10):
        fail(f"нужен Python 3.10 или новее, найден {sys.version.split()[0]}", "установите Python 3.12 x64 с python.org")
    print(f"  Python {sys.version.split()[0]}, версия программы {project_version()}")


def check_modules() -> None:
    step("Проверка библиотек")
    problems = []
    for module_name, package in (("tkinter", "tkinter (входит в Python, при установке включите tcl/tk)"),
                                 ("json5", "json5"), ("playwright", "playwright"), ("PyInstaller", "pyinstaller")):
        try:
            __import__(module_name)
            print(f"  {module_name}: есть")
        except Exception as exc:
            problems.append(f"{package}: {exc}")
    if problems:
        fail("не найдены библиотеки: " + "; ".join(problems),
             "запускайте сборку через BUILD_EXE.bat: он сам создаёт окружение и ставит всё нужное")


def run_preflight(skip_tests: bool) -> None:
    step("Проверка кода перед сборкой")
    if skip_tests:
        print("  пропущено (--skip-tests)")
        return
    env = dict(os.environ, PYTHONUTF8="1")
    tests = sorted(p.name for p in ROOT.glob("test_*.py"))
    for name in tests:
        started = time.time()
        try:
            result = subprocess.run([sys.executable, name], cwd=str(ROOT), env=env, timeout=TEST_TIMEOUT,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            fail(f"тест {name} не завершился за {TEST_TIMEOUT} с")
        ok = result.returncode == 0
        print(f"  {'OK  ' if ok else 'FAIL'} {name} ({time.time() - started:.1f} с)")
        if not ok:
            print("\n".join(result.stdout.splitlines()[-25:]))
            fail(f"тест {name} не прошёл, собирать exe с неисправным кодом нельзя",
                 "пришлите вывод выше автору или запустите сборку с --skip-tests на свой риск")


def ensure_chromium(skip: bool, refresh: bool) -> dict:
    step("Chromium для встраивания в exe")
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=str(BROWSERS_DIR), PYTHONUTF8="1")
    if refresh and BROWSERS_DIR.exists():
        shutil.rmtree(BROWSERS_DIR, ignore_errors=True)
    if find_browser_executable(BROWSERS_DIR) is None:
        if skip:
            fail("Chromium не найден, а --skip-chromium запрещает скачивание", "уберите --skip-chromium")
        print("  скачиваю Chromium (около 150-200 МБ), нужен интернет...")
        result = run([sys.executable, "-m", "playwright", "install", "chromium"], env=env)
        if result.returncode != 0:
            fail("не удалось скачать Chromium", "проверьте интернет/VPN/антивирус и запустите сборку снова")
    exe = find_browser_executable(BROWSERS_DIR)
    if exe is None:
        fail("после установки Chromium не найден в " + str(BROWSERS_DIR))
    print(f"  найден: {exe.relative_to(ROOT)}")
    return env


def build_exe(env: dict, version: str) -> Path:
    step("Сборка exe (PyInstaller, может занять 3-10 минут)")
    write_version_info(version)
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    target = DIST_DIR / EXE_NAME
    if target.exists():
        try:
            target.unlink()
        except OSError:
            fail(f"не удаётся удалить старый {target.name}", "закройте программу, если она запущена, и повторите")
    DIST_DIR.mkdir(exist_ok=True)
    build_env = dict(env, MT_APP_NAME=APP_NAME, MT_BROWSERS_DIR=str(BROWSERS_DIR))
    result = run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
                  "--distpath", DIST_DIR, "--workpath", BUILD_DIR, SPEC_FILE], env=build_env)
    if result.returncode != 0 or not target.exists():
        fail("PyInstaller завершился с ошибкой", "прочитайте последние строки выше; чаще всего помогает закрыть антивирус на время сборки")
    size_mb = target.stat().st_size / (1024 * 1024)
    print(f"  готово: {target} ({size_mb:.0f} МБ)")
    return target


def finalize(target: Path, version: str, make_zip: bool) -> Path:
    step("Лицензия, контрольная сумма, архив")
    copied = []
    for name in EXTRA_DIST_FILES:
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, DIST_DIR / name)
            copied.append(name)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (DIST_DIR / f"{EXE_NAME}.sha256.txt").write_text(f"{digest} *{EXE_NAME}\n", encoding="utf-8")
    print(f"  SHA-256: {digest}")
    print("  рядом с exe: " + ", ".join(copied))
    archive = DIST_DIR / f"{APP_NAME}_v{version}.zip"
    if make_zip:
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(target, EXE_NAME)
            for name in copied:
                z.write(DIST_DIR / name, name)
        print(f"  архив для передачи: {archive.name}")
    return archive


def smoke_test(target: Path, skip: bool) -> None:
    step("Проверка готового exe (самотест и запуск встроенного Chromium)")
    if skip:
        print("  пропущено (--skip-smoke)")
        return
    work = DIST_DIR / "_smoke"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    exe_copy = work / target.name
    shutil.copy2(target, exe_copy)
    report_path = work / "selftest_result.json"
    print("  первый запуск распаковывает файлы, подождите...")
    try:
        result = subprocess.run([str(exe_copy), "--selftest", str(report_path), "--browser"],
                                cwd=str(work), timeout=SMOKE_TIMEOUT)
    except subprocess.TimeoutExpired:
        fail(f"самотест exe не завершился за {SMOKE_TIMEOUT} с", "антивирус мог заблокировать распаковку; добавьте папку dist в исключения")
    if not report_path.exists():
        fail(f"exe запустился (код {result.returncode}), но не создал отчёт самотеста",
             "запустите exe вручную и посмотрите сообщение об ошибке; возможно, антивирус удалил файлы")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    for name, item in report.get("checks", {}).items():
        print(f"  {'OK  ' if item['ok'] else 'FAIL'} {name}" + ("" if item["ok"] else f" - {item['detail']}"))
    shutil.rmtree(work, ignore_errors=True)
    if not report.get("ok"):
        fail("готовый exe не прошёл самотест", "результат выше показывает, что именно не работает")


def main() -> int:
    parser = argparse.ArgumentParser(description="Сборка Minecraft Translator в один exe")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--skip-chromium", action="store_true")
    parser.add_argument("--refresh-chromium", action="store_true")
    parser.add_argument("--skip-smoke", action="store_true")
    parser.add_argument("--no-zip", action="store_true")
    args = parser.parse_args()
    started = time.time()
    print("=" * 60)
    print("  Minecraft Translator: сборка одного exe")
    print("=" * 60)
    version = project_version()
    check_sources()
    check_modules()
    run_preflight(args.skip_tests)
    env = ensure_chromium(args.skip_chromium, args.refresh_chromium)
    target = build_exe(env, version)
    finalize(target, version, not args.no_zip)
    smoke_test(target, args.skip_smoke)
    step("Готово")
    print(f"  Файл для запуска: {target}")
    print(f"  Время сборки: {(time.time() - started) / 60:.1f} мин")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nСборка прервана пользователем.")
        sys.exit(130)
