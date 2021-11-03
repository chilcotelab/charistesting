import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import pandas as pd
import numpy as np
from glob import glob
import os


def reverse(lst):
    return [ele for ele in reversed(lst)]


def paramvaluesfinder(param):
    """
    Reads through the log file generated by a parameter sweep and can find out what parameters were used.
    ---
    Arg:
        param (str): Either the name of a KLIP parameter (e.g. 'corr_smooth') or 'ni', which stands for number of
        injections.
    ---
    Returns:
        If param is a KLIP parameter, returns a list of the value(s) for that parameter. If param is 'ni',
        then returns a single number which is the number of injected planets.
    """
    paramline = None
    fluxes = None
    pas = None
    with open(os.path.realpath('../log.txt')) as logfile:
        for line in logfile:
            if str.lower(param) != 'ni':
                if str.lower(param) in str.lower(line):
                    paramline = line
                    break
            else:
                if str.lower('Fake Fluxes') in str.lower(line):
                    fluxes = line
                elif str.lower('Fake PAs') in str.lower(line):
                    pas = line
    if paramline is not None:
        paramline = paramline.replace(' ', '')
        for i in range(len(paramline)):
            if paramline[i] == '[':
                starting_index = i + 1
            elif paramline[i] == ']':
                final_index = i
        if str.lower(param) in ['annuli', 'subsections', 'numbasis']:
            vals = [int(val) for val in paramline[starting_index: final_index].split(',')]
        elif str.lower(param) in ['movement', 'corr_smooth']:
            vals = [float(val) for val in paramline[starting_index: final_index].split(',')]
        elif str.lower(param) in ['highpass']:
            vals = list()
            for val in paramline[starting_index: final_index].split(','):
                if str.lower(val) == 'true':
                    vals.append(True)
                elif str.lower(val) == 'false':
                    vals.append(False)
                else:
                    vals.append(float(val))
        else:
            raise ValueError(f"Sorry, this function does not currently support value finding for param {param}.")
    elif fluxes is not None and pas is not None:
        flux_vals = list()
        pa_vals = list()
        fluxes = fluxes.replace(' ', '')
        pas = pas.replace(' ', '')
        for p in [fluxes, pas]:
            for i in range(len(p)):
                if p[i] == '[':
                    starting_index = i + 1
                elif p[i] == ']':
                    final_index = i
            for val in p[starting_index: final_index].split(','):
                if p == fluxes:
                    flux_vals.append(float(val))
                elif p == pas:
                    pa_vals.append(float(val))
        vals = len(flux_vals) * len(pa_vals)

    return vals


def valuefinder(filename, param):
    """
    Looks at a filename and discerns the KLIP parameters used to produce it. Can either find a specific KLIP
    parameter and return it in the form of a string, or it can find all KLIP parameters and return them in original
    form (int/float/bool).
    ---
    Args:
        filename (str): The name of the file we are interested in.
        param (str): Either a KLIP parameter (with the caveat that numbasis='kl' and corr_smooth='smooth'), or 'all'.
    ---
    Returns:
        If param is a specific parameter, returns a singular value for that parameter. If param is 'all',
        then returns a list of all the KLIP parameters.
    """
    param = str.lower(param)
    paramlengths = {'annuli': 6, 'subsections': 11, 'movement': 8, 'spectrum': 8, 'kl': 2, 'smooth': 6, 'highpass': 8}
    if param != 'all':
        paramlength = paramlengths[param]
        startingindex = None  # will be defined soon
        for j in range(len(filename)):
            if str.lower(filename[j: j + paramlength]) == param:
                if param == 'kl':
                    startingindex = j + paramlength
                else:
                    startingindex = j - 1

        if startingindex is not None:
            if param != 'kl':
                valuelength = 0
                while startingindex >= 0 and filename[startingindex] != '_' and filename[startingindex] != '/':
                    startingindex -= 1
                    valuelength += 1
                end_index = startingindex + 1 + valuelength
                value = filename[startingindex + 1: end_index]
            else:
                end_index = startingindex + 2
                value = filename[startingindex: end_index]

        return value
    else:
        values = []
        for prm in paramlengths.keys():
            paramlength = paramlengths[prm]
            startingindex = None  # will be defined soon
            for j in range(len(filename)):
                if str.lower(filename[j: j + paramlength]) == prm:
                    if prm == 'kl':
                        startingindex = j + paramlength
                    else:
                        startingindex = j - 1

            if prm != 'kl':
                valuelength = 0
                while startingindex > 0 and filename[startingindex] != '_' and filename[startingindex] != '/':
                    startingindex -= 1
                    valuelength += 1
                end_index = startingindex + 1 + valuelength
                value = filename[startingindex + 1: end_index]
            else:
                end_index = startingindex + 2
                value = filename[startingindex: end_index]

            if prm == 'annuli' or prm == 'subsections' or prm == 'kl':
                value = int(value)
            elif prm == 'movement' or prm == 'smooth':
                value = float(value)
            elif prm == 'highpass':
                if str.lower(value) == 'true':
                    value = True
                elif str.lower(value) == 'false':
                    value = False
                else:
                    value = float(value)
            elif prm == 'spectrum':
                if str.lower(value) == 'none':
                    value = None
            values.append(value)

        return values


