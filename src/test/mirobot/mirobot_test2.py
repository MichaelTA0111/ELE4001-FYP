import random
from threading import Thread
import time
import cv2
from wlkata_mirobot import WlkataMirobot

from coordinate_logger import CoordinateLogger


x, y, z = 100, 100, 100
roll, pitch, yaw = 0, 0, 0
do_open, do_close = False, False
joints = {1: 45, 2: -30, 3: 50, 4: 0, 5: -25, 6: -45}


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


def logging_thread(arm):
    logger = CoordinateLogger()

    previous_millis = time.time() * 1000

    while True:
        if (current_millis := time.time() * 1000) - previous_millis >= 500:
            previous_millis = current_millis
            logger.log_coordinates(arm)


def arm_thread():
    global do_open, do_close, joints

    print('Arm Starting')

    arm = WlkataMirobot(portname='COM3', default_speed=20)
    arm.home()

    Thread(target=logging_thread, args=(arm, )).start()

    previous_time = time.time()

    while True:
        current_time = time.time()
        if current_time - previous_time > 10:
            previous_time = current_time
            joints[1] = random.randint(-50, 100)
            joints[2] = random.randint(0, 50)
            joints[3] = random.randint(-100, 0)
            joints[4] = random.randint(-180, 180)
            joints[5] = random.randint(-180, 0)
            joints[6] = random.randint(-180, 180)
            print(f'Setting joints to: \n1 {joints[1]}\n2 {joints[2]}\n3 {joints[3]}\n4 {joints[4]}\n5 {joints[5]}\n'
                  f'6 {joints[6]}')

            arm.set_joint_angle(joints, speed=20)

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
