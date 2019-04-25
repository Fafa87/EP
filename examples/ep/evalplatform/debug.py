import sys
import os

class DebugCenter(object):
    version = 1
    
    # Set those before running program.
    chosen_level = 1
    chosen_categories = set()
    
    debug_on = True
    log_to_file = False
    
    # Set those for every usage. Possibly override this in derived class for a given program.
    category_levels = {}
    possible_categories = set()
    log_file = "log.txt"
    
    def __init__(self,level = None,categories = None):
        if not level is None:
            self.chosen_level = level
        if not categories is None:
            self.chosen_categories = categories

    def check_if_enabled(self, level, categories):
        if type(categories) is str:
            category = categories
            categories = set([category])
            if level is None and category in self.category_levels:
                # take level of category
                level = self.category_levels[category]
        if not self.chosen_categories.issubset(self.possible_categories):
            raise Exception("Chosen debug category is not registered in DebugCenter!")
        if not categories.issubset(self.possible_categories):
            raise Exception("One of the used categories is not registered in DebugCenter!")
        return self.debug_on and (level <= self.chosen_level or any([cat in self.chosen_categories for cat in categories]))
    
    def show_in_console(self, level, categories, text):
        if(self.check_if_enabled(level, categories)):
            print text
            return True
        return False
    
    def log_in_file(self, level, text):
        if(self.log_to_file and self.check_if_enabled(level, set())):
            with open(self.log_file,'a') as f:
                f.write(text + '\n')
            return True
        return False

# ================== #
#       Tests 
# ================== #
        
import unittest

class TestDebugCenter(unittest.TestCase):
    debug_center = DebugCenter()
    def test_check(self):
        self.debug_center.chosen_categories = set(["seg"])
        # get by category
        self.assertTrue(self.debug_center.check_if_enabled(10,set(["seg"])))
        # get by level
        self.assertTrue(self.debug_center.check_if_enabled(0,set()))
        # dont get
        self.assertFalse(self.debug_center.check_if_enabled(10,set()))
        # get by level dont get by debug_print
        self.debug_center.debug_on = False
        self.assertFalse(self.debug_center.check_if_enabled(0,set()))
        self.debug_center.debug_on = True
        # get by category_level
        self.assertTrue(self.debug_center.check_if_enabled(None,"merge"))
        # dont get by category_level
        self.assertFalse(self.debug_center.check_if_enabled(None,"track"))
        
    def test_log(self):
        self.debug_center.log_to_file = True
        # get by level 
        self.assertTrue(self.debug_center.log_in_file(0,"Universe to be destroyed..."))
        self.assertTrue(self.debug_center.log_in_file(0,"Universe has been destroyed..."))
        # check if file created and correct
        with open(self.debug_center.log_file,'r') as f:
                lines = f.readlines()
                self.assertEqual(len(lines),2 )
                self.assertEqual(lines[0].strip(),"Universe to be destroyed...")
                self.assertEqual(lines[1].strip(),"Universe has been destroyed...")
        # dont get by log_to_file
        self.debug_center.log_to_file = False
        self.debug_center.log_in_file(0,"Just kiddding?")
        with open(self.debug_center.log_file,'r') as f:
                lines = f.readlines()
                self.assertEqual(len(lines),2)
        
    def test_wrong_category(self):
        # Incorrect chosen_categories
        self.debug_center.chosen_categories = set(["seg","merged"])
        with self.assertRaises(Exception):
            self.debug_center.check_if_enabled(10,set(["seg"]))
        
        # Correct chosen_categories
        self.debug_center.chosen_categories = set(["seg","merge"])
        self.debug_center.check_if_enabled(10,set(["seg"]))
        
        # Incorrect categories to check
        with self.assertRaises(Exception):
            self.debug_center.check_if_enabled(10,set(["sego"]))
    
    def setUp(self):
        if(os.path.isfile(self.debug_center.log_file)):
            os.remove(self.debug_center.log_file)
        self.debug_center = DebugCenter()
        self.debug_center.chosen_level = 1 
        self.debug_center.category_levels = {"merge" : 1, "track" : 10}
        self.debug_center.possible_categories = set(["seg","track","merge"])
        
    def tearDown(self):
        if(os.path.isfile(self.debug_center.log_file)):
            os.remove(self.debug_center.log_file)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules["__main__"])
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.system("pause")