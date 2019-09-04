import sys
import unittest
import os

from ep.evalplatform.debug import *


class TestDebugCenter(unittest.TestCase):
    debug_center = DebugCenter()

    def test_check(self):
        self.debug_center.chosen_categories = {"seg"}
        # get by category
        self.assertTrue(self.debug_center.check_if_enabled(10, {"seg"}))
        # get by level
        self.assertTrue(self.debug_center.check_if_enabled(0, set()))
        # dont get
        self.assertFalse(self.debug_center.check_if_enabled(10, set()))
        # get by level dont get by debug_print
        self.debug_center.debug_on = False
        self.assertFalse(self.debug_center.check_if_enabled(0, set()))
        self.debug_center.debug_on = True
        # get by category_level
        self.assertTrue(self.debug_center.check_if_enabled(None, "merge"))
        # dont get by category_level
        self.assertFalse(self.debug_center.check_if_enabled(None, "track"))

    def test_log(self):
        self.debug_center.log_to_file = True
        # get by level
        self.assertTrue(self.debug_center.log_in_file(0, "Universe to be destroyed..."))
        self.assertTrue(self.debug_center.log_in_file(0, "Universe has been destroyed..."))
        # check if file created and correct
        with open(self.debug_center.log_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(lines[0].strip(), "Universe to be destroyed...")
            self.assertEqual(lines[1].strip(), "Universe has been destroyed...")
        # dont get by log_to_file
        self.debug_center.log_to_file = False
        self.debug_center.log_in_file(0, "Just kiddding?")
        with open(self.debug_center.log_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)

    def test_wrong_category(self):
        # Incorrect chosen_categories
        self.debug_center.chosen_categories = {"seg", "merged"}
        with self.assertRaises(Exception):
            self.debug_center.check_if_enabled(10, {"seg"})

        # Correct chosen_categories
        self.debug_center.chosen_categories = {"seg", "merge"}
        self.debug_center.check_if_enabled(10, {"seg"})

        # Incorrect categories to check
        with self.assertRaises(Exception):
            self.debug_center.check_if_enabled(10, {"sego"})

    def setUp(self):
        if os.path.isfile(self.debug_center.log_file):
            os.remove(self.debug_center.log_file)
        self.debug_center = DebugCenter()
        self.debug_center.chosen_level = 1
        self.debug_center.category_levels = {"merge": 1, "track": 10}
        self.debug_center.possible_categories = {"seg", "track", "merge"}

    def tearDown(self):
        if os.path.isfile(self.debug_center.log_file):
            os.remove(self.debug_center.log_file)
