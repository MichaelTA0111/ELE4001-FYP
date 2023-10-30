import random
import time
from threading import Thread

import numpy as np
import cv2
from wlkata_mirobot import WlkataMirobot

from config import MIROBOT_PORT, RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from opencv_helper_functions import empty, stack_images, draw_contours


x, y, z = 100, 100, 100
roll, pitch, yaw = 0, 0, 0
do_open, do_close = False, False
joints = {1: 45, 2: -30, 3: 50, 4: 0, 5: -25, 6: -45}
run = True


def camera_thread():
    global x, y, z, do_open, do_close, run

    cv2.namedWindow('Trackbars')
    cv2.resizeWindow('Trackbars', 640, 240)
    cv2.createTrackbar('Hue Min', 'Trackbars', 0, 179, empty)  # Ranges from 0 to 360 or 0 to 180?
    cv2.createTrackbar('Hue Max', 'Trackbars', 19, 179, empty)
    cv2.createTrackbar('Sat Min', 'Trackbars', 110, 255, empty)
    cv2.createTrackbar('Sat Max', 'Trackbars', 240, 255, empty)
    cv2.createTrackbar('Val Min', 'Trackbars', 153, 255, empty)
    cv2.createTrackbar('Val Max', 'Trackbars', 255, 255, empty)

    cap = cv2.VideoCapture(0)
    cap.set(3, RESOLUTION_WIDTH)
    cap.set(4, RESOLUTION_HEIGHT)

    while run:
        _, img = cap.read()
        # img = cv2.flip(img, 1)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        hue_min = cv2.getTrackbarPos('Hue Min', 'Trackbars')
        hue_max = cv2.getTrackbarPos('Hue Max', 'Trackbars')
        sat_min = cv2.getTrackbarPos('Sat Min', 'Trackbars')
        sat_max = cv2.getTrackbarPos('Sat Max', 'Trackbars')
        val_min = cv2.getTrackbarPos('Val Min', 'Trackbars')
        val_max = cv2.getTrackbarPos('Val Max', 'Trackbars')
        # print(f'{hue_min} {hue_max} {sat_min} {sat_max} {val_min} {val_max}')

        lower = np.array([hue_min, sat_min, val_min])
        upper = np.array([hue_max, sat_max, val_max])
        mask = cv2.inRange(img_hsv, lower, upper)
        img_resultant = cv2.bitwise_and(img, img, mask=mask)
        img_canny = cv2.Canny(img_resultant, 50, 50)
        img_contour = img.copy()

        draw_contours(img_canny, img_contour)

        img_stack = stack_images(0.5, [[img, img_hsv, mask], [img_resultant, img_canny, img_contour]])

        cv2.imshow('Image Stack', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            run = False


def arm_thread():
    global do_open, do_close, joints, run

    print('Arm Starting')

    arm = WlkataMirobot(portname=MIROBOT_PORT, debug=False, default_speed=20)
    arm.home()

    previous_move_time = time.time()

    while run:
        if (current_time := time.time()) - previous_move_time > 30:
            previous_move_time = current_time
            joints[1] = random.randint(-50, 100)
            joints[2] = random.randint(0, 50)
            joints[3] = random.randint(-100, 0)
            joints[4] = random.randint(-180, 180)
            joints[5] = random.randint(-180, 0)
            joints[6] = random.randint(-180, 180)

            print(f'Setting joints to: \n1 {joints[1]}\n2 {joints[2]}\n3 {joints[3]}\n4 {joints[4]}\n5 {joints[5]}\n'
                  f'6 {joints[6]}')
            arm.set_joint_angle(joints)

        if do_open:
            arm.gripper_open()
            do_open = False
            print('Opening Gripper')
        elif do_close:
            arm.gripper_close()
            do_close = False
            print('Closing Gripper')

    arm.home()


def main():
    Thread(target=camera_thread).start()
    Thread(target=arm_thread).start()
    print('Both threads started successfully!')


if __name__ == '__main__':
    main()
