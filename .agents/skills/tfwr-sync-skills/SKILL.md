---
name: tfwr-sync-skills
description: >
  Syncs The Farmer Was Replaced project skills after Save0 farm or strategy
  code changes. Use when editing Saves/Save0, VALUE, layout, harvest, maze,
  tick cache, AGENTS.md, or when the user mentions 更新 skill / 同步 skill /
  自动更新 skill / tfwr-sync-skills.
---

# TFWR Sync Skills

改完农场或策略代码后，把**已落地的事实**写回 skill。用户没点名也要做。

只改 `.agents/skills/`。`.claude` / `.grok` / `.cursor` 的 skills 是符号链接，不要复制第二份。UTF-8 无 BOM，frontmatter 从首字节 `---` 开始。

## 何时跑

- 排错时先读工程根 `output.txt`，再跑 `/tfwr-control` 的 `parse`，读 `.agents/error-iter/last.md`，再改代码
- 刚改过 `Saves/Save0/*.py` 的种植、布局、收获、走位、迷宫门槛、tick 缓存
- 刚改过 `AGENTS.md` 工作流程或硬约束
- 用户说「更新 skill / 同步文档」
- 解锁进度变了（先 `/tfwr-save` 跑 `parse_save.ps1`）

不要为了同步去改 `save.json` 或无人机脚本。代码是真值，skill 跟着代码走。

## 对照表

| 代码里变了什么 | 更新哪里 |
| --- | --- |
| VALUE / MIN / `pick_mode` / 保底 / 金子口径 | `tfwr-strategy/SKILL.md`，`tfwr-farm/references/farm-layout.md` |
| `tile_plan`、单矩形、一波一模式、轮次锁 | 同上 |
| 向日葵只收最大、南瓜合体、仙人掌四向 swap / 折返 | 同上 |
| 迷宫生成条件、寻路、`output.txt` | 同上，以及 `tfwr-farm/SKILL.md` |
| 圈级缓存、`refresh_size`、脏标记、少 `measure` | strategy、farm-layout、`tfwr-farm/SKILL.md` |
| 方言、tick、禁止语法 | `tfwr-farm/references/dialect.md` |
| 模块职责、入口圈顺序、多无人机 | `tfwr-farm/SKILL.md`、farm-layout、dialect |
| `spawn_drone` / 列并行 / 迷宫分叉 | 同上，以及 `tfwr-strategy/SKILL.md` |
| 解锁 / 新 API | 先 `parse_save.ps1`，再 `tfwr-save/references/save-snapshot.md` |
| 新脚本 / `import` 模块 / `save.json` 窗口列表 | `tfwr-save/SKILL.md`，以及 `tfwr-farm/SKILL.md` 硬约束 |
| 工作流程、skill 维护规则 | `AGENTS.md`（工程根，不是 skill 副本） |
| `output.txt` 分类 / 热键 / 抽出 API | `tfwr-control/SKILL.md`，以及 `tfwr-control/references/game-api.md` |

权威概览是 `/tfwr-strategy`。田块接线是 farm-layout。不要两处口径打架。

## 步骤

1. 对照本次改动的 `Saves/Save0` 文件，列出变了的事实（数字、条件、缓存、不要做什么）。
2. 打开对照表里的现有 skill，只改过时的句子。
3. 策略数字必须和代码常量一致：草 2、木 8、胡萝卜 40、Power 40、南瓜 80、奇异物质/仙人掌/骨头/金子 80；MIN Power 500、Power 上限 16000、草/木 2000、胡萝卜 800。
4. 写清「慢是 tick 不是少走路」时，不要写成取消仙人掌折返。
5. 不编解锁。Megafarm 已解锁就写 `spawn_drone`；仍锁才写「不要 spawn」。不要写死工人数。
6. 不新增 `.cursor/skills` 实体目录。链接坏了跑 `tfwr-farm/scripts/ensure-agent-links.bat`。
7. 验收：skill 与代码一致；无 BOM；没有把符号链接改成副本。

## 不要做

- 不要把 skill 写成代码复述或粘贴整文件。
- 不要在同步时改策略数字「顺便优化」。
- 不要维护 Claude/Grok/Cursor 三份 skill 树。
