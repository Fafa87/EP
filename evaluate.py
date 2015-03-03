import sys
import os
import re
import shutil
import stat

from evalplatform.utils import *
import evalplatform.plot_comparison as evaluate
from evalplatform.utils import debug_center

TMP_SUFFIX = ".tmp" # every added intermediate file has tmp suffix in the name, such files are omitted in case of evaluation.
DEFAULT_PARSER = "PLATFORM_DEF"
OUTPUT_FOLDER = "Output"
MERGED_SUFFIXES = [".tmp",".merged",".merged2"] # reeeallly?

delete_tmp = 0 # are all temporary files to be removed at the end of the evaluation? Value is read from ini file.

def find_all_files(folder,filename):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f)) and filename in f and (TMP_SUFFIX not in f) and (".track_eval" not in f and ".seg_eval" not in f and ".eval." not in f and ".eval_summary." not in f) 
     and f != filename + ".merged" 
     ]
    return files
    
def find_all_created_files_paths(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f)) and ((TMP_SUFFIX in f) or any([ s in f for s in ALL_SUFFIXES]))]
    return [os.path.join(folder,f) for f in files]

def find_all_created_directories(folder):
    directories = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder,f)) and any([ s in f for s in ALL_DIRECTORIES])]
    return [os.path.join(folder,d) for d in directories]
    
def get_trailing_number(text):
        reversed = text[::-1]
        m = re.search("\D", reversed)
        return int(reversed[:m.start()][::-1])
        
def determine_all_snaptimes(file_names):
    """Return list of times."""
    return[get_trailing_number(os.path.splitext(file)[0]) for file in file_names] 

def merge_seg_track_files(folder,files):
    """Merge two files into one, add tmp suffix if not already there."""
    file_one = open(os.path.join(folder,files[0]),"r")
    seg_all = file_one.readlines()
    seg_header,seg = seg_all[0],seg_all[1:]
    file_one.close()
    
    file_two = open(os.path.join(folder,files[1]),"r")
    tracking_all = file_two.readlines()
    tracking_header,tracking = tracking_all[0],tracking_all[1:]
    file_two.close()
    
    segment = dict([ ((int(line.split(",")[0]),int(line.split(",")[1])),line.split(",")[2:]) for line in seg])
    track = dict([ ((int(line.split(",")[0]),int(line.split(",")[1])),line.split(",")[2:]) for line in tracking])
    new_header = ",".join([seg_header] + tracking_header.split(",")[2:]).replace("\n","")
    for key in segment.keys():
        if key in track:
            segment[key]+= track[key]
        else:
            segment[key]+= ['-1']

    lines = [ ",".join(list([str(k) for k in key]) + value) for (key,value) in sorted(segment.items()) ] 
    lines = [new_header +"\n"] + ([ line.replace("\n","") + "\n" for line in lines ])

    output_name = files[0] + ".merged2"
    if TMP_SUFFIX not in output_name:
        output_name += TMP_SUFFIX
        
    output_file = open(os.path.join(folder,output_name),"w")
    output_file.writelines(lines)
    output_file.close()
    return output_name
    
def merge_files_into_one(times, folder, files):
    """Merge many files into one, add tmp suffix if not already there."""
    def add_file(write_file,new_file_path,time):
        new_file = open(new_file_path,"r")
        data = new_file.readlines()[1:]
        new_file.close()
        
        with_frame_number = [",".join([str(time)] + [line.strip() + "\n"]) for line in data]
        write_file.writelines(with_frame_number)
     
    number_files = sorted([(get_trailing_number(os.path.splitext(x)[0]),x) for x in files])
        
    output_name = files[0] + ".merged"
    if TMP_SUFFIX not in output_name:
        output_name += TMP_SUFFIX
    
    # Read header
    first_file = open(os.path.join(folder,files[0]),"r")
    header = first_file.readlines()[0]
    first_file.close()
    
    write_file = open(os.path.join(folder,output_name),"w")
    write_file.writelines("Frame_number, " + header) 
    for num,file in number_files:
        if num in times:
            add_file(write_file,os.path.join(folder,file),times.index(num)+1)

    write_file.close()
    return output_name

