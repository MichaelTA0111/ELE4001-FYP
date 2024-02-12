from datetime import datetime
import csv
import matplotlib.pyplot as plt


class CoordinateLogger:
    def __init__(self):
        start_time_str = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
        self.filename = f'block_coordinate_log_{start_time_str}'
        self.filename_csv = self.filename + '.csv'
        self.filename_png = self.filename + '.png'
        self.filename_svg = self.filename + '.svg'
        self.coordinate_list = []

        with open(self.filename_csv, 'w') as f:
            f.write('x,y,depth\n')

    def log_coordinates(self, do_print=False):
        if len(self.coordinate_list):
            with open(self.filename_csv, 'a') as f:
                [f.write(line) for line in self.coordinate_list]
            self.coordinate_list.clear()

            if do_print:
                print('Coordinates logged successfully')

    def append_coordinates(self, xy, depth, do_print=False):
        coordinate_str = f'{xy[0]},{xy[1]},{depth}\n'
        self.coordinate_list.append(coordinate_str)

        if do_print and not len(self.coordinate_list) % 10:
            print(f'Appended {len(self.coordinate_list)} items')

        if len(self.coordinate_list) >= 50:
            self.log_coordinates(do_print=do_print)

    def graph_coordinates(self):
        coordinates = []
        with open(self.filename_csv) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    coordinates.append(row)
                    line_count += 1

        # Create a figure with 3 subplots
        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(12, 8))

        # Plot x, y, and depth against index
        for i in range(3):
            axes[i].plot(range(len(coordinates)), [coord[i] for coord in coordinates])
        axes[0].set_title('x-ordinate over time')
        axes[1].set_title('y-ordinate over time')
        axes[2].set_title('Depth over time')

        plt.tight_layout()
        plt.savefig(self.filename_png)
        plt.savefig(self.filename_svg)
        plt.show()

