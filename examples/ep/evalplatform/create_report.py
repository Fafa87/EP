# Creates easy to use table (csv) from Summary.txt file created by Evaluation Platform.

import sys

measure_type = "F:"

def create_report(summary_file_path,precision,format,output_file):
    global measure_type
    summary_file = open(summary_file_path,"rU")
    data = summary_file.readlines()

    all_algo_results = []
    algo_results = []
    # in case there is no end line
    if len(data[-1].strip()) != 0:
        data.append("\n")

    # split into algorithm list
    for d in data:
        if len(d.strip()) == 0:
            all_algo_results.append(algo_results)
            algo_results = []
        else:
            algo_results.append(d)

    # parse measure and results
    algo_results_parsed = []
    """
    (name, (measure : value))
    """
    for d in all_algo_results:
        algo_name = d[0].split(":")[1].strip()
        measure_f = [dd for dd in d[1:] if measure_type in dd or len(dd.split(":")[1].strip()) == 0]
        measures = [m.split(":")[0].strip() for m in measure_f[::2]]
        values = [float(m.split(":")[1]) for m in measure_f[1::2]]
        measure_value = list(zip(measures,values))
        algo_results_parsed.append((algo_name,measure_value))
    
    # output report
    if format == "csv":
        measures = [a[0] for a in algo_results_parsed[0][1]]
        output = open(output_file,"w")
        output.writelines("Measure;" + ";".join([a[0] for a in algo_results_parsed]) + "\n")
        for m in measures:
            measure_line = m + ";" 
            values = [[mv for (mn,mv) in a[1] if mn == m][0] for a in algo_results_parsed]
            output.writelines(measure_line + ";".join([("{:." + str(precision) + "f}").format(a) for a in values]) + "\n")
        output.close()

def create_sensible_report(summary_file_path,precision,output_file):
    all_algo_results = []
    algo_results = []

    with open(summary_file_path,"r") as summary_file:
        for line in summary_file:
            line = line.strip()
            if not line:
                if algo_results:
                    all_algo_results.append(algo_results)
                    algo_results = []
            else:
                algo_results.append(line)

    if algo_results:
        all_algo_results.append(algo_results)

    algo_dicts = list()
    keys = set()
    for d in all_algo_results:
        algo_dict = dict()
        stack = list()
        for entry in d:
            (name, value) = entry.split(":")
            value = value.strip()
            if not value: # just key
                stack.append(name)
            else:
                if name == "F":
                    name = stack.pop()
                algo_dict[name] = value.strip()
                keys.add(name)
        algo_dicts.append(algo_dict)

    keys.remove("Algorithm")
    keys = ["Algorithm"] + sorted(keys)

    with open(output_file, "w") as output:
        output.write(",".join(keys) + "\n")
        for algo in algo_dicts:
            output.write(",".join([algo[k] for k in keys]) + "\n")

if __name__ == '__main__':
    if len(sys.argv) - 1 < 5:
        print ("Script usage: <summary_file_path> <number_precision> csv <output_file_path> <measure_type>")
        exit(0)
    measure_type = sys.argv[-1]
    create_report(*sys.argv[1:-1])
