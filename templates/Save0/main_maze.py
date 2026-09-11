# 迷宫入口。游戏里执行本文件才刷金子。
# 不要被 main / plant import（顶层会开跑）。
# 失败原因会 print 到工程根 output.txt。

import maze_module

clear()

while True:
	if maze_module.try_start_maze() == False:
		break
	maze_module.run_maze()
	while num_drones() > 1:
		pass
	clear()
