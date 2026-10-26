# -*- coding: utf-8 -*-
                                                                                     

                                                                                                     

                                                     
                                                                                   
                                                                                              
                                                                                              
                                                      
                                                                                                     
   
import collections
import re
import sqlite3
import sys
from pathlib import Path

CYR = re.compile(r"[а-яА-ЯёЁ]")


def load_cache(paths):
    cache = {}
    for p in paths:
        if not Path(p).exists():
            continue
        con = sqlite3.connect(p)
        try:
            cols = [r[1] for r in con.execute("pragma table_info(translations)")]
            o = "original_text" if "original_text" in cols else cols[1]
            t = "translated_text" if "translated_text" in cols else cols[4]
            for orig, tr in con.execute(f"select {o}, {t} from translations"):
                cache.setdefault(orig, tr)
        finally:
            con.close()
    return cache


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    rows = [l.rstrip("\n").split("\t") for l in open(argv[1], encoding="utf-8")][1:]
    cache = load_cache(argv[2:])
    print(f"Ключей без русского: {len(rows)}; записей в кэше: {len(cache)}")
    stat = collections.Counter()
    ex = collections.defaultdict(list)
    bymod = collections.defaultdict(collections.Counter)
    for row in rows:
        if len(row) < 4:
            continue
        ns, jar, key, en = row[:4]
        if en not in cache:
            st = "NOT_IN_CACHE"
        else:
            tr = cache[en]
            if tr == en:
                st = "CACHE_ECHO"
            elif CYR.search(tr or ""):
                st = "CACHE_HAS_RUSSIAN"
            else:
                st = "CACHE_NO_CYRILLIC"
        stat[st] += 1
        bymod[ns][st] += 1
        if len(ex[st]) < 12:
            ex[st].append((ns, key[-42:], en[:60], (cache.get(en) or "")[:60]))
    out = ["=== Итог ==="]
    for st, n in stat.most_common():
        out.append(f"{n:6d}  {st}")
    for st, items in ex.items():
        out.append(f"\n--- {st} (примеры) ---")
        for ns, key, en, tr in items:
            out.append(f"  {ns:22s} {key:42s} | {en} -> {tr}")
    out.append("\n--- по модам (первые 15) ---")
    for ns, c in sorted(bymod.items(), key=lambda kv: -sum(kv[1].values()))[:15]:
        out.append(f"  {ns:26s} {dict(c)}")
    text = "\n".join(out)
    print(text)
    (Path(__file__).resolve().parent / "diagnose_missing_report.txt").write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
