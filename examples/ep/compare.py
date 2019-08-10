#!/usr/bin/env python2
import sys
import os
from ep.evalplatform.utils import *
import ep.evalplatform.gather_results as comparison
from ep.evalplatform.utils import debug_center
import ep.evaluate

def find_eval(folder):
    if not os.path.isdir(folder):
        debug_center.show_in_console(None,"Error", "ERROR: Results folder ({}) do not exist!".format(folder))
        return ''
    
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f))]
    summary = [f for f in files if SUMMARY_SUFFIX in f]
    if len(summary) == 0:
        debug_center.show_in_console(None,"Error", "ERROR: No summary file found in {}".format(folder))
        return ''  
    elif len(summary) != 1:
        debug_center.show_in_console(None,"Error", "ERROR: Only one summary file expected in {}, found: {}".format(folder,len(summary)))
        return ''
    
    return summary[0][:-len(SUMMARY_SUFFIX)]
    
def find_all_created_files_paths(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f))]
    return [os.path.join(folder,f) for f in files]

if(len(sys.argv) < 3):
    print("".join(["Wrong number (" + str(len(sys.argv) - 1) + ") of arguments 1+2k required)."]))
    print("".join(sys.argv[1:]))
    print("".join(["Program usage: compare.py <results_folder> [<algorithm_subpath>]2+" ]))
    print("".join(["Alternative usage: compare.py <results_folder> <file_path_with_rest_of_params>"]))
else: 
    # Unpack parameters if passed as separate file (e.g. compare many grid search results).
    if len(sys.argv) == 3:
        with open(sys.argv[2], "r") as f:
            sys.argv = sys.argv[:2] + f.read().split("\n")

    debug_center.configure(CONFIG_FILE)
    algorithm_number = len(sys.argv)-2
    
    results_folder = os.path.join(ep.evaluate.OUTPUT_FOLDER,sys.argv[1])
    algorithm_results = []
    for i in range(algorithm_number):
        algorithm_results.append(sys.argv[i+2])
    
    path_file = [[algorithm, find_eval(os.path.join(results_folder,algorithm))] for algorithm in algorithm_results if find_eval(os.path.join(results_folder,algorithm)) != '']

    comparison.run_script(["gather_results.py",results_folder] + sum(path_file,[]))
    #os.system("python gather_results.py " + " ".join([results_folder] + sum(path_file,[])))
    
    