def roc_generator(snr_values, param1, num_injections, filepath_to_save, file_finder='*.csv', generate='plot'):
    """
    Makes an ROC curve or a table of the data that would be plotted on the ROC curve.
    ---
    Args:
        snr_values (list): SNR Values to plot
        param1: Should be tuple of form (str: name of parameter, list: values used for parameter)
        num_injections (int): Number of planets that got injected
        filepath_to_save (str): Where to save graph.
        file_finder (str): passed into glob to get all relevant files.
        generate (str): either 'plot' or 'table' -- tells it what to generate
    """
    if not (generate == 'plot' or generate == 'table'):
        raise ValueError('generate argument is invalid. must be either "plot" or "table".')
    collection = {str(val): {str(snr): list() for snr in snr_values} for val in param1[1]}
    originalwd = os.getcwd()
    os.chdir(os.path.realpath('../detections/'))
    filelist = glob(file_finder)
    for file in filelist:  # i used only to get different colors/markers on graph
        detections = pd.read_csv(file)
        val = valuefinder(file, param1[0])
        for snr in snr_values:
            detections_subset = detections[detections['SNR Value'] >= snr]
            detections_subset = detections_subset[detections_subset['Injected'] != "Science Target"]
            inj = []
            for m in detections_subset['Injected']:
                if m is True or m == "True":
                    inj.append(True)
                elif m is False or m == "False":
                    inj.append(False)
            collection[val][str(snr)].append([np.sum(inj), len(inj) - np.sum(inj)])
    if generate == 'table':
        df = pd.DataFrame(columns=['Param Value', 'SNR', 'Avg True Positives', 'Avg False Positives'])
    for i, val in enumerate(param1[1]):
        val = str(val)
        k = collection[val]
        x = []
        y = []
        for snr in snr_values:
            A = k[str(snr)]
            tp = np.sum([a[0] for a in A])
            fp = np.sum([a[1] for a in A])
            if generate == 'plot':
                y.append(tp / (num_injections * len(A)))
                x.append(fp / (num_injections * len(A)))
            else:
                tp /= len(A)
                fp /= len(A)
                newrow = {'Param Value': val, 'SNR': snr, 'Avg True Positives': tp, 'Avg False Positives': fp}
                df.append(newrow, ignore_index=True)
        if generate == 'plot':
            markers = ['.', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+',
                       'x', 'X', 'D', 'd', '|', '_']
            colors = list(mcolors.BASE_COLORS) + list(mcolors.TABLEAU_COLORS)
            plt.plot(x, y, label=val, marker=markers[i], color=colors[i])
    if generate == 'plot':
        plt.xlabel('False Positives')
        plt.ylabel('True Positives')
        plt.title(f'ROC Curve as a Function of {param1[0]}')
        plt.legend(loc='lower right')
        os.chdir(originalwd)
        plt.savefig(filepath_to_save)
    else:
        os.chdir(originalwd)
        df.to_csv(filepath_to_save, index=False)


def max_value_heatmap(param1, param2, filepath_to_save, file_finder='*.csv'):
    """
    Just shows the maximum SNR value found (i.e. SNR of HD1160)
    Args:
        param1: Should be tuple of form (str: name of parameter, list: values used for parameter)
        param2: Should be tuple of form (str: name of parameter, list: values used for parameter)
        filepath_to_save: string
        file_finder: str -- passed into glob to get all relevant (CSV) files.
    """
    originalwd = os.getcwd()
    os.chdir(os.path.realpath('../detections/'))
    fileset = glob(file_finder)
    full_data = {str(a): {str(m): list() for m in reverse(param2[1])} for a in param1[1]}
    for file in fileset:
        df = pd.read_csv(file)
        snr = df['SNR Value'].max()
        if np.isnan(snr):
            with open(f'{originalwd}/empty_detection_files.txt', 'a') as f:
                f.write(f'{file}\n')
        else:
            p1 = valuefinder(file, param1[0])
            p2 = valuefinder(file, param2[0])
            full_data[p1][p2].append(snr)
    for p1 in param1[1]:
        for p2 in param2[1]:
            p1 = str(p1)
            p2 = str(p2)
            full_data[p1][p2] = np.mean(full_data[p1][p2])
            full_data[p1][p2] = int(round(full_data[p1][p2]))
    plot_snr = []
    for p2 in param2[1]:
        plot_snr.append([full_data[str(p1)][str(p2)] for p1 in param1[1]])
    data_to_plot = pd.DataFrame(plot_snr, index=param2[1], columns=param1[1])
    sns.heatmap(data_to_plot, annot=True, linewidths=0.2, fmt='d', cbar=False)
    plt.xlabel(param1[0])
    plt.ylabel(param2[0])
    plt.title('Maximum Planet SNR Values')
    os.chdir(originalwd)
    plt.savefig(filepath_to_save)


