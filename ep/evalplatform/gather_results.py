import shutil

from PIL import Image

from ep.evalplatform.create_report import create_report, create_sensible_report
from ep.evalplatform.plotting import Plotter
from ep.evalplatform.utils import *

images_sufixes = [SEGPLOT_SUFFIX, TRACKPLOT_SUFFIX]
SUMMARY_GNUPLOT_FILE = "plot_summary.plt"
terminal_type = "png"


def join2(path):
    border = 5
    imA = Image.open(os.path.join(path, "M1.png"))
    imB = Image.open(os.path.join(path, "M2.png"))
    image_size = imA.size
    half_size = (image_size[0] // 2, image_size[1] // 2)

    imA = imA.resize(half_size, Image.ANTIALIAS)
    imB = imB.resize(half_size, Image.ANTIALIAS)

    merged = Image.new('RGB', (2 * border + image_size[0], 2 * border + half_size[1]))
    merged.paste(imA, (border, border))
    merged.paste(imB, (border + half_size[0], border))

    merged.save(os.path.join(path, "Glued.png"))


def join4(path):
    border = 5
    imA = Image.open(os.path.join(path, "M1.png"))
    imB = Image.open(os.path.join(path, "M2.png"))
    imC = Image.open(os.path.join(path, "M3.png"))
    imD = Image.open(os.path.join(path, "M4.png"))
    image_size = imA.size
    half_size = (image_size[0] // 2, image_size[1] // 2)

    imA = imA.resize(half_size, Image.ANTIALIAS)
    imB = imB.resize(half_size, Image.ANTIALIAS)
    imC = imC.resize(half_size, Image.ANTIALIAS)
    imD = imD.resize(half_size, Image.ANTIALIAS)

    merged = Image.new('RGB', (2 * border + half_size[0] * 2, 2 * border + half_size[1] * 2))
    merged.paste(imA, (border, border))
    merged.paste(imB, (border + half_size[0], border))
    merged.paste(imC, (border, border + half_size[1]))
    merged.paste(imD, (border + half_size[0], border + half_size[1]))

    merged.save(os.path.join(path, "Glued.png"))


def join6(path):
    border = 5
    imA = Image.open(os.path.join(path, "M1.png"))
    imB = Image.open(os.path.join(path, "M2.png"))
    imC = Image.open(os.path.join(path, "M3.png"))
    imD = Image.open(os.path.join(path, "M4.png"))
    imE = Image.open(os.path.join(path, "M5.png"))
    if os.path.isfile(os.path.join(path, "M6.png")):
        imF = Image.open(os.path.join(path, "M6.png"))
    image_size = imA.size
    half_size = (image_size[0] // 2, image_size[1] // 2)

    imA = imA.resize(half_size, Image.ANTIALIAS)
    imB = imB.resize(half_size, Image.ANTIALIAS)
    imC = imC.resize(half_size, Image.ANTIALIAS)
    imD = imD.resize(half_size, Image.ANTIALIAS)
    imE = imE.resize(half_size, Image.ANTIALIAS)
    if os.path.isfile(os.path.join(path, "M6.png")):
        imF = imF.resize(half_size, Image.ANTIALIAS)

    merged = Image.new('RGB', (2 * border + half_size[0] * 3, 2 * border + half_size[1] * 2), "white")
    merged.paste(imA, (border, border))
    merged.paste(imB, (border + half_size[0], border))
    merged.paste(imC, (border + half_size[0] * 2, border))
    merged.paste(imD, (border, border + half_size[1]))
    merged.paste(imE, (border + half_size[0], border + half_size[1]))
    if os.path.isfile(os.path.join(path, "M6.png")):
        merged.paste(imF, (border + half_size[0] * 2, border + half_size[1]))

    merged.save(os.path.join(path, "Glued.png"))


imageglue_functions = {2: join2, 4: join4, 6: join6}


def read_algorithm_name(summary_path):
    summary_file = open(summary_path, "rU")
    linia = summary_file.readlines()[0]
    summary_file.close()
    return linia[len("Algorithm: "):].strip()


def check_existance(files, filter, get_path=None):
    existing_files = []
    for file in files:
        get_path = get_path or (lambda x: x)
        file_path = get_path(file)
        if os.path.isfile(file_path) == 0:
            debug_center.show_in_console(None, "Warning", "".join(["WARNING: ", "File don't exist: " + file_path]))
        else:
            existing_files.append(file)
    if filter == 0:
        return files
    return existing_files


def run_show_results(showSuccess, showFailed, result):
    if result == 0:
        debug_center.show_in_console(None, "Info", showSuccess)
    else:
        debug_center.show_in_console(None, "Error", showFailed)


def create_additional_plots(title, name_data_paths, set_number, output_name):
    """
    @param set_number: first element is 0
    """
    try:
        if not name_data_paths:
            return -1

        if len(name_data_paths) > 50:
            debug_center.show_in_console(None, "Warning",
                                         "WARNING: Too many plots given, merged plot would not make any sense.")
            return -1

        # Extract data from all the algorithms.
        name_data = [(name, read_from_file(path)) for (name, path) in name_data_paths]

        # Create data for the plot.
        names, algo_datasets = zip(*name_data)
        datasets = [datasets[set_number] for datasets in algo_datasets]

        tmp_file = "create_additional_plots.tmp"
        write_to_file(datasets, tmp_file)

        plt_filename = package_path(SUMMARY_GNUPLOT_FILE, 0)
        with Plotter(terminal_type, plt_filename, title) as plotter:
            debug_center.show_in_console(None, "Progress", "".join(["Ploting " + output_name + "..."]))
            plotter.setup_ploting_area(wide_plots, datasets[0])
            plotter.use_generic_plots(names)
            plotter.plot_it(tmp_file, output_name)

        debug_center.show_in_console(None, "Progress", "".join(["Ploting done..."]))

        # Clean up the mess
        os.remove(tmp_file)
        return 0

    except IOError as e:
        debug_center.show_in_console(None, "Error", ("ERROR: Could not create cross plot: {}".format(e)))
        return -1


def merge_txt(file_paths, output):
    results = []
    for file in file_paths:
        file = open(file, "rU")
        results.append(file.readlines())
        file.close()
    merged_results = "\n\n".join(["".join(res) for res in results])

    file = open(output, "w")
    file.write(merged_results)
    file.close()


def merge_images(images_paths, results_folder, output):
    if len(images_paths) == 0:
        debug_center.show_in_console(None, "Error", "".join(["ERROR: ", "No plots given"]))
        return -1
    elif len(images_paths) == 1:
        debug_center.show_in_console(None, "Error",
                                     "".join(["ERROR: ", "Too few plots (2 required): ", str(len(images_paths))]))
        return -1
    elif len(images_paths) == 3:
        debug_center.show_in_console(None, "Warning", "".join(
            ["WARNING: ", "Too many plots given (2 expected): ", str(len(images_paths))]))
        debug_center.show_in_console(None, "Warning", "".join(["WARNING: ", "Only first 2 are considered."]))
        images_paths = images_paths[:2]
    elif len(images_paths) == 5:
        debug_center.show_in_console(None, "Warning", "".join(
            ["WARNING: ", "Too many plots given (4 expected): ", str(len(images_paths))]))
        debug_center.show_in_console(None, "Warning", "".join(["WARNING: ", "Only first 4 are considered."]))
        images_paths = images_paths[:4]
    elif len(images_paths) > 6:
        debug_center.show_in_console(None, "Warning", "".join(
            ["WARNING: ", "Too many plots given (6 expected): ", str(len(images_paths))]))
        debug_center.show_in_console(None, "Warning", "".join(["WARNING: ", "Only first 6 are considered."]))
        images_paths = images_paths[:6]

    for i in range(len(images_paths)):
        shutil.copy(images_paths[i], os.path.join(results_folder, "M" + str(i + 1) + ".png"))

    # join images pipeline
    try:
        spaces = len(images_paths)
        imageglue_functions[spaces](results_folder)
        shutil.move(os.path.join(results_folder, "Glued.png"), output)
    except Exception as e:
        debug_center.show_in_console(None, "Error",
                                     "ERROR: Could not run PIL to merge plots: {0} {1}".format(sys.exc_info()[0], e))
        return -1

    for i in range(len(images_paths)):
        os.remove(os.path.join(results_folder, "M" + str(i + 1) + ".png"))

    return 0


def run_script(args):
    global terminal_type, wide_plots

    if len(args) % 2 == 0 and len(args) < 4:
        print("".join(["Wrong number (" + str(len(args) - 1) + ") of arguments (1+2(1+k) required)."]))
        print(args)
        print("".join(["Program usage: gather_results.py <results_folder> [<algorithm_subpath> <algorithm_name>]x+"]))
    else:
        debug_center.configure(CONFIG_FILE)

        if read_ini(CONFIG_FILE, 'plot', 'terminal') != '':
            terminal_type = read_ini(CONFIG_FILE, 'plot', 'terminal').strip()
        if read_ini(CONFIG_FILE, 'plot', 'wideplots') != '':
            wide_plots = bool(int(read_ini(CONFIG_FILE, 'plot', 'wideplots')))

        algorithm_number = (len(args) - 1) // 2

        results_folder = args[1]
        algorithm_results = []
        for i in range(algorithm_number):
            algorithm_results.append((args[2 + i * 2], args[2 + i * 2 + 1]))

        # Calculate image paths and check existance
        summaries_paths = []
        algorithms_surname = []  # now taken from summary files
        images_paths = []
        segmentation_data_paths = []
        tracking_data_paths = []
        for (algo_results, algo_name) in algorithm_results:
            summary_path = os.path.join(results_folder, algo_results, algo_name + SUMMARY_SUFFIX)
            segmentation_data_path = os.path.join(results_folder, algo_results, algo_name + SEGPLOTDATA_SUFFIX)
            tracking_data_path = os.path.join(results_folder, algo_results, algo_name + TRACKPLOTDATA_SUFFIX)
            result_paths = [os.path.join(results_folder, algo_results, algo_name + sufix) for sufix in images_sufixes]

            # we require summary file for algorithm name
            if check_existance([summary_path], 1):
                algorithms_surname.append(read_algorithm_name(summary_path))
                summaries_paths.append(summary_path)
                segmentation_data_paths.append(segmentation_data_path)
                tracking_data_paths.append(tracking_data_path)
                images_paths += result_paths

        summaries_paths = check_existance(summaries_paths, 1)
        images_paths = check_existance(images_paths, 1)
        segmentation_data = check_existance(zip(algorithms_surname, segmentation_data_paths), 1, lambda x: x[1])
        tracking_data = check_existance(zip(algorithms_surname, tracking_data_paths), 1, lambda x: x[1])

        debug_center.show_in_console(None, "Progress", "Merging files...")

        # Merge summaries
        merge_txt(summaries_paths, os.path.join(results_folder, "Summary.txt"))
        debug_center.show_in_console(None, "Progress", "Summaries merged")

        # Produce additional report
        create_report(os.path.join(results_folder, "Summary.txt"), 4, "csv", os.path.join(results_folder, "Report.csv"))
        create_sensible_report(os.path.join(results_folder, "Summary.txt"), 4,
                               os.path.join(results_folder, "Sensible Report.csv"))
        debug_center.show_in_console(None, "Progress", "CSV summary created")

        # Merge images (using Image module)
        if terminal_type != "svg":
            result_merged_segmentation = merge_images([p for p in images_paths if p.endswith(SEGPLOT_SUFFIX)],
                                                      results_folder,
                                                      os.path.join(results_folder, "Plot_segmentation.png"))
            run_show_results("Segmentation plots merged", "Segmentation plots NOT merged", result_merged_segmentation)

            result_merged_tracking = merge_images([p for p in images_paths if p.endswith(TRACKPLOT_SUFFIX)],
                                                  results_folder, os.path.join(results_folder, "Plot_tracking.png"))
            run_show_results("Tracking plots merged", "Tracking plots NOT merged", result_merged_tracking)
        else:
            debug_center.show_in_console(None, "Info",
                                         "Skipping merging plots as it is unavailable for '" + terminal_type + "' plotting terminal.")

        debug_center.show_in_console(None, "Progress", "...merging done")

        debug_center.show_in_console(None, "Progress", "Additional cross-algorithm ploting...")

        # Create additional cross-algorithm plots

        # F value for all algorithms for segmentation
        # Precision
        # Recall

        plot_success = create_additional_plots("F value for segmentation", segmentation_data, 3,
                                               os.path.join(results_folder, "Plot_segmentation_F_summary.png"))
        run_show_results("Segmentation F value comparison plot was created...",
                         "Segmentation F value comparison plot was NOT created...", plot_success)

        plot_success = create_additional_plots("Precision of segmentation", segmentation_data, 1,
                                               os.path.join(results_folder, "Plot_segmentation_precision_summary.png"))
        run_show_results("Segmentation precision comparison plot was created...",
                         "Segmentation precision comparison plot was NOT created...", plot_success)

        plot_success = create_additional_plots("Recall value for segmentation", segmentation_data, 2,
                                               os.path.join(results_folder, "Plot_segmentation_recall_summary.png"))
        run_show_results("Segmentation recall value comparison plot was created...",
                         "Segmentation recall value comparison plot was NOT created...", plot_success)

        # F value for all algorithms for tracking
        # Precision
        # Recall
        plot_success = create_additional_plots("F value for tracking", tracking_data, 2,
                                               os.path.join(results_folder, "Plot_tracking_F_summary.png"))
        run_show_results("Tracking F value comparison plot was created",
                         "Tracking F value comparison plot was NOT created", plot_success)

        plot_success = create_additional_plots("Precision of tracking", tracking_data, 0,
                                               os.path.join(results_folder, "Plot_tracking_precision_summary.png"))
        run_show_results("Tracking precision comparison plot was created...",
                         "Tracking precision comparison plot was NOT created...", plot_success)

        plot_success = create_additional_plots("Recall value for tracking", tracking_data, 1,
                                               os.path.join(results_folder, "Plot_tracking_recall_summary.png"))
        run_show_results("Tracking recall value comparison plot was created...",
                         "Tracking recall value comparison plot was NOT created...", plot_success)

        debug_center.show_in_console(None, "Progress", "...ploting done")


if __name__ == '__main__':
    run_script(sys.argv)
