"""
Test classes for Addic7edProvider. 
    
The classes derives all the test from BaseSubProviderTest.
"""
import unittest

import BaseSubProviderTest

class Test_heb_Addic7edProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.Addic7ed.heb_Addic7edProvider import Addic7edProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            Addic7edProvider.Addic7edProvider())

class Test_eng_Addic7edProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.Addic7ed.eng_Addic7edProvider import Addic7edProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            Addic7edProvider.Addic7edProvider())

class Test_nor_Addic7edProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.Addic7ed.nor_Addic7edProvider import Addic7edProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            Addic7edProvider.Addic7edProvider())

class Test_rus_Addic7edProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.Addic7ed.rus_Addic7edProvider import Addic7edProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            Addic7edProvider.Addic7edProvider())