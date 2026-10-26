# -*- coding: utf-8 -*-
# ======================================================================
# Создатель Dominika4ik
# https://eblo.id/@dominikan4ik
# при поддержке t.me/kefir_play
# сайт моего знакомого https://chkpnt.ru/welcome (активно развивается)
# просьба подписаться на него https://www.youtube.com/@kefir__play__ru
# ======================================================================





from __future__ import annotations

import json
import os
import queue
import re
import shutil
import sys
import threading
import time
import traceback
import zipfile
from datetime import datetime
from pathlib import Path
import deploy_safety
import license_texts
import tkinter as tk
from tkinter import ttk, filedialog, messagebox



if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(BUNDLE_DIR / "playwright-browsers")
    try:
        _probe = APP_DIR / ".write_test.tmp"
        _probe.write_text("ok", encoding="utf-8")
        _probe.unlink()
    except OSError:
        APP_DIR = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "MinecraftTranslator"
        APP_DIR.mkdir(parents=True, exist_ok=True)
else:
    APP_DIR = Path(__file__).resolve().parent
    BUNDLE_DIR = APP_DIR

import translator_engine as tr
if getattr(sys, "frozen", False) and (APP_DIR / "glossary_ru.json").exists():
    tr.GLOSSARY_PATH = APP_DIR / "glossary_ru.json"


