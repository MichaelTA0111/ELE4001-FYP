import csv
import matplotlib.pyplot as plt


class ErrorLogger:
    def __init__(self, name, create=True):
        self.filename = f'../error_logs/error_log_{name}'
        self.filename_csv = self.filename + '.csv'
        self.filename_png = self.filename + '.png'
        self.filename_svg = self.filename + '.svg'
        self.error_list = []

        if create:
            with open(self.filename_csv, 'w') as f:
                f.write('x,y\n')

    def log_errors(self, do_print=False):
        if len(self.error_list):
            with open(self.filename_csv, 'a') as f:
                [f.write(line) for line in self.error_list]

            self.error_list.clear()

            if do_print:
                print('Errors logged successfully')

    def append_errors(self, x, y, continue_on_log=False, do_print=False):
        error_str = f'{x},{y}\n'
        self.error_list.append(error_str)

        if do_print and not len(self.error_list) % 10:
            print(f'Appended {len(self.error_list)} items')

        if len(self.error_list) >= 200:
            self.log_errors(do_print=do_print)
            return continue_on_log

        return True

    def graph_errors(self):
        errors = []
        print()
        with open(self.filename_csv, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    errors.append(row)
                    line_count += 1

        # Create a figure with 3 subplots
        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(7, 5))

        # Plot x, y, and depth against index
        for i in range(2):
            axes[i].plot(range(len(errors)), [int(error[i]) for error in errors])
            axes[i].set_xlabel('Time step')
            axes[i].xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Set y-axis ticks to integers
            axes[i].yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Set y-axis ticks to integers
            axes[i].axhline(0, color='red', linestyle='--')

        axes[0].set_title('x error over time')
        axes[0].set_ylabel('x error (px)')
        axes[1].set_title('y error over time')
        axes[1].set_ylabel('y error (px)')

        plt.tight_layout()
        plt.savefig(self.filename_png)
        plt.savefig(self.filename_svg)
        plt.show()


if __name__ == '__main__':
    print('Input block location and K_p')
    location = input()
    error_logger = ErrorLogger(location, create=False)
    error_logger.graph_errors()
