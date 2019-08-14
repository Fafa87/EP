from __future__ import division # so that a / b == float(a) / b
import sys
import os
from itertools import *

from ep.evalplatform.utils import*
from ep.evalplatform.parsers import*
from ep.evalplatform.parsers_image import*
from ep.evalplatform.yeast_datatypes import CellOccurence
from ep.evalplatform import draw_details

SEGMENTATION_GNUPLOT_FILE = "plot_segmentation.plt"
TRACKING_GNUPLOT_FILE = "plot_tracking.plt"

parsers = [DefaultPlatformParser(), OldGroundTruthParser(), CellProfilerParser(), CellProfilerParserTracking(), CellTracerParser(), CellIDParser(), TrackerParser(), CellSerpentParser(), CellStarParser(),
CellProfilerParserTrackingOLDTS2(), LabelImageParser(), MaskImageParser([2,3])
]
input_type =  dict([(p.symbol,p) for p in parsers])

ground_truth_parser = OldGroundTruthParser()

# Max match distance. Read from: evaluation.ini at program folder then use this default.
loaded_ini = False
cutoff = 30  # pixels
cutoff_iou = 0.3  # intersection / union
output_evaluation_details = 0
draw_evaluation_details = 0
fill_markers = False
markersize = 7
ignored_frame_size = 0
all_data_evaluated = 0
wide_plots = 0

def filter_border(celllist, image_size = (10000,10000)):
    if(celllist == []):
        return []
    if(isinstance(celllist[0],CellOccurence)):
        def close_to_border(cell, limits):
            return not (ignored_frame_size <= cell.position[0] <= (limits[0] - ignored_frame_size) and
                        ignored_frame_size <= cell.position[1] <= (limits[1] - ignored_frame_size))

        return [cell for cell in celllist if not cell.obligatory() or close_to_border(cell, image_size) ]
    elif(len(celllist[0]) == 2):
        return [(cell_A, cell_B) for (cell_A, cell_B) in celllist if not cell_A.obligatory() or not cell_B.obligatory()]
    else:
        print (celllist)

def read_ground_truth(path, parser=None):
    """
    Returns::
        [Cell]
    """
    parser = parser or ground_truth_parser
    debug_center.show_in_console(None,"Progress","Reading ground truth data...")
    debug_center.show_in_console(None,"Tech","".join(["Uses ", parser.__class__.__name__, " parser..."]))
    cells = parser.load_from_file(path)
    debug_center.show_in_console(None,"Progress","Done reading ground truth data...")
    return cells

def make_all_cells_important(frame_cells):
    for frame_cell in frame_cells:
        frame_cell[1].colour = 0

def read_results(path, parser, name):
    """
    Returns::
        (algorithm_name,[Cell])
    """
    debug_center.show_in_console(None,"Progress","".join(["Reading ", name, " results data..."]))
    debug_center.show_in_console(None,"Tech","".join(["Uses ", parser.__class__.__name__, " parser..."]))
    cells = parser.load_from_file(path)
    make_all_cells_important(cells) # cells cannot use colour temporary
    debug_center.show_in_console(None,"Progress","".join(["Done reading ", name, " result data..."]))
    return (name,cells)

def write_to_file_tracking(stats, path):
    data_sets = ([],[],[])
    for (f,(p,r,ff)) in stats:
        f_short = str(f)[:20]
        data_sets[0].append((f_short,p))
        data_sets[1].append((f_short,r))
        data_sets[2].append((f_short,ff))
    write_to_file(data_sets,path)

def write_to_file_segmentation(stats, path):
    data_sets = ([],[],[],[])
    for (f,(a,b,c,d)) in stats:
        f_short = str(f)[:20]
        data_sets[0].append((f_short,a))
        data_sets[1].append((f_short,b))
        data_sets[2].append((f_short,c))
        data_sets[3].append((f_short,d))
    write_to_file(data_sets,path)

def write_to_file_printable(details, path):
    if details != []:
        headers = details[0].csv_headers()
        records = [d.csv_record() for d in details]
        write_to_csv(headers,records,path)
    else:
        write_to_csv(["No details!"],[],path)

def format_prF(title, params):
    (precision, recall, F) = params
    return [title,"Precision: " + str(precision), "Recall: " + str(recall), "F: " + str(F)]

