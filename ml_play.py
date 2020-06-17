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
        self.car_pos = ()
        self.speedup = 1
        pass

    def update(self, scene_info):
        """
        Generate the command according to the received scene information
        """
        global last_path
        global target_path
        global last_command
        has_car = []
        command = []
        surrounded = 0

        if len(scene_info[self.player])!=0:
            if last_path == 0:
                last_path = scene_info[self.player][0]
                #print("initial path = ", last_path)
            if scene_info[self.player][0]==target_path and scene_info[self.player][0]!= last_path:
                last_path = scene_info[self.player][0]
                print("No.", self.player_no+1," last_path updated = ",last_path)

            self.car_pos = scene_info[self.player]

            for car in scene_info["cars_info"]:
                if car["id"]==self.player_no:
                    self.car_vel = car["velocity"]
                    #print(self.car_vel)
            
            for i in range(8):
                new = []
                for j in range(4):
                    new.append(0)
                has_car.append(new)

            rlimit = 105
            llimit = -105
            if last_command[0] == "MOVE_RIGHT":
                rlimit = 70
            elif last_command[0] == "MOVE_LEFT":
                llimit = -70
            '''if len(last_command)>0:
                if last_command[0] == "MOVE_RIGHT":
                    rlimit = 70
                elif last_command[0] == "MOVE_LEFT":
                    llimit = -70'''
            
            for car in scene_info["cars_info"]:
                xx = car["pos"][0] - self.car_pos[0]
                yy = car["pos"][1] - self.car_pos[1]
                has_car_index = -1
                parallel_y = 85 - (self.car_vel - car["velocity"])*8    # player can run more/less than computer

                if xx>=-35 and xx<=35 and yy<-80 and yy>-240 and car["velocity"]<self.car_vel:
                        has_car_index = 1 
                elif yy>=-120 and yy<=parallel_y:
                    if xx<-35 and xx>=llimit:   #40
                        has_car_index = 3
                    elif xx>35 and xx<=rlimit:
                        has_car_index = 4
                elif yy<-120 and yy>-220:    # hmove_time = 40/2 = 20, (15 - 10)*20 = 100 <- min look ahead distance
                    if xx<-35 and xx>=llimit and car["velocity"]<self.car_vel:
                        has_car_index = 0
                    elif xx>35 and xx<=rlimit and car["velocity"]<self.car_vel:
                        has_car_index = 2
                elif yy>parallel_y and yy<160:
                    if xx<-35 and xx>=llimit:
                        has_car_index = 5
                    elif xx>35 and xx<=rlimit:
                        has_car_index = 7
                    elif xx>=-35 and xx<=35:
                        has_car_index = 6
                if has_car_index>-1:
                    has_car[has_car_index][0] = 1
                    has_car[has_car_index][1] = car["velocity"]
                    has_car[has_car_index][2] = car["pos"][0]
                    has_car[has_car_index][3] = car["pos"][1]
                    print("**No.", self.player_no+1,"HAS CAR", car["id"], "AT",has_car_index,"**(frame ",scene_info["frame"], ")")
                '''if self.car_pos[0]>580:
                    has_car[4][0] = 1
                    has_car[4][1] = self.car_vel
                    has_car[4][2] = 665
                    has_car[4][3] = self.car_pos[1]
                elif self.car_pos[0]<50:
                    has_car[3][0] = 1
                    has_car[3][1] = self.car_vel
                    has_car[3][2] = -35
                    has_car[3][3] = self.car_pos[1]'''

            # Decide to move right or left
            if has_car[1][0]:
                # car at 0 and 2
                if has_car[0][0] and has_car[2][0]:
                    # player is on a track
                    if (self.car_pos[0]-35)%70==0:
                        if has_car[0][1] > has_car[2][1]:
                            target_path = last_path-70
                        else:
                            target_path = last_path+70
                    else:
                        command = last_command
                # car at 0
                elif has_car[0][0]:
                    target_path = last_path + 70
                # car at 2
                elif has_car[2][0]:
                    target_path = last_path - 70
                else:
                    if last_path > 315:
                        target_path = last_path - 70
                    else:
                        target_path = last_path + 70
                
                # no car at 0 or 2
                '''elif last_command[0] == "MOVE_RIGHT":
                    if last_command[1] == "MOVE_LEFT":
                        target_path = last_path
                    else:
                        target_path = last_path + 70
                elif last_command[0] == "MOVE_LEFT":
                    target_path = last_path - 70'''
                
                if has_car[3][0] and has_car[4][0]:
                    surrounded = 1
                    target_path = last_path
                    command.append("MOVE_RIGHT")
                    command.append("MOVE_LEFT")
                    print("No.", self.player_no+1, " IS SURROUNDED!!!!!!!")
                elif has_car[3][0]:
                    if last_command[0] == "MOVE_RIGHT" and last_command[1] == "MOVE_LEFT":
                        target_path = last_path
                    else:
                        target_path = last_path + 70
                elif has_car[4][0]:
                    if last_command[0] == "MOVE_RIGHT" and last_command[1] == "MOVE_LEFT":
                        target_path = last_path
                    else:
                        target_path = last_path - 70
                if last_path == 35:
                    target_path = last_path + 70
                elif last_path == 595:
                    target_path = last_path - 70


            if command == []:
                if target_path != 0:
                    if target_path > self.car_pos[0]:
                        if has_car[4][0] and last_path == 35:
                            command.append("BRAKE")
                        else:
                            command.append("MOVE_RIGHT")
                    elif target_path < self.car_pos[0]:
                        if has_car[3][0] and last_path == 595:
                            command.append("BRAKE")
                        else:
                            command.append("MOVE_LEFT")

                V = self.car_vel
                if surrounded: #and V > has_car[1][0]:
                    d = abs(has_car[1][3] - self.pos[1]) - 80
                    a = 0.3
                    auto_brake_time = (V - has_car[1][0])/0.3
                    to_pass = 3     # pass 3
                    pass_y = [0, 0, 0, 0, 0]
                    pass_y[3] = 80 + self.car_pos[1]- has_car[3][3] - (self.car_vel - has_car[3][1])*8    # player can run more/less than computer
                    pass_y[4] = 80 + self.car_pos[1]- has_car[4][3] - (self.car_vel - has_car[4][1])*8    # player can run more/less than computer
                    if pass_y[3]/(15 - has_car[3][1]) > pass_y[4]/(15 - has_car[4][1]):
                        to_pass = 4  # pass 4
                    inter_pass_speed = math.sqrt(math.pow(has_car[to_pass][1], 2) + 2*a*pass_y[to_pass])
                    if inter_pass_speed > 15:
                        inter_pass_speed = 15
                    t_speedtomax = (15 - inter_pass_speed) / 0.3

                    if self.car_vel == 15:  # already speed up to max-speed
                        a = 0
                    
                    if d >= pass_y[to_pass] + inter_pass_speed*t_speedtomax + 0.5*a*math.pow(t_speedtomax, 2) + (15 - inter_pass_speed)*(20 - t_speedtomax):
                        if to_pass == 3:
                            command = ("MOVE_LEFT")                               
                        elif to_pass == 4:
                            command = ("MOVE_RIGHT")
                        command.append("SPEED")
                    # will collide even auto-brake
                    elif V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
                        command.append("BRAKE")
                        print("#No.", self.player_no+1," BRAKE : surrounded")
                elif target_path == last_path+70:  # MOVE RIGHT
                    if has_car[1][0]:
                        auto_brake_time = (V - has_car[1][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
                            command.append("BRAKE")
                            print("#No.", self.player_no+1," BRAKE : MOVE_RIGHT1")
                        elif V < has_car[1][1]:
                            command.append("SPEED")
                    if has_car[2][0]:   
                        auto_brake_time = (V - has_car[2][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[2][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[2][3]) - 80:
                            command.append("BRAKE")
                            print("#No.", self.player_no+1," BRAKE : MOVE_RIGHT2")  
                        elif V < has_car[2][1]:
                            command.append("SPEED")  
                    if not has_car[1][0] and not has_car[2][0]:
                        command.append("SPEED")
                elif target_path == last_path-70:   #MOVE LEFT
                    if has_car[1][0]:
                        auto_brake_time = (V - has_car[1][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
                            command.append("BRAKE")
                            print("#No.", self.player_no+1," BRAKE : MOVE_LEFT1")
                        elif V < has_car[1][1]:
                            command.append("SPEED")
                    if has_car[0][0]:
                        auto_brake_time = (V - has_car[0][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[0][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[0][3]) - 80:
                            command.append("BRAKE")
                            print("#No.", self.player_no+1," BRAKE : MOVE_LEFT0")
                        elif V < has_car[0][1]:
                            command.append("SPEED")
                    if not has_car[1][0] and not has_car[0][0]:
                        command.append("SPEED")
                else:
                    if has_car[1][0]:
                        auto_brake_time = (V - has_car[1][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
                            command.append("BRAKE")
                            print("#No.", self.player_no+1," BRAKE : straight")
                        elif V < has_car[1][1]:
                            command.append("SPEED")
                    else:
                        command.append("SPEED")

            if scene_info["status"] != "ALIVE":
                return "RESET"

            if len(command) != 0 and command[0] == "BRAKE":
                for i in range(len(command)):
                    if command[i] == "SPEED":
                        command.remove("SPEED")

            # [ IF GO STRAIGHT FUNC ]

            last_command = ["NONE", "NONE", "NONE"]
            for i in range(len(command)):
                last_command[i] = command[i]

            print("No.", self.player_no+1," Command : ", command)
            return command


    def reset(self):
        """
        Reset the status
        """
        pass


'''
            # IF player is going straight
            if len(command) == 1 and command[0] == "SPEED":
                if has_car[0][0] or has_car[1][0] or has_car[2][0]:
                    pass
                else: 
                    print("++++++++++ PLUS PLUS +++++++++++")
                    if self.car_pos[0] == 35 and not has_car[4][0]:
                        command = ["MOVE_RIGHT", "SPEED"]
                    elif self.car_pos[0] == 595 and not has_car[3][0]:
                        command = ["MOVE_LEFT", "SPEED"]
                    else:
                        for car in scene_info["cars_info"]:
                            xx = car["pos"][0] - last_path
                            yy = car["pos"][1] - self.car_pos[1]
                            has_car_index = -1

                            if car["pos"][1] < self.car_pos[1]:
                                if xx>=-35 and xx<=35:
                                        has_car_index = 1 
                                elif xx<-35 and xx>=-70 and car["velocity"]<self.car_vel:
                                        has_car_index = 0
                                elif xx>35 and xx<=70 and car["velocity"]<self.car_vel:
                                        has_car_index = 2
                            if has_car_index>-1:
                                has_car[has_car_index][0] = 1
                                if car["pos"][1] > has_car[has_car_index][3]:
                                    has_car[has_car_index][1] = car["velocity"]
                                    has_car[has_car_index][2] = car["pos"][0]
                                    has_car[has_car_index][3] = car["pos"][1]

                        if has_car[1][0] and has_car[0][0] and not has_car[2][0] and not has_car[4][0]:
                            command = ["MOVE_RIGHT", "SPEED"]
                        elif has_car[1][0] and has_car[2][0] and not has_car[0][0] and not has_car[3][0]:
                            command = ["MOVE_LEFT", "SPEED"]
                        elif has_car[1][0] and has_car[0][0] and has_car[2][0]:
                            if has_car[3][0]:
                                command = ["MOVE_RIGHT", "SPEED"]
                            elif has_car[4][0]:
                                command = ["MOVE_LEFT", "SPEED"]
                            elif has_car[0][3] > has_car[2][3]:     # 0 is closer
                                command = ["MOVE_RIGHT", "SPEED"]
                            elif has_car[0][3] < has_car[2][3]:
                                command = ["MOVE_LEFT", "SPEED"]
                        elif has_car[1][0] and not has_car[0][0] and not has_car[2][0]:
                            track_carnum = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                            for car in scene_info["cars_info"]:
                                if car["pos"][1] < self.car_pos[1]:
                                    track_carnum[int((last_path - 35) / 70)] += 1
                            for i in range(2, 6):
                                rtrack = last_path + 70*i
                                ltrack = last_path - 70*i
                                if rtrack > 595:
                                    rtrack = 595
                                elif ltrack < 35:
                                    ltrack = 35
                                if track_carnum[int((ltrack-35) / 70)] > track_carnum[int((rtrack-35) / 70)]:
                                    command = ["MOVE_RIGHT", "SPEED"]
                                    break
                                elif track_carnum[int((rtrack-35) / 70)] > track_carnum[int((ltrack-35) / 70)]:
                                    command = ["MOVE_LEFT", "SPEED"]
                                    break'''
