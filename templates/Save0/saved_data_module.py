# 跨格记忆：每格种什么、当前模式、网格、南瓜齐不齐、向日葵花瓣。
# Timing：调用/读变量/模块点号 0 tick；二元运算和 if 各 1；下标 1；def 1。
# 热路径禁止整表扫描。脚下格用 plan_at（已在界内）。邻格才 plan_for_tile。
# 向日葵花瓣增量改 max/known，不要每格 recompute。
# tile_plan[x][y] 是种植/收获/施肥的依据。一波一个模式，布局是单矩形。
# 南瓜/仙人掌轮次锁未收完不换模式。Power < 500 打断锁。

PLAN_GRASS = 0
PLAN_BUSH = 1
PLAN_TREE = 2
PLAN_CARROT = 3
PLAN_PUMPKIN = 4
PLAN_SUNFLOWER = 5
PLAN_CACTUS = 6
PLAN_DINOSAUR = 7

plant_data = [[]]
archived_plant_data = [[]]
tile_plan = [[]]
column_plan = []
column_ok = []
column_visit_x = -1
column_tiles_seen = 0
column_issue = False
cactus_tiles_seen = 0
cactus_issue = False
cactus_column_folded = False
pumpkin_harvest_allowed = False
pumpkin_cycle = False
cactus_harvest_allowed = False
cactus_cycle = False
sunflower_cycle = False
sunflower_hold_plant = False
sunflower_tier_box = [0]
sunflower_cut_box = [0]
sunflower_petals = [[]]
sunflower_mapped = False
sunflower_max_x = -1
sunflower_max_y = -1
sunflower_max_val = -1
sunflower_hist = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
cactus_sizes = [[]]
layout_ready = False
cached_size = 0
# 列表盒子不重绑：layout_box / sunflower_box / cactus_box。花瓣不要只写独立的 sunflower_petals。
layout_box = [tile_plan]
size_box = [0]
cactus_box = [cactus_sizes]
sunflower_box = [sunflower_petals]
column_mixed = []
cactus_count = []
has_cactus_flag = False
has_pumpkin_flag = False
cactus_sort_dirty = True
cactus_sort_cached = False
LAYOUT_GEN = 9
last_layout = [-1, -1, -1, -1, -1]
current_mode = PLAN_GRASS
sunflower_known = 0
sunflower_expected = 0
cactus_rect_w = 0
cactus_rect_h = 0
cactus_dim = [0, 0]
cactus_origin = [0, 0]
pumpkin_col_count = 0
pumpkin_ok_count = 0
cactus_col_count = 0
cactus_ok_count = 0

def get_current_plan():
	return current_mode

def get_current_mode():
	return current_mode

def plan_for_column(column_x):
	if column_x < 0:
		return PLAN_GRASS
	if column_x >= cached_size:
		return PLAN_GRASS
	return column_plan[column_x]

# 脚下格：refresh 之后坐标一定在界内，两次下标。
def plan_at(pos_x, pos_y):
	return layout_box[0][pos_x][pos_y]

# 邻格可能越界（仙人掌西/南，或世界边缘）。
def plan_for_tile(pos_x, pos_y):
	if pos_x < 0:
		return PLAN_GRASS
	if pos_y < 0:
		return PLAN_GRASS
	size = world_size()
	if pos_x >= size:
		return PLAN_GRASS
	if pos_y >= size:
		return PLAN_GRASS
	return layout_box[0][pos_x][pos_y]

def is_pumpkin_column(column_x):
	return plan_for_column(column_x) == PLAN_PUMPKIN

def is_sunflower_column(column_x):
	return plan_for_column(column_x) == PLAN_SUNFLOWER

def column_has_sunflower(column_x):
	if column_x < 0:
		return False
	size = world_size()
	if column_x >= size:
		return False
	y = 0
	while y < size:
		if plan_at(column_x, y) == PLAN_SUNFLOWER:
			return True
		y = y + 1
	return False

def is_cactus_column(column_x):
	return plan_for_column(column_x) == PLAN_CACTUS

def is_pumpkin_tile(pos_x, pos_y):
	return plan_for_tile(pos_x, pos_y) == PLAN_PUMPKIN

def is_sunflower_tile(pos_x, pos_y):
	return plan_for_tile(pos_x, pos_y) == PLAN_SUNFLOWER

def is_cactus_tile(pos_x, pos_y):
	return plan_for_tile(pos_x, pos_y) == PLAN_CACTUS

def column_is_mixed(column_x):
	if column_x < 0:
		return False
	if column_x >= len(column_mixed):
		return False
	return column_mixed[column_x]

