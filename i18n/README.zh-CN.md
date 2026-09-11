# TFWR Agents

《The Farmer Was Replaced》（编程农场）的 Agent 工作区。

只维护一份权威 skill、一键安装，以及农场脚本模板。你的存档不会进仓库。

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

## 仓库里有什么

- `AGENTS.md` — 把游戏用户目录当成工作区时，Cursor / Claude / Grok 要遵守的规则
- `.agents/skills/` — **唯一的 skill 真源**。Claude / Cursor / Grok 通过安装脚本建的符号链接来发现它
- `templates/Save0/` — 无人机脚本（`main`、向日葵、南瓜、仙人掌、恐龙、迷宫等）
- `setup.bat` / `setup.ps1` — 先选语言，再问存档路径，把本仓库拷进去并自动做完初始化
- `i18n/` — 多语言 README 和安装提示。仓库根目录只保留英文

## 仓库里没有什么

- `Saves/`（包括 `save.json`）
- `Backup/`
- `Player.log`、`output.txt`、`options.txt`、Steam 云文件
- `.claude/skills`、`.grok/skills`、`.cursor/skills`（只是链接，不是第二份副本）

## 环境要求

- 游戏已安装并至少运行过一次（才会有用户目录）
- Windows（用 `mklink`；失败时打开**开发人员模式**）
- 用 [Cursor](https://cursor.com)（或 Claude Code / Grok）打开**游戏用户目录**
- Python 3，用来跑 `tfwr_control.py`
- 可选：.NET SDK，只有要重编注入辅助程序时才需要

默认游戏目录：

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

## 一键初始化

仓库可以克隆到**任何地方**（如下载文件夹），不必先放进存档目录。

```bat
git clone https://github.com/MlsMoon/tfwr-agents.git
cd tfwr-agents
setup.bat
```

双击或运行 `setup.bat` 后会**先让你输入语言**（`en`、`zh-CN`、`ja` 等），再问存档路径，然后**自动把自己拷进该目录并做完初始化**。不用再跑第二步。

默认语言是英文（直接回车）。默认路径（再回车一次）：

`%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced`

选好语言之后的提示：

- 填的是【存档】目录，不是 `steamapps\common\The Farmer Was Replaced`
- 如果文件夹不存在，先启动一次游戏
- 可以从资源管理器地址栏复制路径再粘贴

不弹窗、直接指定路径：

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -Lang zh-CN -GameRoot "C:\Users\你\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced"
```

成功后，用 Cursor 打开**那个存档目录**。脚本会：

1. 把 `AGENTS.md`、`.agents\skills`、模板和 setup 拷进存档目录
2. 把 `templates\Save0\*.py` 拷进 `Saves\Save0` — **绝不写 `save.json`**
3. 创建：

```
.claude\skills  ->  ..\.agents\skills
.grok\skills    ->  ..\.agents\skills
.cursor\skills  ->  ..\.agents\skills
CLAUDE.md       ->  AGENTS.md
GROK.md         ->  AGENTS.md
```

只装 skill、保留你现在的无人机脚本：

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -SkipFarmScripts
```

如果 `Saves\Save0` 里多了新的 `.py`，还要在**游戏内**编辑器建一个**同名窗口**。只在磁盘建文件不能 `import`。

## 使用

1. 用 Cursor 打开用户目录（里面有 `AGENTS.md` 和 `Saves\Save0`）。
2. 游戏里打开：`file watcher = enabled`，`tabs to spaces = disabled`。见 `options.example.txt`。
3. 在该目录的终端启动农场：

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py run-main
```

4. **不要按 F5**。F5 只跑当前焦点窗口，经常不是 `main`。
5. 跑农场时 **不要执行 `main_maze`**。迷宫只刷金子。
6. 打开 file watcher 后，已有的 `Saves\Save0\*.py` 会热读。改完策略要用 `/tfwr-sync-skills` 把事实写回 `.agents\skills`。

常用命令（同一目录）：

```bat
python .agents\skills\tfwr-control\scripts\tfwr_control.py parse
python .agents\skills\tfwr-control\scripts\tfwr_control.py snapshot
python .agents\skills\tfwr-control\scripts\tfwr_control.py stop
```

| 命令 | 作用 |
| --- | --- |
| `run-main` / `restart` | 用游戏内部 API 启动 `main`（不操鼠标） |
| `parse` | 分类 `output.txt`（红字 vs `sun_wait` / `dino`） |
| `snapshot` | 库存、无人机、速度、日志 |
| `stop` | `StopMainExecution` |

## Skill

| Skill | 何时用 |
| --- | --- |
| `/tfwr-farm` | 改无人机脚本（方言、Tab、模块） |
| `/tfwr-strategy` | VALUE、`pick_mode`、向日葵 / 南瓜 / 仙人掌 / 恐龙 |
| `/tfwr-save` | 当前存档解锁了什么 |
| `/tfwr-control` | 启动 `main`、看 output、快照 |
| `/tfwr-sync-skills` | 改完农场后只更新 `.agents/skills` |

只改 `.agents/skills/`。不要在 `.claude` / `.grok` / `.cursor` 再维护一份。

## 农场脚本

模板会拷进**你自己的** `Saves\Save0`。窗口名需要是：

`main`、`main_maze`、`drone_module`、`plant_module`、`saved_data_module`、`harvest_module`、`move_module`、`sunflower_module`、`pumpkin_module`、`cactus_module`、`dinosaur_module`、`maze_module`

`__builtins__.py` 只给外部编辑器看，游戏里不要 `import`。

把正在用的脚本导回 git 模板：

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File setup.ps1 -ExportFarm
```

## 说明

- 没有许可证文件。后果自负。
- 不要用 `set_world_size` 扩地（会清场）。
- 不要自动 `unlock()`，除非你明确要求。
- 缩进必须用 **Tab**。
