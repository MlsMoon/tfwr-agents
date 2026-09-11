# TFWR Agents

Agent-Arbeitsbereich für **The Farmer Was Replaced**.

Ein kanonischer Skill-Baum, Ein-Klick-Installation und Farm-Skriptvorlagen. Spielstände liegen nicht im Repo.

**[English](../README.md)** ·
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

## Enthalten

- `AGENTS.md` — Regeln für Cursor / Claude / Grok, wenn dieser Ordner der Workspace ist
- `.agents/skills/` — **die einzige Skill-Kopie**. Claude / Cursor / Grok finden sie über Symlinks von setup
- `templates/Save0/` — Drohnen-Skripte (`main`, Sonnenblume, Kürbis, Kaktus, Dinosaurier, Labyrinth, …)
- `setup.bat` / `setup.ps1` — zuerst Sprache, dann Save-Pfad; kopiert das Repo und schließt Init selbst ab
- `i18n/` — übersetzte READMEs und Setup-Texte. Die Repo-Wurzel bleibt Englisch

## Nicht enthalten

- `Saves/` (einschließlich `save.json`)
- `Backup/`
- `Player.log`, `output.txt`, `options.txt`, Steam-Cloud-Dateien
- `.claude/skills`, `.grok/skills`, `.cursor/skills` (nur Links, keine zweite Kopie)

## Voraussetzungen

- Spiel installiert und mindestens einmal gestartet (Userdata-Ordner)
- Windows (`mklink`; bei Fehlern **Entwicklermodus** einschalten)
- [Cursor](https://cursor.com) (oder Claude Code / Grok) auf dem **Userdata-Ordner**
- Python 3 für `tfwr_control.py`
- Optional: .NET SDK, nur zum Neu-Bauen des Helpers

Standardordner:

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## Initialisieren (einmal)

Beliebig klonen. Muss nicht im Save-Ordner liegen.

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

`setup.bat` fragt zuerst nach der **Sprache** (`en`, `zh-CN`, `de`, …), dann nach dem Save-Pfad, **kopiert dieses Repo dorthin und schließt die Initialisierung selbst ab**. Kein zweiter Befehl.

Standard (Enter):

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

Hinweis: Save-Ordner, nicht Steam-Install. Ordner fehlt? Spiel einmal starten.

Danach den **Save-Ordner** in Cursor öffnen. Das Skript:

1. kopiert `AGENTS.md`, `.agents\skills`, Vorlagen und Setup in den Save-Ordner
2. kopiert `templates\Save0\*.py` nach `Saves\Save0` — **schreibt nie `save.json`**
3. erstellt:

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

Nur Skills, Drohnen-Dateien behalten:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

Neue `.py` in `Saves\Save0` brauchen ein **gleichnamiges Fenster** im **Spiel-Editor**. Eine Datei auf der Platte allein ist kein importierbares Modul.

## Nutzung

1. Userdata-Ordner in Cursor öffnen (`AGENTS.md` und `Saves\Save0`).
2. Im Spiel: `file watcher = enabled`, `tabs to spaces = disabled`. Siehe `options.example.txt`.
3. Farm im Terminal dieses Ordners starten:

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **Nicht F5.** F5 startet das fokussierte Fenster, oft nicht `main`.
5. Für die Farm **nicht `main_maze`** ausführen. Das Labyrinth farmt nur Gold.
6. Bei aktivem File Watcher laden vorhandene `Saves\Save0\*.py` heiß nach. Nach Strategieänderungen `/tfwr-sync-skills` auf `.agents\skills`.

Nützliche Befehle (gleicher Ordner):

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| Befehl | Bedeutung |
| --- | --- |
| `run-main` / `restart` | `main` über die Spiel-API (ohne Maus) |
| `parse` | `output.txt` klassifizieren |
| `snapshot` | Inventar, Drohnen, Tempo, Logger |
| `stop` | `StopMainExecution` |

## Skills

| Skill | Wann |
| --- | --- |
| `/tfwr-farm` | Drohnen-Skripte (Dialekt, Tab, Module) |
| `/tfwr-strategy` | VALUE, `pick_mode`, Sonnenblume / Kürbis / Kaktus / Dino |
| `/tfwr-save` | Freischaltungen des Saves |
| `/tfwr-control` | `main` starten, Output, Snapshot |
| `/tfwr-sync-skills` | Nach Farm-Änderungen nur `.agents/skills` |

Skills nur unter `.agents/skills/` ändern. Keinen zweiten Baum unter `.claude` / `.grok` / `.cursor`.

## Farm-Skripte

Vorlagen landen in **deinem** `Saves\Save0`. Fensternamen:

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py` ist ein Editor-Stub. Nicht im Spiel `import`ieren.

Live-Skripte zurück ins Git-Template:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## Hinweise

- Keine Lizenzdatei. Nutzung auf eigene Gefahr.
- Nicht `set_world_size` zum Vergrößern (räumt das Feld).
- Nicht `unlock()`, außer du willst das ausdrücklich.
- Einrückung mit **Tab**.
