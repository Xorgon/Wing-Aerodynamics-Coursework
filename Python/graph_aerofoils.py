# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 14:59:22 2018

@author: Elijah
"""

from matplotlib import pyplot as plt
import numpy as np
import math
import run_xfoil


def get_coords(filename="coords.txt"):
    file = open(filename)
    lines = file.readlines()
    coords = []
    for line in lines:
        line = line.strip("\n ")
        coord = line.split(" ", maxsplit=1)
        coord[0].strip(" ")
        coord[1].strip(" ")
        coords.append([float(coord[0]), float(coord[1])])
    return np.array(coords)


def plot_coords(coords, ax=None, style="-", label=None):
    coords = np.array(coords)
    if ax is None:
        plt.plot(coords[:, 0], coords[:, 1], style, label=label)
    else:
        ax.plot(coords[:, 0], coords[:, 1], style, label=label)


def get_thickness(x, coords, camber_points, ax=None, style=None):
    camber_points = np.array(camber_points)
    camber_point = [x, 0]
    camber_angle = 0

    for i in range(len(camber_points) - 1):
        c_point_1 = camber_points[i]
        c_point_2 = camber_points[i + 1]
        if camber_points[i, 0] <= x <= camber_points[i + 1, 0]:
            camber_angle = math.pi / 2 + math.atan2((c_point_2[1] - c_point_1[1]), (c_point_2[0] - c_point_1[0]))
            camber_point[1] = c_point_1[1] + (c_point_2[1] - c_point_1[1]) * (x - c_point_1[0]) / (
                c_point_2[0] - c_point_1[0])

    upper_coord = [0.5, 0.5]
    set_upper = False
    lower_coord = [0.5, -0.5]
    set_lower = False
    for i in range(len(coords) - 1):
        angle_1 = math.atan2((coords[i, 1] - camber_point[1]), (coords[i, 0] - camber_point[0]))
        angle_2 = math.atan2((coords[i + 1, 1] - camber_point[1]), (coords[i + 1, 0] - camber_point[0]))

        if angle_2 - camber_angle < 0 and angle_1 - camber_angle > 0 and math.fabs(
                        angle_2 - angle_1) < math.pi:  # Upper surface
            dif_angle_fract = math.sin(camber_angle - angle_1) / math.sin(angle_2 - angle_1)
            dif_x = coords[i + 1, 0] - coords[i, 0]
            dif_y = coords[i + 1, 1] - coords[i, 1]
            upper_coord[0] = coords[i, 0] + dif_x * dif_angle_fract
            upper_coord[1] = coords[i, 1] + dif_y * dif_angle_fract
            set_upper = True
        if angle_2 - (camber_angle - math.pi) < 0 and angle_1 - (camber_angle - math.pi) > 0 and math.fabs(
                        angle_2 - angle_1) < math.pi:  # Lower Surface
            dif_angle_fract = math.sin((camber_angle - math.pi) - angle_1) / math.sin(angle_2 - angle_1)
            dif_x = coords[i + 1, 0] - coords[i, 0]
            dif_y = coords[i + 1, 1] - coords[i, 1]
            lower_coord[0] = coords[i, 0] + dif_x * dif_angle_fract
            lower_coord[1] = coords[i, 1] + dif_y * dif_angle_fract
            set_lower = True

    if ax is not None:
        plot_coords([upper_coord, lower_coord], ax, style)

    if set_upper and set_lower:
        return math.sqrt((upper_coord[0] - lower_coord[0]) ** 2 + (upper_coord[1] - lower_coord[1]) ** 2)
    else:
        return 0


def get_mean_height(x, coords):
    lower_y = 0
    upper_y = 0
    for i in range(len(coords) - 1):
        if coords[i, 0] > x > coords[i + 1, 0]:
            x_dif = (x - coords[i, 0]) / (coords[i + 1, 0] - coords[i, 0])
            lower_y = coords[i, 1] + (coords[i + 1, 1] - coords[i, 1]) * x_dif
        if coords[i, 0] < x < coords[i + 1, 0]:
            x_dif = (x - coords[i, 0]) / (coords[i + 1, 0] - coords[i, 0])
            upper_y = coords[i, 1] + (coords[i + 1, 1] - coords[i, 1]) * x_dif
    return (lower_y + upper_y) / 2


def plot_aerofoil(coords, ax=None, style="-", label=None):
    camber_points = []

    num_camber_points = 500
    max_camber = 0
    max_camber_x = 0
    for n in range(num_camber_points):
        x = n / (num_camber_points - 1)
        y = get_mean_height(x, coords)
        camber_points.append([x, y])
        if y > max_camber:
            max_camber = y
            max_camber_x = x

    num_thickness_points = 1000
    max_thickness = 0
    max_thickness_x = 0
    for n in range(num_thickness_points):
        x = n / (num_thickness_points - 1)
        thickness = get_thickness(x, coords, camber_points)
        if thickness > max_thickness:
            max_thickness = thickness
            max_thickness_x = x

    print("Max camber = {0:.2f}% at x = {1:.2f}%".format(100 * max_camber, 100 * max_camber_x))
    print("Max thickness = {0:.2f}% at x = {1:.2f}%".format(100 * max_thickness, 100 * max_thickness_x))

    if ax is None:
        fig = plt.figure()
        fig.patch.set_facecolor('white')
        ax = fig.gca()
        ax.set_xlim((0, 1))
        ax.set_ylim((-0.5, 0.5))
    get_thickness(max_thickness_x, coords, camber_points, ax, style)
    plot_coords(coords, ax, style, label)
    plot_coords(camber_points, ax, style)


def plot_varying_beta():
    filename_suffix = "-beta-aerofoil.txt"
    start_beta = 0.01
    end_beta = 0.2
    num_betas = 25
    betas = np.arange(start_beta, end_beta, (end_beta - start_beta) / num_betas)
    max_cambers = []
    max_thicknesses = []
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlim((0, 1))
    ax.set_ylim((-0.5, 0.5))
    for beta in betas:
        coords = get_coords(str(beta) + filename_suffix)
        camber_points = []

        num_camber_points = 100
        max_camber = 0
        max_camber_x = 0
        for n in range(num_camber_points):
            x = n / (num_camber_points - 1)
            y = get_mean_height(x, coords)
            camber_points.append([x, y])
            if y > max_camber:
                max_camber = y
                max_camber_x = x

        num_thickness_points = 200
        max_thickness = 0
        for n in range(num_thickness_points):
            x = n / (num_thickness_points - 1)
            thickness = get_thickness(x, coords, camber_points)
            if thickness > max_thickness:
                max_thickness = thickness
                max_thickness_x = x

        max_cambers.append(max_camber)
        max_thicknesses.append(max_thickness)

        get_thickness(max_thickness_x, coords, camber_points, ax)
        plot_coords(coords, ax)
        plot_coords(camber_points, ax)

    fig, ax1 = plt.subplots()
    fig.patch.set_facecolor('white')
    ax1.plot(betas, max_cambers, 'r')
    ax1.set_ylabel("Maximum Camber", color='r')
    ax1.set_xlabel("$\\beta$")
    ax2 = ax1.twinx()
    ax2.plot(betas, max_thicknesses, 'b')
    ax2.set_ylabel("Maximum Thickness", color='b')


def plot_varying_epsilon():
    filename_suffix = "-epsilon-aerofoil.txt"
    start_epsilon = 0.05
    end_epsilon = 0.09
    num_epsilon = 10
    epsilons = np.arange(start_epsilon, end_epsilon, (end_epsilon - start_epsilon) / num_epsilon)
    max_cambers = []
    max_thicknesses = []
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlim((0, 1))
    ax.set_ylim((-0.5, 0.5))
    for epsilon in epsilons:
        coords = get_coords(str(epsilon) + filename_suffix)
        camber_points = []

        num_camber_points = 100
        max_camber = 0
        max_camber_x = 0
        for n in range(num_camber_points):
            x = n / (num_camber_points - 1)
            y = get_mean_height(x, coords)
            camber_points.append([x, y])
            if y > max_camber:
                max_camber = y
                max_camber_x = x

        num_thickness_points = 200
        max_thickness = 0
        for n in range(num_thickness_points):
            x = n / (num_thickness_points - 1)
            thickness = get_thickness(x, coords, camber_points)
            if thickness > max_thickness:
                max_thickness = thickness
                max_thickness_x = x

        max_cambers.append(max_camber)
        max_thicknesses.append(max_thickness)

        get_thickness(max_thickness_x, coords, camber_points, ax)
        plot_coords(coords, ax)
        plot_coords(camber_points, ax)

    fig, ax1 = plt.subplots()
    fig.patch.set_facecolor('white')
    ax1.plot(epsilons, max_cambers, 'r')
    ax1.set_ylabel("Maximum Camber", color='r')
    ax1.set_xlabel("$\\epsilon$")
    ax2 = ax1.twinx()
    ax2.plot(epsilons, max_thicknesses, 'b')
    ax2.set_ylabel("Maximum Thickness", color='b')


def naca_coords_to_program_coords(naca_coords):
    coords = []
    for i in range(len(naca_coords)):
        coords.append(naca_coords[len(naca_coords) - 1 - i])
    coords = np.array(coords)
    return coords


def plot_cl_error(filename="dpan-results.txt"):
    file = open(filename, "r")
    lines = file.readlines()
    logns = []
    errors = []
    cl_theory = float(lines[0].split(",")[1])
    for line in lines[1:-1]:
        split = line.split(",")
        N = int(split[0])
        error = float(split[1]) - cl_theory
        logns.append(math.log(1 / N))
        errors.append(math.log(error))

    x = np.arange(logns[0], logns[-1], -0.001)
    y = np.add(8.9, np.multiply(3.2, x))

    fig = plt.figure()
    fig.patch.set_facecolor('white')
    ax = fig.gca()
    ax.plot(logns, errors, "k-", label="Actual")
    ax.plot(x, y, "k--", label="Best Fit (gradient = 3.2)")
    ax.set_xlabel("log(1/N)")
    ax.set_ylabel("log(Error)")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc=4)


def plot_xfoil_cl_cd(filename):
    alphas, cls, cds = run_xfoil.load_xfoil_alpha_cl_cd_data(filename)
    fig, ax1 = plt.subplots()
    fig.patch.set_facecolor('white')
    ax1.plot(alphas, cls, 'r')
    ax1.set_ylabel("$C_L$", color='r')
    ax1.set_xlabel("$\\alpha$")
    ax2 = ax1.twinx()
    ax2.plot(alphas, cds, 'b')
    ax2.set_ylabel("$C_D$", color='b')


def plot_aerofoil_polar_comparison(filename1, filename2):
    alphas1, cls1, cds1 = run_xfoil.load_xfoil_alpha_cl_cd_data(filename1)
    alphas2, cls2, cds2 = run_xfoil.load_xfoil_alpha_cl_cd_data(filename2)
    fig, ax1 = plt.subplots()
    fig.patch.set_facecolor('white')
    ax1.plot(alphas1, cls1, 'r', label="Karman-Trefftz")
    ax1.plot(alphas2, cls2, 'r--', label="NACA 1511")
    ax1.set_ylabel("$C_L$", color='r')
    ax1.set_xlabel("$\\alpha$")
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels, loc=2)
    ax2 = ax1.twinx()
    ax2.plot(alphas1, cds1, 'b')
    ax2.plot(alphas2, cds2, 'b--')
    ax2.set_ylabel("$C_D$", color='b')


def plot_aerofoil_transition_comparison(filename1, filename2):
    alphas1, xtrs1 = run_xfoil.load_xfoil_alpha_transition_data(filename1)
    alphas2, xtrs2 = run_xfoil.load_xfoil_alpha_transition_data(filename2)
    fig, ax1 = plt.subplots()
    fig.patch.set_facecolor('white')
    ax1.plot(alphas1, xtrs1, 'k', label="Karman-Trefftz")
    ax1.plot(alphas2, xtrs2, 'k--', label="NACA 1511")
    ax1.set_ylabel("Upper side transition point (x/c)")
    ax1.set_xlabel("$\\alpha$")
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels)


def plot_aerofoil_separation_comparison(ktreff_filename, naca_number, rerun=True):
    alphas = range(30)
    separation_points_1 = []
    separation_points_2 = []
    if rerun:
        run_xfoil.run_xfoil_alphas_cp_profile(ktreff_filename, "ktreff_pressure_output", alphas)
        run_xfoil.run_xfoil_naca_alphas_cp_profile(naca_number, "naca_pressure_output", alphas)
    for alpha in alphas:
        output = run_xfoil.calculate_separation_point("ktreff_pressure_output-" + str(alpha) + ".txt")
        if output:
            separation_points_1.append(output)
        else:
            separation_points_1.append(None)

        output = run_xfoil.calculate_separation_point("naca_pressure_output-" + str(alpha) + ".txt")
        if output:
            separation_points_2.append(output)
        else:
            separation_points_2.append(None)

    fig, ax = plt.subplots()
    fig.patch.set_facecolor('white')
    ax.plot(alphas, separation_points_1, 'k', label="Karman-Trefftz")
    ax.plot(alphas, separation_points_2, 'k--', label="NACA 1511")
    ax.set_ylabel("Seperation point (x/c)")
    ax.set_xlabel("$\\alpha$")
    ax.set_xlim((15, 30))
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)


def plot_aerofoil_shape_comparison():
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    ax = fig.gca()
    ax.set_xlim((0, 1))
    ax.set_ylim((-0.1, 0.1))
    plot_aerofoil(get_coords("coords.txt"), ax, "k-", "Karman-Trefftz")
    plot_aerofoil(naca_coords_to_program_coords(get_coords("NACA_coords.txt")), ax, "k--", "NACA")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)


# plot_varying_beta()
# plot_varying_epsilon()
plot_aerofoil_shape_comparison()
plot_aerofoil_polar_comparison("ktreff_polar.txt", "NACA_1511_polar.txt")
plot_aerofoil_transition_comparison("ktreff_polar.txt", "NACA_1511_polar.txt")
plot_aerofoil_separation_comparison("coords.txt", 1511, False)
plot_cl_error()
plt.show()