def format_summary(algorithm, segmentation,tracking,long_tracking):
    lines = ["Algorithm: " + algorithm]
    lines += format_prF("Segmentation:", segmentation[1:])
    if len(tracking)!=0:
        lines += format_prF("Tracking:",tracking)
    if len(long_tracking)!=0:
        lines += format_prF("Long-time tracking:",long_tracking)
    return "\n".join(lines)

def write_summary(algorithm, segmentation,tracking,long_tracking, path):
    file = open(path,"w")
    summary = format_summary(algorithm,segmentation,tracking,long_tracking)
    file.write(summary)
    file.close()

def distance(cell_a, cell_b):
    return ((cell_a.position[0]-cell_b.position[0])**2 + (cell_a.position[1]-cell_b.position[1])**2)**0.5

def find_correspondence(ground_truth, results):
    """
    Greadily match if distance close enough
    Input: [Cell] x2
    Matching:
    [(ground_truth_cell, results_cell)]  -> can easily calculate false positives/negatives and cell count + tracking
    """
    edges = [(g.similarity(r),(g,r)) for g in ground_truth for r in results if g.is_similar(r, cutoff, cutoff_iou)]
    correspondences = []
    matchedGT = set([])
    matchedRes = set([])

    for (d,(a,b)) in sorted(edges, key=lambda x: -x[0]):
        if not b in matchedRes:
            if not a in matchedGT:
                correspondences.append((a,b))
                matchedGT.add(a)
            matchedRes.add(b)

    return correspondences

def calculate_stats_segmentation(ground_truth_frame, results_frame, image_size = (100000,100000)):
    """
    Input: [Cell] x2
    Result: (cell_count_results, cell_count_ground_truth, correspondences, false_positives, false_negatives)
    """
    load_general_ini(CONFIG_FILE)

    border_results = filter_border(results_frame, image_size)
    for c in border_results:
        c.colour = 1

    border_groundtruth = filter_border(ground_truth_frame, image_size)
    for c in border_groundtruth:
        c.colour = 1

    correspondence = find_correspondence(ground_truth_frame, results_frame)
    border_correspondence = filter_border(correspondence, image_size)

    matched_GT = [gt for gt,_ in correspondence]
    matched_res = [res for _,res in correspondence]

    matched_border_GT = [gt for gt, _ in border_correspondence]
    matched_border_res = [res for _, res in border_correspondence]

    correct_results = [SegmentationResult(gt,res) for (gt,res) in correspondence if (gt,res) not in border_correspondence]
    obligatory_results = [res for res in results_frame if res not in border_results and res not in matched_border_res]
    obligatory_gt = [gt for gt in ground_truth_frame if gt not in border_groundtruth and gt not in matched_border_GT]
    false_negatives = [SegmentationResult(gt,None) for gt in ground_truth_frame if gt not in border_groundtruth and gt not in matched_GT]
    false_positives = [SegmentationResult(None,res) for res in results_frame if res not in border_results and res not in matched_res]

    return (len(obligatory_results),len(obligatory_gt),
            correct_results,
            false_positives,
            false_negatives)

def calculate_precision_recall_F_metrics(algorithm_number, real_number, correct_number):
    """
    Result: (precision, recall, F)
    """
    if algorithm_number == 0:
        precision = 0
    else:
        precision = float(correct_number)/algorithm_number
    if real_number == correct_number: # 0 / 0
        recall = 1
    else:
        recall = float(correct_number)/real_number
    return (precision, recall, 2*float(correct_number)/(real_number+algorithm_number))   #precision*recall/(precision+recall))

def calculate_metrics_segmentation(params):
    """
    Input: (cell_count_results, cell_count_ground_truth, correspondences, false_positives, false_negatives)
    Result: (cell_count_results/cell_count_ground_truth, precision, recall, F)
    """
    (cell_count_results, cell_count_ground_truth, correspondences, false_positives, false_negatives) = params
    prf = calculate_precision_recall_F_metrics(cell_count_results, cell_count_ground_truth, correspondences)

    if cell_count_ground_truth == 0:
        return tuple([0]) + prf

    return tuple([float(cell_count_results)/cell_count_ground_truth]) + prf

