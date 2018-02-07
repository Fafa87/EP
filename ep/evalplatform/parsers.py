import itertools
import csv

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .yeast_datatypes import*

### ======= CELLPARSER HIERARCHY ======= ###

class CSVCellParser():
    """Base class for standard parsers.
    Mapping must include "frame_nr","cell_nr","position_x","position_y".
    Can include: 
        - "cell_colour" if it is additionally marked
        - "unique_id" if there is a unique id throughout all the sequence
    """
    map_name = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3}
    csv_dialect = None
    
    def validate(self):
        return any([k in self.map_name for k in ["frame_nr","cell_nr","position_x","position_y"]])
    
    def cell_colour(self,line):
        if "cell_colour" in self.map_name:
            self.set_line(line)
            return int(float(self.get_column("cell_colour")))
        return 0
    
    def unique_id(self,line):
        if "unique_id" in self.map_name:
            self.set_line(line)
            return int(float(self.get_column("unique_id")))
        return -1
    
    def is_csv_header(self,headers):
        """Takes raw csv line and checks if it looks like header (every column is not a number)."""
        headers_list = self.csv_split(headers)
        for h in headers_list:
            try:
                parsed = float(h) # check if it is a number
            except Exception as e:
                parsed = None
            if parsed != None:
                return False
        return True #all([h is not number for h in headers])
    
    def csv_line(self, data):
        line = StringIO()
        cw = csv.writer(line)
        cw.writerow(data)
        return line.getvalue().strip()
    
    def csv_split(self, line):
        if self.csv_dialect is not None:
            data_split = list(csv.reader([line],self.csv_dialect))[0]
        else:
            data_split = list(csv.reader([line]))[0]
        return [col.replace(",",".").strip() for col in data_split]
    
    def set_line(self,line):
        self.columns = self.csv_split(line)
    
    def get_column(self,value_name):
        return self.columns[self.map_name[value_name]]
        
    def parse(self,lines):
        """
        [(frame_nr, cell_id, position_x, position_y)]
        """
        self.csv_dialect = None
        if(self.is_csv_header(lines[0])):
            self.configure(lines[0])
            lines = lines[1:]
        return [ self.parse_line(line) for line in lines] 

    def parse_line(self,line):
        self.set_line(line)
        cell = CellOccurence(int(self.get_column("frame_nr")),int(self.get_column("cell_nr")),self.unique_id(line),
            (float(self.get_column("position_x")), float(self.get_column("position_y"))))
        cell.colour = self.cell_colour(line)
        return (int(self.get_column("frame_nr")), cell)
    
    def configure(self,headers):
        if len(headers.strip()) > 0:
            try:
                self.csv_dialect = csv.Sniffer().sniff(headers,[',',';'])
            except csv.Error:
                print ("CSV delimiter could not be established from file headers. Defaults are used.")

class CellProfilerParser(CSVCellParser):
    symbol = "CP"
    
    map_regular_name = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3}
    map_colour_name = {"frame_nr" : 0, "cell_nr" : 1, "cell_colour" : 2, "position_x" : 3, "position_y" : 4}
    
    def configure(self,headers):
        if("Features_Colour" in headers or "Cell_colour" in headers):
            self.map_name = self.map_colour_name
        else:
            self.map_name = self.map_regular_name
        CSVCellParser.configure(self,headers)
        

class OldGroundTruthParser(CSVCellParser):
    symbol = "OLDGT"
    
    map_regular_name = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3, "unique_id" : 1}
    map_colour_name = {"frame_nr" : 0, "cell_nr" : 1, "cell_colour" : 2, "position_x" : 3, "position_y" : 4, "unique_id" : 1}
    
    def configure(self,headers):
        if("Features_Colour" in headers or "Cell_colour" in headers):
            self.map_name = self.map_colour_name
        else:
            self.map_name = self.map_regular_name
        CSVCellParser.configure(self,headers)
        
class CellIDParser(CSVCellParser):
    symbol = "CID"
    
    map_name = {"frame_nr" : 1, "cell_nr" : 0, "position_x" : 3, "position_y" : 4, "unique_id" : 0}
    def set_line(self,line):
        self.columns = line[:-1].split("\t")  
        self.columns[1] = str(int(self.columns[1])+1) # shift frame_nr so that it is >0

    def configure(self,headers):
        self.csv_dialect = csv.excel()
        self.csv_dialect.delimiter = '\t'

