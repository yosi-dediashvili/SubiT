from api import version
from api.providers.iprovider import IProvider
from api.title import MovieTitle
from api.languages import Languages

from helpers import MockedProvider

import doctest
import unittest


class TestProviderVersion(unittest.TestCase):
    def setUp(self):
        self.title = MovieTitle("The Matrix")
        self.lang = Languages.HEBREW
        self.provider = MockedProvider()

    def test_invalid_language(self):
        from api.exceptions import InvalidLanguageValue
        with self.assertRaisesRegexp(InvalidLanguageValue, 
            "language instance must be supplied\."):
            version.ProviderVersion([], self.title, "hebrew", self.provider)

    def test_invalid_provider(self):
        from api.exceptions import InvalidProviderValue
        with self.assertRaisesRegexp(InvalidProviderValue, 
            "provider instance must be supplied\."):
            version.ProviderVersion([], self.title, self.lang, object())

    def test_rank_group(self):
        provider_version = version.ProviderVersion(
            [], self.title, self.lang, self.provider)
        self.assertEqual(provider_version.rank_group, 1)
        provider_version.rank = 61
        self.assertEqual(provider_version.rank_group, 7)
        provider_version.rank = 100
        self.assertEqual(provider_version.rank_group, 10)

    def test_rank(self):
        provider_version = version.ProviderVersion(
            [], self.title, self.lang, self.provider)
        from api.exceptions import InvalidRankValue
        with self.assertRaisesRegexp(InvalidRankValue, 
            "rank value must be between 0 to 100."):
            provider_version.rank = 101

        with self.assertRaisesRegexp(InvalidRankValue, 
            "rank value must be between 0 to 100."):
            provider_version.rank = -1

    def test_repr(self):
        provider_version = version.ProviderVersion(
            ["720p", "dts"], self.title, self.lang, self.provider, rank=60,
            version_string="the.matrix.1999.720p.dts")
        self.assertRegexpMatches(
            str(provider_version), 
            "\<ProviderVersion identifiers\=\['720p', 'dts'\], "
            "title\=\<MovieTitle .*?\>, language\=\<Language .*?\>, "
            "provider\=\<Provider .*?\>, "
            "version_string='the\.matrix\.1999\.720p\.dts', "
            "attributes\=\{.*?\}, num_of_cds\=0, rank\=60, rank_group\=6\>")


def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        version,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    tests.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestProviderVersion))
    test_runner.run(tests)