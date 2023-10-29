from datetime import datetime


class CoordinateLogger:
    def __init__(self):
        start_time_str = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
        self.filename = f'mirobot_coordinate_log_{start_time_str}.csv'
        self.coordinate_list = []

        with open(self.filename, 'w') as f:
            f.write('x,y,z,roll,pitch,yaw,j1,j2,j3,j4,j5,j6\n')

    def log_coordinates(self, arm):
        status = arm.get_status()
        coordinate_str = (f'{status.cartesian.x},{status.cartesian.y},{status.cartesian.z},'
                          f'{status.cartesian.roll},{status.cartesian.pitch},{status.cartesian.yaw},'
                          f'{status.angle.joint1},{status.angle.joint2},{status.angle.joint3},'
                          f'{status.angle.joint4},{status.angle.joint5},{status.angle.joint6}\n')
        self.coordinate_list.append(coordinate_str)

        if not len(self.coordinate_list) % 10:
            print(f'Logged {len(self.coordinate_list)} items')

        if len(self.coordinate_list) >= 50:
            with open(self.filename, 'a') as f:
                [f.write(line) for line in self.coordinate_list]
            self.coordinate_list.clear()

