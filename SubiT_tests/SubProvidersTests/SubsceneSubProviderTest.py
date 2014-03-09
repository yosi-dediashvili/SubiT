"""
Test classes for SubsceneProvider. 
    
The classes derives all the test from BaseSubProviderTest.
"""

import unittest

import BaseSubProviderTest
from TestUtils import WriteTestLog


class base_SubscenceProviderTest(BaseSubProviderTest.BaseSubProviderTest):
    def __init__(
        self, 
        provider, 
        movie_query = 'Batman The Dark Knight', 
        series_query = 'The Big Bang Theory'):

        BaseSubProviderTest.BaseSubProviderTest.__init__(
            self,
            provider,
            movie_query,
            series_query)

    def findMovieSubStageList(self, query):
        WriteTestLog("Our version got called.")
        movies = \
            BaseSubProviderTest.BaseSubProviderTest.findMovieSubStageList(
                self, query)

        # Return a one item list (so we'll always be selected).
        return [movies[0]]


class Test_heb_SubsceneProviderTest(
    unittest.TestCase, base_SubscenceProviderTest):
    def setUp(self):
        from SubProviders.Subscene.heb_SubsceneProvider import SubsceneProvider
        base_SubscenceProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider())

class Test_eng_SubsceneProviderTest(
    unittest.TestCase, base_SubscenceProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.eng_SubsceneProvider import SubsceneProvider
        base_SubscenceProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider())

class Test_spa_SubsceneProviderTest(
    unittest.TestCase, base_SubscenceProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.spa_SubsceneProvider import SubsceneProvider
        base_SubscenceProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider(),
            series_query = 'Lost Fourth Season')

class Test_tur_SubsceneProviderTest(
    unittest.TestCase, base_SubscenceProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.tur_SubsceneProvider import SubsceneProvider
        base_SubscenceProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider(),
            series_query = 'Heroes Third Season')

class Test_slo_SubsceneProviderTest(
    unittest.TestCase, base_SubscenceProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.slo_SubsceneProvider import SubsceneProvider
        base_SubscenceProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider(),
            series_query = 'Lost Fourth Season')

class Test_cze_SubsceneProviderTest(
    unittest.TestCase, base_SubscenceProviderTest):    
    def setUp(self):
        from SubProviders.Subscene.cze_SubsceneProvider import SubsceneProvider
        base_SubscenceProviderTest.__init__(
            self, 
            SubsceneProvider.SubsceneProvider(),
            series_query = 'Lost Fifth Season')