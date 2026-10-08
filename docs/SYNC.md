# Синхронизация: Obsidian ↔ локальная папка ↔ GitHub

**Главный принцип: у каждого файла одна «живая» копия.** Конфликты появляются, когда один и тот же файл
правят в двух местах до того, как они сверены (пример — merge-коммит `249506a` от 28.09.2026).

## Текущая схема (настроена 08.10.2026)

Физическая папка с заметками одна — `content/` в репозитории. Obsidian видит её через junction.

```
C:\Users\Пользователь\wand_sign_navigator\content              ← НАСТОЯЩАЯ папка (git)
C:\OBSIDIAN\new-vault\00 Projects\03 wand_sign_navigator  ──(junction)──►  content
```

| Где | Что это | Как меняется |
|---|---|---|
| **GitHub** (`kagort/wand_sign_navigator`, ветка `v5`) | весь сайт Quartz + `content/` | `git push`; каждый push в `v5` пересобирает сайт (`.github/workflows/deploy-pages.yml`) |
| **Локальная папка** `wand_sign_navigator/content` | та же папка, что и в Obsidian | правки в Obsidian, фиксация через git |

Синхронизировать нужно только две стороны: локальный репозиторий и GitHub. Это делает git.

Проверка, что схема цела:
```powershell
(Get-Item "$env:USERPROFILE\wand_sign_navigator\content").LinkType                          # пусто — обычная папка
(Get-Item "C:\OBSIDIAN\new-vault\00 Projects\03 wand_sign_navigator").LinkType          # Junction
```

### Что пошло не так при настройке (чтобы не повторить)

- Раньше ссылка была **в обратную сторону**: `content` была junction на папку Obsidian. Поэтому сверка
  «копий» показывала полное совпадение — это была одна папка. После переименования папки в Obsidian
  и создания встречной ссылки получилось кольцо (ошибка «Имя этого файла не может быть разрешено системой»).
- `New-Item -ItemType Junction` в Windows PowerShell 5.1 портит путь с кириллицей (`Пользователь`).
  Ссылки создавать только через `cmd /c mklink /J`.
- Ссылку удалять только `cmd /c rmdir "<ссылка>"`. **Не** `Remove-Item -Recurse` и не удаление
  через Проводник с «удалить всё» — это может стереть содержимое настоящей папки.
- `Move-Item` без `-Destination` переносит в текущую папку (у админ-консоли это `C:\WINDOWS\system32`).
- Не создавать ссылку на `content` где-то ещё внутри хранилища и не включать для `content`
  сторонние облачные синхронизаторы — это снова даст две «живые» копии.

### Как настроить заново (например, на другом компьютере)

1. `git clone https://github.com/kagort/wand_sign_navigator` (лучше в путь без кириллицы, например `C:\Projects`).
2. Закрыть Obsidian.
3. `cmd /c mklink /J "<хранилище>\00 Projects\03 wand_sign_navigator" "<репозиторий>\content"`
   (macOS/Linux: `ln -s "<репозиторий>/content" "<хранилище>/00 Projects/03 wand_sign_navigator"`).
4. Открыть Obsidian и проверить заметки и картинки (`assets/`).

> Внутри `content/` не должно быть папки `.obsidian` (настройки хранилища лежат в его корне).
> На всякий случай `.obsidian` уже внесена в `.gitignore`.

### Ежедневный цикл (pull → работа → commit → push)

```bash
cd wand_sign_navigator
git pull origin v5        # 1. ПЕРЕД началом работы: забрать то, что изменилось на GitHub
# 2. работа в Obsidian (файлы меняются прямо в content/)
git status                # 3. посмотреть, что изменилось
git add content
git commit -m "Карточки гл. 3: …"
git push origin v5        # 4. ПОСЛЕ работы: отправить на GitHub → сайт пересоберётся
```

Можно поставить плагин **Obsidian Git**, но настроить его на **репозиторий** `wand_sign_navigator`, а не на основное хранилище
(иначе личные заметки окажутся рядом с публикуемыми). Если плагин мешает — хватает четырёх команд выше.

### Правила, которые исключают конфликты

1. **Pull в начале, push в конце** каждой сессии. Не оставлять незапушенные правки на ночь.
2. **Сессии Claude** (облачные) работают в ветке `claude/…`. Их изменения попадают в `v5` только через Pull Request.
   После мержа PR — сразу `git pull origin v5` локально.
