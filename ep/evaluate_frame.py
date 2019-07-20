import sys

import ep.evalplatform.plot_comparison as simple_eval


def evaluate_one_frame(gt_file_path, result_file_path, algo_name, parser_symbol="PLATFORM_DEF", image_size=(100000, 100000)):
    """
    Assumes that gt_file_path and result_file_path have format parsable by parser of provided symbol.
    """
    gt_data = simple_eval.read_ground_truth(gt_file_path)
    res_data = simple_eval.read_results(result_file_path, simple_eval.input_type[parser_symbol], algo_name)

    gt_single_data = [a[1] for a in gt_data]
    res_single_data = [a[1] for a in res_data[1]]

    # TODO future option , image_size)
    (cr, cg, corr, fp, fn) = simple_eval.calculate_stats_segmentation(gt_single_data, res_single_data)

    results_seg_summary = simple_eval.calculate_precision_recall_F_metrics(cr, cg, len(corr))
    metrics = {'Precision': results_seg_summary[0], 'Recall': results_seg_summary[1], 'F': results_seg_summary[2]}
    evaluation_details = {'Correct': corr, 'FalsePositive': fp, 'FalseNegative': fn}

    return metrics, evaluation_details


def show_details_one_frame(input_image, details, output_path):
    # TODO if necessary, below is sample example
    """
    simple_eval.write_to_file_printable(reduce_plus(segmentation_details), details_path)
    output_file_prefix = "SegDetails_"
    overlord = draw_details.EvaluationDetails([details_path, input_file_part])
    output_drawings_directory = ensure_directory_in(details_path, SEG_DRAWING_FOLDER)
    draw_details.run(overlord, input_directory, output_drawings_directory, output_file_prefix)
    debug_center.show_in_console(None, "Progress", "Done drawing detailed segmentation results...")
    """
    pass


if __name__ == '__main__':
    assert len(sys.argv) == 4
    (metrics, _) = evaluate_one_frame(sys.argv[1], sys.argv[2], sys.argv[3])
    print (metrics)
