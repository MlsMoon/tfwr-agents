---
name: tfwr-farm
description: >
  Writes and edits The Farmer Was Replaced (TFWR / 编程农场) drone scripts
  in the game DSL. Use when changing Saves/Save0, harvest/plant/move/water
  loops, pumpkins, sunflowers, trees, mazes, cacti, dinosaurs, polyculture,
  multi-drone, leaderboards, or when the user mentions 无人机 / 农场脚本.
---

# TFWR Farm

改本存档的无人机脚本时加载本 skill。权威规则在工程根 `AGENTS.md`。只维护 `.agents/skills/`。

改之前先读工程根 `output.txt`，再跑 `/tfwr-control` 的 `parse`，再加载 `/tfwr-save` 并跑 `scripts/parse_save.ps1`。只写快照里已解锁的 API。

## output.txt

工程根（与 `AGENTS.md` 同级）的 `output.txt` 是游戏输出文件。`print()` 和脚本报错会写到这里。`quick_print()` 多半只在游戏窗口，不一定进这个文件。

排错、改 `main_maze` / 农场脚本、用户说「跑不了 / 报错」时，**先读这个文件，再跑** `python .agents/skills/tfwr-control/scripts/tfwr_control.py parse`。摘要在 `.agents/error-iter/last.md`。空文件只说明没 print、或游戏还没写出，不能当成「没有错误」。`sun_wait` 是当前最大档未熟，不是解释器红字。失败原因用 `print()`（不要每格打），方便下次对照。需要重跑农场时用 `/tfwr-control` 的 `run-main`（注入调用 `MainSim.StartMainExecution`）。不要操鼠标，不要裸 F5。`print("boot main")` 是确认入口已执行，不要删。

## 先读再改

1. 确认工作区是游戏存档根目录（含 `Saves/Save0/` 与 `AGENTS.md`）。先读 `output.txt`。
2. 先读现有模块，再动手：
  - `Saves/Save0/main.py` — 只扫田，不读金子、不开迷宫。保留 `# TFWR_RUN_MAIN`；启动用 `/tfwr-control` 的 `run-main`
  - `Saves/Save0/main_maze.py` — 刷金子入口；不要被农场 `import`
  - `Saves/Save0/drone_module.py` — `run_mode` 分发；填料列 + 伴侣
  - `Saves/Save0/harvest_module.py` — 填料成熟就收；特殊作物只清错格
  - `Saves/Save0/plant_module.py` — `pick_mode` / `spawn_columns` / 伴侣 / 水肥
  - `Saves/Save0/sunflower_module.py` — 整田种、按花瓣档位多人收，至少留 10 朵拿 8 倍；工人只走目标 y；发完回家再等；当前档未熟就地施肥
  - `Saves/Save0/pumpkin_module.py` — 补坏南瓜、对角 `measure` 同 ID 再收
  - `Saves/Save0/cactus_module.py` — 整田种、列南北/行东西排序、西南角收
  - `Saves/Save0/dinosaur_module.py` — 清场戴帽、固定圈走位、摘帽再开一轮
  - `Saves/Save0/move_module.py` — `go_to`；恐龙戴帽时不要用
  - `Saves/Save0/maze_module.py` — 生成迷宫、分叉 `spawn_drone`、`run_maze`；失败 `print` 到 `output.txt`
  - `Saves/Save0/saved_data_module.py` — `tile_plan` / `layout_box`、当前模式、轮次锁、花瓣/仙人掌表
3. `__builtins__.py` 是编辑器桩，不要当运行时实现去改，也不要 `import`。
4. 策略决策先读 `/tfwr-strategy`。方言与当前田块接线见：
   - [dialect.md](references/dialect.md)
   - [farm-layout.md](references/farm-layout.md)

## 硬约束

