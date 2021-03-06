import unittest

from ep.evalplatform.utils import *


class TestSlices(unittest.TestCase):
    def test_slice_intersect_inclusion(self):
        s1 = (slice(0, 10), slice(15, 17))
        s2 = (slice(0, 10), slice(15, 17))
        self.assertEqual(s1, slices_intersection(s1, s2))

        s2 = (slice(0, 15), slice(15, 33))
        self.assertEqual(s1, slices_intersection(s1, s2))

        s2 = (slice(2, 7), slice(15, 16))
        self.assertEqual(s2, slices_intersection(s1, s2))

    def test_slice_partial_overlap(self):
        s1 = (slice(0, 10), slice(15, 17))
        s2 = (slice(5, 13), slice(15, 16))
        self.assertEqual((slice(5, 10), slice(15, 16)), slices_intersection(s1, s2))

    def test_slice_disjoin(self):
        s1 = (slice(0, 10), slice(15, 17))
        s2 = (slice(0, 0), slice(15, 15))
        self.assertEqual(s2, slices_intersection(s1, s2))

        s2 = (slice(13, 14), slice(0, 18))
        self.assertEqual(None, slices_intersection(s1, s2))

        s2 = (slice(0, 24), slice(0, 3))
        self.assertEqual(None, slices_intersection(s1, s2))

    def test_slice_arithmetic(self):
        s1 = (slice(0, 10), slice(15, 17))
        s2 = (slice(2, 4), slice(15, 19))
        self.assertEqual((slice(2, 14), slice(30, 36)), slices_arithmetic(s1, s2, 1, 1))

    def test_slice_relative(self):
        s1 = (slice(0, 10), slice(15, 17))
        s2 = (slice(2, 4), slice(15, 19))
        self.assertEqual((slice(2, 4), slice(0, 4)), slices_relative(s1, s2))

        # handle zeros
        self.assertEqual((slice(0, 8), slice(0, 2)), slices_relative(s2, s1))


class TestPathManipulation(unittest.TestCase):
    def test_split_path(self):
        if os.name == 'nt':
            components = split_path(r"C:\program files\test")
            self.assertEqual(components, ["C:\\", "program files", "test"])

            components = split_path(r"program files\test\\")
            self.assertEqual(components, ["program files", "test", ""])

        else:
            components = split_path(r"home/program files/test")
            self.assertEqual(components, ["home", "program files", "test"])

            components = split_path(r"program files/test/")
            self.assertEqual(components, ["program files", "test", ""])

    def test_determine_output_path(self):
        if os.name == 'nt':
            file_path = r"TestSet1\Results\Mine\res.png"
            output_path = "Output"
            result = determine_output_filepath(file_path, output_path)
            self.assertEqual(result, os.path.join(output_path, file_path))

            file_path = r"c:\TestSet1\Results\Mine\res.png"
            output_path = "Output"
            result = determine_output_filepath(file_path, output_path)
            self.assertEqual(result, r"c:\TestSet1\Results\Mine\Output\res.png")

            file_path = r"c:\TestSet1\Results\Mine\res.png"
            output_path = r"d:\Output"
            result = determine_output_filepath(file_path, output_path)
            self.assertEqual(result, r"d:\Output\Mine\res.png")
        else:
            file_path = "TestSet1/Results/Mine/res.png"
            output_path = "Output"
            result = determine_output_filepath(file_path, output_path)
            self.assertEqual(result, os.path.join(output_path, file_path))

            file_path = "/home/TestSet1/Results/Mine/res.png"
            output_path = "Output"
            result = determine_output_filepath(file_path, output_path)
            self.assertEqual(result, "/home/TestSet1/Results/Mine/Output/res.png")

            file_path = "/home/TestSet1/Results/Mine/res.png"
            output_path = "/home/Output"
            result = determine_output_filepath(file_path, output_path)
            self.assertEqual(result, "/home/Output/Mine/res.png")


class TestINI(unittest.TestCase):
    def test_readini(self):
        read_data = read_ini('test.tmp', 'a', 'b')
        self.assertEqual(read_data, 'testvalue')

    def setUp(self):
        config = ConfigParser.ConfigParser()
        config.add_section('a')
        config.set('a', 'b', 'testvalue')
        file = open('test.tmp', 'w')
        config.write(file)
        file.close()

    def tearDown(self):
        os.remove('test.tmp')


class TestReadWritePlot(unittest.TestCase):
    def readfile(self, path):
        opened_file = open(path, "rU")
        lines = opened_file.readlines()
        opened_file.close()
        return lines

    def setUp(self):
        self.filename = "testowy"
        self.data_saved = '"1" 2\n"3" 5\n"10" 12\n\n\n"1" 20\n"3" 50\n"10" 120\n\n\n"1" 200\n"3" 500\n"10" 1200'
        self.data_read = [[("1", 2), ("3", 5), ("10", 12)], [("1", 20), ("3", 50), ("10", 120)],
                          [("1", 200), ("3", 500), ("10", 1200)]]
        opened_file = open(self.filename, "w")
        opened_file.writelines(self.data_saved)
        opened_file.close()

    def tearDown(self):
        os.remove(self.filename)

    def test_write(self):
        write_to_file(self.data_read, self.filename)
        read_data = "".join(self.readfile(self.filename))
        self.assertEqual(read_data, self.data_saved)

    def test_read(self):
        data = read_from_file(self.filename)
        self.assertEqual(data, self.data_read)

