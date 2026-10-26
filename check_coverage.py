# -*- coding: utf-8 -*-
                                                                     

                                                                                                               

                            
                                                                                                            
                                                                                                               
                                                                                           
                                                                           
   
import json
import re
import sys
import zipfile
from pathlib import Path

CYR = re.compile(r"[а-яА-ЯёЁ]")
PACK = "Modpack_Auto_Rus.zip"


def load_json(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except Exception:
        return None


def collect_ru(mc: Path):
                                                                                               
    ru, sources = {}, {}

    def add(ns, data, where):
        if isinstance(data, dict):
            ru.setdefault(ns, {}).update({k: v for k, v in data.items() if isinstance(v, str)})
            sources.setdefault(ns, set()).add(where)

    kj = mc / "kubejs" / "assets"
    if kj.is_dir():
        for f in kj.glob("*/lang/ru_ru.json"):
            add(f.parts[-3], load_json(f.read_bytes()), "kubejs")
    for zp in list((mc / "resourcepacks").glob("*.zip")) if (mc / "resourcepacks").is_dir() else []:
        try:
            with zipfile.ZipFile(zp) as z:
                for n in z.namelist():
                    m = re.fullmatch(r"assets/([^/]+)/lang/ru_ru\.json", n)
                    if m:
                        add(m.group(1), load_json(z.read(n)), "pack:" + zp.name)
        except Exception:
            pass
    return ru, sources


NOISE_KEY = re.compile(r"(^|[._])(_?comment\w*|language(\.region|\.name|\.code)?|comment_id)$|^_", re.I)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    mc = Path(argv[1])
    if not (mc / "mods").is_dir():
        print("В указанной папке нет mods. Нужна папка minecraft (где mods, config, options.txt).")
        return 2
    out = []
    w = out.append

                                
    w("=== 1. Установка ===")
    opt = mc / "options.txt"
    packs_line = lang_line = ver_line = ""
    if opt.exists():
        for line in opt.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("resourcePacks:"):
                packs_line = line
            elif line.startswith("lang:"):
                lang_line = line
            elif line.startswith("version:"):
                ver_line = line
        w(f"options.txt: {lang_line or 'lang: (нет)'} | {ver_line or 'version: (нет)'}")
        w(f"  {packs_line or 'resourcePacks: (нет)'}")
        w(f"  ресурс-пак включён: {'ДА' if PACK in packs_line else 'НЕТ'}")
        inc = [l for l in opt.read_text(encoding='utf-8', errors='ignore').splitlines() if l.startswith("incompatibleResourcePacks:")]
        if inc and PACK in inc[0]:
            w("  !!! пак в списке несовместимых (неверный pack_format)")
    else:
        w("options.txt: НЕТ (игра ещё не запускалась или файл в другом месте)")
    zp = mc / "resourcepacks" / PACK
    if zp.exists():
        try:
            with zipfile.ZipFile(zp) as z:
                meta = load_json(z.read("pack.mcmeta")) or {}
                names = z.namelist()
            w(f"{PACK}: есть, pack_format={meta.get('pack', {}).get('pack_format')}, "
              f"lang-файлов={sum(1 for n in names if '/lang/' in n)}, tips={sum(1 for n in names if '/tips/' in n)}")
        except Exception as e:
            w(f"{PACK}: ПОВРЕЖДЁН ({e})")
    else:
        w(f"{PACK}: НЕТ в resourcepacks (деплой не дошёл до этого шага?)")
    w(f"KubeJS: {'есть' if (mc / 'kubejs').is_dir() else 'нет'}")
    loaders = []
    jars = sorted((mc / "mods").glob("*.jar"), key=lambda p: p.name.lower())
    w(f"JAR в mods: {len(jars)}")

    ru, ru_src = collect_ru(mc)

                                    
    rows, no_lang, all_missing = [], [], []
    fabric = forge = 0
    for jar in jars:
        try:
            with zipfile.ZipFile(jar) as z:
                names = set(z.namelist())
                fabric += "fabric.mod.json" in names
                forge += "META-INF/mods.toml" in names
                for n in names:
                    m = re.fullmatch(r"assets/([^/]+)/lang/en_us\.json", n)
                    if not m:
                        continue
                    ns = m.group(1)
                    en = load_json(z.read(n))
                    if not isinstance(en, dict):
                        continue
                    own = load_json(z.read(f"assets/{ns}/lang/ru_ru.json")) if f"assets/{ns}/lang/ru_ru.json" in names else {}
                    have = dict(ru.get(ns, {}))
                    if isinstance(own, dict):
                        have.update({k: v for k, v in own.items() if isinstance(v, str)})
                    keys = [k for k, v in en.items()
                            if isinstance(v, str) and re.search(r"[A-Za-z]{3}", v) and not NOISE_KEY.search(k)]
                    if not keys:
                        continue
                    done = [k for k in keys if k in have and CYR.search(have[k])]
                    miss = [k for k in keys if k not in done]
                    all_missing += [(ns, jar.name, k, en[k]) for k in miss]
                    rows.append((len(miss), len(keys), ns, jar.name, miss[:3], sorted(ru_src.get(ns, [])) + (["jar"] if own else [])))
        except Exception as e:
            w(f"!!! не удалось прочитать {jar.name}: {e}")
    w(f"Загрузчик по JAR: Forge={forge}, Fabric={fabric}" + ("  !!! Fabric-моды: переводчик ищет META-INF/mods.toml" if fabric and not forge else ""))

    total = sum(r[1] for r in rows)
    miss_total = sum(r[0] for r in rows)
    w("")
    w("=== 2. Покрытие русским (ключи с английским текстом) ===")
    w(f"Пространств имён: {len(rows)}, ключей: {total}, без русского: {miss_total} "
      f"({(100 * miss_total / total if total else 0):.1f}%)")
    w("Хуже всего (первые 40):")
    for miss, n, ns, jar, sample, src in sorted(rows, reverse=True)[:40]:
        w(f"  {ns:28s} {miss:5d}/{n:<5d} {jar[:44]:44s} источники ru: {','.join(src) or 'нет'}")
        for k in sample[:2]:
            w(f"        пример без перевода: {k}")

                                             
    w("")
    w("=== 3. Подсказки, книги, ресурс-паки ===")
    tips_en = patch_en = patch_ru = 0
    tips_raw, tips_key, tips_bad = 0, 0, []
    pack_names = set()
    if zp.exists():
        try:
            pack_names = set(zipfile.ZipFile(zp).namelist())
        except Exception:
            pass
    for jar in jars:
        try:
            with zipfile.ZipFile(jar) as z:
                names = set(z.namelist())
                for n in names:
                    if re.fullmatch(r"assets/([^/]+)/tips/[^/]+\.json", n):
                        tips_en += 1
                        ns = n.split("/")[1]
                        d = load_json(z.read(n)) or {}
                        tip = d.get("tip") if isinstance(d, dict) else None
                        if isinstance(tip, dict) and "translate" in tip:
                            tips_key += 1
                            key = tip["translate"]
                            if not (key in ru.get(ns, {}) and CYR.search(ru[ns][key])):
                                en_all = load_json(z.read(f"assets/{ns}/lang/en_us.json")) if f"assets/{ns}/lang/en_us.json" in names else {}
                                en_text = (en_all or {}).get(key, "?")
                                tips_bad.append((jar.name[:34], n, f"ключ {key} без русского: {str(en_text)[:60]}"))
                        elif isinstance(tip, str):
                            tips_raw += 1
                            if not (n in pack_names):
                                tips_bad.append((jar.name[:34], n, f"текст в JSON, в паке нет: {tip[:60]}"))
                    if "/patchouli_books/" in n and "/en_us/" in n and n.endswith(".json"):
                        patch_en += 1
                    if "/patchouli_books/" in n and "/ru_ru/" in n and n.endswith(".json"):
                        patch_ru += 1
        except Exception:
            pass
    w(f"Файлов подсказок Tips в JAR: {tips_en} (через lang-ключ: {tips_key}, с текстом прямо в JSON: {tips_raw}); без русского: {len(tips_bad)}")
    for jn, n, why in tips_bad[:25]:
        w(f"   {jn:34s} {n.split('/')[-1][:28]:28s} {why}")
    w(f"Страниц Patchouli en_us: {patch_en}, ru_ru (в JAR): {patch_ru}  "
      "(книги читаются только из JAR мода: без записи в JAR они остаются английскими)")
    for d in ("config/openloader", "kubejs/assets", "resourcepacks"):
        p = mc / d
        if p.exists():
            tips_local = list(p.rglob("tips/*.json"))
            w(f"{d}: подсказок Tips рядом с игрой: {len(tips_local)}")
    other = [p.name for p in (mc / "resourcepacks").glob("*") if p.name != PACK] if (mc / "resourcepacks").is_dir() else []
    w(f"Другие ресурс-паки: {', '.join(other) or 'нет'}")

    tsv = Path(__file__).resolve().parent / "coverage_missing.tsv"
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("namespace\tjar\tkey\tenglish\n")
        for ns, jar, k, v in sorted(all_missing):
            f.write(f"{ns}\t{jar}\t{k}\t{v[:160].replace(chr(9), ' ').replace(chr(10), ' ')}\n")
    w("")
    w(f"Полный список ключей без русского: {tsv.name} ({len(all_missing)} строк)")

    text = "\n".join(out)
    dest = Path(__file__).resolve().parent / "coverage_report.txt"
    dest.write_text(text, encoding="utf-8")
    print(text)
    print(f"\nОтчёт сохранён: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
