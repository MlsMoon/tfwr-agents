# 仙人掌：独占整田。只和仙人掌计划格交换。列南北、行东西排序。
# 整田有序再收到西南角，产量是数量的平方。计划格上的南瓜/向日葵先清。

import move_module
import plant_module
import saved_data_module

def handle_column_tile():
	# 扫列只清错作物并测尺寸，不 swap、不收。
	entity = get_entity_type()
	pos_x = get_pos_x()
	pos_y = get_pos_y()

	if entity != Entities.Cactus:
		if entity == Entities.Dead_Pumpkin:
			planted = plant_module.plant_cactus()
			saved_data_module.set_plant_type(pos_x, pos_y, planted)
			saved_data_module.set_cactus_size(pos_x, pos_y, -1)
			return
		if entity != None:
			if entity != Entities.Grass:
				harvest()
		saved_data_module.clear_sunflower_tile(pos_x, pos_y)
		saved_data_module.set_cactus_size(pos_x, pos_y, -1)
		saved_data_module.set_plant_type(pos_x, pos_y, None)
		return

	if can_harvest() == False:
		saved_data_module.record_cactus_tile(entity, False)
		return

	my_size = saved_data_module.cactus_size_at(pos_x, pos_y)
	if my_size < 0:
		my_size = measure()
		if my_size == None:
			saved_data_module.record_cactus_tile(entity, True)
			return
		if my_size > 9:
			harvest()
			saved_data_module.clear_sunflower_tile(pos_x, pos_y)
			saved_data_module.set_cactus_size(pos_x, pos_y, -1)
			saved_data_module.set_plant_type(pos_x, pos_y, None)
			return
		saved_data_module.set_cactus_size(pos_x, pos_y, my_size)
	saved_data_module.record_cactus_tile(entity, True)

def neighbor_ready_size(pos_x, pos_y):
	if saved_data_module.is_cactus_tile(pos_x, pos_y) == False:
		return -1
	size = saved_data_module.world_size()
	if pos_x < 0:
		return -1
	if pos_y < 0:
		return -1
	if pos_x >= size:
		return -1
	if pos_y >= size:
		return -1
	size_val = saved_data_module.cactus_size_at(pos_x, pos_y)
	if size_val < 0:
		return -1
	if size_val > 9:
		return -1
	return size_val

def try_swaps(pos_x, pos_y, my_size, do_ns, do_ew):
	swapped = False
	if do_ew:
		west = neighbor_ready_size(pos_x - 1, pos_y)
		if west >= 0:
			if west > my_size:
				if swap(West):
					saved_data_module.set_cactus_size(pos_x - 1, pos_y, my_size)
					saved_data_module.set_cactus_size(pos_x, pos_y, west)
					my_size = west
					swapped = True
		east = neighbor_ready_size(pos_x + 1, pos_y)
		if east >= 0:
			if east < my_size:
				if swap(East):
					saved_data_module.set_cactus_size(pos_x + 1, pos_y, my_size)
					saved_data_module.set_cactus_size(pos_x, pos_y, east)
					my_size = east
					swapped = True
	if do_ns:
		if pos_y > 0:
			south = neighbor_ready_size(pos_x, pos_y - 1)
			if south >= 0:
				if south > my_size:
					if swap(South):
						saved_data_module.set_cactus_size(pos_x, pos_y - 1, my_size)
						saved_data_module.set_cactus_size(pos_x, pos_y, south)
						my_size = south
						swapped = True
		north = neighbor_ready_size(pos_x, pos_y + 1)
		if north >= 0:
			if north < my_size:
				if swap(North):
					saved_data_module.set_cactus_size(pos_x, pos_y + 1, my_size)
					saved_data_module.set_cactus_size(pos_x, pos_y, north)
					swapped = True
	return swapped

def handle_sort_body(do_ns, do_ew, allow_harvest):
	entity = get_entity_type()
	pos_x = get_pos_x()
	pos_y = get_pos_y()

	if entity != Entities.Cactus:
		saved_data_module.record_cactus_tile(entity, False)
		if entity == Entities.Dead_Pumpkin:
			planted = plant_module.plant_cactus()
			saved_data_module.set_plant_type(pos_x, pos_y, planted)
			return
		if entity != None:
			if entity != Entities.Grass:
				harvest()
		saved_data_module.clear_sunflower_tile(pos_x, pos_y)
		saved_data_module.set_cactus_size(pos_x, pos_y, -1)
		saved_data_module.set_plant_type(pos_x, pos_y, None)
		return

	grown = can_harvest()
	if grown == False:
		saved_data_module.record_cactus_tile(entity, False)
		return

	my_size = saved_data_module.cactus_size_at(pos_x, pos_y)
	if my_size < 0:
		my_size = measure()
		if my_size == None:
			saved_data_module.record_cactus_tile(entity, True)
			return
		if my_size > 9:
			harvest()
			saved_data_module.clear_sunflower_tile(pos_x, pos_y)
			saved_data_module.set_cactus_size(pos_x, pos_y, -1)
			saved_data_module.set_plant_type(pos_x, pos_y, None)
			return
		saved_data_module.set_cactus_size(pos_x, pos_y, my_size)

	if try_swaps(pos_x, pos_y, my_size, do_ns, do_ew):
		saved_data_module.record_cactus_tile(entity, True)
		return

	saved_data_module.record_cactus_tile(entity, True)
	if allow_harvest:
		if saved_data_module.can_harvest_cactus_now():
			harvest()
			saved_data_module.mark_cactus_harvest_done()

def handle_sort_ns():
	handle_sort_body(True, False, False)