MIN_SUNFLOWERS = 10
MIN_POWER = 500
POWER_TARGET = 16000
pumpkin_wave_need = 0
pumpkin_wave_ready = 0
pumpkin_wave_dead = 0

def drone_count():
	n = max_drones()
	if n < 1:
		n = 1
	return n

# 向日葵模式占整田。按花瓣档位多人收，少占列会浪费工人。
def sunflower_rect(size):
	if size < 1:
		return [1, 1]
	return [size, size]

# 仙人掌占整田，产量是数量平方。不要再按工人数缩成小矩形。
def cactus_rect(size):
	if size < 1:
		return [1, 1]
	return [size, size]

def cactus_block_origin():
	return cactus_origin[0]

def cactus_block_width():
	width = cactus_dim[0]
	if width < 1:
		width = cactus_rect_w
	return width

def cactus_block_height():
	height = cactus_dim[1]
	if height < 1:
		height = cactus_rect_h
	return height

def print_sun_skip():
	print("sun_skip", sunflower_known, sunflower_expected)

def print_cactus_skip():
	sorted_flag = 0
	if cactus_block_sorted():
		sorted_flag = 1
	print("cactus_skip", cactus_ok_count, cactus_col_count, sorted_flag)

def cactus_tiles_in_column(column_x):
	if column_x < 0:
		return 0
	if column_x >= len(cactus_count):
		return 0
	return cactus_count[column_x]

def has_cactus_column():
	return has_cactus_flag

def count_cactus_columns():
	return cactus_col_count

def cactus_cycle_active():
	if cactus_cycle == False:
		return False
	return has_cactus_column()

def count_sunflower_columns():
	total = 0
	for column_index in range(len(column_plan)):
		if column_plan[column_index] == PLAN_SUNFLOWER:
			total = total + 1
	return total

def has_pumpkin_column():
	return has_pumpkin_flag

def count_pumpkin_columns():
	return pumpkin_col_count

def pumpkin_cycle_active():
	if pumpkin_cycle == False:
		return False
	return has_pumpkin_column()

def sunflower_cycle_active():
	if sunflower_cycle == False:
		return False
	if sunflower_expected < MIN_SUNFLOWERS:
		return False
	return True

def mark_sunflower_hold():
	global sunflower_hold_plant
	sunflower_hold_plant = True

def sunflower_should_hold_plant():
	return sunflower_hold_plant

def end_sunflower_lock():
	global sunflower_cycle
	global sunflower_hold_plant
	sunflower_cycle = False
	sunflower_hold_plant = False

def column_has_tier(column_x, target):
	if column_x < 0:
		return False
	size = world_size()
	if column_x >= size:
		return False
	y = 0
	while y < size:
		if plan_at(column_x, y) == PLAN_SUNFLOWER:
			if sunflower_petal_at(column_x, y) == target:
				return True
		y = y + 1
	return False

def set_sunflower_tier(val):
	sunflower_tier_box[0] = val

def sunflower_tier_target():
	return sunflower_tier_box[0]

def set_sunflower_cut(n):
	sunflower_cut_box[0] = n

def sunflower_cut_left():
	return sunflower_cut_box[0]

def take_sunflower_cut():
	if sunflower_cut_box[0] < 1:
		return False
	sunflower_cut_box[0] = sunflower_cut_box[0] - 1
	return True

def hist_add(val, delta):
	if val < 0:
		return
	if val >= len(sunflower_hist):
		return
	sunflower_hist[val] = sunflower_hist[val] + delta

def clear_sunflower_hist():
	i = 0
	while i < len(sunflower_hist):
		sunflower_hist[i] = 0
		i = i + 1

def rebuild_sunflower_hist():
	clear_sunflower_hist()
	size = world_size()
	grid = sunflower_box[0]
	tiles = layout_box[0]
	x = 0
	while x < size:
		y = 0
		while y < size:
			if tiles[x][y] == PLAN_SUNFLOWER:
				hist_add(grid[x][y], 1)
			y = y + 1
		x = x + 1

def count_sunflowers_with_petals(val):
	if val < 0:
		return 0
	if val >= len(sunflower_hist):
		return 0
	return sunflower_hist[val]

def collect_sunflower_tier_jobs(target, budget):
	jobs = []
	left = budget
	size = world_size()
	tiles = layout_box[0]
	grid = sunflower_box[0]
	x = 0
	while x < size:
		if left < 1:
			break
		rows = []
		y = 0
		while y < size:
			if left < 1:
				break
			if tiles[x][y] == PLAN_SUNFLOWER:
				if grid[x][y] == target:
					rows.append(y)
					left = left - 1
			y = y + 1
		if len(rows) > 0:
			jobs.append([x, rows])
		x = x + 1
	return jobs

