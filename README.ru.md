# TFWR Agents

Рабочее пространство Agent для **The Farmer Was Replaced**.

Одно каноническое дерево skills, установка одной командой и шаблоны скриптов. Сохранения в репозиторий не попадают.

**[English](README.md)** ·
**[简体中文](README.zh-CN.md)** ·
**[繁體中文](README.zh-TW.md)** ·
**[日本語](README.ja.md)** ·
**[한국어](README.ko.md)** ·
**[Deutsch](README.de.md)** ·
**[Français](README.fr.md)** ·
**[Español](README.es.md)** ·
**[Português](README.pt-BR.md)** ·
**[Русский](README.ru.md)** ·
**[Tiếng Việt](README.vi.md)** ·
**[Bahasa Indonesia](README.id.md)**

## Что внутри

- `AGENTS.md` — правила для Cursor / Claude / Grok, когда эта папка — workspace
- `.agents/skills/` — **единственная копия skills**. Редакторы видят её через ссылки setup
- `templates/Save0/` — скрипты дрона (`main`, подсолнух, тыква, кактус, динозавр, лабиринт, …)
- `setup.bat` / `setup.ps1` — копирует skills и скрипты в папку игры и создаёт ссылки

## Чего нет

- `Saves/` (включая `save.json`)
- `Backup/`
- `Player.log`, `output.txt`, `options.txt`, файлы Steam Cloud
- `.claude/skills`, `.grok/skills`, `.cursor/skills` (только ссылки, не вторая копия)

## Требования

- Игра установлена и хотя бы раз запущена (папка userdata)
- Windows (`mklink`; при ошибке включите **режим разработчика**)
- [Cursor](https://cursor.com) (или Claude Code / Grok) открыт на **папке userdata**
- Python 3 для `tfwr_control.py`
- По желанию: .NET SDK, только чтобы пересобрать helper

Папка по умолчанию:

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## Инициализация (одна команда)

Клонируйте куда угодно. Не обязательно в папку сейва.

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

`setup.bat` **спросит путь к сейву**, **скопирует репозиторий туда и сам закончит init**. Вторая команда не нужна.

Путь по умолчанию (Enter):

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

Подсказка: папка **сейва**, не установки Steam. Если её нет — один раз запустите игру.

Потом откройте **эту папку сейва** в Cursor. Скрипт:

1. копирует `AGENTS.md`, `.agents\skills`, шаблоны и setup в папку сейва
2. копирует `templates\Save0\*.py` в `Saves\Save0` — **никогда не пишет `save.json`**
3. создаёт:

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

Только skills, оставить текущие скрипты дрона:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

Новый `.py` в `Saves\Save0` требует **окно с тем же именем** в **внутриигровом** редакторе. Файл на диске сам по себе не импортируется.

## Использование

1. Откройте папку userdata в Cursor (`AGENTS.md` и `Saves\Save0`).
2. В игре: `file watcher = enabled`, `tabs to spaces = disabled`. См. `options.example.txt`.
3. Запустите ферму в терминале этой папки:

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **Не нажимайте F5.** F5 запускает активное окно, часто не `main`.
5. Для фермы **не запускайте `main_maze`**. Лабиринт фармит только золото.
6. При file watcher существующие `Saves\Save0\*.py` подхватываются на лету. После смены стратегии — `/tfwr-sync-skills` в `.agents\skills`.

Полезные команды (та же папка):

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| Команда | Смысл |
| --- | --- |
| `run-main` / `restart` | Запуск `main` через API игры (без мыши) |
| `parse` | Разбор `output.txt` |
| `snapshot` | Инвентарь, дроны, скорость, лог |
| `stop` | `StopMainExecution` |

## Skills

| Skill | Когда |
| --- | --- |
| `/tfwr-farm` | Скрипты дрона (диалект, Tab, модули) |
| `/tfwr-strategy` | VALUE, `pick_mode`, подсолнух / тыква / кактус / дино |
| `/tfwr-save` | Что открыто в сейве |
| `/tfwr-control` | Запуск `main`, output, снимок |
| `/tfwr-sync-skills` | После правок фермы обновить только `.agents/skills` |

Править skills только в `.agents/skills/`. Не держите второе дерево в `.claude` / `.grok` / `.cursor`.

## Скрипты фермы

Шаблоны копируются в **ваш** `Saves\Save0`. Имена окон:

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py` — заглушка для редактора. Не `import` в игре.

Выгрузить рабочие скрипты обратно в git-шаблоны:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## Замечания

- Файла лицензии нет. Используйте на свой риск.
- Не расширяйте поле через `set_world_size` (оно очищается).
- Не вызывайте `unlock()`, если сами об этом не просили.
- Отступы только **Tab**.
