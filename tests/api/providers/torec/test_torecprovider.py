import sys
sys.path.append("..\\..")
import os
from api.providers.torec import provider as torecprovider
TorecProvider = torecprovider.TorecProvider
from api.requestsmanager import RequestsManager
from api.languages import Languages
from api.title import MovieTitle
from api.title import SeriesTitle
from api.version import ProviderVersion
from api.version import Version

import unittest
import doctest


class TestTorecProvider(unittest.TestCase):
    def setUp(self):
        self.provider = TorecProvider(
            [Languages.HEBREW], RequestsManager())


def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        torecprovider, 
        optionflags=doctest.NORMALIZE_WHITESPACE)
    tests.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestTorecProvider))
    test_runner.run(tests)