3. Не править одновременно один и тот же файл в Obsidian и через Claude/веб-интерфейс GitHub.
4. Не переименовывать файлы с карточками в проводнике — только в Obsidian (он обновляет wiki-ссылки),
   и сразу закоммитить переименование.
5. Не запускать `npm run format` (Prettier) на `content/`: он ломает frontmatter
   (пример — дублированный заголовок в `content/00-meta/konventsii.md`).
   Защита: добавить строку `content` в `.prettierignore`.
6. Переводы строк: в репозитории `* text=auto eol=lf`. На Windows один раз выполнить
   `git config core.autocrlf false`, чтобы не получать «изменённые» файлы без реальных правок.

### Если конфликт всё же случился

```bash
git pull origin v5
# CONFLICT (content): Merge conflict in content/01-concepts/xxx.md
```
1. Открыть файл, найти маркеры `<<<<<<<`, `=======`, `>>>>>>>`, оставить нужный текст, удалить маркеры.
2. `git add content/01-concepts/xxx.md && git commit` → `git push origin v5`.

---

## Запасная схема: если ссылку сделать нельзя (две физические копии)

Тогда **одно направление**: Obsidian — источник правды для заметок, репозиторий — только приёмник.

1. Править заметки **только** в Obsidian. В `content/` руками ничего не менять.
2. Перед публикацией: `git pull origin v5`, затем зеркалировать папку:
   - Windows: `robocopy "C:\хранилище\wilson-guide" "C:\…\wand_sign_navigator\content" /MIR /XD .obsidian .trash`
   - macOS/Linux: `rsync -av --delete --exclude .obsidian --exclude .trash "/хранилище/wilson-guide/" "/…/wand_sign_navigator/content/"`
3. `git add content && git commit && git push origin v5`.
4. Если на GitHub появились изменения `content/` (PR от Claude), то после `git pull` скопировать их
   **обратно** в Obsidian (та же команда в обратную сторону) **до** новой правки в Obsidian.

> `/MIR` и `--delete` удаляют в приёмнике файлы, которых нет в источнике. Перед первым запуском обязательно сверить копии.

---

## Первичная сверка трёх копий

Скрипт `scripts/compare_content.py` сравнивает две папки по содержимому (SHA-256), без учёта `.obsidian`/`.trash`,
и показывает, какая копия файла новее.

```bash
cd wand_sign_navigator

# 1. Локальная папка ↔ GitHub
git fetch origin v5
git status                         # незакоммиченные локальные правки
git log --oneline HEAD..origin/v5  # коммиты на GitHub, которых нет локально
git log --oneline origin/v5..HEAD  # локальные коммиты, которых нет на GitHub
git diff --stat origin/v5 -- content

# 2. Локальная папка ↔ Obsidian
python scripts/compare_content.py content "C:/путь/к/хранилищу/wilson-guide"
```

> В PowerShell путь пишется **без `\` в конце**: `"C:\папка\"` превращается в `C:\папка"`, и папка не находится.

Как читать результат и сводить копии:

| Результат | Действие |
|---|---|
| `Только в A` (только в репозитории) | скопировать в Obsidian — или удалить, если файл удалён сознательно |
| `Только в B` (только в Obsidian) | скопировать в `content/` |
| `Разное содержимое` | открыть обе версии, объединить вручную; подсказка `A новее/B новее` — по дате изменения |
| `Отличаются только переводом строк` | не требует действий |

После сверки: `git add content && git commit -m "Сверка с Obsidian" && git push origin v5`, повторно запустить скрипт —
должно быть `ИТОГ: копии совпадают`. Только после этого переходить на схему с junction.

## Эталон GitHub на 08.10.2026

Ветка `v5`, коммит `249506a`. `content/`: 213 файлов, из них 139 `.md`.

| Папка | Файлов |
|---|---|
| `00-meta` | 1 |
| `01-concepts` | 27 |
| `02-metaphors` | 12 (включая `.gitkeep`) |
| `03-people` | 76 + 69 изображений в `assets/` |
| `04-cases` | 5 |
| `05-chapters` | 4 |
| `06-context` | 14 + 3 изображения в `assets/` |
| корень | `index.md`, `README.md` |
