import os
import sys
import unittest

from ep.evalplatform import plot_comparison
from ep.evalplatform.parsers_image import LabelImageParser, MaskImageParser
from ep.evalplatform.yeast_datatypes import *
from tests.test_parsers_image import TestMaskImageParser


class TestColours(unittest.TestCase):
    # 3 proper cells in GT + 3 border ones
    # GT = 3 | 2 -> 4 | 3
    # Algo = 2 | 2 -> 3 | 2
    dictionary_colour = {}

    def setUp(self):
        def map_to_cells(frame, old_cell_data):
            return [CellOccurence(frame, old_data[0], old_data[0], (old_data[1], old_data[2])) for old_data in
                    old_cell_data]

        self.dictionary_colour = dict(
            [((1, 1), 0), ((1, 2), 0), ((1, 3), 3), ((1, 4), 3), ((1, 5), 0), ((2, 1), 0), ((2, 2), 0), ((2, 3), 3),
             ((2, 4), 3), ((2, 5), 0), ((2, 6), 0), ((2, 7), 3)])
        self.frame0GT = map_to_cells(1, [(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4), (5, 5, 5)])
        self.frame1GT = map_to_cells(2, [(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4), (5, 5, 5), (6, 6, 6), (7, 7, 7)])
        self.frame0Res = map_to_cells(1, [(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4)])
        self.frame1Res = map_to_cells(2, [(1, 1, 1), (2, 2, 2), (5, 5, 5), (3, 3, 3), (7, 7, 7)])

        self.frame0Mapping = [(self.frame0GT[0], self.frame0Res[0]), (self.frame0GT[1], self.frame0Res[1]),
                              (self.frame0GT[2], self.frame0Res[2]), (self.frame0GT[3], self.frame0Res[3])]
        self.frame1Mapping = [(self.frame1GT[0], self.frame1Res[0]), (self.frame1GT[1], self.frame1Res[1]),
                              (self.frame1GT[2], self.frame1Res[3]),
                              (self.frame1GT[4], self.frame1Res[2]), (self.frame1GT[6], self.frame1Res[4])]

    def apply_colours(self, data, colours):
        for cell in data:
            key = (cell.frame_number, cell.cell_id)
            if key in colours:
                cell.colour = colours[key]
            else:
                cell.colour = 0

    def test_find_correspondence_with_overlap_usage(self):
        gt = [c for _, c in MaskImageParser().load_from_file(TestMaskImageParser.RESULT_GT_PATH)]
        self.assertEqual(2, len(gt))
        algo = [c for _, c in LabelImageParser().load_from_file(TestMaskImageParser.RESULT_ALGO_PATH)]
        self.assertEqual(2, len(algo))

        plot_comparison.cutoff_iou = 0.1
        matching = plot_comparison.find_correspondence(gt, algo)
        self.assertEqual(2, len(matching))

        plot_comparison.cutoff_iou = 0.6
        matching = plot_comparison.find_correspondence(gt, algo)
        self.assertEqual(1, len(matching))

        plot_comparison.cutoff_iou = 0.9
        matching = plot_comparison.find_correspondence(gt, algo)
        self.assertEqual(0, len(matching))

    def test_calculate_stats_tracking(self):
        # (last_gt,last_res),last_mapping,(new_gt,new_res),new_mapping
        # len(found_links), len(real_links), len(correct_links))
        self.apply_colours(self.frame1Res, self.dictionary_colour)
        self.apply_colours(self.frame1GT, self.dictionary_colour)
        wyniki = plot_comparison.calculate_stats_tracking((self.frame0GT, self.frame0Res), self.frame0Mapping,
                                                          (self.frame1GT, self.frame1Res), self.frame1Mapping)
        self.assertEqual([2, 3, 2], list(map(len, wyniki[:3])))
        # precision = 100%
        # recall = 66%

        # no colours
        self.apply_colours(self.frame1Res, {})
        self.apply_colours(self.frame1GT, {})
        wyniki = plot_comparison.calculate_stats_tracking((self.frame0GT, self.frame0Res), self.frame0Mapping,
                                                          (self.frame1GT, self.frame1Res), self.frame1Mapping)
        self.assertEqual([3, 5, 3], list(map(len, wyniki[:3])))
        # precision = 100%
        # recall = 60%

    def test_calculate_stats_segmentation(self):
        """
        ground_truth_frame, results_frame
        Input: [(cell_id, position_x, position_y)] x2
        Result: (cell_count_results, cell_count_ground_truth, correspondences, false_positives, false_negatives)
        """
        self.apply_colours(self.frame0Res, self.dictionary_colour)
        self.apply_colours(self.frame0GT, self.dictionary_colour)
        wyniki = plot_comparison.calculate_stats_segmentation(self.frame0GT, self.frame0Res)
        self.assertEqual((2, 3), wyniki[:2])
        self.assertEqual(2, len(wyniki[2]))
        # precision = 100%
        # recall = 66%

        self.apply_colours(self.frame0Res, {})
        self.apply_colours(self.frame0GT, {})
        wyniki = plot_comparison.calculate_stats_segmentation(self.frame0GT, self.frame0Res)
        self.assertEqual((4, 5), wyniki[:2])
        self.assertEqual(4, len(wyniki[2]))
        # precision = 100%
        # recall = 80%!

        self.apply_colours(self.frame1Res, self.dictionary_colour)
        self.apply_colours(self.frame1GT, self.dictionary_colour)
        wyniki = plot_comparison.calculate_stats_segmentation(self.frame1GT, self.frame1Res)
        self.assertEqual((3, 4), wyniki[:2])
        self.assertEqual(3, len(wyniki[2]))
        # precision = 100%
        # recall = 75%

        self.apply_colours(self.frame1Res, {})
        self.apply_colours(self.frame1GT, {})
        wyniki = plot_comparison.calculate_stats_segmentation(self.frame1GT, self.frame1Res)
        self.assertEqual((5, 7), wyniki[:2])
        self.assertEqual(5, len(wyniki[2]))
        # precision = 100%
        # recall = 71%

