import cv2
import numpy as np


def image():
    img = np.zeros((512, 512, 3), np.uint8)

    print(img)

    img[:] = 100, 100, 50  # Changes pixel colour for all elements in the array
    img[256:384, 128:384] = 50, 50, 100

    cv2.line(img, (0, 0), (img.shape[1], img.shape[0]), (0, 255, 0), 3)
    cv2.rectangle(img, (0, 0), (250, 350), (0, 0, 255), 2)
    cv2.circle(img, (400, 50), 30, (255, 255, 0), 5)
    cv2.putText(img, ' OpenCV ', (300, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 150, 0), 3)

    cv2.imshow('Image', img)
    cv2.waitKey(0)


if __name__ == '__main__':
    image()
