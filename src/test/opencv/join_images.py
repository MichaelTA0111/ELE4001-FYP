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


def advanced():
    img = cv2.imread('resources/lena.png')
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

    img_line = stack_images(0.8, [img, img_gray, img])
    img_grid = stack_images(0.5, [[img, img_gray, img], [img_gray, img, img_gray]])

    cv2.imshow('Image Line', img_line)
    cv2.imshow('Image Grid', img_grid)
    cv2.waitKey(0)


def basic():
    img = cv2.imread('resources/lena.png')

    stack_hor = np.hstack((img, img))
    stack_ver = np.vstack((img, img))

    cv2.imshow('Horizontal Stack', stack_hor)
    cv2.imshow('Vertical Stack', stack_ver)
    cv2.waitKey(0)


if __name__ == '__main__':
    basic()
    advanced()
