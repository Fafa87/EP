import sys
import os
import stat
import shutil

import csv
import ConfigParser

import debug

CONFIG_FILENAME = "evaluation.ini"

# Name suffixes
SUMMARY_SUFFIX = ".eval.summary.txt"
SEGPLOTDATA_SUFFIX = ".eval.segplot.txt"
SEGPLOT_SUFFIX = ".eval.segplot.png"
SEGPLOT_SUFFIX2 = ".eval.segplot.svg"
SEGDETAILS_SUFFIX = ".eval.segdetails.txt"
TRACKPLOTDATA_SUFFIX = ".eval.trackplot.txt"
TRACKPLOT_SUFFIX = ".eval.trackplot.png"
TRACKPLOT_SUFFIX2 = ".eval.trackplot.svg"
TRACKDETAILS_SUFFIX = ".eval.trackdetails.txt"
LONGTRACKDETAILS_SUFFIX = ".eval.longtrackdetails.txt"

ALL_SUFFIXES = [SUMMARY_SUFFIX,SEGPLOTDATA_SUFFIX,SEGPLOT_SUFFIX,SEGPLOT_SUFFIX2,SEGDETAILS_SUFFIX,TRACKPLOTDATA_SUFFIX,TRACKPLOT_SUFFIX,TRACKPLOT_SUFFIX2,TRACKDETAILS_SUFFIX,LONGTRACKDETAILS_SUFFIX]

SEG_DRAWING_FOLDER = "Segmentation details"
TRACK_DRAWING_FOLDER = "Tracking details"
LONG_DRAWING_FOLDER = "Long tracking details" 
ALL_DIRECTORIES = [SEG_DRAWING_FOLDER,TRACK_DRAWING_FOLDER,LONG_DRAWING_FOLDER]
    
def reduce_plus(ls):
    return reduce(lambda a,b: a+b,ls)
    
def get_config_file_path():
    """
    In case that cwd is not in the same directory that config file. Check if file is where the executed script is.
    """
    if not os.path.isfile(CONFIG_FILENAME):
        return os.path.join(os.path.dirname(sys.argv[0]),CONFIG_FILENAME)
    return CONFIG_FILENAME

CONFIG_FILE = get_config_file_path()
    
def split_path(path):
    if os.path.split(path)[0] != path and os.path.split(path)[0] != '':
        (dir, file) = os.path.split(path)
        return split_path(dir) + [file]
    return [path]

def ensure_directory_in(filepath, directory_name):
    """Check is in the directory of the given filepath exists directory of the given name, if not it is created.
    
    Returns::
        ensured_directory_path - <path>\directory_name
    """
    
    ensured_directory_path = os.path.join(os.path.split(filepath)[0],directory_name) 
    if not os.path.exists(ensured_directory_path):
        os.makedirs(ensured_directory_path)
    return ensured_directory_path

def determine_output_filepath(filepath,output_path):
    if os.path.isabs(filepath) == True:
        if os.path.isabs(output_path) == True:
            # just put it in the given folder
            components = split_path(filepath)
            return os.path.join(output_path,os.path.join(*components[-2:]))
        else:
            # let output be one level up 
            components = split_path(filepath)
            return os.path.join(os.path.join(*components[:-1]),output_path,os.path.join(*components[-1:]))
    return os.path.join(output_path,filepath)
     
