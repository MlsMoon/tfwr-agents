# Save0 当前布局

农场入口 `Saves/Save0/main.py`：`clear()`，走到 `(0, 0)`，只扫田。不读金子、不开迷宫。`run_mode` 只 `pick_mode` 再调模块 `run()`。

迷宫入口 `Saves/Save0/main_maze.py`：只刷金子。不要从农场 `import`。排错先读工程根 `output.txt`。

**农场**：一波一种。向日葵/南瓜/仙人掌各自整田种完再收。草木胡萝卜种完补 `get_companion` 伴侣。恐龙单机清场戴帽，不发工人。

**迷宫**：清掉占格后种灌木，按升级消耗奇异物质。分叉 `spawn_drone`，满员则 DFS 回溯。只收宝藏。`clear()` 前等到只剩主无人机。失败会 `print` 到 `output.txt`。

改脚本前先跑 `/tfwr-save` 的 `parse_save.ps1`。新 `import` 必须对应游戏编辑器里已有的窗口。用户明确要求时可以往 `save.json` 窗口列表加名字；游戏开着且 `autosave progress` 开启时仍可能被冲掉。农场圈开头 `refresh_size()`：边长没变就复用表，变了才 `ensure_world_size`。热路径不要每格 ensure。

## 走位

按列并行，**可以走回头路**。每列都走，清掉上一波留下的作物。仙人掌收尾时先按列南北并行，再按行东西并行。世界会环绕。`go_to` 走较短环绕方向。恐龙戴帽时不环绕，不要用 `go_to`。

## 种植

原点 `pick_mode()` 只选一个模式。`apply_mode_layout` 从 `(0,0)` 画一个矩形，剩余格铺草。不要再切 first/second/third。特殊作物矩形都是 `size×size`。

价值：草 2、木 8、胡萝卜 40、Power 40、南瓜 80、奇异物质 80、仙人掌 80、骨头 80。金子 80 只在 `maze_module`，农场不读。

保底：Power 500、草 2000、木 2000、胡萝卜 800。南瓜/仙人掌/骨头/奇异物质无数量保底。

`tile_plan[x][y]` 是种植/收获/施肥的依据。`current_mode` 是这一波的模式。

仙人掌买不起（`get_cost` 要仙人掌库存）就不进候选。种仙人掌要土壤。

向日葵在 Power `< 16000` 时进候选：低于 500 强制上场。这一波占整田。档位没收完用 `sunflower_hold_plant` 阻止补种；只剩 10 朵才放锁。南瓜/仙人掌/草木胡萝卜独占整田。树按 `(x+y)%2` 棋盘格。骨头更穷且仙人掌够买苹果时上恐龙。

## 向日葵

Power ≥ 16000 才不种。低于 16000 占整田。种下立刻 `measure()`。扫列只测不收。表齐后按花瓣档位多人收：先收完所有当前最大档（15，再 14…），至少留 10 朵拿 8 倍。档位没收完不要补种。收过的格会变草。只剩 10 朵才放锁。hold 之后 `known < expected` 是收过的洞，不要当表不齐退出。不要用 9 档封顶。工人只走本档的 y，不要整列走到顶。发完最后一列先回家再 `wait_for`。花瓣 hist 增量改 max，不要每清一朵整表扫描。不要每档 `print sun_tier`。当前档未熟就地施肥（最多 3 次），保持 hold。hold 时跳过整田补种。不要按列收光，也不要单机收一朵就补种。

## 南瓜

坏南瓜立刻补种。本块计划格都是成熟活南瓜，且对角 `measure()` 同一个 ID，再收合体（产量是这块立方）。工人上报 need/ready/dead。不要收零散小合体。轮次未收完不换模式。

## 仙人掌

整田排序再收，产量是数量平方。独占这一波。仙人格上出现南瓜/坏南瓜必须先收掉再补种。只给成熟的记尺寸；邻格不是仙人掌计划格、没成熟、或尺寸像花瓣（>9）不要 swap。列上多人南北换，行上多人东西换。整田西南小、东北大且都成熟再收到 `(0,0)`。仙人格不施肥。

计划格和实体对不上时先清掉再种。花瓣放进 `sunflower_box`，用 `world_size()` 判界，扫完后 `recount_sunflower_scan`。表不齐不要连收。不要每圈 `print sun_skip`。仙人掌已齐却排不好才 `print cactus_skip`。

## 填料伴侣

草木胡萝卜种下后 `get_companion()`。伴侣在本列就工人顺手种，否则交回主无人机补种。伴侣只可能是草/灌木/树/胡萝卜。不要种到向日葵/南瓜/仙人格上。

## 恐龙

`dinosaur_module.run()`：进波 `clear()` 一次后戴帽。偶边长哈密顿圈 + 只朝苹果抄近路（圈下标必须落在当前→苹果的弧上）。不要纯跟圈，不要贪心曼哈顿。走不动或没苹果再摘帽拿 `n²`。苹果看 `get_cost(Entities.Apple)`。不 `spawn_drone`，戴帽不用 `go_to`，不跨波锁。摘帽 `print("dino", eaten, steps)`。

## 迷宫

执行 `main_maze`。不要把金子门槛写回农场。生成：清占格 + 灌木 + 边长 × 2^(迷宫升级-1) 的奇异物质。`measure()` 能读到宝藏坐标才算开成功。寻路：分叉 spawn，满员 DFS，只收宝藏。先读 `output.txt`。

## 肥料

奇异物质资产低于作物最小资产才施。填料列脚下是南瓜/向日葵/仙人格就不施。向日葵收当前最大档时未熟可以施。不要对灌木用变异质，除非走迷宫模块。主无人机圈初算 `fertilizer_wanted`；工人内存独立，列开头用 `column_should_fertilize()`（必要时自己 `num_items`）。库存共享。

## Tick 缓存

慢是语句 tick，不是少走路。官方口径见 dialect.md：调用/读变量/模块点号是 0；贵的是下标、`if`、二元运算、整表扫描。

- 脚下格用 `plan_at`（两次下标）。邻格才 `plan_for_tile`。
- 向日葵 `known` / `expected` / max / `sunflower_hist` **增量**更新。不要每清一朵整表 `recompute`，不要每档全表 `count` / `recount`。
- `refresh_size`：原点或坐标超出 `cached_size` 才查边长。
- 写 `tile_plan` 时一次扫出仙人掌格数、向日葵计数。
- 布局参数没变则跳过重画。
- 仙人掌排序脏标记；列 ok 用计数，不要每格扫所有列。
- 热路径用 `模块.函数`，不要 `from m import f`。
- 布局给工人看用 `layout_box`，不要只重绑 `tile_plan`。

## 改策略时

先读 `/tfwr-strategy`。代码入口：

- 价值/保底/`pick_mode`/伴侣：`plant_module.py`
- 分发 `run_mode`：`drone_module.py`；入口 `main.py`
- 向日葵：`sunflower_module.py`；南瓜：`pumpkin_module.py`；仙人掌：`cactus_module.py`；恐龙：`dinosaur_module.py`
- 迷宫生成/分叉 spawn：`maze_module.py`；入口 `main_maze.py`
- 跨格记忆 / `layout_box` / `apply_mode_layout` / `refresh_size`：`saved_data_module.py`
- 改完加载 `/tfwr-sync-skills`
