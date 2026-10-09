#!/usr/bin/env python3
"""Собирает дашборды из data/*.json (сначала запустить build_dataset.py).

    dashboards/linia.html — «Линия книги»: главы — участки, разделы — станции.

Страница самодостаточна (данные встроены), её можно открыть локально двойным щелчком.
На сайте она публикуется по адресу /linia/ (шаг в .github/workflows/deploy-pages.yml).
"""
import datetime
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, DASH, CONTENT = ROOT / "data", ROOT / "dashboards", ROOT / "content"
SITE = "https://kagort.github.io/wand_sign_navigator/"


def chapters(sections):
    out = []
    for n in range(1, 7):
        text = (CONTENT / "05-chapters" / f"chapter_{n}.md").read_text(encoding="utf8")
        title = re.search(r'^title:\s*"?(.+?)"?\s*$', text, re.M).group(1)
        short = re.sub(r"\s*\(стр\..*\)$", "", title)
        out.append(dict(n=n, title=title, short=short, sections=sum(1 for s in sections if s["chapter"] == n)))
    return out


def main():
    sections = json.loads((DATA / "sections.json").read_text(encoding="utf8"))
    cards = json.loads((DATA / "cards.json").read_text(encoding="utf8"))
    used = {c for s in sections for c in s["cards"]}
    payload = dict(
        sections=[{k: s[k] for k in ("id", "chapter", "section", "title", "annotation", "url", "cards")} for s in sections],
        cards={c["id"]: {k: c[k] for k in ("title", "kind", "url", "portrait")} for c in cards if c["id"] in used},
        chapters=chapters(sections),
    )
    tpl = (DASH / "linia.template.html").read_text(encoding="utf8")
    html = (tpl.replace("/*DATA*/null", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
               .replace("SITE_URL", SITE)
               .replace("DATE_BUILT", datetime.date.today().strftime("%d.%m.%Y")))
    (DASH / "linia.html").write_text(html, encoding="utf8")
    print(f"dashboards/linia.html: станций {len(sections)}, карточек {len(used)}")


if __name__ == "__main__":
    main()
