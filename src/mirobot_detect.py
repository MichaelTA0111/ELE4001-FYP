import random
import time
from threading import Thread

import numpy as np
import cv2
from wlkata_mirobot import WlkataMirobot

from config import MIROBOT_PORT, RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from opencv_helper_functions import stack_images, get_contours


x, y, z = 100, 100, 100
roll, pitch, yaw = 0, 0, 0
do_open, do_close = False, False
joints = {1: 45, 2: -30, 3: 50, 4: 0, 5: -25, 6: -45}
run = True


def camera_thread():
    global x, y, z, do_open, do_close, run

    # Set up camera feed
    cap = cv2.VideoCapture(0)
    cap.set(3, RESOLUTION_WIDTH)
    cap.set(4, RESOLUTION_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 5)

    # # Create the trackbar window for HSV values
    # cv2.namedWindow('Trackbars')
    # cv2.resizeWindow('Trackbars', 640, 240)
    # cv2.createTrackbar('Hue Min', 'Trackbars', 100, 179, empty)  # Ranges from 0 to 360 or 0 to 180?
    # cv2.createTrackbar('Hue Max', 'Trackbars', 112, 179, empty)
    # cv2.createTrackbar('Sat Min', 'Trackbars', 114, 255, empty)
    # cv2.createTrackbar('Sat Max', 'Trackbars', 255, 255, empty)
    # cv2.createTrackbar('Val Min', 'Trackbars', 65, 255, empty)
    # cv2.createTrackbar('Val Max', 'Trackbars', 206, 255, empty)

    # Set the HSV values
    blue_hsv_min = np.array([100, 114, 65])
    blue_hsv_max = np.array([112, 255, 206])

    pts1 = np.float32([[370, 274], [994, 236], [182, 708], [1244, 706]])  # Points on original image
    pts2 = np.float32([[0, 0], [RESOLUTION_WIDTH, 0],
                       [0, RESOLUTION_HEIGHT], [RESOLUTION_WIDTH, RESOLUTION_HEIGHT]])  # New output points
    ct_matrix = cv2.getPerspectiveTransform(pts1, pts2)

    while run:
        _, img = cap.read()
        img_warped = cv2.warpPerspective(img, ct_matrix, (RESOLUTION_WIDTH, RESOLUTION_HEIGHT))
        img_hsv = cv2.cvtColor(img_warped, cv2.COLOR_BGR2HSV)

        # hue_min = cv2.getTrackbarPos('Hue Min', 'Trackbars')
        # hue_max = cv2.getTrackbarPos('Hue Max', 'Trackbars')
        # sat_min = cv2.getTrackbarPos('Sat Min', 'Trackbars')
        # sat_max = cv2.getTrackbarPos('Sat Max', 'Trackbars')
        # val_min = cv2.getTrackbarPos('Val Min', 'Trackbars')
        # val_max = cv2.getTrackbarPos('Val Max', 'Trackbars')

        blue_mask = cv2.inRange(img_hsv, blue_hsv_min, blue_hsv_max)
        img_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_mask)
        img_canny = cv2.Canny(img_resultant, 50, 50)
        img_contour = img_warped.copy()

        contours = get_contours(img_canny, img_contour)
        midpoints = [[c[0] + c[2] // 2, c[1] + c[3] // 2] for c in contours]

        img_stack = stack_images(0.5,
                                 [[img_warped, img_hsv, blue_mask], [img_resultant, img_canny, img_contour]])

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
