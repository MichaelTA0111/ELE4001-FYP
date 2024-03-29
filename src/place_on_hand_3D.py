import time
from threading import Thread

import numpy as np
import cv2
from wlkata_mirobot import WlkataMirobot
from cvzone.HandTrackingModule import HandDetector
import pykinect_azure as pykinect

from config import MIROBOT_PORT, RES_HEIGHT, RES_WIDTH
from opencv_helper_functions import stack_images, get_contours


ee_coords = [[], []]
run = True
detector = HandDetector(detectionCon=0.8, maxHands=1)


def map_coords(img_coords, depth):
    """
    Convert image coordinates to end-effector coordinates
    :param img_coords: List of x and y coordinates from the image
    :param depth: The depth of the object being parsed from the image
    :return: List of x, y and z coordinates for the robot end-effector
    """
    # TODO: account for variable height, required for hand heights
    z_eq = 70

    print(img_coords, depth)

    # Note the x and y ordinates from the image map to the y and x ordinates of the end effector respectively
    # Note the x ordinate is scaled from 9 to 250 instead of 0 to 250 to account for an offset
    gripper_coords = [np.interp(img_coords[1], [166, 604], [9, 250]),
                      np.interp(img_coords[0], [132, 1152], [-250, 250])]

    # Account for offset of end-effector position due to the gripper being asymmetrical,
    # i.e. Add 0 to x-ordinate, subtract 14 from y-ordinate
    return [gripper_coords[0] + 0, gripper_coords[1] - 14]


def camera_thread():
    global ee_coords, run, detector, ct_matrix

    # Initialize the library, if the library is not found, add the library path as argument
    pykinect.initialize_libraries()

    # Modify camera configuration
    device_config = pykinect.default_configuration
    device_config.color_format = pykinect.K4A_IMAGE_FORMAT_COLOR_BGRA32
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_720P
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED

    # Start device
    device = pykinect.start_device(config=device_config)

    # Set the HSV values
    blue_hsv_min = np.array([100, 94, 71])
    blue_hsv_max = np.array([116, 240, 158])

    pts1 = np.float32([[292, 172], [976, 172], [162, 652], [1086, 664]])  # Points on original image
    pts2 = np.float32([[0, 0], [RES_WIDTH, 0],
                       [0, RES_HEIGHT], [RES_WIDTH, RES_HEIGHT]])  # New output points
    ct_matrix = cv2.getPerspectiveTransform(pts1, pts2)

    while run:
        # Get capture
        capture = device.update()

        # Get the color image from the capture
        ret_color, color_image = capture.get_color_image()

        # Get the colored depth
        ret_depth, transformed_depth_image = capture.get_transformed_depth_image()

        if not ret_color or not ret_depth:
            continue

        img = np.zeros((720, 1280, 3), dtype='uint8')
        r, g, b = color_image[:, :, 0], color_image[:, :, 1], color_image[:, :, 2]
        img[:, :, 0] = r
        img[:, :, 1] = g
        img[:, :, 2] = b

        img_warped = cv2.warpPerspective(img, ct_matrix, (RES_WIDTH, RES_HEIGHT))
        hands, img_warped = detector.findHands(img_warped)

        img_warped_depth = cv2.warpPerspective(transformed_depth_image, ct_matrix, (RES_WIDTH, RES_HEIGHT))

        img_hsv = cv2.cvtColor(img_warped, cv2.COLOR_BGR2HSV)

        blue_mask = cv2.inRange(img_hsv, blue_hsv_min, blue_hsv_max)
        img_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_mask)
        img_canny = cv2.Canny(img_resultant, 50, 50)
        img_contour = img_warped.copy()

        # Only parse the block coordinates if 1 block is found
        if (contours := get_contours(img_canny, img_contour)) and len(contours) == 1:
            contour = contours[0]
            block_centre = [contour[0] + contour[2] // 2, contour[1] + contour[3] // 2]
            block_depth = img_warped_depth[block_centre[1], block_centre[0]]
            print(f'Block found at ({block_centre[1]}, {block_centre[0]}, {block_depth})')
            # ee_coords[0] = map_coords(block_centre, block_depth)

        # Only parse the hand coordinates if 1 hand is found
        if hands and len(hands) == 1:
            hand = hands[0]
            hand_centre = list(hand.get('center'))
            hand_depth = img_warped_depth[hand_centre[1], hand_centre[0]]
            ee_coords[1] = map_coords(hand_centre, hand_depth)

        img_stack = stack_images(0.5,
                                 [[img_warped, img_hsv, blue_mask], [img_resultant, img_canny, img_contour]])

        cv2.imshow('Image Stack', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            run = False


def arm_thread():
    global ee_coords, run

    print('Arm Starting')

    arm = WlkataMirobot(portname=MIROBOT_PORT, debug=False, default_speed=20)
    arm.home()

    # Wait until the camera thread is stopped
    while run:
        pass

    # Temp, change length to 2 to work
    if len(ee_coords) == 3:
        print(f'Successfully found a block at {ee_coords[0]} and a hand at {ee_coords[1]}!')

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
