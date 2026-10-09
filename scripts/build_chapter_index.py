#!/usr/bin/env python3
"""Вписывает в хабы глав (content/05-chapters/chapter_N.md, predislovie.md) сводку и список всех карточек главы.

Источник — data/sections.json и data/cards.json (сначала запустить build_dataset.py): карточка входит
в главу, если относится хотя бы к одному её разделу. Блоки между маркерами
    <!-- chapter-summary:start --> … <!-- chapter-summary:end -->   сводка, перед первым заголовком «##»
    <!-- chapter-index:start --> … <!-- chapter-index:end -->       список карточек, в конце хаба
генерируются целиком и руками не правятся; остальной текст хаба не трогается.
Списки — вики-ссылки, поэтому те же связи видны на графе Quartz и в Obsidian.

Запуск:  python scripts/build_chapter_index.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, HUBS = ROOT / "data", ROOT / "content" / "05-chapters"


def markers(name):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    return start, end, re.compile(r"\n*" + re.escape(start) + r".*?" + re.escape(end) + r"\n*", re.S)


SUMMARY, INDEX = markers("chapter-summary"), markers("chapter-index")

KINDS = [  # (вид карточки, заголовок списка, подпись в сводке)
    ("персоналия", "Персоналии", "персоналии"),
    ("метафора", "Метафоры и образы", "метафоры"),
    ("пример-кейс", "Кейсы", "кейсы"),
    ("концепт", "Концепции", "концепции"),
    ("контекст", "Контекст", "контекст"),
]


def label(text):
    return str(text).replace("|", "/").replace("[", "(").replace("]", ")")


def blocks(chapter, sections, cards):
    secs = [s for s in sections if s["chapter"] == chapter]
    where = {}
    for s in secs:
        for cid in s["cards"]:
            if cid in cards:
                where.setdefault(cid, []).append(s)
    if not where:
        return "", ""
    by_kind = {k: sorted((c for c in where if cards[c]["kind"] == k), key=lambda c: cards[c]["title"].lower()) for k, _, _ in KINDS}
    parts = [f"Разделов: **{len(secs)}**"] if chapter else []
    parts += [f"{short}: **{len(by_kind[k])}**" for k, _, short in KINDS if by_kind[k]]
    line = " · ".join(parts)
    summary = [SUMMARY[0], "", "## Сводка по главе", "",
               line[0].upper() + line[1:] + f" · всего карточек: **{len(where)}** · [полный список ↓](#все-карточки-главы)", "", SUMMARY[1]]
    note = "через тире — разделы, где встречается карточка; " if chapter else ""
    out = [INDEX[0], "", "## Все карточки главы", "",
           f"*Собрано по всем разделам главы; {note}список генерируется скриптом `scripts/build_chapter_index.py`.*"]
    for k, heading, _ in KINDS:
        if not by_kind[k]:
            continue
        out += ["", f"### {heading} ({len(by_kind[k])})", ""]
        for cid in by_kind[k]:
            line = f"- [[{cid}|{label(cards[cid]['title'])}]]"
            if chapter:
                line += " — " + ", ".join(f"[[{s['id']}|({s['section']})]]" for s in where[cid])
            out.append(line)
    return "\n".join(summary), "\n".join(out + ["", INDEX[1]])


def main():
    sections = json.loads((DATA / "sections.json").read_text(encoding="utf8"))
    cards = {c["id"]: c for c in json.loads((DATA / "cards.json").read_text(encoding="utf8"))}
    for path in sorted(HUBS.glob("*.md")):
        m = re.fullmatch(r"chapter_(\d)|predislovie", path.stem)
        if not m:
            continue
        chapter = int(m.group(1) or 0)
        text = path.read_text(encoding="utf8")
        new = INDEX[2].sub("\n\n", SUMMARY[2].sub("\n\n", text)).rstrip("\n") + "\n"
        summary, index = blocks(chapter, sections, cards)
        if summary:
            head = re.search(r"^## ", new, re.M)
            at = head.start() if head else len(new)
            new = new[:at].rstrip("\n") + "\n\n" + summary + "\n\n" + new[at:].lstrip("\n")
            new = new.rstrip("\n") + "\n\n" + index + "\n"
        if new != text:
            path.write_text(new, encoding="utf8")
        print(f"{path.relative_to(ROOT)}: {'обновлён' if new != text else 'без изменений'}")


if __name__ == "__main__":
    main()
