import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector

from config import RES_HEIGHT, RES_WIDTH
from pykinect_helper_functions import initialise_camera, read_camera


def camera_thread():
    detector = HandDetector(detectionCon=0.8, maxHands=1)

    camera = initialise_camera()

    pts1 = np.float32([[292, 172], [976, 172], [162, 652], [1086, 664]])  # Points on original image
    pts2 = np.float32([[0, 0], [RES_WIDTH, 0], [0, RES_HEIGHT], [RES_WIDTH, RES_HEIGHT]])  # New output points
    ct_matrix = cv2.getPerspectiveTransform(pts1, pts2)

    while True:
        img, _ = read_camera(camera)

        if isinstance(img, bool):
            continue

        img_warped = cv2.warpPerspective(img, ct_matrix, (RES_WIDTH, RES_HEIGHT))
        hands, img_warped = detector.findHands(img_warped)

        cv2.imshow('Video Feed', img_warped)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break


def main():
    camera_thread()


if __name__ == '__main__':
    main()
