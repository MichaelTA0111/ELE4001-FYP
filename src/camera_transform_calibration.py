import cv2
import numpy as np

from datetime import datetime

from opencv_helper_functions import stack_images
from config import RESOLUTION_HEIGHT, RESOLUTION_WIDTH


def detect():
    cap = cv2.VideoCapture(0)
    cap.set(3, RESOLUTION_WIDTH)
    cap.set(4, RESOLUTION_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 5)
    # fps = int(cap.get(5))
    # print("fps:", fps)

    while True:
        _, img = cap.read()

        pts1 = np.float32([[292, 172], [976, 172], [162, 652], [1086, 664]])  # Points on original image
        pts2 = np.float32([[0, 0], [RESOLUTION_WIDTH, 0],
                           [0, RESOLUTION_HEIGHT], [RESOLUTION_WIDTH, RESOLUTION_HEIGHT]])  # New output points
        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        img_warped = cv2.warpPerspective(img, matrix, (RESOLUTION_WIDTH, RESOLUTION_HEIGHT))

        img_stack = stack_images(0.5, [[img], [img_warped]])

        cv2.imshow('Image Stack', img_stack)

        key = cv2.waitKey(1)
        if key == ord('q'):
            start_time_str = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
            filename = f'camera_transform_calibration_{start_time_str}.png'
            cv2.imwrite(filename, img_stack)
            break


if __name__ == '__main__':
    detect()
