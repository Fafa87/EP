import os
import shutil


class Plotter:
    PLOT_WIDTH = 1200
    DATA_POINT_WIDTH = 80

    def __init__(self, terminal_type, config_path, title):
        self.terminal_type = terminal_type
        self.plot_config_path = config_path
        self.gnuplot_options = []
        self.title = title
        self.temp_paths = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for file_path in self.temp_paths:
            os.remove(file_path)

    def setup_ploting_area(self, wide_plot, data_points=None):
        if wide_plot and data_points:
            good_width = max(Plotter.PLOT_WIDTH, int(Plotter.PLOT_WIDTH / Plotter.DATA_POINT_WIDTH * len(data_points)))
        else:
            good_width = Plotter.PLOT_WIDTH

        if self.terminal_type != "svg":
            term_set = "pngcairo size {0},800 linewidth 2 font \\\",22\\\"".format(good_width)
            output_file_extension = ".png"
        else:
            term_set = "svg size {0},800 linewidth 2 font \\\",22\\\"".format(good_width)
            output_file_extension = ".svg"
        self.gnuplot_options = {"terminal": term_set, "output_file_extension": output_file_extension}

    def use_generic_plots(self, names):
        plt_filename_modified = self.plot_config_path + ".tmp"

        shutil.copy(self.plot_config_path, plt_filename_modified)
        self.plot_config_path = plt_filename_modified

        with open(plt_filename_modified, "a") as plt_file:
            plt_file.write("\n")
            plt_file.write("plot " + ",".join(
                ["data_file index {0} using 2:xtic(pad($0, 1)) title \"{1}\" with lines lw 2".format(i, name)
                 for (i, name) in enumerate(names)]))
            plt_file.write("\n")

    def plot_it(self, data_file, output_plot_path):
        plot_path_no_ext = os.path.splitext(output_plot_path)[0]
        gnuplot_setup_script = "\"data_file='{}';" \
                               "plot_title='{}';" \
                               "output_file='{}';" \
                               "set terminal {};" \
                               "output_file_extension='{}';\"".format(data_file, self.title, plot_path_no_ext,
                                                                      self.gnuplot_options["terminal"],
                                                                      self.gnuplot_options["output_file_extension"])
        ploting = "gnuplot -e " + gnuplot_setup_script + " " + self.plot_config_path
        os.system(ploting)
