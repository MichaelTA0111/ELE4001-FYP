import cv2
import numpy as np


def image():
    img = cv2.imread('resources/cards.jpg')

    width, height = 250, 350

    pts1 = np.float32([[111, 219], [287, 188], [154, 482], [352, 440]])  # Points on original image
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])  # New output points
    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    img_warped = cv2.warpPerspective(img, matrix, (width, height))

    cv2.imshow('Original Image', img)
    cv2.imshow('Warped Image', img_warped)
    cv2.waitKey(0)


if __name__ == '__main__':
    image()
