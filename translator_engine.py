#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================================================================
# Создатель Dominika4ik
# https://eblo.id/@dominikan4ik
# при поддержке t.me/kefir_play
# сайт моего знакомого https://chkpnt.ru/welcome (активно развивается)
# просьба подписаться на него https://www.youtube.com/@kefir__play__ru
# ======================================================================







































































#3месяца
from __future__ import annotations

import os
import re
import sys
import inspect
import json
import logging
import time
import copy
import shutil
import string
import sqlite3
import hashlib
import asyncio
import zipfile
import traceback
import random
import threading
import unicodedata
import collections
import difflib
import io
import math

try:
    import json5 as _json5
except ImportError:
    _json5 = None
from dataclasses import dataclass, field
#ПИРЕВОДЧИК
from pathlib import Path
from typing import Any, Optional, Union

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    async_playwright = None
    PlaywrightTimeoutError = Exception


# ======================================================================
# Создатель Dominika4ik
# https://eblo.id/@dominikan4ik
# при поддержке t.me/kefir_play
# сайт моего знакомого https://chkpnt.ru/welcome (активно развивается)
# просьба подписаться на него https://www.youtube.com/@kefir__play__ru
# CONFIG
# ======================================================================









ROOT_DIR = Path(__file__).resolve().parent
MC_DIR = ROOT_DIR / "minecraft"
RESOURCEPACK_NAME = "Modpack_Auto_Rus"
RESOURCEPACK_DIR = MC_DIR / "resourcepacks" / RESOURCEPACK_NAME
TRANSLATED_MODPACK_DIR = ROOT_DIR / "Translated_Modpack"


PATCHOULI_OUTPUT_DIR = ROOT_DIR / "Translated_Patchouli"
CACHE_DB_PATH = ROOT_DIR / "translation_cache.db"
REPORTS_DIR = ROOT_DIR / "translation_reports"
TRANSLATION_ERROR_LOG = REPORTS_DIR / "translation_request_errors.log"




FULL_LOG_PATH = None
#Никифор
_FULL_LOGGER = logging.getLogger("minecraft_translator")
_FULL_LOGGER.setLevel(logging.DEBUG)
_FULL_LOGGER.propagate = False
_FULL_LOG_HANDLER = None
_FULL_LOG_STDOUT = None
_FULL_LOG_STDERR = None

class _TeeStream:
    def __init__(self, original, stream_name):
        self.original = original
        self.stream_name = stream_name
    def write(self, data):
        try:
            if self.original:
                self.original.write(data)
                self.original.flush()
        except Exception:
            pass
        try:
            if data:
                _FULL_LOGGER.debug("[%s] %s", self.stream_name, data.rstrip("\n"))
        except Exception:
            pass
    def flush(self):
        try:
            if self.original:
                self.original.flush()
        except Exception:
            pass
    def isatty(self):
        #   t.me/kefir_play
        try:
            return self.original.isatty()
        except Exception:
            return False
    def fileno(self):
        return self.original.fileno()

def start_full_logging(prefix="translation") -> Path:
    global FULL_LOG_PATH, _FULL_LOG_HANDLER, _FULL_LOG_STDOUT, _FULL_LOG_STDERR
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        FULL_LOG_PATH = REPORTS_DIR / f"full_log_{stamp}_{prefix}.log"
        if _FULL_LOG_HANDLER:
            try:
                _FULL_LOGGER.removeHandler(_FULL_LOG_HANDLER)
                _FULL_LOG_HANDLER.close()
            except Exception:
                pass
        _FULL_LOG_HANDLER = logging.FileHandler(FULL_LOG_PATH, mode="w", encoding="utf-8")
        _FULL_LOG_HANDLER.setFormatter(logging.Formatter(
            "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(threadName)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"))
        _FULL_LOG_HANDLER.setLevel(logging.DEBUG)
        _FULL_LOGGER.addHandler(_FULL_LOG_HANDLER)
        _FULL_LOG_STDOUT = sys.stdout
        _FULL_LOG_STDERR = sys.stderr
        sys.stdout = _TeeStream(_FULL_LOG_STDOUT, "STDOUT")
        sys.stderr = _TeeStream(_FULL_LOG_STDERR, "STDERR")
        _FULL_LOGGER.info("=" * 100)
        #   https://www.youtube.com/@kefir__play__ru
        _FULL_LOGGER.info("FULL DIAGNOSTIC LOG STARTED | pid=%s | python=%s", os.getpid(), sys.version.replace("\n", " "))
        _FULL_LOGGER.info("log_file=%s", FULL_LOG_PATH)
        _FULL_LOGGER.info("=" * 100)
        return FULL_LOG_PATH
    except Exception:
        return Path(FULL_LOG_PATH) if FULL_LOG_PATH else REPORTS_DIR / "full_log_failed.log"

def log_event(message: str, level="INFO") -> None:
    try:
        getattr(_FULL_LOGGER, str(level).lower(), _FULL_LOGGER.info)(message)
    except Exception:
        pass

def stop_full_logging() -> None:
    global _FULL_LOG_HANDLER, _FULL_LOG_STDOUT, _FULL_LOG_STDERR
    try:
        _FULL_LOGGER.info("FULL DIAGNOSTIC LOG END")
        if _FULL_LOG_HANDLER:
            _FULL_LOGGER.removeHandler(_FULL_LOG_HANDLER)
            _FULL_LOG_HANDLER.flush()
            _FULL_LOG_HANDLER.close()
            _FULL_LOG_HANDLER = None
    except Exception:
        pass
    try:
        if _FULL_LOG_STDOUT is not None:
            sys.stdout = _FULL_LOG_STDOUT
        if _FULL_LOG_STDERR is not None:
            sys.stderr = _FULL_LOG_STDERR
    except Exception:
        #   https://chkpnt.ru/welcome
        pass






CACHE_DIR = ROOT_DIR / "cache"
GLOBAL_CACHE_DB_PATH = CACHE_DIR / "global_translations.db"
TRANSLATION_CONFLICTS_PATH = CACHE_DIR / "translation_conflicts.json"
INVALID_CACHE_ENTRIES_PATH = CACHE_DIR / "invalid_cache_entries.json"









MANUAL_TRANSLATION_DIR = ROOT_DIR / "manual_translation"
MANUAL_TXT_NAME = "perevod_vruchnuyu.txt"
MANUAL_AI_JSON_NAME = "perevod_dlya_II.json"




GLOBAL_CACHE_SCHEMA_VERSION = 1





QUALITY_VALIDATED = "validated"
QUALITY_UNVALIDATED = "unvalidated"
QUALITY_REJECTED = "rejected"
QUALITY_MANUAL = "manual"
GLOBAL_CACHE_USABLE_STATUSES = (QUALITY_MANUAL, QUALITY_VALIDATED)




SOURCE_GOOGLE = "google"
SOURCE_DEEPL = "deepl"
SOURCE_OLLAMA = "ollama"
SOURCE_MANUAL = "manual"
SOURCE_IMPORTED = "imported"




SOURCE_PRIORITY = (SOURCE_MANUAL, SOURCE_DEEPL, SOURCE_OLLAMA, SOURCE_IMPORTED, SOURCE_GOOGLE)
QUALITY_PRIORITY = (QUALITY_MANUAL, QUALITY_VALIDATED, QUALITY_UNVALIDATED, QUALITY_REJECTED)

SOURCE_LANG = "en"
TARGET_LANG = "ru"

#Nikifor






CLASSIFIER_VERSION = 6













VALIDATOR_VERSION = 3







CACHE_AUDIT_VERSION = 1





COPY_OFFICIAL_RU_INTO_PACK = True








QUARANTINE_ALL_LEGACY_CACHE = True
LEGACY_CACHE_CUTOFF = 1791504000.0









MAX_CONCURRENT_REQUESTS = 1
BATCH_SIZE = 3900


PROGRESS_CALLBACK = None
CANCEL_REQUESTED = False

def set_progress_callback(callback):
    global PROGRESS_CALLBACK
    PROGRESS_CALLBACK = callback

def request_cancel():
    global CANCEL_REQUESTED
    CANCEL_REQUESTED = True

def clear_cancel():
    global CANCEL_REQUESTED
    CANCEL_REQUESTED = False

def _log_translation_error(message: str) -> None:

    #Dominikan4ik
    log_event(message, "ERROR")
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with TRANSLATION_ERROR_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {message}\n")
    except Exception:
        pass


def _progress(stage, current=0, total=0, message=""):
    cb = PROGRESS_CALLBACK
    if cb is not None:
        try:
            cb(stage, current, total, message)
        except Exception:
            pass

def configure_translation(concurrent_requests=1, batch_size=3900):
    global MAX_CONCURRENT_REQUESTS, BATCH_SIZE
    MAX_CONCURRENT_REQUESTS = max(1, int(concurrent_requests))
    BATCH_SIZE = max(1, min(5000, int(batch_size)))





JOIN_SEPARATOR = "\n"

MAX_RETRIES = 5
BASE_BACKOFF = 2.0
REQUEST_TIMEOUT = 20












NOOP_MIN_LEN_FOR_SUSPECT = 3
#Kefir




NOOP_BATCH_SUSPECT_RATIO = 0.5




MAX_CONSECUTIVE_SUSPECT_BATCHES = 3
CIRCUIT_BREAKER_COOLDOWN = 30.0




CIRCUIT_BREAKER_COOLDOWNS = (30.0, 120.0, 600.0)

ANALYZE_ONLY = True


EN_LOCALE_NAMES = {"en_us", "en_gb", "en", "english", "en_au", "en_ca"}


LANG_FILE_EXTS = {".json", ".lang", ".properties", ".json5", ".toml", ".xml", ".txt"}





CONF_HIGH = "HIGH"
CONF_MEDIUM = "MEDIUM"
CONF_LOW = "LOW"
CONF_SKIP = "SKIP"


TEXT_KEY_HINTS = {
    "title", "subtitle", "description", "desc", "text", "message", "msg",
    "label", "tooltip", "comment", "warning", "info", "lore", "dialogue",
    "dialog", "chapter", "quest", "objective", "reward", "name", "displayname",
    "display", "hover", "content", "summary", "notes", "note", "flavor",
    "flavour", "greeting", "prompt", "hint", "story", "narrative", "question",
    "answer", "instructions", "instruction", "welcome", "goodbye", "success",
    "failure", "error", "confirm", "cancel", "accept", "decline", "reject",
    "button", "menu", "header", "footer", "caption",
}





ID_KEY_HINTS = {
    "id", "ids", "uid", "uuid", "guid", "type", "item", "items", "block",
    "blocks", "entity", "recipe", "advancement", "tag", "tags",
    "function", "predicate", "loot_table", "loottable", "texture", "model",
    "sound", "path", "namespace", "registry", "registryname", "registry_name",
    "modid", "mod_id", "translate", "key", "keys", "class", "target",
    "parent", "parents", "child", "children", "link", "links", "dependency",
    "dependencies", "unlocks", "icon", "condition", "conditions", "result",
    "ingredient", "ingredients", "output", "input", "slot", "color", "colour",
    "rgb", "hex", "count", "amount", "level", "duration", "cooldown",
    "priority", "weight", "chance", "x", "y", "z", "width", "height",
    "depth", "version", "format", "protocol", "hash", "checksum",
    "fingerprint", "quest_id", "chapter_id", "task_id", "reward_id",
    "questid", "chapterid", "taskid", "rewardid",
    "formula", "expression", "script", "regex", "macro", "operator",
}

#42БРАТУХА
RESOURCE_LOCATION_RE = re.compile(r"^[a-z0-9_.\-]+:[a-z0-9_./\-]+$")



















