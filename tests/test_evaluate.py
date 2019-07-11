import os
import unittest

import imageio
import numpy as np

from ep import evaluate
from tests.testbase import TestBase


class TestEvalute(TestBase):
    def setUp(self):
        super(TestEvalute, self).setUp()
        self.image_1 = np.zeros((10, 10), dtype=np.uint8)
        self.image_1[5:8, 8:11] = 1
        self.image_1[5, 7] = 2

    def test_merge_files_into_one_images(self):
        image1_path = "image1.tiff"
        image2_path = "image3.tiff"
        image3_path = "image12.tiff"
        files = [image1_path, image2_path, image3_path]
        self.save_temp(image1_path, self.image_1)
        self.save_temp(image2_path, self.image_1)
        self.save_temp(image3_path, self.image_1)

        output_file = evaluate.merge_files_into_one([1, 3, 12], "", files)
        self.to_clear.append(output_file)
        with open(output_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(4, len(lines))
            self.assertEqual("Frame_number, Filepath\n", lines[0])
            self.assertEqual("1," + image1_path, lines[1].strip())
            self.assertEqual("3," + image2_path, lines[2].strip())
            self.assertEqual("12," + image3_path, lines[3].strip())

    def test_merge_files_into_one_filter(self):
        image1_path = "image1.tiff"
        image2_path = "image3.tiff"
        image3_path = "image12.tiff"
        files = [image1_path, image2_path, image3_path]
        self.save_temp(image1_path, self.image_1)
        self.save_temp(image2_path, self.image_1)
        self.save_temp(image3_path, self.image_1)

        output_file = evaluate.merge_files_into_one([1, 12], "", files)
        self.to_clear.append(output_file)
        with open(output_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(3, len(lines))
            self.assertEqual("Frame_number, Filepath\n", lines[0])
            self.assertEqual("1," + image1_path, lines[1].strip())
            self.assertEqual("12," + image3_path, lines[2].strip())

    def test_merge_files_into_one_csv(self):
        f1 = self.create_temp("f1")
        f1.write("headers\n")
        f1.write("plik1_data\n")
        f1.close()

        f2 = self.create_temp("f2")
        f2.write("headers\n")
        f2.write("plik2_data\n")
        f2.close()
        files = ["f1", "f2"]

        output_file = evaluate.merge_files_into_one([1, 2], "", files)
        self.to_clear.append(output_file)
        with open(output_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(3, len(lines))
            self.assertEqual("Frame_number, headers\n", lines[0])
            self.assertEqual("1,plik1_data\n", lines[1])
            self.assertEqual("2,plik2_data\n", lines[2])
