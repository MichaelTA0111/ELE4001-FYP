import cv2


def image():
    img = cv2.imread('resources/lena.png')
    cv2.imshow('Read Image Test', img)
    cv2.waitKey(0)


def video():
    width, height = 1280, 720
    cap = cv2.VideoCapture('resources/test_video.mp4')

    while True:
        success, img = cap.read()
        img = cv2.resize(img, (width, height))
        cv2.imshow('Read Video Test', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def webcam():
    width, height = 1280, 720
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)
    cap.set(10, 150)

    while True:
        success, img = cap.read()
        cv2.imshow('Read Webcam Test', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    # image()
    # video()
    webcam()
