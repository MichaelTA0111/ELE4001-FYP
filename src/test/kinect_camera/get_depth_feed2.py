import cv2
import numpy as np
import pykinect_azure as pykinect

from src.config import RESOLUTION_WIDTH, RESOLUTION_HEIGHT


if __name__ == "__main__":
    # Set camera transform settings
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

    cv2.namedWindow('Transformed Depth Image', cv2.WINDOW_NORMAL)
    while True:

        # Get capture
        capture = device.update()

        # Get the depth
        ret_depth, transformed_depth_image = capture.get_transformed_depth_image()
        transformed_depth_image = cv2.warpPerspective(transformed_depth_image, ct_matrix, (RESOLUTION_WIDTH, RESOLUTION_HEIGHT))

        if not ret_depth:
            continue

        # Display the image
        cv2.imshow('Transformed Depth Image', transformed_depth_image)
        print(f'{transformed_depth_image = }')

        # transformed_depth_image has a DEPTH16 image format

        # Press q key to stop
        if cv2.waitKey(1) == ord('q'):
            break
