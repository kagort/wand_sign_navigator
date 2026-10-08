# Прогресс сессий

Журнал работы над проектом «Путеводитель по „Блуждающим значениям“» (Quartz v5 + Obsidian).
Новые записи добавляются **сверху**. Порядок синхронизации описан в [SYNC.md](SYNC.md).

## Шаблон записи

```
## ГГГГ-ММ-ДД — <кратко о сессии>
**Ветка/коммит:** …
**Сделано:**
- …
**Найдено / проблемы:**
- …
**Следующие шаги:**
- [ ] …
```

---

## 2026-10-08 — README проекта

**Сделано:**
- `content/README.md` переписан под фактическую структуру (папки `00`–`06`, junction, цикл git) и скрыт
  с сайта через `draft: true` (плагин `remove-draft` включён в `quartz.config.yaml`). В Obsidian заметка видна.
- Цели пилота отмечены по состоянию репозитория: 27 карточек понятий, хабы глав 1–3 есть.

**Следующие шаги:**
- [ ] Битые ссылки: исправить опечатки (`bertran-rassel` → `bertrand-russell`, `oliver-heviside` → `oliver-heaviside`), для остальных создать заготовки.
- [ ] MOC-карты (цель пилота).

---

## 2026-10-08 — исправления в content/

**Сделано:**
- `content/00-meta/konventsii.md`: удалена испорченная строка `## title: … type: мета` (дубль frontmatter).
- `04-cases/oklahoma-hoedown-primer (переделать!).md` → `oklahoma-hoedown-primer.md`; пометка перенесена
  в frontmatter как `todo: "переделать"`. Ссылки `[[oklahoma-hoedown-primer]]` теперь работают.
- `.prettierignore`: добавлена `content` — Prettier больше не трогает заметки.

**Следующие шаги:**
- [x] Решить судьбу `content/README.md` (публикуется на сайте).
- [ ] Создать или исправить заметки по списку битых ссылок (см. первую запись).

---

## 2026-10-08 — переход на одну папку (junction)

**Ветка/коммит:** `claude/stoic-allen-kf1xbo` от `v5` @ `f987f0b`

**Сделано:**
- Выяснено, что `content/` в репозитории была junction на папку Obsidian (ссылка «наоборот»).
- Схема перевёрнута: настоящая папка — `C:\Users\Пользователь\wand_sign_navigator\content`,
  в хранилище — junction `C:\OBSIDIAN\new-vault\00 Projects\03 wand_sign_navigator` → `content`.
- Проверено: через ссылку видно 213 файлов, `git status` чистый, локальная `v5` = `origin/v5`.
- `docs/SYNC.md` переписан под фактическую схему, добавлены грабли настройки.

**Найдено / проблемы:**
- `New-Item -ItemType Junction` (PowerShell 5.1) ломает пути с кириллицей — использовать `mklink /J`.

**Следующие шаги:**
- [ ] Открыть Obsidian, проверить заметки/картинки; тестовая заметка должна появиться в `git status`.
- [x] Добавить `content` в `.prettierignore`, исправить frontmatter в `konventsii.md`.
- [x] Переименовать `oklahoma-hoedown-primer (переделать!).md`.

---

## 2026-10-08 — первая сверка с Obsidian, исправление скрипта

**Ветка/коммит:** `claude/stoic-allen-kf1xbo` от `v5` @ `cdecaab` (после слияния PR #10)

**Сделано:**
- PR #10 (журнал, SYNC.md, скрипт сверки) слит в `v5`.
- `compare_content.py`: убирает хвостовые кавычки в путях и останавливается с ошибкой, если папки нет
  (раньше несуществующая папка давала «0 файлов» без предупреждения).

**Найдено / проблемы:**
- Первый запуск сверки показал «B = 0 файлов» из-за пути `"C:\…\03 wand_sign_navigator\"`: в PowerShell `\"`
  экранирует кавычку. Папка Obsidian: `C:\OBSIDIAN\new-vault\00 Projects\03 wand_sign_navigator`.

**Следующие шаги:**
- [ ] Повторить сверку с путём без `\` в конце и свести расхождения.

---

## 2026-10-08 — анализ репозитория, журнал, схема синхронизации

**Ветка/коммит:** `claude/stoic-allen-kf1xbo` от `v5` @ `249506a`

**Сделано:**
- Проанализирован репозиторий: Quartz v5, заметки в `content/`, сайт публикуется через GitHub Pages
  (`.github/workflows/deploy-pages.yml`, каждый push в `v5`).
- Создан этот журнал `docs/Progress.md`.
- Описан алгоритм синхронизации Obsidian ↔ локальная папка ↔ GitHub: `docs/SYNC.md`.
- Добавлен скрипт сверки двух копий `scripts/compare_content.py`.
- Зафиксирован эталон содержимого `content/` на GitHub (213 файлов, 139 `.md`).

**Найдено / проблемы:**
- `docs/` — это документация самого Quartz (из upstream). На сайт не попадает: сборка идёт с `-d content`.
- Merge-коммит `249506a` (28.09) — `v5` правили из двух мест; это риск конфликтов.
- `content/00-meta/konventsii.md` — frontmatter продублирован строкой `## title: … type: мета`
  (похоже на работу Prettier). В `.prettierignore` нет `content`.
- `content/README.md` — внутренняя инструкция по пилоту; сейчас она публикуется на сайте.
- Файл с пробелами и скобками в имени: `04-cases/oklahoma-hoedown-primer (переделать!).md`,
  а ссылка `[[oklahoma-hoedown-primer]]` на него не ведёт.
- Ссылки на несуществующие заметки (пока не написаны или опечатки):
  `bertran-rassel` (6 ссылок), `empty-form`, `obshchie-imena`, `religio-medici-tsitata`, `sense-and-sensibilia` (по 2),
  `druidy-primer-kripke`, `etimologii-svyatogo-isidora`, `oliver-heviside`, `otkrytaya-tekstura`, `quine-nominalism`,
  `semantic-finality`, `wilson-rounder-records-biography`, `Беркли` (по 1),
  главы 4–6 в `index.md`, картинки `assets/isaac_hawkins_browne.jpg`, `assets/william_of_ockham.jpg`.
- Локальную папку и Obsidian из облачной сессии не видно: их нужно сверить у себя скриптом (см. SYNC.md).

**Следующие шаги:**
- [ ] Сверить локальную папку и Obsidian с GitHub (`git status`, `scripts/compare_content.py`), свести расхождения.
- [ ] Перейти на схему с junction/symlink (Obsidian открывает `content/` напрямую).
- [ ] Добавить `content` в `.prettierignore`, исправить frontmatter в `konventsii.md`.
- [ ] Решить судьбу `content/README.md` (перенести в `docs/` или отметить `draft: true`).
- [ ] Переименовать `oklahoma-hoedown-primer (переделать!).md` → `oklahoma-hoedown-primer.md` (пометку перенести в `status`).
- [ ] Создать или исправить заметки по списку битых ссылок.