def reset_column_ok_only(size):
	global column_ok
	global column_visit_x
	global column_tiles_seen
	global column_issue
	global cactus_tiles_seen
	global cactus_issue
	global cactus_column_folded
	global pumpkin_harvest_allowed
	global cactus_harvest_allowed
	global pumpkin_ok_count
	global cactus_ok_count
	global pumpkin_wave_need
	global pumpkin_wave_ready
	global pumpkin_wave_dead

	column_ok = []
	for column_index in range(size):
		column_ok.append(False)
	column_visit_x = -1
	column_tiles_seen = 0
	column_issue = False
	cactus_tiles_seen = 0
	cactus_issue = False
	cactus_column_folded = False
	pumpkin_harvest_allowed = False
	cactus_harvest_allowed = False
	pumpkin_wave_need = 0
	pumpkin_wave_ready = 0
	pumpkin_wave_dead = 0
	pumpkin_ok_count = 0
	cactus_ok_count = 0

def reset_column_derived(size):
	global column_mixed
	global cactus_count
	global has_cactus_flag
	global has_pumpkin_flag
	global cactus_rect_w
	global cactus_rect_h
	global pumpkin_col_count
	global cactus_col_count
	global sunflower_expected
	column_mixed = []
	cactus_count = []
	for column_index in range(size):
		column_mixed.append(False)
		cactus_count.append(0)
	has_cactus_flag = False
	has_pumpkin_flag = False
	cactus_rect_w = 0
	cactus_rect_h = 0
	cactus_dim[0] = 0
	cactus_dim[1] = 0
	cactus_origin[0] = 0
	cactus_origin[1] = 0
	pumpkin_col_count = 0
	cactus_col_count = 0
	sunflower_expected = 0

def finalize_layout_tables(size, old_plan, old_ok):
	global column_plan
	global column_ok
	global column_mixed
	global cactus_count
	global has_cactus_flag
	global has_pumpkin_flag
	global cactus_rect_w
	global cactus_rect_h
	global pumpkin_col_count
	global pumpkin_ok_count
	global cactus_col_count
	global cactus_ok_count
	global sunflower_expected
	global sunflower_known
	global sunflower_mapped
	global pumpkin_harvest_allowed
	global cactus_harvest_allowed
	global cactus_sort_dirty

	new_plan = []
	new_ok = []
	new_mixed = []
	new_cactus = []
	has_cactus_flag = False
	has_pumpkin_flag = False
	pumpkin_col_count = 0
	pumpkin_ok_count = 0
	cactus_col_count = 0
	cactus_ok_count = 0
	sunflower_expected = 0
	sunflower_known = 0
	min_cx = size
	max_cx = -1
	old_plan_len = len(old_plan)
	old_ok_len = len(old_ok)

	for column_index in range(size):
		column_tiles = tile_plan[column_index]
		column_petals = sunflower_box[0][column_index]
		first_plan = column_tiles[0]
		mixed = False
		cactus_here = 0
		chosen = PLAN_GRASS
		found_special = False
		for row_index in range(size):
			tile = column_tiles[row_index]
			if tile != first_plan:
				mixed = True
			if tile == PLAN_SUNFLOWER:
				sunflower_expected = sunflower_expected + 1
				if column_petals[row_index] >= 0:
					sunflower_known = sunflower_known + 1
				if cactus_box[0][column_index][row_index] >= 0:
					cactus_box[0][column_index][row_index] = -1
			else:
				if column_petals[row_index] >= 0:
					column_petals[row_index] = -1
				if tile == PLAN_CACTUS:
					cactus_here = cactus_here + 1
					if column_index < min_cx:
						min_cx = column_index
					if column_index > max_cx:
						max_cx = column_index
				else:
					if cactus_box[0][column_index][row_index] >= 0:
						cactus_box[0][column_index][row_index] = -1
			if found_special == False:
				if tile == PLAN_PUMPKIN:
					chosen = PLAN_PUMPKIN
					found_special = True
				elif tile == PLAN_CACTUS:
					chosen = PLAN_CACTUS
					found_special = True
				elif tile == PLAN_SUNFLOWER:
					chosen = PLAN_SUNFLOWER
					found_special = True
		if found_special == False:
			for row_index in range(size):
				if chosen != PLAN_GRASS:
					break
				tile = column_tiles[row_index]
				if tile != PLAN_GRASS:
					chosen = tile
		ok_val = False
		if chosen == PLAN_PUMPKIN:
			has_pumpkin_flag = True
			pumpkin_col_count = pumpkin_col_count + 1
		elif chosen == PLAN_CACTUS:
			if column_index < old_plan_len:
				if old_plan[column_index] == PLAN_CACTUS:
					if column_index < old_ok_len:
						ok_val = old_ok[column_index]
		if cactus_here > 0:
			has_cactus_flag = True
			cactus_col_count = cactus_col_count + 1
			if ok_val:
				cactus_ok_count = cactus_ok_count + 1
		new_plan.append(chosen)
		new_ok.append(ok_val)
		new_mixed.append(mixed)
		new_cactus.append(cactus_here)

	if max_cx < 0:
		cactus_rect_w = 0
		cactus_rect_h = 0
		cactus_origin[0] = 0
		cactus_origin[1] = 0
	else:
		cactus_rect_w = max_cx - min_cx + 1
		cactus_rect_h = size
		cactus_origin[0] = min_cx
		cactus_origin[1] = 0
	cactus_dim[0] = cactus_rect_w
	cactus_dim[1] = cactus_rect_h
	cactus_sort_dirty = True

	column_plan = new_plan
	column_ok = new_ok
	column_mixed = new_mixed
	cactus_count = new_cactus
	pumpkin_harvest_allowed = False
	if pumpkin_col_count > 0:
		if pumpkin_ok_count == pumpkin_col_count:
			pumpkin_harvest_allowed = True
	cactus_harvest_allowed = False
	if cactus_col_count > 0:
		if cactus_ok_count == cactus_col_count:
			if cactus_block_sorted():
				cactus_harvest_allowed = True
	rebuild_sunflower_hist()
	recompute_sunflower_max()
	sunflower_mapped = False
	if sunflower_expected > 0:
		if sunflower_known == sunflower_expected:
			sunflower_mapped = True