def distance(p0, p1):
    return ((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)**0.5
    
def package_path(filename, quoted = 1):
    """
    Return relative (from cwd) path to file in package folder.
    In quotes.
    """
    name = os.path.join(os.path.dirname(__file__),filename)
    if quoted:
        return "\"" + name + "\""
    return name

def read_from_csv(path):
    """
    Args::
        path - full path of the existing csv file
    Returns::
        (headers,[record])
    """
    opened_file = open(path,"rb")
    lines = list(csv.reader(opened_file))
    opened_file.close()
    return (lines[0],lines[1:])

def write_to_csv(headers,records, path):
    """
    Args::
        headers - list of header names
        records - list of records where every record is a list
        path - full path of the created csv file
    """
    opened_file = open(path,"wb")
    cw = csv.writer(opened_file)
    cw.writerows([headers]+sorted(records))
    opened_file.close()

def write_to_file(data_sets, path):
    """
    data_set: [(f,val)] -> 1 2\n2 5\n3 8
    data_sets: [data_set] -> data1\n\n\ndata2
    """
    data = map(lambda dataset : "\n".join([ str(int(f)) + " " + str(val) for (f,val) in dataset]),data_sets)
    joined = "\n\n\n".join(data)
    opened_file = open(path,"w")
    opened_file.writelines(joined)
    opened_file.close()
    
def read_from_file(path):
    """
    Reads plot file
    Returns data sets
    data_set: [(f,val)] -> 1 2\n2 5\n3 8
    data_sets: [data_set] -> data1\n\n\ndata2
    """
    opened_file = open(path,"rU")
    joined = opened_file.read()
    opened_file.close()
    
    return [ [ (float(line.split(" ")[0]), float(line.split(" ")[1])) for line in dataset.split("\n")]  for dataset in joined.split("\n\n\n")]

def read_ini(file_path, section, key):
    """
    Reads value from ini file.
    """
    config = ConfigParser.ConfigParser()
    config.read(file_path)
    if config.has_option(section,key):  
        return config.get(section,key)
    return ''
    
def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

class EvaluationDebug(debug.DebugCenter):
    category_levels = {"Result" : 0.1, "Error" : 1, "Warning" : 2, "Info" : 3, "Progress" : 3.1, "Tech" : 3.2, "Trace" : 4.1}
    possible_categories = set(category_levels.keys())
    
    chosen_level = 3
    chosen_categories = set()
    debug_on = True
    log_to_file = False
    
    def configure(self,ini_file):
        if read_ini(ini_file,'debug','verbosity') != '':
            self.chosen_level = float(read_ini(ini_file,'debug','verbosity'))

        if read_ini(ini_file,'debug','show') != '':
            self.debug_on = bool(read_ini(ini_file,'debug','show')) 

        if read_ini(ini_file,'debug','logtofile') != '':
            self.log_to_file = bool(read_ini(ini_file,'debug','logtofile')) 
        

debug_center = EvaluationDebug()
    
# ================== #
#       Tests 
# ================== #
    
import random
import unittest
import os

class TestPathManipulation(unittest.TestCase):
    def test_split_path(self):
        components = split_path(r"C:\program files\test")
        self.assertEqual(components, ["C:\\","program files","test"])
        
        components = split_path(r"program files\test\\")
        self.assertEqual(components, ["program files","test",""])
        
    def test_determine_output_path(self):
        file_path = r"TestSet1\Results\Mine\res.png"
        output_path = "Output"
        result = determine_output_filepath(file_path, output_path)
        self.assertEqual(result, os.path.join(output_path,file_path))
        
        file_path = r"c:\TestSet1\Results\Mine\res.png"
        output_path = "Output"
        result = determine_output_filepath(file_path, output_path)
        self.assertEqual(result, r"c:\TestSet1\Results\Mine\Output\res.png")
        
        file_path = r"c:\TestSet1\Results\Mine\res.png"
        output_path = "d:\Output"
        result = determine_output_filepath(file_path, output_path)
        self.assertEqual(result, r"d:\Output\Mine\res.png")
        
    
class TestINI(unittest.TestCase):
    def test_readini(self):
        read_data = read_ini('test.tmp','a','b')
        self.assertEqual(read_data,'testvalue') 
    
    def setUp(self):
        config = ConfigParser.ConfigParser()
        config.add_section('a')
        config.set('a','b','testvalue')
        file = open('test.tmp','w')
        config.write(file)
        file.close()
        
    def tearDown(self):
        os.remove('test.tmp')

class TestReadWritePlot(unittest.TestCase):
    def readfile(self,path):
        opened_file = open(path,"rU")
        lines = opened_file.readlines()
        opened_file.close()
        return lines
    
    def setUp(self):
        self.filename = "testowy"
        self.data_saved = "1 2\n3 5\n10 12\n\n\n1 20\n3 50\n10 120\n\n\n1 200\n3 500\n10 1200"
        self.data_read = [[(1,2),(3,5),(10,12)],[(1,20),(3,50),(10,120)],[(1,200),(3,500),(10,1200)]]
        opened_file = open(self.filename,"w")
        opened_file.writelines(self.data_saved)
        opened_file.close()
        
    def tearDown(self):
        os.remove(self.filename)

    def test_write(self):
        write_to_file(self.data_read,self.filename)
        read_data = "".join(self.readfile(self.filename))
        self.assertEqual(read_data,self.data_saved)

    def test_read(self):
        data = read_from_file(self.filename)
        self.assertEqual(data,self.data_read)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules["__main__"])
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestReadWritePlot)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main()
    os.system("pause")
    
