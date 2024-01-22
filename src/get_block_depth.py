import time
from threading import Thread

import numpy as np
import cv2
import pykinect_azure as pykinect

from config import RES_HEIGHT, RES_WIDTH
from opencv_helper_functions import stack_images, get_contours


run = True


def camera_thread():
    global run, ct_matrix

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
        img_warped_depth = cv2.warpPerspective(transformed_depth_image, ct_matrix, (RES_WIDTH, RES_HEIGHT))
        img_hsv = cv2.cvtColor(img_warped, cv2.COLOR_BGR2HSV)

        blue_mask = cv2.inRange(img_hsv, blue_hsv_min, blue_hsv_max)
        img_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_mask)
        img_canny = cv2.Canny(img_resultant, 50, 50)
        img_contour = img_warped.copy()

        # Only parse the block coordinates if 1 block is found
        if (contours := get_contours(img_canny, img_contour)) and len(contours) == 2:
            output = 'Block(s) found at:\n'
            for i, contour in enumerate(contours):
                block_centre = [contour[0] + contour[2] // 2, contour[1] + contour[3] // 2]
                block_depth = img_warped_depth[block_centre[1], block_centre[0]]
                if i > 0:
                    output += ', '
                output += f'(x: {block_centre[1]}, y: {block_centre[0]}, depth: {block_depth})'
            print(output)

        img_stack = stack_images(0.5,
                                 [[img_contour]])

        cv2.imshow('Video Feed', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            run = False


def main():
    Thread(target=camera_thread).start()
    print('Both threads started successfully!')


if __name__ == '__main__':
    main()