def reset_tile_plan(size):
	global tile_plan
	tile_plan = []
	for column_index in range(size):
		column_tiles = []
		for row_index in range(size):
			column_tiles.append(PLAN_GRASS)
		tile_plan.append(column_tiles)
	publish_layout()
	reset_column_derived(size)
	invalidate_last_layout()

def reset_sunflower_petals(size):
	global sunflower_petals
	global sunflower_mapped
	global sunflower_max_x
	global sunflower_max_y
	global sunflower_max_val
	global sunflower_known
	sunflower_petals = []
	for column_index in range(size):
		column_petals = []
		for row_index in range(size):
			column_petals.append(-1)
		sunflower_petals.append(column_petals)
	sunflower_mapped = False
	sunflower_max_x = -1
	sunflower_max_y = -1
	sunflower_max_val = -1
	sunflower_known = 0
	clear_sunflower_hist()
	sunflower_box[0] = sunflower_petals

def reset_cactus_sizes(size):
	global cactus_sizes
	global cactus_sort_dirty
	global cactus_sort_cached
	cactus_sizes = []
	for column_index in range(size):
		column_sizes = []
		for row_index in range(size):
			column_sizes.append(-1)
		cactus_sizes.append(column_sizes)
	cactus_box[0] = cactus_sizes
	cactus_sort_dirty = True
	cactus_sort_cached = False

def reset_pumpkin_columns(size):
	global column_plan
	global pumpkin_cycle
	global cactus_cycle
	global sunflower_cycle

	column_plan = []
	for column_index in range(size):
		column_plan.append(PLAN_GRASS)
	pumpkin_cycle = False
	cactus_cycle = False
	sunflower_cycle = False
	reset_tile_plan(size)
	reset_column_ok_only(size)
	reset_sunflower_petals(size)
	reset_cactus_sizes(size)

def publish_layout():
	layout_box[0] = tile_plan
	size_box[0] = cached_size
	cactus_box[0] = cactus_sizes
	sunflower_box[0] = sunflower_petals

def world_size():
	size = size_box[0]
	if size < 1:
		size = cached_size
	if size < 1:
		size = get_world_size()
	return size

def refresh_size():
	global cached_size
	size = get_world_size()
	if size == cached_size:
		size_box[0] = size
		return size
	ensure_world_size(size)
	cached_size = size
	publish_layout()
	return size

def invalidate_last_layout():
	global last_layout
	last_layout = [-1, -1, -1, -1, -1]

