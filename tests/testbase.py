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
