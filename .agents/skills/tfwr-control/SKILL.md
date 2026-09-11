---
name: tfwr-control
description: >
  Watches The Farmer Was Replaced output.txt, classifies interpreter errors vs
  status prints, starts the main farm window by calling in-game MainSim APIs,
  and extracts the public script API from the installed game docs. Use when the
  user mentions 报错, output, 自动控制, 启动 main, 反编译, API, F5, or error iteration.
---

# TFWR Control

给 Agent 用的外部工具，**不要**放进 `Saves/Save0`。权威规则在工程根 `AGENTS.md`。只维护 `.agents/skills/`。

游戏安装目录默认从 `Player.log` 的 Mono 路径解析。公开脚本 API 以游戏自带的 `StreamingAssets/Languages/builtins.py` 和 `Languages/ZH` 文档为准。不要整份反编译、不要回写 `Core.dll`。

## 何时用

- 用户说「有报错 / 看 output / 还是报错」
- 改完脚本要对照 `output.txt` 迭代
- 需要启动农场、重跑、停止、或抽出 API

## 启动农场必须跑 main

官方执行按钮只「开始或停止执行**此窗口**中的代码」。`F5` 走 `InputBoss`：读 `workspace.activeWindow`，不是固定入口。

内部真正的农场启动（`Core.dll`，只抽这条路径，不整份回写）：

1. `MainSim.Inst.workspace.codeWindows` 是 `ConcurrentDictionary<string, CodeWindow>`，键是窗口标题。
2. `codeWindows.TryGetValue("main", …)` 拿到 `main`，不要拿 `main_maze`。
3. 若 `MainSim.Inst.IsExecuting()`，先 `StopMainExecution()`。
4. `Node tree = codeWindow.Parse()`。
5. `MainSim.Inst.StartMainExecution(codeWindow, tree)`。

`simulate()` / `ScheduleLeaderboardStart` 会新建一套模拟农场，不是真实田，不要拿来启动 `main`。

`Utils.dll` 里的命名管道 `BongoCatxTheFarmerWasReplaced` / `TapTapLootxTheFarmerWasReplaced` 只给其它游戏发敲击，不能执行脚本。

file watcher 只热读 `.py` 文本，不会按运行按钮。

## 固定启动法

不要操作用户的鼠标，不要用搜索框打字，不要裸 F5。

```bat
python .agents/skills/tfwr-control/scripts/tfwr_control.py run-main
```

`run-main` / `restart` 会：

1. 把目标窗口名写进 `.agents/error-iter/run-target.txt`（默认 `main`）。
2. 用 `tfwr_mono_invoke.py` 把 `TfwrRunMain.dll` 载入 `TheFarmerWasReplaced.exe` 的 Mono（不要用鼠标/F5）。
3. 在 Unity 主线程（`Awaitable._synchronizationContext.Post`）调用上面的 `StartMainExecution`。
4. 读 `.agents/error-iter/run-main-invoke.log`。成功行类似 `StartMainExecution(main)`。
5. `output.txt` 出现 `boot main` 才算农场圈真的从 `main` 起来。

payload / 注入器在 [scripts/tfwr-invoke](scripts/tfwr-invoke)。缺 dll 时会 `dotnet build`。不要点 `main_maze` 的播放键。

## 命令

在工程根执行：

```bat
python .agents/skills/tfwr-control/scripts/tfwr_control.py parse
python .agents/skills/tfwr-control/scripts/tfwr_control.py cycle
python .agents/skills/tfwr-control/scripts/tfwr_control.py status
python .agents/skills/tfwr-control/scripts/tfwr_control.py extract-api
python .agents/skills/tfwr-control/scripts/tfwr_control.py run-main
python .agents/skills/tfwr-control/scripts/tfwr_control.py snapshot
python .agents/skills/tfwr-control/scripts/tfwr_control.py restart
python .agents/skills/tfwr-control/scripts/tfwr_control.py stop
python .agents/skills/tfwr-control/scripts/tfwr_control.py screenshot
```

`restart` 等于 `run-main`。`snapshot` 在 Unity 主线程读 `Logger.GetOutputString`、`MainSim.GetInventory` / `GetCurrentTime` / `GetCallStack`、`Simulation.SpeedFactor`、无人机坐标，写入 `.agents/error-iter/snapshot.json` 和 `snapshot.md`。连续两帧可以算资产/秒。`stop` 走 `StopMainExecution`，不是热键。`play` / `pause` 仍是热键，不要用来启动农场。

改完脚本后先 `snapshot` 看效率，再决定要不要 `run-main`。file watcher 热读已有模块时，不必每次清场重启。

`parse` / `cycle` 会覆盖写入 [../error-iter/last.md](../../error-iter/last.md) 和 `last.json`。有解释器/解析错误时退出码 2。

## 分类

| 级别 | 例子 | 怎么处理 |
| --- | --- | --- |
| error | `从未被定义`、`不存在具有此名称的模块`、缩进/语法 | 改对应模块，file watcher 热读，必要时 `run-main` |
| wait | `sun_wait unripe` | 不是红字。当前最大档未熟。应施肥催熟，保持 hold，不要放锁补种 |
| info | `boot main`、`dino`、`sun_tier`、`sun_unlock`、`maze:` | 状态日志。`dino` 后面是本轮吃掉的苹果数和步数 |
| empty | 空 `output.txt` | 不能当成没报错 |

错误文案模板来自游戏 `Languages/ZH/Strings/execute_errors.txt` 和 `parse_errors.txt`。

## 迭代

1. 读工程根 `output.txt`，再跑 `parse`。
2. 读 `.agents/error-iter/last.md`。
3. error：改 `Saves/Save0` 对应模块。不要猜。
4. wait：检查向日葵 hold/施肥，不要当成模块缺失。
5. 改完再 `parse`。需要重跑农场就 `run-main`，不要裸 F5，不要操鼠标。
6. 直到没有 error。

抽出的 API 摘要： [references/game-api.md](references/game-api.md)

## 不要做

- 不要把本脚本 `import` 进无人机代码。
- 不要整份反编译或回写游戏逻辑源码。启动路径只保留上面那 5 步摘要。
- 不要操作用户的鼠标或往编辑器里打字来启动 `main`。
- 不要在没找到游戏进程时假装已经启动。
- 不要把裸 F5 当成启动了 `main`。
- 不要点 `main_maze` 的运行按钮来跑农场。
