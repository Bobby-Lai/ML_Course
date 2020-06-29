import math

last_command = ["NONE", "NONE", "NONE"]
last_path = 0
target_path = 0

class MLPlay:
	def __init__(self, player):
		self.player = player
		if self.player == "player1":
			self.player_no = 0
		elif self.player == "player2":
			self.player_no = 1
		elif self.player == "player3":
			self.player_no = 2
		elif self.player == "player4":
			self.player_no = 3
		self.car_vel = 0
		self.car_pos = (0, 0)
		self.coin_num = 0
		self.last_coin_num = 0
		self.computer_cars = []
		self.coins_pos = []
		self.last_frame = 0
		self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
		self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center

	def update(self, scene_info:dict):
		"""
		Generate the command according to the received scene information
		"""
		global last_path
		global target_path
		global last_command
		has_car = []
		command = []
		surrounded = 0

		if len(scene_info[self.player])!=0:         # Player is alive (has position info)
			if last_path == 0:                      # Initialize last_path to current path
				last_path = scene_info[self.player][0]
				target_path = last_path
			if abs(scene_info[self.player][0] - target_path) < 3 and scene_info[self.player][0]!= last_path:  # Player completes path transition
				last_path = scene_info[self.player][0]

			# Get basic scene information :
			# player's position, lane, velocity, coin number
			# computer cars' position, coins' position
			self.car_pos = scene_info[self.player]
			self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
			for car in scene_info["cars_info"]:
				if car["id"]==self.player_no:
					self.car_vel = car["velocity"]
					self.coin_num = car["coin_num"]
			self.computer_cars = scene_info["computer_cars"]
			if scene_info.__contains__("coins"):
				self.coins_pos = scene_info["coins"]
			

			#		玩家車輛相對位置九宮格
			#        |    |    |    |
			#        |  0 |  1 |  2 |
			#        |    |  4 |    |
			#        |  3 |  c |  5 |
			#        |    |    |    |
			#        |  6 |  7 |  8 |
			#        |    |    |    |

			# 初始化
			for i in range(9):
				new = []
				for j in range(4):
					new.append(0)
				has_car.append(new)

			# 左右邊界
			rinside = self.lanes[self.car_lane] + 35
			routter = self.lanes[self.car_lane] + 105
			linside = self.lanes[self.car_lane] - 35
			loutter = self.lanes[self.car_lane] - 105
			
			# 生成當前狀態九宮格 (若格內有車，flag = 1, 並記錄速度及位置)
			# 填入左邊界
			if self.car_lane == 0:
				has_car[0][0] = 1
				has_car[0][1] = 0
				has_car[0][2] = -35
				has_car[0][3] = self.car_pos[1] + 100
				has_car[3][0] = 1
				has_car[3][1] = 0
				has_car[3][2] = -35
				has_car[3][3] = self.car_pos[1]
				has_car[6][0] = 1
				has_car[6][1] = 0
				has_car[6][2] = -35
				has_car[6][3] = self.car_pos[1] - 100
			# 填入右邊界
			if self.car_lane == 8:
				has_car[2][0] = 1
				has_car[2][1] = 0
				has_car[2][2] = 665
				has_car[2][3] = self.car_pos[1] + 100
				has_car[5][0] = 1
				has_car[5][1] = 0
				has_car[5][2] = 665
				has_car[5][3] = self.car_pos[1]
				has_car[8][0] = 1
				has_car[8][1] = 0
				has_car[8][2] = 665
				has_car[8][3] = self.car_pos[1] - 100
			# 生成當前狀態九宮格 (若格內有車，flag = 1, 並記錄速度及位置)
			for car in scene_info["cars_info"]:
				xx = car["pos"][0] - self.lanes[self.car_lane]
				yy = car["pos"][1] - self.car_pos[1]
				has_car_index = -1
				parallel_y = 85 - (self.car_vel - car["velocity"])*8    # player can run more/less than computer

				if car["id"] == self.player_no:
					continue
				if xx>=-35 and xx<=35 and yy<-80 and yy>-300: #and car["velocity"]<self.car_vel:
						has_car_index = 1 
						if yy > -200:
							has_car_index = 4
				elif yy>=-100 and yy<=parallel_y:
					if car["pos"][0] >= loutter and car["pos"][0] < linside:   #40
						has_car_index = 3
					elif car["pos"][0] >= rinside and car["pos"][0] < routter:
						has_car_index = 5
				elif yy<-100 and yy>-250:    # hmove_time = 40/2 = 20, (15 - 10)*20 = 100 <- min look ahead distance
					if car["pos"][0] >= loutter and car["pos"][0] < linside: #and car["velocity"]<self.car_vel:
						has_car_index = 0
					elif car["pos"][0] >= rinside and car["pos"][0] < routter: #and car["velocity"]<self.car_vel:
						has_car_index = 2
				elif yy>parallel_y and yy<160:
					if car["pos"][0] >= loutter and car["pos"][0] < linside:
						has_car_index = 6
					elif car["pos"][0] >= rinside and car["pos"][0] < routter:
						has_car_index = 8
					elif car["pos"][0] >= linside and car["pos"][0] < rinside:
						has_car_index = 7
				if has_car_index>-1:
					has_car[has_car_index][0] = 1
					has_car[has_car_index][1] = car["velocity"]
					has_car[has_car_index][2] = car["pos"][0]
					has_car[has_car_index][3] = car["pos"][1]

			if self.player_no == 0:
				print(has_car[0][0], has_car[1][0], has_car[2][0])
				print(has_car[3][0], has_car[4][0], has_car[5][0])
				print(has_car[6][0], has_car[7][0], has_car[8][0])
				print("------------------------------------")

			# 正前方有車，判斷要往左或往右移
			if has_car[4][0] or has_car[1][0]:
				# 1. 先檢查車左前及右前方
				# car at 0, 4(1) and 2
				if has_car[0][0] and has_car[2][0]:
					left_d = self.car_pos[1] - has_car[0][3]
					right_d = self.car_pos[1] - has_car[2][3]
					left_t = (self.car_pos[0] - (self.lanes[self.car_lane] - 70)) // 3
					right_t = (self.car_pos[0] - (self.lanes[self.car_lane] + 70)) // 3
					left_d -= (self.car_vel - has_car[0][1]) * left_t
					right_d -= (self.car_vel - has_car[2][1]) * right_t
					if left_d > right_d:
						target_path = self.lanes[self.car_lane - 1]
					else:
						target_path = self.lanes[self.car_lane + 1]
				# car at 0
				elif has_car[0][0]:
					target_path = self.lanes[self.car_lane + 1]
				# car at 2
				elif has_car[2][0]:
					target_path = self.lanes[self.car_lane - 1]
				else:
					################################################# COIN (前方有車，左前及右前沒車)
					if last_path > 310:
						target_path = self.lanes[self.car_lane - 1]
					else:
						target_path = self.lanes[self.car_lane + 1]
				
				# 2. 檢查車子左右，若有車則覆蓋 target_path
				if has_car[3][0] and has_car[5][0]:
					surrounded = 1
					target_path = self.lanes[self.car_lane]
				elif has_car[3][0]:
					target_path = self.lanes[self.car_lane + 1]
				elif has_car[5][0]:
					target_path = self.lanes[self.car_lane - 1]

			# if command == []:
			# 依據 target_path 加入向左移／向右移指令
			if target_path != last_path:
				if target_path - self.car_pos[0] > 2:
					command.append("MOVE_RIGHT")
				elif target_path - self.car_pos[0] < -2:
					command.append("MOVE_LEFT")

			V = self.car_vel
			if surrounded: #and V > has_car[1][0]:
				if has_car[4][0]:
					if has_car[3][1] > has_car[5][1] and has_car[3][1] != 0:
						command = ["BRAKE", "MOVE_LEFT"]
					elif has_car[5][1] > has_car[3][1] and has_car[5][1] != 0:
						command = ["BRAKE", "MOVE_RIGHT"]
					elif has_car[3][1] == 0:
						command = ["BRAKE", "MOVE_RIGHT"]
					elif has_car[5][1] == 0:
						command = ["BRAKE", "MOVE_LEFT"]
					else:
						command = ["BRAKE"]
				elif has_car[1][0]:
					if has_car[3][3] - self.car_pos[1] > 40 - 5 * self.car_vel and has_car[3][1] != 0:
						command = ["SPEED", "MOVE_LEFT"]
					elif has_car[5][3] - self.car_pos[1] > 40 - 5 * self.car_vel and has_car[5][1] != 0:
						command = ["SPEED", "MOVE_RIGHT"]
					else:
						command = ["SPEED"]
				else:
					command = ["SPEED"]
					# elif not has_car[0][0] or not has_car[2][0]:
					# 	command = ["SPEED"]
					# elif has_car[3][1] > has_car[5][1] and has_car[3][1] != 0:
					# 	command = ["BRAKE", "MOVE_LEFT"]
					# elif has_car[5][1] > has_car[3][1] and has_car[5][1] != 0:
					# 	command = ["BRAKE", "MOVE_RIGHT"]
					# elif has_car[3][1] == 0:
					# 	command = ["BRAKE", "MOVE_RIGHT"]
					# elif has_car[5][1] == 0:
					# 	command = ["BRAKE", "MOVE_LEFT"]
					# else:
					# 	command = ["BRAKE"]
			elif target_path - self.car_pos[0] > 2:  # MOVE RIGHT
				if has_car[1][0]:
					auto_brake_time = (V - has_car[1][1])/0.3
					if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
						command.append("BRAKE")
					elif V < has_car[1][1]:
						command.append("SPEED")
				if has_car[4][0]:
					auto_brake_time = (V - has_car[4][1])/0.3
					if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[4][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[4][3]) - 80:
						command.append("BRAKE")
					elif V < has_car[4][1]:
						command.append("SPEED")
				if has_car[2][0]:   
					auto_brake_time = (V - has_car[2][1])/0.3
					if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[2][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[2][3]) - 80:
						command.append("BRAKE")
					elif V < has_car[2][1]:
						command.append("SPEED")
				if not has_car[1][0] and not has_car[2][0] and not has_car[4][0]:
					command.append("SPEED")
			elif target_path - self.car_pos[0] < -2:   #MOVE LEFT
				if has_car[1][0]:
					auto_brake_time = (V - has_car[1][1])/0.3
					if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
						command.append("BRAKE")
					elif V < has_car[1][1]:
						command.append("SPEED")
				if has_car[4][0]:
					auto_brake_time = (V - has_car[4][1])/0.3
					if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[4][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[4][3]) - 80:
						command.append("BRAKE")
					elif V < has_car[4][1]:
						command.append("SPEED")
				if has_car[0][0]:
					auto_brake_time = (V - has_car[0][1])/0.3
					if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[0][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[0][3]) - 80:
						command.append("BRAKE")
					elif V < has_car[0][1]:
						command.append("SPEED")
				if not has_car[1][0] and not has_car[0][0] and not has_car[4][0]:
					command.append("SPEED")
			else:
				if has_car[1][0]:
					auto_brake_time = (V - has_car[1][1])/0.3
					if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
						command.append("BRAKE")
					elif V < has_car[1][1]:
						command.append("SPEED")
				elif has_car[4][0]:
					auto_brake_time = (V - has_car[4][1])/0.3
					if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[4][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[4][3]) - 80:
						command.append("BRAKE")
					elif V < has_car[4][1]:
						command.append("SPEED")
				else:
					command.append("SPEED")

			if len(command) != 0 and command[0] == "BRAKE":
				for i in range(len(command)):
					if command[i] == "SPEED":
						command.remove("SPEED")

			# [ IF GO STRAIGHT FUNC ]

			last_command = ["NONE", "NONE", "NONE"]
			for i in range(len(command)):
				last_command[i] = command[i]

		##################################################################

		if scene_info["status"] != "ALIVE":
			return "RESET"

		return command


	def reset(self):
		global last_path
		global target_path
		global last_command
		self.car_vel = 0
		self.car_pos = (0, 0)
		self.coin_num = 0
		self.computer_cars = []
		self.coins_pos = []
		self.last_coin_num = 0
		self.last_frame = 0
		last_command = ["NONE", "NONE", "NONE"]
		last_path = 0
		target_path = 0
		print("####################### RESET ########################")
		pass
