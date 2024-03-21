##################################### YOLO v7 for Obstacles #########################################
import MyTest

# This vevrsion is best in Race with Sensors for Obstacle
import AVISEngine2
import cv2
import numpy as np
from simple_pid import PID

import pyautogui

kp = 1.8
ki = 0.2
kd = 0.2
pid = PID(kp, ki, kd, setpoint=1)

Car = AVISEngine2.Car()

Car.connect("127.0.0.1", 25001)

counter = 0
position = 'right'

obstacle = False

REFRENCE_R = 256 - 73
REFRENCE_L = 256 + 56
CURRENT_PXL = 256

error = 0
steer = 0
Debugging = True

if Debugging: frame_saved = 55; from os import system




try:
    while(True):
        Car.setSpeed(200000000000)
        Car.getData()
        sensors = Car.getSensors()

        if steer < 60 and steer > -60:
            Car.setSteering(0)
        
        if counter > 4 :
            ########################################### Az inji shoro mere ... ###########################################
            Car.getData()

            image = Car.getImage()
            frame = image[275:365, :]
            # MyTest.find_Obstacle(frame)
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv_frame = cv2.medianBlur(hsv_frame, 7)
            
            ########################################### Roud ###########################################
            yellow_mask_up = np.array([28,115,154])
            yellow_mask_low = np.array([31,180,255])
            yellow_mask = cv2.inRange(hsv_frame, yellow_mask_up, yellow_mask_low)

            upRoudMask, dnRoudMask  = 0, 190
            lane_contours, _ = cv2.findContours(yellow_mask[upRoudMask:dnRoudMask,:], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            areas = [cv2.contourArea(c) for c in lane_contours]
            sorted_areas = np.argsort(areas)

            try:
                roudSize = dnRoudMask-upRoudMask
                lane_mask = cv2.drawContours(np.zeros((roudSize,512)), lane_contours, sorted_areas[-1], 255, -1)
            except Exception as e:
                if Debugging: print(f"Roud Error =====> {e}")
                pass

            CURRENT_PXL = np.mean(np.where(lane_mask>0), axis=1)[1]
            if np.isnan(CURRENT_PXL): CURRENT_PXL = 256

            upRoudMaskY, dnRoudMaskY  = 25, 65
            YELLOW_PXL = np.mean(np.where(yellow_mask[upRoudMaskY:dnRoudMaskY,:]>0), axis=1)[1]
            if np.isnan(YELLOW_PXL): YELLOW_PXL = 256

            if YELLOW_PXL>256:
                position = 'left'
            else:
                position = 'right'

            ########################################### PID ###########################################
            if position == "right":
                Car.setSensorAngle(13)
                if sensors[2] < 1499:
                    error = (REFRENCE_L - CURRENT_PXL)*(0.7)
                    steer = pid(error)
                    Car.setSteering(int(steer))
                else:
                    error = REFRENCE_R - CURRENT_PXL
                    steer = (pid(error))
                    Car.setSteering(int(steer))

            else:
                Car.setSensorAngle(40)
                if sensors[2] < 1490:
                    error = REFRENCE_L - CURRENT_PXL 
                    steer = (pid(error))
                    Car.setSteering(int(steer))
                elif sensors[2] > 1499:
                    error = (REFRENCE_R - CURRENT_PXL)*(0.17)
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

                cv2.imshow('frame', _frame)

                cv2.imshow('Lane_Mask(Yellow)', lane_mask)

                key = cv2.waitKey(1)

                ########################################### Display Parameters ###########################################

                if sensors[2] < 1499 : 
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
                print(f'=> Position : {position}')
                print("=============================")
                print(f'=> Sensors : {sensors}')

                if key == ord('w'):
                    # گرفتن اسکرین‌شات

                    screenshot = pyautogui.screenshot()

                    # ذخیره‌ی اسکرین‌شات با یک نام فایل
                    # name = (f'./Color/race_frame_{frame_saved}.png', frame)
                    # screenshot.save('screenshot.png')
                    
                    screenshot.save(f'./Color/race_frame_{frame_saved}.png')
                    
                    # cv2.imwrite(f'./Color/race_frame_{frame_saved}.png', frame)
                    frame_saved += 1
        
        counter += 1

except Exception as e:
    if Debugging:
        print(f"While Error => {e}")
    pass

finally:
    Car.stop()
