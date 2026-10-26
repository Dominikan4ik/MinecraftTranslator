from translator_engine import GoogleTranslateEngine


idxs = list(range(5))
resp = """MTX000000: Привет
MTX000001: Как дела?
MTX000002: Это тест
MTX000003: Майнкрафт — игра
MTX000004: Готово"""
assert GoogleTranslateEngine._parse_marked_response(resp, idxs) == [
    "Привет", "Как дела?", "Это тест", "Майнкрафт — игра", "Готово"
]



partial = """MTX000000: Один
MTX000001: Два
MTX000003: Четыре
MTX000004: Пять"""
assert GoogleTranslateEngine._parse_marked_response_partial(partial, [0,1,2,3,4]) == [
    "Один", None, None, "Четыре", "Пять"
]

print("marker parser tests: OK")