def handle_sort_ew():
	handle_sort_body(False, True, False)

def handle_harvest_final():
	handle_sort_body(True, True, True)

def collect_cells(is_column, index, limit):
	cells = []
	i = 0
	while i < limit:
		if is_column:
			pos_x = index
			pos_y = i
		else:
			pos_x = i
			pos_y = index
		if saved_data_module.plan_at(pos_x, pos_y) == saved_data_module.PLAN_CACTUS:
			sz = saved_data_module.cactus_size_at(pos_x, pos_y)
			if sz >= 0:
				cells.append([pos_x, pos_y, sz])
		i = i + 1
	return cells

def apply_cells(cells):
	if cells == None:
		return
	i = 0
	while i < len(cells):
		cell = cells[i]
		saved_data_module.set_cactus_size(cell[0], cell[1], cell[2])
		i = i + 1

def work_column_sort():
	column_x = get_pos_x()
	height = saved_data_module.world_size()
	while get_pos_y() != 0:
		move(South)
	y = 0
	while y < height:
		if saved_data_module.plan_at(column_x, y) == saved_data_module.PLAN_CACTUS:
			handle_sort_ns()
		y = y + 1
		if y < height:
			move(North)
	y = height - 1
	while y > 0:
		move(South)
		y = y - 1
		if saved_data_module.plan_at(column_x, y) == saved_data_module.PLAN_CACTUS:
			handle_sort_ns()
	return collect_cells(True, column_x, height)

def work_row_sort():
	row_y = get_pos_y()
	origin = 0
	width = saved_data_module.world_size()
	while get_pos_x() != origin:
		if get_pos_x() > origin:
			move(West)
		else:
			move(East)
	x = 0
	while x < width:
		pos_x = origin + x
		if saved_data_module.plan_at(pos_x, row_y) == saved_data_module.PLAN_CACTUS:
			handle_sort_ew()
		x = x + 1
		if x < width:
			move(East)
	x = width - 1
	while x > 0:
		move(West)
		x = x - 1
		pos_x = origin + x
		if saved_data_module.plan_at(pos_x, row_y) == saved_data_module.PLAN_CACTUS:
			handle_sort_ew()
	return collect_cells(False, row_y, origin + width)

def wait_handles(handles):
	i = 0
	while i < len(handles):
		apply_cells(wait_for(handles[i]))
		i = i + 1

def run_column_sorts():
	origin = 0
	width = saved_data_module.world_size()
	handles = []
	x = 0
	while x < width:
		column_x = origin + x
		if saved_data_module.cactus_tiles_in_column(column_x) < 1:
			x = x + 1
			continue
		move_module.go_to(column_x, 0)
		if num_drones() < max_drones():
			handle = spawn_drone(work_column_sort)
			if handle != None:
				handles.append(handle)
				x = x + 1
				continue
		apply_cells(work_column_sort())
		x = x + 1
	wait_handles(handles)

def run_row_sorts():
	origin = 0
	height = saved_data_module.world_size()
	handles = []
	y = 0
	while y < height:
		move_module.go_to(origin, y)
		if num_drones() < max_drones():
			handle = spawn_drone(work_row_sort)
			if handle != None:
				handles.append(handle)
				y = y + 1
				continue
		apply_cells(work_row_sort())
		y = y + 1
	wait_handles(handles)

def work_plant_column():
	column_x = get_pos_x()
	size = saved_data_module.world_size()
	while get_pos_y() != 0:
		move(South)
	cact_seen = 0
	cact_issue = False
	y = 0
	while y < size:
		handle_column_tile()
		plant_module.handle_plant()
		plant_module.record_sunflower_if_needed()
		plant_module.handle_water_tile()
		if saved_data_module.plan_at(get_pos_x(), get_pos_y()) == saved_data_module.PLAN_CACTUS:
			cact_seen = cact_seen + 1
			ent = get_entity_type()
			if ent != Entities.Cactus:
				cact_issue = True
			elif can_harvest() == False:
				cact_issue = True
		y = y + 1
		if y < size:
			move(North)
	cacti = []
	row = 0
	while row < size:
		if saved_data_module.plan_at(column_x, row) == saved_data_module.PLAN_CACTUS:
			sz = saved_data_module.cactus_size_at(column_x, row)
			if sz >= 0:
				cacti.append([row, sz])
		row = row + 1
	cact_ok = False
	if cact_seen > 0:
		if cact_issue == False:
			cact_ok = True
	return [column_x, cact_ok, cacti]

def apply_plant_report(report):
	if report == None:
		return
	column_x = report[0]
	cacti = report[2]
	i = 0
	while i < len(cacti):
		row = cacti[i]
		saved_data_module.set_cactus_size(column_x, row[0], row[1])
		i = i + 1
	saved_data_module.apply_column_report(column_x, False, report[1])

def finish_pass():
	if saved_data_module.has_cactus_column() == False:
		return
	size = saved_data_module.world_size()
	if size < 1:
		return
	passes = size
	i = 0
	while i < passes:
		if saved_data_module.cactus_block_sorted():
			break
		run_column_sorts()
		run_row_sorts()
		i = i + 1
	saved_data_module.refresh_cactus_harvest_allowed()
	if saved_data_module.can_harvest_cactus_now() == False:
		if saved_data_module.all_cactus_columns_ok():
			saved_data_module.print_cactus_skip()
		return
	move_module.go_to(0, 0)
	handle_harvest_final()

def run():
	saved_data_module.reset_column_ok_only(saved_data_module.cached_size)
	plant_module.spawn_columns(work_plant_column, apply_plant_report)
	finish_pass()
