# -*- coding: utf-8 -*-
import os
import sys
import unittest

import ep.evaluate_frame as ef
from tests.testbase import TestBase

TMP_DIR = "tmp_test"


class TestEvaluateFrame(TestBase):
    def setUp(self):
        super(TestEvaluateFrame, self).setUp()

    def test_single_evaluation(self):

        ef.evaluate_one_frame()

        pass
