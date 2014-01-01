import unittest

import BaseSubProviderTest
from SubProviders.OpenSubtitles.heb_OpenSubtitlesProvider import OpenSubtitlesProvider

class Test_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    """
    Test class for OpenSubtitlesProvider. 
    
    The class derives all the test from BaseSubProviderTest.
    """
    def setUp(self):
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())