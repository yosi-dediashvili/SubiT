import sys
sys.path.append("..\\..")
import os
import time
from api.providers.torec.hamster import TorecHashCodesHamster
from api.requestsmanager import RequestsManager

import unittest

class TestTorecHashCodeHamster(unittest.TestCase):
    def setUp(self):
        self.hamster = TorecHashCodesHamster(RequestsManager())

    def test_remove_after_max_time_passed(self):
        self.hamster.add_sub_id("23703")
        self.hamster.add_sub_id("2638")
        self.assertEquals(len(self.hamster._records), 2)
        time.sleep(10)
        self.assertEquals(len(self.hamster._records), 2)
        time.sleep(120)
        self.assertEquals(len(self.hamster._records), 0)

    def test_remove_after_after_request(self):
        self.hamster.add_sub_id("23703")
        self.hamster.add_sub_id("2638")
        self.assertEquals(len(self.hamster._records), 2)
        self.hamster.remove_sub_id("2638")
        self.assertEquals(len(self.hamster._records), 1)
        self.assertEquals(self.hamster._records.keys()[0], "23703")


def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestTorecHashCodeHamster)
    test_runner.run(tests)