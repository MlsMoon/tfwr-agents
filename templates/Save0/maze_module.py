# 迷宫生成和寻路。只给 main_maze 用，不要 import 进农场。
# 失败原因用 print()，会进工程根 output.txt。
# 分叉处尽量 spawn 工人；满员就自己 DFS 回溯。

MIN_POWER = 500

maze_size = 0
maze_need = 0

def maze_substance_need():
	# 官方：边长 * 2^(迷宫升级-1)。方言不要写 **。
	size = get_world_size()
	need = size
	level = num_unlocked(Unlocks.Mazes)
	extra = level - 1
	while extra > 0:
		need = need * 2
		extra = extra - 1
	return need

def try_start_maze():
	global maze_size
	global maze_need
	if num_unlocked(Unlocks.Mazes) < 1:
		print("maze: locked")
		return False
	if num_items(Items.Power) < MIN_POWER:
		print("maze: low power")
		return False
	maze_size = get_world_size()
	maze_need = maze_substance_need()
	if num_items(Items.Weird_Substance) < maze_need:
		print("maze: low weird")
		print(maze_need)
		return False
	if get_entity_type() != None:
		harvest()
	if get_entity_type() != None:
		till()
	if plant(Entities.Bush) == False:
		print("maze: plant bush failed")
		return False
	if use_item(Items.Weird_Substance, maze_need) == False:
		print("maze: use weird failed")
		return False
	if measure() == None:
		print("maze: no treasure")
		return False
	return True

def opposite_dir(direction):
	if direction < 2:
		return direction + 2
	return direction - 2

def make_maze_branch(direction, back):
	# 工厂把方向钉死，避免闭包读到循环变量的最后一次值。
	def maze_branch():
		dirs = [North, East, South, West]
		if can_move(dirs[direction]):
			move(dirs[direction])
		maze_dfs(back)
	return maze_branch

def maze_dfs(came_from):
	# 只收宝藏。走道不是树篱。measure() 变空说明别人已经收了。
	if get_entity_type() == Entities.Treasure:
		harvest()
		return
	if measure() == None:
		return
	dirs = [North, East, South, West]
	di = 0
	while di < 4:
		if di != came_from:
			if can_move(dirs[di]):
				back = opposite_dir(di)
				spawned = False
				if num_drones() < max_drones():
					handle = spawn_drone(make_maze_branch(di, back))
					if handle != None:
						spawned = True
				if spawned == False:
					move(dirs[di])
					maze_dfs(back)
					if get_entity_type() == Entities.Treasure:
						harvest()
						return
					if measure() == None:
						return
					if can_move(dirs[back]):
						move(dirs[back])
		di = di + 1

def wait_other_drones():
	while num_drones() > 1:
		if get_entity_type() == Entities.Treasure:
			harvest()
			return
		if measure() == None:
			pass

def run_maze():
	maze_dfs(-1)
	if get_entity_type() == Entities.Treasure:
		harvest()
	wait_other_drones()
