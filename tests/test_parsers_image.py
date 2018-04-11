# -*- coding: utf-8 -*-
import os
import unittest

import imageio
from numpy.testing import *

from ep.evalplatform.parsers_image import *


class TestCellImageParser(unittest.TestCase):
    def setUp(self):
        self.parser = MaskImageParser()
        self.to_clear = []
        self.image_1 = np.zeros((20, 15), dtype=np.uint8)
        self.image_1[5:8, 8:11] = 1
        self.image_2 = np.zeros((30, 20), dtype=np.uint8)
        self.image_2[7:10, 3] = 1

    def tearDown(self):
        for path in self.to_clear:
            os.remove(path)

    def create_temp(self, path):
        self.to_clear.append(path)
        return open(path, "w")

    def save_temp(self, path, image):
        self.to_clear.append(path)
        imageio.imsave(path, image)

    def validate(self, *args, **kwargs):
        TestCellImageParser.validate_cell(self, *args, **kwargs)

    @staticmethod
    def validate_cell(self, cell, frame, cell_id, unique_id, posxy, colour, precision=2):
        self.assertEqual(frame, cell.frame_number)
        self.assertEqual(cell_id, cell.cell_id)
        self.assertEqual(unique_id, cell.unique_id)
        self.assertAlmostEqual(posxy[0], cell.position[0], precision)
        self.assertAlmostEqual(posxy[1], cell.position[1], precision)
        self.assertEqual(colour, cell.colour)

    def test_cell_slices(self):
        image = np.zeros((40, 40), dtype=np.uint8)
        image[8:15, 3:10] = 1
        image[10:18, 7:13] = 2
        image[1:3, 30:35] = 3
        image[33:35, 20:21] = 3
        cells = self.parser.parse_labels(1, image, {})
        self.validate(cells[0], 1, 1, -1, (5.12, 10.56), 0)
        self.validate(cells[1], 1, 2, -1, (9.5, 13.5), 0)
        self.validate(cells[2], 1, 3, -1, (30, 6.83), 0)
        assert_array_equal(image[8:15, 3:10] == 1, cells[0].mask)
        assert_array_equal(image[10:18, 7:13] == 2, cells[1].mask)
        assert_array_equal(image[1:35, 20:35] == 3, cells[2].mask)
        self.assertEqual(34, cells[0].area)  # because of overlap in image
        self.assertEqual(48, cells[1].area)
        self.assertEqual(2 + 2 * 5, cells[2].area)

        self.assertEqual((slice(8, 15), slice(3, 10)), cells[0].mask_slice)
        self.assertAlmostEqual(5, cells[0].distance(cells[1]), 0)

        self.assertAlmostEqual(0, cells[0].overlap(cells[1]), 2)
        self.assertAlmostEqual(0, cells[0].overlap(cells[2]), 2)
        self.assertAlmostEqual(0, cells[1].overlap(cells[2]), 2)

    def test_cell_overlap(self):
        image1 = np.zeros((40, 40), dtype=np.uint8)
        image1[8:15, 3:10] = 1
        image1[12, 9] = 0  # make overlap non rectanglular
        image2 = np.zeros((40, 40), dtype=np.uint8)
        image2[10:18, 7:13] = 2
        image2[1:3, 30:35] = 3
        image2[33:35, 20:21] = 3
        cells = self.parser.parse_labels(1, image1, {})
        cells += self.parser.parse_labels(1, image2, {})
        self.validate(cells[0], 1, 1, -1, (5.9375, 10.979), 0)
        self.validate(cells[1], 1, 2, -1, (9.5, 13.5), 0)
        self.validate(cells[2], 1, 3, -1, (30, 6.83), 0)
        assert_array_equal(image1[8:15, 3:10] == 1, cells[0].mask)
        assert_array_equal(image2[10:18, 7:13] == 2, cells[1].mask)
        assert_array_equal(image2[1:35, 20:35] == 3, cells[2].mask)
        self.assertEqual(7 * 7 - 1, cells[0].area)
        self.assertEqual(48, cells[1].area)
        self.assertEqual(2 + 2 * 5, cells[2].area)

        self.assertAlmostEqual(15 - 1, cells[0].overlap(cells[1]), 2)
        self.assertAlmostEqual(0, cells[0].overlap(cells[2]), 2)
        self.assertAlmostEqual(0, cells[1].overlap(cells[2]), 2)

    def test_parse_labels(self):
        image = np.zeros((40, 40), dtype=np.uint8)
        image[8:15, 8:15] = 1
        image[10, 30] = 2
        image[10, 12] = 3
        cells = self.parser.parse_labels(1, image, {})
        self.assertEqual(3, len(cells))
        self.validate(cells[0], 1, 1, -1, (10.98, 11.02), 0)
        self.validate(cells[1], 1, 2, -1, (30, 10), 0)
        self.validate(cells[2], 1, 3, -1, (12, 10), 0)

        cells = self.parser.parse_labels(2, image, {2: 5})
        self.assertEqual(3, len(cells))
        self.validate(cells[0], 2, 1, -1, (10.98, 11.02), 0)
        self.validate(cells[1], 2, 2, -1, (30, 10), 5)
        self.validate(cells[2], 2, 3, -1, (12, 10), 0)

    def fake_load_single_image(self, called):
        def load_single_image(f, p):
            misc.imread(p)
            called.append((f, p))
            fake = CellOccurence(0, 0, 0, None)
            fake.frame_number = 0
            fake.data = p
            return [fake]

        return load_single_image

    def prepare_merged(self, path, images):
        f = self.create_temp(path)
        f.write("Frame, dane\n")
        for i, m in enumerate(images, 1):
            f.write(str(i) + "," + m + "\n")
        f.close()

    def test_is_image(self):
        image1_path = "image_1.png"
        self.save_temp(image1_path, self.image_1)
        image2_path = "image_1.tif"
        self.save_temp(image2_path, self.image_1)

        self.assertEqual(True, ImageCellParser.is_image(image1_path))
        self.assertEqual(True, ImageCellParser.is_image(image2_path))

        merged_path = "merged.png"
        self.prepare_merged(merged_path, [image1_path, image2_path])

        data3 = ImageCellParser.is_image(merged_path)
        self.assertEqual(False, data3)

    def test_load_single(self):
        called = []
        self.parser.load_single_image = self.fake_load_single_image(called)

        image1_path = "image_1.png"
        image2_path = "image_2.tiff"
        self.save_temp(image1_path, self.image_1)
        self.save_temp(image2_path, self.image_2)

        res = self.parser.load_from_file(image1_path)
        self.assertEqual(0, res[0][0])
        self.assertEqual(image1_path, res[0][1].data)
        self.assertEqual([(1, image1_path)], called)

        called[:] = []
        res = self.parser.load_from_file(image2_path)
        self.assertEqual(0, res[0][0])
        self.assertEqual(image2_path, res[0][1].data)
        self.assertEqual([(1, image2_path)], called)

    def test_load_merged(self):
        called = []
        self.parser.load_single_image = self.fake_load_single_image(called)

        image1_path = "image_2.tiff"
        image2_path = "image_1.png"
        self.save_temp(image1_path, self.image_1)
        self.save_temp(image2_path, self.image_2)

        merged_path = "merged.png"
        self.prepare_merged(merged_path, [image1_path, image2_path])

        res = self.parser.load_from_file(merged_path)
        self.assertEqual(0, res[0][0])
        self.assertEqual(0, res[1][0])
        self.assertEqual(image1_path, res[0][1].data)
        self.assertEqual(image2_path, res[1][1].data)
        self.assertEqual([(1, image1_path), (2, image2_path)], called)


