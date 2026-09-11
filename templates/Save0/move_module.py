# 走位：环绕最短路径 go_to。旧蛇形只给单机脚本用，农场主循环不走这里。

import saved_data_module

is_up_direction = True

def go_to(tx, ty):
	size = saved_data_module.world_size()
	while get_pos_x() != tx:
		cx = get_pos_x()
		east = tx - cx
		if east < 0:
			east = east + size
		west = cx - tx
		if west < 0:
			west = west + size
		if east <= west:
			move(East)
		else:
			move(West)
	while get_pos_y() != ty:
		cy = get_pos_y()
		north = ty - cy
		if north < 0:
			north = north + size
		south = cy - ty
		if south < 0:
			south = south + size
		if north <= south:
			move(North)
		else:
			move(South)

def set_up_direction(in_is_up_direction):
	global is_up_direction
	is_up_direction = in_is_up_direction

def apply_column_direction():
	if get_pos_y() == 0:
		set_up_direction(True)
	else:
		set_up_direction(False)

def need_change_column():
	if is_up_direction:
		if get_pos_y() == saved_data_module.cached_size - 1:
			return True
		return False
	if get_pos_y() == 0:
		return True
	return False

def skip_clean_pumpkin_columns():
	if saved_data_module.should_skip_current_column() == False:
		return

	# 只有脚下这列已经确认健康才东移。不要在每格都 begin_column，否则永远走不满一列。
	skipped = 0
	size = saved_data_module.cached_size
	while saved_data_module.should_skip_current_column():
		move(East)
		skipped = skipped + 1
		if skipped >= size:
			return

	apply_column_direction()
	saved_data_module.begin_column(get_pos_x())

def handle_change_column():
	if need_change_column() == False:
		return False

	# 仙人掌还没排好：掉头沿原路再扫一遍，不要急着 East。
	if saved_data_module.should_fold_cactus_column(get_pos_x()):
		saved_data_module.begin_cactus_fold()
		if is_up_direction:
			set_up_direction(False)
			move(South)
		else:
			set_up_direction(True)
			move(North)
		return True

	# 先结算本列，再东移；健康南瓜列下一轮才会被 skip。
	saved_data_module.finish_column(get_pos_x())
	move(East)
	apply_column_direction()
	skip_clean_pumpkin_columns()
	saved_data_module.begin_column(get_pos_x())
	return True

def handle_move():
	is_changed_column = handle_change_column()
	if is_changed_column:
		return

	if is_up_direction:
		move(North)
	else:
		move(South)
