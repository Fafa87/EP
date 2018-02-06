import unittest
import sys
import os

from ep.evalplatform import plot_comparison


class TestColours(unittest.TestCase):
    # 3 proper cells in GT + 3 border ones
    # GT = 3 | 2 -> 4 | 3
    # Algo = 2 | 2 -> 3 | 2
    dictionary_colour = {}
    def setUp(self):
        self.dictionary_colour = dict([((1,1),0),((1,2),0),((1,3),3),((1,4),3),((1,5),0),((2,1),0),((2,2),0),((2,3),3),((2,4),3),((2,5),0),((2,6),0),((2,7),3)])
        self.frame0GT = [(1,1,1),(2,2,2),(3,3,3),(4,4,4),(5,5,5)]
        self.frame1GT = [(1,1,1),(2,2,2),(3,3,3),(4,4,4),(5,5,5),(6,6,6),(7,7,7)]
        self.frame0Res = [(1,1,1),(2,2,2),(3,3,3),(4,4,4)]
        self.frame1Res = [(1,1,1),(2,2,2),(5,5,5),(3,3,3),(7,7,7)]

        self.frame0Mapping = [((1,1,1),(1,1,1)),((2,2,2),(2,2,2)),((3,3,3),(3,3,3)),((4,4,4),(4,4,4))]
        self.frame1Mapping = [((1,1,1),(1,1,1)),((2,2,2),(2,2,2)),((3,3,3),(3,3,3)),((5,5,5),(5,5,5)),((7,7,7),(7,7,7))]


    def test_calculate_stats_tracking(self):
        # (last_gt,last_res),last_mapping,(new_gt,new_res),new_mapping
        # len(found_links), len(real_links), len(correct_links))
        plot_comparison.frame_id = 2
        plot_comparison.dictionary_colour = self.dictionary_colour
        wyniki = plot_comparison.calculate_stats_tracking((self.frame0GT,self.frame0Res),self.frame0Mapping,(self.frame1GT,self.frame1Res),self.frame1Mapping)
        self.assertEqual((2,3,2),wyniki)
        # precision = 100%
        # recall = 66%

        # no colours
        plot_comparison.dictionary_colour = dict([(a,0) for (a,x) in self.dictionary_colour.items()])
        wyniki = plot_comparison.calculate_stats_tracking((self.frame0GT,self.frame0Res),self.frame0Mapping,(self.frame1GT,self.frame1Res),self.frame1Mapping)
        self.assertEqual((3,5,3),wyniki)
        # precision = 100%
        # recall = 60%

    def test_calculate_stats_segmentation(self):
        """
        ground_truth_frame, results_frame
        Input: [(cell_id, position_x, position_y)] x2
        Result: (cell_count_results, cell_count_ground_truth, correspondences, false_positives, false_negatives)
        """
        plot_comparison.frame_id = 1
        plot_comparison.dictionary_colour = self.dictionary_colour
        wyniki = plot_comparison.calculate_stats_segmentation(self.frame0GT,self.frame0Res)
        self.assertEqual((2,3,2),wyniki[:3])
        # precision = 100%
        # recall = 66%

        plot_comparison.dictionary_colour = dict([(a,0) for (a,x) in self.dictionary_colour.items()])
        wyniki = plot_comparison.calculate_stats_segmentation(self.frame0GT,self.frame0Res)
        self.assertEqual((4,5,4),wyniki[:3])
        # precision = 100%
        # recall = 80%!

        plot_comparison.frame_id = 2
        plot_comparison.dictionary_colour = self.dictionary_colour
        wyniki = plot_comparison.calculate_stats_segmentation(self.frame1GT,self.frame1Res)
        self.assertEqual((3,4,3),wyniki[:3])
        # precision = 100%
        # recall = 75%

        plot_comparison.dictionary_colour = dict([(a,0) for (a,x) in self.dictionary_colour.items()])
        wyniki = plot_comparison.calculate_stats_segmentation(self.frame1GT,self.frame1Res)
        self.assertEqual((5,7,5),wyniki[:3])
        # precision = 100%
        # recall = 71%

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules["__main__"])
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.system("pause")
