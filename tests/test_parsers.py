### ======= TESTS ======= ###
        
import unittest
import os
import sys
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
        output = ct_parser.parse(self.input)
        correct_out = [(1,1,284.75,256.65),(1,2,306.8,235.28),(1,3,318.05,264.6),(1,4,342.28,286.51),(2,1,283.83,246.32),(2,1,288.3,261.77)]
        self.assertEqual(correct_out,output)
        
class TestCellStarParser(unittest.TestCase):
    def setUp(self):
        self.input = ["FWEFWEF",r"""BF_pos0_time0001 (1).mat'"",0,""287"",""339.23"",""0""",
                r"""BF_pos0_time0001 (1).mat'"",0,""226"",""113"",""0""",
                r"""BF_pos0_time0004.mat'"",0,""289"",""340"",""1""",
                r"""BF_pos0_time0004.mat'"",0,""256"",""123"",""2"""]
        self.input2 = ["FWEFWEF",'1,1,"287","339,23",0','1,2,"186","301,0"', '1,3,"255","122,1"']
    
    def test_parse(self):
        cstar_parser = CellStarParser()
        output = cstar_parser.parse(self.input2)
        #correct_out = [(1,1,287,339.23,0),(1,2,226,113,0),(2,3,289,340,1),(2,4,256,123,2)]
        correct2_out = [(1,1,287,339.23,0),(1,2,186,301,0),(1,3,255,122,1)]
        self.assertEqual(correct2_out,output)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules["__main__"])
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.system("pause")