class TrackerParser(CSVCellParser):
    symbol = "TR"
    
    map_name = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3, "unique_id" : 1}
    
class CellProfilerParserTrackingOLDTS2(CSVCellParser):
    symbol = "CPTS2"
    map_name = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3, "unique_id" : 1} 
    
class CellSerpentParser(CSVCellParser):
    symbol = "CS"
    
    map_name = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3}
    filenames = {}
    def get_column(self,value_name):
        if value_name == "frame_nr":
            tekst = self.columns[self.map_name[value_name]]
            if not tekst in self.filenames:
                self.filenames[tekst] = len(self.filenames)+1
            return self.filenames[tekst]
        else:
            return self.columns[self.map_name[value_name]]
          
class DefaultPlatformParser(CSVCellParser):
    """Main parser for Evaluation platform and benchmark data sets.
    
    The CSV file header is important for data selection and must include all:
    [Frame_number, Cell_number, Position_X, Position_Y]
    and optionally some of:
    [Cell_colour, Unique_cell_number]
    
    If any of the headers is not one of the above default column numbers are used with the information printed to stdout.
    
    """
    symbol = "PLATFORM_DEF"

    required_headers_list = ["Frame_number", "Cell_number", "Position_X", "Position_Y"]
    possible_headers = required_headers_list + ["Cell_colour", "Unique_cell_number"]
    # for compatibility (should be removed?)
    header_to_csvcellparser = {"Frame_number" : "frame_nr", "Cell_number" : "cell_nr", 
                               "Position_X" : "position_x", "Position_Y" : "position_y", 
                               "Unique_cell_number" : "unique_id", "Cell_colour" : "cell_colour"}
    
    map_regular_name_segrack = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3, "unique_id" : 4}
    map_regular_name_segonly = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3}
    map_colour_name_segtrack = {"frame_nr" : 0, "cell_nr" : 1, "cell_colour" : 2, "position_x" : 3, "position_y" : 4, "unique_id" : 5} 
    map_colour_name_segonly = {"frame_nr" : 0, "cell_nr" : 1, "cell_colour" : 2, "position_x" : 3, "position_y" : 4} 
    
    def __init__(self):
        # ignore case by setting it to lower
        self.required_headers_list = [l.lower() for l in self.required_headers_list]
        self.possible_headers = [l.lower() for l in self.possible_headers]
        self.header_to_csvcellparser = dict([(a.lower(),b) for a,b in  self.header_to_csvcellparser.items()])
    
    def configure(self,headers):
        CSVCellParser.configure(self,headers)
        # lower case so it can be found in dictionary
        header_list = [h.lower().strip() for h in self.csv_split(headers)]
        if any([h not in self.possible_headers for h in header_list]) or any([h not in header_list for h in self.required_headers_list]):
            # CSV file headers are not consistent with expected ones. Use default option.
            print ("File header does not comply with the expected headers list. The default setting are used instead.")
            print ("Provided headers: ", header_list)
            if "Cell_colour" in headers :
                if "Unique_cell_number" in headers:
                    self.map_name = self.map_colour_name_segtrack
                else:
                    self.map_name = self.map_colour_name_segonly
            else:
                if "Unique_cell_number" in headers or len(header_list) == len(self.map_regular_name_segrack):
                    self.map_name = self.map_regular_name_segrack
                else:
                    self.map_name = self.map_regular_name_segonly
            print ("Used mapping: ", self.map_name)
        else:
            self.map_name = dict([(self.header_to_csvcellparser[h.strip()],i) for i,h in enumerate(header_list)])
        
    
    
    def parse(self,lines):
        """
        [(frame_nr, cell_id, position_x, position_y)]
        """
        self.csv_dialect = None
        if(self.is_csv_header(lines[0])):
            self.configure(lines[0])
            lines = lines[1:]
        return [ self.parse_line(line) for line in lines] 

    def parse_line(self,line):
        self.set_line(line)
        cell = CellOccurence(int(self.get_column("frame_nr")),int(self.get_column("cell_nr")),self.unique_id(line),
            (float(self.get_column("position_x")), float(self.get_column("position_y"))))
        cell.colour = self.cell_colour(line)
        return (int(self.get_column("frame_nr")), cell)
    
    def output(self, cells, output_colors = False):
        """
        Output the given cells as a CSV file in EP format.
        The inclusion of Unique_cell_number and Cell_colour columns depending on the cells itself and output_colours parameter.
        Returns:
            csv formated string
        """
        
        has_tracking_data = len(cells) > 0 and cells[0][1].has_tracking_data()
        
        ordered_headers = ["Frame_number", "Cell_number"]
        if(output_colors): 
            ordered_headers += ["Cell_colour"]
        ordered_headers += ["Position_X", "Position_Y"]
        if(has_tracking_data):
            ordered_headers += ["Unique_cell_number"]
            
        csv = [CSVCellParser.csv_line(self, ordered_headers)]
        for (f,cell) in cells:
            csv += [self.output_cell(cell,output_colors)]
        return "\n".join(csv)
        
    def output_cell(self, cell, output_colors = False):   
        '@type cell: CellOccurence'
        data = [cell.frame_number, cell.cell_id]
        if(output_colors): 
            data += [cell.colour]
        data += [cell.position[0], cell.position[1]]
        if(cell.has_tracking_data()):
            data += [cell.unique_id]
        return CSVCellParser.csv_line(self, data)
        
        
