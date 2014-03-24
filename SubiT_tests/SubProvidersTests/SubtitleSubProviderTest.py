"""
Test classes for SubtitleProvider. 
    
The classes derives all the test from BaseSubProviderTest.
"""

import unittest

import BaseSubProviderTest

class Test_eng_SubtitleProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.Subtitle.eng_SubtitleProvider import SubtitleProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubtitleProvider.SubtitleProvider(),
            # IMDB's id for The Matrix Reloaded
            "tt0234215",
            # The IMDB's id for Lost series.
            "tt0411008")

class Test_heb_SubtitleProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.Subtitle.heb_SubtitleProvider import SubtitleProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubtitleProvider.SubtitleProvider())