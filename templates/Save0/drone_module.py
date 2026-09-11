# 多无人机：run_mode 只选模式再调模块 run()。发列用 plant_module.spawn_columns。
# 填料列在这里种、收、记伴侣。恐龙单机 measure 追苹果。不要 import 进迷宫。

import cactus_module
import dinosaur_module
import harvest_module
import move_module
import plant_module
import pumpkin_module
import saved_data_module
import sunflower_module

def work_filler_column():
	column_x = get_pos_x()
	size = saved_data_module.world_size()
	while get_pos_y() != 0:
		move(South)
	do_fert = plant_module.column_should_fertilize()
	comps = []
	y = 0
	while y < size:
		harvest_module.handle_harvest()
		plant_module.handle_plant()
		item = plant_module.note_companion()
		if item != None:
			comps.append(item)
		if do_fert:
			plant_module.handle_fertilizer_tile()
		plant_module.handle_water_tile()
		y = y + 1
		if y < size:
			move(North)
	return plant_module.plant_same_column_companions(column_x, comps)

def apply_filler(report):
	plant_module.queue_companions(report)

def run_filler():
	plant_module.reset_companions()
	saved_data_module.reset_column_ok_only(saved_data_module.cached_size)
	plant_module.spawn_columns(work_filler_column, apply_filler)
	plant_module.plant_queued_companions()

def run_mode():
	saved_data_module.refresh_size()
	mode = plant_module.pick_mode()
	if mode == saved_data_module.PLAN_DINOSAUR:
		dinosaur_module.run()
		move_module.go_to(0, 0)
		return
	plant_module.prepare_mode(mode)
	if mode == saved_data_module.PLAN_SUNFLOWER:
		sunflower_module.run()
	elif mode == saved_data_module.PLAN_PUMPKIN:
		pumpkin_module.run()
	elif mode == saved_data_module.PLAN_CACTUS:
		cactus_module.run()
	else:
		run_filler()
	move_module.go_to(0, 0)

def run_farm_wave():
	run_mode()