class TestMaskImageParser(unittest.TestCase):
    def setUp(self):
        self.parser = MaskImageParser(facultative=[3])
        self.to_clear = []
        self.image_1 = np.zeros((20, 18), dtype=np.uint8)
        self.image_1[5:8, 8:11] = 1
        self.image_1[5, 7] = 1
        # same object because of 8 direction neighbourhood
        self.image_1[4, 6] = 1
        # different object
        self.image_1[2, 5] = 1
        self.image_1[5:8, 11] = 6
        # treat as facultative
        self.image_1[3:10, 12:15] = 3

        # ignored
        self.image_1[15, 15] = 5
        self.image_1[17, 15] = 2

        # facultative touching other - different object
        self.image_1[4, 7] = 3

    def tearDown(self):
        for path in self.to_clear:
            os.remove(path)

    def save_temp(self, path, image):
        self.to_clear.append(path)
        imageio.imsave(path, image)

    def test_pixel_analyses(self):
        self.assertEqual(False, self.parser.is_facultative(0))
        self.assertEqual(False, self.parser.is_facultative(1))
        self.assertEqual(False, self.parser.is_facultative(2))
        self.assertEqual(True, self.parser.is_facultative(3))

        self.assertEqual(False, self.parser.is_relevant(0))
        self.assertEqual(True, self.parser.is_relevant(1))
        self.assertEqual(False, self.parser.is_relevant(2))
        self.assertEqual(True, self.parser.is_relevant(3))

    def test_two_cell_mask_and_labels(self):
        gt = self.parser.load_from_file("input/result_gt.tif")
        self.assertEqual(2, len(gt))
        TestCellImageParser.validate_cell(self, gt[0][1], 1, 1, -1, (21, 8), 0, precision=0)
        TestCellImageParser.validate_cell(self, gt[1][1], 1, 2, -1, (22, 22), 0, precision=0)
        self.assertNotEqual(None, gt[0][1].mask)

        parser_label = LabelImageParser()
        algo = parser_label.load_from_file("input/result_algo.tif")
        self.assertEqual(2, len(algo))
        TestCellImageParser.validate_cell(self, algo[0][1], 1, 1, -1, (21, 7), 0, precision=0)
        TestCellImageParser.validate_cell(self, algo[1][1], 1, 2, -1, (22, 21), 0, precision=0)
        self.assertNotEqual(None, algo[0][1].mask)

    def test_image_to_labels(self):
        labels, colours = self.parser.image_to_labels(self.image_1)
        expected_labels = np.zeros((20, 18), dtype=np.int32)
        expected_labels[5:8, 8:11] = 2
        expected_labels[5, 7] = 2
        expected_labels[4, 6] = 2
        expected_labels[2, 5] = 1
        expected_labels[3:10, 12:15] = 3
        expected_labels[4, 7] = 4

        expected_colours = {1: 0, 2: 0, 3: 3, 4: 3}
        assert_array_equal(expected_labels, labels)
        self.assertEqual(expected_colours, colours)

    def test_load_from_file(self):
        image1_path = "image1.tiff"
        image2_path = "image2.png"
        self.save_temp(image1_path, self.image_1)
        self.save_temp(image2_path, self.image_1)

        def validate_image1(data):
            self.assertEqual(4, len(data))
            data = [d[1] for d in data]
            TestCellImageParser.validate_cell(self, data[0], 1, 1, -1, (5, 2), 0)
            TestCellImageParser.validate_cell(self, data[1], 1, 2, -1, (8.545, 5.727), 0)
            TestCellImageParser.validate_cell(self, data[2], 1, 3, -1, (13, 6), 3)
            TestCellImageParser.validate_cell(self, data[3], 1, 4, -1, (7, 4), 3)

        res = self.parser.load_from_file(image1_path)
        validate_image1(res)

        res = self.parser.load_from_file(image2_path)
        validate_image1(res)