- 语言是游戏 DSL，不是 CPython。按 [dialect.md](references/dialect.md) 写，写完用方言清单自检。
- 缩进用 **Tab**，与 `options.txt` 的 `tabs to spaces = disabled` 以及现有模块一致。
- `allow locked features = disabled`：快照未解锁的 API 不要写。以 `parse_save.ps1` 为准。Megafarm 已解锁，农场/迷宫用 `spawn_drone` / `wait_for` / `num_drones` / `max_drones`。不要自动 `unlock()`。不要用 `set_world_size` 改田（会清场）。
- `import` 只能引用游戏内其它脚本文件（如 `import saved_data_module`），禁止标准库。名字必须和编辑器窗口标题一致。只在磁盘新建 `.py` 不够，游戏会报「不存在具有此名称的模块」。用户明确要求时可以把窗口名写入 `save.json`；游戏开着仍可能被 `autosave progress` 冲掉。细则见 `/tfwr-save`。
- 空值比较用 `== None` / `!= None`，不用 `is`。
- 未要求时不要改 `save.json`、`Backup/`、日志、主题、Steam 云文件。
- 不要无故推倒现有模块结构。优先在对应模块里改：种植进 `plant_module`，填料收获进 `harvest_module`，向日葵进 `sunflower_module`，南瓜进 `pumpkin_module`，仙人掌进 `cactus_module`，恐龙进 `dinosaur_module`，分发进 `drone_module`，跨格状态进 `saved_data_module`。

## 改代码时

- 无人机只看脚下。要看别的格子必须走过去，或用已有内存表（`saved_data_module`）。
- 成功的 `move` / `harvest` / `plant` / `till` / `use_item` 约 `200` tick；`can_*` / `get_*` / `measure` / `num_items` 约 `1` tick。函数调用本身是 0；热路径写 `模块.函数`。少做无效动作和整表扫描。
- 世界边缘会环绕。回原点用向西/向南走到 `0`，不要假设不会绕回。
- 地面：胡萝卜、南瓜、向日葵需要 `Grounds.Soil`；草地/灌木通常要草地。`till()` 在土壤与草地间切换。
- 草被 `harvest()` 后实体仍在。要用土壤时先 `till()`。
- 原点 `pick_mode()` 一波一个模式。草 VALUE 2、Power VALUE 40、南瓜/骨头 VALUE 80。向日葵在 Power `< 16000` 时进候选，低于 500 强制上场，占整田。按花瓣档位多人收，至少留 10 朵拿 8 倍；工人只走目标 y；发完最后一列先回家再等。档位没收完不要补种；当前档未熟就地施肥。只剩 10 朵才放锁。南瓜对角 `measure` 同 ID 再收。仙人掌整田排序后收到西南角。填料种下后 `get_companion`。恐龙单机走哈密顿圈并朝苹果抄近路，走不动再摘帽；一波只 `clear()` 一次。农场圈开头调一次 `refresh_size()`，热路径不要每格 `ensure_world_size(get_world_size())`。
- 改完策略/布局/收获/走位后加载 `/tfwr-sync-skills`，只改 `.agents/skills/`。
- 树：紧邻其它树会变慢。现逻辑按 `(x+y)%2` 棋盘格种树，方便多无人机。
- Power 在库存 `> 0` 时自动 2× 移速。
- `print()` 会停约 1 秒，并写入工程根 `output.txt`。热路径用 `quick_print()`。失败原因用 `print()`，方便读文件排错。
- 多无人机：工人内存独立。布局放进 `layout_box`，花瓣放进 `sunflower_box`，仙人掌尺寸放进 `cactus_box`。列结果用 `wait_for` 交回后再 `recount_sunflower_scan`。库存共享。向日葵下种/测瓣和按档位收都一列一个工人；当前档目标放进 `sunflower_tier_box`。仙人掌列南北并行、行东西并行。恐龙不 spawn。迷宫分叉再 spawn。`clear()` 前等到 `num_drones() == 1`。

## 验收

- 只改了 `Saves/Save0/` 下需要的 `.py`（通常不含 `__builtins__.py`）。新 `import` 对应的窗口已在游戏里建过，或已明确让用户去建。
- 无完整 Python 语法；Tab 缩进；`import` 只指向游戏窗口里已有的文件。
- 农场圈按模式走模块 `run()`。迷宫走独立模式，不要塞进扫田。
- 链接若缺失/损坏，运行 `tfwr-farm/scripts/ensure-agent-links.bat`。
