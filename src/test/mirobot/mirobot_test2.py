import random
from threading import Thread
import time
import cv2
from wlkata_mirobot import WlkataMirobot, WlkataMirobotTool


x, y, z = 100, 100, 100
a, b, c = 0, 0, 0
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
        # elif key == ord('o'):
        #     do_open = True
        #     time.sleep(0.2)
        # elif key == ord('c'):
        #     do_close = True
        #     time.sleep(0.2)
        # elif key == ord('u'):
        #     x -= 10
        #     print(f'Decreasing x to {x}')
        #     time.sleep(0.2)
        # elif key == ord('v'):
        #     y -= 10
        #     print(f'Decreasing y to {y}')
        #     time.sleep(0.2)
        # elif key == ord('w'):
        #     z -= 10
        #     print(f'Decreasing z to {z}')
        #     time.sleep(0.2)
        # elif key == ord('x'):
        #     x += 10
        #     print(f'Increasing x to {x}')
        #     time.sleep(0.2)
        # elif key == ord('y'):
        #     y += 10
        #     print(f'Increasing y to {y}')
        #     time.sleep(0.2)
        # elif key == ord('z'):
        #     z += 10
        #     print(f'Increasing z to {z}')
        #     time.sleep(0.2)


def parse_command():
    global x, y, z, a, b, c, do_open, do_close

    command = input()
    print(command)

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
    if command[0] == 'j1':
        joints[1] = int(command[1])
    if command[0] == 'j2':
        joints[2] = int(command[1])
    if command[0] == 'j3':
        joints[3] = int(command[1])
    if command[0] == 'j4':
        joints[4] = int(command[1])
    if command[0] == 'j5':
        joints[5] = int(command[1])
    if command[0] == 'j6':
        joints[6] = int(command[1])
    if command[0] == 'open':
        do_open = True
    if command[0] == 'close':
        do_close = True


def arm_thread():
    global x, y, z, a, b, c, do_open, do_close
    global joints

    print('Arm Starting')

    arm = WlkataMirobot(portname='COM3', debug=True)
    arm.home()

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

        arm.set_joint_angle(joints, speed=200)

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
