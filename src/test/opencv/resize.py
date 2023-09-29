import cv2


def image():
    img = cv2.imread('resources/shapes.png')
    print(img.shape)

    img_resize = cv2.resize(img, (1000, 500))
    print(img_resize.shape)

    img_cropped = img[46:419, 52:495]

    cv2.imshow('Original Image', img)
    cv2.imshow('Resized Image', img_resize)
    cv2.imshow('Cropped Image', img_cropped)
    cv2.waitKey(0)


if __name__ == '__main__':
    image()
