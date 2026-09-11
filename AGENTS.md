# The Farmer Was Replaced

## 语言

- 所有回答和回复使用简体中文。

## 这是什么

这是《The Farmer Was Replaced》（编程农场）的**游戏存档目录**，不是普通 Git / Plastic 工程。

- 可写无人机脚本只在 `Saves/Save0/`。
- `Saves/Save0/__builtins__.py` 是给外部编辑器的类型桩，**不是游戏可执行代码**，不要当运行时实现去改，也不要 `import` 它。
- `Saves/Save0/save.json`、`Backup/`、`Player.log`、`Title.json`、`options.txt`、`steam_autocloud.vdf` 是游戏/Steam 数据。**未明确要求时不要改。**
- `import` 名必须等于游戏编辑器窗口标题。只在磁盘新建 `.py` 不会变成可导入模块。新文件要用户在编辑器里建同名窗口；用户明确要求时可以改 `save.json` 窗口列表，但游戏开着仍可能被 `autosave progress` 冲掉。细则在 `/tfwr-save`。

当前存档选项：`file watcher = enabled`（改**已有** `Saves/Save0/*.py` 会被游戏热读）、`autosave progress = enabled`（游戏开着会重写 `save.json`）、`tabs to spaces = disabled`（必须用 **Tab** 缩进）、`allow locked features = disabled`（未解锁的语法/API 不要写进脚本，除非用户明确说已打开全功能）。

## 工作流程

- 排错或改无人机脚本时，**必须先读工程根 `output.txt`**（与 `AGENTS.md` 同级）。游戏把 `print()` 和运行报错写进这个文件；空文件表示这次没打过 print / 没记下错误。不要凭空猜「脚本没跑」。
- 用户说「有报错 / 看 output」或刚改完脚本时，**必须再跑** `python .agents/skills/tfwr-control/scripts/tfwr_control.py parse`，读 `.agents/error-iter/last.md`。解释器/解析错误才改代码；`sun_wait` 是当前档未熟，不是红字。改完再 parse。要重跑农场必须 `run-main` / `restart`（注入后调用 `MainSim.StartMainExecution`，目标窗口 `main`）。不要操鼠标，不要裸 F5。细则在 `/tfwr-control`。
- 动到 `Saves/Save0`、作物策略、研究树或问「解锁了什么」时，**必须先加载 `/tfwr-save`**，运行 `.agents/skills/tfwr-save/scripts/parse_save.ps1`，按快照只写已解锁 API。公开函数名以 `/tfwr-control` 的 `extract-api` 摘要为准，不要整份反编译游戏逻辑。
- 改种植权重、VALUE、布局、迷宫门槛或收获规则时，再加载 `/tfwr-strategy`，按策略概览改，不要另起一套口径。
- 然后再加载 `/tfwr-farm` 改无人机脚本。不要凭 `__builtins__.py` 或全科技假设写 `get_cost`、`unlock()`、仙人掌、迷宫、恐龙、多无人机。
- 游戏语言是 Python **方言**，不是 CPython。禁止按完整 Python 习惯写 lambda、推导式、三元表达式、`try/except`、标准库 `import`、`f-string`、`int()`/`float()` 等。细则以 skill 为准；API 以存档快照 + 游戏内文档为准。桩文件只给编辑器看。
- 先读现有模块再改：`main.py`、`main_maze.py`、`drone_module.py`、`harvest_module.py`、`plant_module.py`、`sunflower_module.py`、`pumpkin_module.py`、`cactus_module.py`、`dinosaur_module.py`、`move_module.py`、`saved_data_module.py`、`maze_module.py`。不要 `import` 游戏窗口里还没有的文件。农场不要 `import main_maze`。
- 改完 `Saves/Save0` 的策略、布局、收获、走位、迷宫门槛或 tick 缓存后，**必须加载 `/tfwr-sync-skills`**，把事实写回 `.agents/skills/`，不要只改代码。
- 本目录无项目级版本库。禁止自动 `git init` / `git commit`。不要提示 Plastic 提交。

## Skill 单一维护源规则

项目 skill 的唯一权威维护源是 `.agents/skills/`。
`.claude/skills/`、`.grok/skills/` 与 `.cursor/skills/` 为相对路径目录符号链接，目标均为 `../.agents/skills`，分别供 Claude Code、Grok 与 Cursor 发现同一套 skill；禁止再维护第二份镜像副本。

`CLAUDE.md` 与 `GROK.md` 为指向 `AGENTS.md` 的相对路径文件符号链接，不是独立副本。

### 更新义务

- 新增、修改或删除 skill 时，只处理 `.agents/skills/` 中的版本。
- 不得把 `.claude/skills/`、`.grok/skills/` 或 `.cursor/skills/` 当作独立权威源去比较、同步、补齐、复原或重建。
- 同名路径同时可见时，以 `.agents/skills/` 中最新且完整的版本为唯一真值。

### 验证

- 只校验 `.agents/skills/` 内目标 skill 的文件完整性、frontmatter、UTF-8 无 BOM 和引用有效性。

### 编码

- 所有 `.agents/skills/*/SKILL.md` 统一使用 UTF-8 **无 BOM**，frontmatter 从文件首字节 `---` 开始。

### 注意

- 不要把符号链接改回普通目录副本。发现链接缺失/损坏时，**必须自动执行** `.agents/skills/tfwr-farm/scripts/ensure-agent-links.bat`（不要手写 `mklink` 复制 skill 树）。
- 若链接损坏且不便跑脚本，才按同样相对路径重建：

```bat
mklink /D .claude\skills ..\.agents\skills
mklink /D .grok\skills ..\.agents\skills
mklink /D .cursor\skills ..\.agents\skills
mklink CLAUDE.md AGENTS.md
mklink GROK.md AGENTS.md
```
