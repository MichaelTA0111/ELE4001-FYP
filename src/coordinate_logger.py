import csv
import matplotlib.pyplot as plt


class CoordinateLogger:
    def __init__(self, name, create=True):
        self.filename = f'../block_coordinates/block_coordinate_log_{name}'
        self.filename_csv = self.filename + '.csv'
        self.filename_png = self.filename + '.png'
        self.filename_svg = self.filename + '.svg'
        self.coordinate_list = []

        if create:
            with open(self.filename_csv, 'w') as f:
                f.write('x,y,depth\n')

    def log_coordinates(self, do_print=False):
        if len(self.coordinate_list):
            with open(self.filename_csv, 'a') as f:
                [f.write(line) for line in self.coordinate_list]
            self.coordinate_list.clear()

            if do_print:
                print('Coordinates logged successfully')

    def append_coordinates(self, xy, depth, continue_on_log=False, do_print=False):
        coordinate_str = f'{xy[0]},{xy[1]},{depth}\n'
        self.coordinate_list.append(coordinate_str)

        if do_print and not len(self.coordinate_list) % 10:
            print(f'Appended {len(self.coordinate_list)} items')

        if len(self.coordinate_list) >= 200:
            self.log_coordinates(do_print=do_print)
            return continue_on_log

        return True

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
        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(9, 7))

        # Plot x, y, and depth against index
        for i in range(3):
            axes[i].plot(range(len(coordinates)), [int(coord[i]) for coord in coordinates])
            axes[i].yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Set y-axis ticks to integers
            axes[i].set_xlabel('Time step')

        axes[0].set_title('x-ordinate over time')
        axes[0].set_ylabel('x Value')
        axes[1].set_title('y-ordinate over time')
        axes[1].set_ylabel('y Value')
        axes[2].set_title('Depth over time')
        axes[2].set_ylabel('Depth Value')

        plt.tight_layout()
        plt.savefig(self.filename_png)
        plt.savefig(self.filename_svg)
        plt.show()


if __name__ == '__main__':
    print('Input block location')
    location = input()
    coordinate_logger = CoordinateLogger(location, create=False)
    coordinate_logger.graph_coordinates()
