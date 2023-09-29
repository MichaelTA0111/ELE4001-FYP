from threading import Thread
import time
import cv2
from wlkata_mirobot import WlkataMirobot, WlkataMirobotTool


x, y, z = 100, 100, 100
do_open, do_close = False, False


def camera_thread():
    global x, y, z, do_open, do_close

    print('Camera Starting')

    width, height = 1280, 720
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)

    while True:
        _, img = cap.read()
        img = cv2.flip(img, 1)
        cv2.imshow('Video Feed', img)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('o'):
            do_open = True
            time.sleep(0.2)
        elif key == ord('c'):
            do_close = True
            time.sleep(0.2)
        elif key == ord('u'):
            x -= 10
            time.sleep(0.2)
        elif key == ord('v'):
            y -= 10
            time.sleep(0.2)
        elif key == ord('w'):
            z -= 10
            time.sleep(0.2)
        elif key == ord('x'):
            x += 10
            time.sleep(0.2)
        elif key == ord('y'):
            y += 10
            time.sleep(0.2)
        elif key == ord('z'):
            z += 10
            time.sleep(0.2)


def arm_thread():
    global x, y, z, do_open, do_close

    print('Arm Starting')

    arm = WlkataMirobot(portname='COM3')
    arm.home()

    while True:
        arm.p2p_interpolation(x, y, z)

        if do_open:
            arm.gripper_open()
            do_open = False
            print('Opening Gripper')
        elif do_close:
            arm.gripper_close()
            do_close = False
            print('Closing Gripper')


def main():
    Thread(target=camera_thread).start()
    Thread(target=arm_thread).start()
    print('Both threads started successfully!')


if __name__ == '__main__':
    main()
