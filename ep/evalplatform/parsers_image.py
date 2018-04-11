from abc import abstractmethod
import imghdr

import numpy as np
import scipy.misc as misc
import scipy.ndimage
import scipy.ndimage.measurements as measures

from .yeast_datatypes import CellOccurence


class ImageCellParser:
    def __init__(self):
        pass

    @abstractmethod
    def image_to_labels(self, image):
        return

    @staticmethod
    def is_image(path):
        return imghdr.what(path) is not None

    def parse_labels(self, frame, label_image, label_to_colour):
        res = []
        num_components = label_image.max()
        objects = measures.find_objects(label_image, num_components)
        for label in range(1, num_components + 1):
            colour = 0
            if label in label_to_colour:
                colour = label_to_colour[label]

            label_slice = objects[label - 1]
            if label_slice is None:
                continue

            object_mask = label_image == label

            # calculate center of mass
            points_yx = np.nonzero(object_mask)
            (y, x) = points_yx[0].mean(), points_yx[1].mean()

            # create result CellOcurrence
            cell = CellOccurence(frame, label, -1, (x, y))
            cell.colour = colour
            cell.mask = object_mask[label_slice].copy()
            cell.mask_slice = label_slice
            res.append(cell)
        return res

    def load_single_image(self, frame, path):
        image = misc.imread(path)
        label_image, label_to_colour = self.image_to_labels(image)
        return self.parse_labels(frame, label_image, label_to_colour)

    def load_from_merged_file(self, path):
        """
        :param path: path to merged image with list of paths to image files
        :return: all data 
        """
        with open(path, "r") as f:
            image_paths = f.readlines()

        res = []
        # first line are headers
        for i, p in list(enumerate(image_paths))[1:]:
            res += self.load_single_image(i, p.split(',')[1].strip())
        return res

    def load_from_file(self, path):
        if self.is_image(path):
            res = self.load_single_image(1, path)
        else:
            res = self.load_from_merged_file(path)
        return [(c.frame_number, c) for c in res]


class MaskImageParser(ImageCellParser):
    symbol = "MASK"

    def __init__(self, facultative=[]):
        self.facultative_values = facultative

    def is_facultative(self, v):
        return v in self.facultative_values

    def is_relevant(self, v):
        return v == 1 or self.is_facultative(v)

    def gt_label_to_snakes(self, components):
        num_components = components.max()
        return [(components == label) for label in range(1, num_components + 1)]

    def image_to_labels(self, image):
        image_cleared = image.copy()
        values = set(np.unique(image_cleared))
        values_relevant = set([val for val in values if self.is_relevant(val) and val != 0])
        for val_irrelevant in values - values_relevant:
            image_cleared[image_cleared == val_irrelevant] = 0

        number = 0
        components = np.zeros(image.shape, dtype=np.int32)
        colours = {}
        for val in values_relevant:
            comp, num_comp = scipy.ndimage.label(image_cleared == val, np.ones((3, 3)))
            comp[comp != 0] += number
            components += comp

            for num in range(number + 1, number + 1 + num_comp):
                colour = 0
                if val > 1:
                    colour = val
                colours[num] = colour
            number += num_comp

        return components, colours


class LabelImageParser(ImageCellParser):
    symbol = "LABEL"

    def parse_image(self, image):
        values = np.unique(image)
        # remap labels to [1..] values
        curr = 1
        label_image = image.copy()
        for v in values[1:]:  # zero is ignored
            label_image[image == v] = curr
            curr += 1
        return label_image

    def image_to_labels(self, image):
        curr = 1
        label_image = image.copy()
        values = np.unique(image)
        colours = {}
        for v in values[1:]:  # zero is ignored
            label_image[image == v] = curr
            colours[curr] = 0
            curr += 1

        return label_image, colours