def parse_data(args, parent_folder):
    if(args[0] == '/S'):
        # Single file!
        folder = os.path.join(parent_folder,args[1])
        seg_track_name = args[2]
        return (args[3:],(folder,seg_track_name))
    else:
        # Separate!
        folder = os.path.join(parent_folder,args[0]) 
        seg_name = args[1]
        track_name = args[2]
        return (args[3:],(folder,seg_name,track_name))
        

if __name__ == '__main__':
    debug_center.configure(CONFIG_FILE)
    testset_folder = sys.argv[1]
    arg_list = sys.argv[2:]

    # Read GT information
    gt = []
    gt_parser = DEFAULT_PARSER
    
    if(arg_list[0] == '/Parser'):
        gt_parser = arg_list[1]
        arg_list = arg_list[2:]
    
    (arg_list, gt) = parse_data(arg_list,testset_folder)
    many_files_gt = len(find_all_files(gt[0],gt[1])) > 1

    # Read Algorithm information
    algo = []
    algo_parser = DEFAULT_PARSER
    algo_name = arg_list[0]
    arg_list = arg_list[1:]

    if(arg_list[0] == '/Parser'):
        algo_parser = arg_list[1]
        arg_list = arg_list[2:]

    (arg_list, algo) = parse_data(arg_list,testset_folder)
    many_files_algo = len(find_all_files(algo[0],algo[1])) > 1
    
    output_to_stdout = []
    if(arg_list != [] and arg_list[0] == '/OutputStd'):
        output_to_stdout = ['/OutputStd']
        arg_list = arg_list[1:]
    
    automatic_details_drawing_params = []
    if(arg_list != [] and arg_list[0] == '/Input'):
        automatic_details_drawing_params = ['/Input',os.path.join(testset_folder,arg_list[1]),arg_list[2]]
        arg_list = arg_list[3:]
    
    # Validate multifile
    if(many_files_gt ^ many_files_algo):
        debug_center.show_in_console(None,"Warning", "WARNING: Either both algorith results and ground truth should use many files or none of them. Make sure that frames are correctly matched (GT-Results).")
        #sys.exit(1) we can live without it

    gt_files = []
    algo_files = []
    evaluate_tracking = not (len(algo) > 2 and algo[2] == "NONE" or len(gt) > 2 and gt[2] == "NONE")
    if evaluate_tracking == False:
        algo = algo[0:2]
        gt = gt[0:2]
    
    # If we have many files then find snapshot times and merge files
    if(many_files_gt or many_files_algo):
        debug_center.show_in_console(None,"Tech", "Many files option detected. Merging files...")
        
        # Calculate snapshot times
        times = []
        if many_files_gt:
            debug_center.show_in_console(None,"Tech", "Ground truth uses many files option. Merging files...")
            times += determine_all_snaptimes(find_all_files(gt[0],gt[1]))
            if len(gt) > 2 and gt[2] :
                times += determine_all_snaptimes(find_all_files(gt[0],gt[2]))
            
        if many_files_algo:
            debug_center.show_in_console(None,"Tech", "Algorithm results uses many files option. Merging files...")
            times += determine_all_snaptimes(find_all_files(algo[0],algo[1]))
            if len(algo) > 2:
                times += determine_all_snaptimes(find_all_files(algo[0],algo[2]))
            
        all_times = list(set(times))
        # Merge files for every group
        
        if many_files_gt:
            gt_files = [merge_files_into_one(all_times,gt[0],find_all_files(gt[0],gt[1]))]
            if len(gt) > 2:
                gt_files += [merge_files_into_one(all_times,gt[0],find_all_files(gt[0],gt[2]))]
        
        if many_files_algo:
            algo_files = [merge_files_into_one(all_times,algo[0],find_all_files(algo[0],algo[1]))]
            if len(algo) > 2:
                algo_files += [merge_files_into_one(all_times,algo[0],find_all_files(algo[0],algo[2]))]
        debug_center.show_in_console(None,"Tech", "...done merging files")

    if(many_files_gt == 0):
        # add original files
        debug_center.show_in_console(None,"Info", "Ground truth uses single files option...")
        gt_files = find_all_files(gt[0],gt[1])
        if len(gt) > 2:
            gt_files += find_all_files(gt[0],gt[2])
            
    if(many_files_algo == 0):
        # add original files
        debug_center.show_in_console(None,"Info", "Algorithm results uses single files option...")
        algo_files = find_all_files(algo[0],algo[1])
        if len(algo) > 2:
            algo_files += find_all_files(algo[0],algo[2])

    # Merge two files into one
    if(len(gt_files) > 1):
        debug_center.show_in_console(None,"Tech", "Two files for GT. Merging...")
        gt_input = merge_seg_track_files(gt[0],gt_files)
        debug_center.show_in_console(None,"Tech", "...done merging")
    else:
        # kopiuj plik do tempa
        gt_input = gt_files[0]

    if(len(algo_files) > 1):
        debug_center.show_in_console(None,"Tech", "Two results files. Merging...")
        algo_input = merge_seg_track_files(algo[0],algo_files)
        debug_center.show_in_console(None,"Tech", "...done merging")
    elif len(algo_files) == 1:
        # kopiuj plik do tempa
        algo_input = algo_files[0]
    else:
        raise Exception("No algorithm results found.")
        
    # Run evaluation 
    evaluate_tracking_param = ''
    if evaluate_tracking == 0:
        evaluate_tracking_param = "/SegOnly"
    
    gt_path = os.path.join(gt[0],gt_input)
    algo_path = os.path.join(algo[0],algo_input)

    parameters = output_to_stdout + automatic_details_drawing_params + [gt_path, evaluate_tracking_param, gt_parser, algo_path, algo_parser, algo_name] 
    
    evaluate.run_script(["plot_comparison.py"] + [param for param in parameters if param != ''])
    #os.system("python plot_comparison.py " + " ".join(["\""+param+"\"" for param in parameters if param != '']))
    
    debug_center.show_in_console(None,"Progress", "Moving files to output...")
    
    # get results files from gt and algo
    gt_files = [p for p in find_all_created_files_paths(gt[0]) if os.path.isfile(p)]
    algo_files = [p for p in find_all_created_files_paths(algo[0]) if os.path.isfile(p)]
    created_details = find_all_created_directories(algo[0])
    
    # move files into output folders 
    for gt_file in gt_files:
        new_path = determine_output_filepath(gt_file,OUTPUT_FOLDER) #os.path.basename(gt_file)
        if(os.path.isfile(new_path)):
            os.remove(new_path)
        os.renames(gt_file, new_path)
        
    for algo_file in algo_files:
        new_path = determine_output_filepath(algo_file,OUTPUT_FOLDER) #os.path.basename(algo_file)
        if(os.path.isfile(new_path)):
            os.remove(new_path)
        os.renames(algo_file, new_path)
        
    # move evaluation details drawings
    for directory in created_details:
        new_path = determine_output_filepath(directory,OUTPUT_FOLDER) 
        if(os.path.isdir(new_path)):
            shutil.rmtree(new_path,onerror=remove_readonly)
        os.renames(directory, new_path)

    debug_center.show_in_console(None,"Progress", "...done moving")
    
    delete_tmp = 0
    if read_ini(CONFIG_FILE,'misc','cleartmp') != '':
        delete_tmp = float(read_ini(CONFIG_FILE,'misc','cleartmp'))

    if delete_tmp:
        debug_center.show_in_console(None,"Progress", "Deleting intermediate files as requested...")
        tmp_paths_to_remove = [determine_output_filepath(file,OUTPUT_FOLDER)for file in gt_files + algo_files if any([suf for suf in MERGED_SUFFIXES if file.endswith(suf)])]
        for t in tmp_paths_to_remove:
            os.remove(t)
            if len(os.listdir(os.path.dirname(t))) == 0:
                os.rmdir(os.path.dirname(t))
        debug_center.show_in_console(None,"Progress", "...done deleting")
    