import cv2
import numpy as np
import pykinect_azure as pykinect
from pykinect_azure import K4A_CALIBRATION_TYPE_COLOR, K4A_CALIBRATION_TYPE_DEPTH, k4a_float2_t

from src.config import RESOLUTION_WIDTH, RESOLUTION_HEIGHT


if __name__ == "__main__":
    # Create the transform matrix
    pts1 = np.float32([[292, 172], [976, 172], [162, 652], [1086, 664]])  # Points on original image
    pts2 = np.float32([[0, 0], [RESOLUTION_WIDTH, 0],
                       [0, RESOLUTION_HEIGHT], [RESOLUTION_WIDTH, RESOLUTION_HEIGHT]])  # New output points
    ct_matrix = cv2.getPerspectiveTransform(pts1, pts2)

    # Initialize the library, if the library is not found, add the library path as argument
    pykinect.initialize_libraries()

    # Modify camera configuration
    device_config = pykinect.default_configuration
    device_config.color_format = pykinect.K4A_IMAGE_FORMAT_COLOR_BGRA32
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_720P
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
    # print(device_config)

    # Start device
    device = pykinect.start_device(config=device_config)

    cv2.namedWindow('Transformed Color Depth Image', cv2.WINDOW_NORMAL)

    while True:
        # Get capture
        capture = device.update()

        # Get the color image from the capture
        ret_color, color_image = capture.get_color_image()

        # Get the colored depth
        ret_depth, transformed_colored_depth_image = capture.get_transformed_colored_depth_image()

        if not ret_color or not ret_depth:
            continue

        img_warped = cv2.warpPerspective(transformed_colored_depth_image, ct_matrix, (RESOLUTION_WIDTH, RESOLUTION_HEIGHT))

        pix_x = color_image.shape[1] // 2
        pix_y = color_image.shape[0] // 2
        rgb_depth = transformed_colored_depth_image[pix_y, pix_x]

        pixels = k4a_float2_t((pix_x, pix_y))

        pos3d_color = device.calibration.convert_2d_to_3d(pixels, rgb_depth, K4A_CALIBRATION_TYPE_COLOR,
                                                          K4A_CALIBRATION_TYPE_COLOR)
        pos3d_depth = device.calibration.convert_2d_to_3d(pixels, rgb_depth, K4A_CALIBRATION_TYPE_COLOR,
                                                          K4A_CALIBRATION_TYPE_DEPTH)
        print(f"RGB depth: {rgb_depth}, RGB pos3D: {pos3d_color}, Depth pos3D: {pos3d_depth}")

        # Overlay body segmentation on depth image
        cv2.imshow('Image', img_warped)

        # Press q key to stop
        if cv2.waitKey(1) == ord('q'):
            break
