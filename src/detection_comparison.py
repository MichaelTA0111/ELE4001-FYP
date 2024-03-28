import numpy as np
import cv2

from config import RES_HEIGHT, RES_WIDTH
from opencv_helper_functions import ContourSize, stack_images, get_contours
from pykinect_helper_functions import initialise_camera, read_camera


def camera_thread():
    camera = initialise_camera()

    # Set the HSV values
    orange_ee_hsv_min = np.array([2, 185, 73])
    orange_ee_hsv_max = np.array([27, 255, 255])

    pts1 = np.float32([[292, 172], [976, 172], [162, 652], [1086, 664]])  # Points on original image
    pts2 = np.float32([[0, 0], [RES_WIDTH, 0], [0, RES_HEIGHT], [RES_WIDTH, RES_HEIGHT]])  # New output points
    ct_matrix = cv2.getPerspectiveTransform(pts1, pts2)

    kernel_dilate = np.ones((5, 5), np.uint8)
    kernel_erode = np.ones((3, 3), np.uint8)

    while True:
        img, _ = read_camera(camera)

        if isinstance(img, bool):
            continue

        img_warped = cv2.warpPerspective(img, ct_matrix, (RES_WIDTH, RES_HEIGHT))
        img_hsv = cv2.cvtColor(img_warped, cv2.COLOR_BGR2HSV)

        orange_ee_mask = cv2.inRange(img_hsv, orange_ee_hsv_min, orange_ee_hsv_max)
        img_ee_resultant = cv2.bitwise_and(img_warped, img_warped, mask=orange_ee_mask)
        img_ee_canny = cv2.Canny(img_ee_resultant, 50, 50)

        # Apply dilation and erosion to Canny image
        img_ee_canny_dilated = cv2.dilate(img_ee_canny, kernel_dilate, iterations=1)
        img_ee_canny_eroded = cv2.erode(img_ee_canny_dilated, kernel_erode, iterations=1)

        img_contour = img_warped.copy()
        get_contours(img_ee_canny_eroded, img_contour, size=ContourSize.LARGE)

        img_stack = stack_images(0.5,
                                 [[img_warped, img_ee_canny],
                                  [img_ee_canny_eroded, img_contour]])

        cv2.imshow('Image Stack', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break


def main():
    camera_thread()


if __name__ == '__main__':
    main()
