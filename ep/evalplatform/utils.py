import csv
import os
import re
import shlex
import stat
import sys
from functools import reduce

import numpy as np

try:
    import configparser as ConfigParser
except:
    import ConfigParser

from ep.evalplatform import debug

CONFIG_FILENAME = "evaluation.ini"

# Name suffixes
SUMMARY_SUFFIX = ".eval.summary.txt"
SEGPLOTDATA_SUFFIX = ".eval.segplot.txt"
SEGPLOT_SUFFIX = ".eval.segplot.png"
SEGPLOT_SUFFIX2 = ".eval.segplot.svg"
SEGDETAILS_SUFFIX = ".eval.segdetails.txt"
TRACKPLOTDATA_SUFFIX = ".eval.trackplot.txt"
TRACKPLOT_SUFFIX = ".eval.trackplot.png"
TRACKPLOT_SUFFIX2 = ".eval.trackplot.svg"
TRACKDETAILS_SUFFIX = ".eval.trackdetails.txt"
LONGTRACKDETAILS_SUFFIX = ".eval.longtrackdetails.txt"

ALL_SUFFIXES = [SUMMARY_SUFFIX, SEGPLOTDATA_SUFFIX, SEGPLOT_SUFFIX, SEGPLOT_SUFFIX2, SEGDETAILS_SUFFIX,
                TRACKPLOTDATA_SUFFIX, TRACKPLOT_SUFFIX, TRACKPLOT_SUFFIX2, TRACKDETAILS_SUFFIX, LONGTRACKDETAILS_SUFFIX]

SEG_DRAWING_FOLDER = "Segmentation details"
TRACK_DRAWING_FOLDER = "Tracking details"
LONG_DRAWING_FOLDER = "Long tracking details"
ALL_DIRECTORIES = [SEG_DRAWING_FOLDER, TRACK_DRAWING_FOLDER, LONG_DRAWING_FOLDER]


def reduce_plus(ls):
    return reduce(lambda a, b: a + b, ls)


def slice_to_array(slice):
    return np.array(slice.indices(1000000))[:2]


def slices_intersection(slices1, slices2):
    # Fast non-zero intersection check.
    if slices1[0].start > slices2[0].stop or slices1[1].start > slices2[1].stop or \
            slices2[0].start > slices1[0].stop or slices2[1].start > slices1[1].stop:
        return None
    ys1 = slice_to_array(slices1[0])
    xs1 = slice_to_array(slices1[1])
    ys2 = slice_to_array(slices2[0])
    xs2 = slice_to_array(slices2[1])

    slice_y = slice(max(ys1[0], ys2[0]), min(ys1[1], ys2[1]))
    slice_x = slice(max(xs1[0], xs2[0]), min(xs1[1], xs2[1]))
    return slice_y, slice_x


def slices_relative(slices_origin, slices_absolute):
    ys1 = slice_to_array(slices_origin[0])
    xs1 = slice_to_array(slices_origin[1])
    ys2 = slice_to_array(slices_absolute[0])
    xs2 = slice_to_array(slices_absolute[1])

    ys2 -= ys1[0]
    xs2 -= xs1[0]

    ys2 = np.maximum(ys2, 0)
    xs2 = np.maximum(xs2, 0)

    slice_y = slice(*ys2)
    slice_x = slice(*xs2)
    return slice_y, slice_x


def slices_arithmetic(slices1, slices2, mult1, mult2):
    ys1 = slice_to_array(slices1[0])
    xs1 = slice_to_array(slices1[1])
    ys2 = slice_to_array(slices2[0])
    xs2 = slice_to_array(slices2[1])

    slice_y = slice(*(ys1 * mult1 + ys2 * mult2))
    slice_x = slice(*(xs1 * mult1 + xs2 * mult2))
    return slice_y, slice_x


def get_config_file_path():
    """
    In case that cwd is not in the same directory that config file. Check if file is where the executed script is.
    """
    chosen_path = CONFIG_FILENAME
    if not os.path.isfile(CONFIG_FILENAME):
        chosen_path = os.path.join(os.path.dirname(sys.argv[0]), CONFIG_FILENAME)

    if not os.path.isfile(chosen_path):
        print("Config file: {0} does not exist.".format(chosen_path))
    return chosen_path


CONFIG_FILE = get_config_file_path()


def split_path(path):
    if os.path.split(path)[0] != path and os.path.split(path)[0] != '':
        (dir, file) = os.path.split(path)
        return split_path(dir) + [file]
    return [path]


def ensure_directory_in(filepath, directory_name):
    """Check is in the directory of the given filepath exists directory of the given name, if not it is created.
    
    Returns::
        ensured_directory_path - <path>\directory_name
    """

    ensured_directory_path = os.path.join(os.path.split(filepath)[0], directory_name)
    if not os.path.exists(ensured_directory_path):
        os.makedirs(ensured_directory_path)
    return ensured_directory_path


