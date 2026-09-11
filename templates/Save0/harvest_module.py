# 收获：填料成熟就收。特殊作物只清错格，不在这里收完。
# 向日葵只测不收。南瓜补坏瓜。仙人掌扫列只清错作物并测尺寸。

import cactus_module
import pumpkin_module
import saved_data_module

def handle_harvest():
	current_entity = get_entity_type()
	pos_x = get_pos_x()
	pos_y = get_pos_y()
	plan = saved_data_module.plan_at(pos_x, pos_y)

	if current_entity == Entities.Dead_Pumpkin:
		if plan == saved_data_module.PLAN_PUMPKIN:
			pumpkin_module.replace_dead()
			return
		return

	if current_entity == Entities.Pumpkin:
		if plan != saved_data_module.PLAN_PUMPKIN:
			harvest()
			saved_data_module.set_cactus_size(pos_x, pos_y, -1)
			saved_data_module.set_plant_type(pos_x, pos_y, None)
			return
		return

	if current_entity == Entities.Sunflower:
		if plan != saved_data_module.PLAN_SUNFLOWER:
			harvest()
			saved_data_module.clear_sunflower_tile(pos_x, pos_y)
			saved_data_module.set_cactus_size(pos_x, pos_y, -1)
			saved_data_module.set_plant_type(pos_x, pos_y, None)
		return

	if plan == saved_data_module.PLAN_SUNFLOWER:
		if current_entity != None:
			if current_entity != Entities.Grass:
				harvest()
				saved_data_module.set_cactus_size(pos_x, pos_y, -1)
				saved_data_module.set_plant_type(pos_x, pos_y, None)
		return

	if plan == saved_data_module.PLAN_CACTUS:
		cactus_module.handle_column_tile()
		return

	if plan == saved_data_module.PLAN_PUMPKIN:
		pumpkin_module.handle_column_tile()
		return

	harvest()
