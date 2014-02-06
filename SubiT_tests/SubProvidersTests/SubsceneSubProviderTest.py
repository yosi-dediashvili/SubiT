"""
Test classes for SubsceneProvider. 
    
The classes derives all the test from BaseSubProviderTest.
"""

import unittest

import BaseSubProviderTest

class Test_heb_SubsceneProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):
    def setUp(self):
        from SubProviders.Subscene.heb_SubsceneProvider import SubsceneProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider())

class Test_eng_SubsceneProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.eng_SubsceneProvider import SubsceneProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider())

class Test_spa_SubsceneProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.spa_SubsceneProvider import SubsceneProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider())

class Test_tur_SubsceneProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.tur_SubsceneProvider import SubsceneProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider())

class Test_slo_SubsceneProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.slo_SubsceneProvider import SubsceneProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider())

class Test_cze_SubsceneProviderTest(
    unittest.TestCase, BaseSubProviderTest.BaseSubProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.cze_SubsceneProvider import SubsceneProvider
        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider())