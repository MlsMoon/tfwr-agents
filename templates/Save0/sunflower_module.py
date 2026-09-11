# 向日葵：整田下种并测花瓣。收的时候按花瓣档位从高到低，一列一个工人。
# 至少留 10 朵才有 8 倍。同一档收完再收下一档。档位没收完不要补种，
# 否则新花可能变成更高的未熟最大，整波丢掉倍数。
# 工人内存是拷贝，收成看父进程交回的格子数。花瓣计数用 hist，不要整表重算。
# 工人只走到本档的 y，发完最后一列先回家再 wait。当前档未熟就地施肥。

import harvest_module
import plant_module
import move_module
import saved_data_module

def work_plant_column():
	column_x = get_pos_x()
	size = saved_data_module.world_size()
	while get_pos_y() != 0:
		move(South)
	petals = []
	y = 0
	while y < size:
		harvest_module.handle_harvest()
		plant_module.handle_plant()
		plant_module.record_sunflower_if_needed()
		plant_module.handle_water_tile()
		p = saved_data_module.sunflower_petal_at(column_x, y)
		if p >= 0:
			petals.append([y, p])
		y = y + 1
		if y < size:
			move(North)
	return [column_x, petals]

def apply_plant_report(report):
	if report == None:
		return
	column_x = report[0]
	petals = report[1]
	i = 0
	while i < len(petals):
		row = petals[i]
		saved_data_module.set_sunflower_petals(column_x, row[0], row[1])
		i = i + 1

def ripen_here():
	tries = 0
	while can_harvest() == False:
		if tries >= 3:
			return False
		if num_items(Items.Fertilizer) < 1:
			return False
		use_item(Items.Fertilizer)
		tries = tries + 1
	return True

def make_harvest_worker(rows):
	def work_column_harvest_tier():
		column_x = get_pos_x()
		while get_pos_y() != 0:
			move(South)
		cleared = []
		i = 0
		while i < len(rows):
			ty = rows[i]
			while get_pos_y() < ty:
				move(North)
			if get_entity_type() == Entities.Sunflower:
				if ripen_here():
					harvest()
					saved_data_module.clear_sunflower_tile(column_x, ty)
					saved_data_module.set_plant_type(column_x, ty, None)
					cleared.append(ty)
			i = i + 1
		return [column_x, cleared]
	return work_column_harvest_tier

def apply_clears(report):
	if report == None:
		return 0
	column_x = report[0]
	cleared = report[1]
	n = 0
	i = 0
	while i < len(cleared):
		saved_data_module.clear_sunflower_tile(column_x, cleared[i])
		saved_data_module.set_plant_type(column_x, cleared[i], None)
		n = n + 1
		i = i + 1
	return n

def wait_one_harvest(handles):
	if len(handles) < 1:
		return 0
	n = apply_clears(wait_for(handles[0]))
	i = 0
	while i < len(handles) - 1:
		handles[i] = handles[i + 1]
		i = i + 1
	handles.pop()
	return n

def run_tier_harvests(jobs):
	handles = []
	got = 0
	i = 0
	while i < len(jobs):
		job = jobs[i]
		move_module.go_to(job[0], 0)
		worker = make_harvest_worker(job[1])
		if num_drones() >= max_drones():
			got = got + wait_one_harvest(handles)
		if num_drones() < max_drones():
			handle = spawn_drone(worker)
			if handle != None:
				handles.append(handle)
				i = i + 1
				continue
		got = got + apply_clears(worker())
		i = i + 1
	move_module.go_to(0, 0)
	j = 0
	while j < len(handles):
		got = got + apply_clears(wait_for(handles[j]))
		j = j + 1
	return got

def harvest_current_tier():
	# 1 收成，0 没熟，-1 只剩保底该放锁。
	if saved_data_module.sunflower_bonus_ready() == False:
		return -1
	max_val = saved_data_module.sunflower_max_petals()
	if max_val < 7:
		return -1
	n_max = saved_data_module.count_sunflowers_with_petals(max_val)
	if n_max < 1:
		return -1
	known = saved_data_module.count_known_sunflowers()
	budget = known - saved_data_module.MIN_SUNFLOWERS
	if budget < 1:
		return -1
	if budget > n_max:
		budget = n_max
	saved_data_module.set_sunflower_tier(max_val)
	jobs = saved_data_module.collect_sunflower_tier_jobs(max_val, budget)
	if len(jobs) < 1:
		return -1
	got = run_tier_harvests(jobs)
	if got > 0:
		return 1
	return 0

def finish_pass():
	# hold 之后收过的格花瓣是 -1，known < expected 是正常的，不要当表不齐直接退出。
	if saved_data_module.sunflower_should_hold_plant() == False:
		if saved_data_module.sunflower_scan_complete() == False:
			saved_data_module.recount_sunflower_scan()
			if saved_data_module.sunflower_scan_complete() == False:
				return
	if saved_data_module.sunflower_bonus_ready() == False:
		quick_print("sun_unlock", "no_bonus")
		saved_data_module.end_sunflower_lock()
		return
	while True:
		result = harvest_current_tier()
		if result == 1:
			continue
		if result == -1:
			quick_print("sun_unlock", "budget")
			saved_data_module.end_sunflower_lock()
			return
		return

def run():
	saved_data_module.reset_column_ok_only(saved_data_module.cached_size)
	if saved_data_module.sunflower_should_hold_plant() == False:
		plant_module.spawn_columns(work_plant_column, apply_plant_report)
		saved_data_module.recount_sunflower_scan()
		if saved_data_module.count_known_sunflowers() >= saved_data_module.MIN_SUNFLOWERS:
			saved_data_module.mark_sunflower_hold()
	finish_pass()
