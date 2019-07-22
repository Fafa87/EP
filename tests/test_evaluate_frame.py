# -*- coding: utf-8 -*-
from copy import deepcopy
from unittest import skip

from ep import evaluate_frame
from ep.evalplatform.yeast_datatypes import CellOccurence
from tests.testbase import TestBase


class TestEvaluateFrame(TestBase):
    def setUp(self):
        super(TestEvaluateFrame, self).setUp()
        self.gt_data = {1: CellOccurence(3, 1, 1, (100, 100), 0),
                        2: CellOccurence(3, 2, 2, (210, 200), 1),
                        7: CellOccurence(3, 3, 3, (300, 300), 0),
                        8: CellOccurence(3, 4, 4, (10, 350), 0),
                        9: CellOccurence(3, 5, 5, (490, 490), 0)}
        self.algo_data = {2: CellOccurence(3, 1, 1, (400, 100)),
                          3: CellOccurence(3, 2, 2, (10, 150)),
                          4: CellOccurence(3, 3, 3, (10, 160)),
                          5: CellOccurence(3, 4, 4, (210, 210)),
                          6: CellOccurence(3, 5, 5, (210, 200)),
                          7: CellOccurence(3, 6, 6, (300, 300)),
                          8: CellOccurence(3, 7, 7, (10, 350)),
                          10: CellOccurence(3, 5, 5, (250, 500))}

    def test_single_evaluation_all(self):
        self.save_in_platform_format("gt.csv", self.gt_data.values())
        self.save_in_platform_format("algo.csv", self.algo_data.values())

        metrics, details = evaluate_frame.evaluate_one_frame("gt.csv", "algo.csv", "Kartek")
        self.assertEqual(2.0 / 7, metrics["Precision"])
        self.assertEqual(2.0 / 4, metrics["Recall"])
        self.assertEqual(4.0 / 11, metrics["F"])

        correct_pairs = [(c.cell_GT, c.cell_algo) for c in details["Correct"]]
        self.assertEqual(2, len(correct_pairs))
        self.assertIn((self.gt_data[7], self.algo_data[7]), correct_pairs)
        self.assertIn((self.gt_data[8], self.algo_data[8]), correct_pairs)

        fp_pairs = [(c.cell_GT, c.cell_algo) for c in details["FalsePositive"]]
        self.assertEqual(5, len(fp_pairs))
        self.assertIn((None, self.algo_data[3]), fp_pairs)
        self.assertIn((None, self.algo_data[4]), fp_pairs)
        self.assertIn((None, self.algo_data[2]), fp_pairs)
        self.assertIn((None, self.algo_data[5]), fp_pairs)
        self.assertIn((None, self.algo_data[10]), fp_pairs)

        fn_pairs = [(c.cell_GT, c.cell_algo) for c in details["FalseNegative"]]
        self.assertEqual(2, len(fn_pairs))
        self.assertIn((self.gt_data[1], None), fn_pairs)
        self.assertIn((self.gt_data[9], None), fn_pairs)

    def test_single_evaluation_count_facultative(self):
        gt_without_faculatative = deepcopy(self.gt_data)
        gt_without_faculatative[2].colour = 0
        self.save_in_platform_format("gt.csv", gt_without_faculatative.values())
        self.save_in_platform_format("algo.csv", self.algo_data.values())

        metrics, details = evaluate_frame.evaluate_one_frame("gt.csv", "algo.csv", "Kartek")
        self.assertEqual(3.0 / 8, metrics["Precision"])
        self.assertEqual(3.0 / 5, metrics["Recall"])
        self.assertEqual(6.0 / 13, metrics["F"])

        correct_pairs = [(c.cell_GT, c.cell_algo) for c in details["Correct"]]
        self.assertEqual(3, len(correct_pairs))
        self.assertIn((gt_without_faculatative[2], self.algo_data[6]), correct_pairs)
        self.assertIn((self.gt_data[7], self.algo_data[7]), correct_pairs)
        self.assertIn((self.gt_data[8], self.algo_data[8]), correct_pairs)

        fp_pairs = [(c.cell_GT, c.cell_algo) for c in details["FalsePositive"]]
        self.assertEqual(5, len(fp_pairs))
        self.assertIn((None, self.algo_data[3]), fp_pairs)
        self.assertIn((None, self.algo_data[4]), fp_pairs)
        self.assertIn((None, self.algo_data[2]), fp_pairs)
        self.assertIn((None, self.algo_data[5]), fp_pairs)
        self.assertIn((None, self.algo_data[10]), fp_pairs)

        fn_pairs = [(c.cell_GT, c.cell_algo) for c in details["FalseNegative"]]
        self.assertEqual(2, len(fn_pairs))
        self.assertIn((self.gt_data[1], None), fn_pairs)
        self.assertIn((self.gt_data[9], None), fn_pairs)

    @skip("TODO")
    def test_single_evaluation_ignore_borders(self):
        pass

    def test_single_evaluation_with_mask_format(self):
        self.save_in_mask_format("gt.tif", self.gt_data.values(), 4)
        self.save_in_mask_format("algo.tif", self.algo_data.values(), 4)

        metrics, details = evaluate_frame.evaluate_one_frame("gt.tif", "algo.tif", "Kartek", parser_symbol="MASK")
        self.assertEqual(2.0 / 7, metrics["Precision"])
        self.assertEqual(2.0 / 4, metrics["Recall"])
        self.assertEqual(4.0 / 11, metrics["F"])

        correct_pairs = [(c.cell_GT, c.cell_algo) for c in details["Correct"]]
        self.assertEqual(2, len(correct_pairs))
        self.assertEqualsCellsPairs((self.gt_data[7], self.algo_data[7]), correct_pairs[0], ignore_ids=True)
        self.assertEqualsCellsPairs((self.gt_data[8], self.algo_data[8]), correct_pairs[1], ignore_ids=True)

        fp_pairs = [(c.cell_GT, c.cell_algo) for c in details["FalsePositive"]]
        self.assertEqual(5, len(fp_pairs))
        self.assertEqualsCellsPairs((None, self.algo_data[3]), fp_pairs[1], ignore_ids=True)
        self.assertEqualsCellsPairs((None, self.algo_data[4]), fp_pairs[2], ignore_ids=True)
        self.assertEqualsCellsPairs((None, self.algo_data[2]), fp_pairs[0], ignore_ids=True)
        self.assertEqualsCellsPairs((None, self.algo_data[5]), fp_pairs[3], ignore_ids=True)
        self.assertEqualsCellsPairs((None, self.algo_data[10]), fp_pairs[4], ignore_ids=True)

        fn_pairs = [(c.cell_GT, c.cell_algo) for c in details["FalseNegative"]]
        self.assertEqual(2, len(fn_pairs))
        self.assertEqualsCellsPairs((self.gt_data[1], None), fn_pairs[0], ignore_ids=True)
        self.assertEqualsCellsPairs((self.gt_data[9], None), fn_pairs[1], ignore_ids=True)

    @skip("TODO")
    def test_single_evaluation_uses_ini_values(self):
        # TODO test if it reads params from ini
        pass
