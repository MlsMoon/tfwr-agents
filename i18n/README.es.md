# TFWR Agents

Espacio de trabajo de Agent para **The Farmer Was Replaced**.

Un solo árbol canónico de skills, instalador de un paso y plantillas de scripts. La partida no entra en el repositorio.

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

## Qué incluye

- `AGENTS.md` — reglas para Cursor / Claude / Grok cuando esta carpeta es el workspace
- `.agents/skills/` — **la única copia de skills**. Los editores las ven por los enlaces de setup
- `templates/Save0/` — scripts del dron (`main`, girasol, calabaza, cactus, dinosaurio, laberinto, …)
- `setup.bat` / `setup.ps1` — primero el idioma, luego la ruta de guardado; copia el repo y termina la init
- `i18n/` — README traducidos y textos de instalación. La raíz del repo sigue en inglés

## Qué no incluye

- `Saves/` (incluido `save.json`)
- `Backup/`
- `Player.log`, `output.txt`, `options.txt`, archivos de Steam Cloud
- `.claude/skills`, `.grok/skills`, `.cursor/skills` (enlaces, no una segunda copia)

## Requisitos

- Juego instalado y abierto al menos una vez (carpeta de userdata)
- Windows (`mklink`; activa el **modo de desarrollador** si falla)
- [Cursor](https://cursor.com) (o Claude Code / Grok) abierto en la **carpeta de userdata**
- Python 3 para `tfwr_control.py`
- Opcional: SDK de .NET, solo para recompilar el helper

Carpeta por defecto:

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## Inicializar (un paso)

Clona donde quieras. No hace falta que sea la carpeta de guardado.

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

`setup.bat` pide primero el **idioma** (`en`, `zh-CN`, `es`, …), luego la ruta de guardado, **copia este repo ahí y termina la init solo**. No hace falta un segundo comando.

Ruta por defecto (Enter):

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

Pista: carpeta de **guardado**, no la instalación de Steam. Si no existe, abre el juego una vez.

Luego abre **esa carpeta de guardado** en Cursor. El script:

1. copia `AGENTS.md`, `.agents\skills`, plantillas y setup a la carpeta de guardado
2. copia `templates\Save0\*.py` a `Saves\Save0` — **nunca escribe `save.json`**
3. crea:

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

Solo skills, conservar tus scripts actuales:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

Un `.py` nuevo en `Saves\Save0` necesita una **ventana con el mismo nombre** en el editor **del juego**. Un archivo en disco no es un módulo importable.

## Uso

1. Abre la carpeta de userdata en Cursor (`AGENTS.md` y `Saves\Save0`).
2. En el juego: `file watcher = enabled`, `tabs to spaces = disabled`. Ver `options.example.txt`.
3. Arranca la granja en un terminal de esa carpeta:

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **No pulses F5.** F5 ejecuta la ventana enfocada, a menudo no `main`.
5. Para la granja **no ejecutes `main_maze`**. El laberinto solo farmea oro.
6. Con file watcher, los `Saves\Save0\*.py` existentes se recargan. Tras un cambio de estrategia, `/tfwr-sync-skills` hacia `.agents\skills`.

Comandos útiles (misma carpeta):

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| Comando | Significado |
| --- | --- |
| `run-main` / `restart` | Arranca `main` por la API del juego (sin ratón) |
| `parse` | Clasifica `output.txt` |
| `snapshot` | Inventario, drones, velocidad, registro |
| `stop` | `StopMainExecution` |

## Skills

| Skill | Cuándo |
| --- | --- |
| `/tfwr-farm` | Scripts del dron (dialecto, Tab, módulos) |
| `/tfwr-strategy` | VALUE, `pick_mode`, girasol / calabaza / cactus / dino |
| `/tfwr-save` | Desbloqueos de la partida |
| `/tfwr-control` | Arrancar `main`, output, snapshot |
| `/tfwr-sync-skills` | Tras un cambio, actualizar solo `.agents/skills` |

Edita skills solo en `.agents/skills/`. No mantengas un segundo árbol en `.claude` / `.grok` / `.cursor`.

## Scripts de granja

Las plantillas van a **tu** `Saves\Save0`. Nombres de ventana:

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py` es un stub del editor. No lo `import`es en el juego.

Exportar tus scripts vivos a las plantillas git:

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## Notas

- No hay archivo de licencia. Úsalo bajo tu responsabilidad.
- No uses `set_world_size` para ampliar (limpia el campo).
- No llames `unlock()` salvo que lo pidas explícitamente.
- Sangría con **Tab**.
