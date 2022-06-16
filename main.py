pid_centralise = PIDCtrl()
pid_dist = PIDCtrl()
marker_list = []

left = 12 # 2
right = 11 # 1
question_mark = 47
heart = 8
stop = 13 # 3
luggage_markers = [14, 15, 16, 17] # 4 5 6 7
first = {14:"left", 15:"left", 16:"right", 17:"right"}
second = {14:"left", 15:"right", 16:"left", 17:"right"}
gripper_status = False
luggage_number = 0

def start():
    robotic_arm_ctrl.recenter()
    global marker_list
    global pid_centralise
    global pid_dist
    global luggage_markers
    global first
    global second
    global luggage_number
    global gripper_status
    vision_ctrl.enable_detection(rm_define.vision_detection_marker)
    ir_distance_sensor_ctrl.enable_measure(1)
    pid_centralise.set_ctrl_params(200, 0, 0)
    pid_dist.set_ctrl_params(5, 0, 0)
    vision_ctrl.set_marker_detection_distance(3)
    chassis_ctrl.set_trans_speed(1)
    gripper_ctrl.open()

    while True:
        chassis_ctrl.set_trans_speed(0)
        marker_list = vision_ctrl.get_marker_detection_info()
        print(marker_list)

        if(len(marker_list) > 2):
            chassis_ctrl.set_trans_speed(1)
            x_coord = marker_list[2]
            h_coord = marker_list[5]
            pid_centralise.set_error(x_coord - 0.5)
            centralise_output = pid_centralise.get_output()
            dist_output = pid_dist.get_output()
            chassis_ctrl.move_with_speed(dist_output, 0, centralise_output)
            chassis_ctrl.set_rotate_speed(180)

            #check if facing luggage
            if (marker_list[1] in luggage_markers and not gripper_status):
                pid_dist.set_error((0.15-h_coord))
                robotic_arm_ctrl.moveto(200, -55)
                if (h_coord >= 0.08):
                    while (ir_distance_sensor_ctrl.get_distance_info(1) > 2):
                        print(ir_distance_sensor_ctrl.get_distance_info(1))
                        continue
                    chassis_ctrl.stop()
                    time.sleep(0.5)
                    robotic_arm_ctrl.moveto(200,-10)
                    time.sleep(1)
                    gripper_ctrl.close()
                    time.sleep(1)
                    gripper_status = True
                    luggage_number = marker_list[1]
                    robotic_arm_ctrl.recenter()
                    time.sleep(0.5)
                    chassis_ctrl.rotate_with_degree(rm_define.anticlockwise,180)
                    time.sleep(1)
            #facing others
            else:
                if (gripper_status):
                    limit = 0.14
                    pid_dist.set_error(0.28-h_coord)
                    fine_tune = 40
                else:
                    limit = 0.27
                    pid_dist.set_error(0.3-h_coord)
                    fine_tune = 20
                if(h_coord > limit):
                    while (ir_distance_sensor_ctrl.get_distance_info(1) > fine_tune):
                        print(ir_distance_sensor_ctrl.get_distance_info(1))
                        continue
                    if marker_list[1] == left:
                        chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
                        time.sleep(0.5)
                    elif marker_list[1] == right:
                        chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)
                        time.sleep(0.5)
                    elif marker_list[1] == question_mark:
                        direction = first[int(luggage_number)]
                        if direction == "left":
                            chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
                        elif direction == "right":
                            chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)
                        time.sleep(1)
                    elif marker_list[1] == heart:
                        direction = second[int(luggage_number)]
                        if direction == "left":
                            chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
                        elif direction == "right":
                            chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)
                        time.sleep(1)
                    elif marker_list[1] == stop:
                        chassis_ctrl.stop()
                        robotic_arm_ctrl.moveto(200,-55)
                        time.sleep(2)
                        gripper_ctrl.open()
                        time.sleep(2)
                        robotic_arm_ctrl.recenter()
                        time.sleep(2)
                        chassis_ctrl.rotate_with_degree(rm_define.anticlockwise,180)
                        time.sleep(1)
                        luggage_number = 0
                        gripper_status = False
        else:
            chassis_ctrl.set_trans_speed(0.4)
            chassis_ctrl.move_with_distance(0,0.4)
