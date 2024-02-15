import numpy as np
import pykinect_azure as pykinect


def initialise_camera():
    # Initialize the library, if the library is not found, add the library path as argument
    pykinect.initialize_libraries()

    # Modify camera configuration
    device_config = pykinect.default_configuration
    device_config.color_format = pykinect.K4A_IMAGE_FORMAT_COLOR_BGRA32
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_720P
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED

    # Start device
    return pykinect.start_device(config=device_config)

def read_camera(camera):
    # Get capture
    capture = camera.update()

    # Get the color image from the capture
    ret_color, color_image = capture.get_color_image()

    # Get the colored depth
    ret_depth, transformed_depth_image = capture.get_transformed_depth_image()

    if not ret_color or not ret_depth:
        return False, False

    img = np.zeros((720, 1280, 3), dtype='uint8')
    r, g, b = color_image[:, :, 0], color_image[:, :, 1], color_image[:, :, 2]
    img[:, :, 0] = r
    img[:, :, 1] = g
    img[:, :, 2] = b

    return img, transformed_depth_image
