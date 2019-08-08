EVALUATION TOOL FOR CELL SEGMENTATION AND TRACKING
version 1.2.0

1a. Requirements
- Python version 2.7, 3.7
- PIL (python library)
- imageio (python library)
- Gnuplot (should be available from command line)
- Tested only on Windows XP and Mac OS X 10.7.5 and Ubuntu

1b. Requirements instal on Ubuntu (on clean machine)
sudo apt-get install python-pip
sudo pip install matplotlib
sudo apt-get install python-tk
sudo apt-get install gnuplot
sudo pip install Pillow
sudo pip install imageio

1c. Additional naming requirements
- no results data file can contain ".eval." or ".tmp" in its name
- per-frame results files should end with frame number
- only one results evaluation per folder

2. Instalation
	put files in your main comparison folder (see usage examples):
	Comparison
	    ---> ep
            ---> evalplatform
            ---> compare.py
            ---> evaluate.py
        ---> TestSet1
             ---> GroundTruth
             ---> RawData (optionally to show evaluation details)
             ---> Algo1
             ---> Algo2
	
3. Configuration 
	There is evaluation.ini file which contains:
	- maximal distance (in pixels) between cell in algorithm results and cell in ground truth so it can be considered a match. This parameter depends on the resolution of your images and average cell sizes. We recomend to use a value corresponding to the max  cell size in pixels present in your images.
    - minimal iou similarity is a threshold on how similar have to be contours (when using LABEL or MASK image parser) for two object to be considered a match
	- outputevaluationdetails decides whether to produce detailed results (every correct, false positive, false negative is registered).
	- drawevaluationdetails decides whether to draw the above details upon the provided input images.
	- cleartmp a switch deciding whether to remove all temporary files after evaluation.
	- debug verbosity which limits the amount of information printed to console.
		Values are: 1 (Errors), 2 (+Warnings), 3 (+Informations), 3.1 (+Evaluation progress), 3.2 (+platform technicalities)
	- terminal is the output plots format, supported values are "svg" and "png"
	- fill_markers if 1 then the cell centers are filled in segmentation details
    - markersize the size of the cell centers in segmentation details

4. Usage ep.evaluate with cell centers formats 
	This program can assess the algorithm results based on provided ground truth.
	Input:
		Input images (optional) - folder with imagery that both ground truth and algorithm results correspond to.
		
		GroundTruth - folder with ground truth files (one file one per frame): 
			Segmentation ground truth files (e.g. gt_seg_001.txt,gt_seg_002.txt) - files containing given substring
				Format in comma or semicolon separated CSV type:
					Header line: 
						Cell_number, Cell_colour, Position_X, Position_Y
					Line for every cell:
						<cell_number>, <cell_colour>, <center_position_x>, <center_position_y>
						
					<cell_colour> is the special label on each cell. Currently used are:
						== 0 a regular cell
						!= 0 an unidentified object (when it is found / not found a program is neither rewarded nor penalised) 
						
			Tracking ground truth files (e.g. gt_tra_001.txt,gt_tra_002.txt) - files containing given substring 
				Format in comma or semicolon separated CSV type:
					Header line: 
						Cell_number, Unique_cell_number
					Line for every cell:
						<cell_number>, <unique_cell_number>
		
		Algorithm name - user friendly algorithm name
		
		Algorithm Results - folder with algorithm results file (same as in case of GroundTruth - one file per one frame) 
			Segmentation algorithm results files (e.g. res_seg_001.txt,res_seg_002.txt) - files containing given substring
				Format in comma or semicolon separated CSV type:
					Header line: 
						Cell_number, Position_X, Position_Y
					Line for every cell:
						<cell_number>, <center_position_x>, <center_position_y>
						
			Tracking algorithm results files (e.g. res_tra_001.txt,res_tra_002.txt) - files containing given substring
				Format in comma or semicolon separated CSV type:
					Header line: 
						Cell_number, Unique_cell_number
					Line for every cell:
						<cell_number>, <unique_cell_number>
						
	Output:
		Names prefix = <first_file_name>.<algorithm_name>.eval.
		
		Evalution summary file (suffix = summary.txt)
		Segmentation
			- plot (suffix = segplot.png)
			- plot data (suffix = segplot.png)
			- evaluation details (suffix = segdetails.txt)
		Tracking (if provided)
			- plot (suffix = trackplot.txt)
			- plot data (suffix = trackplot.png)
			- evaluation details (suffix = trackdetails.txt)
		Long-term tracking (if provided)
			- evaluation details (suffix = longtrackdetails.txt)
			
		If input images are provided then additionally the details are drawn upon the input images and placed into folders:
		- Segmentation details
		- Tracking details
		- Long tracking details
			
	Abstract syntax:
		python -m ep.evaluate TestSetDir GroundTruthDir GroundTruthSegmentationPrefix GroundTruthTrackingPrefix AlgoDir AlgoNameInPlots AlgoSegmentaionPrefix AlgoTrackingPrefix [/Input InputImageryDir InputImageryPrefix]
	
	Additional usage options are described in part 7.
	
	Usage examples:
		Simple case:
			python -m ep.evaluate TestSet1 "GroundTruth" "gt_seg" "gt_track" CellProfiler "Algo1" "cp_seg" "cp_track"
		
		If we want to test only segmentation:
			python -m ep.evaluate TestSet1 "GroundTruth" "gt_seg" NONE CellProfiler "Algo1" "cp_seg" NONE
			
		If we want additional details plotting:
			python -m ep.evaluate TestSet1 "GroundTruth" "gt_seg" "gt_track" CellProfiler "Algo1" "cp_seg" "cp_track" /Input "RawData" "bf"