def specific_target_heatmap(param1, param2, filepath_to_save, target_loc, file_finder='*.csv'):
    """
    Just shows the average value of a particular
    Args:
        param1: Should be tuple of form (str: name of parameter, list: values used for parameter)
        param2: Should be tuple of form (str: name of parameter, list: values used for parameter)
        filepath_to_save: string
        target_loc: list of form [X, Y], w/ position of target post-KLIP (in pixels)
        file_finder: str -- passed into glob to get all relevant (CSV) files.
    """
    originalwd = os.getcwd()
    os.chdir(os.path.realpath('../detections/'))
    fileset = glob(file_finder)
    full_data = {str(a): {str(m): list() for m in reverse(param2[1])} for a in param1[1]}
    X, Y = target_loc
    for file in fileset:
        df = pd.read_csv(file)
        specific_target_df = df[((df['x'] - X) ** 2 + (df['y'] - Y) ** 2) < 9]  # within 3 pixels
        if len(specific_target_df) == 0:
            snr = 0
        else:
            snr = list(specific_target_df['SNR Value'])[0]
        p1 = valuefinder(file, param1[0])
        p2 = valuefinder(file, param2[0])
        full_data[p1][p2].append(snr)
    for p1 in param1[1]:
        for p2 in param2[1]:
            p1 = str(p1)
            p2 = str(p2)
            full_data[p1][p2] = np.mean(full_data[p1][p2])
            full_data[p1][p2] = int(round(full_data[p1][p2]))
    plot_snr = []
    for p2 in param2[1]:
        plot_snr.append([full_data[str(p1)][str(p2)] for p1 in param1[1]])
    data_to_plot = pd.DataFrame(plot_snr, index=param2[1], columns=param1[1])
    sns.heatmap(data_to_plot, annot=True, linewidths=0.2, fmt='d', cbar=False)
    plt.xlabel(param1[0])
    plt.ylabel(param2[0])
    plt.title('Average SNR Value')
    os.chdir(originalwd)
    plt.savefig(filepath_to_save)


def mean_value_heatmap(param1, param2, num_injections, filepath_to_save, file_finder='*.csv'):
    """
    Shows mean SNR of injected planets.
    Args:
        param1: Should be tuple of form (str: name of parameter, list: values used for parameter)
        param2: Should be tuple of form (str: name of parameter, list: values used for parameter)
        num_injections: Number of fake planets injected.
        filepath_to_save: string
        file_finder: str -- passed into glob to get all relevant (CSV) files.
    """
    originalwd = os.getcwd()
    os.chdir(os.path.realpath('../detections/'))
    fileset = glob(file_finder)
    full_data = {str(a): {str(m): list() for m in param2[1]} for a in param1[1]}
    for file in fileset:
        df = pd.read_csv(file)
        injected = df[df["Injected"] == "True"]
        snrs = list(injected['SNR Value'])
        missing = [0] * (num_injections - len(injected['SNR Value']))  # treating non-detection as SNR = 0
        snr_avg = np.mean(snrs + missing)
        if np.isnan(snr_avg):
            with open(f'{originalwd}/empty_detection_files.txt', 'a') as f:
                f.write(f'{file}\n')
        else:
            p1 = valuefinder(file, param1[0])
            p2 = valuefinder(file, param2[0])
            full_data[p1][p2].append(snr_avg)
    for p1 in param1[1]:
        for p2 in param2[1]:
            p01 = str(p1)
            p02 = str(p2)
            full_data[p01][p02] = np.nanmean(full_data[p01][p02])
            full_data[p01][p02] = round(full_data[p01][p02], 2)
    plot_snr = []
    for p2 in param2[1]:
        plot_snr.append([full_data[str(p1)][str(p2)] for p1 in param1[1]])
    data_to_plot = pd.DataFrame(plot_snr, index=param2[1], columns=param1[1])
    sns.heatmap(data_to_plot, annot=True, linewidths=0.2, fmt='.2f', cbar=False)
    plt.xlabel(param1[0])
    plt.ylabel(param2[0])
    plt.title('Mean Injected Planet SNR Value')
    os.chdir(originalwd)
    plt.savefig(filepath_to_save)
