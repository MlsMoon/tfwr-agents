---
name: tfwr-save
description: >
  Parses The Farmer Was Replaced Save0 save.json for items, unlock tokens,
  and upgrade levels. Use when changing Saves/Save0 scripts, checking
  research progress, asking what is unlocked, or before writing drone APIs.
---

# TFWR Save

给 Agent 用的存档解析 skill，**不要**把本目录脚本放进 `Saves/Save0`（游戏 DSL 跑不了）。

权威规则在工程根 `AGENTS.md`。只维护 `.agents/skills/`。

## 何时用

- 改农场脚本、作物策略、研究树、扩地之前
- 用户问「解锁了什么 / 有哪些科技 / 能不能用某某函数」
- 需要对照当前库存决定种什么

先跑解析，改策略读 `/tfwr-strategy`，再加载 `/tfwr-farm` 写无人机代码。

## 解析

在工程根执行：

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File .agents\skills\tfwr-save\scripts\parse_save.ps1
```

或 `.agents/skills/tfwr-save/scripts/parse_save.bat`。

工具只读 `Saves/Save0/save.json`，把人类可读摘要打到 stdout，并覆盖写入 [save-snapshot.md](references/save-snapshot.md)。对照表见 [unlock-catalog.md](references/unlock-catalog.md)。

未要求时不要改 `save.json`、`Backup/`、日志、Steam 云文件。用户明确要求改存档时，可以改窗口列表，但仍要先看下面的规矩。

## 脚本文件与存档窗口

`import foo` 的名字必须等于游戏编辑器**窗口顶部的文件名**（一般是 `foo.py` 去掉后缀）。只在磁盘上新建 `Saves/Save0/foo.py`，游戏不会当模块，`output.txt` 会报「不存在具有此名称的模块」。

游戏认的是编辑器里建过的窗口。`save.json` 里的 `minimizedFiles` / `openFilePositions` / `openFileScrollPositions` / `openFileSizes` 是窗口 UI 列表。用户明确要求改存档时，可以把新窗口名写进去（紧凑 JSON，`separators=(',', ':')`，不要丢掉 `items`）。

当前存档 `options.txt`：`file watcher = enabled`（改已有 `.py` 会热读），`autosave progress = enabled`（游戏开着会按内存里的窗口列表重写 `save.json`）。游戏开着时刚写入的窗口名可能被冲掉；让用户暂停脚本或回到菜单后再看窗口列表。

要加新模块：

1. 优先让用户在游戏编辑器里**新建文件**，窗口标题必须和 `import` 名一致。
2. 用户要求改存档时，同时把名字写入上面四个窗口字段。
3. Agent 再写/改 `Saves/Save0/<名字>.py`。已有窗口时 file watcher 会读磁盘。
4. 不要因为存档里还没有这个窗口，就把逻辑塞回旧文件、或假装模块不需要。

当前窗口列表应包含：`cactus_module`、`dinosaur_module`、`drone_module`、`harvest_module`、`main`、`main_maze`、`maze_module`、`move_module`、`plant_module`、`pumpkin_module`、`saved_data_module`、`sunflower_module`。

对照已有模块：看 `Saves/Save0/*.py`，并用 `save.json` 的窗口列表核对。两边对不上时，以游戏窗口为准；磁盘多出来的 `.py` 还不能 `import`。

## 写脚本时

- `allow locked features = disabled`：快照里标成未解锁的 API 不要写进 `Saves/Save0`。
- `__builtins__.py` 是编辑器桩，**不代表已解锁**。
- `unlocks` 数组里的 `unlocks` 只表示能查 `Unlocks` / `num_unlocked`，不是 `unlock()`。
- `trade` / `carrot_seed` 是旧解锁名，当前桩没有这些 API，不要用。
- 升级档看 `name_N`（如 `expand_5`）。田边长用运行时 `get_world_size()`，不要写死。
- 库存会边跑边变；逻辑用 `num_items` / `num_unlocked`，快照只给 Agent 看。
