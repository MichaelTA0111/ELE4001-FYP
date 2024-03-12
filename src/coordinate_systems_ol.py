from enum import Enum

import numpy as np


class ObjectType(Enum):
    BLOCK = 0
    EE = 1
    HAND = 2


class Object:
    def __init__(self):
        self.img_x = None
        self.img_y = None
        self.robot_x = None
        self.robot_y = None

    def update(self, x, y):
        self.img_x = x
        self.img_y = y

    def reset(self):
        self.img_x = None
        self.img_y = None

    def map_coords(self):
        """ Convert image coordinates to end-effector coordinates """
        # Note the x and y ordinates from the image map to the y and x ordinates of the end effector respectively
        # Note the x ordinate is scaled from 9 to 250 instead of 0 to 250 to account for an offset
        target_x = np.interp(self.img_y, [166, 604], [9, 250])
        target_y = np.interp(self.img_x, [132, 1152], [-250, 250])

        # Account for offset of end-effector position due to the gripper being asymmetrical,
        # i.e. Add 0 to x-ordinate, subtract 14 from y-ordinate
        self.robot_x = target_x + 0
        self.robot_y = target_y - 14

    @property
    def is_controllable(self):
        return self.img_x is not None and self.img_y is not None

    @property
    def img(self):
        return [self.img_x, self.img_y]

    @property
    def robot(self):
        return [self.robot_x, self.robot_y]


class ObjectCoordinates:
    def __init__(self):
        self.block = Object()
        self.ee = Object()
        self.hand = Object()

    def calculate_y_error(self, object_type):
        if object_type is ObjectType.BLOCK and not self.is_block_controllable:
            return None

        if object_type is ObjectType.HAND and not self.is_hand_controllable:
            return None

        # Calculate the error in the image x coordinates
        if object_type is ObjectType.BLOCK:
            x_error_px = self.ee.img_x - self.block.img_x
        elif object_type is ObjectType.HAND:
            x_error_px = self.ee.img_x - self.hand.img_x
        else:
            raise NotImplementedError
        # print(f'x error: {x_error_px} px')

        # Convert pixel reading to mm according to manual calibration
        y_error_mm = x_error_px * 0.484

        # Account for gripper offset
        y_error_mm += 10

        return y_error_mm

    def calculate_robot_coordinates(self, object_type, y, y_error):
        if object_type is ObjectType.BLOCK:
            self.block.map_coords()
            robot_x = self.block.robot_x
        elif object_type is ObjectType.HAND:
            self.hand.map_coords()
            robot_x = self.hand.robot_x
        else:
            raise NotImplementedError

        robot_y = y - y_error

        return robot_x, robot_y

    @property
    def is_block_controllable(self):
        return self.ee.is_controllable and self.block.is_controllable

    @property
    def is_hand_controllable(self):
        return self.ee.is_controllable and self.hand.is_controllable
