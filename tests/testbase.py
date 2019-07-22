import os
import unittest

import imageio
import numpy as np


class TestBase(unittest.TestCase):
    def setUp(self):
        self.to_clear = []

    def tearDown(self):
        for path in self.to_clear:
            os.remove(path)

    def save_temp(self, path, image):
        self.to_clear.append(path)
        imageio.imsave(path, image)

    def create_temp(self, path):
        self.to_clear.append(path)
        return open(path, "w")

    def draw_cell(self, image, position, radius, value):
        left = max(0, position[0] - radius)
        top = max(0, position[1] - radius)
        right = position[0] + radius
        bottom = position[1] + radius
        image[top: bottom + 1, left: right + 1] = value

    def save_in_platform_format(self, filename, cells):
        with self.create_temp(filename) as file:
            file.write("Frame_nr, Cell_nr, Cell_colour, Position_X, Position_Y\n")
            for cell in cells:
                file.write("{frame}, {cellid}, {color}, {posx}, {posy}\n".format(
                    frame=cell.frame_number, cellid=cell.cell_id, posx=cell.position[0], posy=cell.position[1],
                    color=cell.colour))

    def save_in_mask_format(self, filename, cells, radius):
        image = np.zeros((510, 510), dtype=np.uint8)
        for cell in cells:
            self.draw_cell(image, cell.position, radius, cell.colour + 1)
        self.save_temp(filename, image)

    def assertEqualsCells(self, a, b, ignore_ids=False):
        if a is None or b is None:
            self.assertEqual(a, b)
        else:
            if not ignore_ids:
                self.assertEquals(a, b)
            else:
                self.assertEquals((a.position, a.colour), (b.position, b.colour))

    def assertEqualsCellsPairs(self, a2, b2, ignore_ids=False):
        self.assertEqualsCells(a2[0], b2[0], ignore_ids)
        self.assertEqualsCells(a2[1], b2[1], ignore_ids)
