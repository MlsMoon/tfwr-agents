# TFWR Agents

Espace de travail Agent pour **The Farmer Was Replaced**.

Une seule arborescence de skills, un installeur en une commande, et des modèles de scripts. Les sauvegardes ne sont pas dans le dépôt.

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

## Contenu

- `AGENTS.md` — règles Cursor / Claude / Grok quand ce dossier est le workspace
- `.agents/skills/` — **la seule copie des skills**. Les outils les voient via les liens créés par setup
- `templates/Save0/` — scripts de drone (`main`, tournesol, citrouille, cactus, dinosaure, labyrinthe, …)
- `setup.bat` / `setup.ps1` — d’abord la langue, puis le chemin de sauvegarde ; copie et termine l’init
- `i18n/` — README traduits et textes d’install. La racine du dépôt reste en anglais

## Hors dépôt

- `Saves/` (y compris `save.json`)
- `Backup/`
- `Player.log`, `output.txt`, `options.txt`, fichiers Steam Cloud
- `.claude/skills`, `.grok/skills`, `.cursor/skills` (liens, pas une seconde copie)

## Prérequis

- Jeu installé et lancé au moins une fois (dossier userdata)
- Windows (`mklink` ; activez le **mode développeur** en cas d’échec)
- [Cursor](https://cursor.com) (ou Claude Code / Grok) ouvert sur le **dossier userdata**
- Python 3 pour `tfwr_control.py`
- Optionnel : SDK .NET, seulement pour recompiler l’helper

Dossier par défaut :

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## Initialisation (une commande)

Clonez n’importe où. Pas besoin d’être dans le dossier de sauvegarde.

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

`setup.bat` demande d’abord la **langue** (`en`, `zh-CN`, `fr`, …), puis le chemin de sauvegarde, **copie ce dépôt dedans et termine l’init tout seul**. Pas de seconde commande.

Chemin par défaut (Entrée) :

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

Astuce : dossier de **sauvegarde**, pas l’install Steam. S’il n’existe pas, lancez le jeu une fois.

Ensuite ouvrez **ce dossier de sauvegarde** dans Cursor. Le script :

1. copie `AGENTS.md`, `.agents\skills`, modèles et setup dans le dossier de sauvegarde
2. copie `templates\Save0\*.py` vers `Saves\Save0` — **n’écrit jamais `save.json`**
3. crée :

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

Skills seulement, garder vos scripts actuels :

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

Un nouveau `.py` dans `Saves\Save0` exige une **fenêtre du même nom** dans l’éditeur **en jeu**. Un fichier disque seul n’est pas importable.

## Utilisation

1. Ouvrez le dossier userdata dans Cursor (`AGENTS.md` et `Saves\Save0`).
2. Dans le jeu : `file watcher = enabled`, `tabs to spaces = disabled`. Voir `options.example.txt`.
3. Démarrez la ferme dans un terminal de ce dossier :

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **Ne pas appuyer sur F5.** F5 exécute la fenêtre au premier plan, souvent pas `main`.
5. Pour la ferme, **ne pas lancer `main_maze`**. Le labyrinthe ne farm que l’or.
6. Avec le file watcher, les `Saves\Save0\*.py` existants se rechargent. Après un changement de stratégie, `/tfwr-sync-skills` vers `.agents\skills`.

Commandes utiles (même dossier) :

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| Commande | Rôle |
| --- | --- |
| `run-main` / `restart` | Démarre `main` via l’API du jeu (sans souris) |
| `parse` | Classe `output.txt` |
| `snapshot` | Inventaire, drones, vitesse, logs |
| `stop` | `StopMainExecution` |

## Skills

| Skill | Quand |
| --- | --- |
| `/tfwr-farm` | Scripts drone (dialecte, Tab, modules) |
| `/tfwr-strategy` | VALUE, `pick_mode`, tournesol / citrouille / cactus / dino |
| `/tfwr-save` | Déblocages de la sauvegarde |
| `/tfwr-control` | Lancer `main`, output, snapshot |
| `/tfwr-sync-skills` | Après un changement, mettre à jour seulement `.agents/skills` |

N’éditez les skills que dans `.agents/skills/`. Pas de second arbre sous `.claude` / `.grok` / `.cursor`.

## Scripts de ferme

Les modèles vont dans **votre** `Saves\Save0`. Noms de fenêtres :

`main`, `main_maze`, `drone_module`, `plant_module`, `saved_data_module`, `harvest_module`, `move_module`, `sunflower_module`, `pumpkin_module`, `cactus_module`, `dinosaur_module`, `maze_module`

`__builtins__.py` est un stub éditeur. Ne pas l’`import`er en jeu.

Renvoyer vos scripts vivants vers les modèles git :

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## Notes

- Pas de fichier de licence. Usage à vos risques.
- Ne pas agrandir avec `set_world_size` (vide le champ).
- Ne pas appeler `unlock()` sauf demande explicite.
- Indentation en **Tab**.
