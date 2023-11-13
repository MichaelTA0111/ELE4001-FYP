import cv2
import numpy as np

from opencv_helper_functions import stack_images, get_contours, empty
from config import RESOLUTION_HEIGHT, RESOLUTION_WIDTH


def detect():
    cv2.namedWindow('Trackbars')
    cv2.resizeWindow('Trackbars', 640, 240)
    cv2.createTrackbar('Hue Min', 'Trackbars', 0, 179, empty)  # Ranges from 0 to 360 or 0 to 180?
    cv2.createTrackbar('Hue Max', 'Trackbars', 19, 179, empty)
    cv2.createTrackbar('Sat Min', 'Trackbars', 110, 255, empty)
    cv2.createTrackbar('Sat Max', 'Trackbars', 240, 255, empty)
    cv2.createTrackbar('Val Min', 'Trackbars', 153, 255, empty)
    cv2.createTrackbar('Val Max', 'Trackbars', 255, 255, empty)

    cap = cv2.VideoCapture(0)
    cap.set(3, RESOLUTION_WIDTH)
    cap.set(4, RESOLUTION_HEIGHT)

    while True:
        _, img = cap.read()
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        hue_min = cv2.getTrackbarPos('Hue Min', 'Trackbars')
        hue_max = cv2.getTrackbarPos('Hue Max', 'Trackbars')
        sat_min = cv2.getTrackbarPos('Sat Min', 'Trackbars')
        sat_max = cv2.getTrackbarPos('Sat Max', 'Trackbars')
        val_min = cv2.getTrackbarPos('Val Min', 'Trackbars')
        val_max = cv2.getTrackbarPos('Val Max', 'Trackbars')

        lower = np.array([hue_min, sat_min, val_min])
        upper = np.array([hue_max, sat_max, val_max])
        mask = cv2.inRange(img_hsv, lower, upper)
        img_resultant = cv2.bitwise_and(img, img, mask=mask)
        img_canny = cv2.Canny(img_resultant, 50, 50)
        img_contour = img.copy()

        get_contours(img_canny, img_contour)

        img_stack = stack_images(0.5, [[img, img_hsv, mask], [img_resultant, img_canny, img_contour]])

        cv2.imshow('Image Stack', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

if __name__ == '__main__':
    detect()