def determine_output_filepath(filepath, output_path):
    if os.path.isabs(filepath) == True:
        if os.path.isabs(output_path) == True:
            # just put it in the given folder
            components = split_path(filepath)
            return os.path.join(output_path, os.path.join(*components[-2:]))
        else:
            # let output be one level up 
            components = split_path(filepath)
            return os.path.join(os.path.join(*components[:-1]), output_path, os.path.join(*components[-1:]))
    return os.path.join(output_path, filepath)


def distance(p0, p1):
    return ((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2) ** 0.5


def get_trailing_order(text, is_path=False):
    if is_path:
        text = os.path.splitext(text)[0]
    reversed_name = text[::-1]
    m = re.search("\D", reversed_name + " ")
    number = reversed_name[:m.start()][::-1]
    return number if number else text


def parse_file_order(order_object):
    if isinstance(order_object, str):
        try:
            order_normalized = int(order_object)
        except ValueError:
            order_normalized = order_object
    elif isinstance(order_object, int):
        order_normalized = int(order_object)
    else:
        raise Exception("Order is neither str nor int: " + str(order_object))

    return order_normalized


def setup_ploting_terminal(terminal_type, data_points, wide_plot):
    if wide_plot:
        good_width = max(1200, int(1200 / 80 * len(data_points)))
    else:
        good_width = 1200

    if terminal_type != "svg":
        term_set = "pngcairo size {0},800 linewidth 2 font \\\",22\\\"".format(good_width)
        output_file_extension = ".png"
    else:
        term_set = "svg size {0},800 linewidth 2 font \\\",22\\\"".format(good_width)
        output_file_extension = ".svg"
    return term_set, output_file_extension, ""


def package_path(filename, quoted=1):
    """
    Return relative (from cwd) path to file in package folder.
    In quotes.
    """
    name = os.path.join(os.path.dirname(__file__), filename)
    if quoted:
        return "\"" + name + "\""
    return name


def open_csv(path, mode):
    try:
        return open(path, mode, newline='')
    except TypeError:
        return open(path, mode + "b")


def read_from_csv(path):
    """
    Args::
        path - full path of the existing csv file
    Returns::
        (headers,[record])
    """
    opened_file = open_csv(path, "r")
    lines = list(csv.reader(opened_file))
    opened_file.close()
    return (lines[0], lines[1:])


def write_to_csv(headers, records, path):
    """
    Args::
        headers - list of header names
        records - list of records where every record is a list
        path - full path of the created csv file
    """
    opened_file = open_csv(path, "w")
    cw = csv.writer(opened_file)
    cw.writerows([headers] + sorted(records))
    opened_file.close()


def write_to_file(data_sets, path):
    """
    data_set: [(f,val)] -> 1 2\n2 5\n3 8
    data_sets: [data_set] -> data1\n\n\ndata2
    """
    data = map(lambda dataset: "\n".join(["\"" + str(f) + "\" " + str(val) for (f, val) in dataset]), data_sets)
    joined = "\n\n\n".join(data)
    opened_file = open(path, "w")
    opened_file.writelines(joined)
    opened_file.close()


def read_from_file(path):
    """
    Reads plot file
    Returns data sets
    data_set: [(f,val)] -> 1 2\n2 5\n3 8
    data_sets: [data_set] -> data1\n\n\ndata2
    """
    opened_file = open(path, "rU")
    joined = opened_file.read()
    opened_file.close()

    datasets = [[shlex.split(line) for line in dataset.split("\n")] for dataset in joined.split("\n\n\n")]
    return [[(tokens[0], float(tokens[1])) for tokens in dataset] for dataset in datasets]


def read_ini(file_path, section, key):
    """
    Reads value from ini file.
    """
    config = ConfigParser.ConfigParser()
    config.read(file_path)
    if config.has_option(section, key):
        return config.get(section, key)
    return ''


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


class EvaluationDebug(debug.DebugCenter):
    category_levels = {"Result": 0.1, "Error": 1, "Warning": 2, "Info": 3, "Progress": 3.1, "Tech": 3.2, "Trace": 4.1}
    possible_categories = set(category_levels.keys())

    chosen_level = 3
    chosen_categories = set()
    debug_on = True
    log_to_file = False

    def configure(self, ini_file):
        if read_ini(ini_file, 'debug', 'verbosity') != '':
            self.chosen_level = float(read_ini(ini_file, 'debug', 'verbosity'))

        if read_ini(ini_file, 'debug', 'show') != '':
            self.debug_on = bool(read_ini(ini_file, 'debug', 'show'))

        if read_ini(ini_file, 'debug', 'logtofile') != '':
            self.log_to_file = bool(read_ini(ini_file, 'debug', 'logtofile'))


debug_center = EvaluationDebug()
