import unittest

import BaseSubProviderTest
from SubProviders.Subtitle.heb_SubtitleProvider import SubtitleProvider

class Test_SubtitleProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    """
    Test class for SubtitleProvider. 
    
    The class derives all the test from BaseSubProviderTest.
    """
    def setUp(self):
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubtitleProvider.SubtitleProvider())