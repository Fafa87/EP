#===== INPUT FROM EP =====#
#output_file = <filename_without_extension>
#output_file_extension = ".svg"|".png"
#set terminal (svg | pngcairo) size 1200,800 linewidth 2 font ",22" # (depends on evaluation.ini)
#data_file = <path_to_tmp_file_with_data>

if (!exists("plot_title")) plot_title=""
if (!exists("xlabel_lines")) xlabel_lines=1
pad(num, label_col) = ("\n\n\n\n"[:(int(num) % xlabel_lines)]) . stringcolumn(label_col)

#===== GRID SETTINGS =====#
grid_xtics=1; 
grid_mxtics=1;

grid_xlabel="Frame"
grid_ylabel=""

#===== FINAL SETTINGS =====#
# Output
#set terminal (svg | pngcairo | other) [options] # if you want to override evaluation.ini settings
set output output_file.output_file_extension

# Plot style
set style data lines
set key bottom center outside box Right horizontal 
unset grid
set grid mxtics mytics xtics ytics

# Ranges and labels
set yrange [0.5:1]
set mytics 5
set ylabel grid_ylabel

set xtics grid_xtics font ",12" offset character 0,0.25 
set mxtics grid_mxtics
set xlabel grid_xlabel

set title plot_title font ",40"

#===== PLOT DATA =====#
plot data_file index 1 using 2:xtic(pad($0,1)) title "Precision" with lines lw 2 \
	 ,data_file index 2 using 2:xtic(pad($0,1)) title "Recall" with lines lw 2 \
	 ,data_file index 3 using 2:xtic(pad($0,1)) title "F" with lines lw 2

