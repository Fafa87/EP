# -*- coding: utf-8 -*-
import math
import unittest
import os

import ep.compare
import ep.evaluate

class TestSingleEvaluation(unittest.TestCase):
    def test_single_evaluation(self):
        pass

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules["__main__"])
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.system("pause")
