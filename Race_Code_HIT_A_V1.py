import AVISEngine2
import cv2
import numpy as np
import time
from os import system
from simple_pid import PID

kp = 3
ki = 0.2
kd = 0.2
pid = PID(kp, ki, kd, setpoint=1)

Car = AVISEngine2.Car()

Car.connect("127.0.0.1", 25001)

counter = 0
position = 'right'

obstacle = False
mean_obstacle = 0

REFRENCE = 128
CURRENT_PXL = 128
SECOND_PXL = 128

time1 = time.time()
error = 0
Debugging = True


try:
    while(True):
        Car.setSpeed(200000000000)
        Car.getData()
        sensors = Car.getSensors()
        
        if error < 65 or error > -65:
            Car.setSteering(0)
        
        if counter > 4 :
            ########################################### Az inji shoro mere ... ###########################################
            Car.getData()

            frame = Car.getImage()
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv_frame = cv2.medianBlur(hsv_frame, 7)

            ########################################### Roud ###########################################

            mask = cv2.inRange(hsv_frame, np.array([90,12,20]), np.array([150,55,55]))
            mask = cv2.medianBlur(mask, 3)

            up_mask, down_mask  = 110, 195
            lane_contours, _ = cv2.findContours(mask[up_mask:down_mask,:], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            areas = [cv2.contourArea(c) for c in lane_contours]
            sorted_areas = np.argsort(areas)
            try:
                right_lane_mask = cv2.drawContours(np.zeros((85,256)), lane_contours, sorted_areas[-1], 255, -1)
                left_lane_mask = cv2.drawContours(np.zeros((85,256)), lane_contours, sorted_areas[-2], 255, -1)
            except Exception as e:
                if Debugging:
                    print(f"Roud Error =====> {e}")
                pass

            CURRENT_PXL = np.mean(np.where(right_lane_mask>0), axis=1)[1]
            SECOND_PXL = np.mean(np.where(left_lane_mask>0), axis=1)[1]            

            if np.isnan(CURRENT_PXL): CURRENT_PXL = 128
            if np.isnan(SECOND_PXL): SECOND_PXL = 128

            yellow_mask = cv2.inRange(hsv_frame, np.array([28,115,154]), np.array([31,180,255]))
            YELLOW_PXL = np.mean(np.where(yellow_mask[140:190,:]>0), axis=1)[1]

            if np.isnan(YELLOW_PXL): YELLOW_PXL = 128

            if YELLOW_PXL>128:
                position = 'left'
            else:
                position = 'right'
            
            ########################################### Obstacle ###########################################


            obstacle_mask = cv2.inRange(hsv_frame[80:180, :], np.array([95,5,70]), np.array([115,38,135]))
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
                if Debugging:
                    print(f"Obstacle Error => {e}")
                pass

            obs_yellow = np.mean(np.where(yellow_mask[75:110,:]>0), axis=1)[1]
            if np.isnan(obs_yellow): obs_yellow = 128

            if mean_obstacle > obs_yellow : 
                obstacle = True
            else:
                obstacle = False

            ########################################### PID ###########################################

            if position == "right":
                if mean_obstacle > obs_yellow :
                    if error <= 3 and error >= -3:
                        error = (REFRENCE - CURRENT_PXL) 
                    else:
                        error = (REFRENCE - SECOND_PXL)*(0.2)
                    steer = pid(error)
                    Car.setSteering(int(steer))
                else:
                    error = REFRENCE - CURRENT_PXL 
                    steer = (pid(error))
                    Car.setSteering(int(steer))

            else:
                if mean_obstacle > obs_yellow:
                    error = REFRENCE - CURRENT_PXL
                    steer = pid(error)
                    Car.setSteering(int(steer))
                elif sensors[2] < 1490:
                    error = REFRENCE - CURRENT_PXL 
                    steer = (pid(error))
                    Car.setSteering(int(steer))
                elif sensors[2] > 1499:
                    error = (REFRENCE - SECOND_PXL)*(0.2)
                    steer = (pid(error))
                    Car.setSteering(int(steer))

            Car.setSpeed(200000000000)

            ########################################### Display Frames ###########################################

            if Debugging:

                cv2.putText(frame, "roud_mask", (0,120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
                frame = cv2.rectangle(frame,(0,up_mask),(256,down_mask),(0,255,0),1)
                cv2.putText(frame, "yellow_mask", (0,150), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
                frame = cv2.rectangle(frame,(0,140),(256,190),(0,0,255),1)
                cv2.putText(frame, "obstacle", (0,40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 2)
                frame = cv2.rectangle(frame,(0,50),(256,150),(255,0,0),1)
                cv2.putText(frame, "yellow_obs", (100,70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 255), 2)
                frame = cv2.rectangle(frame,(10,75),(246,110),(0,255,255),1)

                out = np.concatenate((frame, hsv_frame), axis=1)

                cv2.imshow('frame', frame)

                lane_masks = np.concatenate((left_lane_mask, right_lane_mask), axis=1)
                cv2.imshow('left_Lane_Mask / right_Lane_Mask', lane_masks)
                
                # out1 = np.concatenate((mask[130:200,:], yellow_mask[140:190,:]), axis=1)
                cv2.imshow('yellow_mask', yellow_mask[140:190,:])

                cv2.imshow("obstacle_mask", obstacle_mask)

                new = np.zeros((100,256,3))
                cv2.rectangle(new, (x,y),(x+w,y+h),(0,255,0),2)
                cv2.rectangle(obstacle_mask, (x,y),(x+w,y+h),(0,255,0),2)
                cv2.imshow("Obstacle_founder", new)

                cv2.imshow("Yellow_Obstacle", yellow_mask[75:110,:])
                

                key = cv2.waitKey(1)

                ########################################### Display Parameters ###########################################

                system('cls')
                print(f"Yellow line : {YELLOW_PXL}")
                print(f'Current : {CURRENT_PXL}')
                print(f'Second : {SECOND_PXL}')
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
                    # np.save('masks.npy', hsv_frame)
                    cv2.imwrite(f'./race_frame{counter}.png', hsv_frame)
        
        counter += 1

except Exception as e:
    if Debugging:
        print(f"While Error => {e}")
    pass

finally:
    Car.stop()
