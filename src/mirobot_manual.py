from threading import Thread
import cv2
from wlkata_mirobot import WlkataMirobot

from config import MIROBOT_PORT, RESOLUTION_HEIGHT, RESOLUTION_WIDTH


x, y, z = 100, 100, 100
a, b, c = 0, 0, 0
do_open, do_close = False, False


def camera_thread():
    global x, y, z, do_open, do_close

    print('Camera Starting')

    cap = cv2.VideoCapture(0)
    cap.set(3, RESOLUTION_WIDTH)
    cap.set(4, RESOLUTION_HEIGHT)

    while True:
        _, img = cap.read()
        cv2.imshow('Video Feed', img)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break


def parse_command():
    global x, y, z, a, b, c, do_open, do_close

    command = input()
    command = command.split(' ')
    if command[0] == 'x':
        x = int(command[1])
    if command[0] == 'y':
        y = int(command[1])
    if command[0] == 'z':
        z = int(command[1])
    if command[0] == 'a':
        a = int(command[1])
    if command[0] == 'b':
        b = int(command[1])
    if command[0] == 'c':
        c = int(command[1])
    if command[0] == 'open':
        do_open = True
    if command[0] == 'close':
        do_close = True


def arm_thread():
    global x, y, z, a, b, c, do_open, do_close

    print('Arm Starting')

    arm = WlkataMirobot(portname=MIROBOT_PORT)
    arm.home()

    while True:
        parse_command()

        print(f'Moving to coordinates:\nx {x}\ny {y}\nz {z}\na {a}\nb {b}\nc {c}')
        arm.p2p_interpolation(x, y, z, a, b, c)

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
