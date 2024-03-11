from enum import Enum

import cv2
import numpy as np


class ContourSize(Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


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


def draw_contour(img, c):
    cv2.drawContours(img, c, -1, (255, 0, 0), 3)
    perimeter = cv2.arcLength(c, True)
    approx_outline = cv2.approxPolyDP(c, 0.02 * perimeter, True)
    x, y, w, h = cv2.boundingRect(approx_outline)

    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return [x, y, w, h]


def get_contours(img_src, img_dst, size=ContourSize.MEDIUM):
    contours, hierarchy = cv2.findContours(img_src, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

    positions = []

    for c in contours:
        area = cv2.contourArea(c)
        # print(area)

        if size is ContourSize.SMALL and 100 < area <= 1500:
            positions.append(draw_contour(img_dst, c))
        elif size is ContourSize.MEDIUM and 1500 < area <= 2500:
            positions.append(draw_contour(img_dst, c))
        elif size is ContourSize.LARGE and 1500 < area:
            positions.append(draw_contour(img_dst, c))

    return positions


if __name__ == '__main__':
    print('Please run a different source file!')
