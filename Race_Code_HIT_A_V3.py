import AVISEngine2
import cv2
import numpy as np
from simple_pid import PID

kp = 2
ki = 0.2
kd = 0.2
pid = PID(kp, ki, kd, setpoint=1)

Car = AVISEngine2.Car()

Car.connect("127.0.0.1", 25001)

counter = 0
position = 'right'

obstacle = False
mean_obstacle = 0

REFRENCE_R = 128 - 48
REFRENCE_L = 128 + 30
CURRENT_PXL = 128

error = 0
steer = 0
Debugging = True

if Debugging: frame_saved = 0; from os import system

try:
    while(True):
        Car.setSpeed(200000000000)
        Car.getData()
        sensors = Car.getSensors()

        if steer < 55 and steer > -65:
            Car.setSteering(0)
        
        if counter > 4 :
            ########################################### Az inji shoro mere ... ###########################################
            Car.getData()

            frame = Car.getImage()
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv_frame = cv2.medianBlur(hsv_frame, 7)

            ########################################### Roud ###########################################
            yellow_mask_up = np.array([28,115,154])
            yellow_mask_low = np.array([31,180,255])
            yellow_mask = cv2.inRange(hsv_frame, yellow_mask_up, yellow_mask_low)

            up_roud_mask, down__roud_mask  = 110, 190
            lane_contours, _ = cv2.findContours(yellow_mask[up_roud_mask:down__roud_mask,:], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            areas = [cv2.contourArea(c) for c in lane_contours]
            sorted_areas = np.argsort(areas)

            try:
                lane_mask = cv2.drawContours(np.zeros((80,256)), lane_contours, sorted_areas[-1], 255, -1)

            except Exception as e:
                if Debugging: print(f"Roud Error =====> {e}")
                pass

            CURRENT_PXL = np.mean(np.where(lane_mask>0), axis=1)[1]
            if np.isnan(CURRENT_PXL): CURRENT_PXL = 128

            YELLOW_PXL = np.mean(np.where(yellow_mask[140:190,:]>0), axis=1)[1]
            if np.isnan(YELLOW_PXL): YELLOW_PXL = 128

            if YELLOW_PXL>128:
                position = 'left'
            else:
                position = 'right'
            
            ########################################### Obstacle ###########################################
            upper_race_2 = np.array([95,5,70])
            lower_race_2 = np.array([115,38,135])
            obstacle_mask = cv2.inRange(hsv_frame[80:180, :], upper_race_2, lower_race_2)
            obstacle_mask = cv2.medianBlur(obstacle_mask, 3)

            points, _ = cv2.findContours(obstacle_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            sorted_points = sorted(points, key=len)

            try:
                if cv2.contourArea(sorted_points[-1])>264:
                    x,y,w,h = cv2.boundingRect(sorted_points[-1])
                    mean_obstacle = x + (w/2)
                else:
                    mean_obstacle = 0
                    x,y,w,h = 0,0,0,0

            except Exception as e:
                if Debugging: print(f"Obstacle Error => {e}")
                pass

            obs_yellow = np.mean(np.where(yellow_mask[75:110,:]>0), axis=1)[1]
            if np.isnan(obs_yellow): obs_yellow = 128

            ########################################### PID ###########################################
            if position == "right":
                if mean_obstacle > obs_yellow :
                    error = (REFRENCE_L - CURRENT_PXL)*(0.10)
                    steer = pid(error)
                    Car.setSteering(int(steer))
                else:
                    error = REFRENCE_R - CURRENT_PXL
                    steer = (pid(error))
                    Car.setSteering(int(steer))

            else:
                if mean_obstacle > obs_yellow:
                    error = REFRENCE_L - CURRENT_PXL
                    steer = pid(error)
                    Car.setSteering(int(steer))
                elif sensors[2] < 1490:
                    error = REFRENCE_L - CURRENT_PXL 
                    steer = (pid(error))
                    Car.setSteering(int(steer))
                elif sensors[2] > 1499:
                    error = (REFRENCE_R - CURRENT_PXL)*(0.10)
                    steer = (pid(error))
                    Car.setSteering(int(steer))

            Car.setSpeed(200000000000)

            ########################################### Display Frames ###########################################

            if Debugging:

                _frame = np.copy(frame)
                cv2.putText(_frame, "roud_mask", (0,120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
                _frame = cv2.rectangle(_frame,(0,up_roud_mask),(256,down__roud_mask),(0,255,0),1)
                cv2.putText(_frame, "yellow_mask", (0,150), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
                _frame = cv2.rectangle(_frame,(0,140),(256,190),(0,0,255),1)
                cv2.putText(_frame, "obstacle", (0,40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 2)
                _frame = cv2.rectangle(_frame,(0,50),(256,150),(255,0,0),1)
                cv2.putText(_frame, "yellow_obs", (100,70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 255), 2)
                _frame = cv2.rectangle(_frame,(10,75),(246,110),(0,255,255),1)

                cv2.imshow('frame', _frame)

                cv2.imshow('Lane_Mask(Yellow)', lane_mask)

                new = np.zeros((100,256))
                cv2.rectangle(new, (x,y),(x+w,y+h),255,2)
                cv2.rectangle(obstacle_mask, (x,y),(x+w,y+h),(0,255,0),2)

                Obstacle = np.concatenate((obstacle_mask, new), axis=0)
                All_Obstacle = np.concatenate((Obstacle,yellow_mask[75:110,:]), axis=0)
                cv2.imshow("Obstacle_founder", All_Obstacle)

                key = cv2.waitKey(1)

                ########################################### Display Parameters ###########################################

                if mean_obstacle > obs_yellow : 
                    obstacle = True
                else:
                    obstacle = False

                system('cls')
                print(f"Yellow line : {YELLOW_PXL}")
                print(f'Current : {CURRENT_PXL}')
                print(f'Error : {error}')
                print(f'=> Steer : {steer}')
                print("=============================")
                print(f'Obstacle : {obstacle}')
                print(f'Mean_Obstacle : {mean_obstacle}')
                print(f'Obstacle_yellow : {obs_yellow}')
                print(f'=> Position : {position}')
                print("=============================")
                print(f'=> Sensors : {sensors}')

                if key == ord('w'):
                    cv2.imwrite(f'./Color/race_frame_{frame_saved}.png', frame)
                    frame_saved += 1
        
        counter += 1

except Exception as e:
    if Debugging:
        print(f"While Error => {e}")
    pass

finally:
    Car.stop()
