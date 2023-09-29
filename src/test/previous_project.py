# This section imports  relevant libraries such as WlkataMirobot and numpy which are required for the script to execute
import cv2
# from mirobot import Mirobot
import time
import threading
from wlkata_mirobot import WlkataMirobot
from wlkata_mirobot import WlkataMirobotTool
import os
from cvzone.HandTrackingModule import HandDetector

import numpy as np

# This section initializes the video feed capture and  hand detector
width, height = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)
detector = HandDetector(detectionCon=0.8, maxHands=2)
colorR = (255, 255, 255)

# This section initializes the variables which will be called when running the script
threshold1 = 400
threshold2 = width - 400
hands = None
img = None
fingers = None
xvalue = None
zvalue = None
yvalue = None
xvalue2 = None
zvalue2 = None
yvalue2 = None
yvalue3 = None


# This section sets up a thread to receive the co-ordinates of the hand convert them to robot co-ordinates
def camera_thread():
    global xvalue
    global zvalue
    global yvalue
    global fingers
    global xvalue2
    global zvalue2
    global yvalue2
    global yvalue3
    global fingers2
    global orientation
    global orientation1

    while True:
        _, img = cap.read()
        img = cv2.flip(img, 1)

        hands, img = detector.findHands(img)
        # cv2.line(img, (threshold1, 0), (threshold1, height), (0, 255, 0), 10)
        # cv2.line(img, (threshold2, 0), (threshold2, height), (0, 255, 0), 10)

        if hands:
            if len(hands) == 2:
                hand1 = hands[0]
                hand2 = hands[1]
                # This is to force the program to recognize the right hand as hand1 and left hand as hand2
                # however it does not work due to reasons unknown
                hand1["type"] = "Left"
                hand2["type"] = "Right"

                # Setting variable to convert position from first hand to robot co-ordinates
                fingers = detector.fingersUp(hand1)
                cx, cy = hand1['center']
                box = hand1['bbox']
                xvalue = np.interp(cx, [0, 1270], [-160, 300])
                zvalue = np.interp(cy, [0, 720], [300, 40])
                yvalue = np.interp(box[2], [50, 500], [140, 220])
                yvalue3 = np.interp(cy, [0, 720], [220, 140])

                # Setting variable to convert position from second hand to robot co-ordinates
                fingers2 = detector.fingersUp(hand2)
                cx2, cy2 = hand2['center']
                box2 = hand2['bbox']
                xvalue2 = np.interp(cx2, [0, 1270], [-160, 200])
                zvalue2 = np.interp(cy2, [0, 720], [300, 40])
                yvalue2 = np.interp(box2[2], [50, 500], [120, 240])

                # zvalue2 = np.interp(cy2, [0, 720], [300, 40])

        cv2.imshow("image", img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break


# This section sets up a function to control the Mirobot with the converted co-ordinates
def arm_thread():
    arm = WlkataMirobot(portname='COM3')
    arm.home()

    # switch_time = time.time()
    # gripper_open = False

    while True:
        # This sets the arm to the received co-ordinates
        arm.p2p_interpolation(xvalue, yvalue3, zvalue2)

        print('y', yvalue)
        print('z', zvalue)

        # This section sets up a finger detection to detect an arm close or open
        if fingers == [0, 0, 0, 0, 0]:
            arm.gripper_close()

        if fingers == [1, 1, 1, 1, 1]:
            arm.gripper_open()

        # if (time.time() - switch_time) > 10:
        #     if gripper_open:
        #         arm.gripper_close()
        #         print('opening gripper')
        #     else:
        #         arm.gripper_open()
        #         print('closing gripper')
        #     gripper_open = not gripper_open

        key = cv2.waitKey(1)
        if key == ord('q'):
            break


# This section implements multi-threading which allows for the 2 functions to run concurrently
threading.Thread(target=camera_thread).start()
threading.Thread(target=arm_thread).start()
