from api import titlediscovery

import doctest
from hashlib import sha1
import unittest
import os


PATH_TO_MOVIE_FILE = os.path.join(
    os.path.dirname(__file__), 
    'Tears of Steel', 
    'Tears.of.Steel[SHORT].2012.BRRip.AC3.XViD-RemixHD.avi')

MOVIE_FILE_SHA1 = "3f2b0a7ed4bca05a5e5aa9095368ef1b0d856861"

class TestTitleDiscovery(unittest.TestCase):
    def test_file_hash(self):
        title = titlediscovery.discover_title(PATH_TO_MOVIE_FILE)

        self.assertIsNotNone(title)
        self.assertEquals(title.name, "Tears of Steel")
        self.assertEquals(title.year, 2012)
        self.assertEquals(title.imdb_id, "tt2285752")

def hash_matches():
    sha1_val = sha1(open(PATH_TO_MOVIE_FILE, "rb").read()).hexdigest()
    return sha1_val == MOVIE_FILE_SHA1

def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=2)
    tests = doctest.DocTestSuite(titlediscovery)
    if os.path.exists(PATH_TO_MOVIE_FILE) and hash_matches():
        tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(
            TestTitleDiscovery))
    else:
        print 
        print
        print "---------------------------------------------------------------"
        print "Not testing with files. Movie is missing (or incorrect hash).  "
        print "---------------------------------------------------------------"

    test_runner.run(tests)