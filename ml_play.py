# Import the necessary modules and classes
from mlgame.communication import ml as comm
import pickle
import numpy as np
import os 


def ml_loop(side: str):

    with open(os.path.join(os.path.dirname(__file__),'save','model.pickle'), 'rb') as f:
        model = pickle.load(f)

    ball_served = False
    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-10) and scene_info["platform_1P"][0]+20 < (pred+10):
                return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10)and scene_info["platform_2P"][0]+20 < (pred+10):
                if scene_info["platform_2P"][1]+30-scene_info["ball_speed"][1] > scene_info["ball"][1] : #slice
                    return 0
                    #if scene_info["ball"][0] > scene_info["platform_2P"][0]+20 and scene_info["ball_speed"][0] > 0:
                    #    return 1
                    #elif scene_info["ball"][0] > scene_info["platform_2P"][0]+20 and scene_info["ball_speed"][0] < 0:
                    #    return 1
                else :
                    return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left

    def ml_loop_for_1P(): 
        ball_x = 200 - scene_info["ball"][0]
        ball_y = 500 - scene_info["ball"][1]
        block_x = 200 - scene_info["blocker"][0]
        speed_x = -1*scene_info["ball_speed"][0]
        speed_y = -1*scene_info["ball_speed"][1]
        if speed_y > 0 :
            if speed_x > 0:
                direction = 0
            else :
                direction = 1
        else :
            if speed_x > 0:
                direction = 2
            else:
                direction = 3
        X = [ball_x, ball_y, direction, block_x, speed_x, speed_y]
        X = np.array(X).reshape((1,-1))
        pred = 200 - model.predict(X)
        return move_to(player = '1P',pred = pred)
    
    def ml_loop_for_2P():  # as same as 1P
        # print ("blocker : %s, ball : %s"%(scene_info["blocker"],scene_info["ball"]))
        if scene_info["ball_speed"][1] > 0 :
            if scene_info["ball_speed"][0] > 0:
                direction = 0
            else :
                direction = 1
        else :
            if scene_info["ball_speed"][0] > 0:
                direction = 2
            else:
                direction = 3
        X = [scene_info["ball"][0], scene_info["ball"][1], direction, scene_info["blocker"][0],scene_info["ball_speed"][0],scene_info["ball_speed"][1]]
        X = np.array(X).reshape((1,-1))
        pred = model.predict(X)
        return move_to(player = '2P',pred = pred)
    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
            ball_served = True
        else:
            if side == "1P":
                command = ml_loop_for_1P()
            else:
                command = ml_loop_for_2P()

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
