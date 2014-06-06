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

class Test_spa_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.spa_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())

class Test_tur_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.tur_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())

class Test_slo_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.slo_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())

class Test_cze_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.cze_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())

class Test_bul_OpenSubtitlesProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.OpenSubtitles.bul_OpenSubtitlesProvider import \
            OpenSubtitlesProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            OpenSubtitlesProvider.OpenSubtitlesProvider())