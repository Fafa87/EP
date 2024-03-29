import fire
import imageio
import matplotlib.pyplot as plt
import scipy.misc as misc

from .parsers import *
from .utils import *


# ========= FRAMEWORK =========== #

class PaintRequestABC(object):
    def __init__(self, file, **kwargs):
        """
        Args::
            file : string
                filename of the image file to modify
        """
        self.file = file
        self.markersize = kwargs.get('markersize', 7)
        self.markerfill = kwargs.get('markerfill', False)

    def draw_cell(self, axis, position, result):
        colours = {EvaluationResult.CORRECT: "#00FF00", EvaluationResult.FALSE_POSITIVE: "r",
                   EvaluationResult.FALSE_NEGATIVE: "y"}
        markerfacecolor = "none"
        if self.markerfill:
            markerfacecolor = colours[result]
        axis.plot(position[0], position[1], "o", alpha=1, markersize=self.markersize, markerfacecolor=markerfacecolor,
                  markeredgecolor=colours[result])

    def draw_line(self, axis, position1, position2, result):
        colours = {EvaluationResult.CORRECT: "#00FF00", EvaluationResult.FALSE_POSITIVE: "r",
                   EvaluationResult.FALSE_NEGATIVE: "y"}
        axis.plot([position1[0], position2[0]], [position1[1], position2[1]], color=colours[result], linestyle='-',
                  linewidth=1)

    def draw(self, image, axis):
        pass


class DrawingOverlordABC(object):
    def __init__(self, **kwargs):
        pass

    def help_params(self):
        return ""

    def read_data(self):
        """Reads data that is later used for preparing PaintRequests."""
        pass

    def create_paint_requests(self, frame, image_file, data):
        """Creates PaintRequests."""
        return []

    def image_filter(self, filename):
        """
        Additional filtering of the input images.
        
        Args::
            filename
            
        Return::
            Whether this file should be included in the input images set.
        """
        (_, extension) = os.path.splitext(filename)
        return extension in [".tiff", ".tif", ".jpg", ".png"]

    def input_images(self, directory):
        directory = directory or "."
        files = [f for f in os.listdir(directory) if
                 os.path.isfile(os.path.join(directory, f)) and self.image_filter(f)]
        return files


# ============= PAINT REQUEST IMPLEMENTATION =============== #

class SegmentationDetail(PaintRequestABC):
    def __init__(self, file, evaluation_detail, **kwargs):
        PaintRequestABC.__init__(self, file, **kwargs)
        self.evaluation_detail = evaluation_detail

    def draw(self, image, axis):
        detail = self.evaluation_detail
        '@type detail: SegmentationResult'
        self.draw_cell(axis, (detail.cell_algo or detail.cell_GT).position, detail.result)
        if detail.result == EvaluationResult.CORRECT and distance(detail.cell_algo.position,
                                                                  detail.cell_GT.position) > 5:  # show difference
            self.draw_line(axis, detail.cell_algo.position, detail.cell_GT.position, detail.result)


class TrackingDetail(PaintRequestABC):
    def __init__(self, file, evaluation_detail):
        PaintRequestABC.__init__(self, file)
        self.evaluation_detail = evaluation_detail

    def draw(self, image, axis):
        detail = self.evaluation_detail
        '@type detail: TrackingResult'
        link = (detail.link_algo or detail.link_GT)
        # self.draw_cell(axis, link.cell_A.position, detail.result) - draw only current position
        self.draw_cell(axis, link.cell_B.position, detail.result)
        self.draw_line(axis, link.cell_A.position, link.cell_B.position, detail.result)
        pass


EvaluationType = Enum("SEGMENTATION", "TRACKING", "MISC")


class EvaluationDetails(DrawingOverlordABC):
    def __init__(self, details_file,
                 required_substring=None, details_type=None, draw_correct=True,
                 fill_markers=False, markersize=7, **kwargs):
        DrawingOverlordABC.__init__(self, **kwargs)
        self.details_file = details_file
        self.required_substring = required_substring
        self.fill_markers = fill_markers
        self.markersize = markersize
        self.details_type = details_type or EvaluationDetails.determine_type(self.details_file)
        self.draw_correct = draw_correct

    @staticmethod
    def determine_type(filepath):
        if SEGDETAILS_SUFFIX in filepath:
            return EvaluationType.SEGMENTATION
        elif TRACKDETAILS_SUFFIX in filepath or LONGTRACKDETAILS_SUFFIX in filepath:
            return EvaluationType.TRACKING
        else:
            return EvaluationType.MISC

    def image_filter(self, filename_with_ext):
        """
        Filter using part of the filename
        
        Args::
            filename
            
        Return::
            Whether this file should be included in the input images set.
        """
        (filename, extension) = os.path.splitext(filename_with_ext)
        if not self.required_substring is None and self.required_substring not in filename_with_ext:
            return False
        return extension in [".tiff", ".tif", ".jpg", ".png"]

    def help_params(self):
        return "details_file, {input_files_substring}, {specific_details_file_type}, {draw_also_correct_results}"

    def read_data(self):
        """Reads data that is later used for preparing PaintRequests.
        
        Returns::
            [(frame,data)] where data is evaluation details (segmentation or tracking)
        """
        data = []
        if os.path.isfile(self.details_file):
            (_, records) = read_from_csv(self.details_file)
            if self.details_type == EvaluationType.SEGMENTATION:
                data = [SegmentationResult.csv_init(r) for r in records]
            elif self.details_type == EvaluationType.TRACKING:
                data = [TrackingResult.csv_init(r) for r in records]
        else:
            debug_center.show_in_console(None, "Warning", "".join([self.details_file, " is not found."]))
        return [(d.frame, d) for d in data]

    def create_paint_request(self, frame, image_file, data_sample):
        """@type data_sample: EvaluationDetail"""
        if data_sample.result != EvaluationResult.CORRECT or self.draw_correct:
            if isinstance(data_sample, SegmentationResult):
                return [SegmentationDetail(image_file, data_sample, markerfill=self.fill_markers,
                                           markersize=self.markersize)]
            elif isinstance(data_sample, TrackingResult):
                return [TrackingDetail(image_file, data_sample)]
        return []


