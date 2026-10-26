
















from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Callable, Iterable, Optional

MANIFEST_NAME = "backup_manifest.json"
MANIFEST_VERSION = 2


class BackupError(RuntimeError):
    pass


class DeployRollbackFailed(RuntimeError):


    def __init__(self, message, original, rollback_error):
        super().__init__(message)
        self.original = original
        self.rollback_error = rollback_error


class RestoreError(RuntimeError):
    def __init__(self, message: str, errors: list):
        super().__init__(message)
        self.errors = errors


def sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def is_reparse_or_symlink(path: Path) -> bool:

    try:
        if path.is_symlink():
            return True
        st = os.lstat(path)
    except OSError:
        return False
    attrs = getattr(st, "st_file_attributes", 0)
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _has_link_component(root: Path, target: Path) -> Optional[Path]:

    try:
        rel = target.relative_to(root)
    except ValueError:
        return target
    cur = root
    for part in rel.parts:
        cur = cur / part
        if os.path.lexists(cur) and is_reparse_or_symlink(cur):
            return cur
    return None


def safe_rel_target(root: Path, relative: str) -> tuple:

    if not isinstance(relative, str) or not relative:
        raise ValueError(f"empty/invalid path in manifest: {relative!r}")
    rel = Path(relative)
    win = PureWindowsPath(relative)
    if (rel.is_absolute() or win.is_absolute() or win.drive or win.root
            or ".." in rel.parts or ".." in win.parts):
        raise ValueError(f"unsafe path in backup manifest: {relative!r}")
    return rel, root / rel


def _atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def make_backup(modpack: Path, backup: Path, files: Iterable[Path], new_files: Iterable[Path],
                jars: Iterable[Path] = (), cancelled: Callable[[], bool] = lambda: False) -> dict:


    modpack = Path(modpack)
    backup.mkdir(parents=True, exist_ok=False)
    try:
        entries = {}
        for p in files:
            if cancelled():
                raise BackupError("Перевод остановлен пользователем во время резервного копирования.")
            p = Path(p)
            link = _has_link_component(modpack, p)
            if link is not None:
                raise BackupError(f"Цель деплоя находится за symlink/reparse point: {link}")
            if not os.path.lexists(p):
                continue
            if not p.is_file():
                raise BackupError(f"Цель деплоя существует, но это не файл: {p}")
            rel = p.relative_to(modpack)
            dst = backup / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            src_hash = sha256_file(p)
            if sha256_file(dst) != src_hash:
                raise BackupError(f"Копия не совпала с оригиналом по SHA-256: {p}")
            entries[rel.as_posix()] = {"sha256": src_hash, "size": p.stat().st_size}

        new_list = []
        for p in new_files:
            p = Path(p)
            link = _has_link_component(modpack, p)
            if link is not None:
                raise BackupError(f"Новый файл находится за symlink/reparse point: {link}")
            rel = p.relative_to(modpack).as_posix()
            if rel in entries:
                continue
            new_list.append(rel)


        new_dirs = set()
        for rel in new_list:
            for parent in Path(rel).parents:
                if str(parent) in (".", ""):
                    continue
                if not (modpack / parent).exists():
                    new_dirs.add(parent.as_posix())

        manifest = {
            "version": MANIFEST_VERSION,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "modpack": str(modpack),
            "description": "Backup of files that will be replaced by the translator.",
            "files": entries,
            "new_files": sorted(set(new_list)),
            "new_dirs": sorted(new_dirs, key=lambda s: -len(s)),
            "jar_files": [Path(j).relative_to(modpack).as_posix() for j in jars],

            "existing_files": sorted(entries),
        }
        if cancelled():
            raise BackupError("Перевод остановлен пользователем во время резервного копирования.")
        _atomic_write_text(backup / MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False, indent=2))
        return manifest
    except BaseException:
        shutil.rmtree(backup, ignore_errors=True)
        raise


def load_manifest(backup: Path) -> dict:
    path = Path(backup) / MANIFEST_NAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RestoreError(f"Манифест резервной копии отсутствует или повреждён: {path}: {exc}", [str(exc)])
    if not isinstance(data, dict):
        raise RestoreError(f"Манифест резервной копии имеет неверный формат: {path}", ["not an object"])

    if "files" not in data:
        data["files"] = {rel: {} for rel in data.get("existing_files", []) if isinstance(rel, str)}
    if not isinstance(data["files"], dict) or not isinstance(data.get("new_files", []), list):
        raise RestoreError(f"Манифест резервной копии неполон: {path}", ["bad structure"])
    return data


def restore_backup(modpack: Path, backup: Path) -> dict:

    modpack = Path(modpack)
    backup = Path(backup)
    manifest = load_manifest(backup)
    errors: list = []
    stats = {"restored": 0, "already_ok": 0, "removed": 0, "dirs_removed": 0}

    for relative, meta in manifest["files"].items():
        try:
            rel, target = safe_rel_target(modpack, relative)
            link = _has_link_component(modpack, target)
            if link is not None:
                raise OSError(f"путь за symlink/reparse point: {link}")
            source = backup / rel
            if not source.is_file():
                raise FileNotFoundError(f"нет файла резервной копии: {source}")
            want = meta.get("sha256")
            if want and sha256_file(source) != want:
                raise OSError(f"копия в backup повреждена (SHA-256 не совпал): {source}")
            if target.is_file() and sha256_file(target) == (want or sha256_file(source)):
                stats["already_ok"] += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_name(target.name + ".mct-restore.tmp")
            try:
                shutil.copy2(source, temp)
                os.replace(temp, target)
            finally:
                if temp.exists():
                    try:
                        temp.unlink()
                    except OSError:
                        pass
            stats["restored"] += 1
        except Exception as exc:
            errors.append(f"{relative}: {exc}")

    for relative in manifest.get("new_files", []):
        try:
            _rel, target = safe_rel_target(modpack, relative)
            link = _has_link_component(modpack, target)
            if link is not None:
                raise OSError(f"путь за symlink/reparse point: {link}")
            if not os.path.lexists(target):
                continue
            if target.is_file():
                target.unlink()
                stats["removed"] += 1
            else:
                raise OSError("ожидался обычный файл; каталоги автоматически не удаляются")
        except Exception as exc:
            errors.append(f"{relative}: {exc}")

    for relative in manifest.get("new_dirs", []):
        try:
            _rel, target = safe_rel_target(modpack, relative)
            if target.is_dir() and not is_reparse_or_symlink(target) and not any(target.iterdir()):
                target.rmdir()
                stats["dirs_removed"] += 1
        except Exception:
            pass

    if errors:
        raise RestoreError(f"Откат выполнен не полностью ({len(errors)} ошибок): " + "; ".join(errors[:5]), errors)
    return stats


def deploy_with_rollback(modpack: Path, backup: Path, deploy: Callable[[], int],
                         log: Callable[[str], None] = lambda _m: None) -> int:


    try:
        return deploy()
    except BaseException as deploy_exc:
        try:
            stats = restore_backup(modpack, backup)
            log(f"DEPLOY_ROLLBACK completed: {stats}")
        except BaseException as rb_exc:
            log(f"DEPLOY_ROLLBACK FAILED: {rb_exc!r}")
            note = (f"Автоматический откат также не удался: {rb_exc}. "
                    f"Резервная копия для ручного восстановления: {backup}")
            raise DeployRollbackFailed(f"{deploy_exc}. {note}", deploy_exc, rb_exc) from deploy_exc
        raise