### ======= Tracking link HIERARCHY ======= ###

class TrackingLinkParser(CSVCellParser):
    """Base class for parsers of segmentation and tracking data without unique_id.
    Uses CSVCellParser by providing it with previously preprocessed data (with calculated unique_id).
    
    Original mapping is used for preprocessing and must include "frame_nr","cell_nr","position_x","position_y","last_frame_nr".
    if "last_frame_nr" = 0 then this is a new frame.
    """
    
    map_name = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3, "unique_id" : 1}
    original_map = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3, "last_frame_nr" : 4}
        
    def get_original_column(self,value_name):
        return self.original_columns[self.original_map[value_name]]
        
    def set_original_line(self,line):
        self.original_columns = [col.replace(",",".").strip() for col in list(csv.reader([line]))[0]]
        
    def parse_original_line(self,line):
        self.set_original_line(line)
        (f,cid,x,y,lastid) = (self.get_original_column("frame_nr"),self.get_original_column("cell_nr"),
                              self.get_original_column("position_x"),self.get_original_column("position_y"),
                              self.get_original_column("last_frame_nr"))
        return (int(f),int(cid),float(x),float(y),int(lastid))
    
    def parse(self,lines):
        """
        Args::
            lines - [string] including all the data from a file to parse
        Returns:: 
            [Cell]
        """
        self.csv_dialect = None
        if self.is_csv_header(lines[0]):
            self.configure(lines[0])
            lines = lines[1:]
        preprocessed_lines = [CSVCellParser.csv_line(self,data) for data in self.preprocess(lines)]
        return CSVCellParser.parse(self, [CSVCellParser.csv_line(self,self.map_name.keys())] + preprocessed_lines) 
    
    def preprocess(self,lines):
        """
        Returns::
            [(frame_nr, unique_id, position_x, position_y)]
        """
        count = 1
        splits = 0
        frames_grouped = itertools.groupby([ self.parse_original_line(line) for line in lines],lambda x: x[0])
        results = []
        last_cells = dict()
        # current cell id -> general cell id
        new_cells = dict()
        for (frame, cells) in frames_grouped:
            last_cells = new_cells
            new_cells = dict()
            for (f,cid,x,y,lastid) in cells:
                if lastid == 0:
                    new_cells[cid] = count
                    results.append((f,new_cells[cid],x,y))
                    count = count + 1
                else:
                    if lastid in last_cells: # propagate cell id
                        if last_cells[lastid] in new_cells.values():
                            splits = splits + 1
                            new_cells[cid] = count
                            count = count + 1
                        else:
                            new_cells[cid] = last_cells[lastid]
                        results.append((f,new_cells[cid],x,y))
                    else:
                        print("".join(["CELL NOT IN THE PREVIOUS FRAME??"]))
                        print("{} {} {}".format(frame,lastid,last_cells))
        if splits > 0:
            print("Number of splits (unhandled yet): {}".format(splits))
        return results
         
class CellTracerParser(TrackingLinkParser):
    symbol = "CT"
    pass

class CellStarParser(TrackingLinkParser):
    symbol = "CSTAR"
    pass

class CellProfilerParserTracking(TrackingLinkParser):
    symbol = "CPT"
    original_map = {"frame_nr" : 0, "cell_nr" : 1, "position_x" : 2, "position_y" : 3, "last_frame_nr" : 12}
    
