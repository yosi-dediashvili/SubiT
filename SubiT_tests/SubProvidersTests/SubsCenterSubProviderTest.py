"""
Test classes for SubsCenterProvider. 
    
The classes derives all the test from BaseSubProviderTest.
"""

import unittest

import BaseSubProviderTest

class Test_eng_SubsCenterProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.SubsCenter.eng_SubsCenterProvider import \
            SubsCenterProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubsCenterProvider.SubsCenterProvider())

class Test_heb_SubsCenterProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.SubsCenter.heb_SubsCenterProvider import \
            SubsCenterProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubsCenterProvider.SubsCenterProvider())
