"""
The template of the main script of the machine learning process
"""
'''
import pickle
import numpy as np
import games.arkanoid.communication as comm
from games.arkanoid.communication import ( 
    SceneInfo, GameStatus, PlatformAction
)
import os.path as path


def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    filename = path.join(path.dirname(__file__),"save/clf_KMeans_BallAndDirection.pickle")
    with open(filename, 'rb') as file:
        clf = pickle.load(file)

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    
    s = [95,93]
    def get_direction(ball_x,ball_y,ball_pre_x,ball_pre_y):
        VectorX = ball_x - ball_pre_x
        VectorY = ball_y - ball_pre_y
        if(VectorX>=0 and VectorY>=0):
            return 0
        elif(VectorX>0 and VectorY<0):
            return 1
        elif(VectorX<0 and VectorY>0):
            return 2
        elif(VectorX<0 and VectorY<0):
            return 3
        
        

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
            
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            feature = []
            #feature.append(scene_info.ball[0])      #0 ball_x
            #feature.append(scene_info.ball[1])      #1 ball_y
            ball_x = scene_info.ball[0]
            ball_y = scene_info.ball[1]
            
            feature.append(scene_info.platform[0])  #2 plat_x
            feature.append(ball_x - s[0])       #3 vector_x
            feature.append(ball_y - s[1])       #4 vector_y
            feature.append(get_direction(ball_x,ball_y,s[0],s[1]))  #5 direction
            print(feature[0])
            print(feature[1])
            print(feature[3])
            print(feature[4])
            feature.append((feature[2] / feature[1]))     #6 slope
            feature.append(s[0] + ((400 - s[1])/feature[4]))    #7 predict_ball_x
            
            s = [ball_x, ball_y]
            feature = np.array(feature)
            feature = feature.reshape((-1,6))                
            y = clf.predict(feature)
            
            if y == 0:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                print('NONE')
            elif y == 1:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                print('LEFT')
            elif y == 2:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                print('RIGHT')
'''
            """
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process
    This loop is run in a separate process, and communicates with the game process.
    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False #有沒有發球
    ball_x = 93
    ball_y = 93
    preball_y = 93

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready() #保留

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False


            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            preball_x = ball_x
            if preball_y > ball_y :
                up = True
            else :
                up = False
            preball_y = ball_y
            ball_x = scene_info.ball[0] + 2.5
            if preball_x > ball_x :
                left = True
            else :
                left = False
            ball_y = scene_info.ball[1] + 2.5
            platform_x = scene_info.platform[0] + 20
            if up :
                if platform_x == 95 :
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                elif platform_x > 95 :
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                else :
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            else :
                    if left :
                        if ball_x - (397.5 - ball_y) < 0 :
                            drop_x = -(ball_x - (397.5 - ball_y))
                        else :
                            drop_x = ball_x - (397.5 - ball_y)
                    else :
                        if ball_x + (397.5 - ball_y) > 200 :
                            drop_x = 400 - (ball_x + (397.5 - ball_y))
                        else :
                            drop_x = ball_x + (397.5 - ball_y)
                    if platform_x > drop_x + 3.5 :
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                    elif platform_x < drop_x  - 3.5:
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                    else :
                        comm.send_instruction(scene_info.frame, PlatformAction.NONE)
