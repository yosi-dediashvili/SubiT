"""
Test classes for OpenSubtitlesProvider. 
    
The classes derives all the test from BaseSubProviderTest.
"""

import unittest

import BaseSubProviderTest

class Test_all_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.all_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())

class Test_eng_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.eng_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())

class Test_heb_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.heb_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())

class Test_nor_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.nor_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())

class Test_rus_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.rus_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())