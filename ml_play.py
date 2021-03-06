"""
The template of the main script of the machine learning process
"""
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
    

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    
    ball_pre_x = 95         # ball's previous x
    ball_pre_y = 395        # ball's previous y
    ball_x = 95
    ball_y = 395
    plat_center = 95        # center of the platform = plat_x + 20
    window_width = 200      # width of the game window
    slope = 1               # slope of ball's move

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
            ball_pre_x = scene_info.ball[0]
            ball_pre_y = scene_info.ball[1]
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            ball_x = scene_info.ball[0]
            ball_y = scene_info.ball[1]
            plat_center = scene_info.platform[0] + 20
            '''if ball_y - ball_pre_y < 0:     # ball is moving up
                if plat_center > 100:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                    print('LEFT')
                elif plat_center < 100:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                    print('RIGHT')
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                    print('NONE')
                else:'''
            if ball_y - ball_pre_y != 0:
                slope = (ball_y - ball_pre_y) / (ball_x - ball_pre_x)
            else:
                slope = 1

            predict_x = ball_x + ((400 - ball_y) / slope)
            if predict_x > 200:
                predict_x = 400 - predict_x     # predict_x = 200 - (predict_x - 200)
            elif predict_x < 0:
                predict_x = -predict_x

            plat_ball_diff = abs(plat_center - predict_x)
            ball_pre_x = ball_x
            ball_pre_y = ball_y

            if plat_ball_diff <= 10:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                print('NONE')
            elif predict_x < plat_center:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                print('LEFT')
            elif predict_x > plat_center:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                print('RIGHT')