def calculate_stats_tracking(params_last,last_mapping,params_new,new_mapping):
    """
    (found_links, real_links, correct_links, false_positive, false_negative)
    1 to 1 correspondence version
    """
    (last_gt, last_res) = params_last
    (new_gt, new_res) = params_new

    # ignore non obligatory GT cells
    last_gt = [c for c in last_gt if c.obligatory()]
    new_gt = [c for c in new_gt if c.obligatory()]

    # leaves only cell from results the ones matched with the obligatory cells or not matched at all
    last_res = [c for c in last_res if (last_mapping == [] or (c not in list(zip(*last_mapping))[1])) or (list(zip(*last_mapping))[0][list(zip(*last_mapping))[1].index(c)].obligatory())] # searches in [(a,b)] for the a when given b.
    new_res = [c for c in new_res if (new_mapping == [] or (c not in list(zip(*new_mapping))[1])) or (list(zip(*new_mapping))[0][list(zip(*new_mapping))[1].index(c)].obligatory())]

    # ignore mapping connected to the non-obligatory GT cells 
    last_mapping = [(gt,res) for (gt,res) in last_mapping if gt.obligatory()]
    new_mapping = [(gt,res) for (gt,res) in new_mapping if gt.obligatory()]

    # find links and make pairs of cells in results with the same unique_id in GT
    number_change = [(last[1],new[1],last[0],new[0]) for last in last_mapping for new in new_mapping if last[0].unique_id==new[0].unique_id]
    correct_links = [(TrackingLink(l_res,n_res),TrackingLink(l_gt,n_gt)) for (l_res,n_res,l_gt,n_gt) in number_change
                        if l_res.unique_id == n_res.unique_id]

    # find the number of existing links
    real_links = [TrackingLink(last,new) for last in last_gt for new in new_gt if last.unique_id==new.unique_id]
    found_links = [TrackingLink(last,new) for last in last_res for new in new_res if last.unique_id==new.unique_id]

    correct_results = [TrackingResult(link_gt,link_res) for (link_res,link_gt) in correct_links]
    false_negatives = [TrackingResult(gt,None) for gt in real_links if correct_links == [] or gt not in list(zip(*correct_links))[1]]
    false_positives = [TrackingResult(None,res) for res in found_links if correct_links == [] or res not in list(zip(*correct_links))[0]]

    return (found_links, real_links, correct_results, false_positives, false_negatives) # evaluation_details


def load_general_ini(path):
    global cutoff, cutoff_iou, draw_evaluation_details, ignored_frame_size, \
        loaded_ini, fill_markers, markersize, all_data_evaluated

    if read_ini(path, 'evaluation', 'maxmatchdistance') != '':
        cutoff = float(read_ini(path, 'evaluation', 'maxmatchdistance'))
    if read_ini(path, 'evaluation', 'miniousimilarity') != '':
        cutoff_iou = float(read_ini(path, 'evaluation', 'miniousimilarity'))
    if read_ini(path, 'evaluation', 'drawevaluationdetails') != '':
        draw_evaluation_details = float(read_ini(path, 'evaluation', 'drawevaluationdetails'))
    if read_ini(path, 'evaluation', 'ignoredframesize') != '':
        ignored_frame_size = float(read_ini(path, 'evaluation', 'ignoredframesize'))
    if read_ini(path, 'evaluation', 'alldataevaluated') != '':
        all_data_evaluated = bool(int(read_ini(path, 'evaluation', 'alldataevaluated')))

    if read_ini(path, 'details', 'fill_markers') != '':
        fill_markers = bool(int(read_ini(path, 'details', 'fill_markers')))
    if read_ini(path, 'details', 'markersize') != '':
        markersize = int(read_ini(path, 'details', 'markersize'))


