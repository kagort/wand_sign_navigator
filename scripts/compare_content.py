#!/usr/bin/env python3
"""Сравнивает две копии папки с заметками (например, content/ репозитория и папку в Obsidian).

Использование:
    python scripts/compare_content.py <папка_A> <папка_B>
    python scripts/compare_content.py content "D:/Obsidian/Vault/wilson-guide"

Файлы сравниваются по содержимому (SHA-256); разница только в переводах строк
(CRLF/LF) не считается отличием, но помечается отдельно.
"""
import hashlib
import sys
from datetime import datetime
from pathlib import Path

IGNORE_DIRS = {".obsidian", ".trash", ".git", "node_modules", ".quartz-cache"}
IGNORE_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def scan(root: Path) -> dict[str, Path]:
    files = {}
    for p in root.rglob("*"):
        if not p.is_file() or p.name in IGNORE_FILES:
            continue
        rel = p.relative_to(root)
        if any(part in IGNORE_DIRS for part in rel.parts):
            continue
        files[rel.as_posix()] = p
    return files


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def mtime(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    a_root, b_root = Path(sys.argv[1]), Path(sys.argv[2])
    a, b = scan(a_root), scan(b_root)

    only_a = sorted(a.keys() - b.keys())
    only_b = sorted(b.keys() - a.keys())
    differ, eol_only = [], []
    for rel in sorted(a.keys() & b.keys()):
        da, db = a[rel].read_bytes(), b[rel].read_bytes()
        if digest(da) == digest(db):
            continue
        if da.replace(b"\r\n", b"\n") == db.replace(b"\r\n", b"\n"):
            eol_only.append(rel)
        else:
            differ.append(rel)

    print(f"A = {a_root}  ({len(a)} файлов)")
    print(f"B = {b_root}  ({len(b)} файлов)\n")
    print(f"Только в A: {len(only_a)}")
    for rel in only_a:
        print(f"  + {rel}  [{mtime(a[rel])}]")
    print(f"\nТолько в B: {len(only_b)}")
    for rel in only_b:
        print(f"  + {rel}  [{mtime(b[rel])}]")
    print(f"\nРазное содержимое: {len(differ)}")
    for rel in differ:
        ta, tb = a[rel].stat().st_mtime, b[rel].stat().st_mtime
        newer = "A новее" if ta > tb else "B новее"
        print(f"  ~ {rel}  A[{mtime(a[rel])}] B[{mtime(b[rel])}] -> {newer}")
    print(f"\nОтличаются только переводом строк (CRLF/LF): {len(eol_only)}")
    for rel in eol_only:
        print(f"  = {rel}")

    clean = not (only_a or only_b or differ)
    print("\nИТОГ:", "копии совпадают" if clean else "есть расхождения")
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
