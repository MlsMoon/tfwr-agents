# 恐龙：偶边长哈密顿圈 + 只朝苹果方向的安全抄近路。
# 纯跟圈平均走 size²/2 才吃一颗，32×32 太慢。贪心曼哈顿横切尾巴，n 很小。
# 抄近路：邻居必须在「当前 → 苹果」的圈弧上（圈下标前进且不超过苹果），
# 再选离苹果圈距最短的一格。折返相邻时可以跳，尾巴仍在身后。
# 摘帽 print("dino", eaten, steps)。不要 set_world_size。

import plant_module
import saved_data_module

def hat_off():
	change_hat(Hats.Straw_Hat)

def any_move():
	if can_move(North):
		return True
	if can_move(East):
		return True
	if can_move(South):
		return True
	if can_move(West):
		return True
	return False

def cycle_dir(x, y, n):
	if y == 0:
		if x == 0:
			return North
		return West
	if x == n - 1:
		return South
	if x % 2 == 0:
		if y < n - 1:
			return North
		return East
	if y > 1:
		return South
	return East

def serp_dir(x, y, n):
	if y % 2 == 0:
		if x < n - 1:
			return East
		return North
	if x > 0:
		return West
	return North

def next_dir(x, y, n):
	if n % 2 == 0:
		return cycle_dir(x, y, n)
	return serp_dir(x, y, n)

def cycle_index(x, y, n):
	if y == 0:
		if x == 0:
			return 0
		last_col = n + (n - 2) * (n - 1)
		return last_col + (n - 1) + (n - 1 - x)
	if x == 0:
		return y
	if x == n - 1:
		last_col = n + (n - 2) * (n - 1)
		return last_col + (n - 1 - y)
	base = n + (x - 1) * (n - 1)
	if x % 2 == 1:
		return base + (n - 1 - y)
	return base + (y - 1)

def serp_index(x, y, n):
	if y % 2 == 0:
		return y * n + x
	return y * n + (n - 1 - x)

def cell_index(x, y, n, even):
	if even:
		return cycle_index(x, y, n)
	return serp_index(x, y, n)

def fwd(a, b, period):
	d = b - a
	if d < 0:
		d = d + period
	return d

def neighbor(x, y, d):
	if d == North:
		return [x, y + 1]
	if d == East:
		return [x + 1, y]
	if d == South:
		return [x, y - 1]
	return [x - 1, y]

def leftover_if(d, x, y, n, even, here, goal, period, need):
	if can_move(d) == False:
		return -1
	pos = neighbor(x, y, d)
	idx = cell_index(pos[0], pos[1], n, even)
	step = fwd(here, idx, period)
	if step < 1:
		return -1
	if step >= need:
		return -1
	return fwd(idx, goal, period)

def pick_dir(tx, ty, n, even):
	x = get_pos_x()
	y = get_pos_y()
	here = cell_index(x, y, n, even)
	goal = cell_index(tx, ty, n, even)
	period = n * n
	need = fwd(here, goal, period)
	if need < 1:
		return next_dir(x, y, n)
	if even == False:
		if goal < here:
			return next_dir(x, y, n)
	best = next_dir(x, y, n)
	best_left = leftover_if(best, x, y, n, even, here, goal, period, need)
	if best_left < 0:
		best = None
		best_left = period
	left = leftover_if(North, x, y, n, even, here, goal, period, need)
	if left >= 0:
		if left < best_left:
			best = North
			best_left = left
	left = leftover_if(East, x, y, n, even, here, goal, period, need)
	if left >= 0:
		if left < best_left:
			best = East
			best_left = left
	left = leftover_if(South, x, y, n, even, here, goal, period, need)
	if left >= 0:
		if left < best_left:
			best = South
			best_left = left
	left = leftover_if(West, x, y, n, even, here, goal, period, need)
	if left >= 0:
		if left < best_left:
			best = West
			best_left = left
	if best != None:
		return best
	return next_dir(x, y, n)

def step_along(n):
	d = next_dir(get_pos_x(), get_pos_y(), n)
	if can_move(d) == False:
		return False
	return move(d)

def step_toward(tx, ty, n, even):
	d = pick_dir(tx, ty, n, even)
	if can_move(d) == False:
		d = next_dir(get_pos_x(), get_pos_y(), n)
		if can_move(d) == False:
			return False
	return move(d)

def bones_still_needed():
	bone = plant_module.crop_score(saved_data_module.PLAN_DINOSAUR)
	pumpkin = plant_module.crop_score(saved_data_module.PLAN_PUMPKIN)
	cactus = plant_module.crop_score(saved_data_module.PLAN_CACTUS)
	if bone > pumpkin:
		return True
	if bone > cactus:
		return True
	return False

def finish(eaten, steps):
	print("dino", eaten, steps)
	hat_off()
	return True

def chase_cycle():
	n = saved_data_module.world_size()
	if n < 1:
		n = get_world_size()
	even = True
	if n % 2 != 0:
		even = False
	change_hat(Hats.Dinosaur_Hat)
	if get_entity_type() != Entities.Apple:
		hat_off()
		return False
	eaten = 0
	steps = 0
	miss = 0
	limit = n * n
	has_tgt = False
	tx = 0
	ty = 0
	while True:
		if num_items(Items.Power) < plant_module.MIN_POWER:
			return finish(eaten, steps)
		if any_move() == False:
			return finish(eaten, steps)
		on_apple = False
		if get_entity_type() == Entities.Apple:
			on_apple = True
			miss = 0
			if plant_module.can_buy_apple() == False:
				if step_along(n):
					eaten = eaten + 1
					steps = steps + 1
				return finish(eaten, steps)
			nxt = measure()
			if nxt == None:
				return finish(eaten, steps)
			tx = nxt[0]
			ty = nxt[1]
			has_tgt = True
		else:
			miss = miss + 1
			if has_tgt:
				if get_pos_x() == tx:
					if get_pos_y() == ty:
						has_tgt = False
			if miss >= limit:
				return finish(eaten, steps)
		moved = False
		if has_tgt:
			moved = step_toward(tx, ty, n, even)
		else:
			moved = step_along(n)
		if moved == False:
			return finish(eaten, steps)
		steps = steps + 1
		if on_apple:
			eaten = eaten + 1

def run():
	clear()
	started = False
	while True:
		if plant_module.can_buy_apple() == False:
			return
		if num_items(Items.Power) < plant_module.MIN_POWER:
			return
		if started:
			if bones_still_needed() == False:
				return
		if chase_cycle() == False:
			return
		started = True
