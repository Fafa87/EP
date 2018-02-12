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
            print (text)
            return True
        return False
    
    def log_in_file(self, level, text):
        if(self.log_to_file and self.check_if_enabled(level, set())):
            with open(self.log_file,'a') as f:
                f.write(text + '\n')
            return True
        return False