def ensure_world_size(size):
	global plant_data
	global archived_plant_data
	global cached_size

	need_rebuild = False
	if len(plant_data) != size:
		need_rebuild = True
	elif size > 0:
		if len(plant_data[0]) != size:
			need_rebuild = True

	if need_rebuild == False:
		if len(column_plan) != size:
			reset_pumpkin_columns(size)
		if len(column_ok) != size:
			reset_column_ok_only(size)
		if len(sunflower_petals) != size:
			reset_sunflower_petals(size)
		elif size > 0:
			if len(sunflower_petals[0]) != size:
				reset_sunflower_petals(size)
		if len(cactus_sizes) != size:
			reset_cactus_sizes(size)
		elif size > 0:
			if len(cactus_sizes[0]) != size:
				reset_cactus_sizes(size)
		if len(tile_plan) != size:
			reset_tile_plan(size)
		elif size > 0:
			if len(tile_plan[0]) != size:
				reset_tile_plan(size)
		cached_size = size
		publish_layout()
		return

	archived_plant_data = []
	for old_column in plant_data:
		archived_column = []
		for old_entity in old_column:
			archived_column.append(old_entity)
		archived_plant_data.append(archived_column)

	plant_data = []
	for column_index in range(size):
		column_data = []
		for row_index in range(size):
			column_data.append(Entities.Grass)
		plant_data.append(column_data)

	# 新列是空的，旧合体标记和花瓣表不能继续用。
	reset_pumpkin_columns(size)
	cached_size = size
	publish_layout()

def get_archived_plant_data():
	return archived_plant_data

def get_plant_type(posx, posy):
	if posx < 0:
		return Entities.Grass
	if posy < 0:
		return Entities.Grass
	if posx >= cached_size:
		return Entities.Grass
	if posy >= cached_size:
		return Entities.Grass
	return plant_data[posx][posy]

def set_plant_type(pos_x, pos_y, entity):
	if pos_x < 0:
		return
	if pos_y < 0:
		return
	if pos_x >= cached_size:
		return
	if pos_y >= cached_size:
		return
	plant_data[pos_x][pos_y] = entity
	if entity != Entities.Sunflower:
		if sunflower_petal_at(pos_x, pos_y) >= 0:
			set_sunflower_petals(pos_x, pos_y, -1)

def paint_first_rect(new_tiles, plan, width, height, size):
	if width < 0:
		width = 0
	if height < 0:
		height = 0
	if width > size:
		width = size
	if height > size:
		height = size
	for column_index in range(width):
		for row_index in range(height):
			new_tiles[column_index][row_index] = plan

def apply_mode_flags(mode):
	global pumpkin_cycle
	global cactus_cycle
	global sunflower_cycle
	global sunflower_hold_plant
	global current_mode
	current_mode = mode
	if mode == PLAN_PUMPKIN:
		pumpkin_cycle = True
	else:
		pumpkin_cycle = False
	if mode == PLAN_CACTUS:
		cactus_cycle = True
	else:
		cactus_cycle = False
	if mode == PLAN_SUNFLOWER:
		sunflower_cycle = True
	else:
		sunflower_cycle = False
		sunflower_hold_plant = False

def apply_mode_layout(mode, width, height):
	# 一波一个矩形。剩余格铺草，方便清掉上一波留下的特殊作物。
	global tile_plan
	global column_plan
	global column_ok
	global layout_ready
	global last_layout

	size = cached_size
	if size < 1:
		size = refresh_size()
	if len(last_layout) != 5:
		invalidate_last_layout()

	use_w = width
	use_h = height
	if use_w < 1:
		use_w = 1
	if use_h < 1:
		use_h = 1
	if use_w > size:
		use_w = size
	if use_h > size:
		use_h = size

	if last_layout[0] == mode:
		if last_layout[1] == use_w:
			if last_layout[2] == use_h:
				if last_layout[3] == size:
					if last_layout[4] == LAYOUT_GEN:
						layout_ready = True
						apply_mode_flags(mode)
						return

	new_tiles = []
	for column_index in range(size):
		column_tiles = []
		for row_index in range(size):
			column_tiles.append(PLAN_GRASS)
		new_tiles.append(column_tiles)

	paint_first_rect(new_tiles, mode, use_w, use_h, size)

	old_plan = column_plan
	old_ok = column_ok
	tile_plan = new_tiles
	apply_mode_flags(mode)
	layout_ready = True
	publish_layout()
	last_layout[0] = mode
	last_layout[1] = use_w
	last_layout[2] = use_h
	last_layout[3] = size
	last_layout[4] = LAYOUT_GEN
	finalize_layout_tables(size, old_plan, old_ok)

