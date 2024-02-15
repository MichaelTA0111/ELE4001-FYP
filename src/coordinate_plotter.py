from enum import Enum
import csv
from statistics import mean, stdev

import matplotlib.pyplot as plt


class PlotData(Enum):
    TOP = (4, 'top')
    MID = (3, 'mid')
    HIGH = (4, 'high')
    ALL = (11, 'all')

    def __init__(self, num_files, partial_filename):
        self.num_files = num_files
        self.base_filename = f'../block_coordinates/block_coordinate_log_{partial_filename}'


def parse_data(filename):
    coords = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                coords.append(row)
                line_count += 1

    x = [int(coord[0]) for coord in coords]
    y = [int(coord[1]) for coord in coords]
    depth = [int(coord[2]) for coord in coords]

    return x, y, depth


def plot(plot_data):
    x_mean = []
    x_std = []
    y_mean = []
    y_std = []
    depth_mean = []
    depth_std = []

    for i in range(1, plot_data.num_files+1):
        x, y, depth = parse_data(f'{plot_data.base_filename}{i}.csv')
        x_mean.append(mean(x))
        x_std.append(stdev(x))
        y_mean.append(mean(y))
        y_std.append(stdev(y))
        depth_mean.append(mean(depth))
        depth_std.append(stdev(depth))

    # Create a figure with 3 subplots
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 8))

    # Plot x, y, and depth against index
    for i in range(3):
        axes[i].xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Set y-axis ticks to integers
        axes[i].yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Set y-axis ticks to integers
        axes[i].set_xlabel('Position')

    axes[0].errorbar(range(1, plot_data.num_files+1), x_mean, x_std,
                     linestyle='None', marker='x', label='x', capsize=5, elinewidth=1)
    axes[0].set_title('x Value against Position')
    axes[0].set_ylabel('x Value')

    axes[1].errorbar(range(1, plot_data.num_files+1), y_mean, y_std,
                     linestyle='None', marker='x', label='y', capsize=5, elinewidth=1)
    axes[1].set_title('y Value against Position')
    axes[1].set_ylabel('y Value')

    axes[2].errorbar(range(1, plot_data.num_files+1), depth_mean, depth_std,
                     linestyle='None', marker='x', label='Depth', capsize=5, elinewidth=1)
    axes[2].set_title('Depth against Position')
    axes[2].set_ylabel('Depth')

    plt.tight_layout()
    plt.savefig(f'{plot_data.base_filename}.png')
    plt.savefig(f'{plot_data.base_filename}.svg')
    plt.show()


def plot_all():
    x_mean = []
    x_std = []
    y_mean = []
    y_std = []
    depth_mean = []
    depth_std = []

    for plot_data in PlotData:
        if plot_data is PlotData.ALL:
            continue

        for i in range(1, plot_data.num_files+1):
            x, y, depth = parse_data(f'{plot_data.base_filename}{i}.csv')
            x_mean.append(mean(x))
            x_std.append(stdev(x))
            y_mean.append(mean(y))
            y_std.append(stdev(y))
            depth_mean.append(mean(depth))
            depth_std.append(stdev(depth))

    # Create a figure with 3 subplots
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 8))

    # Plot x, y, and depth against index
    for i in range(3):
        axes[i].xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Set y-axis ticks to integers
        axes[i].yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Set y-axis ticks to integers
        axes[i].set_xlabel('Position')

    axes[0].errorbar(range(1, PlotData.ALL.num_files+1), x_mean, x_std,
                     linestyle='None', marker='x', label='x', capsize=5, elinewidth=1)
    axes[0].set_title('x Value against Position')
    axes[0].set_ylabel('x Value')

    axes[1].errorbar(range(1, PlotData.ALL.num_files+1), y_mean, y_std,
                     linestyle='None', marker='x', label='y', capsize=5, elinewidth=1)
    axes[1].set_title('y Value against Position')
    axes[1].set_ylabel('y Value')

    axes[2].errorbar(range(1, PlotData.ALL.num_files+1), depth_mean, depth_std,
                     linestyle='None', marker='x', label='Depth', capsize=5, elinewidth=1)
    axes[2].set_title('Depth against Position')
    axes[2].set_ylabel('Depth')

    plt.tight_layout()
    plt.savefig(f'{PlotData.ALL.base_filename}.png')
    plt.savefig(f'{PlotData.ALL.base_filename}.svg')
    plt.show()


if __name__ == '__main__':
    plot(PlotData.TOP)
    plot(PlotData.MID)
    plot(PlotData.HIGH)
    plot_all()
