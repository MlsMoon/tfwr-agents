# TFWR Agents

Agent workspace for **The Farmer Was Replaced** (编程农场).

One canonical skill tree, a one-shot installer, and farm script templates. Your save data stays on your machine.

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

## What you get

- `AGENTS.md` — rules for Cursor / Claude / Grok when this folder is the workspace
- `.agents/skills/` — **the only skill copy**. Claude / Cursor / Grok see it through symlinks created by setup
- `templates/Save0/` — drone scripts (`main`, sunflower, pumpkin, cactus, dinosaur, maze, …)
- `setup.bat` / `setup.ps1` — ask for the save path, copy this repo there, then finish init (skills + farm scripts + links)

## What is not in this repo

- `Saves/` (including `save.json`)
- `Backup/`
- `Player.log`, `output.txt`, `options.txt`, Steam cloud files
- `.claude/skills`, `.grok/skills`, `.cursor/skills` (symlinks, not a second copy)

## Requirements

- The game installed and launched at least once (so the userdata folder exists)
- Windows (setup uses `mklink`; turn on **Developer Mode** if link creation fails)
- [Cursor](https://cursor.com) (or Claude Code / Grok) opened on the **game userdata** folder
- Python 3, for `tfwr_control.py`
- Optional: .NET SDK, only if you rebuild the in-process helper

Default game folder:

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## Initialize (one shot)

Clone **anywhere** (Downloads is fine). You do not need to clone into the save folder.

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

`setup.bat` will **ask you to type the save path**, then **copy this repo into that folder and finish init by itself** (skills, farm scripts, Claude / Cursor / Grok links). No second command.

Default path (press Enter):

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

Hints shown in the bat:

- This is the **save** folder, not `steamapps\common\The Farmer Was Replaced`
- Launch the game once if that folder does not exist yet
- You can paste the path from File Explorer's address bar

Non-interactive:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -GameRoot "C:\Users\YOU\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced"
```

After it succeeds, open **that save folder** in Cursor. The script:

1. Copies `AGENTS.md`, `.agents\skills`, templates, and setup files into the save folder
2. Copies `templates\Save0\*.py` into `Saves\Save0` — **never writes `save.json`**
3. Creates:

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

Skills only, keep your current drone files:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

If a new `.py` appears in `Saves\Save0`, open the **in-game** editor and create a window with the **same title**. A file on disk is not an importable module.

## Use

1. Open the userdata folder in Cursor (the folder that contains `AGENTS.md` and `Saves\Save0`).
2. In the game: `file watcher = enabled`, `tabs to spaces = disabled`. See `options.example.txt`.
3. Start the farm from a terminal in that folder:

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. Do **not** press F5. F5 runs the focused editor window, which is often not `main`.
5. Do **not** run `main_maze` when you want the farm. Maze is gold only.
6. Existing `Saves\Save0\*.py` hot-reload when file watcher is on. After a strategy change, sync facts back into `.agents\skills` (`/tfwr-sync-skills`).

Useful commands (same folder):

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| Command | Meaning |
| --- | --- |
| `run-main` / `restart` | Start `main` via the game API (no mouse) |
| `parse` | Classify `output.txt` (errors vs `sun_wait` / `dino`) |
| `snapshot` | Inventory, drones, speed, logger |
| `stop` | `StopMainExecution` |

## Skills

| Skill | When |
| --- | --- |
| `/tfwr-farm` | Edit drone scripts (dialect, Tab indent, modules) |
| `/tfwr-strategy` | VALUE, `pick_mode`, sunflower / pumpkin / cactus / dino |
| `/tfwr-save` | What the save has unlocked |
| `/tfwr-control` | Start `main`, parse output, snapshot |
| `/tfwr-sync-skills` | After a farm change, update `.agents/skills` only |

Edit skills only under `.agents/skills/`. Never maintain a second tree under `.claude` / `.grok` / `.cursor`.

## Farm scripts

Templates are copied into **your** `Saves\Save0`. They expect windows named:

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py` is an editor stub. Do not `import` it in the game.

To copy your live scripts back into git templates:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## Notes

- No license file. Use at your own risk.
- Do not `set_world_size` to expand the farm (it clears the field).
- Do not `unlock()` unless you explicitly want that.
- Indent with **Tab**.
