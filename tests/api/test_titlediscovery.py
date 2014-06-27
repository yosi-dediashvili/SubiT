from api import titlediscovery

import doctest
import unittest
import os


PATH_TO_MOVIE_FILE = os.path.join(
    os.path.dirname(__file__), 
    'Tears of Steel', 
    'Tears.of.Steel[SHORT].2012.BRRip.AC3.XViD-RemixHD.avi')

class TestTitleDiscovery(unittest.TestCase):
    def test_file_hash(self):
        title = titlediscovery.discover_title(PATH_TO_MOVIE_FILE)
        
        self.assertIsNotNone(title)
        self.assertEquals(title.name, "Tears of Steel")
        self.assertEquals(title.year, 2012)
        self.assertEquals(title.imdb_id, "tt2285752")

def run_tests():
    doctest.testmod(
        titlediscovery, 
        verbose=False, 
        optionflags=doctest.NORMALIZE_WHITESPACE)

    if os.path.exists(PATH_TO_MOVIE_FILE):
        unittest.TextTestRunner(verbosity=0).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(TestDiscoveryTest))
    else:
        print 
        print
        print "------------------------------------------------------"
        print "Not testing with real files. Movie is missing."
        print "------------------------------------------------------"