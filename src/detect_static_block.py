import numpy as np
import cv2

from config import RES_HEIGHT, RES_WIDTH
from opencv_helper_functions import stack_images, get_contours
from coordinate_logger import CoordinateLogger
from pykinect_helper_functions import initialise_camera, read_camera


def camera_thread():
    run = True
    print('Input block location')
    location = input()
    coordinate_logger = CoordinateLogger(location)

    camera = initialise_camera()

    # Set the HSV values
    blue_block_hsv_min = np.array([100, 94, 71])
    blue_block_hsv_max = np.array([116, 240, 158])

    pts1 = np.float32([[292, 172], [976, 172], [162, 652], [1086, 664]])  # Points on original image
    pts2 = np.float32([[0, 0], [RES_WIDTH, 0],
                       [0, RES_HEIGHT], [RES_WIDTH, RES_HEIGHT]])  # New output points
    ct_matrix = cv2.getPerspectiveTransform(pts1, pts2)

    while run:
        img, img_depth = read_camera(camera)

        if isinstance(img, bool):
            continue

        img_warped = cv2.warpPerspective(img, ct_matrix, (RES_WIDTH, RES_HEIGHT))
        img_warped_depth = cv2.warpPerspective(img_depth, ct_matrix, (RES_WIDTH, RES_HEIGHT))
        img_hsv = cv2.cvtColor(img_warped, cv2.COLOR_BGR2HSV)

        blue_block_mask = cv2.inRange(img_hsv, blue_block_hsv_min, blue_block_hsv_max)
        img_block_resultant = cv2.bitwise_and(img_warped, img_warped, mask=blue_block_mask)
        img_block_canny = cv2.Canny(img_block_resultant, 50, 50)
        img_contour = img_warped.copy()

        # Only parse the block coordinates if 1 block is found
        if (contours := get_contours(img_block_canny, img_contour)) and len(contours) == 1:
            contour = contours[0]
            block_centre = [contour[0] + contour[2] // 2, contour[1] + contour[3] // 2]
            block_depth = img_warped_depth[block_centre[1], block_centre[0]]
            run = coordinate_logger.append_coordinates(block_centre, block_depth)

        img_stack = stack_images(0.5,
                                 [[img_contour]])

        cv2.imshow('Image Stack', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            run = False

        if not run:
            coordinate_logger.graph_coordinates()


def main():
    camera_thread()


if __name__ == '__main__':
    main()