def run_script(args):
    global ground_truth_parser, output_evaluation_details, wide_plots

    if(len(args) < 4):
        print("".join(["Parameters: \n<ground_truth_csv_file> {/SegOnly} {<ground_truth_type>} <algorithm_results_csv_file> <algorithm_results_type> [algorithm_name] [ground_truth_seg_csv_file]" ]))
    else:
        load_general_ini(CONFIG_FILE)
        if read_ini(CONFIG_FILE,'evaluation','outputevaluationdetails') != '':
            output_evaluation_details = float(read_ini(CONFIG_FILE,'evaluation','outputevaluationdetails'))
        if read_ini(CONFIG_FILE,'plot','terminal') != '':
            terminal_type = read_ini(CONFIG_FILE,'plot','terminal').strip()
        if read_ini(CONFIG_FILE, 'plot', 'wideplots') != '':
            wide_plots = bool(int(read_ini(CONFIG_FILE, 'plot', 'wideplots')))

        debug_center.configure(CONFIG_FILE)

        output_summary_stdout = 0
        if args[1] == "/OutputStd":
            output_summary_stdout = 1
            args = args[:1] + args[2:]

        input_directory = None
        input_file_part = None
        if args[1] == "/Input":
            input_directory,input_file_part = args[2],args[3]
            args = args[:1] + args[4:]

        ground_truth_csv_file = args[1]

        evaluate_tracking = 1
        if args[2] == "/SegOnly":
            evaluate_tracking = 0
            args = args[:2] + args[3:]

        if args[2] in input_type:
            ground_truth_parser = input_type[args[2]]
            args = args[:2] + args[3:]

        algorithm_results_csv_file = args[2]
        algorithm_results_type = args[3]

        if algorithm_results_type not in input_type:
            debug_center.show_in_console(None,"Error","ERROR: " + algorithm_results_type + " is not supported. There are supported types: " + str(input_type))
            sys.exit()
        else:
            parser = input_type[algorithm_results_type]

        algorithm_name = "Algorithm"
        if(len(args) > 4):
            algorithm_name = args[4]
        debug_center.show_in_console(None,"Info","".join(["Algorithm name: ", algorithm_name]))
        filtered_algorithm_name = ''.join([c for c in algorithm_name if c.isalnum()])

        ground_truth_seg_csv_file = ground_truth_csv_file
        if len(args) == 6:
            ground_truth_seg_csv_file = args[5]

        results_data = read_results(algorithm_results_csv_file,parser,algorithm_name)

        def read_GT(ground_truth_csv_file, tracking = False):
            ground_truth_data = read_ground_truth(ground_truth_csv_file)
            # filter data without tracking GT
            if tracking:
                ground_truth_data = [(f,cell) for (f,cell) in ground_truth_data if cell.has_tracking_data() ]

            # use all frames with data or just frames where both gt and algo results
            gt_set = set([item[0] for item in ground_truth_data])
            res_set = set([item[0] for item in results_data[1]])
            list_of_frames = sorted(gt_set | res_set if all_data_evaluated else gt_set & res_set)

            if(list_of_frames == []):
                debug_center.show_in_console(None,"Error","ERROR: No ground truth data! Intersection of ground truth and results is empty!")
                sys.exit()
            data_per_frame = dict([(frame,( [g[1] for g in ground_truth_data if g[0] == frame],
                                            [r[1] for r in results_data[1] if r[0] == frame and not (tracking and not r[1].has_tracking_data())]))
                                            for frame in list_of_frames])
            return ground_truth_data,list_of_frames,data_per_frame

        ground_truth_data,list_of_frames,data_per_frame = read_GT(ground_truth_seg_csv_file)

        debug_center.show_in_console(None,"Progress","Evaluating segmentation...")
        stats = []
        segmentation_details = []
        image_sizes = {}

        if output_evaluation_details and draw_evaluation_details:
            overlord = draw_details.EvaluationDetails(SEGDETAILS_SUFFIX, input_file_part)
            image_sizes = draw_details.get_images_sizes(overlord, input_directory)

        for frame in list_of_frames:
            image_size = image_sizes.get(frame, (100000, 100000))

            (cr,cg,corr,fp,fn) = calculate_stats_segmentation(data_per_frame[frame][0],data_per_frame[frame][1], image_size)
            segmentation_details += (corr,fp,fn)
            stats.append((frame,(cr,cg,len(corr),len(fp),len(fn))))

        (crs,cgs,corrs) = (0,0,0)
        for (f,(cr,cg,corr,fp,fn)) in stats:
            crs += cr
            cgs += cg
            corrs += corr

        results_seg_summary = calculate_metrics_segmentation((crs,cgs,corrs,0,0))
        debug_center.show_in_console(None,"Progress","Done evaluating segmentation...")

        summary_path = algorithm_results_csv_file + "." + filtered_algorithm_name + SUMMARY_SUFFIX
        tmp_path = algorithm_results_csv_file + "." + filtered_algorithm_name + SEGPLOTDATA_SUFFIX
        plot_path = algorithm_results_csv_file + "." + filtered_algorithm_name + SEGPLOT_SUFFIX
        details_path = algorithm_results_csv_file + "." + filtered_algorithm_name + SEGDETAILS_SUFFIX

        debug_center.show_in_console(None,"Progress","Ploting segmentation results...")
        write_to_file_segmentation([(stat[0],calculate_metrics_segmentation(stat[1])) for stat in stats], tmp_path)

        # Setup terminal.
        term_set, output_file_extension = setup_ploting_terminal(terminal_type, stats, wide_plots)

        plot_path_no_ext = os.path.splitext(plot_path)[0]
        plot_file = package_path(SEGMENTATION_GNUPLOT_FILE)

        ploting= "gnuplot -e " + "\"data_file='{}';plot_title='{}';output_file='{}';set terminal {};output_file_extension='{}';\"".format(tmp_path,algorithm_name,plot_path_no_ext,term_set,output_file_extension) + " " + plot_file
        os.system(ploting)
        debug_center.show_in_console(None,"Progress","Done ploting segmentation results...")

        if output_evaluation_details:
            debug_center.show_in_console(None,"Progress","Printing detailed segmentation results...")
            write_to_file_printable(reduce_plus(segmentation_details), details_path)
            debug_center.show_in_console(None,"Progress","Done printing detailed segmentation results...")
            if draw_evaluation_details:
                if not (input_directory is None or input_file_part is None):
                    debug_center.show_in_console(None,"Progress","Drawing detailed segmentation results...")
                    output_file_prefix = "SegDetails_"
                    overlord = draw_details.EvaluationDetails(details_path,
                                                              required_substring=input_file_part,
                                                              fill_markers=fill_markers,
                                                              markersize=markersize)
                    output_drawings_directory = ensure_directory_in(details_path,SEG_DRAWING_FOLDER)
                    draw_details.run(overlord, input_directory, output_drawings_directory, output_file_prefix)
                    debug_center.show_in_console(None,"Progress","Done drawing detailed segmentation results...")
                else:
                    debug_center.show_in_console(None,"Info","Skipping evaluation details drawing despite parameters as no input images were provided.")

        else:
            debug_center.show_in_console(None,"Info","Skipping evaluation details printing as desired by parameters.")

        if evaluate_tracking == 1:
            ground_truth_data,list_of_frames,data_per_frame = read_GT(ground_truth_csv_file, True)

            debug_center.show_in_console(None,"Progress","Evaluating tracking...")
            stats_tracking = []
            tracking_details = []
            data = data_per_frame[list_of_frames[0]]
            last_data = data
            last_correspondence = find_correspondence(data[0], data[1])
            #last_frame_id = list_of_frames[0]
            # collect all evalustion details
            for frame in list_of_frames[1:]:
                data = data_per_frame[frame]
                new_correspondence = find_correspondence(data[0], data[1])

                (tcr,tcg,tcorr,tfp,tfn) = calculate_stats_tracking(last_data,last_correspondence,data,new_correspondence)
                tracking_details += (tcorr,tfp,tfn)

                stats_tracking.append((frame,(len(tcr),len(tcg),len(tcorr))))
                last_correspondence = new_correspondence
                last_data = data

            (tcrs,tcgs,tcorrs) = (0,0,0)
            for (f,(tcr,tcg,tcorr)) in stats_tracking:
                tcrs += tcr
                tcgs += tcg
                tcorrs += tcorr

            results_track_summary = calculate_precision_recall_F_metrics(tcrs,tcgs,tcorrs)
            debug_center.show_in_console(None,"Progress","Done evaluating tracking...")

            tmp_path = algorithm_results_csv_file + "." + filtered_algorithm_name + TRACKPLOTDATA_SUFFIX
            plot_path = algorithm_results_csv_file + "." + filtered_algorithm_name + TRACKPLOT_SUFFIX
            details_path = algorithm_results_csv_file + "." + filtered_algorithm_name + TRACKDETAILS_SUFFIX

            debug_center.show_in_console(None,"Progress","Ploting tracking results...")
            write_to_file_tracking([(stat[0],calculate_precision_recall_F_metrics(*stat[1])) for stat in stats_tracking], tmp_path)

            plot_path_no_ext = os.path.splitext(plot_path)[0]
            plot_file = package_path(TRACKING_GNUPLOT_FILE)
            ploting= "gnuplot -e " + "\"data_file='{}';plot_title='{}';output_file='{}';set terminal {};output_file_extension='{}';\"".format(tmp_path,algorithm_name,plot_path_no_ext,term_set,output_file_extension) + " " + plot_file

            os.system(ploting)
            debug_center.show_in_console(None,"Progress","Done ploting tracking results...")

            if output_evaluation_details:
                debug_center.show_in_console(None,"Progress","Printing detailed tracking results...")
                write_to_file_printable(reduce_plus(tracking_details), details_path)
                debug_center.show_in_console(None,"Progress","Done printing detailed tracking results...")
                if draw_evaluation_details:
                    if not (input_directory is None or input_file_part is None):
                        debug_center.show_in_console(None,"Progress","Drawing detailed tracking results...")
                        output_file_prefix = "TrackDetails_"
                        overlord = draw_details.EvaluationDetails(details_path,
                                                                  required_substring=input_file_part,
                                                                  fill_markers=fill_markers,
                                                                  markersize=markersize)
                        output_drawings_directory = ensure_directory_in(details_path,TRACK_DRAWING_FOLDER)
                        draw_details.run(overlord, input_directory, output_drawings_directory, output_file_prefix)
                        debug_center.show_in_console(None,"Progress","Done drawing detailed tracking results...")
                    else:
                        debug_center.show_in_console(None,"Info","Skipping evaluation details drawing despite parameters as no input images were provided.")
            else:
                debug_center.show_in_console(None,"Info","Skipping evaluation details printing as desired by parameters.")

            # Calculate additional long-time tracking measure
            if(len(data_per_frame)>2):
                debug_center.show_in_console(None,"Progress","Evaluating long-time tracking...")
                long_tracking_details = []

                first_data = data_per_frame[list_of_frames[0]]
                first_correspondence = find_correspondence(first_data[0], first_data[1])

                last_data = data_per_frame[list_of_frames[-1]]
                last_correspondence = find_correspondence(last_data[0], last_data[1])

                (lcr,lcg,lcorr,lfp,lfn) = calculate_stats_tracking(first_data,first_correspondence,last_data,last_correspondence)
                results_long_track_summary = calculate_precision_recall_F_metrics(len(lcr),len(lcg),len(lcorr))
                long_tracking_details += (lcorr,lfp,lfn)

                details_path = algorithm_results_csv_file + "." + filtered_algorithm_name + LONGTRACKDETAILS_SUFFIX
                if output_evaluation_details:
                    debug_center.show_in_console(None,"Progress","Printing detailed long-time tracking results...")
                    write_to_file_printable(reduce_plus(long_tracking_details), details_path)
                    debug_center.show_in_console(None,"Progress","Done printing detailed long-time tracking results...")
                    if draw_evaluation_details:
                        if not (input_directory is None or input_file_part is None):
                            debug_center.show_in_console(None,"Progress","Drawing detailed long-time tracking results...")
                            output_file_prefix = "LongTrackDetails_"
                            overlord = draw_details.EvaluationDetails(details_path,
                                                                      required_substring=input_file_part,
                                                                      fill_markers=fill_markers,
                                                                      markersize=markersize)
                            output_drawings_directory = ensure_directory_in(details_path,LONG_DRAWING_FOLDER)
                            draw_details.run(overlord, input_directory, output_drawings_directory, output_file_prefix)
                            debug_center.show_in_console(None,"Progress","Done drawing detailed long-time tracking results...")
                        else:
                            debug_center.show_in_console(None,"Info","Skipping evaluation details drawing despite parameters as no input images were provided.")
                else:
                    debug_center.show_in_console(None,"Info","Skipping evaluation details printing as desired by parameters.")

                debug_center.show_in_console(None,"Progress","Done evaluating long-time tracking...")
            else:
                debug_center.show_in_console(None,"Info","Skipping long-time tracking evaluation because there are too few frames.")
                results_long_track_summary = []
        else:
            debug_center.show_in_console(None,"Info","Skipping tracking evaluation as desired by parameters.")
            results_track_summary = []
            results_long_track_summary = []

        # save all the evaluation details if chosen to do so
        # plot the results if /PLOT directory + name
        write_summary(algorithm_name,results_seg_summary, results_track_summary, results_long_track_summary, summary_path)
        debug_center.show_in_console(None,"Progress","Done evaluating...")

        if output_summary_stdout:
            debug_center.show_in_console(None,"Result",format_summary(algorithm_name,results_seg_summary, results_track_summary, results_long_track_summary))

if __name__ == '__main__':
    run_script(sys.argv)
