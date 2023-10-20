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


def draw_contours(img_src, img_dst):
    contours, hierarchy = cv2.findContours(img_src, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for c in contours:
        area = cv2.contourArea(c)

        if area > 500:
            cv2.drawContours(img_dst, c, -1, (255, 0, 0), 3)
            perimeter = cv2.arcLength(c, True)
            approx_outline = cv2.approxPolyDP(c, 0.02 * perimeter, True)
            num_corners = len(approx_outline)
            x, y, w, h = cv2.boundingRect(approx_outline)

            if num_corners == 3:
                obj_type = 'Triangle'
            elif num_corners == 4:
                if (aspect_ratio := w / h) > 0.98 and aspect_ratio < 1.02:
                    obj_type = 'Square'
                else:
                    obj_type = 'Rectangle'
            elif num_corners > 4:
                obj_type = 'Circle'
            else:
                obj_type = 'Unknown'

            cv2.rectangle(img_dst, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img_dst,
                        obj_type,
                        (x + w // 2 - 25, y + h // 2),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.5,
                        (0, 0, 0),
                        2)


def detect():
    path = 'resources/shapes.png'

    img = cv2.imread(path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (7, 7), 1)
    img_canny = cv2.Canny(img_blur, 50, 50)
    img_contour = img.copy()
    img_blank = np.zeros_like(img)

    draw_contours(img_canny, img_contour)

    img_stack = stack_images(0.75, [[img, img_gray, img_blur], [img_canny, img_contour, img_blank]])

    cv2.imshow('Image Stack', img_stack)
    cv2.waitKey(0)


if __name__ == '__main__':
    detect()
