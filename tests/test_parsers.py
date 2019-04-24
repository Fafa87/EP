import os
import sys
import unittest

from ep.evalplatform.parsers import *


class TestCellTracerParser(unittest.TestCase):
    def setUp(self):
        self.input = ["FWEFWEF",
                      "1,1,284.75,256.65,0",
                      "1,2,306.8,235.28,0",
                      "1,3,318.05,264.6,0",
                      "1,4,342.28,286.51,0",
                      "2,1,283.83,246.32,1",
                      "2,2,288.3,261.77,1"]

    def test_parse(self):
        ct_parser = CellTracerParser()
        output = list(list(zip(*ct_parser.parse(self.input)))[1])
        correct_out = [CellOccurence(1, 1, 1, (284.75, 256.65), 0),
                       CellOccurence(1, 2, 2, (306.8, 235.28), 0),
                       CellOccurence(1, 3, 3, (318.05, 264.6), 0),
                       CellOccurence(1, 4, 4, (342.28, 286.51), 0),
                       CellOccurence(2, 1, 1, (283.83, 246.32), 0),  # no colour parsed
                       CellOccurence(2, 5, 5, (288.3, 261.77), 0)]
        self.assertSequenceEqual(output, correct_out)


class TestCellStarParser(unittest.TestCase):
    def setUp(self):
        self.input = ["FWEFWEF",
                       '1,1,"287","339,23",0',
                       '1,2,"186","301,0",0',
                       '1,3,"255","122,1",0',
                       '2,1,"256","122,1",3']

    def test_parse(self):
        cstar_parser = CellStarParser()
        output = list(list(zip(*cstar_parser.parse(self.input)))[1])
        correct2_out = [CellOccurence(1, 1, 1, (287.0, 339.23)),
                        CellOccurence(1, 2, 2, (186.0, 301.0)),
                        CellOccurence(1, 3, 3, (255.0, 122.1)),
                        CellOccurence(2, 1, 3, (256.0, 122.1))]
        self.assertSequenceEqual(correct2_out, output)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules["__main__"])
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.system("pause")
