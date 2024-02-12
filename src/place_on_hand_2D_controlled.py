import time
from threading import Thread

import numpy as np
import cv2
from wlkata_mirobot import WlkataMirobot
from cvzone.HandTrackingModule import HandDetector

from config import MIROBOT_PORT, RES_HEIGHT, RES_WIDTH
from opencv_helper_functions import stack_images, get_contours
from pykinect_helper_functions import initialise_camera, read_camera


ee_pos = []
ee_coords = [[], []]
run = True
detector = HandDetector(detectionCon=0.8, maxHands=1)


def map_coords(img_coords, z=70):
    """
    Convert image coordinates to end-effector coordinates
    :param img_coords: List of x and y coordinates from the image
    :param z: The z-ordinate of the object being parsed from the image
    :return: List of x and y coordinates for the robot end-effector
    """
    # TODO: account for variable height, required for hand heights
    z_eq = 70
    z_bar = z - z_eq

    # Note the x and y ordinates from the image map to the y and x ordinates of the end effector respectively
    # Note the x ordinate is scaled from 9 to 250 instead of 0 to 250 to account for an offset
    ee_coords = [np.interp(img_coords[1], [166, 604], [9, 250]),
                 np.interp(img_coords[0], [132, 1152], [-250, 250])]

    # Account for offset of end-effector position due to the gripper being asymmetrical,
    # i.e. Add 0 to x-ordinate, subtract 14 from y-ordinate
    return [ee_coords[0] + 0, ee_coords[1] - 14]


def camera_thread():
    global ee_pos, ee_coords, run, detector

    camera = initialise_camera()

    # Set the HSV values
    blue_dot_hsv_min = np.array([107, 49, 93])
    blue_dot_hsv_max = np.array([124, 240, 198])
    blue_block_hsv_min = np.array([100, 94, 71])
    blue_block_hsv_max = np.array([116, 240, 158])

    pts1 = np.float32([[292, 172], [976, 172], [162, 652], [1086, 664]])  # Points on original image
    pts2 = np.float32([[0, 0], [RES_WIDTH, 0],
                       [0, RES_HEIGHT], [RES_WIDTH, RES_HEIGHT]])  # New output points
    ct_matrix = cv2.getPerspectiveTransform(pts1, pts2)

    while run:
        img, _ = read_camera(camera)

        if not img:
            continue

        img_warped = cv2.warpPerspective(img, ct_matrix, (RES_WIDTH, RES_HEIGHT))
        hands, img_warped = detector.findHands(img_warped)

        img_hsv = cv2.cvtColor(img_warped, cv2.COLOR_BGR2HSV)

        blue_dot_mask = cv2.inRange(img_hsv, blue_dot_hsv_min, blue_dot_hsv_max)
        img_dot_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_dot_mask)
        img_dot_canny = cv2.Canny(img_dot_resultant, 50, 50)

        blue_block_mask = cv2.inRange(img_hsv, blue_block_hsv_min, blue_block_hsv_max)
        img_block_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_block_mask)
        img_block_canny = cv2.Canny(img_block_resultant, 50, 50)

        img_contour = img_warped.copy()

        # Only parse the end effector position if 1 dot is found
        if (contours := get_contours(img_dot_canny, img_contour, small=True)) and len(contours) == 1:
            contour = contours[0]
            ee_pos = [contour[0] + contour[2] // 2, contour[1] + contour[3] // 2]
            print(ee_pos)

        # Only parse the block coordinates if 1 block is found
        if (contours := get_contours(img_block_canny, img_contour)) and len(contours) == 1:
            contour = contours[0]
            block_centre = [contour[0] + contour[2] // 2, contour[1] + contour[3] // 2]
            ee_coords[0] = map_coords(block_centre)

        # Only parse the hand coordinates if 1 hand is found
        if hands and len(hands) == 1:
            hand = hands[0]
            hand_centre = list(hand.get('center'))
            ee_coords[1] = map_coords(hand_centre)

        img_stack = stack_images(0.5,
                                 [[img_warped, img_hsv, blue_dot_mask],
                                  [img_dot_resultant, img_dot_canny, img_contour]])

        cv2.imshow('Image Stack', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            run = False


def arm_thread():
    global ee_coords, run

    print('Arm Starting')

    arm = WlkataMirobot(portname=MIROBOT_PORT, debug=False, default_speed=20)
    # arm.gripper_close()
    arm.home()

    # Wait until the camera thread is stopped
    while run:
        pass

    if len(ee_coords) == 2:
        print(f'Successfully found a blocks at {ee_coords[0]} and a hand at {ee_coords[1]}!')

        src = ee_coords[0]
        dst = ee_coords[1]

        print(f'Moving above source block')
        arm.p2p_interpolation(src[0], src[1], 130, 0, 0, 0)
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
        arm.p2p_interpolation(src[0], src[1], 130, 0, 0, 0)
        time.sleep(1)

        print(f'Moving above destination block')
        arm.p2p_interpolation(dst[0], dst[1], 130, 0, 0, 0)
        time.sleep(1)

        print(f'Setting on destination block')
        arm.p2p_interpolation(dst[0], dst[1], 105, 0, 0, 0)
        time.sleep(1)

        print(f'Releasing down source block')
        arm.gripper_open()
        time.sleep(1)

        print(f'Moving above destination block')
        arm.p2p_interpolation(dst[0], dst[1], 130, 0, 0, 0)
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
