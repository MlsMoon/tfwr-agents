# 种植：原点只选一个模式，这一波田归它，不再切三块混种。
#
# 作物比同一量纲：资产 = 数量 * VALUE。谁更小谁更该种。
# VALUE 是折算尺度（草 2、木 8、胡萝卜/Power 40、南瓜/仙人掌/骨头 80），
# 不是研究树报价。
#
# MIN 是硬保底。数量低于 MIN 时加超大分。
# Power < 500：强制向日葵，打断南瓜/仙人掌轮次锁。
# Power < 16000：向日葵仍进候选，谁更穷谁上场。Power VALUE 40。
# 骨头更穷且仙人掌够买苹果：上恐龙，measure 追苹果，卡住摘帽再开一轮。
# 否则在南瓜 / 仙人掌 / 草木胡萝卜里选最穷的。
#
# 向日葵模式占整田，按花瓣档位多人收，档位没收完不补种。
# 填料种下后 get_companion，本列顺手种，外列交回主无人机。
# 施肥：奇异物质资产（×80）低于作物最小资产才施。填料列南瓜/向日葵/仙人格不施。
# 向日葵收当前最大档时未熟可以施，写在 sunflower_module。
# 金子/迷宫不在这里。刷金子执行 main_maze。

import move_module
import saved_data_module

VALUE_HAY = 2
VALUE_WOOD = 8
VALUE_CARROT = 40
VALUE_PUMPKIN = 80
VALUE_POWER = 40
VALUE_WEIRD = 80
VALUE_CACTUS = 80
VALUE_BONE = 80

COMP_GRASS = 0
COMP_BUSH = 1
COMP_TREE = 2
COMP_CARROT = 3
pending_companions = []

MIN_POWER = 500
MIN_HAY = 2000
MIN_WOOD = 2000
MIN_CARROT = 800
CARROT_HAY_NEED = 20
CARROT_WOOD_NEED = 20
# 低于保底时加在得分上，必须比任何正常资产都大。
FLOOR_BONUS = 1000000000

fertilizer_wanted = False
cached_water = 0
cached_fertilizer = 0

def after_plant(wanted):
	if plant(wanted):
		return wanted
	return get_entity_type()

def plant_carrot():
	if get_ground_type() != Grounds.Soil:
		till()
	return after_plant(Entities.Carrot)

def plant_bush():
	if get_ground_type() == Grounds.Soil:
		till()
	return after_plant(Entities.Bush)

def plant_tree():
	if get_ground_type() != Grounds.Soil:
		till()
	return after_plant(Entities.Tree)

def plant_bush_and_tree():
	# 多无人机时邻格表不可靠。棋盘格保证树不相邻。
	pos_x = get_pos_x()
	pos_y = get_pos_y()
	if (pos_x + pos_y) % 2 == 0:
		return plant_tree()
	return plant_bush()

def plant_grass():
	if get_ground_type() == Grounds.Soil:
		till()
	return after_plant(Entities.Grass)

def plant_pumpkin():
	if get_ground_type() != Grounds.Soil:
		till()
	return after_plant(Entities.Pumpkin)

def plant_sunflower():
	if get_ground_type() != Grounds.Soil:
		till()
	return after_plant(Entities.Sunflower)

def plant_cactus():
	if get_ground_type() != Grounds.Soil:
		till()
	return after_plant(Entities.Cactus)

def get_plant_type(posx, posy):
	return saved_data_module.get_plant_type(posx, posy)

def can_afford_carrot():
	if num_unlocked(Unlocks.Carrots) == 0:
		return False
	if num_items(Items.Hay) <= CARROT_HAY_NEED:
		return False
	if num_items(Items.Wood) <= CARROT_WOOD_NEED:
		return False
	return True

