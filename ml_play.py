"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import pickle
import numpy as np
import os.path as path

def ml_loop(side: str):
	"""
	The main loop for the machine learning process

	The `side` parameter can be used for switch the code for either of both sides,
	so you can write the code for both sides in the same script. Such as:
	```python
	if side == "1P":
		ml_loop_for_1P()
	else:
		ml_loop_for_2P()
	```

	@param side The side which this script is executed for. Either "1P" or "2P".
	"""

	# === Here is the execution order of the loop === #

	# 1. Put the initialization code here
	ball_served = False
	blocker_dir = 0	# Blocker's moving direction (0: None, 1: Right, 2: Left)
	pre_blocker = 0

	filename = path.join(path.dirname(__file__),'save','mymodel.pickle')
	with open(filename, 'rb') as file:
		model = pickle.load(file)
	
	
	def ml_loop_for_1P(): 
		ball_x = 200 - scene_info["ball"][0]
		ball_y = 500 - scene_info["ball"][1]
		block_x = 200 - scene_info["blocker"][0]
		speed_x = -1*scene_info["ball_speed"][0]
		speed_y = -1*scene_info["ball_speed"][1]
		if speed_y > 0:
			if speed_x > 0:
				direction = 0
			else:
				direction = 1
		else:
			if speed_x > 0:
				direction = 2
			else:
				direction = 3
		X = [ball_x, ball_y, direction, block_x, speed_x, speed_y]
		X = np.array(X).reshape((1,-1))
		pred = 200 - model.predict(X)
		return move_to(plat_side = '1P',pred = pred)

	def ml_loop_for_2P():  # as same as 1P
		# print ("blocker : %s, ball : %s"%(scene_info["blocker"],scene_info["ball"]))
		if scene_info["ball_speed"][1] > 0:
			if scene_info["ball_speed"][0] > 0:
				direction = 0
			else:
				direction = 1
		else:
			if scene_info["ball_speed"][0] > 0:
				direction = 2
			else:
				direction = 3
		X = [scene_info["ball"][0], scene_info["ball"][1], direction, scene_info["blocker"][0],scene_info["ball_speed"][0],scene_info["ball_speed"][1]]
		X = np.array(X).reshape((1,-1))
		pred = model.predict(X)
		return move_to(plat_side = '2P',pred = pred)

	def move_to(plat_side, pred):
		if plat_side == '1P':
			if scene_info["platform_1P"][0]+20  > (pred-10) and scene_info["platform_1P"][0]+20 < (pred+10):
				# Slicing
				if scene_info["platform_1P"][1] <= scene_info["ball"][1] + scene_info["ball_speed"][1]:
					slicing_dir = slicing_predict(ball_x = scene_info["ball"][0], speed_x = scene_info["ball_speed"][0], speed_y = scene_info["ball_speed"][1])
					print("******Slicing", slicing_dir)
					return slicing_dir
				else:
					'''afterR = scene_info["platform_1P"][0] + 5
					afterL = scene_info["platform_1P"][0] - 5
					if scene_info["platform_1P"][0] < 100 and afterR+30 > pred and afterR+10 < pred:
						return 1
					elif scene_info["platform_1P"][0] > 100 and afterL+30 > pred and afterL+10 < pred:
						return 2
					#print("N")
					else:'''
					return 0    #NONE
			elif scene_info["platform_1P"][0]+20 <= (pred-10):
				#print("R")
				return 1	#RIGHT
			else:
				#print("L")
				return 2	#LEFT
		else:
			if scene_info["platform_2P"][0]+20  > (pred-15)and scene_info["platform_2P"][0]+20 < (pred+10):
				if scene_info["platform_2P"][1]+30-scene_info["ball_speed"][1] > scene_info["ball"][1]:
					if scene_info["ball"][0] > scene_info["platform_2P"][0]+20:
						return 1
					elif scene_info["ball"][0] < scene_info["platform_2P"][0]+20:
						return 2
				else:
					return 0	#NONE
			elif scene_info["platform_2P"][0]+20 <= (pred-10): 
				return 1	#RIGHT
			else: 
				return 2	#LEFT

	def slicing_predict(ball_x, speed_x, speed_y):
		# Positive Slicing
		x = ball_x
		y = 415
		blocker_x = scene_info["blocker"][0]
		blocker_direction = blocker_dir
		speed = speed_x + 3

		while y > 260:
			blocker_x = blocker_x + (blocker_direction * 5)
			if blocker_x>170:
				blocker_x = 170
				blocker_direction *= -1
			elif blocker_x < 0:
				blocker_x = 0
				blocker_direction *= -1

			x += speed
			y -= speed_y
			if x > 195:
				x = 195
				speed *= -1
			elif x < 0:
				x = 0
				speed *= -1
		if blocker_x > x+15 or blocker_x+40 < x:
			if speed_x > 0:
				return 1
			elif speed_x <0:
				return 2
			#print("Slice Positive, ", speed_x/abs(speed_x), " / ", speed_x)

		# Opposite Slicing
		x = ball_x
		y = 415
		blocker_x = scene_info["blocker"][0]
		blocker_direction = blocker_dir
		speed = -speed_x

		while y > 260:
			blocker_x = blocker_x + (blocker_direction * 5)
			if blocker_x>170:
				blocker_x = 170
				blocker_direction *= -1
			elif blocker_x < 0:
				blocker_x = 0
				blocker_direction *= -1

			x += speed
			y -= speed_y
			if x > 195:
				x = 195
				speed *= -1
			elif x < 0:
				x = 0
				speed *= -1
		if blocker_x > x+15 or blocker_x+40 < x:
			if speed_x > 0:
				return 2
			elif speed_x < 0:
				return 1
			#print("Slice Oppositive, ", -(speed_x / abs(speed_x)), " / ", speed_x)
		return 0
		#print("No Slice")

	# 2. Inform the game process that ml process is ready
	comm.ml_ready()

	# 3. Start an endless loop
	while True:
		# 3.1. Receive the scene information sent from the game process
		scene_info = comm.recv_from_game()

		# 3.2. If either of two sides wins the game, do the updating or
		#		resetting stuff and inform the game process when the ml process
		#		is ready.
		if scene_info["status"] != "GAME_ALIVE":
			# Do some updating or resetting stuff
			ball_served = False

			# 3.2.1 Inform the game process that
			#	the ml process is ready for the next round
			comm.ml_ready()
			continue

		# 3.3 Put the code here to handle the scene information

		# 3.4 Send the instruction for this frame to the game process
		if not ball_served:
			comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
			ball_served = True
			pre_blocker = scene_info["blocker"][0]
		else:
			blocker_dir = scene_info["blocker"][0] - pre_blocker
			pre_blocker = scene_info["blocker"][0]

			if side == "1P":
				command = ml_loop_for_1P()
			else:
				command = ml_loop_for_2P()

			if command == 0:
				comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
			elif command == 1:
				comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
			else:
				comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
