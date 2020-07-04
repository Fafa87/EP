from attrdict import AttrDict


def plot_comparison_legacy_parse(args, input_type):
    """
    Parse args and return AttrDict with parameters:
    - output_summary_stdout: if OutputStd is specified or not existent
    - input_directory: directory with input image data or not existent
    - input_file_part: substring present in input file part or not existent
    - evaluate_tracking: 0 if tracking should not be evaluated or not existent
    - ground_truth_special_parser: ground truth parser
    - algorithm_name: friendly name of the evaluated algorithm or not existent
    - algorithm_results_csv_file: path to csv file with algorithm results
    - algorithm_results_type: type of the algorithm results
    - ground_truth_seg_csv_file: separate ground truth csv file with segmentation or not existent
    """
    parsed_args = AttrDict()
    if len(args) < 4:
        print("".join([
                          "Parameters: \n<ground_truth_csv_file> {/SegOnly} {<ground_truth_type>} <algorithm_results_csv_file> <algorithm_results_type> [algorithm_name] [ground_truth_seg_csv_file]"]))
        return None
    else:
        if args[1] == "/OutputStd":
            parsed_args.output_summary_stdout = True
            args = args[:1] + args[2:]
        else:
            parsed_args.output_summary_stdout = False

        if args[1] == "/Input":
            parsed_args.input_directory, parsed_args.input_file_part = args[2], args[3]
            args = args[:1] + args[4:]

        parsed_args.ground_truth_csv_file = args[1]

        if args[2] == "/SegOnly":
            parsed_args.evaluate_tracking = False
            args = args[:2] + args[3:]
        else:
            parsed_args.evaluate_tracking = True

        if args[2] in input_type:
            parsed_args.ground_truth_special_parser = args[2]
            args = args[:2] + args[3:]

        parsed_args.algorithm_results_csv_file = args[2]
        parsed_args.algorithm_results_type = args[3]

        if len(args) > 4:
            parsed_args.algorithm_name = args[4]

        if len(args) == 6:
            parsed_args.ground_truth_seg_csv_file = args[5]

    return parsed_args