# 返回 [数量, VALUE, MIN]。未知计划当空，得分会极低。
def crop_info(plan):
	if plan == saved_data_module.PLAN_GRASS:
		return [num_items(Items.Hay), VALUE_HAY, MIN_HAY]
	if plan == saved_data_module.PLAN_BUSH:
		return [num_items(Items.Wood), VALUE_WOOD, MIN_WOOD]
	if plan == saved_data_module.PLAN_TREE:
		return [num_items(Items.Wood), VALUE_WOOD, MIN_WOOD]
	if plan == saved_data_module.PLAN_CARROT:
		return [num_items(Items.Carrot), VALUE_CARROT, MIN_CARROT]
	if plan == saved_data_module.PLAN_PUMPKIN:
		return [num_items(Items.Pumpkin), VALUE_PUMPKIN, 0]
	if plan == saved_data_module.PLAN_SUNFLOWER:
		return [num_items(Items.Power), VALUE_POWER, MIN_POWER]
	if plan == saved_data_module.PLAN_CACTUS:
		return [num_items(Items.Cactus), VALUE_CACTUS, 0]
	if plan == saved_data_module.PLAN_DINOSAUR:
		return [num_items(Items.Bone), VALUE_BONE, 0]
	return [0, 1, 0]

# 资产越小越该种。低于 MIN 再加 FLOOR_BONUS，保底永远压过「只是偏穷」。
def crop_score(plan):
	info = crop_info(plan)
	count = info[0]
	value = info[1]
	minimum = info[2]
	score = 0 - (count * value)
	if count < minimum:
		score = score + FLOOR_BONUS
	return score

# 五种作物资产的最小值。奇异物质跟这个比，低了才施肥。
def min_crop_wealth():
	hay_w = num_items(Items.Hay) * VALUE_HAY
	wood_w = num_items(Items.Wood) * VALUE_WOOD
	carrot_w = num_items(Items.Carrot) * VALUE_CARROT
	pumpkin_w = num_items(Items.Pumpkin) * VALUE_PUMPKIN
	power_w = num_items(Items.Power) * VALUE_POWER
	cactus_w = num_items(Items.Cactus) * VALUE_CACTUS
	smallest = hay_w
	if wood_w < smallest:
		smallest = wood_w
	if carrot_w < smallest:
		smallest = carrot_w
	if pumpkin_w < smallest:
		smallest = pumpkin_w
	if power_w < smallest:
		smallest = power_w
	if cactus_w < smallest:
		smallest = cactus_w
	return smallest

def refresh_circle_cache(min_w):
	global fertilizer_wanted
	global cached_water
	global cached_fertilizer
	cached_water = num_items(Items.Water)
	cached_fertilizer = num_items(Items.Fertilizer)
	fertilizer_wanted = False
	if cached_fertilizer > 0:
		weird_w = num_items(Items.Weird_Substance) * VALUE_WEIRD
		if weird_w < min_w:
			fertilizer_wanted = True

def fertilizer_is_wanted():
	return fertilizer_wanted

def has_water_charge():
	if cached_water > 0:
		return True
	return False

def consume_fertilizer():
	global cached_fertilizer
	if cached_fertilizer <= 0:
		return
	use_item(Items.Fertilizer)
	cached_fertilizer = cached_fertilizer - 1

def consume_water():
	global cached_water
	if cached_water <= 0:
		return
	use_item(Items.Water)
	cached_water = cached_water - 1

def collect_candidates():
	options = []
	options.append(saved_data_module.PLAN_GRASS)
	if num_unlocked(Unlocks.Trees) > 0:
		options.append(saved_data_module.PLAN_TREE)
	else:
		options.append(saved_data_module.PLAN_BUSH)
	if can_afford_carrot():
		options.append(saved_data_module.PLAN_CARROT)
	if num_unlocked(Unlocks.Pumpkins) > 0:
		options.append(saved_data_module.PLAN_PUMPKIN)
	# 能量低于上限就进候选。低于 500 强制上场。
	if num_unlocked(Unlocks.Sunflowers) > 0:
		if num_items(Items.Power) < saved_data_module.POWER_TARGET:
			options.append(saved_data_module.PLAN_SUNFLOWER)
	if can_afford_cactus():
		options.append(saved_data_module.PLAN_CACTUS)
	return options

