import cv2
import numpy as np

from opencv_helper_functions import ContourSize, stack_images, get_contours, empty
from config import RESOLUTION_HEIGHT, RESOLUTION_WIDTH


def detect():
    cv2.namedWindow('Trackbars')
    cv2.resizeWindow('Trackbars', 640, 330)
    cv2.createTrackbar('Hue Min 1', 'Trackbars', 0, 179, empty)
    cv2.createTrackbar('Hue Max 1', 'Trackbars', 10, 179, empty)
    cv2.createTrackbar('Hue Min 2', 'Trackbars', 170, 179, empty)
    cv2.createTrackbar('Hue Max 2', 'Trackbars', 179, 179, empty)
    cv2.createTrackbar('Sat Min', 'Trackbars', 0, 255, empty)
    cv2.createTrackbar('Sat Max', 'Trackbars', 255, 255, empty)
    cv2.createTrackbar('Val Min', 'Trackbars', 0, 255, empty)
    cv2.createTrackbar('Val Max', 'Trackbars', 255, 255, empty)

    cap = cv2.VideoCapture(0)
    cap.set(3, RESOLUTION_WIDTH)
    cap.set(4, RESOLUTION_HEIGHT)

    while True:
        _, img = cap.read()
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        hue_min1 = cv2.getTrackbarPos('Hue Min 1', 'Trackbars')
        hue_max1 = cv2.getTrackbarPos('Hue Max 1', 'Trackbars')
        hue_min2 = cv2.getTrackbarPos('Hue Min 2', 'Trackbars')
        hue_max2 = cv2.getTrackbarPos('Hue Max 2', 'Trackbars')
        sat_min = cv2.getTrackbarPos('Sat Min', 'Trackbars')
        sat_max = cv2.getTrackbarPos('Sat Max', 'Trackbars')
        val_min = cv2.getTrackbarPos('Val Min', 'Trackbars')
        val_max = cv2.getTrackbarPos('Val Max', 'Trackbars')

        lower1 = np.array([hue_min1, sat_min, val_min])
        upper1 = np.array([hue_max1, sat_max, val_max])
        lower2 = np.array([hue_min2, sat_min, val_min])
        upper2 = np.array([hue_max2, sat_max, val_max])
        mask1 = cv2.inRange(img_hsv, lower1, upper1)
        mask2 = cv2.inRange(img_hsv, lower2, upper2)
        mask = mask1 + mask2
        img_resultant = cv2.bitwise_and(img, img, mask=mask)
        img_canny = cv2.Canny(img_resultant, 50, 50)
        img_contour = img.copy()

        get_contours(img_canny, img_contour)
        get_contours(img_canny, img_contour, size=ContourSize.SMALL)

        img_stack = stack_images(0.5, [[img, img_hsv, mask], [img_resultant, img_canny, img_contour]])

        cv2.imshow('Image Stack', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break


if __name__ == '__main__':
    detect()
