# TFWR Agents

《The Farmer Was Replaced》（程式農場）的 Agent 工作區。

只維護一份權威 skill、一鍵安裝，以及農場腳本範本。你的存檔不會進倉庫。

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

## 倉庫裡有什麼

- `AGENTS.md` — 把遊戲使用者目錄當成工作區時，Cursor / Claude / Grok 要遵守的規則
- `.agents/skills/` — **唯一的 skill 真源**。Claude / Cursor / Grok 透過安裝腳本建立的符號連結來發現它
- `templates/Save0/` — 無人機腳本（`main`、向日葵、南瓜、仙人掌、恐龍、迷宮等）
- `setup.bat` / `setup.ps1` — 把 skill 與腳本拷進遊戲目錄，並建立連結

## 倉庫裡沒有什麼

- `Saves/`（包括 `save.json`）
- `Backup/`
- `Player.log`、`output.txt`、`options.txt`、Steam 雲端檔
- `.claude/skills`、`.grok/skills`、`.cursor/skills`（只是連結，不是第二份副本）

## 環境需求

- 遊戲已安裝並至少執行過一次（才會有使用者目錄）
- Windows（使用 `mklink`；失敗時請開啟**開發人員模式**）
- 用 [Cursor](https://cursor.com)（或 Claude Code / Grok）開啟**遊戲使用者目錄**
- Python 3，用來跑 `tfwr_control.py`
- 可選：.NET SDK，只有要重編注入輔助程式時才需要

預設遊戲目錄：

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## 一鍵初始化

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

腳本會：

1. 找到遊戲使用者目錄（或使用 `-GameRoot`）
2. 把 `AGENTS.md` 與 `.agents\skills` 拷過去（若已在該目錄則略過）
3. 把 `templates\Save0\*.py` 拷進 `Saves\Save0` — **絕不寫入 `save.json`**
4. 建立：

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

自訂路徑：

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -GameRoot "D:\path\TheFarmerWasReplaced"
```

只裝 skill、保留你現在的無人機腳本：

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

若 `Saves\Save0` 多了新的 `.py`，還要在**遊戲內**編輯器建立**同名視窗**。只在磁碟建檔不能 `import`。

## 使用

1. 用 Cursor 開啟使用者目錄（裡面有 `AGENTS.md` 與 `Saves\Save0`）。
2. 遊戲裡開啟：`file watcher = enabled`，`tabs to spaces = disabled`。見 `options.example.txt`。
3. 在該目錄的終端機啟動農場：

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **不要按 F5**。F5 只跑目前焦點視窗，常常不是 `main`。
5. 跑農場時 **不要執行 `main_maze`**。迷宮只刷金子。
6. 開啟 file watcher 後，既有的 `Saves\Save0\*.py` 會熱讀。改完策略要用 `/tfwr-sync-skills` 把事實寫回 `.agents\skills`。

常用命令（同一目錄）：

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| 命令 | 作用 |
| --- | --- |
| `run-main` / `restart` | 用遊戲內部 API 啟動 `main`（不操作滑鼠） |
| `parse` | 分類 `output.txt`（紅字 vs `sun_wait` / `dino`） |
| `snapshot` | 庫存、無人機、速度、日誌 |
| `stop` | `StopMainExecution` |

## Skill

| Skill | 何時用 |
| --- | --- |
| `/tfwr-farm` | 改無人機腳本（方言、Tab、模組） |
| `/tfwr-strategy` | VALUE、`pick_mode`、向日葵 / 南瓜 / 仙人掌 / 恐龍 |
| `/tfwr-save` | 目前存檔解鎖了什麼 |
| `/tfwr-control` | 啟動 `main`、看 output、快照 |
| `/tfwr-sync-skills` | 改完農場後只更新 `.agents/skills` |

只改 `.agents/skills/`。不要在 `.claude` / `.grok` / `.cursor` 再維護一份。

## 農場腳本

範本會拷進**你自己的** `Saves\Save0`。視窗名稱需要是：

`main`、`main_maze`、`drone_module`、`plant_module`、`saved_data_module`、`harvest_module`、`move_module`、`sunflower_module`、`pumpkin_module`、`cactus_module`、`dinosaur_module`、`maze_module`

`__builtins__.py` 只給外部編輯器看，遊戲裡不要 `import`。

把正在用的腳本導回 git 範本：

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## 說明

- 沒有授權條款檔。後果自負。
- 不要用 `set_world_size` 擴地（會清場）。
- 不要自動 `unlock()`，除非你明確要求。
- 縮排必須用 **Tab**。