4. Usage ep.evaluate with full contour formats 
	This program can assess the algorithm results based on ground truth provided in form of labels. 
    The advantage is that we can take object contour into account and reject matches where center is correct but contours are significantly different.
	Input:
		Input images (optional) - folder with imagery that both ground truth and algorithm results correspond to.
		
		GroundTruth - folder with ground truth files (one file one per frame): 
			Segmentation ground truth files (e.g. time001.tif, time002.tif) - files containing given substring
                Each cell should be marked with different positive pixel value.
		
		Algorithm name - user friendly algorithm name
		
		Algorithm Results - folder with algorithm results file (same as in case of GroundTruth - one file per one frame) 
			Segmentation algorithm results files (e.g. seg_time001.txt, seg_time002.txt) - files containing given substring
                Each cell should be marked with different positive pixel value.
						
	Output:
        Same as in case of cell center formats with additional information about the IOU between correctly matched cells.
        
	Abstract syntax:
		python -m ep.evaluate TestSetDir /Parser LABEL GroundTruthDir GroundTruthSegmentationPrefix NONE AlgoDir /Parser LABEL AlgoNameInPlots AlgoSegmentaionPrefix NONE [/Input InputImageryDir InputImageryPrefix]
	
	Usage examples:
		Case with additional details plotting:
			python -m ep.evaluate Various_LabelsBased /Parser LABEL "GroundTruth" time NONE Segmenter /Parser LABEL "Segmenter" "time" NONE /Input RawData time
		
		Segmentation given as masks:
			python -m ep.evaluate Various_MasksBased /Parser MASK "GroundTruth" time NONE Segmenter /Parser MASK "Segmenter" "time" NONE /Input RawData time
   
6. Usage ep.compare
	Compares the selected results. Requires results produced by python -m ep.evaluate. Make sure that all the algorithms to compare provide results for the same set of frames.
	Input:
		Test set folder
		List of folder paths to the results (relative to Test set folder)
		
	Output:
		Summary file
		Summary plots of F value for segmentation and tracking
		Tile made of the individual evaluation plots
		Report file in CSV format with tabular summary of F values for all algorithms
		
	Example:
		python -m ep.compare TestSet1 Algo1 Algo2

7. Usage ep.evaluate_frame
    This is an additional code that can be used in order to evaluate a single set of files with a very simple syntax.
    It can be used in a feedback loop or parameter search for some external tool (e.g. QuPath) both by CLI or by importing that and using it directly (see test_evaluate_frame.py for details). You can specify parser to use so that image parsers can be utilised as well.
		
8. Plots customisation
	By default all the plots are generated as PNG files but there is an option to use vector format namely SVG. In order to do so open evaluation.ini file and set parameter "terminal" to "svg". However this option does not support merging plots to tiles.
	
	Gnuplot is used to plot the results so it is possible to modify the look of them by changing gnuplot scripts files: segmentation.plt, tracking.plt.
		
9. Additional options and informations about ep.evaluate
	Apart from the basic use the evaluation platform can work with a couple of different formats.
	
	Two more formats of ground truth/algorithm results. In case of the algorithm results files Cell_colour column is not present:
		+ Two files per data (all frames packed into one file):
			Segmentation file (e.g. gt_seg.txt) 
				Format in CSV type:
					Header line(required but to be ignored): 
						Frame_number, Cell_number, Cell_colour, Position_X, Position_Y
					Line for every cell:
						<frame_number>, <cell_number>, <cell_colour>, <center_position_x>, <center_position_y>
						
			Tracking file (e.g. gt_tra.txt) 
				Format in CSV type:
					Header line(to be ignored): 
						Frame_number, Cell_number, Unique_cell_number
					Line for every cell:
						<frame_number>, <cell_number>, <unique_cell_number>
						
			Usage example:
				python -m ep.evaluate TestSet1 "GroundTruth" "GroundTruthCentersSeg.csv" "GroundTruthCentersTracking.csv" CellProfiler "Algo1" "CellProfilerResultsSeg.csv"  "CellProfilerResultsTracking.csv"
			
		+ One file per data (as above but segmentation and tracking merged in one file):
			Segmentation and tracking file (e.g. gt.txt) 
				Header line(required but to be ignored): 
					Frame_number, Cell_number, Cell_colour, Position_X, Position_Y, Unique_cell_number
				Line for every cell:
					<frame_number>, <cell_number>, <cell_colour>, <center_position_x>, <center_position_y>, <unique_cell_number>
			
			Usage example:
				python -m ep.evaluate TestSet1 /S "GroundTruth" "GroundTruthCenters.csv" CellProfiler /S  "Algo1" "CellProfilerResults.csv"
			
	Remarks (for advanced users):
		plot_comparison.py which is run by evaluate.py uses one merged file both for GT and algorithm results so this script merges selected files. First merges many files and adds frame numbers, then if two files exist (segmentation and tracking) merges them into one.
		
		There exist an additional switch /Parser to specify mnemonic for parser used to parse these resulting data. Parsers are implemented in parsers.py and its mnemonics are defined in plot_comparison.py. 
		
		For example:
			python -m ep.evaluate TestSet1 /S "GroundTruth" "gt" CellProfiler /Parser CP /S "Algo1" "res"
			
			uses specific "CP" parser for CellProfiler data.
			
10. Help.
	If you still have questions or problems with Evaluation platform please do not hesitate and contact us - will be glad to help.
	