def can_afford_cactus():
	if num_unlocked(Unlocks.Cactus) == 0:
		return False
	cost = get_cost(Entities.Cactus)
	if cost == None:
		return True
	if Items.Cactus in cost:
		if num_items(Items.Cactus) < cost[Items.Cactus]:
			return False
	return True

def apple_pay():
	# 官方文档：苹果花仙人掌。旧版也可能是南瓜。以 get_cost 为准。
	cost = get_cost(Entities.Apple)
	if cost == None:
		return [None, 0]
	if Items.Cactus in cost:
		need = cost[Items.Cactus]
		if need < 1:
			need = 1
		return [Items.Cactus, need]
	if Items.Pumpkin in cost:
		need = cost[Items.Pumpkin]
		if need < 1:
			need = 1
		return [Items.Pumpkin, need]
	for item in cost:
		need = cost[item]
		if need < 1:
			need = 1
		return [item, need]
	return [None, 0]

def can_buy_apple():
	return can_buy_apples(1)

def can_buy_apples(n):
	pay = apple_pay()
	if pay[0] == None:
		return True
	if n < 1:
		n = 1
	return num_items(pay[0]) >= pay[1] * n

def can_afford_dino():
	if num_unlocked(Unlocks.Dinosaurs) == 0:
		return False
	if num_items(Items.Power) < MIN_POWER:
		return False
	size = saved_data_module.world_size()
	if size < 1:
		size = get_world_size()
	return can_buy_apples(size)

def pick_mode():
	# 一波只选一个模式。能量危急强制向日葵；轮次锁未收完则继续。
	power = num_items(Items.Power)
	if power < MIN_POWER:
		if num_unlocked(Unlocks.Sunflowers) > 0:
			return saved_data_module.PLAN_SUNFLOWER
	if saved_data_module.sunflower_cycle_active():
		if power < saved_data_module.POWER_TARGET:
			return saved_data_module.PLAN_SUNFLOWER
	if power >= MIN_POWER:
		if saved_data_module.pumpkin_cycle_active():
			return saved_data_module.PLAN_PUMPKIN
		if saved_data_module.cactus_cycle_active():
			return saved_data_module.PLAN_CACTUS

	options = collect_candidates()
	best = options[0]
	best_score = crop_score(best)
	option_index = 1
	while option_index < len(options):
		plan = options[option_index]
		score = crop_score(plan)
		if score > best_score:
			best = plan
			best_score = score
		option_index = option_index + 1
	if can_afford_dino():
		bone_score = crop_score(saved_data_module.PLAN_DINOSAUR)
		if bone_score > best_score:
			return saved_data_module.PLAN_DINOSAUR
	return best

def mode_rect(mode):
	size = saved_data_module.cached_size
	if size < 1:
		size = saved_data_module.refresh_size()
	return [size, size]

def record_sunflower_here(pos_x, pos_y):
	if get_entity_type() != Entities.Sunflower:
		return
	petals = measure()
	if petals == None:
		return
	saved_data_module.set_sunflower_petals(pos_x, pos_y, petals)

def record_sunflower_if_needed():
	pos_x = get_pos_x()
	pos_y = get_pos_y()
	if saved_data_module.plan_at(pos_x, pos_y) != saved_data_module.PLAN_SUNFLOWER:
		return
	if saved_data_module.sunflower_petal_at(pos_x, pos_y) >= 0:
		return
	record_sunflower_here(pos_x, pos_y)

