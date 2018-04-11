import numpy as np
from cached_property import cached_property
from utils import slices_intersection, slices_relative


class CellOccurence:
    def __init__(self, frame_number, cell_id, unique_id, position):
        """
        All parameters should be greater that zero.
        Unique_id == -1 means that there is no tracking data.
        colour = 0 - cell
        colour != 0 - maybe cell
        """
        self.frame_number = frame_number
        self.cell_id = cell_id
        self.unique_id = unique_id
        self.position = position
        self.colour = 0

        self.mask = None
        self.mask_slice = None

    def get_id(self):
        """Return id of the cell in its frame."""
        if (self.unique_id == -1):
            return self.cell_id
        else:
            return self.unique_id

    def get_triple(self):
        """Return (cell_id, posx, posy) or (unique_id, posx, posy)."""
        return (self.get_id(), self.position[0], self.position[1])

    def has_tracking_data(self):
        return self.unique_id != -1

    def has_contour_data(self):
        return self.mask is not None

    def obligatory(self):
        return self.colour == 0

    def distance(self, cell_b):
        return ((self.position[0] - cell_b.position[0]) ** 2 + (self.position[1] - cell_b.position[1]) ** 2) ** 0.5

    @cached_property
    def area(self):
        if self.has_contour_data():
            return np.count_nonzero(self.mask)
        return None

    def overlap(self, cell_b):
        if self.has_contour_data() and cell_b.has_contour_data():
            slices_overlap = slices_intersection(self.mask_slice, cell_b.mask_slice)
            slice_relative_1 = slices_relative(self.mask_slice, slices_overlap)
            slice_relative_2 = slices_relative(cell_b.mask_slice, slices_overlap)
            overlap = self.mask[slice_relative_1] & cell_b.mask[slice_relative_2]
            return np.count_nonzero(overlap)
        return None

    def iou(self, cell_b):
        if self.has_contour_data() and cell_b.has_contour_data():
            intersect = float(self.overlap(cell_b))
            return intersect / (self.area + cell_b.area - intersect)
        return None

    def similarity(self, cell_b):
        iou_with_b = self.iou(cell_b)
        if iou_with_b is not None:
            return iou_with_b
        else:
            return -self.distance(cell_b)

    def is_similar(self, cell_b, position_cutoff, iou_cutoff):
        iou_with_b = self.iou(cell_b)
        if iou_with_b is not None:
            return iou_with_b > iou_cutoff
        else:
            return self.distance(cell_b) < position_cutoff

    def __hash__(self):
        return hash(self.frame_number) ^ hash(self.get_id()) ^ hash(self.position)

    def __eq__(self, other):
        return self.frame_number == other.frame_number and self.get_id() == other.get_id() and self.position == other.position

    def __str__(self):
        return "frame={0},id={1},position={2}".format(self.frame_number, self.get_id(), self.position)


class TrackingLink(object):
    def __init__(self, cell_A, cell_B):
        self.cell_A = cell_A
        self.cell_B = cell_B

    def __hash__(self):
        return hash(self.cell_A) ^ hash(self.cell_B)

    def __eq__(self, other):
        return self.cell_A == other.cell_A and self.cell_B == other.cell_B

    def __str__(self):
        return "({0}-{1})".format(self.cell_A, self.cell_B)


def Enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


EvaluationResult = Enum("CORRECT", "FALSE_POSITIVE", "FALSE_NEGATIVE", "UNKNOWN")


class EvaluationDetail(object):
    """Encapsulates the information about the evaluation results for further investigation.
    
    Attributes:
        frame - when the evaluation occurs
        result - overall result description
    """

    def __init__(self, frame, result):
        self.result = result
        self.frame = frame

    def __str__(self):
        return "{0} - {1}".format(self.frame, EvaluationResult.reverse_mapping[self.result])

    def calculate_result(self, GT, algo):
        if GT is not None and algo is not None:
            result = EvaluationResult.CORRECT
        elif GT is not None:
            result = EvaluationResult.FALSE_NEGATIVE
        elif algo is not None:
            result = EvaluationResult.FALSE_POSITIVE
        else:
            result = EvaluationResult.UNKNOWN
        return result

    @staticmethod
    def csv_headers():
        return ["Frame", "Result"]

    def csv_record(self):
        return [self.frame, EvaluationResult.reverse_mapping[self.result]]

    def csv_read(self, record):
        self.frame = int(record[0])
        self.result = EvaluationResult.__getattribute__(EvaluationResult, record[1])
        return record[2:]


