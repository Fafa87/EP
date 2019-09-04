import unittest

import fire
from mock import patch

import ep.evalplatform.plot_comparison
from ep.evalplatform.compatibility import plot_comparison_legacy_parse


class TestLegacyPlotComparisonCompatibility(unittest.TestCase):
    def assert_parse_equal(self, args, args_new=None):
        org_run_script = ep.evalplatform.plot_comparison.run_script
        args_new = args_new or args
        with patch('ep.evalplatform.plot_comparison.run_script', autospec=True) as run_script_mock:
            # run legacy parsing
            params = plot_comparison_legacy_parse(args, ep.evalplatform.plot_comparison.input_type)
            ep.evalplatform.plot_comparison.run_script(**params)
            legacy_params = run_script_mock.call_args.kwargs

            # run brand new Fire
            fire.Fire(ep.evalplatform.plot_comparison.run_script, args_new[1:])
            new_params_args = dict(zip(org_run_script.func_code.co_varnames, run_script_mock.call_args.args))
            new_params = run_script_mock.call_args.kwargs
            new_params.update(new_params_args)

            # compare the parsed parameters
            self.assertEqual(legacy_params, new_params)

    def test_legacy_parser(self):
        args = ['file.py', r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv',
                r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT', 'CellProfiler',
                r'Results\Ground Truth\Ground TruthSeg_GroundTruthCenters.csv']
        parsed_args = plot_comparison_legacy_parse(args, ep.evalplatform.plot_comparison.input_type)
        self.assertEqual(args[1], parsed_args.ground_truth_csv_file)
        self.assertEqual(args[2], parsed_args.algorithm_results_csv_file)
        self.assertEqual(args[3], parsed_args.algorithm_results_type)
        self.assertEqual(args[4], parsed_args.algorithm_name)
        self.assertEqual(args[5], parsed_args.ground_truth_seg_csv_file)

    def test_legacy_compatibility(self):
        args = ['file.py', r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv',
                r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT', 'CellProfiler',
                r'Results\Ground Truth\Ground TruthSeg_GroundTruthCenters.csv']
        self.assert_parse_equal(args)

        args = ['file.py', r'/OutputStd', r'/Input', r'input_folder', r'input_par',
                r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv',
                r'/SegOnly',
                r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT', 'CellProfiler']
        args_new = ['file.py', '--output_summary_stdout',
                    '--input_directory', 'input_folder', '--input_file_part', 'input_par',
                    r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv',
                    '--evaluate_tracking=False',
                    r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT', 'CellProfiler']
        self.assert_parse_equal(args, args_new)

        args_new = ['file.py', r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv',
                    r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT', 'CellProfiler',
                    '--input_directory', 'input_folder', '--input_file_part', 'input_par',
                    '--evaluate_tracking=False', '--output_summary_stdout']
        self.assert_parse_equal(args, args_new)

        args = ['file.py', r'/OutputStd', r'/Input', r'input_folder', r'input_par',
                r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv', 'CT',
                r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT', 'CellProfiler']
        args_new = ['file.py', r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv',
                    r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT', 'CellProfiler',
                    '--ground_truth_special_parser', 'CT',
                    '--input_directory', 'input_folder', '--input_file_part', 'input_par',
                    '--output_summary_stdout']
        self.assert_parse_equal(args, args_new)

        args = ['file.py', r'/Input', r'input_folder', r'input_par',
                r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv', 'CT',
                r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT']
        args_new = ['file.py', r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv',
                    r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT',
                    '--ground_truth_special_parser', 'CT',
                    '--input_directory', 'input_folder', '--input_file_part', 'input_par']
        self.assert_parse_equal(args, args_new)

        args = ['file.py',
                r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv', 'CT',
                r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT']
        args_new = ['file.py', r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv',
                    '--ground_truth_special_parser', 'CT',
                    r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT']
        self.assert_parse_equal(args, args_new)

        args = ['file.py',
                r'Results\Ground Truth\Ground Truth_GroundTruthCenters.csv',
                r'Results\CellProfiler\DefaultOUT_FilteredBlue.csv', 'CPT']
        self.assert_parse_equal(args)
