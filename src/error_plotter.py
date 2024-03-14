from enum import Enum
import csv
from statistics import mean, stdev

import matplotlib.pyplot as plt


def plot(location):
    filename = f'../error_logs/error_log_{location}'
    kp_list = ['0-2', '0-4', '0-6', '0-8']
    errors = []
    for i, kp in enumerate(kp_list):
        errors.append([])
        filename_csv = f'{filename}_{kp}.csv'
        with open(filename_csv, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    errors[i].append(row)
                    line_count += 1

    # Create a figure with 3 subplots
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(7, 5))

    # Plot x any y against timestep
    for j, kp in enumerate(kp_list):
        for i in range(2):
            print(f'kp={kp.replace("-", ".")}')
            axes[i].plot(range(len(errors[j])), [int(error[i]) for error in errors[j]],
                         label=f'kp={kp.replace("-", ".")}')

    # Format the plots
    for i in range(2):
        axes[i].set_xlabel('Time step')
        axes[i].xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Set y-axis ticks to integers
        axes[i].yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Set y-axis ticks to integers
        axes[i].axhline(0, color='red', linestyle='--')
        axes[i].legend()

    axes[0].set_title('x error over time')
    axes[0].set_ylabel('x error (px)')
    axes[1].set_title('y error over time')
    axes[1].set_ylabel('y error (px)')

    plt.tight_layout()
    plt.savefig(filename + '.png')
    plt.savefig(filename + '.svg')
    plt.show()


if __name__ == '__main__':
    print('Input block location')
    location = input()
    plot(location)
