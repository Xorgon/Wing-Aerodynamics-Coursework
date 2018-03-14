import re
import os


def load_xfoil_alpha_cl_cd_data(filename):
    file = open(filename, "r")
    lines = file.readlines()
    alphas = []
    cls = []
    cds = []
    for line in lines:
        data_line = re.match(
            "\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)",
            line)
        if data_line:
            alphas.append(float(data_line.group(1)))
            cls.append(float(data_line.group(2)))
            cds.append(float(data_line.group(3)))
    return alphas, cls, cds


def load_xfoil_alpha_transition_data(filename):
    file = open(filename, "r")
    lines = file.readlines()
    alphas = []
    xtrs = []
    for line in lines:
        data_line = re.match(
            "\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)",
            line)
        if data_line:
            alphas.append(float(data_line.group(1)))
            xtrs.append(float(data_line.group(6)))
    return alphas, xtrs


def run_xfoil_alphas_cp_profile(aerofoil_filename, output_filename_prefix, alphas):
    print("Running XFOIL...")
    commands_in = open("commands.in", "w")
    command = "load " + aerofoil_filename + "\n\n" + \
              "ppar\nN\n160\n\n\n" + \
              "oper\n" + \
              "visc " + str(50000000) + "\n" + \
              "iter\n" + \
              "5000\n"
    for alpha in alphas:
        command += "Alfa " + str(alpha) + "\n" + "CPWR " + output_filename_prefix + "-" + str(alpha) + ".txt" + "\n"

    command += "\nquit\n"
    commands_in.write(command)
    commands_in.close()
    command = 'xfoil.exe < commands.in'
    os.system(command)

def run_xfoil_naca_alphas_cp_profile(naca_number, output_filename_prefix, alphas):
    print("Running XFOIL...")
    commands_in = open("commands.in", "w")
    command = "NACA " + str(naca_number) + "\n\n" + \
              "ppar\nN\n160\n\n\n" + \
              "oper\n" + \
              "visc " + str(50000000) + "\n" + \
              "iter\n" + \
              "5000\n"
    for alpha in alphas:
        command += "Alfa " + str(alpha) + "\n" + "CPWR " + output_filename_prefix + "-" + str(alpha) + ".txt" + "\n"

    command += "\nquit\n"
    commands_in.write(command)
    commands_in.close()
    command = 'xfoil.exe < commands.in'
    os.system(command)


def calculate_separation_point(pressure_filename):
    if not os.path.exists(pressure_filename):
        return False
    file = open(pressure_filename)
    lines = file.readlines()
    last_cp = None
    last_delta_cp = None
    last_x = 1
    for line in lines:
        data_line = re.match("\s*(-?\d+\.\d+)\s*(-?\d+\.\d+)\s*(-?\d+\.\d+)", line)
        if data_line:
            x = float(data_line.group(1))
            cp = float(data_line.group(3))
            if last_cp and last_delta_cp:
                delta_cp = cp - last_cp
                if delta_cp * last_delta_cp < 0:  # Change of sign
                    return x
                last_delta_cp = delta_cp
            elif last_cp:
                last_delta_cp = cp - last_cp
            last_cp = cp
            if x < 0.25:  # Approaching the leading edge.
                return False
