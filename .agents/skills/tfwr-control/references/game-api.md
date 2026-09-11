# TFWR 公开脚本 API

从游戏安装目录抽出，不是把 `Core.dll` 整份反编译成逻辑源码。
来源：`D:\Program Files (x86)\Steam\steamapps\common\The Farmer Was Replaced\TheFarmerWasReplaced_Data\StreamingAssets\Languages\builtins.py`

## 行为要点

- 向日葵：至少 10 朵且收当前最大花瓣是 **8 倍**。田里还有更高花瓣时收低档，后面也没倍数。未熟就能 `measure()`。
- 多无人机：内存各自一份拷贝。列表当参数传进去也是拷贝。列结果必须 `wait_for` 交回。`spawn_drone` 官方可以带额外参数，本存档仍用无参工厂闭包。

## 函数

- `abs`
- `add`
- `append`
- `can_harvest`
- `can_move`
- `change_hat`
- `clear`
- `do_a_flip`
- `get_companion`
- `get_cost`
- `get_entity_type`
- `get_ground_type`
- `get_pos_x`
- `get_pos_y`
- `get_tick_count`
- `get_time`
- `get_water`
- `get_world_size`
- `harvest`
- `has_finished`
- `insert`
- `leaderboard_run`
- `len`
- `max`
- `max_drones`
- `measure`
- `min`
- `move`
- `num_drones`
- `num_items`
- `num_unlocked`
- `pet_the_piggy`
- `plant`
- `pop`
- `print`
- `quick_print`
- `random`
- `range`
- `remove`
- `set_execution_speed`
- `set_world_size`
- `simulate`
- `spawn_drone`
- `str`
- `swap`
- `till`
- `unlock`
- `use_item`
- `wait_for`

## 枚举

### Entities

- `Apple`
- `Bush`
- `Cactus`
- `Carrot`
- `Dead_Pumpkin`
- `Dinosaur`
- `Grass`
- `Hedge`
- `Pumpkin`
- `Sunflower`
- `Treasure`
- `Tree`

### Grounds

- `Grassland`
- `Soil`

### Hats

- `Brown_Hat`
- `Cactus_Hat`
- `Carrot_Hat`
- `Dinosaur_Hat`
- `Gold_Hat`
- `Gold_Trophy_Hat`
- `Golden_Cactus_Hat`
- `Golden_Carrot_Hat`
- `Golden_Gold_Hat`
- `Golden_Pumpkin_Hat`
- `Golden_Sunflower_Hat`
- `Golden_Tree_Hat`
- `Gray_Hat`
- `Green_Hat`
- `Pumpkin_Hat`
- `Purple_Hat`
- `Silver_Trophy_Hat`
- `Straw_Hat`
- `Sunflower_Hat`
- `The_Farmers_Remains`
- `Top_Hat`
- `Traffic_Cone`
- `Traffic_Cone_Stack`
- `Tree_Hat`
- `Wizard_Hat`
- `Wood_Trophy_Hat`

### Items

- `Bone`
- `Cactus`
- `Carrot`
- `Fertilizer`
- `Gold`
- `Hay`
- `Piggy`
- `Power`
- `Pumpkin`
- `Water`
- `Weird_Substance`
- `Wood`

### Leaderboards

- `Cactus`
- `Cactus_Single`
- `Carrots`
- `Carrots_Single`
- `Dinosaur`
- `Fastest_Reset`
- `Hay`
- `Hay_Single`
- `Maze`
- `Maze_Single`
- `Pumpkins`
- `Pumpkins_Single`
- `Sunflowers`
- `Sunflowers_Single`
- `Wood`
- `Wood_Single`

### Unlocks

- `Auto_Unlock`
- `Cactus`
- `Unlock`
- `Upgrade`
- `Carrots`
- `Costs`
- `Debug`
- `Debug_2`
- `Dictionaries`
- `Dinosaurs`
- `Expand`
- `Fertilizer`
- `Functions`
- `Grass`
- `Hats`
- `Import`
- `Leaderboard`
- `Lists`
- `Loops`
- `Mazes`
- `Megafarm`
- `Operators`
- `Plant`
- `Polyculture`
- `Pumpkins`
- `Senses`
- `Simulation`
- `Speed`
- `Sunflowers`
- `The_Farmers_Remains`
- `Timing`
- `Top_Hat`
- `Trees`
- `Utilities`
- `Variables`
- `Watering`
- `overloads`
- `Sunflower`
- `Maze`
- `Dinosaur`
