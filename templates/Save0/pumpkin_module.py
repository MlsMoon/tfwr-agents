# 南瓜：独占整田。只补死格。对角 measure 同一个 ID 再收合体。
# 不要收零散小合体。产量是这块立方。

import move_module
import plant_module
import saved_data_module

def replace_dead():
	# 坏南瓜 harvest() 没用，必须种点新的才会消失。
	plan = saved_data_module.plan_at(get_pos_x(), get_pos_y())
	planted = plant_module.plant_for_plan(plan)
	saved_data_module.set_plant_type(get_pos_x(), get_pos_y(), planted)

def handle_column_tile():
	entity = get_entity_type()
	pos_x = get_pos_x()
	pos_y = get_pos_y()
	plan = saved_data_module.plan_at(pos_x, pos_y)

	if entity == Entities.Dead_Pumpkin:
		saved_data_module.record_pumpkin_tile(entity, False)
		replace_dead()
		return

	if entity == Entities.Pumpkin:
		if plan != saved_data_module.PLAN_PUMPKIN:
			harvest()
			saved_data_module.set_cactus_size(pos_x, pos_y, -1)
			saved_data_module.set_plant_type(pos_x, pos_y, None)
			return
		saved_data_module.record_pumpkin_tile(entity, can_harvest())
		return

	if plan == saved_data_module.PLAN_PUMPKIN:
		saved_data_module.record_pumpkin_tile(entity, False)
		if entity != None:
			if entity != Entities.Grass:
				harvest()
				saved_data_module.set_cactus_size(pos_x, pos_y, -1)
				saved_data_module.set_plant_type(pos_x, pos_y, None)

def work_plant_column():
	column_x = get_pos_x()
	size = saved_data_module.world_size()
	while get_pos_y() != 0:
		move(South)
	pump_seen = 0
	pump_ready = 0
	pump_dead = 0
	y = 0
	while y < size:
		handle_column_tile()
		plant_module.handle_plant()
		plant_module.handle_water_tile()
		if saved_data_module.plan_at(get_pos_x(), get_pos_y()) == saved_data_module.PLAN_PUMPKIN:
			ent = get_entity_type()
			pump_seen = pump_seen + 1
			if ent == Entities.Dead_Pumpkin:
				pump_dead = pump_dead + 1
			elif ent == Entities.Pumpkin:
				if can_harvest():
					pump_ready = pump_ready + 1
		y = y + 1
		if y < size:
			move(North)
	return [column_x, pump_seen, pump_ready, pump_dead]

def apply_plant_report(report):
	if report == None:
		return
	saved_data_module.add_pumpkin_wave_counts(report[1], report[2], report[3])

def corners_same():
	size = saved_data_module.world_size()
	if size < 1:
		return False
	move_module.go_to(0, 0)
	if get_entity_type() != Entities.Pumpkin:
		return False
	if can_harvest() == False:
		return False
	a = measure()
	move_module.go_to(size - 1, size - 1)
	if get_entity_type() != Entities.Pumpkin:
		return False
	if can_harvest() == False:
		return False
	b = measure()
	if a == None:
		return False
	if b == None:
		return False
	return a == b

def finish_pass():
	if saved_data_module.can_harvest_pumpkin_now() == False:
		return
	if corners_same() == False:
		return
	move_module.go_to(0, 0)
	if get_entity_type() == Entities.Pumpkin:
		if can_harvest():
			harvest()
			saved_data_module.mark_pumpkin_harvest_done()

def run():
	saved_data_module.reset_column_ok_only(saved_data_module.cached_size)
	plant_module.spawn_columns(work_plant_column, apply_plant_report)
	finish_pass()
