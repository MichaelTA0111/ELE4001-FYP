import cv2

from config import RESOLUTION_HEIGHT, RESOLUTION_WIDTH


def detect():
    cap = cv2.VideoCapture(0)
    cap.set(3, RESOLUTION_WIDTH)
    cap.set(4, RESOLUTION_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 5)

    while True:
        _, img = cap.read()

        cv2.imshow('Video feed', img)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break


if __name__ == '__main__':
    detect()
