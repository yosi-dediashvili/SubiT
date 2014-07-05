from api import titlediscovery

import doctest
from hashlib import sha1
import unittest
import os

PATH_TO_MOVIE_FILE = os.path.join(
    os.path.dirname(__file__), 
    'Tears of Steel', 
    'Tears.of.Steel[SHORT].2012.BRRip.AC3.XViD-RemixHD.avi')
PATH_TO_MOCK_FILE = os.path.join(
    os.path.dirname(__file__), 
    'Tears of Steel', 
    'Tears.of.Steel[SHORT].2012.BRRip.AC3.XViD-RemixHD.mock')
PATH_TO_BAD_FILE_NAME = os.path.join(
    os.path.dirname(__file__), 
    'Tears of Steel', 
    'bad_file_name_zzzzzzzz.mock')
PATH_TO_BAD_DIR_AND_FILE_NAME = os.path.join(
    os.path.dirname(__file__), 
    'bad_directory_name_zzzzzzzz', 
    'bad_file_name_zzzzzzzz.mock')

MOVIE_FILE_SHA1 = "3f2b0a7ed4bca05a5e5aa9095368ef1b0d856861"

class TestTitleDiscovery(unittest.TestCase):
    def test_file_hash(self):
        if not os.path.exists(PATH_TO_MOVIE_FILE) or not hash_matches():
            print 
            print
            print "---------------------------------------------------------"
            print "Not testing hash. Movie is missing (or incorrect hash).  "
            print "---------------------------------------------------------"
            return

        title = titlediscovery.discover_title(PATH_TO_MOVIE_FILE)
        self.assertIsNotNone(title)
        self.assertEquals(title.name, "Tears of Steel")
        self.assertEquals(title.year, 2012)
        self.assertEquals(title.imdb_id, "tt2285752")

    def test_no_file_hash_good_file_name(self):
        title = titlediscovery.discover_title(PATH_TO_MOCK_FILE)
        self.assertIsNotNone(title)
        self.assertEquals(title.name, "Tears of Steel")
        self.assertEquals(title.year, 2012)
        self.assertEquals(title.imdb_id, "tt2285752")

    def test_no_file_hash_good_dir_name(self):
        title = titlediscovery.discover_title(PATH_TO_BAD_FILE_NAME)
        self.assertIsNotNone(title)
        self.assertEquals(title.name, "Tears of Steel")
        self.assertEquals(title.year, 2012)
        self.assertEquals(title.imdb_id, "tt2285752")

    def test_no_results(self):
        title = titlediscovery.discover_title(PATH_TO_BAD_DIR_AND_FILE_NAME)
        self.assertIsNone(title)


def hash_matches():
    sha1_val = sha1(open(PATH_TO_MOVIE_FILE, "rb").read()).hexdigest()
    return sha1_val == MOVIE_FILE_SHA1

def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        titlediscovery, 
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(
        TestTitleDiscovery))
    test_runner.run(tests)