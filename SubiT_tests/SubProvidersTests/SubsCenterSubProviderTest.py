import unittest

import BaseSubProviderTest
from SubProviders.SubsCenter.heb_SubsCenterProvider import SubsCenterProvider

class Test_SubsCenterProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    """
    Test class for SubsCenterProvider. 
    
    The class derives all the test from BaseSubProviderTest.
    """
    def setUp(self):
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubsCenterProvider.SubsCenterProvider())