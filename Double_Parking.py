import AVISEngine2
import cv2
import numpy as np
import time
from os import system

Car = AVISEngine2.Car()

counter = 0
Debugging = True

try:
    time1 = time.time()
    while(True):
        Car.setSpeed(5)
        Car.getData()
        sensors = Car.getSensors()

        if sensors[1] <= 500:
            time2 = time.time() - time1
            Car.setSpeed(0)
            break
    


except Exception as e:
    if Debugging: print(f"Mane Error => {e}")
    pass