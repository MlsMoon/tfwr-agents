# 解锁字符串对照

`save.json` 的 `unlocks` 是字符串数组。带 `_N` 的是升级档，`N` 为已买到的档位。没有列出的科技视为未解锁。

`__builtins__.py` 里有函数 **不等于** 已解锁。`options.txt` 为 `allow locked features = disabled` 时，调用未解锁 API 会报错。

## 升级档

| 存档前缀 | Unlocks | 含义 |
| --- | --- | --- |
| `expand` | `Unlocks.Expand` | 扩地。下一档材料以 Wiki 为准（`expand_5` 之后约 8000 南瓜） |
| `grass` | `Unlocks.Grass` | 草地产量 |
| `speed` | `Unlocks.Speed` | 无人机速度 |
| `trees` | `Unlocks.Trees` | 树/灌木产量 |
| `carrots` | `Unlocks.Carrots` | 胡萝卜产量与种植成本 |
| `pumpkins` | `Unlocks.Pumpkins` | 南瓜产量与种植成本 |
| `watering` | `Unlocks.Watering` | 浇水 |
| `fertilizer` | `Unlocks.Fertilizer` | 肥料 |

作物本体常见记号：`carrot`、`pumpkin`、`sunflower`、`tree`、`bush`、`hay`。

## 已常见、可写的语言/API

`if` / `else` / `elif` / `while` / `for` / `range` / `break` / `continue`、`def` / `return` / `global`、`from` / `import`、列表方法、`len`、`and` / `or` / `not`、`num_items` / `num_unlocked`、`get_pos_*` / `get_entity_type` / `get_ground_type` / `get_water`、`measure`、`min` / `max` / `abs` / `random`、字典/集合、`print` / `quick_print`、`get_time` / `get_tick_count`。

存档里的 `unlocks` 表示能用 `Unlocks` 枚举和 `num_unlocked`，**不是** `unlock()`。

## 默认当作锁定（除非快照里出现对应记号）

| API / 内容 | 需要看到的记号 |
| --- | --- |
| `get_cost` | `costs` / `get_cost` |
| `unlock()` | `auto_unlock` / `unlock`（不要把 `unlocks` 当成这个） |
| `swap`、仙人掌 | `cactus` / `swap` |
| `get_companion`、异种栽培 | `polyculture` / `get_companion` |
| `spawn_drone` / `wait_for` / `has_finished` / `num_drones` / `max_drones` | `megafarm` / `spawn_drone` |
| 迷宫 / 宝藏 / 金 | `mazes` / `maze` / `treasure` / `gold` |
| 恐龙 / 骨 | `dinosaurs` / `dinosaur` |
| `set_execution_speed` / `set_world_size` | `debug_2` |
| `leaderboard_run` | `leaderboard` |
| `simulate` | `simulation` |

## 不要用的旧名

`trade`、`can_trade`、`carrot_seed`、`pumpkin_seed`、`sunflower_seed`：可能出现在 `unlocks` 里，但当前 `__builtins__.py` 没有对应可调用 API。种植直接 `plant(Entities.*)`，花费库存物品。
