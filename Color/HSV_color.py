import cv2 as cv
import numpy as np

def nothing(x):
    pass

cv.namedWindow('road',cv.WINDOW_NORMAL)

cv.createTrackbar('kernel','road',1,99,nothing)
cv.createTrackbar('Hue_low','road',0,180,nothing)
cv.createTrackbar('Hue_up','road',180,180,nothing)
cv.createTrackbar('saturation_low','road',0,255,nothing)
cv.createTrackbar('saturation_up','road',255,255,nothing)
cv.createTrackbar('value_low','road',0,255,nothing)
cv.createTrackbar('value_up','road',255,255,nothing)

while(True):
    image =cv.imread('./color/race_frame_3.png')

    kernel = cv.getTrackbarPos('kernel','road')
    if kernel % 2 !=0:
        img_fill = cv.GaussianBlur(image,(kernel,kernel),0,0)
        # img_fill = cv.medianBlur(image, kernel)

    cv.imshow('img_fill',img_fill)
    hsv_img = cv.cvtColor(img_fill, cv.COLOR_BGR2HSV)

    H_low = cv.getTrackbarPos('Hue_low','road')
    H_up = cv.getTrackbarPos('Hue_up','road')
    S_low = cv.getTrackbarPos('saturation_low','road')
    S_up = cv.getTrackbarPos('saturation_up','road')
    V_low = cv.getTrackbarPos('value_low','road')
    V_up = cv.getTrackbarPos('value_up','road')

    color_low = np.array([H_low,S_low,V_low])
    color_up = np.array([H_up,S_up,V_up])

    color_mask =cv.inRange(hsv_img,color_low,color_up)

    bitwise_frame = cv.bitwise_and(image, image , mask= color_mask)
    cv.imshow('road',bitwise_frame)

    # cv.imshow('color_mask',color_mask)

    if cv.waitKey(1) == ord('q'): break

print('H_low: {}, S_low: {}, V_low: {}'.format(H_low,S_low,V_low))
print('H_up: {}, S_up: {}, V_up: {}'.format(H_up,S_up,V_up))