# ============= EXTERNAL CODE: http://robotics.usc.edu/~ampereir/wordpress/?p=626 ============= #
def SaveFigureAsImage(fileName, fig=None, **kwargs):
    """ Save a Matplotlib figure as an image without borders or frames.
       Args:
            fileName (str): String that ends in .png etc.

            fig (Matplotlib figure instance): figure you want to save as the image
        Keyword Args:
            orig_size (tuple): width, height of the original image used to maintain
            aspect ratio.
    """
    fig_size = fig.get_size_inches()
    w, h = fig_size[0], fig_size[1]
    fig.patch.set_alpha(0)
    if 'orig_size' in kwargs:  # Aspect ratio scaling if required
        w, h = kwargs['orig_size']
        w2, h2 = fig_size[0], fig_size[1]
        fig.set_size_inches([(w2 / w) * w, (w2 / w) * h])
        # on some environment it fails for some reason
        # fig.set_dpi((w2/w)*fig.get_dpi())
    a = fig.gca()
    a.set_frame_on(False)
    a.set_xticks([])
    a.set_yticks([])
    plt.axis('off')
    plt.xlim(0, w)
    plt.ylim(h, 0)
    fig.savefig(fileName, transparent=True, bbox_inches='tight',
                pad_inches=0)


# ========== MODULE PARAMETRISATION =============== #

"""
Below are functions and parameters that have to be provided in order for the drawing module to work properly.
"""
output_file_prefix = "Data_"
get_path_new_file = lambda directory, filename: os.path.join(directory, "".join([output_file_prefix, filename]))
"""Constructs new filename for modified drawing based on the current one."""


# =============== SCRIPT USAGE PARAMETERS ================= #


def get_trailing_number(filepath):
    return parse_file_order(get_trailing_order(filepath, is_path=True))


def get_images_sizes(overlord, directory_images):
    def get_image_size_xy(filepath):
        shape_yx = imageio.imread(filepath).shape
        return shape_yx[1], shape_yx[0]

    def get_old_path_file(filename):
        return os.path.join(directory_images, filename)

    image_list = overlord.input_images(directory_images)
    return dict([(get_trailing_number(f), get_image_size_xy(get_old_path_file(f))) for f in image_list])


def run(overlord, directory_images, directory_output, desired_output_file_prefix=None):
    global output_file_prefix

    if directory_output and not os.path.exists(directory_output):
        os.makedirs(directory_output)

    data = overlord.read_data()
    output_file_prefix = desired_output_file_prefix or output_file_prefix
    # =========== READ INPUT IMAGES ============= #
    image_list = overlord.input_images(directory_images)
    image_number_dict = dict([(get_trailing_number(f), f) for f in image_list])

    # =========== PREPARE PAINT REQUESTS ============== #

    debug_center.show_in_console(None, "Progress", "Creating paint requests...")

    requests = []
    files_with_data = set()
    for (frame, data_piece) in data:
        if frame in image_number_dict:
            image = image_number_dict[frame]
            files_with_data.add(image)
            requests = requests + overlord.create_paint_request(frame, image, data_piece)

    debug_center.show_in_console(None, "Progress", "".join(
        ["Created ", str(len(requests)), " paint requests out of ", str(len(data)), " data points."]))

    # ============ DRAW ============== #

    def get_old_path_file(filename):
        return os.path.join(directory_images, filename)

    keyfunc = lambda req: req.file
    requests = sorted(requests, key=keyfunc)
    file_groups = {file: list(group) for file, group in itertools.groupby(requests, keyfunc)}

    debug_center.show_in_console(None, "Progress", "Applying requests on input images...")
    for file in files_with_data:
        group = file_groups.get(file, [])
        filename = os.path.basename(file)
        file_requests = list(group)
        image_raw = imageio.imread(get_old_path_file(file))
        image = image_raw.astype(float) / np.iinfo(image_raw.dtype).max
        fig = plt.figure(frameon=False)
        plt.axis('off')
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        fig.add_axes(ax)
        ax.set_axis_off()
        ax.imshow(image, cmap=plt.cm.gray)

        i = 0
        for req in file_requests:
            req.draw(image, ax)
            i = i + 1
            # print "Applied", i, "out of", len(requests), "for this file..."

        SaveFigureAsImage(get_path_new_file(directory_output, filename) + ".png", plt.gcf(),
                          orig_size=(image.shape[1], image.shape[0]))
        plt.close(fig)

    debug_center.show_in_console(None, "Progress", "Done applying requests on input images...")


def main(input_images_directory, output_images_directory, output_file_prefix,
         details_file, **kwargs):
    overlord = EvaluationDetails(details_file=details_file, **kwargs)
    run(overlord, input_images_directory, output_images_directory, output_file_prefix)


if __name__ == "__main__":
    fire.Fire(main)
