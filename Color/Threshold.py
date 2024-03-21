import cv2
import numpy as np

def nothing(x):
    pass

cv2.namedWindow('road',cv2.WINDOW_NORMAL)

cv2.createTrackbar('kernel','road',1,99,nothing)
cv2.createTrackbar('thresh1','road',0,255,nothing)
cv2.createTrackbar('thresh2','road',255,255,nothing)

while(True):
    image =cv2.imread('./Color/race_frame_3.png')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) 

    kernel = cv2.getTrackbarPos('kernel','road')
    if kernel % 2 !=0:
        img_fill = cv2.GaussianBlur(image,(kernel,kernel),0,0)
        # img_fill = cv.medianBlur(image, kernel)

    cv2.imshow('img_fill',img_fill)

    thr1 = int(cv2.getTrackbarPos('thresh1','road'))
    thr2 = int(cv2.getTrackbarPos('thresh2','road'))

    ret, thresh1 = cv2.threshold(image, thr1, 255, cv2.THRESH_BINARY) 

    cv2.imshow('thresh1', thresh1)

    if cv2.waitKey(1) == ord('q'): break