def plan_already_growing(entity, plan):
	if entity == None:
		return False
	if entity == Entities.Dead_Pumpkin:
		return False
	if plan == saved_data_module.PLAN_GRASS:
		return entity == Entities.Grass
	if plan == saved_data_module.PLAN_BUSH:
		return entity == Entities.Bush
	if plan == saved_data_module.PLAN_TREE:
		if entity == Entities.Tree:
			return True
		return entity == Entities.Bush
	if plan == saved_data_module.PLAN_CARROT:
		return entity == Entities.Carrot
	if plan == saved_data_module.PLAN_PUMPKIN:
		return entity == Entities.Pumpkin
	if plan == saved_data_module.PLAN_SUNFLOWER:
		return entity == Entities.Sunflower
	if plan == saved_data_module.PLAN_CACTUS:
		return entity == Entities.Cactus
	return False

def can_replace_now(entity, plan):
	if entity == None:
		return True
	if entity == Entities.Dead_Pumpkin:
		return True
	if entity == Entities.Grass:
		return plan != saved_data_module.PLAN_GRASS
	return False

def plant_for_plan(plan):
	if plan == saved_data_module.PLAN_BUSH:
		return plant_bush()
	if plan == saved_data_module.PLAN_TREE:
		return plant_bush_and_tree()
	if plan == saved_data_module.PLAN_CARROT:
		return plant_carrot()
	if plan == saved_data_module.PLAN_PUMPKIN:
		return plant_pumpkin()
	if plan == saved_data_module.PLAN_SUNFLOWER:
		return plant_sunflower()
	if plan == saved_data_module.PLAN_CACTUS:
		return plant_cactus()
	return plant_grass()

def prepare_mode(mode):
	# 只让主无人机在发列之前调。工人不要重画布局。恐龙自己清场，不画作物格。
	saved_data_module.refresh_size()
	if mode == saved_data_module.PLAN_DINOSAUR:
		saved_data_module.apply_mode_flags(mode)
		return mode
	rect = mode_rect(mode)
	saved_data_module.apply_mode_layout(mode, rect[0], rect[1])
	refresh_circle_cache(min_crop_wealth())
	return mode

def prepare_circle():
	return prepare_mode(pick_mode())

def spawn_columns(worker, apply_fn):
	handles = []
	size = saved_data_module.cached_size
	x = 0
	while x < size:
		move_module.go_to(x, 0)
		if num_drones() < max_drones():
			handle = spawn_drone(worker)
			if handle != None:
				handles.append(handle)
				x = x + 1
				continue
		apply_fn(worker())
		x = x + 1
	move_module.go_to(0, 0)
	i = 0
	while i < len(handles):
		apply_fn(wait_for(handles[i]))
		i = i + 1

def companion_code(entity):
	if entity == Entities.Carrot:
		return COMP_CARROT
	if entity == Entities.Tree:
		return COMP_TREE
	if entity == Entities.Bush:
		return COMP_BUSH
	return COMP_GRASS

def plant_companion_code(code):
	if code == COMP_CARROT:
		return plant_carrot()
	if code == COMP_TREE:
		return plant_tree()
	if code == COMP_BUSH:
		return plant_bush()
	return plant_grass()

def is_filler_plan(plan):
	if plan == saved_data_module.PLAN_GRASS:
		return True
	if plan == saved_data_module.PLAN_BUSH:
		return True
	if plan == saved_data_module.PLAN_TREE:
		return True
	if plan == saved_data_module.PLAN_CARROT:
		return True
	return False

def note_companion():
	if num_unlocked(Unlocks.Polyculture) == 0:
		return None
	plan = saved_data_module.plan_at(get_pos_x(), get_pos_y())
	if is_filler_plan(plan) == False:
		return None
	info = get_companion()
	if info == None:
		return None
	wanted = info[0]
	pos = info[1]
	return [pos[0], pos[1], companion_code(wanted)]