def sunflower_petal_at(pos_x, pos_y):
	if pos_x < 0:
		return -1
	if pos_y < 0:
		return -1
	size = world_size()
	if pos_x >= size:
		return -1
	if pos_y >= size:
		return -1
	grid = sunflower_box[0]
	if pos_x >= len(grid):
		return -1
	if pos_y >= len(grid[pos_x]):
		return -1
	return grid[pos_x][pos_y]

def set_sunflower_petals(pos_x, pos_y, petals):
	global sunflower_known
	global sunflower_max_x
	global sunflower_max_y
	global sunflower_max_val
	if pos_x < 0:
		return
	if pos_y < 0:
		return
	size = world_size()
	if pos_x >= size:
		return
	if pos_y >= size:
		return
	grid = sunflower_box[0]
	if pos_x >= len(grid):
		return
	if pos_y >= len(grid[pos_x]):
		return
	if petals == None:
		petals = -1
	if petals >= 0:
		if plan_for_tile(pos_x, pos_y) != PLAN_SUNFLOWER:
			petals = -1
	old = grid[pos_x][pos_y]
	if old == petals:
		return
	grid[pos_x][pos_y] = petals
	hist_add(old, 0 - 1)
	hist_add(petals, 1)
	if old < 0:
		if petals >= 0:
			sunflower_known = sunflower_known + 1
	else:
		if petals < 0:
			sunflower_known = sunflower_known - 1
	if petals > sunflower_max_val:
		sunflower_max_val = petals
		sunflower_max_x = pos_x
		sunflower_max_y = pos_y
		return
	if old == sunflower_max_val:
		if petals < old:
			recompute_sunflower_max()

def clear_sunflower_tile(pos_x, pos_y):
	set_sunflower_petals(pos_x, pos_y, -1)

def recount_sunflower_scan():
	# 工人写共享花瓣表时，主无人机的 known 不会跟着加。收完花也要重数。
	global sunflower_known
	global sunflower_expected
	global sunflower_mapped
	known = 0
	expected = 0
	size = world_size()
	grid = sunflower_box[0]
	tiles = layout_box[0]
	x = 0
	while x < size:
		y = 0
		while y < size:
			if tiles[x][y] == PLAN_SUNFLOWER:
				expected = expected + 1
				if grid[x][y] >= 0:
					known = known + 1
			y = y + 1
		x = x + 1
	sunflower_known = known
	sunflower_expected = expected
	sunflower_mapped = False
	if expected > 0:
		if known == expected:
			sunflower_mapped = True
	rebuild_sunflower_hist()
	recompute_sunflower_max()

def expected_sunflower_tiles():
	return sunflower_expected

def count_known_sunflowers():
	return sunflower_known

def sunflower_bonus_ready():
	return sunflower_known >= MIN_SUNFLOWERS

def recompute_sunflower_max():
	# 只扫 15..0 的计数，不要整田找最大朵。
	global sunflower_max_x
	global sunflower_max_y
	global sunflower_max_val
	p = 15
	while p >= 0:
		if sunflower_hist[p] > 0:
			sunflower_max_val = p
			return
		p = p - 1
	sunflower_max_val = -1
	sunflower_max_x = -1
	sunflower_max_y = -1

def mark_sunflower_mapped():
	global sunflower_mapped
	sunflower_mapped = True

def unmap_sunflowers():
	global sunflower_mapped
	sunflower_mapped = False

def sunflower_is_mapped():
	return sunflower_mapped

def sunflower_max_column():
	return sunflower_max_x

def sunflower_max_pos():
	return [sunflower_max_x, sunflower_max_y]

# 计划里的向日葵格都测过，才知道谁是全局最大。
def sunflower_scan_complete():
	if sunflower_expected < 1:
		return False
	return sunflower_known == sunflower_expected

def sunflower_max_petals():
	return sunflower_max_val

def begin_column(column_x):
	global column_visit_x
	global column_tiles_seen
	global column_issue
	global cactus_tiles_seen
	global cactus_issue
	global cactus_column_folded
	column_visit_x = column_x
	column_tiles_seen = 0
	column_issue = False
	cactus_tiles_seen = 0
	cactus_issue = False
	cactus_column_folded = False

def record_pumpkin_tile(entity, is_harvestable):
	global column_tiles_seen
	global column_issue

	pos_x = get_pos_x()
	if column_visit_x != pos_x:
		begin_column(pos_x)

	column_tiles_seen = column_tiles_seen + 1
	if entity == Entities.Dead_Pumpkin:
		column_issue = True
	elif entity != Entities.Pumpkin:
		column_issue = True
	elif is_harvestable == False:
		column_issue = True

