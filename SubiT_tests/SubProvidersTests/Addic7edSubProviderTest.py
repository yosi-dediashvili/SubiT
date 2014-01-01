import unittest

import BaseSubProviderTest
from SubProviders.Addic7ed.heb_Addic7edProvider import Addic7edProvider

class Test_Addic7edProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    """
    Test class for Addic7edProvider. 
    
    The class derives all the test from BaseSubProviderTest.
    """
    def setUp(self):
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            Addic7edProvider.Addic7edProvider())