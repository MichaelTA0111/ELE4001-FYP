import time
from threading import Thread

import numpy as np
import cv2
from wlkata_mirobot import WlkataMirobot
from cvzone.HandTrackingModule import HandDetector

from config import MIROBOT_PORT, RES_HEIGHT, RES_WIDTH
from opencv_helper_functions import ContourSize, stack_images, get_contours
from pykinect_helper_functions import initialise_camera, read_camera


block_coords = []
hand_coords = []
y_error_mm = 0
run = True
waiting = True
detector = HandDetector(detectionCon=0.8, maxHands=1)


def map_coords(img_coords):
    """
    Convert image coordinates to end-effector coordinates
    :param img_coords: List of x and y coordinates from the image
    :return: List of x and y coordinates for the robot end-effector
    """
    # Note the x and y ordinates from the image map to the y and x ordinates of the end effector respectively
    # Note the x ordinate is scaled from 9 to 250 instead of 0 to 250 to account for an offset
    target_coords = [np.interp(img_coords[1], [166, 604], [9, 250]),
                     np.interp(img_coords[0], [132, 1152], [-250, 250])]

    # Account for offset of end-effector position due to the gripper being asymmetrical,
    # i.e. Add 0 to x-ordinate, subtract 14 from y-ordinate
    return [target_coords[0] + 0, target_coords[1] - 14]


def camera_thread():
    global block_coords, hand_coords, run, waiting, detector, y_error_mm
    ee_coords = []

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

    while run:
        img, _ = read_camera(camera)

        if isinstance(img, bool):
            continue

        img_warped = cv2.warpPerspective(img, ct_matrix, (RES_WIDTH, RES_HEIGHT))
        hands, img_warped = detector.findHands(img_warped)

        img_hsv = cv2.cvtColor(img_warped, cv2.COLOR_BGR2HSV)

        blue_dot_mask = cv2.inRange(img_hsv, blue_dot_hsv_min, blue_dot_hsv_max)
        img_dot_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_dot_mask)
        img_dot_canny = cv2.Canny(img_dot_resultant, 50, 50)

        orange_ee_mask = cv2.inRange(img_hsv, orange_ee_hsv_min, orange_ee_hsv_max)
        img_ee_resultant = cv2.bitwise_and(img_warped, img_warped, mask=orange_ee_mask)
        img_ee_canny = cv2.Canny(img_ee_resultant, 50, 50)

        blue_block_mask = cv2.inRange(img_hsv, blue_block_hsv_min, blue_block_hsv_max)
        img_block_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_block_mask)
        img_block_canny = cv2.Canny(img_block_resultant, 50, 50)

        img_contour = img_warped.copy()

        # Only parse the end effector dot position if 1 dot is found
        if ((dots := get_contours(img_dot_canny, img_contour, size=ContourSize.SMALL)) and
                (ee := get_contours(img_ee_canny, img_contour, size=ContourSize.LARGE)) and len(ee) == 1):
            ee = ee[0]
            for dot in dots:
                dot_pos = [dot[0] + dot[2] // 2, dot[1] + dot[3] // 2]
                ee_x = [ee[0], ee[0] + ee[2]]
                ee_y = [ee[1], ee[1] + ee[3]]

                if ee_x[0] < dot_pos[0] < ee_x[1] and ee_y[0] < dot_pos[1] < ee_y[1]:
                    ee_coords = dot_pos
                    print(f'EE dot found at {ee_coords}')
                    break

        # Only parse the block coordinates if 1 block is found
        if (contours := get_contours(img_block_canny, img_contour)) and len(contours) == 1:
            contour = contours[0]
            block_centre = [contour[0] + contour[2] // 2, contour[1] + contour[3] // 2]
            block_coords = map_coords(block_centre)
            print(f'Block found at {block_centre}')

        if ee_coords and block_coords:
            x_error_px = ee_coords[0] - block_coords[0]
            print(f'x error: {x_error_px} px')

            y_error_mm = x_error_px * 0.484

            # Account for gripper offset
            y_error_mm += 10

        # Only parse the hand coordinates if 1 hand is found
        if hands and len(hands) == 1:
            hand = hands[0]
            hand_centre = list(hand.get('center'))
            hand_coords = map_coords(hand_centre)
            print(f'Hand found at {hand_centre}')

        # img_stack = stack_images(0.5,
        #                          [[img_warped, img_hsv, blue_dot_mask],
        #                           [img_dot_resultant, img_dot_canny, img_contour]])

        cv2.imshow('Image Stack', img_contour)

        key = cv2.waitKey(1)
        if key == ord('c'):
            print('Beginning to move arm')
            waiting = False
        if key == ord('q'):
            run = False


def arm_thread():
    global block_coords, hand_coords, run, waiting, y_error_mm

    print('Arm Starting')

    arm = WlkataMirobot(portname=MIROBOT_PORT, debug=False, default_speed=20)
    # arm.gripper_close()
    arm.home()

    # Wait until the camera thread is stopped
    while run:
        if waiting:
            continue

        y_corrected = False
        while not y_corrected:
            # Account for gripper offset
            if y_error_mm - 10 > 3:
                # Figure out how to move robot y according to mm scale
                pass
            else:
                y_corrected = True

        if block_coords and hand_coords:
            print(f'Successfully found a block at {block_coords} and a hand at {hand_coords}!')

            print(f'Moving above source block')
            arm.p2p_interpolation(block_coords[0], block_coords[1], 130, 0, 0, 0)
            time.sleep(1)

            print('Adjusting robot y ordinate')

            print(f'Opening gripper')
            arm.gripper_open()
            time.sleep(1)

            print(f'Moving to source block')
            arm.p2p_interpolation(block_coords[0], block_coords[1], 70, 0, 0, 0)
            time.sleep(1)

            print(f'Picking up source block')
            arm.gripper_close()
            time.sleep(1)

            print(f'Lifting source block')
            arm.p2p_interpolation(block_coords[0], block_coords[1], 130, 0, 0, 0)
            time.sleep(1)

            print(f'Moving above destination block')
            arm.p2p_interpolation(hand_coords[0], hand_coords[1], 130, 0, 0, 0)
            time.sleep(1)

            print(f'Setting on destination block')
            arm.p2p_interpolation(hand_coords[0], hand_coords[1], 105, 0, 0, 0)
            time.sleep(1)

            print(f'Releasing down source block')
            arm.gripper_open()
            time.sleep(1)

            print(f'Moving above destination block')
            arm.p2p_interpolation(hand_coords[0], hand_coords[1], 130, 0, 0, 0)
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
