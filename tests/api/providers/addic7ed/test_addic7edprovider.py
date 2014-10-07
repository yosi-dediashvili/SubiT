import sys
sys.path.append("..\\..")
import os

from api.providers.addic7ed import Addic7edProvider
from api.requestsmanager import get_manager_instance
from api.languages import Languages
from api.title import MovieTitle
from api.title import SeriesTitle
from api.version import ProviderVersion
from api.version import Version

import unittest
import doctest

class TestAddic7edProvider(unittest.TestCase):
    def setUp(self):
        self.provider = Addic7edProvider(
            [Languages.ENGLISH], get_manager_instance("test_addic7ed_provider"))

    def test_get_titles_versions_series(self):
        """ Simple test to verify that we get version for series. """
        raise NotImplementedError()

    def test_get_titles_versions_movie(self):
        """ Simple test to verify that we get version for movie. """
        raise NotImplementedError()

    def test_get_subtitle_buffer(self):
        """
        Test that given some ProviderVersion, we manage to get the buffer of
        the subtitle.
        """
        raise NotImplementedError()


def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        addic7edprovider,
        optionflags=doctest.NORMALIZE_WHITESPACE)
    tests.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestAddic7edProvider))
    test_runner.run(tests)