def cactus_size_at(pos_x, pos_y):
	if pos_x < 0:
		return -1
	if pos_y < 0:
		return -1
	grid = cactus_box[0]
	if pos_x >= len(grid):
		return -1
	if pos_y >= len(grid[pos_x]):
		return -1
	return grid[pos_x][pos_y]

def set_cactus_size(pos_x, pos_y, size_val):
	global cactus_sort_dirty
	if pos_x < 0:
		return
	if pos_y < 0:
		return
	grid = cactus_box[0]
	if pos_x >= len(grid):
		return
	if pos_y >= len(grid[pos_x]):
		return
	if size_val == None:
		size_val = -1
	if cactus_box[0][pos_x][pos_y] == size_val:
		return
	cactus_box[0][pos_x][pos_y] = size_val
	cactus_sort_dirty = True

def should_fold_cactus_column(column_x):
	if cactus_column_folded:
		return False
	if cactus_tiles_in_column(column_x) < 1:
		return False
	if cactus_block_sorted():
		return False
	return True

def begin_cactus_fold():
	global cactus_tiles_seen
	global cactus_issue
	global cactus_column_folded
	cactus_tiles_seen = 0
	cactus_issue = False
	cactus_column_folded = True

def record_cactus_tile(entity, is_harvestable):
	global cactus_tiles_seen
	global cactus_issue

	pos_x = get_pos_x()
	if plan_at(pos_x, get_pos_y()) != PLAN_CACTUS:
		return
	if column_visit_x != pos_x:
		begin_column(pos_x)

	cactus_tiles_seen = cactus_tiles_seen + 1
	if entity != Entities.Cactus:
		cactus_issue = True
	elif is_harvestable == False:
		cactus_issue = True

def cactus_block_sorted():
	global cactus_sort_dirty
	global cactus_sort_cached
	if cactus_sort_dirty == False:
		return cactus_sort_cached
	cactus_sort_dirty = False
	cactus_sort_cached = False
	size = world_size()
	tiles = layout_box[0]
	sizes = cactus_box[0]
	for column_index in range(size):
		if cactus_count[column_index] < 1:
			continue
		column_tiles = tiles[column_index]
		column_sizes = sizes[column_index]
		for row_index in range(size):
			if column_tiles[row_index] != PLAN_CACTUS:
				continue
			here = column_sizes[row_index]
			if here < 0:
				return False
			if column_index > 0:
				if tiles[column_index - 1][row_index] == PLAN_CACTUS:
					if sizes[column_index - 1][row_index] > here:
						return False
			if row_index > 0:
				if column_tiles[row_index - 1] == PLAN_CACTUS:
					if column_sizes[row_index - 1] > here:
						return False
	cactus_sort_cached = True
	return True

def apply_column_report(column_x, pumpkin_ok, cactus_ok):
	# 工人各有一份内存。列结果由主无人机合并。
	global pumpkin_harvest_allowed
	global cactus_harvest_allowed
	global pumpkin_ok_count
	global cactus_ok_count

	if column_x < 0:
		return
	if column_x >= cached_size:
		return

	was_ok = column_ok[column_x]
	now_ok = False
	if column_plan[column_x] == PLAN_PUMPKIN:
		if pumpkin_ok:
			now_ok = True
	if cactus_count[column_x] > 0:
		if cactus_ok:
			now_ok = True
	column_ok[column_x] = now_ok

	if column_plan[column_x] == PLAN_PUMPKIN:
		if was_ok == False:
			if now_ok:
				pumpkin_ok_count = pumpkin_ok_count + 1
		else:
			if now_ok == False:
				pumpkin_ok_count = pumpkin_ok_count - 1
		refresh_pumpkin_harvest_allowed()
	if cactus_count[column_x] > 0:
		if was_ok == False:
			if now_ok:
				cactus_ok_count = cactus_ok_count + 1
		else:
			if now_ok == False:
				cactus_ok_count = cactus_ok_count - 1
		cactus_harvest_allowed = False
		if cactus_col_count > 0:
			if cactus_ok_count == cactus_col_count:
				if cactus_block_sorted():
					cactus_harvest_allowed = True

