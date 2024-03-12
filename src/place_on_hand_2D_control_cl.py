import time
from threading import Thread

import numpy as np
import cv2
from wlkata_mirobot import WlkataMirobot

from config import MIROBOT_PORT, RES_HEIGHT, RES_WIDTH
from opencv_helper_functions import ContourSize, stack_images, get_contours
from pykinect_helper_functions import initialise_camera, read_camera
from coordinate_systems_cl import ObjectType, ObjectCoordinates


coords = ObjectCoordinates()
run = True
x_error = None
y_error = None
start_time = None


def camera_thread():
    global coords, run, x_error, y_error, start_time

    camera = initialise_camera()

    # Set the HSV values
    blue_dot_hsv_min = np.array([107, 49, 93])
    blue_dot_hsv_max = np.array([124, 240, 198])
    orange_ee_hsv_min = np.array([2, 185, 73])
    orange_ee_hsv_max = np.array([27, 255, 255])
    blue_block_hsv_min = np.array([100, 94, 71])
    blue_block_hsv_max = np.array([116, 240, 158])

    pts1 = np.float32([[292, 172], [976, 172], [162, 652], [1086, 664]])  # Points on original image
    pts2 = np.float32([[0, 0], [RES_WIDTH, 0], [0, RES_HEIGHT], [RES_WIDTH, RES_HEIGHT]])  # New output points
    ct_matrix = cv2.getPerspectiveTransform(pts1, pts2)

    kernel_dilate = np.ones((5, 5), np.uint8)
    kernel_erode = np.ones((3, 3), np.uint8)

    waiting = True
    start_time = time.time()

    while run:
        img, _ = read_camera(camera)

        if isinstance(img, bool):
            continue

        img_warped = cv2.warpPerspective(img, ct_matrix, (RES_WIDTH, RES_HEIGHT))
        img_hsv = cv2.cvtColor(img_warped, cv2.COLOR_BGR2HSV)

        blue_dot_mask = cv2.inRange(img_hsv, blue_dot_hsv_min, blue_dot_hsv_max)
        img_dot_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_dot_mask)
        img_dot_canny = cv2.Canny(img_dot_resultant, 50, 50)

        # Apply dilation and erosion to Canny image
        img_dot_canny_dilated = cv2.dilate(img_dot_canny, kernel_dilate, iterations=1)
        img_dot_canny_eroded = cv2.erode(img_dot_canny_dilated, kernel_erode, iterations=1)

        orange_ee_mask = cv2.inRange(img_hsv, orange_ee_hsv_min, orange_ee_hsv_max)
        img_ee_resultant = cv2.bitwise_and(img_warped, img_warped, mask=orange_ee_mask)
        img_ee_canny = cv2.Canny(img_ee_resultant, 50, 50)

        # Apply dilation and erosion to Canny image
        img_ee_canny_dilated = cv2.dilate(img_ee_canny, kernel_dilate, iterations=1)
        img_ee_canny_eroded = cv2.erode(img_ee_canny_dilated, kernel_erode, iterations=1)

        blue_block_mask = cv2.inRange(img_hsv, blue_block_hsv_min, blue_block_hsv_max)
        img_block_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_block_mask)
        img_block_canny = cv2.Canny(img_block_resultant, 50, 50)

        # Apply dilation and erosion to Canny image
        img_block_canny_dilated = cv2.dilate(img_block_canny, kernel_dilate, iterations=1)
        img_block_canny_eroded = cv2.erode(img_block_canny_dilated, kernel_erode, iterations=1)

        img_contour = img_warped.copy()

        # Only parse the end effector dot position if 1 dot is found
        if ((dots := get_contours(img_dot_canny_eroded, img_contour, size=ContourSize.SMALL)) and
                (ee := get_contours(img_ee_canny_eroded, img_contour, size=ContourSize.LARGE)) and len(ee) == 1):
            ee = ee[0]
            for dot in dots:
                dot_x = dot[0] + dot[2] // 2
                dot_y = dot[1] + dot[3] // 2
                ee_x = [ee[0], ee[0] + ee[2]]
                ee_y = [ee[1], ee[1] + ee[3]]

                if ee_x[0] < dot_x < ee_x[1] and ee_y[0] < dot_y < ee_y[1]:
                    coords.ee.update(dot_x, dot_y)
                    # print(f'EE dot found at {coords.ee.img}')
                    break

        # Only parse the block coordinates if 1 block is found
        if (contours := get_contours(img_block_canny_eroded, img_contour)) and len(contours) == 1:
            contour = contours[0]
            block_x = contour[0] + contour[2] // 2
            block_y = contour[1] + contour[3] // 2
            coords.block.update(block_x, block_y)
            # print(f'Block found at {coords.block.img}')

        # img_stack = stack_images(0.5,
        #                          [[img_warped, img_hsv, orange_ee_mask],
        #                           [img_ee_resultant, img_ee_canny_eroded, img_contour]])
        #
        # cv2.imshow('Image Stack', img_stack)
        cv2.imshow('Image Stack', img_contour)

        key = cv2.waitKey(1)
        if key == ord('q'):
            waiting = False

        if not waiting:
            end_time = time.time()
            if end_time - start_time > 10:
                x_error = coords.calculate_x_error()
                y_error = coords.calculate_y_error()


def arm_thread():
    global coords, run, x_error, y_error, start_time

    print('Arm Starting')

    arm = WlkataMirobot(portname=MIROBOT_PORT, debug=False, default_speed=20)
    # arm.gripper_close()
    arm.home()

    # Wait until the camera thread is stopped
    while run:
        if x_error is None or y_error is None:
            continue

        print(f'{x_error = } px')
        print(f'{y_error = } px')

        arm_status = arm.get_status()
        arm_coords = arm_status.cartesian
        arm_x = arm_coords.x
        arm_y = arm_coords.y
        arm_z = arm_coords.z

        robot_x = coords.calculate_robot_x(arm_x, x_error)
        robot_y = coords.calculate_robot_y(arm_y, y_error)

        print(f'Moving above source block')
        arm.p2p_interpolation(robot_x, robot_y, arm_z, 0, 0, 0)

        if abs(x_error) < 2 and abs(y_error) < 2:
            print('Successfully reached target! Program terminating')
            run = False

        x_error = None
        y_error = None
        coords.ee.reset()
        start_time = time.time()

    arm.home()


def main():
    Thread(target=camera_thread).start()
    Thread(target=arm_thread).start()
    print('Both threads started successfully!')


if __name__ == '__main__':
    main()
