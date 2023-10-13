import cv2
import numpy as np


def stack_grid(scale, images):
    rows = len(images)
    cols = len(images[0])

    width = images[0][0].shape[1]
    height = images[0][0].shape[0]

    for x in range(rows):
        for y in range(cols):
            if images[x][y].shape[:2] == images[0][0].shape[:2]:
                images[x][y] = cv2.resize(images[x][y], (0, 0), None, scale, scale)
            else:
                images[x][y] = cv2.resize(images[x][y], (images[0][0].shape[1], images[0][0].shape[0]),
                                          None, scale, scale)

            if len(images[x][y].shape) == 2:
                images[x][y] = cv2.cvtColor(images[x][y], cv2.COLOR_GRAY2BGR)

    img_blank = np.zeros((height, width, 3), np.uint8)
    hor = [img_blank] * rows

    for x in range(rows):
        hor[x] = np.hstack(images[x])

    return np.vstack(hor)


def stack_line(scale, images):
    rows = len(images)

    for x in range(rows):
        if images[x].shape[:2] == images[0].shape[:2]:
            images[x] = cv2.resize(images[x], (0, 0), None, scale, scale)
        else:
            images[x] = cv2.resize(images[x], (images[0].shape[1], images[0].shape[0]), None, scale, scale)

        if len(images[x].shape) == 2:
            images[x] = cv2.cvtColor(images[x], cv2.COLOR_GRAY2BGR)

    return np.hstack(images)


def stack_images(scale, images):
    rows_available = isinstance(images[0], list)

    if rows_available:
        return stack_grid(scale, images)
    else:
        return stack_line(scale, images)


def empty(a):
    pass


def detect():
    cv2.namedWindow('Trackbars')
    cv2.resizeWindow('Trackbars', 640, 240)
    cv2.createTrackbar('Hue Min', 'Trackbars', 0, 179, empty)  # Ranges from 0 to 360 or 0 to 180?
    cv2.createTrackbar('Hue Max', 'Trackbars', 19, 179, empty)
    cv2.createTrackbar('Sat Min', 'Trackbars', 110, 255, empty)
    cv2.createTrackbar('Sat Max', 'Trackbars', 240, 255, empty)
    cv2.createTrackbar('Val Min', 'Trackbars', 153, 255, empty)
    cv2.createTrackbar('Val Max', 'Trackbars', 255, 255, empty)

    path = 'resources/lambo.png'

    while True:
        img = cv2.imread(path)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        hue_min = cv2.getTrackbarPos('Hue Min', 'Trackbars')
        hue_max = cv2.getTrackbarPos('Hue Max', 'Trackbars')
        sat_min = cv2.getTrackbarPos('Sat Min', 'Trackbars')
        sat_max = cv2.getTrackbarPos('Sat Max', 'Trackbars')
        val_min = cv2.getTrackbarPos('Val Min', 'Trackbars')
        val_max = cv2.getTrackbarPos('Val Max', 'Trackbars')
        print(f'{hue_min} {hue_max} {sat_min} {sat_max} {val_min} {val_max}')

        lower = np.array([hue_min, sat_min, val_min])
        upper = np.array([hue_max, sat_max, val_max])
        mask = cv2.inRange(img_hsv, lower, upper)

        img_resultant = cv2.bitwise_and(img, img, mask=mask)

        img_stack = stack_images(0.75, [[img, img_hsv], [mask, img_resultant]])

        cv2.imshow('Image Stack', img_stack)
        cv2.waitKey(1)


if __name__ == '__main__':
    detect()
