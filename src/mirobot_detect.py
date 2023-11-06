import random
import time
from threading import Thread

import numpy as np
import cv2
from wlkata_mirobot import WlkataMirobot

from config import MIROBOT_PORT, RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from opencv_helper_functions import stack_images, get_contours


ee_coords = [[0, 0]]
x, y, z = 100, 100, 100
roll, pitch, yaw = 0, 0, 0
do_open, do_close = False, False
joints = {1: 45, 2: -30, 3: 50, 4: 0, 5: -25, 6: -45}
run = True


def camera_thread():
    global ee_coords, x, y, z, do_open, do_close, run

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

        # Only parse the desired end effector coordinates if 2 blocks are found
        if len(midpoints) == 2:
            # Convert the midpoints from the image coordinates to end-effector cartesian coordinates
            # Note the x ordinate from the image refers to the y position of the end effector and vice versa
            ee_coords = [[np.interp(m[1], [166, 606], [0, 250]), np.interp(m[0], [134, 1152], [-250, 250])]
                         for m in midpoints]

            # Account for offset of end-effector position due to the gripper being non-symmetrical
            # Add 10 to x-ordinate, subtract 15 from y-ordinate
            ee_coords = [[coords[0] + 10, coords[1] - 15] for coords in ee_coords]

        img_stack = stack_images(0.5,
                                 [[img_warped, img_hsv, blue_mask], [img_resultant, img_canny, img_contour]])

        cv2.imshow('Image Stack', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            run = False


def arm_thread():
    global ee_coords, do_open, do_close, joints, run

    print('Arm Starting')

    arm = WlkataMirobot(portname=MIROBOT_PORT, debug=False, default_speed=20)
    arm.home()

    while run:
        pass

    if len(ee_coords) == 2:
        print('Successfully found 2 blocks!')

        src = ee_coords[0]
        dst = ee_coords[1]

        print(f'Moving above source block')
        arm.p2p_interpolation(src[0], src[1], 120, 0, 0, 0)
        time.sleep(1)

        print(f'Opening gripper')
        arm.gripper_open()
        time.sleep(1)

        print(f'Moving to source block')
        arm.p2p_interpolation(src[0], src[1], 70, 0, 0, 0)
        time.sleep(1)

        print(f'Picking up source block')
        arm.gripper_close()
        time.sleep(1)

        print(f'Lifting source block')
        arm.p2p_interpolation(src[0], src[1], 120, 0, 0, 0)
        time.sleep(1)

        print(f'Moving above destination block')
        arm.p2p_interpolation(dst[0], dst[1], 120, 0, 0, 0)
        time.sleep(1)

        print(f'Setting on destination block')
        arm.p2p_interpolation(dst[0], dst[1], 95, 0, 0, 0)
        time.sleep(1)

        print(f'Releasing down source block')
        arm.gripper_open()
        time.sleep(1)

        print(f'Moving above destination block')
        arm.p2p_interpolation(dst[0], dst[1], 120, 0, 0, 0)
        time.sleep(1)

        print(f'Closing gripper')
        arm.gripper_close()
        time.sleep(1)

    arm.home()


def main():
    Thread(target=camera_thread).start()
    Thread(target=arm_thread).start()
    print('Both threads started successfully!')


if __name__ == '__main__':
    main()