def finish_column(column_x):
	global pumpkin_harvest_allowed
	global cactus_harvest_allowed
	global column_visit_x
	global pumpkin_ok_count
	global cactus_ok_count

	if column_x < 0:
		return
	if column_x >= cached_size:
		return

	was_ok = column_ok[column_x]
	now_ok = False
	if column_plan[column_x] == PLAN_PUMPKIN:
		if column_tiles_seen >= cached_size:
			if column_issue == False:
				now_ok = True
	else:
		need_cactus = cactus_count[column_x]
		if need_cactus > 0:
			if cactus_tiles_seen >= need_cactus:
				if cactus_issue == False:
					now_ok = True
	column_ok[column_x] = now_ok

	if column_plan[column_x] == PLAN_PUMPKIN:
		if was_ok == False:
			if now_ok:
				pumpkin_ok_count = pumpkin_ok_count + 1
		else:
			if now_ok == False:
				pumpkin_ok_count = pumpkin_ok_count - 1
		refresh_pumpkin_harvest_allowed()
	if cactus_count[column_x] > 0:
		if was_ok == False:
			if now_ok:
				cactus_ok_count = cactus_ok_count + 1
		else:
			if now_ok == False:
				cactus_ok_count = cactus_ok_count - 1
		cactus_harvest_allowed = False
		if cactus_col_count > 0:
			if cactus_ok_count == cactus_col_count:
				if cactus_block_sorted():
					cactus_harvest_allowed = True
	column_visit_x = -1

def column_is_ok(column_x):
	if column_x < 0:
		return False
	if column_x >= cached_size:
		return False
	return column_ok[column_x]

def all_pumpkin_columns_ok():
	return pumpkin_harvest_allowed

def all_cactus_columns_ok():
	if cactus_col_count < 1:
		return False
	return cactus_ok_count == cactus_col_count

def all_columns_ok():
	return pumpkin_harvest_allowed

def should_skip_clean_pumpkin():
	# 坏南瓜和未合体列必须每圈都走，不能靠上一圈的 ok 跳过。
	return False

# 花瓣表齐了之后，纯向日葵的非最大列不用再走。表不齐就整列都走。
def should_skip_sunflower_column():
	if sunflower_scan_complete() == False:
		return False
	if sunflower_mapped == False:
		return False
	pos_x = get_pos_x()
	if column_mixed[pos_x]:
		return False
	if column_plan[pos_x] != PLAN_SUNFLOWER:
		return False
	if sunflower_max_x < 0:
		return False
	if pos_x == sunflower_max_x:
		return False
	return True

def should_skip_current_column():
	# 一波一模式后每列都走，清掉上一波留下的作物。
	return False

def add_pumpkin_wave_counts(need, ready, dead):
	global pumpkin_wave_need
	global pumpkin_wave_ready
	global pumpkin_wave_dead
	global pumpkin_harvest_allowed
	pumpkin_wave_need = pumpkin_wave_need + need
	pumpkin_wave_ready = pumpkin_wave_ready + ready
	pumpkin_wave_dead = pumpkin_wave_dead + dead
	refresh_pumpkin_harvest_allowed()

def refresh_pumpkin_harvest_allowed():
	global pumpkin_harvest_allowed
	pumpkin_harvest_allowed = False
	if pumpkin_wave_need < 1:
		if pumpkin_col_count > 0:
			if pumpkin_ok_count == pumpkin_col_count:
				pumpkin_harvest_allowed = True
		return
	if pumpkin_wave_dead > 0:
		return
	if pumpkin_wave_ready < pumpkin_wave_need:
		return
	# 本块计划格都是成熟活南瓜再收，不要收零散小合体。
	pumpkin_harvest_allowed = True

def can_harvest_pumpkin_now():
	return pumpkin_harvest_allowed

def can_harvest_cactus_now():
	return cactus_harvest_allowed

def refresh_cactus_harvest_allowed():
	global cactus_harvest_allowed
	cactus_harvest_allowed = False
	if cactus_col_count < 1:
		return
	if cactus_ok_count != cactus_col_count:
		return
	if cactus_block_sorted():
		cactus_harvest_allowed = True

def mark_pumpkin_harvest_done():
	global pumpkin_cycle
	reset_column_ok_only(cached_size)
	pumpkin_cycle = False

def mark_cactus_harvest_done():
	global cactus_cycle
	global cactus_harvest_allowed
	reset_column_ok_only(cached_size)
	reset_cactus_sizes(cached_size)
	cactus_cycle = False
	cactus_harvest_allowed = False

def farm_layout_ready():
	return layout_ready

def locked_cycle_active():
	if sunflower_cycle_active():
		return True
	if pumpkin_cycle_active():
		return True
	if cactus_cycle_active():
		return True
	return False