APP_TITLE = "Minecraft Modpack Translator"


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")

    def show(self, _event=None):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 8
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tip, text=self.text, justify="left",
            background="#fffde8", relief="solid", borderwidth=1,
            padx=8, pady=6, wraplength=340
        )
        label.pack()

    def hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class TranslatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x650")
        self.minsize(900, 590)

        self.path_var = tk.StringVar()
        self.concurrent_var = tk.IntVar(value=1)
        self.batch_var = tk.IntVar(value=3900)

        self.status_var = tk.StringVar(value="Выберите папку модпака")
        self.stage_var = tk.StringVar(value="")
        self.percent_var = tk.StringVar(value="0%")
        self.eta_var = tk.StringVar(value="Осталось времени: —")
        self.log_queue = queue.Queue()
        self.worker = None
        self.started_at = None
        self.last_progress = None
        self.last_report = None
        self.last_backup = None
        self.last_changed = 0
        self.busy = False


        self.deploying = threading.Event()


        self._gate = threading.Lock()
        self.close_when_idle = False

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("vista")
        except tk.TclError:
            pass

        self._build_styles()
        self._show_setup()
        self.after(100, self._drain_queue)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_styles(self):
        self.style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        self.style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"))
        self.style.configure("Big.TButton", font=("Segoe UI", 11, "bold"), padding=(18, 10))
        self.style.configure("Green.Horizontal.TProgressbar", thickness=18)
        self.style.configure("Card.TLabelframe", padding=14)

    def _clear(self):
        for child in self.winfo_children():
            child.destroy()

    def _header(self, title, subtitle=None):
        frame = ttk.Frame(self, padding=(28, 22, 28, 8))
        frame.pack(fill="x")
        ttk.Label(frame, text=title, style="Title.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(frame, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))
        return frame

    def _show_setup(self):
        self._clear()
        self.busy = False
        self._header(
            "Переводчик сборок Minecraft",
            "Автоматический EN → RU перевод с кэшем и безопасным применением изменений"
        )

        main = ttk.Frame(self, padding=(28, 10, 28, 20))
        main.pack(fill="both", expand=True)

        path_box = ttk.LabelFrame(main, text="Сборка", style="Card.TLabelframe")
        path_box.pack(fill="x", pady=(4, 12))
        row = ttk.Frame(path_box)
        row.pack(fill="x")
        entry = ttk.Entry(row, textvariable=self.path_var, font=("Segoe UI", 11))
        entry.pack(side="left", fill="x", expand=True, ipady=7)
        browse = ttk.Button(row, text="Обзор…", command=self._browse)
        browse.pack(side="left", padx=(10, 0), ipadx=12, ipady=3)
        Tooltip(entry, "Путь к папке Minecraft/сборки. Внутри обычно находятся mods, config, kubejs и другие файлы сборки.")
        Tooltip(browse, "Выбрать папку сборки через проводник Windows.")

        columns = ttk.Frame(main)
        columns.pack(fill="both", expand=True)

        settings = ttk.LabelFrame(columns, text="Настройки скорости", style="Card.TLabelframe")
        settings.pack(side="left", fill="y", padx=(0, 12))

        ttk.Label(
            settings,
            text="Браузерные запросы выполняются последовательно, чтобы не создавать очередь запросов при ограничениях Google.",
            justify="left", wraplength=270
        ).pack(anchor="w", pady=(0, 12))
        self._setting_row(
            settings, "Символов в одном запросе", self.batch_var,
            "Максимальное количество символов в одном браузерном запросе к Google Translate. Рекомендуется 3900."
        )

        note = ttk.Label(
            settings,
            text="Интервал между реальными запросами:\n1 секунда (фиксирован)",
            justify="left", wraplength=270
        )
        note.pack(anchor="w", pady=(20, 6))
        Tooltip(note, "Это защитный лимит самого переводчика. Он не является пользовательской настройкой и специально оставлен фиксированным.")

        info = ttk.LabelFrame(columns, text="Что произойдёт", style="Card.TLabelframe")
        info.pack(side="left", fill="both", expand=True)

        info_text = (
            "1. Анализируется сборка и находятся строки для перевода.\n\n"
            "2. Используется локальный и глобальный SQLite-кэш, чтобы не переводить "
            "одинаковые строки повторно.\n\n"
            "3. Переводы сначала записываются в отдельные результаты и проходят проверки.\n\n"
            "4. Перед изменением сборки создаётся резервная копия всех файлов, "
            "которые будут заменены или добавлены.\n\n"
            "5. Проверенные переводы автоматически применяются прямо к выбранной сборке.\n\n"
            "6. Оригинальные файлы до применения переводов проверяются на целостность."
        )
        ttk.Label(info, text=info_text, justify="left", wraplength=570).pack(fill="both", expand=True)

        bottom = ttk.Frame(main)
        bottom.pack(fill="x", pady=(16, 0))
        self.start_btn = ttk.Button(bottom, text="Начать перевод", style="Big.TButton", command=self._start)
        self.start_btn.pack(side="right")
        Tooltip(self.start_btn, "Запустить анализ, перевод, проверки, резервное копирование и автоматическую замену файлов в выбранной сборке.")

    def _setting_row(self, parent, label, variable, tooltip):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=7)
        lbl = ttk.Label(frame, text=label)
        lbl.pack(anchor="w")
        spin = ttk.Spinbox(frame, from_=1, to=1000, textvariable=variable, width=12)
        spin.pack(anchor="w", pady=(4, 0), ipady=3)
        Tooltip(lbl, tooltip)
        Tooltip(spin, tooltip)

    def _browse(self):
        path = filedialog.askdirectory(title="Выберите папку Minecraft / модпака")
        if path:
            self.path_var.set(path)

    def _validate_setup(self):
        path = Path(self.path_var.get().strip().strip('"'))
        if not path.is_dir():
            messagebox.showerror("Ошибка", "Указанная папка не существует.")
            return None
        if not (path / "mods").is_dir():
            ok = messagebox.askyesno(
                "Папка выглядит необычно",
                "В выбранной папке нет каталога mods.\n\nПродолжить всё равно?"
            )
            if not ok:
                return None
        try:



            concurrent = 1
            batch = int(self.batch_var.get())
            if batch < 1 or batch > 5000:
                raise ValueError
        except Exception:
            messagebox.showerror("Ошибка", "Размер запроса должен быть целым числом от 1 до 5000 символов.")
            return None
        return path, concurrent, batch

    def _start(self):
        validated = self._validate_setup()
        if not validated:
            return
        path, concurrent, batch = validated

        if not messagebox.askyesno(
            "Подтверждение",
            "Перед заменой файлов программа создаст резервную копию изменяемых файлов.\n\n"
            "После успешных проверок переведённые файлы будут автоматически применены к выбранной сборке.\n\n"
            "Начать?"
        ):
            return

        tr.clear_cancel()
        self.busy = True
        self.started_at = time.monotonic()
        self.last_progress = None
        self._show_progress()

        self.worker = threading.Thread(
            target=self._worker_run,
            args=(path, concurrent, batch),
            daemon=True
        )
        self.worker.start()

    def _show_progress(self):
        self._clear()
        self._header("Перевод сборки", "Пожалуйста, не запускайте Minecraft из этой папки до завершения операции.")

        main = ttk.Frame(self, padding=(28, 10, 28, 24))
        main.pack(fill="both", expand=True)

        top = ttk.Frame(main)
        top.pack(fill="x")
        ttk.Label(top, textvariable=self.stage_var, style="Section.TLabel").pack(side="left")
        ttk.Label(top, textvariable=self.percent_var, style="Section.TLabel").pack(side="right")

        self.progress = ttk.Progressbar(
            main, mode="determinate", maximum=100,
            style="Green.Horizontal.TProgressbar"
        )
        self.progress.pack(fill="x", pady=(10, 8))

        ttk.Label(main, textvariable=self.eta_var).pack(anchor="e")

        stats = ttk.LabelFrame(main, text="Текущий этап", style="Card.TLabelframe")
        stats.pack(fill="x", pady=(18, 12))
        self.stats_text = tk.StringVar(value="Подготовка…")
        ttk.Label(stats, textvariable=self.stats_text, justify="left").pack(anchor="w")

        log_frame = ttk.LabelFrame(main, text="Журнал", style="Card.TLabelframe")
        log_frame.pack(fill="both", expand=True)
        self.log_text = tk.Text(log_frame, height=12, wrap="word", state="disabled", font=("Consolas", 9))
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        bottom = ttk.Frame(main)
        bottom.pack(fill="x", pady=(12, 0))
        self.stop_btn = ttk.Button(bottom, text="Остановить после текущего этапа", command=self._stop)
        self.stop_btn.pack(side="right")
        Tooltip(self.stop_btn, "Попросить переводчик остановиться на безопасной контрольной точке. Уже сохранённый кэш не удаляется.")

    def _stop(self):
        if not self.busy:
            return
        with self._gate:
            deploying = self.deploying.is_set()
            if not deploying:
                tr.request_cancel()
        if deploying:
            messagebox.showinfo(
                "Применение переводов",
                "Сейчас переводы применяются к сборке. Остановка в середине этого этапа "
                "может оставить часть файлов изменёнными. Дождитесь завершения применения."
            )
            return
        if hasattr(self, "stop_btn"):
            self.stop_btn.configure(state="disabled")
        self._append_log("Запрошена остановка. Переводчик остановится на безопасной контрольной точке…")

    def _worker_run(self, path: Path, concurrent: int, batch: int):
        try:
            tr.configure_translation(concurrent, batch)
            tr.set_progress_callback(self._progress_callback)

            tr.MC_DIR = path
            tr.RESOURCEPACK_DIR = APP_DIR / "Translation_Output" / tr.RESOURCEPACK_NAME

            tr.TRANSLATED_MODPACK_DIR = APP_DIR / "Translated_Modpack"
            tr.PATCHOULI_OUTPUT_DIR = APP_DIR / "Translated_Patchouli"
            tr.CACHE_DB_PATH = APP_DIR / "translation_cache.db"
            tr.GLOBAL_CACHE_DB_PATH = APP_DIR / "global_translations.db"
            tr.REPORTS_DIR = APP_DIR / "translation_reports"

            tr.start_full_logging("gui")
            tr.log_event(f"GUI worker START | modpack={path} | concurrent={concurrent} | batch_chars={batch}")

            self._queue_log(f"Сборка: {path}")
            self._queue_log("Параллельность браузера: 1 (без очереди фоновых батчей)")
            self._queue_log(f"Символов в запросе: {batch}")
            self._queue_log("Фиксированный интервал запросов: 1 с")

            job = tr.run_translation_job(reset_cancel=False)


            if tr.CANCEL_REQUESTED:
                raise RuntimeError("Перевод остановлен пользователем до применения результатов.")
            report = job["report"]

            if report.get("translation_stats", {}).get("failed", 0):
                self._queue_log(
                    f"Перевод завершён с ошибками: {report['translation_stats'].get('failed', 0)}"
                )

            self._progress_callback("deploy", 0, 1, "Создание резервной копии…")
            backup = self._make_backup(path, job["result"])
            self.last_backup = backup
            self._progress_callback("deploy", 0, 1, f"Резервная копия: {backup}")

            if tr.CANCEL_REQUESTED:
                raise RuntimeError("Перевод остановлен пользователем до применения результатов. Резервная копия сохранена.")

            self._progress_callback("deploy", 0, 1, "Применение проверенных переводов к сборке…")


            with self._gate:
                if tr.CANCEL_REQUESTED:
                    raise RuntimeError("Перевод остановлен пользователем до применения результатов. Резервная копия сохранена.")
                self.deploying.set()
            try:


                changed = deploy_safety.deploy_with_rollback(
                    path, backup, lambda: self._deploy_outputs(path, job["result"]),
                    log=lambda m: tr.log_event(m, "WARNING"),
                )
            finally:
                self.deploying.clear()
            self.last_changed = changed
            self._progress_callback("deploy", 1, 1, f"Изменено файлов: {changed}")

            self.last_report = report
            self.log_queue.put(("done", None))
        except BaseException as exc:
            tr.log_event(f"GUI worker UNHANDLED EXCEPTION: {exc!r}", "ERROR")
            tr.log_event(traceback.format_exc(), "ERROR")
            tr.set_progress_callback(None)
            if tr.CANCEL_REQUESTED and "остановлен пользователем" in str(exc).lower():
                self.log_queue.put(("cancelled", exc))
            else:
                self.log_queue.put(("error", exc))
        finally:
            tr.log_event("GUI worker END")
            tr.stop_full_logging()

    def _progress_callback(self, stage, current, total, message):
        tr.log_event(f"PROGRESS | stage={stage} | {current}/{total} | {message}")
        self.log_queue.put(("progress", (stage, current, total, message)))

    def _queue_log(self, text):
        tr.log_event(f"GUI: {text}")
        self.log_queue.put(("log", text))

    def _append_log(self, text):
        if hasattr(self, "log_text"):
            self.log_text.configure(state="normal")
            self.log_text.insert("end", text + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

    def _drain_queue(self):
        try:
            while True:
                kind, data = self.log_queue.get_nowait()
                if kind == "log":
                    self._append_log(data)
                elif kind == "progress":
                    self._handle_progress(*data)
                    self._append_log(data[3])
                elif kind == "done":
                    tr.set_progress_callback(None)
                    self.busy = False
                    if self.close_when_idle:
                        self.destroy()
                        return
                    self._show_done()
                elif kind == "cancelled":
                    tr.set_progress_callback(None)
                    self.busy = False
                    self._append_log(f"Операция остановлена: {data}")
                    if self.close_when_idle:
                        self.destroy()
                        return
                    self._show_setup()
                elif kind == "error":
                    tr.set_progress_callback(None)
                    self.busy = False
                    self._append_log(f"ОШИБКА: {data}")
                    if self.close_when_idle:
                        self.destroy()
                        return
                    messagebox.showerror("Перевод не завершён", str(data))
                    self._show_setup()
        except queue.Empty:
            pass
        if self.winfo_exists():
            self.after(100, self._drain_queue)

    def _handle_progress(self, stage, current, total, message):
        stage_names = {
            "analysis": "Анализ сборки",
            "translation": "Перевод строк",
            "apply": "Подготовка файлов",
            "deploy": "Применение к сборке",
        }
        self.stage_var.set(stage_names.get(stage, stage))
        if total:
            frac = max(0.0, min(1.0, current / total))
        else:
            frac = 0.0


        bases = {"analysis": (0, 25), "translation": (25, 85), "apply": (85, 95), "deploy": (95, 100)}
        lo, hi = bases.get(stage, (0, 100))
        pct = lo + frac * (hi - lo)
        self.progress["value"] = pct
        self.percent_var.set(f"{pct:.0f}%")

        if self.started_at and pct > 0.1:
            elapsed = time.monotonic() - self.started_at
            remaining = elapsed * (100 - pct) / pct
            self.eta_var.set(f"Осталось времени: {self._format_duration(remaining)}")

        if stage == "translation" and total:
            self.stats_text.set(f"{message}\nОбработано: {current:,} / {total:,} уникальных строк")
        elif stage == "analysis" and total:
            self.stats_text.set(f"{message}\nПроанализировано этапов: {current} / {total}")
        else:
            self.stats_text.set(message)

    @staticmethod
    def _format_duration(seconds):
        if seconds < 60:
            return f"{max(1, int(seconds))} сек."
        minutes = int(seconds // 60)
        if minutes < 60:
            return f"{minutes} мин."
        return f"{minutes // 60} ч. {minutes % 60} мин."



    def _backup_root(self, modpack: Path) -> Path:
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return modpack.parent / "Translation_Backups" / f"{modpack.name}_{stamp}"

    def _make_backup(self, modpack: Path, result):
        backup = self._backup_root(modpack)
        targets = self._collect_deploy_targets(modpack, result)
        deploy_safety.make_backup(
            modpack, backup, targets["files"], targets["new_files"], targets["jars"],
            cancelled=lambda: tr.CANCEL_REQUESTED,
        )
        return backup

    def _restore_backup(self, modpack: Path, backup: Path) -> None:

        deploy_safety.restore_backup(modpack, backup)

    PACK_ZIP_NAME = "Modpack_Auto_Rus.zip"


    EMBED_LICENSE = True


    @staticmethod
    def _patch_jars_enabled(modpack: Path) -> bool:







        env = os.environ.get("MCT_PATCH_JARS")
        if env in ("0", "1"):
            return env == "1"
        if (APP_DIR / "no_patch_jars.flag").exists():
            return False
        if (APP_DIR / "patch_patchouli_jars.flag").exists():
            return True
        minor = tr.mc_minor_version(modpack)
        return minor is not None and minor >= 17

    def _jar_plan(self, modpack: Path, result) -> dict:


        plan: dict = {}
        if not self._patch_jars_enabled(modpack):
            return plan
        for src in result.generic_json_sources:
            if src.get("kind") != "PATCHOULI" or not src.get("deploy_out"):
                continue
            jar_s = str(src.get("jar", ""))
            jp = Path(jar_s)
            out = Path(src["deploy_out"])
            if "!" in jar_s or jp.suffix.lower() != ".jar" or not jp.exists() or not out.exists():
                continue
            sl = plan.setdefault(jp, {"overwrite": {}, "add": {}, "merge": set()})
            sl["add"][src["deploy_entry"]] = out.read_bytes()
        return plan

    @staticmethod
    def _lang_overlay_targets(modpack: Path, result) -> dict:


        targets = {}
        if not (modpack / "kubejs").is_dir():
            return targets
        for src in result.lang_json_sources:
            if src.get("is_config") or not src.get("jar"):
                continue
            m_ns = re.match(r"assets/([^/]+)/lang/", str(src.get("entry", "")))
            ns = m_ns.group(1) if m_ns else src["modid"]
            if ns in targets:
                continue
            if (tr.RESOURCEPACK_DIR / "assets" / ns / "lang" / "ru_ru.json").exists():
                targets[ns] = modpack / "kubejs" / "assets" / ns / "lang" / "ru_ru.json"
        return targets

    def _collect_deploy_targets(self, modpack: Path, result):
        files = []
        new_files = []


        if tr.TRANSLATED_MODPACK_DIR.exists():
            for p in tr.TRANSLATED_MODPACK_DIR.rglob("*"):
                if p.is_file():
                    target = modpack / p.relative_to(tr.TRANSLATED_MODPACK_DIR)
                    files.append(target)
                    if not target.exists():
                        new_files.append(target)

        for target in self._lang_overlay_targets(modpack, result).values():
            files.append(target)
            if not target.exists():
                new_files.append(target)

        jars = list(self._jar_plan(modpack, result).keys())
        files.extend(jars)

        for extra in (modpack / "resourcepacks" / self.PACK_ZIP_NAME, modpack / "options.txt"):
            files.append(extra)
            if not extra.exists():
                new_files.append(extra)

        for extra in self._license_targets(modpack):
            files.append(extra)
            if not extra.exists():
                new_files.append(extra)

        return {"files": files, "new_files": new_files, "jars": jars}

    def _license_targets(self, modpack: Path) -> list:
        if not self.EMBED_LICENSE:
            return []
        return [modpack / license_texts.FOLDER_NAME / name for name in license_texts.license_files()]

    def _write_license_files(self, modpack: Path) -> int:

        written = 0
        data = license_texts.license_bytes()
        for target in self._license_targets(modpack):
            payload = data[target.name]
            try:
                if target.is_file() and target.read_bytes() == payload:
                    continue
            except OSError:
                pass
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(target.name + ".tmp")
            tmp.write_bytes(payload)
            os.replace(tmp, target)
            written += 1
        return written

    def _deploy_outputs(self, modpack: Path, result):
        changed = 0


        if tr.TRANSLATED_MODPACK_DIR.exists():
            for p in tr.TRANSLATED_MODPACK_DIR.rglob("*"):
                if not p.is_file():
                    continue
                target = modpack / p.relative_to(tr.TRANSLATED_MODPACK_DIR)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
                changed += 1


        for ns, target in self._lang_overlay_targets(modpack, result).items():
            try:
                ours = json.loads((tr.RESOURCEPACK_DIR / "assets" / ns / "lang" / "ru_ru.json").read_text(encoding="utf-8"))
            except Exception:
                continue
            merged = {}
            if target.exists():
                try:
                    old = json.loads(target.read_text(encoding="utf-8"))
                    if isinstance(old, dict):
                        merged.update(old)
                except Exception:
                    pass
            merged.update(ours)
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(target.name + ".tmp")
            tmp.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(tmp, target)
            changed += 1


        for jar, plan in self._jar_plan(modpack, result).items():
            if tr.patch_jar_entries(jar, plan["overwrite"], plan["add"], plan["merge"]):
                changed += 1


        zip_path = modpack / "resourcepacks" / self.PACK_ZIP_NAME
        packed = tr.build_resourcepack_zip(
            tr.RESOURCEPACK_DIR, zip_path, tr.detect_pack_format(modpack),
            extra_files=license_texts.license_bytes() if self.EMBED_LICENSE else None,
        )
        if packed:
            changed += 1
            opt = tr.enable_resourcepack_in_options(modpack, self.PACK_ZIP_NAME, set_language=True)
            tr.log_event(f"Resource pack installed: {zip_path} ({packed} files) | options.txt: {opt}")
            self._queue_log(
                f"Ресурс-пак «{self.PACK_ZIP_NAME}» установлен и включён в options.txt, "
                "язык игры: русский. Игра должна быть закрыта."
            )


        if self.EMBED_LICENSE:
            n = self._write_license_files(modpack)
            tr.log_event(f"Licence files: {n} written to {modpack / license_texts.FOLDER_NAME}")
        return changed



    def _show_done(self):
        self._clear()
        report = self.last_report or {}
        stats = report.get("translation_stats", {})
        write_stats = report.get("write_stats", {})

        self._header("Перевод завершён", "Проверенные переводы автоматически применены к выбранной сборке.")

        main = ttk.Frame(self, padding=(28, 6, 28, 24))
        main.pack(fill="both", expand=True)

        columns = ttk.Frame(main)
        columns.pack(fill="both", expand=True)

        left = ttk.LabelFrame(columns, text="Информация о переводе", style="Card.TLabelframe")
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        unique = report.get("unique_candidates", 0)
        translated = stats.get("translated", 0)
        cached = stats.get("cached", 0)
        failed = stats.get("failed", 0)
        errors = len(report.get("errors", []))

        text = (
            f"Найдено модов: {report.get('mod_count', 0):,}\n"
            f"JAR-файлов: {report.get('jar_count', 0):,}\n"
            f"Уникальных строк: {unique:,}\n\n"
            f"Переведено через Google: {translated:,}\n"
            f"Взято из кэша: {cached:,}\n"
            f"Ошибок перевода: {failed:,}\n"
            f"Ошибок проверок: {errors:,}\n\n"
            f"Изменено файлов сборки: {self.last_changed:,}\n"
            f"Подготовлено lang-файлов: {write_stats.get('lang_files_written', 0):,}\n"
        )
        ttk.Label(left, text=text, justify="left", font=("Segoe UI", 11)).pack(anchor="nw")

        right = ttk.LabelFrame(columns, text="Резервная копия", style="Card.TLabelframe")
        right.pack(side="left", fill="both", expand=True)

        backup_text = (
            "Перед применением переводов была создана резервная копия всех "
            "файлов, которые программа заменяла или добавляла.\n\n"
            f"{self.last_backup or '—'}"
        )
        ttk.Label(right, text=backup_text, justify="left", wraplength=400).pack(anchor="nw", fill="x")

        btns = ttk.Frame(right)
        btns.pack(anchor="w", pady=(18, 0))
        b1 = ttk.Button(btns, text="Открыть папку", command=lambda: self._open_path(self.last_backup))
        b1.pack(side="left")
        Tooltip(b1, "Открыть папку с резервной копией в Проводнике Windows.")

        bottom = ttk.Frame(main)
        bottom.pack(fill="x", pady=(18, 0))
        if self.last_backup:
            restore = ttk.Button(bottom, text="Показать инструкцию восстановления", command=self._show_restore_info)
            restore.pack(side="left")
            Tooltip(restore, "Показать, как вручную вернуть файлы из резервной копии.")

        close = ttk.Button(bottom, text="Готово", style="Big.TButton", command=self.destroy)
        close.pack(side="right")

    def _show_restore_info(self):
        messagebox.showinfo(
            "Восстановление",
            "Закройте Minecraft и замените изменённые файлы в сборке файлами из папки резервной копии.\n\n"
            "Для новых файлов, которых раньше не существовало, удалите их.\n\n"
            "Точный список находится в backup_manifest.json."
        )

    @staticmethod
    def _open_path(path):
        if path and Path(path).exists():
            os.startfile(str(path))

    def _on_close(self):
        if self.busy:
            with self._gate:
                deploying = self.deploying.is_set()
            if deploying:
                messagebox.showinfo(
                    "Применение переводов",
                    "Сейчас изменения применяются к модпаку. Закройте окно после завершения этапа, "
                    "чтобы не прерывать применение файлов."
                )
                return
            if not messagebox.askyesno(
                "Перевод выполняется",
                "Запросить безопасную остановку и закрыть окно после завершения текущей операции?"
            ):
                return
            with self._gate:
                deploy_started = self.deploying.is_set()
                self.close_when_idle = True
                if not deploy_started:
                    tr.request_cancel()
            if deploy_started:
                messagebox.showinfo(
                    "Применение переводов",
                    "Применение уже началось. Окно закроется само после его завершения.")
                return
            if hasattr(self, "stop_btn"):
                self.stop_btn.configure(state="disabled")
            self._append_log("Запрошена остановка перед закрытием. Окно закроется после завершения фоновой операции.")
            return
        self.destroy()


def _find_browser_executable(root: Path):
    if not root.exists():
        return None
    for pattern in ("chrome.exe", "chrome", "headless_shell.exe", "headless_shell"):
        for candidate in root.rglob(pattern):
            if candidate.is_file():
                return candidate
    return None


async def _launch_bundled_browser():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto("about:blank")
            return browser.version
        finally:
            await browser.close()


def run_selftest(report_path: Path, with_browser: bool) -> int:
    report = {
        "frozen": bool(getattr(sys, "frozen", False)),
        "python": sys.version.split()[0],
        "app_dir": str(APP_DIR),
        "checks": {},
    }

    def record(name, ok, detail=""):
        report["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}

    for module_name in ("tkinter", "json5", "playwright", "deploy_safety", "license_texts", "translator_engine"):
        try:
            __import__(module_name)
            record(f"import {module_name}", True)
        except Exception as exc:
            required = getattr(sys, "frozen", False) or module_name != "json5"
            record(f"import {module_name}", not required, exc)
    try:
        files = license_texts.license_bytes()
        record("license texts", len(files) == 2 and all(b"MTFUL" in data for data in files.values()))
    except Exception as exc:
        record("license texts", False, exc)
    try:
        record("glossary", len(tr.load_glossary()) > 0, tr.GLOSSARY_PATH)
    except Exception as exc:
        record("glossary", False, exc)
    try:
        probe = APP_DIR / ".selftest_write.tmp"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        record("data folder is writable", True, APP_DIR)
    except Exception as exc:
        record("data folder is writable", False, exc)
    browsers_root = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")) if os.environ.get("PLAYWRIGHT_BROWSERS_PATH") else None
    if getattr(sys, "frozen", False) or browsers_root is not None:
        executable = _find_browser_executable(browsers_root) if browsers_root is not None else None
        record("bundled Chromium present", executable is not None, executable or browsers_root)
    if with_browser:
        try:
            import asyncio
            version = asyncio.run(_launch_bundled_browser())
            record("Chromium launches", True, version)
        except Exception as exc:
            record("Chromium launches", False, exc)
    try:
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            engine_ok = bool(tr.self_test())
        record("engine self-test", engine_ok)
    except Exception as exc:
        record("engine self-test", False, exc)
    report["ok"] = all(item["ok"] for item in report["checks"].values())
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return 2
    return 0 if report["ok"] else 1


def _selftest_arguments(argv):
    if "--selftest" not in argv:
        return None
    index = argv.index("--selftest")
    if index + 1 < len(argv) and not argv[index + 1].startswith("--"):
        path = Path(argv[index + 1])
    else:
        path = APP_DIR / "selftest_result.json"
    return path, "--browser" in argv


if __name__ == "__main__":
    selftest = _selftest_arguments(sys.argv)
    if selftest is not None:
        sys.exit(run_selftest(*selftest))
    app = TranslatorApp()
    app.mainloop()
