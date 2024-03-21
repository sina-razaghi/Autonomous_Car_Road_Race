# This vevrsion is best in Race with Image Proccesing for Obstacle
import AVISEngine2
import cv2
import numpy as np
from simple_pid.PID import PID

kp = 1.6
ki = 0.3
kd = 0.3
pid = PID(kp, ki, kd, setpoint=1)

Car = AVISEngine2.Car()

Car.connect("127.0.0.1", 25001)

counter = 0
position = 'right'

obstacle = False
mean_obstacle = 0

REFRENCE_R = 256 - 74
REFRENCE_L = 256 + 55
CURRENT_PXL = 256

error = 0
steer = 0
Debugging = True

if Debugging: frame_saved = 53; from os import system

try:
    while(True):
        Car.setSpeed(200000000000)
        Car.getData()
        sensors = Car.getSensors()

        if steer < 70 and steer > -70:
            Car.setSteering(0)
        
        if counter > 4 :
            ########################################### Az inji shoro mere ... ###########################################
            Car.getData()

            image = Car.getImage()
            frame = image[170:350, :]
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv_frame = cv2.medianBlur(hsv_frame, 7)
            
            ########################################### Roud ###########################################
            yellow_mask_up = np.array([28,115,154])
            yellow_mask_low = np.array([31,180,255])
            yellow_mask = cv2.inRange(hsv_frame, yellow_mask_up, yellow_mask_low)

            upRoudMask, dnRoudMask  = 105, 180
            lane_contours, _ = cv2.findContours(yellow_mask[upRoudMask:dnRoudMask,:], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            areas = [cv2.contourArea(c) for c in lane_contours]
            sorted_areas = np.argsort(areas)

            try:
                roudSize = dnRoudMask-upRoudMask
                lane_mask = cv2.drawContours(np.zeros((roudSize,512)), lane_contours, sorted_areas[-1], 255, -1)
            except Exception as e:
                if Debugging: print(f"Roud Error =====> {e}")
                lane_mask = 0
                pass

            CURRENT_PXL = np.mean(np.where(lane_mask>0), axis=1)[1]
            if np.isnan(CURRENT_PXL): CURRENT_PXL = 256

            upRoudMaskY, dnRoudMaskY  = 130, 170
            YELLOW_PXL = np.mean(np.where(yellow_mask[upRoudMaskY:dnRoudMaskY,:]>0), axis=1)[1]
            if np.isnan(YELLOW_PXL): YELLOW_PXL = 256

            if YELLOW_PXL>256:
                position = 'left'
            else:
                position = 'right'
            
            ########################################## Obstacle ###########################################
            # # Race Roud 2
            # upper_race = np.array([57,6,133])
            # lower_race = np.array([116,31,175])
            
            # Race Roud 2
            upper_race = np.array([44,2,95])
            lower_race = np.array([121,35,139])

            # # Race Roud 3
            # upper_race = np.array([74,16,90])
            # lower_race = np.array([114,57,137])

            upObsMask, dnObsMask = 0, 140
            obstacle_mask = cv2.inRange(hsv_frame[upObsMask:dnObsMask, :], upper_race, lower_race)
            obstacle_mask = cv2.medianBlur(obstacle_mask, 5)

            points, _ = cv2.findContours(obstacle_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            sorted_points = sorted(points, key=len)

            try:
                if cv2.contourArea(sorted_points[-1])>1150:
                    x,y,w,h = cv2.boundingRect(sorted_points[-1])
                    mean_obstacle = x + (w/2)
                else:
                    mean_obstacle = 0
                    x,y,w,h = 0,0,0,0

            except Exception as e:
                if Debugging: print(f"Obstacle Error => {e}")
                pass

            upObsMaskY, dnObsMaskY = 25, 60
            obs_yellow = np.mean(np.where(yellow_mask[upObsMaskY:dnObsMaskY, :]>0), axis=1)[1]
            if np.isnan(obs_yellow): obs_yellow = 256

            ########################################### PID ###########################################
            if position == "right":
                Car.setSensorAngle(12)
                if mean_obstacle > obs_yellow or sensors[2] < 1499:
                    error = (REFRENCE_L - CURRENT_PXL)*(0.10)
                    steer = pid(error)
                    Car.setSteering(int(steer))
                else:
                    error = REFRENCE_R - CURRENT_PXL
                    steer = (pid(error))
                    Car.setSteering(int(steer))

            else:
                Car.setSensorAngle(40)
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
                cv2.putText(_frame, "roud_mask", (0,upRoudMask-10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
                _frame = cv2.rectangle(_frame,(12,upRoudMask),(500,dnRoudMask),(0,255,0),1)
                cv2.putText(_frame, "yellow_mask", (200,upRoudMaskY-8), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
                _frame = cv2.rectangle(_frame,(0,upRoudMaskY),(512,dnRoudMaskY),(0,0,255),1)
                cv2.putText(_frame, "obstacle", (0,upObsMask+15), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 2)
                _frame = cv2.rectangle(_frame,(1,upObsMask),(511,dnObsMask),(255,0,0),1)
                cv2.putText(_frame, "yellow_obs", (200,upObsMaskY-10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 255), 2)
                _frame = cv2.rectangle(_frame,(10*2,upObsMaskY),(246*2,dnObsMaskY),(0,255,255),1)

                cv2.imshow('frame', _frame)

                cv2.imshow('Lane_Mask(Yellow)', lane_mask)

                new = np.zeros((dnObsMask-upObsMask,512))
                cv2.rectangle(new, (x,y),(x+w,y+h),255,2)
                cv2.rectangle(obstacle_mask, (x,y),(x+w,y+h),(0,255,0),2)

                Obstacle = np.concatenate((obstacle_mask, new), axis=0)
                All_Obstacle = np.concatenate((Obstacle,yellow_mask[upObsMaskY:dnObsMaskY, :]), axis=0)
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
                print(f'=> Position : {position}')
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