def plant_companion_here(code):
	plan = saved_data_module.plan_at(get_pos_x(), get_pos_y())
	if plan == saved_data_module.PLAN_SUNFLOWER:
		return
	if plan == saved_data_module.PLAN_PUMPKIN:
		return
	if plan == saved_data_module.PLAN_CACTUS:
		return
	ent = get_entity_type()
	if code == COMP_CARROT:
		if ent == Entities.Carrot:
			return
	elif code == COMP_TREE:
		if ent == Entities.Tree:
			return
	elif code == COMP_BUSH:
		if ent == Entities.Bush:
			return
	elif ent == Entities.Grass:
		if code == COMP_GRASS:
			return
	if ent != None:
		if ent != Entities.Grass:
			harvest()
	planted = plant_companion_code(code)
	saved_data_module.set_plant_type(get_pos_x(), get_pos_y(), planted)

def plant_same_column_companions(column_x, comps):
	left = []
	i = 0
	while i < len(comps):
		item = comps[i]
		if item[0] == column_x:
			while get_pos_y() < item[1]:
				move(North)
			while get_pos_y() > item[1]:
				move(South)
			plant_companion_here(item[2])
		else:
			left.append(item)
		i = i + 1
	return left

def reset_companions():
	global pending_companions
	pending_companions = []

def queue_companions(items):
	if items == None:
		return
	i = 0
	while i < len(items):
		pending_companions.append(items[i])
		i = i + 1

def plant_queued_companions():
	i = 0
	while i < len(pending_companions):
		item = pending_companions[i]
		move_module.go_to(item[0], item[1])
		plant_companion_here(item[2])
		i = i + 1
	reset_companions()

def column_should_fertilize():
	if fertilizer_wanted:
		return True
	if num_items(Items.Fertilizer) < 1:
		return False
	weird_w = num_items(Items.Weird_Substance) * VALUE_WEIRD
	if weird_w < min_crop_wealth():
		return True
	return False

def handle_fertilizer_tile():
	plan = saved_data_module.plan_at(get_pos_x(), get_pos_y())
	if plan == saved_data_module.PLAN_PUMPKIN:
		return
	if plan == saved_data_module.PLAN_SUNFLOWER:
		return
	if plan == saved_data_module.PLAN_CACTUS:
		return
	entity = get_entity_type()
	if entity == None:
		return
	if entity == Entities.Dead_Pumpkin:
		return
	if can_harvest():
		return
	if num_items(Items.Fertilizer) < 1:
		return
	use_item(Items.Fertilizer)

def handle_water_tile():
	if get_water() >= 0.5:
		return
	if num_items(Items.Water) < 1:
		return
	# 多工人会同时看到还有水，一起 use 就会报警。
	if num_items(Items.Water) < num_drones():
		return
	use_item(Items.Water)

def handle_plant():
	pos_x = get_pos_x()
	pos_y = get_pos_y()
	current_entity = get_entity_type()

	plan = saved_data_module.plan_at(pos_x, pos_y)

	if plan == saved_data_module.PLAN_SUNFLOWER:
		if saved_data_module.sunflower_should_hold_plant():
			if current_entity != Entities.Sunflower:
				saved_data_module.set_plant_type(pos_x, pos_y, current_entity)
				return

	if plan_already_growing(current_entity, plan):
		saved_data_module.set_plant_type(pos_x, pos_y, current_entity)
		if current_entity == Entities.Sunflower:
			if saved_data_module.sunflower_petal_at(pos_x, pos_y) < 0:
				record_sunflower_here(pos_x, pos_y)
		return

	if can_replace_now(current_entity, plan) == False:
		saved_data_module.set_plant_type(pos_x, pos_y, current_entity)
		return

	planted = plant_for_plan(plan)
	saved_data_module.set_plant_type(pos_x, pos_y, planted)
	if planted == Entities.Sunflower:
		record_sunflower_here(pos_x, pos_y)
	if planted == Entities.Cactus:
		if current_entity != Entities.Cactus:
			saved_data_module.set_cactus_size(pos_x, pos_y, -1)
