import unittest

from ep.evalplatform.utils import *


class TestPathManipulation(unittest.TestCase):
    def test_split_path(self):
        components = split_path(r"C:\program files\test")
        self.assertEqual(components, ["C:\\", "program files", "test"])

        components = split_path(r"program files\test\\")
        self.assertEqual(components, ["program files", "test", ""])

    def test_determine_output_path(self):
        file_path = r"TestSet1\Results\Mine\res.png"
        output_path = "Output"
        result = determine_output_filepath(file_path, output_path)
        self.assertEqual(result, os.path.join(output_path, file_path))

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
        self.data_saved = "1 2\n3 5\n10 12\n\n\n1 20\n3 50\n10 120\n\n\n1 200\n3 500\n10 1200"
        self.data_read = [[(1, 2), (3, 5), (10, 12)], [(1, 20), (3, 50), (10, 120)], [(1, 200), (3, 500), (10, 1200)]]
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


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules["__main__"])
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestReadWritePlot)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # unittest.main()
    os.system("pause")
