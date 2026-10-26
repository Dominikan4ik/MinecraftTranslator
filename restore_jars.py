# -*- coding: utf-8 -*-
                                                                          

                                                                                                  
                                                                        

                                                                                   

                                                                                                   
                                                                                                   
                                        
   
import json, shutil, sys, zipfile
from pathlib import Path


def main(argv):
    if len(argv) != 3:
        print(__doc__); return 2
    root, mc = Path(argv[1]), Path(argv[2])
    if not root.is_dir() or not (mc / "mods").is_dir():
        print("Проверьте пути: нужна папка Translation_Backups и папка minecraft (внутри mods)."); return 2
    restored, skipped = {}, []
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        mf = folder / "backup_manifest.json"
        if not mf.exists():
            continue
        for rel in json.loads(mf.read_text(encoding="utf-8")).get("jar_files", []):
            if rel in restored:
                continue
            src = folder / rel
            if not src.is_file():
                continue
            try:
                with zipfile.ZipFile(src) as z:
                    bad = z.testzip()
                if bad:
                    raise zipfile.BadZipFile(f"повреждён {bad}")
            except Exception as e:
                skipped.append((rel, f"{folder.name}: {e}")); continue
            shutil.copy2(src, mc / rel)
            restored[rel] = folder.name
    removed = 0
    for tmp in (mc / "mods").glob("*.translation_tmp"):
        tmp.unlink(); removed += 1
    print(f"Возвращено JAR: {len(restored)}; удалено временных файлов: {removed}")
    for rel, why in skipped:
        print(f"ПРОПУЩЕН {rel}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
