# TFWR_RUN_MAIN
# 入口：清场后回到西南角。只跑农场，不碰金子/迷宫。
# 每波 pick_mode 后交给对应模块 run()。刷金子请执行 main_maze。

import drone_module
import saved_data_module

print("boot main")
clear()

while get_pos_x() != 0:
	move(West)

while get_pos_y() != 0:
	move(South)

saved_data_module.refresh_size()

while True:
	drone_module.run_mode()