class SegmentationResult(EvaluationDetail):
    """Contains the positions of the both ground truth and corresponding cell from the algorithm results. Potentially one of them is non-existent (False positive/negative).
    
    Attributes:
        cell_GT - cell from ground truth
        cell_algo - cell found by an algorithm
    """

    def __init__(self, cell_gt=None, cell_algo=None):
        if (not (cell_gt is None and cell_algo is None)):
            EvaluationDetail.__init__(self, (cell_gt or cell_algo).frame_number,
                                      self.calculate_result(cell_gt, cell_algo))
            self.cell_GT = cell_gt
            self.cell_algo = cell_algo
        else:
            self.cell_GT = None
            self.cell_algo = None

    def __str__(self):
        return "{0}: GT={1}, ALGO={2}".format(EvaluationDetail.__str__(self), self.cell_GT, self.cell_algo)

    @staticmethod
    def csv_headers():
        return EvaluationDetail.csv_headers() + ["GT_id", "GT_pos_x", "GT_pos_y", "Algo_id", "Algo_pos_x", "Algo_pos_y"]

    def csv_record(self):
        record = EvaluationDetail.csv_record(self)

        def print_cell(record, cell):
            if cell:
                record = record + [cell.cell_id] + list(cell.position)
            else:
                record = record + ["", "", ""]
            return record

        record = print_cell(record, self.cell_GT)
        record = print_cell(record, self.cell_algo)
        return record

    def csv_read(self, record):
        record = EvaluationDetail.csv_read(self, record)

        def read_cell(record):
            return CellOccurence(self.frame, record[0], -1, (float(record[1]), float(record[2])))

        if self.result == EvaluationResult.CORRECT or self.result == EvaluationResult.FALSE_NEGATIVE:
            self.cell_GT = read_cell(record)
        record = record[3:]

        if self.result == EvaluationResult.CORRECT or self.result == EvaluationResult.FALSE_POSITIVE:
            self.cell_algo = read_cell(record)
        record = record[3:]
        return record

    @staticmethod
    def csv_init(record):
        sr = SegmentationResult()
        sr.csv_read(record)
        return sr


class TrackingResult(EvaluationDetail):
    """Contains the tracking links from both the ground truth and from the algorithm results. Potentially one of them is non-existent (False positive/negative).
    
    Attributes:
        prev_frame - number of the frame from which comes the other ends of the links
        link_GT - link from ground truth
        link_algo - link found by an algorithm
    """

    def __init__(self, link_gt=None, link_algo=None):
        if (not (link_gt is None and link_algo is None)):
            EvaluationDetail.__init__(self, (link_gt or link_algo).cell_B.frame_number,
                                      self.calculate_result(link_gt, link_algo))
            self.prev_frame = (link_gt or link_algo).cell_A.frame_number
            self.link_GT = link_gt
            self.link_algo = link_algo
        else:
            self.link_GT = None
            self.link_algo = None

    def __str__(self):
        return "{0}: GT_LINK={1}, ALGO_LINK={2}".format(EvaluationDetail.__str__(self), self.link_GT, self.link_algo)

    @staticmethod
    def csv_headers():
        return EvaluationDetail.csv_headers() + ["Prev_frame",
                                                 "GT_unique_id", "GT_pos0_x", "GT_pos0_y", "GT_pos1_x", "GT_pos1_y",
                                                 "Algo_unique_id", "Algo_pos0_x", "Algo_pos0_y", "Algo_pos1_x",
                                                 "Algo_pos1_y"]

    def csv_record(self):
        record = EvaluationDetail.csv_record(self) + [self.prev_frame]

        def print_link(record, link):
            '@type link: TrackingLink'
            if link:
                record = record + [link.cell_A.unique_id] + list(link.cell_A.position) + list(link.cell_B.position)
            else:
                record = record + ["", "", "", "", ""]
            return record

        record = print_link(record, self.link_GT)
        record = print_link(record, self.link_algo)
        return record

    def csv_read(self, record):
        record = EvaluationDetail.csv_read(self, record)
        self.prev_frame = record[0]
        record = record[1:]

        def read_link(record, strip_record=False):
            unique_id, pos0_x, pos0_y, pos1_x, pos1_y = tuple(record[:5])
            if strip_record:
                del record[:5]
            return TrackingLink(CellOccurence(self.prev_frame, unique_id, unique_id, (float(pos0_x), float(pos0_y))),
                                CellOccurence(self.frame, unique_id, unique_id, (float(pos1_x), float(pos1_y))))

        if self.result == EvaluationResult.CORRECT or self.result == EvaluationResult.FALSE_NEGATIVE:
            self.link_GT = read_link(record)
        del record[:5]
        if self.result == EvaluationResult.CORRECT or self.result == EvaluationResult.FALSE_POSITIVE:
            self.link_algo = read_link(record)
        del record[:5]

        return record

    @staticmethod
    def csv_init(record):
        sr = TrackingResult()
        sr.csv_read(record)
        return sr
