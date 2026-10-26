

import queue, sys, tempfile, threading, types
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

import gui_app
import translator_engine as te

CANCEL_MSG = "Перевод остановлен пользователем"


def check(name, cond):
    print(("[OK]   " if cond else "[FAIL] ") + name)
    if not cond:
        raise AssertionError(name)


class Box:
    def __init__(self): self.calls = []
    def showinfo(self, *a, **k): self.calls.append(("info", a))
    def askyesno(self, *a, **k): self.calls.append(("yesno", a)); return True
    def showerror(self, *a, **k): self.calls.append(("error", a))


def make_app(tmp):
    app = object.__new__(gui_app.TranslatorApp)
    app.log_queue = queue.Queue(); app.deploying = threading.Event(); app._gate = threading.Lock()
    app.busy = True; app.close_when_idle = False
    app.last_backup = None; app.last_changed = 0; app.last_report = None
    app.stop_btn = types.SimpleNamespace(configure=lambda **k: None)
    app._append_log = lambda *_: None
    app.calls = []
    app._backup_root = lambda mp: tmp / "bk"
    return app


def final_kinds(app):
    kinds = []
    while True:
        try: kinds.append(app.log_queue.get_nowait()[0])
        except queue.Empty: return kinds


def run_worker(app, tmp, job, make_backup=None, deploy=None, restore=None):
    saved = (gui_app.APP_DIR, te.run_translation_job, te.start_full_logging, te.stop_full_logging, gui_app.messagebox)
    gui_app.APP_DIR = tmp
    te.start_full_logging = lambda *a, **k: None
    te.stop_full_logging = lambda *a, **k: None
    te.run_translation_job = job
    gui_app.messagebox = Box()
    app._make_backup = make_backup or (lambda mp, r: (tmp / "bk"))
    app._deploy_outputs = deploy or (lambda mp, r: 1)
    app._restore_backup = restore or (lambda mp, b: app.calls.append("restore"))
    try:
        app._worker_run(tmp / "mp", 1, 3900)
    finally:
        gui_app.APP_DIR, te.run_translation_job, te.start_full_logging, te.stop_full_logging, gui_app.messagebox = saved
        te.clear_cancel(); te.set_progress_callback(None)
    return final_kinds(app)


OK_JOB = lambda **k: {"report": {}, "result": object()}

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td); (tmp / "bk").mkdir()


    app = make_app(tmp); te.request_cancel(); seen = {}
    def job_a(**k):
        seen["flag"] = te.CANCEL_REQUESTED
        raise RuntimeError(CANCEL_MSG)
    kinds = run_worker(app, tmp, job_a, make_backup=lambda *a: app.calls.append("backup"))
    check("A: pending Stop is still set when the engine starts (not swallowed)", seen["flag"] is True)
    check("A: ends as 'cancelled', never 'done'", kinds[-1] == "cancelled" and "done" not in kinds)
    check("A: no backup/deploy attempted", "backup" not in app.calls)


    app = make_app(tmp)
    def job_b(**k):
        te.request_cancel(); return {"report": {}, "result": object()}
    kinds = run_worker(app, tmp, job_b, make_backup=lambda *a: app.calls.append("backup"))
    check("B: Stop during translation -> 'cancelled', no false success", kinds[-1] == "cancelled" and "done" not in kinds)
    check("B: no backup/deploy attempted", "backup" not in app.calls)


    app = make_app(tmp)
    def backup_c(mp, r):
        te.request_cancel(); raise RuntimeError(CANCEL_MSG + " во время резервного копирования.")
    kinds = run_worker(app, tmp, OK_JOB, make_backup=backup_c, deploy=lambda *a: app.calls.append("deploy") or 1)
    check("C: Stop during backup -> 'cancelled'", kinds[-1] == "cancelled" and "done" not in kinds)
    check("C: deploy never ran", "deploy" not in app.calls)


    app = make_app(tmp)
    def backup_d(mp, r):
        te.request_cancel(); return tmp / "bk"
    kinds = run_worker(app, tmp, OK_JOB, make_backup=backup_d, deploy=lambda *a: app.calls.append("deploy") or 1)
    check("D: Stop just before deploy -> 'cancelled', deploy not started", kinds[-1] == "cancelled" and "deploy" not in app.calls)
    check("D: deploying flag is clear afterwards", not app.deploying.is_set())


    app = make_app(tmp); boxes = []
    def deploy_e(mp, r):
        gui_app.messagebox.calls.clear()
        app._stop()
        boxes.append(list(gui_app.messagebox.calls))
        app.calls.append(("flag_after_stop", te.CANCEL_REQUESTED))
        return 3
    kinds = run_worker(app, tmp, OK_JOB, deploy=deploy_e)
    check("E: Stop during deploy shows the 'wait' dialog", boxes and boxes[0] and boxes[0][0][0] == "info")
    check("E: Stop during deploy does NOT set the cancel flag", ("flag_after_stop", False) in app.calls)
    check("E: deploy completes and success is reported", kinds[-1] == "done" and app.last_changed == 3)
    check("E: deploying flag cleared after deploy", not app.deploying.is_set())


    import shutil, deploy_safety
    app = make_app(tmp)
    mp = tmp / "mp"; mp.mkdir(exist_ok=True); victim = mp / "options.txt"; victim.write_text("original")
    def backup_f(m, r):
        shutil.rmtree(tmp / "bk", ignore_errors=True)
        deploy_safety.make_backup(m, tmp / "bk", [victim], []); return tmp / "bk"
    def deploy_f(m, r):
        victim.write_text("half-translated"); raise OSError("disk full (injected)")
    kinds = run_worker(app, tmp, OK_JOB, make_backup=backup_f, deploy=deploy_f)
    check("F: failed deploy -> file restored by real rollback", victim.read_text() == "original")
    check("F: reported as 'error', never 'done'", kinds[-1] == "error" and "done" not in kinds)
    check("F: deploying flag cleared after failure", not app.deploying.is_set())


    app = make_app(tmp)
    def job_g(**k): raise KeyboardInterrupt()
    kinds = run_worker(app, tmp, job_g)
    check("G: BaseException in worker is reported as error (UI not stuck busy)", kinds and kinds[-1] == "error")


    gui_app.messagebox = Box()
    app = make_app(tmp); app.deploying.set(); te.clear_cancel()
    app._on_close()
    check("H: close during deploy is refused", app.close_when_idle is False and not te.CANCEL_REQUESTED
          and gui_app.messagebox.calls[0][0] == "info")
    app = make_app(tmp); app.deploying.clear(); destroyed = []
    app.destroy = lambda: destroyed.append(1)
    app._on_close()
    check("H: close while translating requests a stop but does NOT destroy the window yet",
          app.close_when_idle is True and te.CANCEL_REQUESTED and not destroyed)
    te.clear_cancel()
    app = make_app(tmp); app.busy = False; app.destroy = lambda: destroyed.append(1)
    app._on_close()
    check("H: idle window closes immediately", destroyed == [1, 1] or destroyed == [1])


    app = make_app(tmp); te.clear_cancel()
    with app._gate:
        t = threading.Thread(target=app._stop); t.start()
        t.join(0.3)
        check("I: _stop waits for the gate while the worker decides", t.is_alive() and not te.CANCEL_REQUESTED)
        app.deploying.set()
    t.join(2)
    check("I: once deploying was set first, Stop is refused (flag stays clear)", not te.CANCEL_REQUESTED)
    te.clear_cancel()

print("CANCEL RACE TESTS OK")
