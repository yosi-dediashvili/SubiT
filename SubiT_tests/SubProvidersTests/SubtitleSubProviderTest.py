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
            SubtitleProvider.SubtitleProvider())

class Test_heb_SubtitleProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.Subtitle.heb_SubtitleProvider import SubtitleProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubtitleProvider.SubtitleProvider())