class TestLabelImageParser(unittest.TestCase):
    def setUp(self):
        self.parser = LabelImageParser()
        self.to_clear = []
        self.image_1 = np.zeros((20, 18), dtype=np.uint8)
        self.image_1[5:8, 8:11] = 2
        self.image_1[5, 7] = 2
        self.image_1[4, 6] = 2
        self.image_1[2, 5] = 4
        self.image_1[5:8, 11] = 6
        self.image_1[3:10, 12:15] = 3

    def tearDown(self):
        for path in self.to_clear:
            os.remove(path)

    def save_temp(self, path, image):
        self.to_clear.append(path)
        imageio.imsave(path, image)

    def test_image_to_labels(self):
        labels, colours = self.parser.image_to_labels(self.image_1)
        expected_labels = np.zeros((20, 18), dtype=np.int32)
        expected_labels[5:8, 8:11] = 1
        expected_labels[5, 7] = 1
        expected_labels[4, 6] = 1
        expected_labels[2, 5] = 3
        expected_labels[5:8, 11] = 4
        expected_labels[3:10, 12:15] = 2

        expected_colours = {1: 0, 2: 0, 3: 0, 4: 0}
        assert_array_equal(expected_labels, labels)
        self.assertEqual(expected_colours, colours)

    def test_load_from_file(self):
        image1_path = "image1.tiff"
        image2_path = "image2.png"
        self.save_temp(image1_path, self.image_1)
        self.save_temp(image2_path, self.image_1)

        def validate_image1(data):
            self.assertEqual(4, len(data))
            data = [d[1] for d in data]
            TestCellImageParser.validate_cell(self, data[0], 1, 1, -1, (8.545, 5.727), 0)
            TestCellImageParser.validate_cell(self, data[1], 1, 2, -1, (13, 6), 0)
            TestCellImageParser.validate_cell(self, data[2], 1, 3, -1, (5, 2), 0)
            TestCellImageParser.validate_cell(self, data[3], 1, 4, -1, (11, 6), 0)

        res = self.parser.load_from_file(image1_path)
        validate_image1(res)

        res = self.parser.load_from_file(image2_path)
        validate_image1(res)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules["__main__"])
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.system("pause")
