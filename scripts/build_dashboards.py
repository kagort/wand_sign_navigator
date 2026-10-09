#!/usr/bin/env python3
"""Собирает дашборды из data/*.json (сначала запустить build_dataset.py).

    quartz/static/dash/linia.html — «Линия книги»: главы — участки, разделы — станции.
    quartz/static/dash/atlas.html — «Атлас персоналий»: линия времени, карта, граф связей, темы, статистика.

Шаблоны — dashboards/*.template.html. Данные встроены, библиотеки лежат рядом (quartz/static/dash/vendor/),
ссылки относительные: страницы работают и на сайте (/static/dash/…), и в локальном `npx quartz build --serve`.
"""
import datetime
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, DASH, CONTENT = ROOT / "data", ROOT / "dashboards", ROOT / "content"
OUT = ROOT / "quartz" / "static" / "dash"
UP = "../../"  # от /static/dash/ до корня сайта


def rel(url):
    return url.replace(SITE, UP) if isinstance(url, str) else url
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
        sections=[{k: rel(s[k]) for k in ("id", "chapter", "section", "title", "annotation", "url", "cards")} for s in sections],
        cards={c["id"]: {k: rel(c[k]) for k in ("title", "kind", "url", "portrait")} for c in cards if c["id"] in used},
        chapters=chapters(sections),
    )
    tpl = (DASH / "linia.template.html").read_text(encoding="utf8")
    html = (tpl.replace("/*DATA*/null", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
               .replace("ATLAS_URL", "atlas.html")
               .replace("SITE_URL", UP)
               .replace("DATE_BUILT", datetime.date.today().strftime("%d.%m.%Y")))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "linia.html").write_text(html, encoding="utf8")
    print(f"quartz/static/dash/linia.html: станций {len(sections)}, карточек {len(used)}")
    build_atlas(sections)


def build_atlas(sections):
    from collections import Counter
    from itertools import combinations
    people = json.loads((DATA / "people.json").read_text(encoding="utf8"))
    edges = json.loads((DATA / "edges.json").read_text(encoding="utf8"))
    ids = {p["id"] for p in people}
    keep = ("id", "title", "title_en", "url", "portrait", "years", "born", "died", "born_year", "died_year",
            "birth_place", "birth_coords", "death_place", "death_coords", "nationality", "alma_mater",
            "affiliations", "fields", "awards", "teachers", "students", "colleagues", "sep", "wiki_ru",
            "notes", "bio_checked", "sections", "chapters", "who", "role", "cause_of_death")
    out_edges = []
    for e in edges:
        if e["source"] in ids and e["target"] in ids and e["type"] in ("учитель→ученик", "коллеги"):
            out_edges.append(dict(source=e["source"], target=e["target"], type="teacher" if e["type"] == "учитель→ученик" else "colleague"))
    related = {tuple(sorted((e["source"], e["target"]))) for e in out_edges}
    co = Counter()
    for s in sections:
        members = sorted(c for c in s["cards"] if c in ids)
        for a, b in combinations(members, 2):
            co[(a, b)] += 1
    out_edges += [dict(source=a, target=b, type="co", w=w) for (a, b), w in co.items() if (a, b) not in related]
    labels = {s["id"]: dict(label="Предисловие" if s["id"] == "predislovie" else f"Гл. {s['chapter']} ({s['section']}) {s['title']}") for s in sections}
    payload = dict(people=[{k: rel(p.get(k)) for k in keep} for p in people], edges=out_edges, sections=labels)
    tpl = (DASH / "atlas.template.html").read_text(encoding="utf8")
    html = (tpl.replace("/*DATA*/null", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
               .replace("LINIA_URL", "linia.html")
               .replace("SITE_URL", UP)
               .replace("DATE_BUILT", datetime.date.today().strftime("%d.%m.%Y")))
    (OUT / "atlas.html").write_text(html, encoding="utf8")
    print(f"quartz/static/dash/atlas.html: персоналий {len(people)}, связей {len(out_edges)}")


if __name__ == "__main__":
    main()
