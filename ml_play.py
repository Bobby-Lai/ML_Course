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
        self.coin_num = 0
        self.last_coin_num = 0
        self.computer_cars = []
        self.coins_pos = []
        self.last_frame = 0

    def update(self, scene_info:dict):
        """
        Generate the command according to the received scene information
        """
        '''self.car_pos = scene_info[self.player]
        for car in scene_info["cars_info"]:
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]
                self.coin_num = car["coin_num"]
        self.computer_cars = scene_info["computer_cars"]
        if scene_info.__contains__("coins"):
            self.coins_pos = scene_info["coins"]'''


        ##################################################################

        global last_path
        global target_path
        global last_command
        has_car = []
        command = []
        surrounded = 0

        if len(scene_info[self.player])!=0:
            if last_path == 0:
                last_path = scene_info[self.player][0]
            if scene_info[self.player][0]==target_path and scene_info[self.player][0]!= last_path:
                last_path = scene_info[self.player][0]

            self.car_pos = scene_info[self.player]

            for car in scene_info["cars_info"]:
                if car["id"]==self.player_no:
                    self.car_vel = car["velocity"]
                    self.coin_num = car["coin_num"]
            self.computer_cars = scene_info["computer_cars"]
            if scene_info.__contains__("coins"):
                self.coins_pos = scene_info["coins"]
            
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
                if has_car[3][0] and has_car[4][0]:
                    surrounded = 1
                    target_path = last_path
                    command.append("MOVE_RIGHT")
                    command.append("MOVE_LEFT")
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
                    if target_path - self.car_pos[0] > 2:
                        if has_car[4][0] and last_path == 35:
                            command.append("BRAKE")
                        else:
                            command.append("MOVE_RIGHT")
                    elif target_path - self.car_pos[0] < -2:
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
                elif target_path == last_path+70:  # MOVE RIGHT
                    if has_car[1][0]:
                        auto_brake_time = (V - has_car[1][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
                            command.append("BRAKE")
                        elif V < has_car[1][1]:
                            command.append("SPEED")
                    if has_car[2][0]:   
                        auto_brake_time = (V - has_car[2][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[2][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[2][3]) - 80:
                            command.append("BRAKE")
                        elif V < has_car[2][1]:
                            command.append("SPEED")  
                    if not has_car[1][0] and not has_car[2][0]:
                        command.append("SPEED")
                elif target_path == last_path-70:   #MOVE LEFT
                    if has_car[1][0]:
                        auto_brake_time = (V - has_car[1][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
                            command.append("BRAKE")
                        elif V < has_car[1][1]:
                            command.append("SPEED")
                    if has_car[0][0]:
                        auto_brake_time = (V - has_car[0][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[0][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[0][3]) - 80:
                            command.append("BRAKE")
                        elif V < has_car[0][1]:
                            command.append("SPEED")
                    if not has_car[1][0] and not has_car[0][0]:
                        command.append("SPEED")
                else:
                    if has_car[1][0]:
                        auto_brake_time = (V - has_car[1][0])/0.3
                        if V*auto_brake_time + (0.5*-0.3*math.pow(auto_brake_time,2)) - has_car[1][1]*auto_brake_time >= abs(self.car_pos[1] - has_car[1][3]) - 80:
                            command.append("BRAKE")
                        elif V < has_car[1][1]:
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



        #print(self.player, " : ", self.car_pos)
        if self.coin_num > self.last_coin_num:
            frame_through = scene_info["frame"] - self.last_frame
            print(self.player, "Frame through : ", frame_through)
            self.last_frame = scene_info["frame"]
            self.last_coin_num = self.coin_num


        ##################################################################

        if scene_info["status"] != "ALIVE":
            return "RESET"

        return command


    def reset(self):
        global last_path
        global target_path
        global last_command
        self.car_vel = 0
        self.car_pos = ()
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
