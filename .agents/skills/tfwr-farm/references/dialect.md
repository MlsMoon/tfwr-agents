# TFWR 方言

游戏自带解释器，看起来像 Python，**不是 CPython**。社区说法若与 `Saves/Save0/__builtins__.py` 或游戏内文档冲突，以后者为准。

## 通常可用

- `if` / `elif` / `else`、`while`、`for ... in range(...)`
- `def`（可嵌套）、`global`、闭包
- 列表：`[]`、下标、`in`、`append` / `pop` / `remove`
- 字典：`[key]`、`in`、`pop`（无 `.get` / `.values`）
- 元组、字符串 `+`、`and` / `or` / `not`
- 比较可链式：`0 < x < 10`
- 类型标注会被忽略，可留给外部编辑器
- 游戏文件之间：`import other_file`、`from other_file import name`
- `len`、`range`、`min`、`max`、`abs`、`random`（均需已解锁）
- `str(obj)` 现已存在；整数截断用 `// 1`，不要用 `int()`

## 不要写

- `lambda`
- 列表/字典推导式、集合字面量 `{x, y}`
- 三元：`a if cond else b`（改成完整 `if` / `else`）
- `try` / `except` / `finally`
- `yield`、生成器
- `f"..."`、反斜杠续行
- `is None` / `is not None`（改 `== None` / `!= None`）
- `int()` / `float()`
- `dict.get`
- `nonlocal`
- 标准库 `import`（`math`、`random` 模块、`sys` 等）
- 类、`*args` / `**kwargs`、具名参数（游戏 API 若未声明默认值，按位置传）
- 列表/字典/集合/字符串上未列出的方法

复合赋值不稳定时用 `x = x + 1`，不要依赖 `x += 1`。

## Timing（科技树原文口径）

基本单位是 tick。无速度升级且无能量时约 400 tick/s。这是游戏模型，不是真实 CPU。

**0 tick**

- 函数调用、读/写变量
- `import`；`模块.名字` 访问已 import 的模块
- 单目 `-`、`not`
- `return` / `break` / `continue`
- `for` / `while` 的迭代本身（不含循环头和条件）
- `get_time()`、`get_tick_count()`、`quick_print()`（连调用也不占 tick）

**1 tick**

- 二元运算：`+ - * / // % and or` 以及比较
- 一个 `if` 分支（不含条件表达式）
- `def`（加载时，每个函数 1 次）
- `for` / `while` 开始
- `pass`
- 下标 `a[i]`（字典/集合再按 key 大小加 tick）
- 把函数或模块赋给变量/参数后再用，从「0 tick」变成 1 tick。所以热路径写 `saved_data_module.plan_at(x, y)`，不要 `from m import f` 再 `f()`。

内置动作另算：成功的 `harvest` / `plant` / `move` / `swap` / `till` / `use_item` / `clear` / `spawn_drone` 约 200；`get_*` / `can_*` / `num_items` / `measure` / `num_drones` / `max_drones` / `has_finished` 约 1。`wait_for` 会等到目标无人机结束。

多无人机：工人内存独立，简单 `global` 互不可见。官方文档：整份内存是拷贝，`spawn_drone` 传进去的列表也是拷贝。列结果必须用 `wait_for` 返回值，不要看工人有没有改 `cut_box`。库存共享。官方 `spawn_drone(task, *args)` 可以带额外参数；本存档仍传无参函数，要带配额用工厂闭包，不要让闭包读循环变量。`clear()` 前等到 `num_drones() == 1`。不要用 `set_world_size` 当扩地。

`print` / `do_a_flip` / `pet_the_piggy` 约 1 秒真实时间。`print()` 和运行报错会写入工程根 `output.txt`。排错先读这个文件。排行榜不要 `print`。

热路径不要整表扫描、不要每格 `len` / `get_world_size` / `ensure_world_size`。`and`/`or` 和嵌套 `if` 差不多贵（都是 1+条件），嵌套 if 不会更便宜。