TRANSLATION_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+){1,}$")
BARE_ID_RE = re.compile(r"^[a-z][a-z0-9_./:\\-]*$")
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
HEX_COLOR_RE = re.compile(r"^#?[0-9a-fA-F]{6}$|^#?[0-9a-fA-F]{3}$")
NUMBER_RE = re.compile(r"^-?\d+(\.\d+)?[bslfdBSLFD]?$")
BOOL_RE = re.compile(r"^(true|false)$", re.IGNORECASE)
COORD_RE = re.compile(r"^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)
PATH_LIKE_RE = re.compile(
    r"^(assets|data|textures|models|sounds|blockstates|structures)[/\\]", re.IGNORECASE
)
FILE_EXT_RE = re.compile(
    r"\.(png|json|ogg|nbt|snbt|txt|jem|jpm|properties|class|ttf|otf|mcmeta)$",
    re.IGNORECASE,
)




BARE_HEX_ID_RE = re.compile(r"^[0-9A-Fa-f]{8,64}$")




OPAQUE_ID_RE = re.compile(r"^(?=[0-9A-Za-z]{8,64}$)(?=[^ ]*[0-9])[0-9A-Za-z]+$")


CONFIG_ENUM_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")



NAMESPACE_PATH_RE = re.compile(r"^[a-z0-9_.\-]+:[a-z0-9_./\-]+$")













MATH_FUNC_NAMES = {
    "sqrt", "min", "max", "abs", "floor", "ceil", "round", "pow", "log",
    "ln", "sin", "cos", "tan", "mod", "exp", "clamp", "lerp",
}
#228
FORMULA_ALLOWED_CHARS_RE = re.compile(r"^[\sA-Za-z0-9_+\-*/().,^%<>=!&|]+$")
FORMULA_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def is_formula_like(value: str) -> bool:



    v = value.strip()
    if not v:
        return False


    if not re.search(r"[()+\-*/^%<>=!&|]", v):
        return False
    if not FORMULA_ALLOWED_CHARS_RE.match(v):
        return False
    tokens = FORMULA_TOKEN_RE.findall(v)
    if not tokens:
        return False
    for tok in tokens:
        if tok.lower() in MATH_FUNC_NAMES:
            continue
        if tok.isupper():
            continue
        return False
    return True


def _normalize_key(key: str) -> str:
    return re.sub(r"[^a-z]", "", key.lower())


#01012007
def _key_tokens(key: str) -> list[str]:




    s = str(key)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", s)
    return [t for t in re.split(r"[^a-zA-Z0-9]+", s.lower()) if t]


def classify_key(key: str) -> str:








    tokens = _key_tokens(key)
    if not tokens:
        return "neutral"
    token_set = set(tokens)
    if token_set & ID_KEY_HINTS:
        return "id"
    if token_set & TEXT_KEY_HINTS:
        return "text"
    return "neutral"


#   t.me/kefir_play
def looks_like_human_text(value: str) -> bool:

    if not value or not value.strip():
        return False
    v = value.strip()
    if len(v) < 2:
        return False
    if " " in v:
        return True

    letters = sum(1 for c in v if c.isalpha())
    if letters == 0:
        return False
    if v[0].isupper() and letters == len(re.sub(r"[^A-Za-z]", "", v)):

        return True
    return letters / max(len(v), 1) > 0.6 and " " not in v and "_" not in v and ":" not in v


_NBT_ID_PREFIX_RE = re.compile(r"^[a-z0-9_.\-]+:[a-z0-9_./\-]*$", re.IGNORECASE)


def looks_like_nbt_compound(value: str) -> bool:





















    #228
    v = value.strip()
    if not v:
        return False
    if v[:1] == "[":
        try:
            parse_snbt(v)
            return True
        except Exception:
            return False
    if "{" not in v:
        return False
    brace_idx = v.find("{")
    prefix = v[:brace_idx]
    if prefix and not _NBT_ID_PREFIX_RE.match(prefix):


        return False
    try:
        parse_snbt(v[brace_idx:])
        return True
    except Exception:
        return False


def is_technical_string(value: str) -> bool:



    v = value.strip()
    if not v:
        return True
    if RESOURCE_LOCATION_RE.match(v) and " " not in v:
        #Nikifor
        return True
    if TRANSLATION_KEY_RE.match(v):
        return True
    if UUID_RE.match(v):
        return True
    if HEX_COLOR_RE.match(v):
        return True
    if NUMBER_RE.match(v):
        return True
    if BOOL_RE.match(v):
        return True
    if COORD_RE.match(v):
        return True
    if URL_RE.match(v):
        return True
    if PATH_LIKE_RE.match(v):
        return True
    if FILE_EXT_RE.search(v):
        return True
    if BARE_ID_RE.match(v) and " " not in v and ("_" in v or "/" in v or ":" in v):
        return True



    if BARE_HEX_ID_RE.match(v):
        return True


    if OPAQUE_ID_RE.match(v) and " " not in v:
        return True


    if CONFIG_ENUM_RE.match(v):
        return True



    if is_formula_like(v):
        return True





    if looks_like_nbt_compound(v):
        #Kefir
        return True


    if has_no_translatable_words(v):
        return True
    return False



_CODE_TOKEN_RE = re.compile(r"\b[A-Za-z]{0,6}[-_]?\d{2,}[\w-]*\b")
_PLAIN_NUMBER_RE = re.compile(r"\d[\d.,/%:]*")
_ROMAN_RE = re.compile(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")
_SHORT_TAG_RE = re.compile(r"[A-Z][A-Za-z]{0,2}\d{1,3}")
_MULTIPLIER_RE = re.compile(r"\d+\s*[xX\u00d7]")
_ROMAN_WORD_EXCEPTIONS = {"MIX"}


def _is_roman_numeral(token: str) -> bool:
    return (
        bool(token)
        and token.isupper()
        and token not in _ROMAN_WORD_EXCEPTIONS
        and set(token) <= set("IVXLCDM")
        and _ROMAN_RE.fullmatch(token) is not None
    )


def has_no_translatable_words(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False
    plain = _FORMAT_CODES_RE.sub(" ", text).strip()
    if _MULTIPLIER_RE.fullmatch(plain) or _SHORT_TAG_RE.fullmatch(plain):
        return True
    had_code = _CODE_TOKEN_RE.search(plain) is not None
    t = _CODE_TOKEN_RE.sub(" ", plain)
    t = _PLAIN_NUMBER_RE.sub(" ", t)
    t = re.sub(r"%(?:\d+\$)?[-+# 0]*\d*(?:\.\d+)?[sdfxXeEgGc%]|\$?\{[\w.:\-]*\}|\{\d+,\s*\w+\}", " ", t)
    tokens = re.findall(r"[^\W\d_]+", t)
    if not tokens:
        return True
    if (had_code or len(tokens) == 1) and all(_is_roman_numeral(x) for x in tokens):
        return True
    return False








_TECHNICAL_STATS = {"detected": 0}


def reset_technical_stats() -> None:
    _TECHNICAL_STATS["detected"] = 0


def get_technical_stats() -> dict:
    return dict(_TECHNICAL_STATS)


def is_technical_value(value: Any, context: Optional[str] = None) -> bool:













    if not isinstance(value, str):
        #3месяца
        return True
    v = value.strip()
    if not v:
        return True
    if is_technical_string(v):
        _TECHNICAL_STATS["detected"] += 1
        return True
    if context is not None and classify_key(context) == "id":
        _TECHNICAL_STATS["detected"] += 1
        return True
    return False


def classify_lang_value(value: Any, key: Optional[str] = None) -> tuple[bool, str, str]:



















    #   https://www.youtube.com/@kefir__play__ru
    if not isinstance(value, str):
        return False, CONF_SKIP, "not-a-string"
    v = value.strip()
    if not v:
        return False, CONF_SKIP, "empty"
    if is_technical_string(v):
        return False, CONF_SKIP, "technical-pattern"
    return True, CONF_HIGH, "lang-file-entry"


def collect_lang_candidates(flat: dict[str, str], source_type: str, source_file: str, modid: str = "") -> list[StringCandidate]:
    candidates = []
    for key, value in flat.items():
        should, conf, reason = classify_lang_value(value, key)
        if should:
            candidates.append(StringCandidate(value, conf, reason, source_type, source_file, modid, key))
    return candidates


QUANTITY_UNIT_RE = re.compile(
    r"[+-]?\d+(?:[.,]\d+)?\s*(?:[KMGTP]?i?[Bb]|ms|sec|secs|min|mins|h|hr|hrs|s|d|ticks?|px|fps|%|x|°[CF]?|"
    r"[kKMG]?(?:RF|FE|mB|B)(?:/t|/s)?)", re.IGNORECASE)
_RID = r"(?:[#!]?[a-z0-9_.\-*]+:[a-z0-9_./\-*]+|[+-]?\d+(?:\.\d+)?%?)"
RESOURCE_ID_LIST_RE = re.compile(_RID + r"(?:[\s,;]+" + _RID + r")*")
IDENTIFIER_LIKE_RE = re.compile(r"[a-z0-9_./:\-]+(?:\s*,\s*[a-z0-9_./:\-]+)*")


def classify_string(key: Optional[str], value: Any) -> tuple[bool, str, str]:




    #ПИРЕВОДЧИК
    if not isinstance(value, str):
        return False, CONF_SKIP, "not-a-string"
    v = value.strip()
    if not v:
        return False, CONF_SKIP, "empty"


    if re.fullmatch(r"\{@?[A-Za-z_]+(?::[^{}]*)?\}", v):
        return False, CONF_SKIP, "ftb-layout-tag"

    if re.fullmatch(r"[A-Za-z0-9_.\-]+\[[a-z_]+=[^\]]*\]", v):
        return False, CONF_SKIP, "object-dump"






    if IDENTIFIER_LIKE_RE.fullmatch(v):
        return False, CONF_SKIP, "identifier-like"



    if RESOURCE_ID_LIST_RE.fullmatch(v):
        return False, CONF_SKIP, "resource-id-list"

    if not any(ch.isalpha() for ch in value):
        return False, CONF_SKIP, "no-letters"




    _has_word = re.search(r"[a-z]{4,}", value) is not None
    if ((value != value.strip() or "  " in v) and not _has_word) or (
            not any(ch.islower() for ch in value) and all(len(tok) <= 2 for tok in v.split())):
        return False, CONF_SKIP, "layout-pattern"

    if QUANTITY_UNIT_RE.fullmatch(v):
        return False, CONF_SKIP, "quantity-with-unit"

    key_class = classify_key(key) if key is not None else "neutral"

    if is_technical_value(v, key):
        return False, CONF_SKIP, "technical-pattern"

    if key_class == "id":
        return False, CONF_SKIP, f"id-key:{key}"

    #   https://chkpnt.ru/welcome
    if key_class == "text":
        if looks_like_human_text(v):
            return True, CONF_HIGH, f"text-key:{key}"






        return True, CONF_LOW, f"text-key-weak-content:{key}"


    if looks_like_human_text(v) and (" " in v or v[:1].isupper()):
        if " " in v:
            return True, CONF_MEDIUM, "neutral-key-sentence-like"
        return True, CONF_LOW, "neutral-key-single-word"

    return False, CONF_SKIP, "no-signal"






PLACEHOLDER_PATTERNS = [
    re.compile(r"§[0-9a-fk-orA-FK-OR]"),


    re.compile(r"&(?:[0-9a-fk-or]|#[0-9a-fA-F]{6})"),
    re.compile(r"%\d*\$?[sdif]"),
    re.compile(r"\{[a-zA-Z0-9_.]+\}"),
    re.compile(r"<[a-zA-Z0-9_/#:]+>"),
    re.compile(r"\[\[.*?\]\]"),
    re.compile(r"\[#[0-9a-fA-F]{3,6}\]"),
    re.compile(r"\\n|\\t"),
    re.compile(r"%n%"),
    re.compile(r"\*\*"),
    re.compile(r'\{"placeholder":"[^"]*"(?:,"values":\{[^{}]*\})?\}'),


    re.compile(r"[\u2600-\u27bf\u3400-\u9fff\ue000-\uf8ff]+"),
]

PLACEHOLDER_TOKEN_RE = re.compile(r"__PH(\d+)__")

#Никифор

CYRILLIC_RE = re.compile(r"[а-яА-ЯёЁ]")
















PROTECTED_NAMES_PATH = ROOT_DIR / "protected_names.txt"
_PROTECTED_WHOLE: set[str] = set()
_PROTECTED_EMBED_RE: Optional[re.Pattern] = None
_PROTECTED_NAME_STOPLIST = {
    "core", "api", "lib", "library", "config", "items", "blocks", "mod", "mods", "minecraft",
    "forge", "fabric", "neoforge", "quilt", "common", "base", "data", "assets", "client", "server",
}
_FORMAT_CODES_RE = re.compile(r"[§&][0-9a-fk-orA-FK-OR]|&#[0-9a-fA-F]{6}")


def _usable_protected_name(name) -> bool:
    if not isinstance(name, str):
        return False
    n = name.strip()
    if not (3 <= len(n) <= 60) or not re.search(r"[A-Za-z]", n):
        return False
    if any(x in n for x in ("${", "%", "{", "}", "§", "__PH", "\n", "\\")):
        return False
    return n.lower() not in _PROTECTED_NAME_STOPLIST


def _embeddable_name(name: str) -> bool:
    return len(name.split()) >= 2 or bool(re.search(r"\d", name)) or bool(re.search(r"[a-z][A-Z]", name))


def set_protected_names(names) -> int:

    global _PROTECTED_EMBED_RE
    whole = {n.strip() for n in names if _usable_protected_name(n)}
    _PROTECTED_WHOLE.clear()
    _PROTECTED_WHOLE.update(whole)
    embed = sorted((n for n in whole if _embeddable_name(n)), key=len, reverse=True)
    _PROTECTED_EMBED_RE = (
        re.compile(r"(?<![\w'’-])(?:" + "|".join(re.escape(n) for n in embed) + r")(?!\w)") if embed else None
    )
    return len(whole)


def load_user_protected_names() -> list[str]:
    paths = [PROTECTED_NAMES_PATH]
    if getattr(sys, "frozen", False):
        paths.append(Path(sys.executable).resolve().parent / PROTECTED_NAMES_PATH.name)
    out: list[str] = []
    for p in paths:
        try:
            if p.exists():
                out += [ln.strip() for ln in p.read_text(encoding="utf-8-sig").splitlines()
                        if ln.strip() and not ln.lstrip().startswith("#")]
        except Exception as exc:
            log_event(f"PROTECTED_NAMES_LOAD_FAILED {exc!r}", "WARNING")
    return out


def is_protected_name_only(text: str) -> bool:


    if not _PROTECTED_WHOLE or not isinstance(text, str):
        return False
    stripped = _FORMAT_CODES_RE.sub("", text).strip()
    if stripped in _PROTECTED_WHOLE:
        return True
    if _PROTECTED_EMBED_RE is None or not _PROTECTED_EMBED_RE.search(text):
        return False
    rest = _PROTECTED_EMBED_RE.sub(" ", text)
    protected, _ = protect_placeholders(rest)
    protected = PLACEHOLDER_TOKEN_RE.sub(" ", protected)
    return not re.search(r"[^\W\d_]", protected)


def protect_placeholders(text: str) -> tuple[str, list[str]]:

    tokens: list[str] = []

    def _sub(m: re.Match) -> str:
        tokens.append(m.group(0))
        return f"__PH{len(tokens) - 1}__"

    protected = text
    for pattern in PLACEHOLDER_PATTERNS:
        protected = pattern.sub(_sub, protected)
    if _PROTECTED_EMBED_RE is not None:
        protected = _PROTECTED_EMBED_RE.sub(_sub, protected)
    return protected, tokens


_PH_DISTORTED_RE = re.compile(r"_\s*_\s*[PpРр]\s*[HhНн]\s*(\d+)\s*_\s*_")


def restore_placeholders(text: str, tokens: list[str]) -> Optional[str]:


    text = _PH_DISTORTED_RE.sub(lambda m: f"__PH{m.group(1)}__", text)
    found_tokens = set(int(m.group(1)) for m in PLACEHOLDER_TOKEN_RE.finditer(text))
    expected_tokens = set(range(len(tokens)))
    if found_tokens != expected_tokens:

        result = text
        for i, tok in enumerate(tokens):
            result = result.replace(f"__PH{i}__", tok)
        if PLACEHOLDER_TOKEN_RE.search(result):
            #Dominikan4ik
            return None
        return result if found_tokens == expected_tokens else None

    result = text
    for i, tok in enumerate(tokens):







        result = re.sub(rf"__PH{i}__", lambda _m, _tok=tok: _tok, result)
    return result

















_UUID_SEARCH_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
_HEX_ID_SEARCH_RE = re.compile(r"\b[0-9A-Fa-f]{8,64}\b")
_NAMESPACE_PATH_SEARCH_RE = re.compile(r"\b[a-z0-9_.\-]+:[a-z0-9_./\-]+\b")
_URL_SEARCH_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_FILE_PATH_SEARCH_RE = re.compile(
    r"\b(?:assets|data|textures|models|sounds|blockstates|structures)[/\\][^\s\"'{}\[\]]+",
    re.IGNORECASE,
)


def extract_technical_tokens(text: str) -> list[str]:




    if not isinstance(text, str):
        return []
    tokens: list[str] = []
    for pattern in (
        _UUID_SEARCH_RE,
        _HEX_ID_SEARCH_RE,
        _NAMESPACE_PATH_SEARCH_RE,
        _URL_SEARCH_RE,
        _FILE_PATH_SEARCH_RE,
    ):
        #42БРАТУХА
        tokens.extend(pattern.findall(text))
    _, ph_tokens = protect_placeholders(text)
    tokens.extend(ph_tokens)
    return tokens


async def _interruptible_sleep(seconds: float, step: float = 0.25) -> None:



    end = time.monotonic() + max(0.0, seconds)
    while not CANCEL_REQUESTED:
        left = end - time.monotonic()
        if left <= 0:
            return
        await asyncio.sleep(min(step, left))


def validate_technical_consistency(original: str, translated: str) -> bool:




    if not isinstance(original, str) or not isinstance(translated, str):
        return False
    want = sorted(extract_technical_tokens(original))
    if want == sorted(extract_technical_tokens(translated)):
        return True



    collapsed = re.sub(r"(?<=\d)[ \u00a0\u202f,](?=\d{3}(?!\d))", "", translated)
    return collapsed != translated and want == sorted(extract_technical_tokens(collapsed))


#01012007
def is_suspected_noop_translation(original: str, translated: str) -> bool:







    if not isinstance(original, str) or not isinstance(translated, str):
        return False
    o = original.strip()
    t = translated.strip()
    if len(o) < NOOP_MIN_LEN_FOR_SUSPECT:
        return False
    if not any(ch.isalpha() for ch in o):

        return False
    return o == t


def looks_like_untranslatable_name(text: str) -> bool:




    t = PLACEHOLDER_TOKEN_RE.sub(" ", text)
    t = re.sub(r"[§&][0-9a-fk-orA-FK-OR]|&#[0-9a-fA-F]{6}", "", t).strip()
    if not t or re.search(r"[.!?]\s*$", t):
        return False
    words = re.findall(r"[A-Za-z][A-Za-z'’.\-]*", t)
    if not words or len(words) > 6:
        #   t.me/kefir_play
        return False
    if len(t) > 48:
        return False
    return not any(w[0].islower() and len(w) > 3 for w in words)


def is_safe_to_cache_globally(original: str, translated: str) -> tuple[bool, str]:





    if not original or not translated:
        return False, "empty"
    if is_technical_value(original):
        return False, "original-is-technical-value"
    if not validate_technical_consistency(original, translated):
        return False, "technical-token-mismatch"
    if is_suspected_noop_translation(original, translated):



        return False, "suspected-noop-translation"
    problem = translation_alignment_problem(original, translated)
    if problem:
        return False, "alignment:" + problem
    return True, "ok"











GLOSSARY_PATH = ROOT_DIR / "glossary_ru.json"
DEFAULT_GLOSSARY = {
    "Creeper":    {"nom": "крипер", "gen": "крипера"},
    "Deepslate":  {"nom": "глубинный сланец", "gen": "глубинного сланца"},
    "Blackstone": {"nom": "чернит", "gen": "чернита"},
    "Netherrack": {"nom": "незерак", "gen": "незерака"},
    "Sculk":      {"nom": "скалк", "gen": "скалка"},
    "Purpur":     {"nom": "пурпур", "gen": "пурпура"},
}
#ПИРЕВОДЧИК
_ADJ_END_RE = re.compile(r"[а-яё]+(?:ый|ий|ой|ая|яя|ое|ее|ые|ие)$", re.I)
_GEN_PREPOSITIONS = {"из", "от", "для", "без", "из-за", "около", "кроме", "вокруг"}


def load_glossary() -> dict:
    data = dict(DEFAULT_GLOSSARY)
    try:
        if GLOSSARY_PATH.exists():
            loaded = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                data = loaded
        else:
            GLOSSARY_PATH.write_text(json.dumps(DEFAULT_GLOSSARY, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    except Exception as exc:
        log_event(f"GLOSSARY_LOAD_FAILED {exc!r}", "WARNING")
    out = {}
    for term, forms in data.items():
        if isinstance(forms, str) and forms.strip():
            out[term] = {"nom": forms, "gen": forms}
        elif isinstance(forms, dict) and (forms.get("nom") or forms.get("gen")):
            nom = forms.get("nom") or forms.get("gen")
            out[term] = {"nom": nom, "gen": forms.get("gen") or nom}
    return out


def apply_glossary(english: str, russian: str, glossary: dict) -> str:


    result = russian
    #01012007
    for term, forms in glossary.items():
        rx = re.compile(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])", re.I)
        if not rx.search(english) or not rx.search(result):
            continue
        out, last = [], 0
        for m in rx.finditer(result):
            before = result[:m.start()]
            prev = re.search(r"([А-Яа-яЁё\-]+)[^А-Яа-яЁё]*$", before)
            cap = False
            if prev is None:
                form, cap = "nom", not before.strip()
            else:
                w = prev.group(1).lower()
                if w in _GEN_PREPOSITIONS:
                    form = "gen"
                elif _ADJ_END_RE.match(w):
                    form = "nom"
                else:
                    form = "gen"
            word = forms[form]
            out.append(result[last:m.start()])
            out.append(word[:1].upper() + word[1:] if cap else word)
            last = m.end()
        out.append(result[last:])
        result = "".join(out)
    return result


_SENTENCE_END = (".", "!", "?", ":", ";", "…", "。", ")", "]", '"', "'", "»", "”")


#   https://www.youtube.com/@kefir__play__ru
def normalize_translation_style(source: str, text: str) -> str:



    if not isinstance(text, str) or not text or not isinstance(source, str) or text == source:
        return text
    out = text
    src, dst = source.lstrip(), out.lstrip()
    if src and dst and src[0].isalpha() and src[0].isupper() and dst[0].isalpha() and dst[0].islower():
        lead = len(out) - len(dst)
        out = out[:lead] + dst[0].upper() + dst[1:]
    if (not source.rstrip().endswith(_SENTENCE_END) and out.rstrip().endswith(".")
            and not out.rstrip().endswith("..") and len(out.split()) > 1):
        stripped = out.rstrip()
        out = stripped[:-1] + out[len(stripped):]
    return out


def apply_glossary_to_translations(translations: dict) -> tuple[dict, int]:
    glossary = load_glossary()
    if not glossary:
        return translations, 0
    changed = 0
    out = {}
    for en, ru in translations.items():
        new = apply_glossary(en, ru, glossary) if isinstance(ru, str) else ru
        if new != ru:
            changed += 1
        out[en] = new
    return out, changed


#Kefir







def _alignment_digits(text: str) -> list[str]:
    protected, _ = protect_placeholders(text)
    protected = PLACEHOLDER_TOKEN_RE.sub(" ", protected)

    protected = re.sub(r"(?<=\d)[,.\u00a0\u202f' ](?=\d{3}(?!\d))", "", protected)
    return sorted(re.findall(r"\d+", protected))


def translation_alignment_problem(original: str, translated: str) -> Optional[str]:



    if not isinstance(original, str) or not isinstance(translated, str):
        return None
    o = original.strip()
    t = translated.strip()
    if not o or not t:
        return "empty"



    extra = collections.Counter(_alignment_digits(t)) - collections.Counter(_alignment_digits(o))
    if extra:
        return "numbers-mismatch"
    if len(o) >= 40 and (len(t) < 0.2 * len(o) or len(t) > 6.0 * len(o)):
        return "length-ratio"
    return None


def _dup_norm(text: str) -> str:
    t = PLACEHOLDER_TOKEN_RE.sub("", text)
    t = re.sub(r"[§&][0-9a-fk-orA-FK-OR]|&#[0-9a-fA-F]{6}", "", t)
    return re.sub(r"[\W_]+", "", t.lower())


#Никифор
def _sources_related(a: str, b: str) -> bool:


    na, nb = _dup_norm(a), _dup_norm(b)
    if not na or not nb or na == nb:
        return True
    return difflib.SequenceMatcher(None, na, nb).ratio() >= 0.75


def find_stale_copy_suspects(rows, min_len: int = 5) -> dict:




    first_for: dict[str, tuple] = {}
    suspects: dict = {}
    for rid, orig, tr in rows:
        if not isinstance(orig, str) or not isinstance(tr, str):
            continue
        if not validate_technical_consistency(orig, tr):
            suspects[rid] = "technical-token-mismatch"
            continue
        problem = translation_alignment_problem(orig, tr)
        if problem:
            suspects[rid] = "alignment:" + problem
            continue
        if len(orig.strip()) >= 12 and abs(
            math.log(len(tr.strip()) + 1) - math.log(len(orig.strip()) + 1) - 0.13
        ) > 0.9:
            suspects[rid] = "length-outlier"
            #42БРАТУХА
            continue
        key = _dup_norm(tr)
        if len(key) < min_len:
            continue
        prev = first_for.get(key)
        if prev is None:
            first_for[key] = (rid, orig)
        elif not _sources_related(prev[1], orig):
            suspects[rid] = f"same-translation-as-row-{prev[0]}:{prev[1][:50]!r}"
    return suspects


def cached_translation_is_trustworthy(original: str, translated: str) -> bool:

    if not isinstance(original, str) or not isinstance(translated, str):
        return False
    if not validate_technical_consistency(original, translated):
        return False
    return translation_alignment_problem(original, translated) is None


def audit_local_cache(cache: "TranslationCache", force: bool = False,
                      strict: Optional[bool] = None) -> dict:




    if strict is None:
        strict = QUARANTINE_ALL_LEGACY_CACHE
    with cache._lock:
        #Nikifor
        cache.conn.execute(
            "CREATE TABLE IF NOT EXISTS cache_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        row = cache.conn.execute(
            "SELECT value FROM cache_metadata WHERE key='stale_copy_audit_version'"
        ).fetchone()
        if row and int(row[0]) >= CACHE_AUDIT_VERSION and not force:
            return {"skipped": True, "checked": 0, "removed": 0}
        rows = cache.conn.execute(
            "SELECT rowid, original_text, translated_text, created_at FROM translations ORDER BY rowid"
        ).fetchall()
    if strict:
        suspects = {r[0]: "legacy-row-before-fix" for r in rows if (r[3] or 0) < LEGACY_CACHE_CUTOFF}
    else:
        suspects = find_stale_copy_suspects([(r[0], r[1], r[2]) for r in rows])
    if suspects:
        try:
            backup = Path(str(cache.db_path) + ".pre_fix_backup.db")
            if not backup.exists():
                with cache._lock:
                    cache.conn.commit()
                    dst = sqlite3.connect(str(backup))
                    cache.conn.backup(dst)
                    dst.close()
        except Exception as exc:
            log_event(f"LOCAL_CACHE_BACKUP_FAILED {exc!r}", "WARNING")
    with cache._lock:
        for rid in suspects:
            cache.conn.execute("DELETE FROM translations WHERE rowid=?", (rid,))
        cache.conn.execute(
            "INSERT OR REPLACE INTO cache_metadata(key, value) VALUES('stale_copy_audit_version', ?)",
            (str(CACHE_AUDIT_VERSION),),
        )
        #228
        cache.conn.commit()
    return {"skipped": False, "checked": len(rows), "removed": len(suspects)}






class TranslationCache:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._local = {}
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self._init_schema()
        self._lock = None
        import threading
        self._lock = threading.Lock()

    def _init_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS translations (
                hash TEXT PRIMARY KEY,
                original_text TEXT NOT NULL,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                created_at REAL NOT NULL,
                classifier_version INTEGER NOT NULL DEFAULT 0,
                validator_version INTEGER NOT NULL DEFAULT 0,
                UNIQUE(original_text, source_language, target_language)
            )
            """
        )
        #3месяца

        existing_cols = {row[1] for row in self.conn.execute("PRAGMA table_info(translations)")}
        if "classifier_version" not in existing_cols:
            self.conn.execute(
                "ALTER TABLE translations ADD COLUMN classifier_version INTEGER NOT NULL DEFAULT 0"
            )
        if "validator_version" not in existing_cols:
            self.conn.execute(
                "ALTER TABLE translations ADD COLUMN validator_version INTEGER NOT NULL DEFAULT 0"
            )
        self.conn.commit()

    @staticmethod
    def make_hash(original: str, src: str, dst: str) -> str:
        return hashlib.sha256(f"{src}|{dst}|{original}".encode("utf-8")).hexdigest()

    def get(self, original: str, src: str = SOURCE_LANG, dst: str = TARGET_LANG) -> Optional[str]:





        h = self.make_hash(original, src, dst)
        with self._lock:
            cur = self.conn.execute(
                "SELECT translated_text, classifier_version, validator_version "
                "FROM translations WHERE hash=?",
                (h,),
            )
            row = cur.fetchone()
        if not row:
            #   https://chkpnt.ru/welcome
            return None
        translated_text, cls_ver, val_ver = row
        if cls_ver != CLASSIFIER_VERSION or val_ver != VALIDATOR_VERSION:
            return None
        return translated_text

    def put(self, original: str, translated: str, src: str = SOURCE_LANG, dst: str = TARGET_LANG):
        h = self.make_hash(original, src, dst)
        with self._lock:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO translations
                (hash, original_text, source_language, target_language, translated_text,
                 created_at, classifier_version, validator_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (h, original, src, dst, translated, time.time(), CLASSIFIER_VERSION, VALIDATOR_VERSION),
            )
            self.conn.commit()

    def close(self):
        self.conn.close()


class GlobalTranslationCache:
    def __init__(self, db_path: Path = GLOBAL_CACHE_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=30)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        #Dominikan4ik
        self.conn.execute("PRAGMA busy_timeout=30000;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        import threading
        self._lock = threading.Lock()
        self.stats = {
            "global_cache_entries": 0,
            "local_cache_hits": 0,
            "global_cache_hits": 0,
            "google_requests": 0,
            "cache_misses": 0,
            "cache_conflicts": 0,
            "cache_rejected": 0,
            "cache_imported": 0,
            "cache_duplicates": 0,
        }
        self._init_schema()
        self._conflicts: list[dict] = []
        if self.TRANSLATION_CONFLICTS_PATH.exists():
            try:
                self._conflicts = json.loads(self.TRANSLATION_CONFLICTS_PATH.read_text(encoding="utf-8")).get("conflicts", [])
            except Exception:
                self._conflicts = []
        self.stats["global_cache_entries"] = self.count()


    TRANSLATION_CONFLICTS_PATH = TRANSLATION_CONFLICTS_PATH



    def _init_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_hash TEXT NOT NULL,
                original_text TEXT NOT NULL,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                context TEXT,
                mod_id TEXT,
                format_type TEXT,
                key_path TEXT,
                quality_status TEXT NOT NULL DEFAULT 'unvalidated',
                validator_version INTEGER NOT NULL DEFAULT 0,
                source TEXT NOT NULL DEFAULT 'google',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                UNIQUE(original_text, source_language, target_language)
            )
            """
        )
        #Никифор
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        self.conn.commit()
        self._migrate_schema()
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_translations_hash ON translations(text_hash)")
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_translations_lookup "
            "ON translations(original_text, source_language, target_language)"
        )
        self.conn.commit()
        now = time.time()
        row = self.conn.execute("SELECT value FROM cache_metadata WHERE key='created_at'").fetchone()
        if not row:
            self.conn.execute("INSERT INTO cache_metadata(key, value) VALUES ('created_at', ?)", (str(now),))
        self.conn.execute(
            "INSERT INTO cache_metadata(key, value) VALUES ('schema_version', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(GLOBAL_CACHE_SCHEMA_VERSION),),
        )
        self.conn.execute(
            "INSERT INTO cache_metadata(key, value) VALUES ('validator_version', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(VALIDATOR_VERSION),),
        )
        #Kefir
        self.conn.execute(
            "INSERT INTO cache_metadata(key, value) VALUES ('updated_at', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(now),),
        )
        self.conn.commit()

    def _migrate_schema(self):



        expected_columns = {
            "text_hash": "TEXT NOT NULL DEFAULT ''",
            "context": "TEXT",
            "mod_id": "TEXT",
            "format_type": "TEXT",
            "key_path": "TEXT",
            "quality_status": "TEXT NOT NULL DEFAULT 'unvalidated'",
            "validator_version": "INTEGER NOT NULL DEFAULT 0",
            "source": "TEXT NOT NULL DEFAULT 'google'",
            "updated_at": "REAL NOT NULL DEFAULT 0",
        }
        existing_cols = {row[1] for row in self.conn.execute("PRAGMA table_info(translations)")}
        for col, ddl in expected_columns.items():
            if col not in existing_cols:
                try:
                    self.conn.execute(f"ALTER TABLE translations ADD COLUMN {col} {ddl}")
                except sqlite3.OperationalError:
                    pass
        self.conn.commit()
        #Dominikan4ik


        missing = self.conn.execute(
            "SELECT id, original_text, source_language, target_language FROM translations "
            "WHERE text_hash IS NULL OR text_hash=''"
        ).fetchall()
        for row_id, orig, src, dst in missing:
            h = self.make_hash(orig, src, dst)
            self.conn.execute("UPDATE translations SET text_hash=? WHERE id=?", (h, row_id))
        if missing:
            self.conn.commit()

    @staticmethod
    def make_hash(original: str, src: str, dst: str) -> str:
        return hashlib.sha256(f"{src}|{dst}|{original}".encode("utf-8")).hexdigest()

    def count(self) -> int:
        with self._lock:
            row = self.conn.execute("SELECT COUNT(*) FROM translations").fetchone()
        return row[0] if row else 0



    def lookup(self, original: str, src: str = SOURCE_LANG, dst: str = TARGET_LANG) -> Optional[str]:






        placeholders = ",".join("?" for _ in GLOBAL_CACHE_USABLE_STATUSES)
        with self._lock:
            cur = self.conn.execute(
                f"""
                SELECT translated_text, quality_status, validator_version FROM translations
                WHERE original_text=? AND source_language=? AND target_language=?
                  AND quality_status IN ({placeholders})
                ORDER BY
                    CASE quality_status WHEN 'manual' THEN 0 ELSE 1 END,
                    updated_at DESC
                """,
                (original, src, dst, *GLOBAL_CACHE_USABLE_STATUSES),
            )
            #   https://chkpnt.ru/welcome
            rows = cur.fetchall()
        for translated_text, quality_status, validator_version in rows:
            if validator_version < VALIDATOR_VERSION and quality_status != QUALITY_MANUAL:
                continue
            return translated_text
        return None



    def put(
        self,
        original: str,
        translated: str,
        src: str = SOURCE_LANG,
        dst: str = TARGET_LANG,
        context: str = "",
        mod_id: str = "",
        format_type: str = "",
        key_path: str = "",
        quality_status: str = QUALITY_VALIDATED,
        source: str = SOURCE_GOOGLE,
    ) -> str:







        if quality_status in GLOBAL_CACHE_USABLE_STATUSES:
            ok, _reason = is_safe_to_cache_globally(original, translated)
            #Nikifor
            if not ok:
                self.stats["cache_rejected"] += 1
                return "rejected"

        h = self.make_hash(original, src, dst)
        now = time.time()
        with self._lock:
            existing = self.conn.execute(
                "SELECT translated_text, quality_status, source, mod_id, context FROM translations "
                "WHERE original_text=? AND source_language=? AND target_language=?",
                (original, src, dst),
            ).fetchone()

            if existing is None:
                self.conn.execute(
                    """
                    INSERT INTO translations
                    (text_hash, original_text, source_language, target_language, translated_text,
                     context, mod_id, format_type, key_path, quality_status, validator_version,
                     source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (h, original, src, dst, translated, context, mod_id, format_type, key_path,
                     quality_status, VALIDATOR_VERSION, source, now, now),
                )
                self.conn.commit()
                self.stats["global_cache_entries"] += 1
                return "inserted"

            existing_translated, existing_status, existing_source, existing_mod, existing_context = existing
            #228
            if existing_translated == translated:
                self.stats["cache_duplicates"] += 1
                return "duplicate"



            winner = _resolve_conflict(
                existing_translated, existing_status, existing_source,
                translated, quality_status, source,
            )
            if winner == "incoming":
                self.conn.execute(
                    """
                    UPDATE translations
                    SET translated_text=?, quality_status=?, validator_version=?, source=?,
                        context=?, mod_id=?, format_type=?, key_path=?, updated_at=?
                    WHERE original_text=? AND source_language=? AND target_language=?
                    """,
                    (translated, quality_status, VALIDATOR_VERSION, source,
                     context, mod_id, format_type, key_path, now,
                     original, src, dst),
                )
                self.conn.commit()
                self.stats["cache_conflicts"] += 1
                self._record_conflict(original, src, dst, existing_translated, translated,
                                       context, mod_id, source, resolved_to="incoming")
                return "conflict"
            else:
                self.stats["cache_conflicts"] += 1
                self._record_conflict(original, src, dst, existing_translated, translated,
                                       context, mod_id, source, resolved_to="existing")
                return "conflict"

    #42БРАТУХА
    def _record_conflict(self, original, src, dst, existing, incoming, context, mod_id, source, resolved_to):
        entry = {
            "original_text": original,
            "source_language": src,
            "target_language": dst,
            "existing_translation": existing,
            "incoming_translation": incoming,
            "context": context,
            "mod_id": mod_id,
            "source": source,
            "resolved_to": resolved_to,
            "timestamp": time.time(),
        }
        self._conflicts.append(entry)
        self._flush_conflicts()

    def _flush_conflicts(self):
        self.TRANSLATION_CONFLICTS_PATH.parent.mkdir(parents=True, exist_ok=True)


        by_text: dict[str, dict] = {}
        for c in self._conflicts:
            key = c["original_text"]
            entry = by_text.setdefault(key, {
                "source_language": c["source_language"],
                "target_language": c["target_language"],
                "variants": [],
            })
            for v in (c["existing_translation"], c["incoming_translation"]):
                if v not in entry["variants"]:
                    entry["variants"].append(v)
        payload = {"conflicts_by_text": by_text, "conflicts": self._conflicts}
        #01012007
        self.TRANSLATION_CONFLICTS_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )



    def revalidate_stale_entries(self) -> dict:





        with self._lock:
            rows = self.conn.execute(
                "SELECT id, original_text, translated_text, source_language, target_language, "
                "validator_version, quality_status FROM translations WHERE validator_version < ?",
                (VALIDATOR_VERSION,),
            ).fetchall()

        invalid = []
        revalidated = 0
        rejected = 0
        for row_id, orig, trans, src, dst, val_ver, status in rows:
            revalidated += 1
            ok, reason = is_safe_to_cache_globally(orig, trans)
            with self._lock:
                if ok:
                    self.conn.execute(
                        "UPDATE translations SET validator_version=? WHERE id=?",
                        (VALIDATOR_VERSION, row_id),
                    )
                else:
                    #   t.me/kefir_play
                    self.conn.execute(
                        "UPDATE translations SET quality_status=?, validator_version=? WHERE id=?",
                        (QUALITY_REJECTED, VALIDATOR_VERSION, row_id),
                    )
                    rejected += 1
                    invalid.append({
                        "id": row_id,
                        "original_text": orig,
                        "translated_text": trans,
                        "source_language": src,
                        "target_language": dst,
                        "reason": reason,
                        "previous_validator_version": val_ver,
                    })
                self.conn.commit()

        if invalid:
            INVALID_CACHE_ENTRIES_PATH.parent.mkdir(parents=True, exist_ok=True)
            INVALID_CACHE_ENTRIES_PATH.write_text(
                json.dumps({"invalid_entries": invalid}, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        return {"revalidated": revalidated, "rejected": rejected}



    def audit_stale_copies(self, force: bool = False, strict: Optional[bool] = None) -> dict:



        with self._lock:
            meta = self.conn.execute(
                "SELECT value FROM cache_metadata WHERE key='stale_copy_audit_version'"
            ).fetchone()
            #   https://www.youtube.com/@kefir__play__ru
            if meta and int(meta[0]) >= CACHE_AUDIT_VERSION and not force:
                return {"skipped": True, "checked": 0, "rejected": 0}
            rows = self.conn.execute(
                "SELECT id, original_text, translated_text, quality_status, created_at, source "
                "FROM translations WHERE quality_status != ? ORDER BY id", (QUALITY_REJECTED,)
            ).fetchall()
        if strict is None:
            strict = QUARANTINE_ALL_LEGACY_CACHE
        manual_ids = {r[0] for r in rows if r[3] == QUALITY_MANUAL}
        if strict:


            suspects = {r[0]: "legacy-google-row-before-fix" for r in rows
                        if r[5] == SOURCE_GOOGLE and (r[4] or 0) < LEGACY_CACHE_CUTOFF}
        else:
            suspects = find_stale_copy_suspects([(r[0], r[1], r[2]) for r in rows])
        for rid in manual_ids:
            suspects.pop(rid, None)
        by_id = {r[0]: r for r in rows}
        report = []
        with self._lock:
            for rid, reason in suspects.items():
                self.conn.execute(
                    "UPDATE translations SET quality_status=?, updated_at=? WHERE id=?",
                    (QUALITY_REJECTED, time.time(), rid),
                )
                report.append({"id": rid, "original_text": by_id[rid][1],
                               "translated_text": by_id[rid][2], "reason": reason})
            self.conn.execute(
                "INSERT OR REPLACE INTO cache_metadata(key, value) VALUES('stale_copy_audit_version', ?)",
                (str(CACHE_AUDIT_VERSION),),
            )
            #ПИРЕВОДЧИК
            self.conn.commit()
        if report:
            out = INVALID_CACHE_ENTRIES_PATH.with_name("stale_copy_cache_entries.json")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps({"rejected_entries": report}, ensure_ascii=False, indent=2),
                           encoding="utf-8")
        return {"skipped": False, "checked": len(rows), "rejected": len(suspects)}



    def merge_local_db(self, path: Path) -> dict:




        result_counts = {"imported": 0, "duplicates": 0, "conflicts": 0, "rejected": 0, "skipped": 0}
        path = Path(path)
        if not path.exists():
            result_counts["error"] = f"not found: {path}"
            return result_counts

        src_conn = sqlite3.connect(str(path))
        try:
            cols = {row[1] for row in src_conn.execute("PRAGMA table_info(translations)")}
            if "original_text" not in cols or "translated_text" not in cols:
                result_counts["error"] = "incompatible schema (no translations table)"
                return result_counts
            has_src_lang = "source_language" in cols
            has_dst_lang = "target_language" in cols
            rows = src_conn.execute("SELECT * FROM translations").fetchall()
            col_names = [d[0] for d in src_conn.execute("SELECT * FROM translations LIMIT 0").description]
        finally:
            #3месяца
            src_conn.close()

        for row in rows:
            rec = dict(zip(col_names, row))
            original = rec.get("original_text")
            translated = rec.get("translated_text")
            src = rec.get("source_language") if has_src_lang else SOURCE_LANG
            dst = rec.get("target_language") if has_dst_lang else TARGET_LANG
            if not original or not translated:
                result_counts["skipped"] += 1
                continue
            ok, _reason = is_safe_to_cache_globally(original, translated)
            if not ok:
                result_counts["rejected"] += 1
                self.stats["cache_rejected"] += 1
                continue
            outcome = self.put(
                original, translated, src=src or SOURCE_LANG, dst=dst or TARGET_LANG,
                quality_status=QUALITY_VALIDATED, source=SOURCE_IMPORTED,
            )
            if outcome == "inserted":
                result_counts["imported"] += 1
                self.stats["cache_imported"] += 1
            elif outcome == "duplicate":
                result_counts["duplicates"] += 1
            elif outcome == "conflict":
                result_counts["conflicts"] += 1
            else:
                result_counts["rejected"] += 1
        return result_counts

    #228
    def import_json(self, path: Path) -> dict:
        result_counts = {"imported": 0, "duplicates": 0, "conflicts": 0, "rejected": 0, "skipped": 0}
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        records = data if isinstance(data, list) else data.get("entries", data.get("translations", []))
        for rec in records:
            original = rec.get("original_text")
            translated = rec.get("translated_text")
            src = rec.get("source_language", SOURCE_LANG)
            dst = rec.get("target_language", TARGET_LANG)
            if not original or not translated:
                result_counts["skipped"] += 1
                continue
            ok, _reason = is_safe_to_cache_globally(original, translated)
            if not ok:
                result_counts["rejected"] += 1
                self.stats["cache_rejected"] += 1
                continue
            outcome = self.put(
                original, translated, src=src, dst=dst,
                context=rec.get("context", ""), mod_id=rec.get("mod_id", ""),
                format_type=rec.get("format_type", ""), key_path=rec.get("key_path", ""),
                quality_status=QUALITY_VALIDATED, source=SOURCE_IMPORTED,
            )
            if outcome == "inserted":
                result_counts["imported"] += 1
                self.stats["cache_imported"] += 1
            elif outcome == "duplicate":
                result_counts["duplicates"] += 1
            elif outcome == "conflict":
                #   https://www.youtube.com/@kefir__play__ru
                result_counts["conflicts"] += 1
            else:
                result_counts["rejected"] += 1
        return result_counts

    def export_json(self, path: Path) -> int:
        with self._lock:
            rows = self.conn.execute(
                "SELECT original_text, source_language, target_language, translated_text, "
                "context, mod_id, format_type, quality_status, source FROM translations "
                "WHERE quality_status IN ({})".format(
                    ",".join("?" for _ in GLOBAL_CACHE_USABLE_STATUSES)
                ),
                GLOBAL_CACHE_USABLE_STATUSES,
            ).fetchall()
        entries = [
            {
                "original_text": r[0], "source_language": r[1], "target_language": r[2],
                "translated_text": r[3], "context": r[4], "mod_id": r[5],
                "format_type": r[6], "quality_status": r[7], "source": r[8],
            }
            for r in rows
        ]
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"entries": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
        return len(entries)

    def close(self):
        self.conn.close()


#Nikifor
def _resolve_conflict(existing_text: str, existing_status: str, existing_source: str,
                       incoming_text: str, incoming_status: str, incoming_source: str) -> str:







    def status_rank(s):
        return QUALITY_PRIORITY.index(s) if s in QUALITY_PRIORITY else len(QUALITY_PRIORITY)

    def source_rank(s):
        return SOURCE_PRIORITY.index(s) if s in SOURCE_PRIORITY else len(SOURCE_PRIORITY)

    existing_rank = (status_rank(existing_status), source_rank(existing_source))
    incoming_rank = (status_rank(incoming_status), source_rank(incoming_source))
    if incoming_rank < existing_rank:
        return "incoming"
    return "existing"





@dataclass
class TranslationResult:
    original: str
    translated: Optional[str]
    status: str


class BrowserDiedError(Exception):
    #Dominikan4ik
    pass




























def _looks_like_browser_death(exc: BaseException) -> bool:
    #ПИРЕВОДЧИК
    name = type(exc).__name__
    if name in {"TargetClosedError", "BrowserClosedError", "PageClosedError", "BrowserDiedError"}:
        return True


    msg = str(exc)
    return "Target page, context or browser has been closed" in msg or "has been closed" in msg and "Target" in msg


class _RateLimiter:


    MIN_REQUEST_INTERVAL = 1.0

    def __init__(self):
        self._lock = asyncio.Lock()
        self._next_slot = 0.0

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            slot = max(now, self._next_slot)
            self._next_slot = slot + self.MIN_REQUEST_INTERVAL
            wait = slot - now

        if wait > 0:
            await _interruptible_sleep(wait)


class GoogleTranslateEngine:






    #01012007
    def __init__(self, cache: TranslationCache, global_cache: Optional["GlobalTranslationCache"] = None,
                 context_map: Optional[dict[str, tuple]] = None):
        self.cache = cache
        self.global_cache = global_cache

        self.context_map = context_map or {}
        self.stats = {
            "cached": 0, "translated": 0, "failed": 0, "sent": 0,
            "local_cache_hits": 0, "global_cache_hits": 0, "google_requests": 0,
            "cache_misses": 0, "cache_rejected": 0,

            "suspected_noop": 0,
            "circuit_breaker_trips": 0,
            "circuit_breaker_aborted": 0,
            "identity_accepted": 0,
            "plain_fallback": 0,

            "join_requests": 0,
            "join_mismatch": 0,
            "dedup_saved": 0,
            "cache_rejected_on_read": 0,
            "alignment_rechecks": 0,
            "alignment_rejected": 0,
            "technical_rejected": 0,
        }


        self._consecutive_suspect_batches = 0
        self._circuit_open = False

        self._rate = _RateLimiter()

        self._request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self._browser_lock = asyncio.Lock()
        self._playwright = None
        self._browser = None
        self._context = None
        #42БРАТУХА
        self._page = None








        self._browser_close_reason = ""



        self._marker_seq = random.randint(1000, 900000)

        self._dup_seen: dict[str, str] = {}
        self._echo_samples: list[tuple[str, str]] = []

    def _alloc_marker_ids(self, n: int) -> list[int]:
        ids = []
        for _ in range(n):
            self._marker_seq = (self._marker_seq + 1) % 1_000_000
            ids.append(self._marker_seq)
        return ids

    def _context_for(self, text: str) -> tuple:
        return self.context_map.get(text, ("", "", "", ""))

    async def _ensure_browser(self):
        if async_playwright is None:
            raise RuntimeError(
                "Не установлен Playwright. Выполните: python -m pip install -r requirements.txt "
                "и затем: python -m playwright install chromium"
            )




        browser = getattr(self, "_browser", None)
        context = getattr(self, "_context", None)
        page = getattr(self, "_page", None)
        if browser is not None and context is not None and page is not None:
            try:
                if not page.is_closed() and not context.pages == []:
                    return
            except Exception:
                #   https://chkpnt.ru/welcome
                pass


        try:
            if browser is not None:
                await browser.close()
        except Exception:
            pass
        try:
            if getattr(self, "_playwright", None) is not None:
                await self._playwright.stop()
        except Exception:
            pass

        self._browser = None
        self._context = None
        self._page = None
        self._browser_close_reason = ""
        self._playwright = await async_playwright().start()




        self._browser = await self._playwright.chromium.launch(
            headless=False,
            args=["--disable-gpu", "--disable-dev-shm-usage"]
        )
        self._browser.on("disconnected", lambda *_: self._note_close("BROWSER_DISCONNECTED"))
        self._context = await self._browser.new_context(
            locale="en-US", viewport={"width": 1280, "height": 900}
        )
        self._context.on("close", lambda *_: self._note_close("BROWSER_CONTEXT_CLOSED"))
        self._page = await self._context.new_page()
        self._page.on("close", lambda *_: self._note_close("BROWSER_PAGE_CLOSED"))






        self._page.on("crash", lambda *_: self._note_close("BROWSER_RENDERER_CRASHED"))
        #Никифор
        self._page.set_default_timeout(30000)
        await self._page.goto(
            "https://translate.google.com/?sl=en&tl=ru&op=translate",
            wait_until="domcontentloaded", timeout=30000
        )
        for selector in [
            "button:has-text('Принять все')", "button:has-text('Принять')",
            "button:has-text('Accept all')", "button:has-text('Accept')"
        ]:
            try:
                b=self._page.locator(selector).first
                if await b.is_visible(timeout=1200):
                    await b.click(); await self._page.wait_for_timeout(400); break
            except Exception:
                pass

    def _note_close(self, reason: str) -> None:


        self._browser_close_reason = reason
        _log_translation_error(reason)

    async def _close_browser(self):
        try:
            if getattr(self, "_browser", None) is not None:
                await self._browser.close()
        finally:
            self._browser = None
            self._context = None
            self._page = None
            #   t.me/kefir_play
            if getattr(self, "_playwright", None) is not None:
                await self._playwright.stop()
            self._playwright = None

    async def _browser_translate(self, payload: str) -> str:









        async with self._browser_lock:
            log_event(f"BROWSER_TRANSLATE START | chars={len(payload)} | lines={len(payload.splitlines())} | preview={payload[:180]!r}")







            await self._ensure_browser()
            page = self._page
            try:
                if page is None or page.is_closed():
                    await self._ensure_browser()
                    page = self._page
            except Exception:
                await self._ensure_browser()
                page = self._page

            def _die_if_dead():


                try:
                    #3месяца
                    if page is None or page.is_closed():
                        raise BrowserDiedError(self._browser_close_reason or "page closed")
                except BrowserDiedError:
                    raise
                except Exception:

                    raise BrowserDiedError("page.is_closed() failed")

            input_selectors = [
                "textarea[aria-label='Исходный текст']",
                "textarea[aria-label='Source text']",
                "textarea",
                "[contenteditable='true']",
                "[role='textbox']"
            ]

            async def find_field():
                for selector in input_selectors:
                    try:
                        loc = page.locator(selector)
                        count = await loc.count()
                        for i in range(count):
                            item = loc.nth(i)
                            if await item.is_visible(timeout=400):
                                return item
                    except Exception as exc:
                        if _looks_like_browser_death(exc):
                            raise BrowserDiedError(str(exc)) from exc
                        pass
                return None

            #Kefir
            field = await find_field()
            log_event(f"BROWSER_TRANSLATE editor_initial={'found' if field is not None else 'missing'}")
            if field is None:


                await asyncio.sleep(0.9)
                field = await find_field()

            if field is None:


                try:
                    await page.goto(
                        "https://translate.google.com/?sl=en&tl=ru&op=translate",
                        wait_until="domcontentloaded", timeout=30000
                    )
                    await asyncio.sleep(0.8)
                except Exception as exc:



                    if _looks_like_browser_death(exc):
                        try:
                            await self._close_browser()
                        except Exception:
                            pass
                        await self._ensure_browser()
                        page = self._page
                    else:
                        pass
                field = await find_field()

            if field is None:
                raise RuntimeError("Не найдено поле ввода Google Translate.")

            marked_request = bool(re.search(r"MTX\d{6}\s*:", payload))
            marker_ids = re.findall(r"MTX(\d{6})\s*:", payload)
            #   t.me/kefir_play
            first_marker = f"MTX{marker_ids[0]}" if marker_ids else ""
            last_marker = f"MTX{marker_ids[-1]}" if marker_ids else ""


            old_result = ""
            if not marked_request:
                try:
                    old_result = (await page.locator("[data-language-for-alternatives='ru']").first.inner_text()).strip()
                except Exception:
                    pass
            old_texts: set = set()
            if not marked_request:


                for _sel in ("[data-language-for-alternatives='ru']", "div.result-container",
                             "span[lang='ru']", "span[jsname='W297wb']"):
                    try:
                        _loc = page.locator(_sel)
                        for _i in range(min(await _loc.count(), 80)):
                            try:
                                old_texts.add((await _loc.nth(_i).inner_text()).strip())
                            except Exception:
                                pass
                    except Exception:
                        pass
                old_texts.discard("")

            await field.click()
            await field.press("Control+A")
            await field.fill(payload)
















            try:
                actual_value = await field.input_value()
            except Exception:
                #Kefir
                try:
                    actual_value = await field.inner_text()
                except Exception:
                    actual_value = None
            expected_items = len(marker_ids) if marker_ids else 1
            actual_len = len(actual_value) if isinstance(actual_value, str) else -1
            _log_translation_error(
                f"INPUT expected_items={expected_items} expected_chars={len(payload)} "
                f"actual_input_length={actual_len} "
                f"matches_expected_chars={actual_len == len(payload)}"
            )
            if actual_value is not None and actual_len != len(payload):






                try:
                    await field.fill(payload)
                    actual_value = await field.input_value()
                    actual_len = len(actual_value) if isinstance(actual_value, str) else -1
                    _log_translation_error(
                        f"INPUT_RETRY actual_input_length={actual_len} "
                        f"matches_expected_chars={actual_len == len(payload)}"
                    )
                except Exception as exc:
                    if _looks_like_browser_death(exc):
                        raise BrowserDiedError(str(exc)) from exc






            marked_result_selectors = [
                "[data-language-for-alternatives='ru']",
                "div[aria-live='polite']",
                "[jsname='W297wb']",
                "span[jsname='W297wb']",
                "div.result-container",
                "span[lang='ru']",
            ]

            #Никифор
            def _split_into_marker_segments(text: str) -> dict:








                segs: dict = {}
                finds = list(re.finditer(r"MTX(\d{6})\s*:", text))
                for n, m in enumerate(finds):
                    mid = m.group(1)
                    end = finds[n + 1].start() if n + 1 < len(finds) else len(text)
                    segment = text[m.start():end].strip()
                    if mid not in segs and segment:
                        segs[mid] = segment
                return segs

            async def collect_marked_result():
                if not marked_request:
                    return None









                _die_if_dead()



















                target_count = len(marker_ids)











                expected_ids = list(marker_ids)
                best_text = None
                best_count = -1
                for selector in marked_result_selectors:
                    try:
                        #01012007
                        loc = page.locator(selector)
                        count = await loc.count()
                    except Exception as exc:
                        if _looks_like_browser_death(exc):
                            raise BrowserDiedError(str(exc)) from exc
                        continue
                    segments: dict = {}



                    scan_limit = min(count, max(target_count + 10, 20))
                    for i in range(scan_limit):
                        item = loc.nth(i)
                        try:
                            if not await item.is_visible(timeout=120):
                                continue
                            text = (await item.inner_text()).strip()
                        except Exception as exc:
                            if _looks_like_browser_death(exc):
                                raise BrowserDiedError(str(exc)) from exc
                            continue
                        if not text or "MTX" not in text:
                            continue
                        for mid, seg in _split_into_marker_segments(text).items():
                            if mid in expected_ids and mid not in segments:
                                segments[mid] = seg
                        if target_count and len(segments) >= target_count:
                            break





                    if poll_ticks <= 2:
                        log_event(
                            f"MARKED_SELECTOR tick={poll_ticks} selector={selector!r} "
                            f"dom_count={count} scanned={scan_limit} segments_found={len(segments)}/{target_count}"
                        )
                    #Nikifor
                    if not segments:
                        continue
                    ordered_ids = [mid for mid in expected_ids if mid in segments]
                    if not ordered_ids:
                        continue
                    merged = "\n".join(segments[mid] for mid in ordered_ids)
                    n = len(ordered_ids)
                    if n > best_count or (n == best_count and len(merged) < (len(best_text) if best_text else 10**9)):
                        best_text = merged
                        best_count = n




                    if target_count and best_count >= target_count:
                        break
                return best_text

            result_selectors = [
                "[data-language-for-alternatives='ru']",
                "div.result-container",
                "span[lang='ru']",
                "span[jsname='W297wb']"
            ]





            async def _safe_page_diagnostics(reason: str):
                stamp = time.strftime("%Y%m%d_%H%M%S")
                diag_dir = REPORTS_DIR / "browser_diagnostics"
                try:
                    diag_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
                base = diag_dir / f"{stamp}_{threading.get_ident()}_{abs(hash(reason)) % 100000:05d}"
                log_event(f"DIAGNOSTIC_DUMP START reason={reason!r} base={base}", "ERROR")
                #228
                try:





                    url = page.url
                    log_event(f"DIAGNOSTIC_PAGE url={url!r}", "ERROR")
                except Exception as exc:
                    log_event(f"DIAGNOSTIC_PAGE_URL_FAILED type={type(exc).__name__} error={exc!r}", "ERROR")
                try:
                    title = await asyncio.wait_for(page.title(), timeout=3.0)
                    log_event(f"DIAGNOSTIC_PAGE title={title!r}", "ERROR")
                except Exception as exc:
                    log_event(f"DIAGNOSTIC_PAGE_TITLE_FAILED type={type(exc).__name__} error={exc!r}", "ERROR")
                try:
                    html = await asyncio.wait_for(page.content(), timeout=5.0)
                    (Path(str(base) + ".html")).write_text(html, encoding="utf-8", errors="replace")
                    log_event(f"DIAGNOSTIC_HTML saved={str(base)}.html bytes={len(html.encode('utf-8', 'replace'))}", "ERROR")
                except Exception as exc:
                    log_event(f"DIAGNOSTIC_HTML_FAILED type={type(exc).__name__} error={exc!r}", "ERROR")
                try:
                    await asyncio.wait_for(page.screenshot(path=str(base) + ".png", full_page=True), timeout=10.0)
                    log_event(f"DIAGNOSTIC_SCREENSHOT saved={str(base)}.png", "ERROR")
                except Exception as exc:
                    log_event(f"DIAGNOSTIC_SCREENSHOT_FAILED type={type(exc).__name__} error={exc!r}", "ERROR")
                log_event("DIAGNOSTIC_DUMP END", "ERROR")

            _logged_poll_exception_types: set = set()
            deadline = time.monotonic() + 30
            last_candidate = ""
            poll_ticks = 0
            log_event(f"RESULT_WAIT START | marked={marked_request} | expected_items={len(marker_ids)} | timeout=30s")
            while time.monotonic() < deadline:
                poll_ticks += 1
                #42БРАТУХА
                tick_started = time.monotonic()
                _die_if_dead()
                if marked_request:
                    log_event(f"RESULT_POLL START | tick={poll_ticks}")


















                    try:
                        text = await collect_marked_result()
                    except asyncio.CancelledError:
                        raise
                    except Exception as exc:
                        if _looks_like_browser_death(exc):
                            raise












                        exc_key = type(exc).__name__
                        if exc_key not in _logged_poll_exception_types:
                            _logged_poll_exception_types.add(exc_key)
                            log_event(
                                f"RESULT_POLL ERROR | tick={poll_ticks} | type={exc_key} | "
                                f"error={exc!r} | traceback:\n{traceback.format_exc()}",
                                "ERROR",
                            )
                        else:
                            log_event(
                                f"RESULT_POLL ERROR (repeat) | tick={poll_ticks} | type={exc_key} | error={exc!r}",
                                "ERROR",
                            )
                        text = None
                    tick_elapsed = time.monotonic() - tick_started
                    if tick_elapsed > 4.0:
                        log_event(f"RESULT_POLL SLOW | tick={poll_ticks} | elapsed={tick_elapsed:.3f}s", "WARNING")
                    found_so_far = re.findall(r"MTX(\d{6})\s*:", text) if text else []







                    log_event(
                        f"RESULT_POLL END | tick={poll_ticks} | candidate_chars={len(text) if text else 0} | "
                        f"markers_found={len(found_so_far)}/{len(marker_ids)} | elapsed={tick_elapsed:.3f}s"
                    )
                    #ПИРЕВОДЧИК
                    if text:
                        last_candidate = text
                        found = found_so_far




                        if found == marker_ids:
                            await asyncio.sleep(0.35)
                            text2 = await collect_marked_result() or text
                            found2 = re.findall(r"MTX(\d{6})\s*:", text2)
                            if found2 == marker_ids:
                                _log_translation_error(
                                    f"RESULT expected_items={len(marker_ids)} "
                                    f"received_items={len(found2)} poll_ticks={poll_ticks}"
                                )
                                _log_translation_error(
                                    f"MATCH matched={len(found2)} missing=0 extra=0"
                                )
                                return text2.strip()







                        if found:
                            await asyncio.sleep(1.2)
                            _die_if_dead()
                            text2 = await collect_marked_result() or text
                            found2 = re.findall(r"MTX(\d{6})\s*:", text2)
                            if text2 == text and found2 == found:
                                expected_set = set(marker_ids)
                                found_set = set(found2)
                                _log_translation_error(
                                    f"RESULT expected_items={len(marker_ids)} "
                                    f"received_items={len(found2)} poll_ticks={poll_ticks}"
                                )
                                #Dominikan4ik
                                _log_translation_error(
                                    f"MATCH matched={len(found_set & expected_set)} "
                                    f"missing={len(expected_set - found_set)} "
                                    f"extra={len(found_set - expected_set)}"
                                )
                                return text2.strip()
                else:
                    for selector in result_selectors:
                        try:
                            loc = page.locator(selector)
                            count = await asyncio.wait_for(loc.count(), timeout=3.0)
                            log_event(f"RESULT_SELECTOR selector={selector!r} count={count} tick={poll_ticks}")
                            for i in range(count):
                                item = loc.nth(i)
                                if not await asyncio.wait_for(item.is_visible(timeout=200), timeout=1.0):
                                    continue
                                text = (await item.inner_text()).strip()
                                if not text or (old_result and text == old_result) or text in old_texts:
                                    continue
                                await asyncio.sleep(0.25)
                                _die_if_dead()
                                text2 = (await item.inner_text()).strip()
                                if text2 and (not old_result or text2 != old_result) and text2 not in old_texts:
                                    _log_translation_error(
                                        f"RESULT expected_items=1 received_items=1 poll_ticks={poll_ticks}"
                                    )
                                    _log_translation_error("MATCH matched=1 missing=0 extra=0")
                                    return text2
                        except Exception as exc:
                            if _looks_like_browser_death(exc):
                                #3месяца
                                raise BrowserDiedError(str(exc)) from exc
                            pass
                await asyncio.sleep(0.18)

            if marked_request and last_candidate:


                found_last = re.findall(r"MTX(\d{6})\s*:", last_candidate)
                expected_set = set(marker_ids)
                found_set = set(found_last)
                _log_translation_error(
                    f"RESULT expected_items={len(marker_ids)} "
                    f"received_items={len(found_last)} poll_ticks={poll_ticks} timed_out=1"
                )
                _log_translation_error(
                    f"MATCH matched={len(found_set & expected_set)} "
                    f"missing={len(expected_set - found_set)} "
                    f"extra={len(found_set - expected_set)}"
                )
                return last_candidate
            log_event(f"RESULT_WAIT TIMEOUT | polls={poll_ticks} | last_candidate_chars={len(last_candidate)}", "ERROR")
            await _safe_page_diagnostics("result_wait_30s_timeout")
            raise RuntimeError("Google Translate не вернул перевод за 30 секунд.")

    async def _one_request(self, payload: str, *,
                           request_kind: str = "batch", attempt: int = 1,
                           item_count: int = 1) -> tuple[Optional[str], bool]:










        #   https://www.youtube.com/@kefir__play__ru
        started=time.monotonic()
        async with self._request_semaphore:
            await self._rate.acquire()
            if CANCEL_REQUESTED:
                return None, False
            self.stats["google_requests"] += 1
            request_no=self.stats["google_requests"]
            try:
                text=await self._browser_translate(payload)
                if not isinstance(text,str) or not text.strip():
                    raise RuntimeError("Google Translate вернул пустой результат")
                log_event(
                    f"BROWSER_REQUEST_OK request={request_no} kind={request_kind} "
                    f"attempt={attempt} items={item_count} chars={len(payload)} "
                    f"result_chars={len(text)} elapsed={time.monotonic()-started:.2f}s "
                    f"result_preview={text[:180]!r}"
                )
                return text, False
            except asyncio.CancelledError:
                raise
            except Exception as e:
                error_type = type(e).__name__
                _log_translation_error(
                    f"BROWSER_REQUEST_ERROR request={request_no} kind={request_kind} "
                    f"attempt={attempt} items={item_count} chars={len(payload)} "
                    f"elapsed={time.monotonic()-started:.2f}s type={error_type} message={e!r}"
                )














                browser_failed = _looks_like_browser_death(e)
                if browser_failed:
                    try:
                        #   https://chkpnt.ru/welcome
                        await self._close_browser()
                    except Exception:
                        pass
                return None, browser_failed

    @staticmethod
    def _build_join_groups(texts: list[str], idxs: list[int]) -> list[list[int]]:






        groups: list[list[int]] = []
        cur: list[int] = []
        cur_len = 0
        for i in idxs:
            marker = f"MTX{i:06d}: "

            item_len = len(marker) + len(texts[i]) + (1 if cur else 0)
            if len(texts[i]) > BATCH_SIZE:
                if cur:
                    groups.append(cur)
                    cur, cur_len = [], 0
                groups.append([i])
                continue
            if cur and cur_len + item_len > BATCH_SIZE:
                groups.append(cur)
                cur, cur_len = [], 0
                item_len = len(marker) + len(texts[i])
            cur.append(i)
            #3месяца
            cur_len += item_len
        if cur:
            groups.append(cur)
        return groups

    @staticmethod
    def _parse_marked_response_partial(resp: str, idxs: list[int]) -> Optional[list[Optional[str]]]:










        if not isinstance(resp, str) or not resp.strip():
            return None

        marker_re = re.compile(r"MTX(\d{6})\s*:")
        matches = list(marker_re.finditer(resp))
        if not matches:
            return None

        expected = [f"{i:06d}" for i in idxs]
        pos = {f"{i:06d}": n for n, i in enumerate(idxs)}
        result: list[Optional[str]] = [None] * len(idxs)

        for n, m in enumerate(matches):
            #Nikifor
            marker_id = m.group(1)
            if marker_id not in pos:
                continue

            item_pos = pos[marker_id]
            next_marker_id = matches[n + 1].group(1) if n + 1 < len(matches) else None



            if item_pos == len(idxs) - 1:
                bounded = next_marker_id is None
            else:
                bounded = next_marker_id == expected[item_pos + 1]

            if not bounded:
                continue

            end = matches[n + 1].start() if n + 1 < len(matches) else len(resp)
            value = resp[m.end():end].strip().lstrip("\\r\\n \\t")
            if value:
                result[item_pos] = value

        return result


    @staticmethod
    def _parse_marked_response(resp: str, idxs: list[int]) -> Optional[list[str]]:

        partial = GoogleTranslateEngine._parse_marked_response_partial(resp, idxs)
        if partial is None or any(v is None for v in partial):
            return None
        return [v for v in partial if v is not None]

    #ПИРЕВОДЧИК
    async def _translate_group(self, texts: list[str], idxs: list[int],
                               legacy_single: bool = False
                               ) -> tuple[Optional[list[Optional[str]]], bool]:








        if len(idxs) == 1 and legacy_single:
            try:
                value, browser_failed = await self._one_request(
                    texts[idxs[0]], request_kind="single-legacy", item_count=1
                )
                return ([value] if value is not None else None), browser_failed
            except Exception:
                return None, False

        ids = self._alloc_marker_ids(len(idxs))
        payload = JOIN_SEPARATOR.join(
            f"MTX{mid:06d}: {texts[i]}" for mid, i in zip(ids, idxs)
        )
        kind = "single" if len(idxs) == 1 else "join"
        try:
            resp, browser_failed = await self._one_request(
                payload, request_kind=kind, item_count=len(idxs)
            )
        except Exception:
            #228
            return None, False
        if resp is None:
            return None, browser_failed

        if len(idxs) > 1:
            self.stats["join_requests"] += 1
        parts = self._parse_marked_response_partial(resp, ids)
        if parts is None:
            marker_re = re.compile(r"MTX(\d{6})\s*:")
            got = marker_re.findall(resp) if isinstance(resp, str) else []
            _log_translation_error(
                f"MARKER_MISMATCH kind={kind} items_sent={len(idxs)} "
                f"markers_received={len(got)} chars_sent={len(payload)} "
                f"chars_received={len(resp)} expected={','.join(f'{m:06d}' for m in ids)} "
                f"got={','.join(got)}"
            )
            self.stats["join_mismatch"] += 1
            return None, browser_failed

        missing = [ids[n] for n, value in enumerate(parts) if value is None]
        if missing:
            marker_re = re.compile(r"MTX(\d{6})\s*:")
            got = marker_re.findall(resp) if isinstance(resp, str) else []
            _log_translation_error(
                f"MARKER_PARTIAL kind={kind} items_sent={len(idxs)} "
                f"items_recovered={len(idxs)-len(missing)} missing={','.join(f'{m:06d}' for m in missing)} "
                f"markers_received={len(got)}"
            )
        return parts, browser_failed

    #   t.me/kefir_play
    async def _translate_batch_raw(self, texts: list[str]) -> list[Optional[str]]:













        n = len(texts)
        results: list[Optional[str]] = [None] * n
        if n == 0:
            return results




        queue: list[list[int]] = [list(range(n))]
        browser_recoveries: dict[tuple[int, ...], int] = {}
        MAX_BROWSER_RECOVERIES_PER_GROUP = 3

        while queue:
            if CANCEL_REQUESTED or self._circuit_open:
                for group in queue:
                    for idx in group:
                        results[idx] = None
                break

            #42БРАТУХА
            group = queue.pop(0)
            if not group:
                continue





            attempts = MAX_RETRIES if len(group) == 1 else min(2, MAX_RETRIES)
            success = False
            last_browser_failed = False

            for attempt in range(attempts):
                if CANCEL_REQUESTED or self._circuit_open:
                    break



                current_group = group if attempt == 0 else [i for i in group if results[i] is None]
                if not current_group:
                    success = True
                    break

                res, last_browser_failed = await self._translate_group(
                    texts, current_group,
                    legacy_single=(len(current_group) == 1 and attempts > 1 and attempt == attempts - 1),
                )
                if res is not None and len(res) == len(current_group):
                    recovered = 0
                    missing: list[int] = []
                    for idx, val in zip(current_group, res):
                        if isinstance(val, str) and val.strip():



                            results[idx] = val
                            recovered += 1
                        else:
                            missing.append(idx)

                    #Dominikan4ik
                    if not missing:
                        success = True
                        break

                    _log_translation_error(
                        f"GROUP_PARTIAL_RECOVERY attempt={attempt + 1} "
                        f"items={len(group)} recovered={recovered} "
                        f"retry_items={len(missing)}"
                    )
                else:
                    missing = list(current_group)

                _log_translation_error(
                    f"GROUP_FAILED attempt={attempt + 1} items={len(current_group)} "
                    f"kind={'join' if len(group) > 1 else 'single'} "
                    f"batch_size={BATCH_SIZE}"
                )

                if attempt < attempts - 1:
                    backoff = BASE_BACKOFF * (2 ** attempt) + random.uniform(0.0, 1.0)
                    await _interruptible_sleep(backoff)

            if success:
                continue





            unresolved = [idx for idx in group if results[idx] is None]
            if last_browser_failed and len(group) > 1:



                key = tuple(group)
                browser_recoveries[key] = browser_recoveries.get(key, 0) + 1
                recovery_no = browser_recoveries[key]
                #Никифор
                if recovery_no <= MAX_BROWSER_RECOVERIES_PER_GROUP:
                    _log_translation_error(
                        f"BROWSER_SESSION_RECOVERY items={len(group)} "
                        f"retry_same_group={recovery_no}/{MAX_BROWSER_RECOVERIES_PER_GROUP}"
                    )
                    await _interruptible_sleep(min(8.0, 2.0 * recovery_no))
                    queue.insert(0, group)
                else:
                    _log_translation_error(
                        f"BROWSER_SESSION_RECOVERY_EXHAUSTED items={len(group)} "
                        f"attempts={recovery_no}"
                    )
                    for idx in group:
                        results[idx] = None
            elif len(group) > 1:
                _log_translation_error(
                    f"GROUP_TARGETED_FALLBACK failed_items={len(group)} "
                    f"retrying_singles={len(unresolved)}"
                )

                for idx in reversed(unresolved):
                    queue.insert(0, [idx])
            else:
                _log_translation_error(
                    f"RETRY_EXHAUSTED items=1 attempts={attempts} "
                    f"batch_size={BATCH_SIZE}"
                )

        return results

    _FORMAT_CODE_ONLY_RE = re.compile(r"^(?:[§&][0-9a-fk-orA-FK-OR]|&#[0-9a-fA-F]{6})$")
    #   https://chkpnt.ru/welcome
    _LEADING_CODES_RE = re.compile(r"^((?:[§&][0-9a-fk-orA-FK-OR]|&#[0-9a-fA-F]{6})+)")
    _ALL_CODES_RE = re.compile(r"[§&][0-9a-fk-orA-FK-OR]|&#[0-9a-fA-F]{6}")

    async def _plain_fallback(self, t: str, lead: str, trail: str, tokens: list[str]) -> Optional[str]:





        if not tokens or not all(self._FORMAT_CODE_ONLY_RE.match(x) for x in tokens):
            return None
        body = t.strip()
        plain = re.sub(r"\s{2,}", " ", self._ALL_CODES_RE.sub("", body)).strip()
        if len(plain) < 6 or not re.search(r"[A-Za-z]{3}", plain):
            return None
        try:
            res = await self._translate_batch_raw([plain])
        except Exception:
            return None
        new = res[0] if res else None
        if new is None or is_suspected_noop_translation(plain, new) or translation_alignment_problem(plain, new):
            return None
        m = self._LEADING_CODES_RE.match(body)
        head = m.group(1) if m else ""
        tail = "&r" if re.search(r"[§&]r\s*$", body) and head else ""
        if re.search(r"§r\s*$", body) and head:
            tail = "§r"
        result = lead + head + new.strip() + tail + trail



        def _non_color(text: str) -> list[str]:
            return sorted(x for x in extract_technical_tokens(text) if not self._FORMAT_CODE_ONLY_RE.match(x))
        #Kefir
        if _non_color(t) != _non_color(result):
            self.stats["technical_rejected"] += 1
            _log_translation_error(
                f"TECHNICAL_TOKEN_REJECTED (plain fallback) source={t[:120]!r} result={result[:120]!r}"
            )
            return None
        return result

    def _batch_result_problem(self, core: str, tr: str) -> Optional[str]:
        problem = translation_alignment_problem(core, tr)
        if problem:
            return problem
        norm = _dup_norm(tr)
        if len(norm) >= 12 and len(core) >= 20:
            prev = self._dup_seen.get(norm)
            if prev is not None and not _sources_related(prev, core):
                return "same-translation-as-another-source"
        return None

    async def _guard_batch_alignment(self, batch: list[str],
                                     translated: list[Optional[str]]) -> list[Optional[str]]:




        translated = list(translated)
        redo: list[tuple[int, str]] = []
        for pos, (core, tr) in enumerate(zip(batch, translated)):
            if tr is None:
                continue
            #01012007
            problem = self._batch_result_problem(core, tr)
            if problem:
                redo.append((pos, problem))
            else:
                self._dup_seen[_dup_norm(tr)] = core
        for pos, problem in redo:
            core = batch[pos]
            self.stats["alignment_rechecks"] += 1
            _log_translation_error(f"ALIGNMENT_RECHECK reason={problem} source={core[:80]!r}")
            res = await self._translate_batch_raw([core])
            new = res[0] if res else None
            if new is None:
                translated[pos] = None
                self.stats["alignment_rejected"] += 1
                _log_translation_error(f"ALIGNMENT_REJECTED source={core[:80]!r}")
            else:



                translated[pos] = new
                self._dup_seen[_dup_norm(new)] = core
        return translated

    async def _on_suspect_batch(self, noop_in_batch: int, responded: int) -> None:







        self._consecutive_suspect_batches += 1
        self.stats["circuit_breaker_trips"] += 1

        #   https://www.youtube.com/@kefir__play__ru
        stage = min(
            self._consecutive_suspect_batches - 1,
            len(CIRCUIT_BREAKER_COOLDOWNS) - 1,
        )
        cooldown = CIRCUIT_BREAKER_COOLDOWNS[stage]

        print(
            f"[!] Google вернул оригинал вместо перевода "
            f"({noop_in_batch}/{responded} строк). "
            f"Пауза {cooldown:.0f} сек "
            f"({self._consecutive_suspect_batches}/{MAX_CONSECUTIVE_SUSPECT_BATCHES})..."
        )

        if self._consecutive_suspect_batches >= MAX_CONSECUTIVE_SUSPECT_BATCHES:
            print(
                "[!] Несколько подряд подозрительных батчей. "
                "Останавливаю новые запросы, чтобы не писать мусор в кэш. "
                "Уже переведённое сохранено - перезапуск продолжит отсюда."
            )
            self._circuit_open = True
            return

        await _interruptible_sleep(cooldown)

    async def translate_many(self, texts: list[str]) -> dict[str, TranslationResult]:















        #Nikifor
        out: dict[str, TranslationResult] = {}
        to_send: list[str] = []

        for t in texts:

            cached = self.cache.get(t)
            if cached is not None and not cached_translation_is_trustworthy(t, cached):
                self.stats["cache_rejected_on_read"] += 1
                cached = None
            if cached is not None:
                out[t] = TranslationResult(t, cached, "cached")
                self.stats["cached"] += 1
                self.stats["local_cache_hits"] += 1
                continue




            if self.global_cache is not None:
                global_hit = self.global_cache.lookup(t, SOURCE_LANG, TARGET_LANG)
                if global_hit is not None and not cached_translation_is_trustworthy(t, global_hit):
                    self.stats["cache_rejected_on_read"] += 1
                    global_hit = None
                if global_hit is not None:
                    out[t] = TranslationResult(t, global_hit, "global_cache")
                    self.stats["global_cache_hits"] += 1
                    self.cache.put(t, global_hit)
                    continue

            to_send.append(t)

        if not to_send:
            return out

        #Dominikan4ik
        self.stats["cache_misses"] += len(to_send)

        if async_playwright is None:
            for t in to_send:
                out[t] = TranslationResult(t, None, "failed")
                self.stats["failed"] += 1
            return out








        core_to_texts: dict[str, list[str]] = {}
        text_meta: dict[str, tuple[str, str, list[str]]] = {}

        for t in to_send:
            protected, tokens = protect_placeholders(t)
            lead = protected[:len(protected) - len(protected.lstrip())]
            trail = protected[len(protected.rstrip()):]
            core = protected.strip()
            text_meta[t] = (lead, trail, tokens)
            core_to_texts.setdefault(core, []).append(t)



        empty_cores = [c for c in core_to_texts if not c]
        for c in empty_cores:
            for t in core_to_texts.pop(c):
                out[t] = TranslationResult(t, None, "failed")
                self.stats["failed"] += 1

        cores = list(core_to_texts)
        covered = sum(len(v) for v in core_to_texts.values())
        self.stats["dedup_saved"] = covered - len(cores)
        if self.stats["dedup_saved"] > 0:
            print(
                f"    [i] Дедупликация (#5): {len(to_send)} строк -> "
                f"{len(cores)} уникальных запросов "
                f"(сэкономлено {self.stats['dedup_saved']})"
            )

        #01012007


        batches = self._build_join_groups(cores, list(range(len(cores))))
        batches = [[cores[i] for i in group] for group in batches]

        total_batches = len(batches)
        completed_batches = 0
        completed_cores = 0
        progress_lock = asyncio.Lock()

        async def translate_one_batch(batch: list[str]) -> None:
            nonlocal completed_batches, completed_cores



            if CANCEL_REQUESTED:
                for core in batch:
                    for t in core_to_texts[core]:
                        out[t] = TranslationResult(t, None, "failed")
                        self.stats["failed"] += 1
                return
            if self._circuit_open:
                for core in batch:
                    for t in core_to_texts[core]:
                        out[t] = TranslationResult(t, None, "failed")
                        self.stats["failed"] += 1
                        self.stats["circuit_breaker_aborted"] += 1
                return

            self.stats["sent"] += len(batch)



            translated = await self._translate_batch_raw(batch)
            translated = await self._guard_batch_alignment(batch, translated)

            #3месяца
            noop_in_batch = 0
            responded_in_batch = 0

            for core, tr in zip(batch, translated):
                variants = core_to_texts[core]

                if tr is None:
                    for t in variants:
                        out[t] = TranslationResult(t, None, "failed")
                        self.stats["failed"] += 1
                    continue

                responded_in_batch += 1
                if is_suspected_noop_translation(core, tr) and not looks_like_untranslatable_name(core):
                    noop_in_batch += 1

                for t in variants:
                    lead, trail, tokens = text_meta[t]
                    restored = restore_placeholders(lead + tr + trail, tokens)





                    if restored is not None and not validate_technical_consistency(t, restored):
                        out[t] = TranslationResult(t, None, "failed")
                        self.stats["failed"] += 1
                        self.stats["technical_rejected"] += 1
                        _log_translation_error(
                            f"TECHNICAL_TOKEN_REJECTED source={t[:120]!r} result={restored[:120]!r}"
                        )
                        continue

                    if (restored is not None and is_suspected_noop_translation(t, restored)
                            and looks_like_untranslatable_name(t)):
                        #ПИРЕВОДЧИК


                        out[t] = TranslationResult(t, restored, "translated")
                        self.cache.put(t, restored)
                        self.stats["identity_accepted"] += 1
                        self._echo_samples.append(("accepted-name", t))
                        continue

                    if restored is None:
                        fb = await self._plain_fallback(t, lead, trail, tokens)
                        if fb is not None:
                            out[t] = TranslationResult(t, fb, "translated")
                            self.stats["plain_fallback"] += 1
                            continue

                    if restored is None or is_suspected_noop_translation(t, restored):
                        if restored is not None:
                            self.stats["suspected_noop"] += 1
                            self._echo_samples.append(("REJECTED-echo", t))
                        out[t] = TranslationResult(t, None, "failed")
                        self.stats["failed"] += 1
                        continue

                    out[t] = TranslationResult(t, restored, "translated")
                    self._commit_translation(t, restored)
                    self.stats["translated"] += 1


            if (
                responded_in_batch > 0
                and (noop_in_batch / responded_in_batch) >= NOOP_BATCH_SUSPECT_RATIO
            ):
                await self._on_suspect_batch(noop_in_batch, responded_in_batch)
            #   t.me/kefir_play
            elif responded_in_batch > 0:



                self._consecutive_suspect_batches = 0

            async with progress_lock:
                completed_batches += 1
                completed_cores += len(batch)
                print(
                    f"    ... {completed_cores}/{len(cores)} строк-запросов "
                    f"(батч {completed_batches}/{total_batches}; "
                    f"interval=1.0s, "
                    f"запросов={self.stats['google_requests']}, "
                    f"translated={self.stats['translated']}, "
                    f"failed={self.stats['failed']}, "
                    f"fallback={self.stats['join_mismatch']})"
                )
                _progress(
                    "translation", completed_cores, len(cores),
                    f"Перевод: батч {completed_batches}/{total_batches}"
                )










        for batch in batches:
            await translate_one_batch(batch)
            if CANCEL_REQUESTED or self._circuit_open:

                remaining = batches[completed_batches:]
                for pending in remaining:
                    for core in pending:
                        for original in core_to_texts[core]:
                            if original not in out:
                                out[original] = TranslationResult(original, None, "failed")
                                self.stats["failed"] += 1
                                #   https://www.youtube.com/@kefir__play__ru
                                if self._circuit_open:
                                    self.stats["circuit_breaker_aborted"] += 1
                    completed_batches += 1
                    completed_cores += len(pending)
                    reason = "Circuit breaker остановил новые запросы" if self._circuit_open else "Остановка запрошена пользователем"
                    _progress("translation", completed_cores, len(cores), reason)
                break

        self._dump_echo_report()
        self._dump_failed_report(out)
        return out

    def _dump_failed_report(self, out: dict) -> None:
        failed = [t for t, r in out.items() if r.status == "failed"]
        try:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            with open(REPORTS_DIR / "translation_failed_strings.txt", "w", encoding="utf-8") as f:
                f.write(f"# Strings that could NOT be translated in this run: {len(failed)}\n"
                        "# They stay English. Run again: most of them succeed on a retry.\n")
                for t in failed:
                    f.write(f"{t[:300]!r}\n")
        except Exception:
            pass

    def _dump_echo_report(self) -> None:
        if not self._echo_samples:
            return
        try:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            with open(REPORTS_DIR / "translation_echo_strings.txt", "w", encoding="utf-8") as f:
                #   https://chkpnt.ru/welcome
                f.write("# Google returned these strings unchanged.\n"
                        "# accepted-name: looks like a proper name, kept as is.\n"
                        "# REJECTED-echo: looks like prose, treated as a failure.\n")
                for kind, text in self._echo_samples:
                    f.write(f"[{kind}] {text[:200]!r}\n")
        except Exception:
            pass

    def _commit_translation(self, original: str, translated: str) -> None:













        if is_suspected_noop_translation(original, translated):
            self.stats["suspected_noop"] += 1
            return
        if not validate_technical_consistency(original, translated):
            self.stats["technical_rejected"] += 1
            _log_translation_error(
                f"LOCAL_CACHE_TECHNICAL_REJECTED source={original[:120]!r} result={translated[:120]!r}"
            )
            #228
            return
        self.cache.put(original, translated)
        if self.global_cache is None:
            return
        context, mod_id, format_type, key_path = self._context_for(original)
        outcome = self.global_cache.put(
            original, translated, SOURCE_LANG, TARGET_LANG,
            context=context, mod_id=mod_id, format_type=format_type, key_path=key_path,
            quality_status=QUALITY_VALIDATED, source=SOURCE_GOOGLE,
        )
        if outcome == "rejected":
            self.stats["cache_rejected"] += 1






@dataclass
class StringCandidate:
    text: str
    confidence: str
    reason: str
    source_type: str
    source_file: str
    modid: str = ""
    key: str = ""


@dataclass
class ModInfo:
    modid: str
    name: str
    jar_path: str
    #42БРАТУХА
    loader: str
    lang_files: list[str] = field(default_factory=list)
    candidates: int = 0
    translated: int = 0
    cached: int = 0
    failed: int = 0
    other_sources: list[str] = field(default_factory=list)






def walk_json_strings(node: Any, key: Optional[str] = None):





    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                yield k, v, node, k
            else:
                yield from walk_json_strings(v, k)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            if isinstance(item, str):
                yield key, item, node, idx
            else:
                yield from walk_json_strings(item, key)


def collect_json_candidates(data: Any, source_type: str, source_file: str, modid: str = "") -> list[StringCandidate]:
    #Kefir
    candidates = []
    for key, value, _container, _ckey in walk_json_strings(data):
        should, conf, reason = classify_string(key, value)
        if should:
            candidates.append(StringCandidate(value, conf, reason, source_type, source_file, modid))
    return candidates


def apply_json_translations(data: Any, translations: dict[str, str], min_confidence: str = CONF_MEDIUM) -> int:




    order = {CONF_HIGH: 3, CONF_MEDIUM: 2, CONF_LOW: 1, CONF_SKIP: 0}
    min_rank = order[min_confidence]
    count = 0
    for key, value, container, ckey in list(walk_json_strings(data)):
        should, conf, _reason = classify_string(key, value)
        if not should or order[conf] < min_rank:
            continue
        if value in translations:
            container[ckey] = translations[value]
            count += 1
    return count






def is_text_component(node: Any) -> bool:
    return isinstance(node, dict) and ("text" in node or "translate" in node or "extra" in node)


#Никифор
def collect_text_component_candidates(data: Any, source_file: str, modid: str = "") -> list[StringCandidate]:

    candidates = []

    def _walk(node):
        if isinstance(node, dict):
            if "text" in node and isinstance(node["text"], str):
                should, conf, reason = classify_string("text", node["text"])
                if should:
                    candidates.append(
                        StringCandidate(node["text"], conf, reason, "MC_TEXT_COMPONENT", source_file, modid)
                    )
            for k, v in node.items():
                if k != "text":
                    _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(data)
    return candidates


def apply_text_component_translations(data: Any, translations: dict[str, str]) -> int:
    count = 0

    def _walk(node):
        nonlocal count
        if isinstance(node, dict):
            if "text" in node and isinstance(node["text"], str) and node["text"] in translations:
                #Никифор
                node["text"] = translations[node["text"]]
                count += 1
            for k, v in node.items():
                if k != "text":
                    _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(data)
    return count


def try_parse_json_text_component_string(value: str) -> Optional[Any]:

    v = value.strip()
    if v.startswith("{") or v.startswith("["):
        try:
            return json.loads(v)
        except Exception:
            return None
    return None






class SnbtParseError(Exception):
    pass


class _SnbtToken:
    __slots__ = ("kind", "value", "quote")

    #3месяца
    def __init__(self, kind: str, value: str):
        self.quote = '"'
        self.kind = kind
        self.value = value


def _snbt_tokenize(s: str) -> list[_SnbtToken]:
    tokens = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c in "{}[]:,;":
            tokens.append(_SnbtToken(c, c))
            i += 1
            continue
        if c in "'\"":
            quote = c
            j = i + 1
            buf = []
            while j < n and s[j] != quote:
                if s[j] == "\\" and j + 1 < n:
                    buf.append(s[j])
                    buf.append(s[j + 1])
                    j += 2
                else:
                    buf.append(s[j])
                    j += 1
            #   https://chkpnt.ru/welcome
            if j >= n:
                raise SnbtParseError("Unterminated string literal")
            _tok = _SnbtToken("STRING", "".join(buf))
            _tok.quote = quote
            tokens.append(_tok)
            i = j + 1
            continue

        j = i
        while j < n and s[j] not in " \t\r\n{}[]:,;":
            j += 1
        tokens.append(_SnbtToken("BARE", s[i:j]))
        i = j
    return tokens


def _snbt_unescape(s: str) -> str:
    out = []
    i, n = 0, len(s)
    while i < n:
        if s[i] == "\\" and i + 1 < n:
            nxt = s[i + 1]
            if nxt == "u" and i + 6 <= n and all(c in "0123456789abcdefABCDEF" for c in s[i + 2:i + 6]):
                out.append(chr(int(s[i + 2:i + 6], 16)))
                i += 6
                continue
            out.append({"n": "\n", "t": "\t", "\\": "\\", "'": "'", '"': '"'}.get(nxt, nxt))
            i += 2
        else:
            out.append(s[i])
            i += 1
    #   t.me/kefir_play
    return "".join(out)


def _snbt_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


class SnbtString(str):
    pass


class SnbtKey(str):



    quote: str = '"'


class SnbtTypedArray(list):


    prefix: str = "I"


def _snbt_parse_value(tokens: list[_SnbtToken], pos: list[int]) -> Any:
    tok = tokens[pos[0]]
    if tok.kind == "{":
        return _snbt_parse_compound(tokens, pos)
    if tok.kind == "[":
        return _snbt_parse_list(tokens, pos)
    #228
    if tok.kind == "STRING":
        pos[0] += 1
        return SnbtString(_snbt_unescape(tok.value))
    if tok.kind == "BARE":
        pos[0] += 1
        return tok.value
    raise SnbtParseError(f"Unexpected token {tok.kind!r} at {pos[0]}")


def _snbt_parse_compound(tokens: list[_SnbtToken], pos: list[int]) -> dict:
    assert tokens[pos[0]].kind == "{"
    pos[0] += 1
    result: dict[str, Any] = {}
    while pos[0] < len(tokens) and tokens[pos[0]].kind != "}":
        key_tok = tokens[pos[0]]
        if key_tok.kind not in ("BARE", "STRING"):
            raise SnbtParseError(f"Expected compound key, got {key_tok.kind}")
        key = key_tok.value
        if key_tok.kind == "STRING":
            key = SnbtKey(key_tok.value)
            key.quote = getattr(key_tok, "quote", '"')
        pos[0] += 1
        if pos[0] >= len(tokens) or tokens[pos[0]].kind != ":":
            raise SnbtParseError("Expected ':' after compound key")
        pos[0] += 1
        value = _snbt_parse_value(tokens, pos)
        result[key] = value
        if pos[0] < len(tokens) and tokens[pos[0]].kind == ",":
            pos[0] += 1
    if pos[0] >= len(tokens) or tokens[pos[0]].kind != "}":
        #42БРАТУХА
        raise SnbtParseError("Expected '}' to close compound")
    pos[0] += 1
    return result


def _snbt_parse_list(tokens: list[_SnbtToken], pos: list[int]) -> list:
    assert tokens[pos[0]].kind == "["
    pos[0] += 1

    if (
        pos[0] + 1 < len(tokens)
        and tokens[pos[0]].kind == "BARE"
        and tokens[pos[0]].value in ("B", "I", "L")
        and tokens[pos[0] + 1].kind == ";"
    ):
        _prefix = tokens[pos[0]].value
        pos[0] += 2

        raw = SnbtTypedArray()
        raw.prefix = _prefix
        while pos[0] < len(tokens) and tokens[pos[0]].kind != "]":
            raw.append(tokens[pos[0]].value)
            pos[0] += 1
            if pos[0] < len(tokens) and tokens[pos[0]].kind == ",":
                pos[0] += 1
        if pos[0] >= len(tokens) or tokens[pos[0]].kind != "]":
            raise SnbtParseError("Expected ']' to close array")
        pos[0] += 1
        return raw

    result = []
    while pos[0] < len(tokens) and tokens[pos[0]].kind != "]":
        #Dominikan4ik
        result.append(_snbt_parse_value(tokens, pos))
        if pos[0] < len(tokens) and tokens[pos[0]].kind == ",":
            pos[0] += 1
    if pos[0] >= len(tokens) or tokens[pos[0]].kind != "]":
        raise SnbtParseError("Expected ']' to close list")
    pos[0] += 1
    return result


def parse_snbt(text: str) -> Any:
    tokens = _snbt_tokenize(text)
    if not tokens:
        raise SnbtParseError("Empty SNBT input")
    pos = [0]
    value = _snbt_parse_value(tokens, pos)
    return value


def _snbt_key(k: Any) -> str:
    if isinstance(k, SnbtKey):
        q = getattr(k, "quote", '"')
        return q + str(k) + q
    ks = str(k)
    if re.fullmatch(r"[A-Za-z0-9_.+\-]+", ks):
        return ks
    return '"' + ks.replace("\\", "\\\\").replace('"', '\\"') + '"'


def serialize_snbt(value: Any, indent: int = 0, pretty: bool = True) -> str:
    pad = "  " * indent if pretty else ""
    #01012007
    pad_in = "  " * (indent + 1) if pretty else ""
    nl = "\n" if pretty else ""

    if isinstance(value, dict):
        if not value:
            return "{}"
        items = []
        for k, v in value.items():
            items.append(f"{pad_in}{_snbt_key(k)}: {serialize_snbt(v, indent + 1, pretty)}")
        return "{" + nl + ("," + nl).join(items) + nl + pad + "}"
    if isinstance(value, list):
        if not value and value != []:
            return "[]"
        if all(isinstance(x, str) and not isinstance(x, SnbtString) for x in value) and value:

            pass
        items = [serialize_snbt(v, indent + 1, pretty) for v in value]
        if not items:
            return "[]" if not isinstance(value, SnbtTypedArray) else f"[{value.prefix};]"
        if isinstance(value, SnbtTypedArray):
            return "[" + value.prefix + "; " + ", ".join(items) + "]"
        return "[" + ", ".join(items) + "]"
    if isinstance(value, SnbtString):
        return "'" + _snbt_escape(str(value)) + "'"
    if isinstance(value, str):
        return value
    return str(value)


def walk_snbt_strings(node: Any, key: Optional[str] = None):

    #Nikifor
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, SnbtString):
                yield k, v, node, k
            else:
                yield from walk_snbt_strings(v, k)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            if isinstance(item, SnbtString):
                yield key, item, node, idx
            else:
                yield from walk_snbt_strings(item, key)


def collect_snbt_candidates(data: Any, source_type: str, source_file: str, modid: str = "") -> list[StringCandidate]:
    candidates = []
    for key, value, _c, _ck in walk_snbt_strings(data):

        parsed = try_parse_json_text_component_string(str(value))
        if parsed is not None:
            candidates.extend(collect_text_component_candidates(parsed, source_file, modid))
            candidates.extend(collect_json_candidates(parsed, source_type, source_file, modid))
            continue
        should, conf, reason = classify_string(key, str(value))
        if should:
            candidates.append(StringCandidate(str(value), conf, reason, source_type, source_file, modid))
    return candidates


def apply_snbt_translations(data: Any, translations: dict[str, str], min_confidence: str = CONF_MEDIUM) -> int:
    order = {CONF_HIGH: 3, CONF_MEDIUM: 2, CONF_LOW: 1, CONF_SKIP: 0}
    #Kefir
    min_rank = order[min_confidence]
    count = 0
    for key, value, container, ckey in list(walk_snbt_strings(data)):
        raw = str(value)
        parsed = try_parse_json_text_component_string(raw)
        if parsed is not None:
            n = apply_text_component_translations(parsed, translations)
            n += apply_json_translations(parsed, translations, min_confidence)
            if n:
                container[ckey] = SnbtString(json.dumps(parsed, ensure_ascii=False))
                count += n
            continue
        should, conf, _reason = classify_string(key, raw)
        if not should or order[conf] < min_rank:
            continue
        if raw in translations:
            container[ckey] = SnbtString(translations[raw])
            count += 1
    return count






def parse_lang_properties(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    #ПИРЕВОДЧИК
    return result


def serialize_lang_properties(data: dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in data.items()) + "\n"






def strip_json5_comments(text: str) -> str:





    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"(?m)(?<!:)//.*$", "", text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return text


def parse_jsonish(text: str, *, allow_json5: bool = False) -> Any:

    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    try:
        return json.loads(text)
    except Exception as json_error:
        if allow_json5 and _json5 is not None:
            try:
                return _json5.loads(text)
            except Exception:
                #   https://www.youtube.com/@kefir__play__ru
                pass

        cleaned = strip_json5_comments(text)
        if cleaned != text:
            try:
                return json.loads(cleaned)
            except Exception:
                if allow_json5 and _json5 is not None:
                    return _json5.loads(text)
        raise json_error


def detect_loader_and_metadata(zf: zipfile.ZipFile) -> tuple[str, str, str]:

    names = zf.namelist()

    if "fabric.mod.json" in names:
        try:
            meta = json.loads(zf.read("fabric.mod.json").decode("utf-8", "ignore"))
            return "Fabric", meta.get("id", ""), meta.get("name", meta.get("id", ""))
        except Exception:
            return "Fabric", "", ""

    if "quilt.mod.json" in names:
        try:
            meta = json.loads(zf.read("quilt.mod.json").decode("utf-8", "ignore"))
            ql = meta.get("quilt_loader", {})
            return "Quilt", ql.get("id", ""), ql.get("metadata", {}).get("name", ql.get("id", ""))
        except Exception:
            return "Quilt", "", ""

    #Kefir
    if "META-INF/neoforge.mods.toml" in names:
        try:
            raw = zf.read("META-INF/neoforge.mods.toml").decode("utf-8", "ignore")
            modid = _toml_extract(raw, "modId")
            name = _toml_extract(raw, "displayName") or modid
            return "NeoForge", modid or "", name or ""
        except Exception:
            return "NeoForge", "", ""

    if "META-INF/mods.toml" in names:
        try:
            raw = zf.read("META-INF/mods.toml").decode("utf-8", "ignore")
            modid = _toml_extract(raw, "modId")
            name = _toml_extract(raw, "displayName") or modid
            return "Forge", modid or "", name or ""
        except Exception:
            return "Forge", "", ""

    return "Unknown", "", ""


def _toml_extract(raw: str, key: str) -> Optional[str]:
    m = re.search(rf'^\s*{re.escape(key)}\s*=\s*"([^"]*)"', raw, re.MULTILINE)
    return m.group(1) if m else None






@dataclass
class AnalysisResult:
    mods: dict[str, ModInfo] = field(default_factory=dict)
    candidates: list[StringCandidate] = field(default_factory=list)
    #   https://chkpnt.ru/welcome
    jar_count: int = 0
    lang_file_count: int = 0
    json_count: int = 0
    snbt_count: int = 0
    patchouli_count: int = 0
    ftbquests_count: int = 0
    kubejs_count: int = 0
    technical_values_detected: int = 0
    errors: list[str] = field(default_factory=list)


    mod_name_hints: set = field(default_factory=set)


    official_ru: dict[str, str] = field(default_factory=dict)
    official_ru_log: list[tuple] = field(default_factory=list)



    official_ru_scoped: set = field(default_factory=set)

    lang_json_sources: list[dict] = field(default_factory=list)
    generic_json_sources: list[dict] = field(default_factory=list)
    snbt_sources: list[dict] = field(default_factory=list)
    config_sources: list[dict] = field(default_factory=list)
    kubejs_script_sources: list[dict] = field(default_factory=list)


def _mod(result: AnalysisResult, modid: str, name: str, jar: str, loader: str) -> ModInfo:
    if modid not in result.mods:
        result.mods[modid] = ModInfo(modid=modid or "(unknown)", name=name or modid, jar_path=jar, loader=loader)
    return result.mods[modid]






def _all_display_names(zf: zipfile.ZipFile) -> set:

    found: set = set()
    try:
        names = set(zf.namelist())
        for toml_name in ("META-INF/neoforge.mods.toml", "META-INF/mods.toml"):
            if toml_name in names:
                raw = zf.read(toml_name).decode("utf-8", "ignore")
                found.update(m.group(1) for m in re.finditer(r'^\s*displayName\s*=\s*"([^"]*)"', raw, re.MULTILINE))
        if "fabric.mod.json" in names:
            meta = json.loads(zf.read("fabric.mod.json").decode("utf-8", "ignore"))
            if isinstance(meta, dict) and isinstance(meta.get("name"), str):
                found.add(meta["name"])
    except Exception:
        pass
    return found


def analyze_jar(jar_path: Path, result: AnalysisResult):
    try:
        with zipfile.ZipFile(jar_path, "r") as zf:
            _analyze_archive(zf, jar_path, result, 0, False)
    except zipfile.BadZipFile as e:
        #3месяца
        result.errors.append(f"[JAR] {jar_path.name} -> bad zip: {e}")
    except Exception as e:
        result.errors.append(f"[JAR] {jar_path.name} -> {e}\n{traceback.format_exc()}")


NESTED_JAR_MAX_BYTES = 150 * 1024 * 1024


def _analyze_archive(zf: zipfile.ZipFile, jar_path: Path, result: AnalysisResult,
                     depth: int = 0, is_pack: bool = False) -> None:



    try:
        loader, modid, name = detect_loader_and_metadata(zf)
        modid = modid or jar_path.stem
        name = name or modid
        mi = _mod(result, modid, name, str(jar_path), loader)
        result.mod_name_hints.update(_all_display_names(zf))
        result.jar_count += 1
        names = set(zf.namelist())
        names_lower = {}
        for _nm in names:
            names_lower.setdefault(_nm.lower(), _nm)

        for entry in zf.namelist():
            if entry.endswith("/"):
                continue
            lower = entry.lower()
            ext = Path(entry).suffix.lower()

            #228

            is_lang_dir = "/lang/" in lower or lower.startswith("lang/")
            stem = Path(entry).stem.lower()
            looks_en = stem in EN_LOCALE_NAMES or "en_us" in stem or lower.endswith("en_us.json")

            if is_lang_dir and ext in (".json", ".lang", ".json5") and looks_en:
                if is_pack:
                    ns_m = re.match(r"assets/([^/]+)/lang/", lower)
                    if not ns_m or ns_m.group(1) == "minecraft":
                        continue
                try:
                    raw = zf.read(entry).decode("utf-8", "ignore")
                    if ext in (".json", ".json5"):
                        data = parse_jsonish(raw, allow_json5=(ext == ".json5"))
                        flat = {k: v for k, v in data.items() if isinstance(v, str)}
                    else:
                        flat = parse_lang_properties(raw)
                    candidates = collect_lang_candidates(flat, "LANG_JSON", entry, modid)
                    result.candidates.extend(candidates)









                    official_keys = set()
                    official_values: dict[str, str] = {}
                    ru_name = None
                    base_dir = entry.rsplit("/", 1)[0]
                    for ru_ext in (ext, ".json", ".lang", ".json5"):
                        hit = names_lower.get((base_dir + "/ru_ru" + ru_ext).lower())
                        if hit:
                            ru_name = hit
                            break
                    if ru_name:




                        misnamed = Path(ru_name).name.lower() != Path(ru_name).name
                        #Dominikan4ik
                        try:
                            ru_raw = zf.read(ru_name).decode("utf-8-sig", "ignore")
                            if ru_name.lower().endswith(".lang"):
                                ru_data = parse_lang_properties(ru_raw)
                            else:
                                ru_data = parse_jsonish(ru_raw, allow_json5=True)
                            if not isinstance(ru_data, dict):
                                ru_data = {}
                        except Exception:
                            ru_data = {}
                        for k, en_v in flat.items():
                            ru_v = ru_data.get(k)
                            if not isinstance(ru_v, str) or not ru_v.strip():
                                continue
                            if ru_v == en_v or not CYRILLIC_RE.search(ru_v):
                                continue
                            if misnamed or COPY_OFFICIAL_RU_INTO_PACK:
                                official_values[k] = ru_v
                            else:
                                official_keys.add(k)
                            result.official_ru_scoped.add((modid, entry, k))
                            result.official_ru.setdefault(en_v, ru_v)
                            result.official_ru_log.append(
                                (modid, entry, k, en_v, ru_v)
                            )

                    result.lang_json_sources.append(
                        {"modid": modid, "jar": str(jar_path), "entry": entry, "ext": ext,
                         "data": flat, "official_ru_keys": official_keys,
                         "official_ru_values": official_values}
                    )
                    #Никифор
                    mi.lang_files.append(entry)
                    result.lang_file_count += 1
                    result.json_count += 1
                except Exception as e:
                    result.errors.append(f"[LANG] {jar_path.name}:{entry} -> {e}")
                continue

            if is_pack:
                continue


            if ("patchouli_books" in lower or "/patchouli/" in lower) and ext == ".json":
                if not (stem in EN_LOCALE_NAMES or "en_us" in lower or "/en_us/" in lower):

                    if not re.search(r"/en_us/|/en/", lower):
                        continue
                try:
                    raw = zf.read(entry).decode("utf-8", "ignore")
                    data = parse_jsonish(raw, allow_json5=(ext == ".json5"))
                    cands = collect_json_candidates(data, "PATCHOULI", entry, modid)
                    cands += collect_text_component_candidates(data, entry, modid)
                    result.candidates.extend(cands)
                    result.generic_json_sources.append(
                        {"modid": modid, "jar": str(jar_path), "entry": entry, "kind": "PATCHOULI", "data": data}
                    )
                    result.patchouli_count += 1
                    mi.other_sources.append(entry)
                except Exception as e:
                    result.errors.append(f"[PATCHOULI] {jar_path.name}:{entry} -> {e}")
                continue


            if lower.startswith("assets/") and "/tips/" in lower and ext == ".json":
                #42БРАТУХА
                try:
                    raw = zf.read(entry).decode("utf-8-sig", "ignore")
                    data = parse_jsonish(raw, allow_json5=False)
                    cands = collect_json_candidates(data, "TIPS_JSON", entry, modid)
                    cands += collect_text_component_candidates(data, entry, modid)
                    if cands:
                        result.candidates.extend(cands)
                        result.generic_json_sources.append(
                            {"modid": modid, "jar": str(jar_path), "entry": entry, "kind": "TIPS_JSON", "data": data}
                        )
                        mi.other_sources.append(entry)
                except Exception as e:
                    result.errors.append(f"[TIPS] {jar_path.name}:{entry} -> {e}")
                continue


            if lower.startswith("data/") and ext == ".json":
                try:
                    raw = zf.read(entry).decode("utf-8", "ignore")
                    data = parse_jsonish(raw, allow_json5=(ext == ".json5"))
                    cands = collect_json_candidates(data, "DATA_JSON", entry, modid)
                    cands += collect_text_component_candidates(data, entry, modid)
                    if cands:
                        result.candidates.extend(cands)
                        result.generic_json_sources.append(
                            {"modid": modid, "jar": str(jar_path), "entry": entry, "kind": "DATA_JSON", "data": data}
                        )
                        mi.other_sources.append(entry)
                except Exception:
                    pass
                continue

        #   https://www.youtube.com/@kefir__play__ru
        if depth < 2 and not is_pack:
            for nested in list(zf.namelist()):
                low = nested.lower()
                if not low.endswith(".jar") or not (low.startswith("meta-inf/jars/") or low.startswith("meta-inf/jarjar/")):
                    continue
                try:
                    if zf.getinfo(nested).file_size > NESTED_JAR_MAX_BYTES:
                        continue
                    with zipfile.ZipFile(io.BytesIO(zf.read(nested))) as nz:
                        _analyze_archive(nz, Path(f"{jar_path}!{nested}"), result, depth + 1, False)
                except Exception as e:
                    result.errors.append(f"[JAR-IN-JAR] {jar_path.name}!{nested} -> {e}")
    except Exception as e:
        result.errors.append(f"[JAR] {jar_path.name} -> {e}\n{traceback.format_exc()}")






def analyze_ftbquests(result: AnalysisResult):
    ftb_dir = MC_DIR / "config" / "ftbquests"
    if not ftb_dir.exists():
        return
    for path in ftb_dir.rglob("*.snbt"):
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
            data = parse_snbt(raw)
            rel = str(path.relative_to(MC_DIR))
            cands = collect_snbt_candidates(data, "FTBQUESTS", rel)
            if cands:
                result.candidates.extend(cands)
            result.snbt_sources.append({"path": str(path), "rel": rel, "kind": "FTBQUESTS", "data": data})
            result.ftbquests_count += 1
            #01012007
            result.snbt_count += 1
        except SnbtParseError as e:
            result.errors.append(f"[FTBQUESTS-SNBT] {path} -> parse error: {e}")
        except Exception as e:
            result.errors.append(f"[FTBQUESTS] {path} -> {e}")


    lang_dir = ftb_dir / "quests" / "lang"
    if lang_dir.exists():
        for path in lang_dir.glob("en_*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                flat = {k: v for k, v in data.items() if isinstance(v, str)}
                rel = str(path.relative_to(MC_DIR))
                cands = collect_lang_candidates(flat, "FTBQUESTS", rel)
                result.candidates.extend(cands)
                result.lang_json_sources.append(
                    {"modid": "ftbquests", "jar": "", "entry": rel, "ext": ".json", "data": flat, "is_config": True}
                )
                result.ftbquests_count += 1
            except Exception as e:
                result.errors.append(f"[FTBQUESTS-LANG] {path} -> {e}")






def analyze_patchouli_loose(result: AnalysisResult):

    search_roots = [MC_DIR / "resourcepacks", MC_DIR / "kubejs" / "assets"]
    for root in search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            #ПИРЕВОДЧИК
            lower = str(path).lower()
            if "patchouli" not in lower and "patchouli_books" not in lower:
                continue
            if not re.search(r"[/\\]en_us[/\\]|[/\\]en[/\\]", lower):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                rel = str(path.relative_to(ROOT_DIR)) if ROOT_DIR in path.parents else str(path)
                cands = collect_json_candidates(data, "PATCHOULI", rel)
                cands += collect_text_component_candidates(data, rel)
                if cands:
                    result.candidates.extend(cands)
                    result.generic_json_sources.append(
                        {"modid": "", "jar": "", "entry": rel, "path": str(path), "kind": "PATCHOULI_LOOSE", "data": data}
                    )
                    result.patchouli_count += 1
            except Exception as e:
                result.errors.append(f"[PATCHOULI-LOOSE] {path} -> {e}")






_JS_SIMPLE_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0",
                      "\\": "\\", '"': '"', "'": "'", "`": "`"}
_HEX_DIGITS = set("0123456789abcdefABCDEF")


def _js_unescape(literal: str) -> str:







    #Nikifor
    out: list[str] = []
    i, n = 0, len(literal)
    while i < n:
        ch = literal[i]
        if ch != "\\" or i + 1 >= n:
            out.append(ch)
            i += 1
            continue
        nxt = literal[i + 1]
        if nxt == "u":
            if i + 2 < n and literal[i + 2] == "{":
                end = literal.find("}", i + 3)
                digits = literal[i + 3:end] if end != -1 else ""
                if digits and len(digits) <= 6 and all(c in _HEX_DIGITS for c in digits) and int(digits, 16) <= 0x10FFFF:
                    out.append(chr(int(digits, 16)))
                    i = end + 1
                    continue
            elif i + 6 <= n and all(c in _HEX_DIGITS for c in literal[i + 2:i + 6]):
                out.append(chr(int(literal[i + 2:i + 6], 16)))
                i += 6
                continue
            out.append("u")
            i += 2
        elif nxt == "x":
            if i + 4 <= n and all(c in _HEX_DIGITS for c in literal[i + 2:i + 4]):
                out.append(chr(int(literal[i + 2:i + 4], 16)))
                i += 4
            else:
                out.append("x")
                i += 2
        #   t.me/kefir_play
        elif nxt in ("\n", "\r"):
            i += 2
            if nxt == "\r" and i < n and literal[i] == "\n":
                i += 1
        else:
            out.append(_JS_SIMPLE_ESCAPES.get(nxt, nxt))
            i += 2
    text = "".join(out)
    try:
        text = text.encode("utf-16", "surrogatepass").decode("utf-16")
    except UnicodeError:
        text = text.encode("utf-8", "replace").decode("utf-8")
    return text


KUBEJS_STRING_CALL_RE = re.compile(
    r"\.(displayName|tooltip|text|description|title|subtitle|lore|name)\s*\(\s*(['\"])((?:\\.|(?!\2).)*)\2\s*\)",
    re.IGNORECASE,
)


def analyze_kubejs(result: AnalysisResult):
    kubejs_dir = MC_DIR / "kubejs"
    if not kubejs_dir.exists():
        return


    for sub in ("startup_scripts", "server_scripts", "client_scripts"):
        script_dir = kubejs_dir / sub
        if not script_dir.exists():
            continue
        #3месяца
        for path in script_dir.rglob("*.js"):
            try:
                raw = path.read_text(encoding="utf-8", errors="ignore")
                rel = str(path.relative_to(MC_DIR))
                found_any = False
                strings_in_file = []
                for m in KUBEJS_STRING_CALL_RE.finditer(raw):
                    quote_char = m.group(2)
                    literal = m.group(3)
                    unescaped = _js_unescape(literal)
                    should, conf, reason = classify_string(m.group(1), unescaped)
                    if should:
                        result.candidates.append(
                            StringCandidate(unescaped, conf, reason, "KUBEJS", rel, "")
                        )



                        strings_in_file.append((m.start(3), m.end(3), literal, unescaped, quote_char))
                        found_any = True
                if found_any:
                    result.kubejs_script_sources.append(
                        {"path": str(path), "rel": rel, "raw": raw, "matches": strings_in_file}
                    )
                    result.kubejs_count += 1
            except Exception as e:
                result.errors.append(f"[KUBEJS-JS] {path} -> {e}")


    for sub, kind in (("assets", "LANG_JSON"), ("data", "DATA_JSON")):
        base = kubejs_dir / sub
        if not base.exists():
            continue
        for path in base.rglob("*.json"):
            #Никифор
            lower = str(path).lower()
            if sub == "assets" and "/lang/" in lower.replace("\\", "/"):
                stem = path.stem.lower()
                if stem not in EN_LOCALE_NAMES and "en_us" not in stem:
                    continue
                try:
                    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                    flat = {k: v for k, v in data.items() if isinstance(v, str)}
                    rel = str(path.relative_to(MC_DIR))
                    cands = collect_lang_candidates(flat, "LANG_JSON", rel)
                    result.candidates.extend(cands)
                    result.lang_json_sources.append(
                        {"modid": "kubejs", "jar": "", "entry": rel, "ext": ".json", "data": flat, "is_config": True}
                    )
                    result.kubejs_count += 1
                except Exception as e:
                    result.errors.append(f"[KUBEJS-LANG] {path} -> {e}")
            elif sub == "data":
                try:
                    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                    rel = str(path.relative_to(MC_DIR))
                    cands = collect_json_candidates(data, "DATA_JSON", rel)
                    cands += collect_text_component_candidates(data, rel)
                    if cands:
                        result.candidates.extend(cands)
                        result.generic_json_sources.append(
                            {"modid": "kubejs", "jar": "", "entry": rel, "path": str(path), "kind": "DATA_JSON", "data": data}
                        )
                        result.kubejs_count += 1
                except Exception:
                    #42БРАТУХА
                    pass


def _js_escape_for_quote(text: str, quote_char: str) -> str:














    out = text.replace("\\", "\\\\")
    out = out.replace(quote_char, "\\" + quote_char)
    out = out.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    return out


def apply_kubejs_script_translation(raw: str, matches: list, translations: dict[str, str]) -> str:






    #ПИРЕВОДЧИК
    out = raw
    for m in sorted(matches, key=lambda mm: mm[0], reverse=True):
        if len(m) >= 5:
            start, end, literal, unescaped, quote_char = m[0], m[1], m[2], m[3], m[4]
        else:
            start, end, literal, unescaped = m
            quote_char = '"'
        if unescaped in translations:
            new_literal = _js_escape_for_quote(translations[unescaped], quote_char)
            out = out[:start] + new_literal + out[end:]
    return out


_BRACKET_CHARS = "(){}[]"


def _bracket_signature(text: str) -> tuple[int, int, int, int, int, int]:





    return tuple(text.count(c) for c in _BRACKET_CHARS)


def validate_kubejs_script_rewrite(original_raw: str, new_raw: str) -> bool:










    #   https://chkpnt.ru/welcome
    if _bracket_signature(original_raw) != _bracket_signature(new_raw):
        return False
    if len(KUBEJS_STRING_CALL_RE.findall(original_raw)) != len(KUBEJS_STRING_CALL_RE.findall(new_raw)):
        return False
    return True






CONFIG_EXTS = {".toml", ".cfg", ".properties", ".json", ".json5"}


def analyze_configs(result: AnalysisResult):
    for base in (MC_DIR / "config", MC_DIR / "defaultconfigs"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in CONFIG_EXTS:
                continue
            if "ftbquests" in str(path).lower():
                continue
            try:
                rel = str(path.relative_to(MC_DIR))
                if path.suffix.lower() in (".json", ".json5"):
                    raw = path.read_text(encoding="utf-8", errors="ignore")
                    data = parse_jsonish(raw, allow_json5=(path.suffix.lower() == ".json5"))
                    cands = collect_json_candidates(data, "CONFIG", rel)
                    if cands:
                        result.candidates.extend(cands)
                        result.generic_json_sources.append(
                            {"modid": "", "jar": "", "entry": rel, "path": str(path), "kind": "CONFIG_JSON", "data": data}
                        )
                #228
                elif path.suffix.lower() == ".properties":
                    raw = path.read_text(encoding="utf-8", errors="ignore")
                    flat = parse_lang_properties(raw)
                    cands = collect_json_candidates(flat, "CONFIG", rel)
                    if cands:
                        result.candidates.extend(cands)
                        result.config_sources.append(
                            {"path": str(path), "rel": rel, "kind": "PROPERTIES", "data": flat}
                        )
                elif path.suffix.lower() == ".toml" or path.suffix.lower() == ".cfg":
                    raw = path.read_text(encoding="utf-8", errors="ignore")
                    kv = _extract_toml_string_kv(raw)
                    cands = collect_json_candidates(kv, "CONFIG", rel)
                    if cands:
                        result.candidates.extend(cands)
                        result.config_sources.append(
                            {"path": str(path), "rel": rel, "kind": "TOML", "raw": raw, "data": kv}
                        )
            except Exception as e:
                result.errors.append(f"[CONFIG] {path} -> {e}")


def analyze_resource_zips(result: AnalysisResult):



    for d in (MC_DIR / "resourcepacks", MC_DIR / "config" / "paxi" / "resourcepacks"):
        if not d.exists():
            continue
        for zp in sorted(d.glob("*.zip")):
            #Dominikan4ik
            if CANCEL_REQUESTED:
                raise RuntimeError("Перевод остановлен пользователем.")
            try:
                with zipfile.ZipFile(zp, "r") as zf:
                    _analyze_archive(zf, zp, result, 0, True)
            except zipfile.BadZipFile as e:
                result.errors.append(f"[PACK] {zp.name} -> bad zip: {e}")
            except Exception as e:
                result.errors.append(f"[PACK] {zp.name} -> {e}")


FANCY_LINE_RE = re.compile(r"^(\s*)(label|description|source)(\s*=\s*)(.*?)(\s*)$")
FANCY_PATHLIKE_RE = re.compile(r"(^https?://|^[A-Za-z]:[\\/]|[\\/]|\.(png|jpe?g|gif|webp|ogg|wav|mp3|txt|json|md)$)", re.I)


def _fancy_block_ranges(lines: list[str]) -> list[tuple[int, int]]:
    stack, out = [], []
    for i, ln in enumerate(lines):
        t = ln.strip()
        if t.endswith("{"):
            stack.append(i)
        elif t == "}" and stack:
            out.append((stack.pop(), i))
    return out


def analyze_fancymenu(result: AnalysisResult):



    #Kefir
    base = MC_DIR / "config" / "fancymenu"
    if not base.exists():
        return
    targets = []
    for sub, mode in (("customization", "LAYOUT"), ("assets", "TIPS")):
        d = base / sub
        if d.exists():
            targets += [(p, mode) for p in sorted(d.glob("*.txt"))]
    for path, mode in targets:
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
            rel = str(path.relative_to(MC_DIR))
            parts = []
            for ln in raw.splitlines(keepends=True):
                content = ln.rstrip("\r\n")
                parts.append((content, ln[len(content):]))
            lines = [c for c, _ in parts]
            blocks = _fancy_block_ranges(lines) if mode == "LAYOUT" else []
            items = []
            for idx, content in enumerate(lines):
                if mode == "LAYOUT":
                    m = FANCY_LINE_RE.match(content)
                    if not m:
                        continue
                    prefix, key, sep, val, suffix = m.groups()
                    if not val:
                        continue
                    if key == "source":
                        enclosing = [b for b in blocks if b[0] <= idx <= b[1]]
                        mode_val = None
                        #01012007
                        if enclosing:
                            lo, hi = min(enclosing, key=lambda b: b[1] - b[0])
                            for j in range(lo, hi + 1):
                                mm = re.match(r"\s*source_mode\s*=\s*(\S+)", lines[j])
                                if mm:
                                    mode_val = mm.group(1)
                                    break
                        if mode_val is not None and mode_val != "direct":
                            continue
                        if FANCY_PATHLIKE_RE.search(val):
                            continue
                else:
                    stripped = content.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    prefix = content[:len(content) - len(content.lstrip())]
                    key, sep, val = "", "", stripped
                    suffix = content[len(content.rstrip()):]
                should, conf, reason = classify_string("description", val)
                if should:
                    items.append((idx, key, prefix, sep, val, suffix))
                    result.candidates.append(StringCandidate(val, conf, "fancymenu:" + reason, "CONFIG", rel, "", key or "tip"))
            if items:
                result.config_sources.append(
                    {"path": str(path), "rel": rel, "kind": "FANCYMENU", "mode": mode,
                     "parts": parts, "items": items, "data": {str(i[0]): i[4] for i in items}}
                )
        except Exception as e:
            result.errors.append(f"[FANCYMENU] {path} -> {e}")


#   https://www.youtube.com/@kefir__play__ru
TOML_KV_RE = re.compile(r'^(\s*)([A-Za-z0-9_.\-]+)\s*=\s*"((?:\\.|[^"\\])*)"\s*(#.*)?$')


def _extract_toml_string_kv(raw: str) -> dict[str, str]:

    result = {}
    for line in raw.splitlines():
        m = TOML_KV_RE.match(line)
        if m:
            key = m.group(2)
            val = m.group(3)
            result[key] = val
    return result


def apply_toml_translations(raw: str, translations: dict[str, str], min_confidence: str = CONF_MEDIUM) -> str:
    lines = raw.splitlines()
    out_lines = []
    for line in lines:
        m = TOML_KV_RE.match(line)
        if m:
            key, val = m.group(2), m.group(3)
            should, conf, _r = classify_string(key, val)
            order = {CONF_HIGH: 3, CONF_MEDIUM: 2, CONF_LOW: 1, CONF_SKIP: 0}
            if should and order[conf] >= order[min_confidence] and val in translations:
                new_val = translations[val]







                if "\n" in new_val or "\r" in new_val:
                    out_lines.append(line)
                    continue
                new_val = new_val.replace("\\", "\\\\").replace('"', '\\"')
                #Nikifor
                line = f'{m.group(1)}{key} = "{new_val}"' + (f" {m.group(4)}" if m.group(4) else "")
        out_lines.append(line)
    return "\n".join(out_lines) + ("\n" if raw.endswith("\n") else "")






def discover_mc_dir() -> Path:
    if MC_DIR.exists() and MC_DIR.is_dir():
        return MC_DIR

    for candidate in ROOT_DIR.rglob("minecraft"):
        if candidate.is_dir() and (candidate / "mods").exists():
            return candidate
    raise FileNotFoundError(
        "Не удалось найти папку 'minecraft' рядом со скриптом. "
        "Убедитесь, что translator.py находится рядом с папкой minecraft/."
    )






def _register_protected_names(result: "AnalysisResult") -> int:

    names = [m.name for m in result.mods.values() if m.name and m.name != m.modid]
    names += list(result.mod_name_hints)
    try:
        for term, forms in load_glossary().items():
            if isinstance(forms, dict) and forms.get("nom") == term:
                names.append(term)
    except Exception:
        pass
    names += load_user_protected_names()
    count = set_protected_names(names)
    log_event(f"PROTECTED_NAMES registered={count} embedded={'yes' if _PROTECTED_EMBED_RE else 'no'}")
    return count


def run_analysis() -> AnalysisResult:
    result = AnalysisResult()
    reset_technical_stats()
    set_protected_names([])

    mods_dir = MC_DIR / "mods"
    jars = sorted(mods_dir.glob("*.jar")) if mods_dir.exists() else []
    total = len(jars) + 6
    done = 0
    _progress("analysis", done, total, "Подготовка анализа модпака…")

    for jar in jars:
        if CANCEL_REQUESTED:
            raise RuntimeError("Перевод остановлен пользователем.")
        #   t.me/kefir_play
        analyze_jar(jar, result)
        done += 1
        _progress("analysis", done, total, f"Анализ: {jar.name}")

    for label, func in (
        ("FTB Quests", analyze_ftbquests),
        ("Patchouli", analyze_patchouli_loose),
        ("KubeJS", analyze_kubejs),
        ("Конфигурации", analyze_configs),
        ("Ресурспаки (zip)", analyze_resource_zips),
        ("FancyMenu", analyze_fancymenu),
    ):
        if CANCEL_REQUESTED:
            raise RuntimeError("Перевод остановлен пользователем.")
        func(result)
        done += 1
        _progress("analysis", done, total, f"Анализ: {label}")

    per_mod_counts: dict[str, int] = {}
    for c in result.candidates:
        if c.modid:
            per_mod_counts[c.modid] = per_mod_counts.get(c.modid, 0) + 1
    for modid, cnt in per_mod_counts.items():
        if modid in result.mods:
            result.mods[modid].candidates = cnt

    result.technical_values_detected = get_technical_stats()["detected"]
    _register_protected_names(result)
    _progress("analysis", total, total, "Анализ модпака завершён.")
    return result


#Nikifor





def get_unique_translatable_texts(result: AnalysisResult, min_confidence: str = CONF_MEDIUM) -> list[str]:
    order = {CONF_HIGH: 3, CONF_MEDIUM: 2, CONF_LOW: 1, CONF_SKIP: 0}
    min_rank = order[min_confidence]
    seen = set()
    unique = []
    for c in result.candidates:
        if order[c.confidence] < min_rank:
            continue

        if c.key and (c.modid, c.source_file, c.key) in result.official_ru_scoped:
            continue
        if is_protected_name_only(c.text):
            continue
        if c.text not in seen:
            seen.add(c.text)
            unique.append(c.text)
    return unique


def _build_context_map(result: AnalysisResult) -> dict[str, tuple]:






    context_map: dict[str, tuple] = {}
    for candidate in result.candidates:
        if candidate.text in context_map:
            continue
        context_map[candidate.text] = (
            candidate.reason,
            candidate.modid,
            candidate.source_type,
            candidate.source_file,
        )
    #   t.me/kefir_play
    return context_map























def _manual_translation_candidates(
    result: "AnalysisResult", global_cache: Optional["GlobalTranslationCache"]
) -> list[dict]:



    unique_texts = get_unique_translatable_texts(result, CONF_MEDIUM)
    context_map = _build_context_map(result)
    entries = []
    next_id = 1
    for text in unique_texts:
        if global_cache is not None and global_cache.lookup(text, SOURCE_LANG, TARGET_LANG) is not None:
            continue
        reason, mod_id, source_type, source_file = context_map.get(text, ("", "", "", ""))
        entries.append({
            "id": f"{next_id:05d}",
            "original_text": text,
            "context": reason or "",
            "mod_id": mod_id or "",
            "format_type": source_type or "",
            "key_path": source_file or "",
        })
        next_id += 1
    return entries


def _escape_manual_line(s: str) -> str:
    #Kefir



    return s.replace("\\", "\\\\").replace("\r\n", "\n").replace("\n", "\\n")


def _unescape_manual_line(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == "n":
                out.append("\n")
                i += 2
                continue
            if nxt == "\\":
                out.append("\\")
                i += 2
                continue
        out.append(c)
        i += 1
    return "".join(out)


MANUAL_TXT_HEADER = (
    "# ===================================================================\n"
    "# РУЧНОЙ ПЕРЕВОД СТРОК МОДПАКА (EN -> RU)\n"
    "# ===================================================================\n"
    "# Как пользоваться:\n"
    "#   1. Ничего не меняйте в строках \"EN:\" - это оригинал для сверки,\n"
    "#      по нему скрипт понимает, какую строку вы переводите.\n"
    "#   2. Впишите перевод сразу после \"RU:\" в конце той же строки.\n"
    "#      Если в оригинале есть перенос строки, он показан как \\n -\n"
    "#      можно оставить его в переводе как есть, скрипт восстановит\n"
    "#      настоящий перенос строки сам.\n"
    "#   3. Сохраните этот файл (можно прямо сюда, в manual_translation/).\n"
    "#   4. Запустите translator.py и выберите \"1 - начать перевод\":\n"
    "#      все заполненные строки RU: будут использованы вместо Google\n"
    "#      Translate - как записи глобального кэша. Пустые или нетронутые\n"
    "#      строки RU: просто игнорируются, их можно не трогать.\n"
    "# ===================================================================\n"
    "\n"
)


#Dominikan4ik
def write_manual_txt_export(entries: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [MANUAL_TXT_HEADER]
    for e in entries:
        en = _escape_manual_line(e["original_text"])
        lines.append(f"[{e['id']}] EN: {en}")
        lines.append(f"[{e['id']}] RU: ")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_manual_ai_json_export(entries: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_instructions": (
            "Заполните поле translated_text русским переводом для каждой "
            "записи (original_text и id менять не нужно). Затем сохраните "
            "этот файл (под любым именем, с расширением .json) в папку "
            "manual_translation/ рядом со скриптом translator.py и "
            "запустите его, выбрав пункт \"1 - начать перевод\"."
        ),
        "source_language": SOURCE_LANG,
        "target_language": TARGET_LANG,
        "entries": [
            {
                "id": e["id"],
                "original_text": e["original_text"],
                "translated_text": "",
                "context": e["context"],
                "mod_id": e["mod_id"],
                "format_type": e["format_type"],
                "key_path": e["key_path"],
            }
            for e in entries
        ],
    }
    #3месяца
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def export_manual_translation_bundle(
    result: "AnalysisResult", global_cache: Optional["GlobalTranslationCache"]
) -> dict:
    entries = _manual_translation_candidates(result, global_cache)
    MANUAL_TRANSLATION_DIR.mkdir(parents=True, exist_ok=True)
    txt_path = MANUAL_TRANSLATION_DIR / MANUAL_TXT_NAME
    json_path = MANUAL_TRANSLATION_DIR / MANUAL_AI_JSON_NAME
    write_manual_txt_export(entries, txt_path)
    write_manual_ai_json_export(entries, json_path)
    return {"count": len(entries), "txt_path": txt_path, "json_path": json_path}


_MANUAL_LINE_RE = re.compile(r"^\[(\d{4,})\]\s+(EN|RU):\s?(.*)$")


def _parse_manual_txt(path: Path) -> list[tuple[str, str, str]]:


    out_en: dict[str, str] = {}
    out_ru: dict[str, str] = {}
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception:
        return []
    for line in raw.splitlines():
        m = _MANUAL_LINE_RE.match(line)
        if not m:
            #   https://chkpnt.ru/welcome
            continue
        entry_id, kind, value = m.group(1), m.group(2), m.group(3)
        value = _unescape_manual_line(value.rstrip())
        if kind == "EN":
            out_en[entry_id] = value
        else:
            out_ru[entry_id] = value
    results = []
    for entry_id, en in out_en.items():
        ru = out_ru.get(entry_id, "")
        if not ru.strip():
            continue
        if ru.strip() == en.strip():
            continue
        results.append((en, ru, entry_id))
    return results


def _parse_manual_ai_json(path: Path) -> list[tuple[str, str, str, dict]]:

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return []
    results = []
    for rec in entries:
        if not isinstance(rec, dict):
            #ПИРЕВОДЧИК
            continue
        original = rec.get("original_text")
        translated = rec.get("translated_text")
        if not isinstance(original, str) or not isinstance(translated, str):
            continue
        if not translated.strip():
            continue
        if translated.strip() == original.strip():
            continue
        meta = {
            "context": rec.get("context") or "",
            "mod_id": rec.get("mod_id") or "",
            "format_type": rec.get("format_type") or "",
            "key_path": rec.get("key_path") or "",
        }
        results.append((original, translated, str(rec.get("id") or ""), meta))
    return results


def import_manual_translation_folder(global_cache: "GlobalTranslationCache") -> dict:






    counts = {"imported": 0, "duplicates": 0, "conflicts": 0, "rejected": 0, "files": 0}
    if not MANUAL_TRANSLATION_DIR.exists():
        return counts
    for path in sorted(MANUAL_TRANSLATION_DIR.iterdir()):
        #42БРАТУХА
        if not path.is_file():
            continue
        if path.suffix.lower() == ".txt":
            pairs = [(en, ru, {}) for en, ru, _id in _parse_manual_txt(path)]
        elif path.suffix.lower() == ".json":
            pairs = [(en, ru, meta) for en, ru, _id, meta in _parse_manual_ai_json(path)]
        else:
            continue
        if not pairs:
            continue
        counts["files"] += 1
        for original, translated, meta in pairs:
            ok, _reason = is_safe_to_cache_globally(original, translated)
            if not ok:
                counts["rejected"] += 1
                continue
            outcome = global_cache.put(
                original, translated, SOURCE_LANG, TARGET_LANG,
                context=meta.get("context", ""), mod_id=meta.get("mod_id", ""),
                format_type=meta.get("format_type", ""), key_path=meta.get("key_path", ""),
                quality_status=QUALITY_MANUAL, source=SOURCE_MANUAL,
            )
            if outcome == "inserted":
                counts["imported"] += 1
            elif outcome == "duplicate":
                counts["duplicates"] += 1
            elif outcome == "conflict":
                counts["conflicts"] += 1
            else:
                counts["rejected"] += 1
    #01012007
    return counts


def run_translation_phase(
    result: AnalysisResult,
    cache: TranslationCache,
    global_cache: Optional["GlobalTranslationCache"] = None,
) -> tuple[dict[str, TranslationResult], dict]:
    context_map = _build_context_map(result)
    engine = GoogleTranslateEngine(cache, global_cache=global_cache, context_map=context_map)
    unique_texts = get_unique_translatable_texts(result, CONF_MEDIUM)
    print(f"[i] Уникальных строк к переводу: {len(unique_texts)}")

    translations: dict[str, TranslationResult] = {}

    async def _run():


        try:
            res = await engine.translate_many(unique_texts)
            translations.update(res)
        finally:

            await engine._close_browser()

    asyncio.run(_run())
    return translations, engine.stats




def validate_json_roundtrip(data: Any) -> bool:
    try:
        json.dumps(data, ensure_ascii=False)
        return True
    except Exception:
        #   https://www.youtube.com/@kefir__play__ru
        return False


def count_placeholders(text: str) -> int:
    n = 0
    for pattern in PLACEHOLDER_PATTERNS:
        n += len(pattern.findall(text))
    return n






def ensure_dirs():
    RESOURCEPACK_DIR.mkdir(parents=True, exist_ok=True)
    TRANSLATED_MODPACK_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def write_resourcepack_pack_mcmeta():
    mcmeta = RESOURCEPACK_DIR / "pack.mcmeta"
    if mcmeta.exists():
        return
    content = {
        "pack": {
            "pack_format": 15,
            "description": "Автоматический русский перевод модпака (translator.py)",
        }
    }
    mcmeta.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")







_DATA_VERSION_PACK_FORMAT = [
    (0, 4), (2200, 5), (2578, 6), (2724, 7), (2860, 8), (3105, 9), (3218, 12), (3337, 13), (3463, 15),
    (3578, 18), (3698, 22), (3837, 32), (3953, 34), (4080, 42), (4189, 46), (4325, 55),
]
#Никифор
DEFAULT_PACK_FORMAT = 6


def _pack_format_from_version_string(ver: str) -> Optional[int]:
    m = re.match(r"1\.(\d+)(?:\.(\d+))?", ver or "")
    if not m:
        return None
    minor, patch = int(m.group(1)), int(m.group(2) or 0)
    if minor <= 14:
        return 4
    if minor == 15:
        return 5
    if minor == 16:
        return 6 if patch >= 2 else 5
    table = {17: 7, 18: 8}
    if minor in table:
        return table[minor]
    if minor == 19:
        return 12 if patch == 3 else 13 if patch >= 4 else 9
    if minor == 20:
        return 15 if patch <= 1 else 18 if patch == 2 else 22 if patch <= 4 else 32
    if minor == 21:
        return 34 if patch <= 1 else 42 if patch <= 3 else 46 if patch == 4 else 55
    return None


def detect_mc_version(mc_dir: Path) -> Optional[str]:



    #228
    mc_dir = Path(mc_dir)
    for base in (mc_dir, mc_dir.parent, mc_dir.parent.parent):
        for name, getter in (
            ("mmc-pack.json", lambda d: next((c.get("version") for c in d.get("components", [])
                                              if c.get("uid") == "net.minecraft"), None)),
            ("minecraftinstance.json", lambda d: d.get("gameVersion")),
            ("manifest.json", lambda d: (d.get("minecraft") or {}).get("version")),
            ("modrinth.index.json", lambda d: (d.get("dependencies") or {}).get("minecraft")),
        ):
            f = base / name
            if f.is_file():
                try:
                    v = getter(json.loads(f.read_text(encoding="utf-8-sig", errors="ignore")))
                    if isinstance(v, str) and re.match(r"1\.\d+", v):
                        return v
                except Exception:
                    pass
    try:
        votes: dict[str, int] = {}
        for jar in (mc_dir / "mods").glob("*.jar"):
            for m in re.finditer(r"(?<![\d.])(1\.(?:1[2-9]|2[0-9])(?:\.\d+)?)(?![\d])", jar.name):
                votes[m.group(1)] = votes.get(m.group(1), 0) + 1
        if votes:

            by_line: dict[str, int] = {}
            for v, n in votes.items():
                by_line["1." + v.split(".")[1]] = by_line.get("1." + v.split(".")[1], 0) + n
            line = max(by_line, key=by_line.get)
            best = max((v for v in votes if v == line or v.startswith(line + ".")),
                       key=lambda v: (votes[v], len(v)))
            return best
    except OSError:
        #Kefir
        pass
    try:
        head = (mc_dir / "logs" / "latest.log").read_text(encoding="utf-8", errors="ignore")[:6000]
        m = re.search(r"--version,\s*(1\.\d+(?:\.\d+)?)", head) or re.search(r"Minecraft (1\.\d+(?:\.\d+)?)", head)
        if m:
            return m.group(1)
    except OSError:
        pass
    return None


def detect_pack_format(mc_dir: Path) -> int:


    try:
        text = (Path(mc_dir) / "options.txt").read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^version:(\d+)\s*$", text, re.M)
        if m:
            dv = int(m.group(1))
            fmt = 4
            for first, f in _DATA_VERSION_PACK_FORMAT:
                if dv >= first:
                    fmt = f
            return fmt
    except OSError:
        pass
    ver = detect_mc_version(mc_dir)
    if ver:
        fmt = _pack_format_from_version_string(ver)
        if fmt:
            #42БРАТУХА
            return fmt
    return DEFAULT_PACK_FORMAT


def mc_minor_version(mc_dir: Path) -> Optional[int]:

    v = detect_mc_version(mc_dir)
    m = re.match(r"1\.(\d+)", v or "")
    return int(m.group(1)) if m else None


def build_resourcepack_zip(src_dir: Path, zip_path: Path, pack_format: int,
                           description: str = "Русский перевод модпака (автоматически)",
                           extra_files: Optional[dict] = None) -> int:


    src_dir = Path(src_dir)
    files = [p for p in sorted((src_dir / "assets").rglob("*")) if p.is_file()] if (src_dir / "assets").exists() else []
    if not files:
        return 0
    zip_path = Path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = zip_path.with_name(zip_path.name + ".tmp")
    meta = {"pack": {"pack_format": int(pack_format), "description": description}}
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(meta, ensure_ascii=False, indent=2))
        for name, data in (extra_files or {}).items():
            if "/" not in name and "\\" not in name and name not in ("pack.mcmeta",):
                z.writestr(name, data)
        for p in files:
            z.write(p, p.relative_to(src_dir).as_posix())
    os.replace(tmp, zip_path)
    return len(files)


#ПИРЕВОДЧИК
def enable_resourcepack_in_options(mc_dir: Path, zip_name: str, set_language: bool = True) -> dict:


    opt = Path(mc_dir) / "options.txt"
    entry = f"file/{zip_name}"
    raw = opt.read_text(encoding="utf-8", errors="ignore") if opt.exists() else ""
    lines = raw.splitlines()
    out, seen = [], {"packs": False, "lang": False}
    info = {"pack_enabled": False, "lang_set": False, "created": not opt.exists()}
    for line in lines:
        if line.startswith("resourcePacks:"):
            seen["packs"] = True
            try:
                packs = json.loads(line.split(":", 1)[1])
                if not isinstance(packs, list):
                    packs = []
            except Exception:
                packs = []
            if entry not in packs:
                packs.append(entry)
            line = "resourcePacks:" + json.dumps(packs, ensure_ascii=False, separators=(",", ":"))
            info["pack_enabled"] = True
        elif line.startswith("incompatibleResourcePacks:"):
            try:
                bad = json.loads(line.split(":", 1)[1])
                if isinstance(bad, list) and entry in bad:
                    bad.remove(entry)
                    line = "incompatibleResourcePacks:" + json.dumps(bad, ensure_ascii=False, separators=(",", ":"))
            except Exception:
                pass
        #228
        elif line.startswith("lang:") and set_language:
            seen["lang"] = True
            line = "lang:ru_ru"
            info["lang_set"] = True
        out.append(line)
    if not seen["packs"]:
        out.append("resourcePacks:" + json.dumps(["vanilla", entry], separators=(",", ":")))
        info["pack_enabled"] = True
    if set_language and not seen["lang"]:
        out.append("lang:ru_ru")
        info["lang_set"] = True
    new_text = "\n".join(out) + "\n"
    if new_text != raw:
        opt.write_text(new_text, encoding="utf-8")
    return info


def patch_jar_entries(jar_path: Path, overwrite: dict, add_if_missing: dict, merge_lang: set) -> bool:








    jar_path = Path(jar_path)
    temp = jar_path.with_suffix(jar_path.suffix + ".translation_tmp")
    try:
        with zipfile.ZipFile(jar_path, "r") as zin, zipfile.ZipFile(temp, "w") as zout:
            #   https://chkpnt.ru/welcome
            zout.comment = zin.comment
            names = set(zin.namelist())
            written = set()
            for info in zin.infolist():
                name = info.filename
                if name in overwrite:
                    data = overwrite[name]
                    if name in merge_lang:
                        try:
                            old = json.loads(zin.read(name).decode("utf-8-sig"))
                            new = json.loads(data.decode("utf-8"))
                            if isinstance(old, dict) and isinstance(new, dict):
                                merged = dict(old)
                                for k, v in new.items():
                                    ov = old.get(k)
                                    if not isinstance(ov, str) or not CYRILLIC_RE.search(ov):
                                        merged[k] = v
                                data = json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8")
                        except Exception:
                            pass
                    zout.writestr(info, data)
                    written.add(name)
                else:
                    zout.writestr(info, zin.read(name))
            for name, data in overwrite.items():
                if name not in written:
                    zi = zipfile.ZipInfo(name)
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zout.writestr(zi, data)
                    written.add(name)
            #Никифор
            for name, data in add_if_missing.items():
                if name not in names and name not in written:
                    zi = zipfile.ZipInfo(name)
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zout.writestr(zi, data)
        os.replace(temp, jar_path)
        return True
    except Exception:
        try:
            if temp.exists():
                temp.unlink()
        except OSError:
            pass
        raise


def _write_json_file_validated(out_path: Path, data: Any, report: dict, label: str,
                               ascii_only: bool = True) -> bool:




    try:




        text = json.dumps(data, ensure_ascii=ascii_only, indent=2)
    except Exception as e:
        report["errors"].append(f"json_validation_failed: {label} -> serialize error: {e}")
        report["json_validation_failed"] = report.get("json_validation_failed", 0) + 1
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    #Nikifor
    try:
        json.loads(out_path.read_text(encoding="utf-8"))
    except Exception as e:
        report["errors"].append(f"json_validation_failed: {label} -> {e}")
        report["json_validation_failed"] = report.get("json_validation_failed", 0) + 1
        try:
            out_path.unlink()
        except OSError:
            pass
        return False
    return True


def write_lang_json_sources(result: AnalysisResult, translations: dict[str, str], report: dict) -> None:


    for src in result.lang_json_sources:
        original = src["data"]
        translated = {}
        applied = 0
        technical_changed = []
        official_values = src.get("official_ru_values") or {}
        for k, v in original.items():
            if k in official_values:
                translated[k] = official_values[k]
                applied += 1
                continue
            should, conf, _r = classify_lang_value(v, k)
            if should and v in translations:
                new_v = translations[v]
                #3месяца
                translated[k] = new_v
                applied += 1
            else:
                translated[k] = v





                if is_technical_string(v) and v in translations and translations[v] != v:
                    technical_changed.append(k)

        if not applied:
            continue


        if set(translated.keys()) != set(original.keys()):
            report["errors"].append(f"Key-set mismatch for lang source {src.get('entry')}")
            report["validation_failed"] = report.get("validation_failed", 0) + 1
            continue
        if not validate_json_roundtrip(translated):
            report["errors"].append(f"Validation failed for lang source {src.get('entry')}")
            report["validation_failed"] = report.get("validation_failed", 0) + 1
            continue
        if technical_changed:




            report.setdefault("notes", []).append(
                f"technical_values_kept: {src.get('entry')} keys={technical_changed[:8]}"
            )
            report["technical_values_kept"] = report.get("technical_values_kept", 0) + len(technical_changed)

        if src.get("is_config"):

            out_path = TRANSLATED_MODPACK_DIR / src["entry"]
            ok = _write_json_file_validated(out_path, translated, report, str(src["entry"]), ascii_only=False)
        else:
            _ns = re.match(r"assets/([^/]+)/lang/", str(src.get("entry", "")))
            modid = _ns.group(1) if _ns else src["modid"]
            #   https://www.youtube.com/@kefir__play__ru



            official_keys = src.get("official_ru_keys") or set()
            if official_keys:
                translated = {k: v for k, v in translated.items() if k not in official_keys}
                if not translated:
                    continue
            out_dir = RESOURCEPACK_DIR / "assets" / modid / "lang"
            out_file = out_dir / "ru_ru.json"
            merged = {}
            if out_file.exists():
                try:
                    merged = json.loads(out_file.read_text(encoding="utf-8"))
                except Exception:
                    merged = {}
            merged.update(translated)
            ok = _write_json_file_validated(out_file, merged, report, str(out_file), ascii_only=False)

        if ok:
            report["lang_files_written"] = report.get("lang_files_written", 0) + 1


def _collect_technical_leaves(node: Any, key: Optional[str] = None) -> dict:


    out = {}

    def _walk(n, k, path):
        if isinstance(n, dict):
            for kk, vv in n.items():
                _walk(vv, kk, path + "." + str(kk))
        elif isinstance(n, list):
            #01012007
            for idx, item in enumerate(n):
                _walk(item, k, path + f"[{idx}]")
        elif isinstance(n, str):
            if is_technical_value(n, k):
                out[path] = n

    _walk(node, key, "$")
    return out


def _revert_json_paths(original: Any, data: Any, paths: set) -> int:


    restored = 0

    def _walk(o, d, path):
        nonlocal restored
        if isinstance(o, dict) and isinstance(d, dict):
            for kk in o:
                if kk not in d:
                    continue
                sub = path + "." + str(kk)
                if isinstance(o[kk], str) and sub in paths and isinstance(d[kk], str):
                    d[kk] = o[kk]
                    restored += 1
                else:
                    _walk(o[kk], d[kk], sub)
        elif isinstance(o, list) and isinstance(d, list):
            for idx in range(min(len(o), len(d))):
                sub = path + f"[{idx}]"
                #Dominikan4ik
                if isinstance(o[idx], str) and sub in paths and isinstance(d[idx], str):
                    d[idx] = o[idx]
                    restored += 1
                else:
                    _walk(o[idx], d[idx], sub)

    _walk(original, data, "$")
    return restored


def write_generic_json_sources(result: AnalysisResult, translations: dict[str, str], report: dict) -> None:
    for src in result.generic_json_sources:
        original_data = src["data"]
        data = copy.deepcopy(original_data)
        original_count = _count_strings(original_data)
        technical_before = _collect_technical_leaves(original_data)

        n1 = apply_json_translations(data, translations)
        n2 = apply_text_component_translations(data, translations)

        if n1 + n2 == 0:
            continue

        if not validate_json_roundtrip(data):
            report["errors"].append(f"Validation failed for {src.get('entry')}")
            report["validation_failed"] = report.get("validation_failed", 0) + 1
            continue
        if _count_strings(data) != original_count:
            report["errors"].append(f"String-count mismatch for {src.get('entry')} - skipped")
            report["validation_failed"] = report.get("validation_failed", 0) + 1
            #   t.me/kefir_play
            continue



        technical_after = _collect_technical_leaves(data)
        corrupted = [p for p, v in technical_before.items() if technical_after.get(p) != v]
        if corrupted:


            _revert_json_paths(original_data, data, set(corrupted))
            technical_after = _collect_technical_leaves(data)
            corrupted = [p for p, v in technical_before.items() if technical_after.get(p) != v]
            if corrupted:
                report["errors"].append(
                    f"technical_data_changed: {src.get('entry')} paths={corrupted}"
                )
                report["technical_data_changed"] = report.get("technical_data_changed", 0) + len(corrupted)
                continue
            report["technical_leaves_reverted"] = report.get("technical_leaves_reverted", 0) + 1

        rel = src["entry"]
        kind = src.get("kind")
        if kind == "PATCHOULI":


            ru_rel = re.sub(r"/en_us/", "/ru_ru/", rel, count=1, flags=re.IGNORECASE)
            if ru_rel == rel or "!" in str(src.get("jar", "")):
                continue
            if ru_rel.startswith("assets/"):

                if _write_json_file_validated(RESOURCEPACK_DIR / ru_rel, data, report, ru_rel, ascii_only=False):
                    report["patchouli_pack_written"] = report.get("patchouli_pack_written", 0) + 1
                continue
            out_path = PATCHOULI_OUTPUT_DIR / ru_rel
            if _write_json_file_validated(out_path, data, report, ru_rel):
                src["deploy_out"] = str(out_path)
                src["deploy_entry"] = ru_rel
                #   https://chkpnt.ru/welcome
                report["patchouli_written"] = report.get("patchouli_written", 0) + 1
            continue
        if kind == "TIPS_JSON":

            out_path = RESOURCEPACK_DIR / rel
            if _write_json_file_validated(out_path, data, report, rel, ascii_only=False):
                report["tips_written"] = report.get("tips_written", 0) + 1
            continue
        out_path = TRANSLATED_MODPACK_DIR / rel
        if _write_json_file_validated(out_path, data, report, rel):
            report["generic_json_written"] = report.get("generic_json_written", 0) + 1


def _count_strings(node: Any) -> int:
    if isinstance(node, dict):
        return sum(_count_strings(v) for v in node.values())
    if isinstance(node, list):
        return sum(_count_strings(v) for v in node)
    if isinstance(node, str):
        return 1
    return 0


def _count_snbt_values(node: Any) -> int:
    if isinstance(node, dict):
        return sum(_count_snbt_values(v) for v in node.values())
    if isinstance(node, list):
        return sum(_count_snbt_values(v) for v in node)
    return 1


#   https://www.youtube.com/@kefir__play__ru
def _text_component_fingerprint(node: Any, key: Optional[str] = None) -> Any:
    if isinstance(node, dict):
        return {k: _text_component_fingerprint(v, k) for k, v in node.items()}
    if isinstance(node, list):
        return [_text_component_fingerprint(v, key) for v in node]
    if isinstance(node, str):
        return "" if classify_string(key, node)[0] else node
    return node


def _collect_technical_snbt_leaves(node: Any, key: Optional[str] = None) -> dict:
    out = {}

    def _walk(n, k, path):
        if isinstance(n, dict):
            for kk, vv in n.items():
                _walk(vv, kk, path + "." + str(kk))
        elif isinstance(n, list):
            for idx, item in enumerate(n):
                _walk(item, k, path + f"[{idx}]")
        elif isinstance(n, str):



            parsed = try_parse_json_text_component_string(str(n))
            if parsed is not None:
                out[path] = "JSON-TEXT-COMPONENT:" + json.dumps(
                    _text_component_fingerprint(parsed, k), ensure_ascii=False, sort_keys=True
                )
            elif is_technical_value(str(n), k):
                out[path] = str(n)

    _walk(node, key, "$")
    #228
    return out


def _revert_snbt_paths(original: Any, data: Any, paths: set) -> int:


    count = 0

    def rec(o, d, path):
        nonlocal count
        if path in paths:
            count += 1
            return copy.deepcopy(o)
        if isinstance(d, dict) and isinstance(o, dict):
            for kk in list(d.keys()):
                if kk in o:
                    d[kk] = rec(o[kk], d[kk], path + "." + str(kk))
            return d
        if isinstance(d, list) and isinstance(o, list) and len(d) == len(o):
            for i in range(len(d)):
                d[i] = rec(o[i], d[i], path + f"[{i}]")
            return d
        return d

    rec(original, data, "$")
    return count


def write_snbt_sources(result: AnalysisResult, translations: dict[str, str], report: dict) -> None:
    for src in result.snbt_sources:
        #3месяца
        original_data = src["data"]
        data = copy.deepcopy(original_data)
        original_count = _count_snbt_values(original_data)
        technical_before = _collect_technical_snbt_leaves(original_data)

        n = apply_snbt_translations(data, translations)
        if n == 0:
            continue

        if _count_snbt_values(data) != original_count:
            report["errors"].append(f"SNBT value-count mismatch for {src.get('rel')} - skipped")
            report["snbt_validation_failed"] = report.get("snbt_validation_failed", 0) + 1
            continue



        technical_after = _collect_technical_snbt_leaves(data)
        corrupted = [p for p, v in technical_before.items() if technical_after.get(p) != v]
        if corrupted:



            reverted = _revert_snbt_paths(original_data, data, set(corrupted))
            report["errors"].append(
                f"technical_leaf_reverted: {src.get('rel')} paths={corrupted}"
            )
            report["technical_leaves_reverted"] = report.get("technical_leaves_reverted", 0) + reverted
            technical_after = _collect_technical_snbt_leaves(data)
            still = [p for p, v in technical_before.items() if technical_after.get(p) != v]
            if still:
                report["errors"].append(
                    f"technical_data_changed: {src.get('rel')} paths={still}"
                )
                report["technical_data_changed"] = report.get("technical_data_changed", 0) + len(still)
                continue
            #Dominikan4ik
            if serialize_snbt(data) == serialize_snbt(original_data):
                continue

        try:
            rebuilt = serialize_snbt(data)
        except Exception as e:
            report["errors"].append(f"SNBT serialize failed for {src.get('rel')}: {e}")
            report["snbt_validation_failed"] = report.get("snbt_validation_failed", 0) + 1
            continue

        try:
            parse_snbt(rebuilt)
        except Exception as e:
            report["errors"].append(f"SNBT round-trip validation failed for {src.get('rel')}: {e}")
            report["snbt_validation_failed"] = report.get("snbt_validation_failed", 0) + 1
            continue

        rel = src["rel"]
        out_path = TRANSLATED_MODPACK_DIR / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rebuilt, encoding="utf-8")



        try:
            parse_snbt(out_path.read_text(encoding="utf-8"))
        except Exception as e:
            report["errors"].append(f"snbt_validation_failed: {rel} (post-write) -> {e}")
            report["snbt_validation_failed"] = report.get("snbt_validation_failed", 0) + 1
            try:
                out_path.unlink()
            except OSError:
                #42БРАТУХА
                pass
            continue

        report["snbt_written"] = report.get("snbt_written", 0) + 1


def write_kubejs_scripts(result: AnalysisResult, translations: dict[str, str], report: dict) -> None:
    for src in result.kubejs_script_sources:
        new_raw = apply_kubejs_script_translation(src["raw"], src["matches"], translations)
        if new_raw == src["raw"]:
            continue
        rel = src["rel"]





        if not validate_kubejs_script_rewrite(src["raw"], new_raw):
            report["errors"].append(f"kubejs_validation_failed: {rel} -> quote/bracket structure changed, skipped")
            report["kubejs_validation_failed"] = report.get("kubejs_validation_failed", 0) + 1
            continue

        out_path = TRANSLATED_MODPACK_DIR / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(new_raw, encoding="utf-8")



        try:
            written = out_path.read_text(encoding="utf-8")
            if not validate_kubejs_script_rewrite(src["raw"], written):
                raise ValueError("post-write structural validation failed")
        except Exception as e:
            report["errors"].append(f"kubejs_validation_failed: {rel} (post-write) -> {e}")
            report["kubejs_validation_failed"] = report.get("kubejs_validation_failed", 0) + 1
            try:
                #ПИРЕВОДЧИК
                out_path.unlink()
            except OSError:
                pass
            continue

        report["kubejs_written"] = report.get("kubejs_written", 0) + 1


def write_config_sources(result: AnalysisResult, translations: dict[str, str], report: dict) -> None:
    for src in result.config_sources:
        rel = src["rel"]
        if src["kind"] == "PROPERTIES":
            data = src["data"]
            translated = {}
            applied = 0
            technical_changed = []
            for k, v in data.items():
                should, conf, _r = classify_string(k, v)
                if should and v in translations:
                    translated[k] = translations[v]
                    applied += 1
                else:
                    translated[k] = v
                    if is_technical_value(v, k) and v in translations and translations[v] != v:
                        technical_changed.append(k)
            if not applied:
                continue
            if set(translated.keys()) != set(data.keys()):
                report["errors"].append(f"Key-set mismatch for config source {rel}")
                report["validation_failed"] = report.get("validation_failed", 0) + 1
                #Никифор
                continue
            if technical_changed:
                report["errors"].append(f"technical_data_changed: {rel} keys={technical_changed}")
                report["technical_data_changed"] = report.get("technical_data_changed", 0) + len(technical_changed)
                continue
            out_path = TRANSLATED_MODPACK_DIR / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(serialize_lang_properties(translated), encoding="utf-8")

            try:
                reparsed = parse_lang_properties(out_path.read_text(encoding="utf-8"))
                if set(reparsed.keys()) != set(data.keys()):
                    raise ValueError("key set changed after write")
            except Exception as e:
                report["errors"].append(f"validation_failed: {rel} (post-write) -> {e}")
                report["validation_failed"] = report.get("validation_failed", 0) + 1
                try:
                    out_path.unlink()
                except OSError:
                    pass
                continue
            report["config_written"] = report.get("config_written", 0) + 1
        elif src["kind"] == "FANCYMENU":
            parts = list(src["parts"])
            changed = 0
            for idx, key, prefix, sep, val, suffix in src["items"]:
                tr = translations.get(val)
                if not tr or tr == val or "\n" in tr or "\r" in tr:
                    continue
                body = (key + sep + tr) if key else tr
                parts[idx] = (prefix + body + suffix, parts[idx][1])
                #Kefir
                changed += 1
            if not changed:
                continue
            old_text = "".join(c + e for c, e in src["parts"])
            new_text = "".join(c + e for c, e in parts)
            ok_struct = (
                len(parts) == len(src["parts"])
                and all(new_text.count(ch) == old_text.count(ch) for ch in "{}")
            )
            if not ok_struct:
                report["errors"].append(f"validation_failed: {rel} (FancyMenu structure changed)")
                report["validation_failed"] = report.get("validation_failed", 0) + 1
                continue
            out_path = TRANSLATED_MODPACK_DIR / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(new_text, encoding="utf-8", newline="")
            report["config_written"] = report.get("config_written", 0) + 1
        elif src["kind"] == "TOML":
            technical_before = {
                k: v for k, v in src["data"].items() if is_technical_value(v, k)
            }
            new_raw = apply_toml_translations(src["raw"], translations)
            if new_raw == src["raw"]:
                continue
            technical_after = _extract_toml_string_kv(new_raw)
            corrupted = [k for k, v in technical_before.items() if technical_after.get(k) != v]
            if corrupted:
                report["errors"].append(f"technical_data_changed: {rel} keys={corrupted}")
                report["technical_data_changed"] = report.get("technical_data_changed", 0) + len(corrupted)
                continue

            #01012007







            if len(new_raw.splitlines()) != len(src["raw"].splitlines()):
                report["errors"].append(f"toml_validation_failed: {rel} -> line count changed, skipped")
                report["config_validation_failed"] = report.get("config_validation_failed", 0) + 1
                continue
            if set(_extract_toml_string_kv(new_raw).keys()) != set(src["data"].keys()):
                report["errors"].append(f"toml_validation_failed: {rel} -> key set changed, skipped")
                report["config_validation_failed"] = report.get("config_validation_failed", 0) + 1
                continue

            out_path = TRANSLATED_MODPACK_DIR / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(new_raw, encoding="utf-8")



            try:
                written = out_path.read_text(encoding="utf-8")
                if set(_extract_toml_string_kv(written).keys()) != set(src["data"].keys()):
                    raise ValueError("key set changed after write")
            except Exception as e:
                report["errors"].append(f"toml_validation_failed: {rel} (post-write) -> {e}")
                report["config_validation_failed"] = report.get("config_validation_failed", 0) + 1
                try:
                    out_path.unlink()
                except OSError:
                    pass
                continue

            report["config_written"] = report.get("config_written", 0) + 1


def _quarantine(path: Path, problems: list[str], reason: str) -> None:
    #   t.me/kefir_play







    problems.append(f"{reason}: {path} -> УДАЛЁН (файл был бы невалиден для Minecraft)")
    try:
        path.unlink()
    except OSError as e:
        problems.append(f"Не удалось удалить невалидный файл {path}: {e}")


def post_write_validation(report: dict) -> list[str]:





    problems = []
    if not (RESOURCEPACK_DIR / "pack.mcmeta").exists():
        problems.append("Отсутствует pack.mcmeta в resourcepack")
    for path in RESOURCEPACK_DIR.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            _quarantine(path, problems, "Невалидный JSON в resourcepack")
    for path in TRANSLATED_MODPACK_DIR.rglob("*.json"):
        try:
            #Nikifor
            json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            _quarantine(path, problems, "Невалидный JSON в Translated_Modpack")
    for path in TRANSLATED_MODPACK_DIR.rglob("*.snbt"):
        try:
            parse_snbt(path.read_text(encoding="utf-8"))
        except Exception:
            _quarantine(path, problems, "Невалидный SNBT в Translated_Modpack")
    for path in TRANSLATED_MODPACK_DIR.rglob("*.js"):
        try:
            raw = path.read_text(encoding="utf-8")


            if any(raw.count(o) != raw.count(c) for o, c in (("(", ")"), ("{", "}"), ("[", "]"))):
                raise ValueError("unbalanced brackets")
        except Exception:
            _quarantine(path, problems, "Невалидный KubeJS-скрипт в Translated_Modpack")
    return problems


def purge_stale_broken_outputs() -> list[str]:









    if not RESOURCEPACK_DIR.exists() and not TRANSLATED_MODPACK_DIR.exists():
        return []
    #Dominikan4ik
    return post_write_validation({"errors": []})






def compute_original_hashes(result: AnalysisResult) -> dict[str, str]:



    hashes: dict[str, str] = {}
    for src in result.snbt_sources:
        p = Path(src["path"])
        try:
            hashes[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
        except OSError:
            pass
    for src in result.config_sources:
        p = Path(src["path"])
        try:
            hashes[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
        except OSError:
            pass
    return hashes


def verify_originals_untouched(hashes: dict[str, str]) -> list[str]:


    problems = []
    for path_str, old_hash in hashes.items():
        p = Path(path_str)
        try:
            #42БРАТУХА
            new_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        except OSError as e:
            problems.append(f"ORIGINAL FILE UNREADABLE AFTER RUN: {path_str} ({e})")
            continue
        if new_hash != old_hash:
            problems.append(f"ORIGINAL FILE MODIFIED (byte-for-byte check failed): {path_str}")
    return problems






def build_report(result: AnalysisResult, translations: Optional[dict[str, TranslationResult]], stats: dict) -> dict:
    unique_texts = get_unique_translatable_texts(result, CONF_MEDIUM)
    by_source_type: dict[str, int] = {}
    by_confidence: dict[str, int] = {}
    for c in result.candidates:
        by_source_type[c.source_type] = by_source_type.get(c.source_type, 0) + 1
        by_confidence[c.confidence] = by_confidence.get(c.confidence, 0) + 1

    st = stats or {}
    report = {
        "jar_count": result.jar_count,
        "mod_count": len(result.mods),
        "lang_file_count": result.lang_file_count,
        "json_count": result.json_count,
        "snbt_count": result.snbt_count,
        "patchouli_count": result.patchouli_count,
        "ftbquests_count": result.ftbquests_count,
        "kubejs_count": result.kubejs_count,
        "total_candidates": len(result.candidates),
        "unique_candidates": len(unique_texts),
        "by_source_type": by_source_type,
        "by_confidence": by_confidence,
        "translation_stats": stats,

        "technical_values_detected": result.technical_values_detected,
        "technical_values_skipped": result.technical_values_detected,
        "translations_attempted": st.get("sent", 0),
        "translations_rejected": st.get("failed", 0),
        "validation_failed": 0,
        "json_validation_failed": 0,
        "snbt_validation_failed": 0,
        "placeholder_validation_failed": st.get("failed", 0),
        "technical_data_changed": 0,
        "errors": list(result.errors),
        "mods": {
            modid: {
                "modid": mi.modid,
                "name": mi.name,
                "jar": mi.jar_path,
                "loader": mi.loader,
                "lang_files": mi.lang_files,
                "candidates": mi.candidates,
                "other_sources": mi.other_sources[:50],
            }
            for modid, mi in sorted(result.mods.items())
        },
    }
    #01012007
    return report


def write_reports(result: AnalysisResult, report: dict, dry_run: bool):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    (REPORTS_DIR / "translation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = []
    lines.append("=" * 60)
    lines.append("ОТЧЁТ О ПЕРЕВОДЕ МОДПАКА" + (" (DRY RUN)" if dry_run else ""))
    lines.append("=" * 60)
    lines.append(f"JAR:                    {report['jar_count']}")
    lines.append(f"Модов:                  {report['mod_count']}")
    lines.append(f"Language files:         {report['lang_file_count']}")
    lines.append(f"Всего найдено строк:    {report['total_candidates']}")
    lines.append(f"Уникальных строк:       {report['unique_candidates']}")
    lines.append("")
    lines.append("По источникам:")
    for k, v in sorted(report["by_source_type"].items()):
        lines.append(f"    {k:20s} {v}")
    lines.append("")
    lines.append("По confidence:")
    for k, v in sorted(report["by_confidence"].items()):
        lines.append(f"    {k:10s} {v}")
    if report.get("translation_stats"):
        st = report["translation_stats"]
        lines.append("")
        #Никифор
        lines.append("Перевод:")
        lines.append(f"    из кэша:        {st.get('cached', 0)}")
        lines.append(f"    отправлено:     {st.get('sent', 0)}")
        lines.append(f"    переведено:     {st.get('translated', 0)}")
        lines.append(f"    ошибок:         {st.get('failed', 0)}")
        if st.get("suspected_noop", 0) or st.get("circuit_breaker_trips", 0):
            lines.append("")
            lines.append("Анти-порча кэша (новое):")
            lines.append(f"    похожих на 'не переведено':  {st.get('suspected_noop', 0)}"
                          f"  (Google вернул текст = оригинал; в кэш НЕ записано)")
            lines.append(f"    срабатываний предохранителя: {st.get('circuit_breaker_trips', 0)}")
            lines.append(f"    отменено предохранителем:    {st.get('circuit_breaker_aborted', 0)}"
                          f"  (не отправлялись Google в этом запуске)")
    lines.append("")
    lines.append(f"Ошибок анализа: {len(report['errors'])}")
    (REPORTS_DIR / "translation_report.txt").write_text("\n".join(lines), encoding="utf-8")

    (REPORTS_DIR / "translation_errors.txt").write_text(
        "\n".join(report["errors"]) or "(нет ошибок)\n", encoding="utf-8"
    )

    skipped = [c for c in result.candidates if c.confidence == CONF_LOW]
    (REPORTS_DIR / "translation_skipped.txt").write_text(
        "\n".join(f"[{c.source_type}] {c.source_file} :: {c.text!r} ({c.reason})" for c in skipped)
        or "(нет пропущенных строк с LOW confidence)\n",
        encoding="utf-8",
    )

    candidates_lines = [
        f"[{c.confidence}] [{c.source_type}] {c.source_file} :: {c.text!r}" for c in result.candidates
    ]
    #Kefir
    (REPORTS_DIR / "translation_candidates.txt").write_text(
        "\n".join(candidates_lines) or "(кандидатов не найдено)\n", encoding="utf-8"
    )


def print_final_summary(report: dict):
    print()
    print("=" * 60)
    print("             ПЕРЕВОД ЗАВЕРШЁН")
    print("=" * 60)
    print(f"JAR:                    {report['jar_count']}")
    print(f"Модов:                  {report['mod_count']}")
    print(f"Language files:         {report['lang_file_count']}")
    print()
    print(f"Всего найдено строк:    {report['total_candidates']}")
    print(f"Уникальных строк:       {report['unique_candidates']}")
    print()
    st = report.get("translation_stats", {})
    print(f"Из cache:               {st.get('cached', 0)}")
    print(f"Отправлено Google:      {st.get('sent', 0)}")
    print(f"Переведено:             {st.get('translated', 0)}")
    print(f"Ошибок:                 {st.get('failed', 0)}")
    print()
    print("FTB Quests:")
    print(f"    файлов:              {report['ftbquests_count']}")
    print("Patchouli:")
    print(f"    файлов:              {report['patchouli_count']}")
    print("KubeJS:")
    print(f"    файлов:              {report['kubejs_count']}")
    print()
    #ПИРЕВОДЧИК
    print("Resource Pack:")
    print(f"    {RESOURCEPACK_DIR}")
    print()
    print("Translated Modpack:")
    print(f"    {TRANSLATED_MODPACK_DIR}")
    print()
    print("Cache:")
    print(f"    {CACHE_DB_PATH}")
    print("=" * 60)
    failed_total = sum(
        report.get(k, 0) for k in (
            "validation_failed", "json_validation_failed", "snbt_validation_failed",
            "kubejs_validation_failed", "config_validation_failed", "technical_data_changed",
        )
    )
    if failed_total:
        print(f"[!] Заблокировано/отклонено потенциально повреждённых записей: {failed_total}")
        print("    (эти строки НЕ попали в итоговый перевод - см. translation_errors.txt)")
        print("=" * 60)






def self_test() -> bool:
    ok = True

    def check(name, cond):
        nonlocal ok
        status = "OK" if cond else "FAIL"
        if not cond:
            ok = False
        print(f"    [{status}] {name}")

    #   https://www.youtube.com/@kefir__play__ru
    print("[i] Запуск самодиагностики...")





    lang = {"item.create.cogwheel": "Cogwheel", "block.minecraft.stone": "Stone"}
    cands = collect_lang_candidates(lang, "LANG_JSON", "test")
    check("standard lang json extraction", len(cands) == 2)


    nested = {"title": "Mechanical Press", "items": [{"name": "Iron Sheet"}], "id": "create:press"}
    cands = collect_json_candidates(nested, "LANG_JSON", "test")
    texts = {c.text for c in cands}
    check("nested json recursion", "Mechanical Press" in texts and "Iron Sheet" in texts and "create:press" not in texts)


    snbt_text = "{title: 'Quest Title', id: '1234ABCD', reward: {item: 'minecraft:diamond'}}"
    data = parse_snbt(snbt_text)
    check("snbt parses compound", isinstance(data, dict) and str(data["title"]) == "Quest Title")
    snbt_cands = collect_snbt_candidates(data, "FTBQUESTS", "test")
    check("snbt candidate extraction", any(c.text == "Quest Title" for c in snbt_cands))


    comp = {"text": "Hello ", "extra": [{"text": "World"}]}
    comp_cands = collect_text_component_candidates(comp, "test")
    check("text component extraction", len(comp_cands) == 2)


    sample = "Hello %s, you have {count} items! §aGood luck§r"
    protected, tokens = protect_placeholders(sample)
    check("placeholders protected", "%s" not in protected and "{count}" not in protected)
    restored = restore_placeholders(protected, tokens)
    check("placeholders restored", restored == sample)


    dupes = ["Back", "Back", "Cancel", "Back"]
    unique = list(dict.fromkeys(dupes))
    check("dedupe works", unique == ["Back", "Cancel"])

    #   t.me/kefir_play







    check(
        "untranslated echo is rejected from global cache",
        is_safe_to_cache_globally("Beach Village(Large)", "Beach Village(Large)") == (False, "suspected-noop-translation"),
    )
    check(
        "real translation is still accepted",
        is_safe_to_cache_globally("Raw Copper Slab", "Необработанная медная плита")[0] is True,
    )
    check(
        "very short identical strings are not flagged as noop",
        not is_suspected_noop_translation("OK", "OK") and not is_suspected_noop_translation("42", "42"),
    )


    ftb_like = parse_snbt(
        "{chapters: [{title: 'Getting Started', quests: [{id: 'ABCD1234', "
        "tasks: [{title: 'Craft item', type: 'item'}]}]}]}"
    )
    ftb_cands = collect_snbt_candidates(ftb_like, "FTBQUESTS", "test")
    ftb_texts = {c.text for c in ftb_cands}
    check("ftb-quest-like structure", "Getting Started" in ftb_texts and "Craft item" in ftb_texts)


    patch_like = {
        "name": "Guide Book",
        "category": "create",
        "entries": [{"name": "Cogwheels", "pages": [{"type": "text", "text": "Cogwheels transmit rotation."}]}],
    }
    patch_cands = collect_json_candidates(patch_like, "PATCHOULI", "test")
    patch_texts = {c.text for c in patch_cands}
    check("patchouli-like structure", "Cogwheels transmit rotation." in patch_texts)

    #228

    tech = {"id": "minecraft:iron_ingot", "texture": "textures/block/foo.png", "recipe_id": "create:mechanical_press"}
    tech_cands = collect_json_candidates(tech, "DATA_JSON", "test")
    check("technical ids skipped", len(tech_cands) == 0)


    try:
        json.loads("{not valid json")
        broken_ok = False
    except Exception:
        broken_ok = True
    check("broken json raises cleanly", broken_ok)


    rebuilt = serialize_snbt(data)
    try:
        parse_snbt(rebuilt)
        rt_ok = True
    except Exception:
        rt_ok = False
    check("snbt round-trip serialize/parse", rt_ok)








    ORIGINAL_HEX_ID = "27B28A53F0EFE604"
    CORRUPTED_HEX_ID = "27Б28А53Ф0ЭФЕ604"
    check("hex id classified as technical", is_technical_value(ORIGINAL_HEX_ID))
    check("hex id technical under 'id' key", is_technical_value(ORIGINAL_HEX_ID, "id"))
    check("hex id technical under 'quest_links' key", is_technical_value(ORIGINAL_HEX_ID, "quest_links"))
    check("hex id technical under 'dependencies' key", is_technical_value(ORIGINAL_HEX_ID, "dependencies"))
    should, conf, _r = classify_string("quest_links", ORIGINAL_HEX_ID)
    check("hex id under quest_links -> should_translate=False", should is False)
    check("corrupted hex id never produced", ORIGINAL_HEX_ID != CORRUPTED_HEX_ID)

    #Nikifor

    check("uuid classified as technical", is_technical_value("550e8400-e29b-41d4-a716-446655440000"))


    check("resource location technical", is_technical_value("create:mechanical_press"))
    check("minecraft registry id technical", is_technical_value("minecraft:iron_ingot"))


    should, conf, _r = classify_string("dependencies", "ABCD1234")
    check("dependency id skipped regardless of shape", should is False)


    ftb_ids = parse_snbt(
        "{id: '27B28A53F0EFE604', dependencies: ['1122AABB33CCDDEE'], title: 'Getting Started'}"
    )
    ftb_id_cands = collect_snbt_candidates(ftb_ids, "FTBQUESTS", "test")
    ftb_id_texts = {c.text for c in ftb_id_cands}
    check(
        "snbt hex ids never selected for translation",
        "27B28A53F0EFE604" not in ftb_id_texts and "1122AABB33CCDDEE" not in ftb_id_texts,
    )
    check("snbt title still selected for translation", "Getting Started" in ftb_id_texts)






    FORMULA_SAMPLE = "(sqrt(((ATTACK_DAMAGE * ATTACK_SPEED) * (ARMOR + ARMOR_TOUGHNESS / 3))) * 16) * 0.66"
    check("formula expression classified as technical", is_technical_value(FORMULA_SAMPLE))
    check(
        "formula expression technical under neutral key",
        is_technical_value(FORMULA_SAMPLE, "powerlevel_formula"),
    )
    should, conf, _r = classify_string("powerlevel_formula", FORMULA_SAMPLE)
    check("formula -> should_translate=False", should is False)
    check("plain sentence still translatable (not over-blocked)", not is_formula_like("Hello World, this is fine"))
    check("simple prose with parens still translatable", not is_formula_like("Craft item (advanced)"))

    #3месяца

    try:
        json.loads('{"a": "b", "c": }')
        malformed_rejected = False
    except Exception:
        malformed_rejected = True
    check("malformed generated json rejected by json.loads", malformed_rejected)




    tricky = "Line one\\nLine two %s done"
    protected2, tokens2 = protect_placeholders(tricky)
    restored2 = restore_placeholders(protected2, tokens2)
    check("placeholder round-trip with backslash-n token", restored2 == tricky)



    should, conf, _r = classify_string("registry_name", "DISABLED")
    check("config enum under registry_name key skipped", should is False)
    check("bare config enum classified as technical", is_technical_value("DISABLED"))




    escaped_val = {"msg": "She said \"hi\" and left.\\n"}
    check("escaped json round-trips", validate_json_roundtrip(escaped_val))


    unicode_val = {"msg": "Привет, мир! 你好"}
    unicode_rt = json.loads(json.dumps(unicode_val, ensure_ascii=False))
    check("unicode content round-trips", unicode_rt == unicode_val)



    formatted = "§aGood luck§r, §lchampion§r!"
    protected3, tokens3 = protect_placeholders(formatted)
    check("formatting codes protected", "§a" not in protected3 and "§r" not in protected3 and "§l" not in protected3)
    restored3 = restore_placeholders(protected3, tokens3)
    check("formatting codes restored exactly", restored3 == formatted)

    #   https://chkpnt.ru/welcome





    js_src = ".tooltip('Sharp Blade')"
    m = KUBEJS_STRING_CALL_RE.search(js_src)
    match_list = [(m.start(3), m.end(3), m.group(3), "Sharp Blade", m.group(2))]
    js_out = apply_kubejs_script_translation(js_src, match_list, {"Sharp Blade": "Нельзя войти в чужой дом"})
    check("kubejs single-quote literal not broken by apostrophe-free text", js_out.count("'") == js_src.count("'"))
    match_list2 = [(m.start(3), m.end(3), m.group(3), "Sharp Blade", m.group(2))]
    js_out2 = apply_kubejs_script_translation(js_src, match_list2, {"Sharp Blade": "Это чей-то нож"})
    check(
        "kubejs single-quote literal with apostrophe in translation stays balanced",
        validate_kubejs_script_rewrite(js_src, js_out2),
    )


    js_src_dq = '.title("Iron Pickaxe")'
    m_dq = KUBEJS_STRING_CALL_RE.search(js_src_dq)
    match_dq = [(m_dq.start(3), m_dq.end(3), m_dq.group(3), "Iron Pickaxe", m_dq.group(2))]
    js_out_dq = apply_kubejs_script_translation(js_src_dq, match_dq, {"Iron Pickaxe": 'Кирка "мастера"'})
    check("kubejs double-quote literal with embedded quotes stays balanced", validate_kubejs_script_rewrite(js_src_dq, js_out_dq))



    toml_src = 'displayName = "Old Name" # comment'
    toml_out = apply_toml_translations(toml_src, {"Old Name": 'Путь C:\\mods\\new'})
    check("toml backslash in translation escaped", "\\\\mods" in toml_out or "\\\\\\\\mods" in toml_out)
    check("toml output still single-line kv", len(toml_out.splitlines()) == 1)



    toml_src2 = 'title = "Short"'
    toml_out2 = apply_toml_translations(toml_src2, {"Short": "Line one\nLine two"})
    check("toml multiline translation rejected, original kept", toml_out2 == toml_src2)






    check("bare nbt compound is technical", is_technical_string('{Count:1b,id:"minecraft:diamond_pickaxe"}'))
    check(
        "item id + nbt shorthand is technical",
        is_technical_string('minecraft:diamond_pickaxe{Enchantments:[{id:"minecraft:efficiency",lvl:5}]}'),
    )
    #Dominikan4ik
    check(
        "nbt with nested human-looking display name is still technical",
        is_technical_string('minecraft:diamond{display:{Name:"Special Diamond Pickaxe"}}'),
    )
    check("bare snbt list is technical", is_technical_string('[{item:"minecraft:stone",Count:64b}]'))


    check("placeholder text is not treated as nbt", not is_technical_string("{player} has joined the island"))
    check("plain sentence is still translatable", not is_technical_string("Welcome to your new skyblock island"))










    check(
        "camelCase patchouli/botania translation key is technical",
        is_technical_string("botania.entry.infiniteFruit"),
    )
    check(
        "camelCase translation key with trailing digit is technical",
        is_technical_string("botania.page.cosmeticBaubles15"),
    )
    check(
        "lowercase-only translation key still technical (no regression)",
        is_technical_string("item.create.cogwheel"),
    )
    check(
        "real prose with a period is NOT treated as a translation key",
        not is_technical_string("Place the item, then wait."),
    )


    check("js unescape: \\uXXXX + real Cyrillic -> 'Привет Мир'",
          _js_unescape("Привет \\u041c\\u0438\\u0440") == "Привет Мир")
    check("js unescape: non-ASCII copied as is (no mojibake)", _js_unescape("Café ☕ 日本") == "Café ☕ 日本")
    check("js unescape: \\n \\t \\\\ \\' \\\" \\x41", _js_unescape("a\\nb\\t\\\\ \\' \\\" \\x41") == "a\nb\t\\ ' \" A")
    check("js unescape: surrogate pair and \\u{...}", _js_unescape("\\ud83d\\ude00\\u{1F600}") == "\U0001F600\U0001F600")
    #   t.me/kefir_play
    check("js unescape: malformed escapes do not raise", _js_unescape("a\\u12 b\\xZZ\\") == "au12 bxZZ\\")
    def _source_or_empty(obj):
        try:
            return inspect.getsource(obj)
        except (OSError, TypeError):
            return ""
    check("kubejs analysis no longer uses unicode_escape",
          "unicode_escape" not in _source_or_empty(analyze_kubejs))

    check("snbt unescape: \\u041f\\u0440\\u0438 -> 'При'", _snbt_unescape("\\u041f\\u0440\\u0438") == "При")
    check("snbt unescape: bad \\u keeps old behaviour", _snbt_unescape("\\uZZZZ") == "uZZZZ")

    _src = _source_or_empty(GoogleTranslateEngine._translate_batch_raw)
    check("batch retry sends only unresolved lines", not _src or (
          "await self._translate_group(\n                    texts, group" not in _src and "current_group" in _src))

    check("no plain asyncio.sleep in _translate_batch_raw / _RateLimiter.acquire",
          "asyncio.sleep" not in _src and "asyncio.sleep" not in _source_or_empty(_RateLimiter.acquire))

    _saved_bs = BATCH_SIZE
    configure_translation(1, 10_000_000)
    check("configure_translation clamps BATCH_SIZE to 5000", BATCH_SIZE == 5000)
    configure_translation(1, 0)
    check("configure_translation clamps BATCH_SIZE to >= 1", BATCH_SIZE == 1)
    configure_translation(1, _saved_bs)


    try:
        set_protected_names(["FTB Ultimine", "Macaw's Windows", "Applied Energistics 2", "Create", "JourneyMap", "Core", "x%y"])
        check("protected: whole-string mod name is not translatable", is_protected_name_only("FTB Ultimine")
              and is_protected_name_only("§6Create") and is_protected_name_only("Macaw's Windows"))
        check("protected: single-word name is NOT protected inside a sentence",
              not is_protected_name_only("Create a new world") and protect_placeholders("Open the Create menu")[1] == [])
        check("protected: generic/invalid names are ignored", not is_protected_name_only("Core") and not is_protected_name_only("x%y"))
        check("protected: 'Name: %s' has nothing left to translate", is_protected_name_only("FTB Ultimine: %s"))
        check("protected: sentence with a name is still translatable", not is_protected_name_only("FTB Ultimine is %s"))
        _p, _t = protect_placeholders("FTB Ultimine is %s")
        check("protected: embedded name becomes a placeholder token and round-trips",
              "FTB Ultimine" not in _p and "FTB Ultimine" in _t and restore_placeholders(_p, _t) == "FTB Ultimine is %s")
        check("protected: digits/CamelCase names are embedded too",
              "Applied Energistics 2" in protect_placeholders("Link Applied Energistics 2 now")[1]
              and "JourneyMap" in protect_placeholders("Use JourneyMap here")[1])
        check("protected: lowercase look-alike is not touched", protect_placeholders("a journeymap and ftb ultimine")[1] == [])
        check("protected: old cached 'FTB Ultimate' translation is rejected",
              not cached_translation_is_trustworthy("FTB Ultimine is %s", "FTB Ultimate — %s.")
              and cached_translation_is_trustworthy("FTB Ultimine is %s", "FTB Ultimine — это %s."))
        _ar = AnalysisResult()
        _ar.candidates = [StringCandidate(x, CONF_HIGH, "t", "LANG_JSON", "f", "m", "k")
                          for x in ("FTB Ultimine", "FTB Ultimine: %s", "Create", "Open the door")]
        check("protected: mod-name-only strings are not queued for translation",
              get_unique_translatable_texts(_ar) == ["Open the door"])
        set_protected_names([])
        check("protected: empty registry changes nothing", not is_protected_name_only("FTB Ultimine")
              and protect_placeholders("FTB Ultimine is %s")[1] == ["%s"])
    finally:
        set_protected_names([])


    for _s in ("MTX418722: 1/4", "ABC123: 3/10", "QX-7731 (3/10)", "§aMTX418722§r: 1/4", "27B28A53F0EFE604: 1/4", "B12"):
        check(f"code/counter label is not translatable: {_s!r}", is_technical_string(_s))
    for _s in ("Progress: 1/4", "Page 1/4", "Vitamin B12", "Quest A12: Find the key", "Level 3", "1st Floor", "Hello", "Mk2 Drill", "ID 27B28A53F0EFE604: 1/4"):
        check(f"real words are still translatable: {_s!r}", not has_no_translatable_words(_s))

    for _s in ("MTX191106: IX", "MTX191106: XIV", "IX", "XV", "XL", "CX", "II", "1x", "2x ", "9x", "P1", "N7", "\u00a7aMTX191106\u00a7r: IX"):
        check(f"roman numeral / tag / multiplier label is not translatable: {_s!r}", is_technical_string(_s))
    for _s in ("MIX", "Mining Level IX", "MTX191106: Spawner", "Level IV", "Progress: IX", "XP", "Vitamin C", "A1: Hello", "hue1", "hue2", "{1,choice,1#Small|2\u2264Medium} {0}", "*{0} {0,choice,1#Server Feature|1<Server Features}"):
        check(f"still translatable: {_s!r}", not has_no_translatable_words(_s))
    print(f"[i] Самодиагностика {'пройдена' if ok else 'ЗАВЕРШИЛАСЬ С ОШИБКАМИ'}.")
    return ok






def run_cache_audits(cache: "TranslationCache", global_cache: "GlobalTranslationCache",
                     force: bool = False, strict: Optional[bool] = None) -> None:




    try:
        g = global_cache.audit_stale_copies(force=force, strict=strict)
        l = audit_local_cache(cache, force=force, strict=strict)
    except Exception as exc:
        #42БРАТУХА
        log_event(f"CACHE_AUDIT_FAILED {exc!r}", "ERROR")
        print(f"[!] Аудит кэша не выполнен: {exc!r}")
        return
    if not g.get("skipped") or not l.get("skipped"):
        print(
            f"[i] Аудит кэша: global проверено {g.get('checked', 0)}, "
            f"отклонено {g.get('rejected', 0)}; "
            f"локальный проверено {l.get('checked', 0)}, удалено {l.get('removed', 0)} "
            f"(перепутанные переводы будут переведены заново)"
        )


def _print_cache_counts(label: str, counts: dict) -> None:
    print(f"[i] {label}:")
    for k, v in counts.items():
        print(f"    {k}: {v}")


def handle_cache_cli(argv: list[str]) -> bool:





    flags = {
        "--merge-cache": None, "--export-cache": None,
        "--import-cache": None, "--cache-stats": None,
        "--audit-cache": None, "--audit-cache-light": None,
    }
    i = 0
    #ПИРЕВОДЧИК
    found_any = False
    while i < len(argv):
        arg = argv[i]
        if arg in flags:
            found_any = True
            if arg in ("--cache-stats", "--audit-cache", "--audit-cache-light"):
                flags[arg] = True
                i += 1
                continue
            if i + 1 >= len(argv):
                print(f"[ОШИБКА] {arg} требует аргумент (путь к файлу).")
                sys.exit(1)
            flags[arg] = argv[i + 1]
            i += 2
            continue
        i += 1

    if not found_any:
        return False

    global_cache = GlobalTranslationCache(GLOBAL_CACHE_DB_PATH)
    try:
        if flags["--merge-cache"]:
            src = Path(flags["--merge-cache"])
            print(f"[i] Слияние {src} с {GLOBAL_CACHE_DB_PATH} ...")
            counts = global_cache.merge_local_db(src)
            _print_cache_counts("Результат слияния cache", counts)

        if flags["--export-cache"]:
            dst = Path(flags["--export-cache"])
            #Nikifor
            n = global_cache.export_json(dst)
            print(f"[i] Экспортировано {n} записей в {dst}")

        if flags["--import-cache"]:
            src = Path(flags["--import-cache"])
            print(f"[i] Импорт {src} в {GLOBAL_CACHE_DB_PATH} ...")
            if src.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
                counts = global_cache.merge_local_db(src)
            else:
                counts = global_cache.import_json(src)
            _print_cache_counts("Результат импорта cache", counts)

        if flags["--audit-cache"] or flags["--audit-cache-light"]:
            local = TranslationCache(CACHE_DB_PATH)
            try:
                run_cache_audits(local, global_cache, force=True,
                                 strict=False if flags["--audit-cache-light"] else None)
            finally:
                local.close()

        if flags["--cache-stats"]:
            revalidation = global_cache.revalidate_stale_entries()
            print(f"[i] Global cache: {GLOBAL_CACHE_DB_PATH}")
            print(f"    Всего записей:       {global_cache.count()}")
            print(f"    Переоценено:         {revalidation['revalidated']}")
            print(f"    Отклонено повторно:  {revalidation['rejected']}")
    finally:
        global_cache.close()

    return True

#Никифор
def write_official_ru_log(result: AnalysisResult) -> Path:


    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / "skipped_official_ru.txt"

    by_mod: dict[str, list[tuple]] = {}
    for modid, entry, key, en_v, ru_v in result.official_ru_log:
        by_mod.setdefault(modid, []).append((entry, key, en_v, ru_v))

    saved_chars = sum(len(en) for en in result.official_ru)

    with path.open("w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("ПРОПУЩЕНО: У МОДА УЖЕ ЕСТЬ ОФИЦИАЛЬНЫЙ РУССКИЙ ПЕРЕВОД\n")
        f.write("=" * 70 + "\n")
        f.write("Эти строки НЕ отправлялись в Google и НЕ попали в наш\n")
        f.write("ресурспак: в игре сработает родной ru_ru.json самого мода.\n\n")
        f.write(f"Модов с официальным русским:   {len(by_mod)}\n")
        f.write(f"Пропущено ключей (мод+ключ):    {len(result.official_ru_scoped)}\n")
        f.write(f"Уникальных EN-текстов в них:   {len(result.official_ru)}\n")
        f.write(f"Всего случаев (с повторами):   {len(result.official_ru_log)}\n")
        f.write(f"Сэкономлено символов:          {saved_chars}\n")
        f.write("=" * 70 + "\n\n")

        for modid in sorted(by_mod):
            rows = by_mod[modid]
            f.write(f"\n--- {modid} ({len(rows)} строк) ---\n")
            for entry, key, en_v, ru_v in rows:
                f.write(f"  {key}\n")
                #228
                f.write(f"      EN: {en_v}\n")
                f.write(f"      RU: {ru_v}\n")

    return path







def run_translation_job(*, reset_cancel: bool = True) -> dict:






    if FULL_LOG_PATH is None:
        start_full_logging("engine")
    log_event("run_translation_job: START")
    if reset_cancel:
        clear_cancel()
    elif CANCEL_REQUESTED:


        raise RuntimeError("Перевод остановлен пользователем до начала анализа.")
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        TRANSLATION_ERROR_LOG.write_text("", encoding="utf-8")
    except Exception:
        pass



    for output_dir in (RESOURCEPACK_DIR, TRANSLATED_MODPACK_DIR, PATCHOULI_OUTPUT_DIR):
        if output_dir.exists():
            shutil.rmtree(output_dir, ignore_errors=False)
    ensure_dirs()

    #01012007
    log_event("PHASE analysis: START")
    result = run_analysis()
    log_event(f"PHASE analysis: END | candidates={len(result.candidates)} | errors={len(result.errors)}")
    if result.official_ru:
        write_official_ru_log(result)

    dry_report = build_report(result, None, {})
    write_reports(result, dry_report, dry_run=True)

    if CANCEL_REQUESTED:
        raise RuntimeError("Перевод остановлен пользователем.")
    if async_playwright is None:
        raise RuntimeError(
            "Не установлен Playwright. Установите зависимости из requirements.txt и выполните: python -m playwright install chromium"
        )

    original_hashes = compute_original_hashes(result)
    cache = TranslationCache(CACHE_DB_PATH)
    global_cache = GlobalTranslationCache(GLOBAL_CACHE_DB_PATH)
    try:
        _progress("translation", 0, 1, "Подготовка к переводу…")
        import_manual_translation_folder(global_cache)
        global_cache.revalidate_stale_entries()
        run_cache_audits(cache, global_cache)
        log_event("PHASE translation: START")
        translations_raw, stats = run_translation_phase(result, cache, global_cache)
        log_event(f"PHASE translation: END | stats={stats}")
        translations = {
            t: r.translated for t, r in translations_raw.items()
            if r.translated is not None
        }
        #   https://www.youtube.com/@kefir__play__ru
        translations, _gl = apply_glossary_to_translations(translations)
        log_event(f"GLOSSARY applied to {_gl} translations")
        translations = {t: normalize_translation_style(t, v) for t, v in translations.items()}

        if CANCEL_REQUESTED:
            raise RuntimeError("Перевод остановлен пользователем.")

        write_report_state = {"errors": []}
        _progress("apply", 0, 5, "Запись переводов…")
        write_resourcepack_pack_mcmeta()
        write_lang_json_sources(result, translations, write_report_state)
        _progress("apply", 1, 5, "Записаны локализации модов…")
        write_generic_json_sources(result, translations, write_report_state)
        _progress("apply", 2, 5, "Записаны JSON-данные…")
        write_snbt_sources(result, translations, write_report_state)
        _progress("apply", 3, 5, "Записаны FTB Quests / SNBT…")
        write_kubejs_scripts(result, translations, write_report_state)
        _progress("apply", 4, 5, "Записаны KubeJS…")
        write_config_sources(result, translations, write_report_state)
        _progress("apply", 5, 5, "Все переводы подготовлены.")

        log_event("PHASE validation: START")
        problems = post_write_validation(write_report_state)
        log_event(f"PHASE validation: END | problems={len(problems)}")
        if problems:
            result.errors.extend(problems)
        original_problems = verify_originals_untouched(original_hashes)
        if original_problems:
            result.errors.extend(original_problems)
        result.errors.extend(write_report_state.get("errors", []))

        #   https://chkpnt.ru/welcome
        final_report = build_report(result, translations_raw, stats)
        final_report["write_stats"] = {
            k: v for k, v in write_report_state.items() if k != "errors"
        }
        for stat_key in (
            "validation_failed", "json_validation_failed",
            "snbt_validation_failed", "kubejs_validation_failed",
            "config_validation_failed", "technical_data_changed",
            "technical_leaves_reverted",
        ):
            final_report[stat_key] = write_report_state.get(stat_key, 0)
        final_report["technical_values_detected"] = get_technical_stats()["detected"]
        final_report["technical_values_skipped"] = get_technical_stats()["detected"]
        write_reports(result, final_report, dry_run=False)
        log_event("run_translation_job: END SUCCESS")
        return {
            "result": result,
            "translations_raw": translations_raw,
            "translations": translations,
            "stats": stats,
            "report": final_report,
        }
    finally:
        cache.close()
        global_cache.close()





def main():
    global MC_DIR, RESOURCEPACK_DIR

    #Kefir
    print("Minecraft Modpack Translator (EN -> RU)")
    print("=" * 60)

    if not self_test():
        print("[!] Самодиагностика выявила проблемы, но выполнение продолжится "
              "(рекомендуется проверить translation_reports/translation_errors.txt).")

    try:
        MC_DIR = discover_mc_dir()
        RESOURCEPACK_DIR = MC_DIR / "resourcepacks" / RESOURCEPACK_NAME
    except FileNotFoundError as e:
        print(f"[ОШИБКА] {e}")
        sys.exit(1)

    print(f"[i] Найдена папка модпака: {MC_DIR}")
    ensure_dirs()

    print("[i] Проверка результатов прошлых запусков на битые файлы...")
    stale_problems = purge_stale_broken_outputs()
    if stale_problems:
        print(f"[!] Удалено повреждённых файлов от прошлых запусков: {len(stale_problems)}")
        for p in stale_problems:
            print(f"    {p}")

    print("[i] Анализ модпака (JAR, FTB Quests, Patchouli, KubeJS, config)...")
    result = run_analysis()


    if result.official_ru:
        official_log = write_official_ru_log(result)
        print(
            f"[i] Пропущено строк с официальным русским переводом мода: "
            f"{len(result.official_ru)} (лог: {official_log})"
        )

    #3месяца
    report = build_report(result, None, {})
    write_reports(result, report, dry_run=True)

    print()
    print(f"JAR найдено:            {report['jar_count']}")
    print(f"Модов найдено:          {report['mod_count']}")
    print(f"Language files:         {report['lang_file_count']}")
    print(f"Всего кандидатов:       {report['total_candidates']}")
    print(f"Уникальных строк:       {report['unique_candidates']}")
    print(f"FTB Quests файлов:      {report['ftbquests_count']}")
    print(f"Patchouli файлов:       {report['patchouli_count']}")
    print(f"KubeJS файлов:          {report['kubejs_count']}")
    print(f"Ошибок анализа:         {len(report['errors'])}")
    print()
    print(f"[i] Полный отчёт: {REPORTS_DIR / 'translation_report.txt'}")
    print(f"[i] Список кандидатов: {REPORTS_DIR / 'translation_candidates.txt'}")

    if not ANALYZE_ONLY:
        choice = "1"
    else:
        print()
        print("1 - начать перевод")
        print("2 - выйти")
        print("3 - экспортировать строки для ручного/ИИ перевода (без Google Translate)")
        choice = input("> ").strip()

    if choice not in ("1", "3"):
        print("Выход без перевода.")
        return

    #Никифор
    global_cache = GlobalTranslationCache(GLOBAL_CACHE_DB_PATH)

    if choice == "3":
        try:
            bundle = export_manual_translation_bundle(result, global_cache)
        finally:
            global_cache.close()
        print()
        print(f"[i] Строк для ручного/ИИ перевода:      {bundle['count']}")
        print(f"[i] Файл для ручного перевода:          {bundle['txt_path']}")
        print(f"[i] Файл-шаблон для перевода через ИИ:  {bundle['json_path']}")
        print()
        print("[i] Впишите перевод в .txt файл вручную (любым способом) и/или")
        print("    отдайте .json файл внешнему ИИ на перевод. Готовый файл")
        print("    (этот же или любой другой .txt/.json) положите в папку")
        print(f"    {MANUAL_TRANSLATION_DIR} и запустите скрипт заново,")
        print("    выбрав пункт \"1\" - переводы подхватятся автоматически.")
        return

    if async_playwright is None:
        print("[ОШИБКА] Playwright не установлен. Выполните: pip install -r requirements.txt и python -m playwright install chromium")
        global_cache.close()
        sys.exit(1)

    original_hashes = compute_original_hashes(result)

    cache = TranslationCache(CACHE_DB_PATH)
    try:
        print("[i] Проверка папки manual_translation/ на готовые ручные/ИИ-переводы...")
        manual_counts = import_manual_translation_folder(global_cache)
        #3месяца
        if manual_counts["files"]:
            print(f"    Файлов обработано: {manual_counts['files']}, "
                  f"добавлено: {manual_counts['imported']}, "
                  f"уже было: {manual_counts['duplicates']}, "
                  f"конфликтов: {manual_counts['conflicts']}, "
                  f"отклонено: {manual_counts['rejected']}")

        global_cache.revalidate_stale_entries()
        run_cache_audits(cache, global_cache)
        print()
        print("[i] Перевод строк через Google Translate...")
        translations_raw, stats = run_translation_phase(result, cache, global_cache)
        translations = {t: r.translated for t, r in translations_raw.items() if r.translated is not None}
        translations, _gl = apply_glossary_to_translations(translations)
        print(f"[i] Глоссарий применён к {_gl} строкам (glossary_ru.json)")
        translations = {t: normalize_translation_style(t, v) for t, v in translations.items()}

        print("[i] Применение переводов и запись результатов...")
        write_report_state = {"errors": []}
        write_resourcepack_pack_mcmeta()
        write_lang_json_sources(result, translations, write_report_state)
        write_generic_json_sources(result, translations, write_report_state)
        write_snbt_sources(result, translations, write_report_state)
        write_kubejs_scripts(result, translations, write_report_state)
        write_config_sources(result, translations, write_report_state)

        print("[i] Проверка результатов...")
        problems = post_write_validation(write_report_state)
        if problems:
            print(f"[!] Обнаружено {len(problems)} проблем при финальной проверке (см. отчёт об ошибках).")
            result.errors.extend(problems)

        #01012007
        print("[i] Проверка целостности оригинальных файлов...")
        original_problems = verify_originals_untouched(original_hashes)
        if original_problems:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА] Оригинальный модпак был изменён! ({len(original_problems)})")
            result.errors.extend(original_problems)

        result.errors.extend(write_report_state.get("errors", []))

        final_report = build_report(result, translations_raw, stats)
        final_report["write_stats"] = {
            k: v for k, v in write_report_state.items() if k != "errors"
        }



        for stat_key in (
            "validation_failed", "json_validation_failed",
            "snbt_validation_failed", "kubejs_validation_failed",
            "config_validation_failed", "technical_data_changed",
            "technical_leaves_reverted",
        ):
            final_report[stat_key] = write_report_state.get(stat_key, 0)
        final_report["technical_values_detected"] = get_technical_stats()["detected"]
        final_report["technical_values_skipped"] = get_technical_stats()["detected"]
        write_reports(result, final_report, dry_run=False)
        print_final_summary(final_report)
    finally:
        cache.close()
        global_cache.close()


if __name__ == "__main__":
    try:
        #ПИРЕВОДЧИК
        main()
    except KeyboardInterrupt:
        print("\n[!] Прервано пользователем. Прогресс сохранён в translation_cache.db.")
        sys.exit(130)
    except Exception:
        print("\n[ОШИБКА] Необработанное исключение:")
        traceback.print_exc()
        sys.exit(1)
