from api.titleversions import TitleVersions
from api.version import ProviderVersion
from api.title import MovieTitle
from api.languages import Languages

from helpers import MockedProvider

import unittest

class TestTitleVersions(unittest.TestCase):
    def setUp(self):
        self.title = MovieTitle("The Matrix")
        self.title_versions = TitleVersions(self.title)

    def test_same_rank_different_language(self):
        heb_version = ProviderVersion(
            [], self.title, Languages.HEBREW, MockedProvider(), rank=80)
        eng_version = ProviderVersion(
            [], self.title, Languages.ENGLISH, MockedProvider(), rank=80)

        self.title_versions.add_version(heb_version)
        self.title_versions.add_version(eng_version)

        self.assertIn(Languages.HEBREW, self.title_versions.versions.keys())
        self.assertIn(Languages.ENGLISH, self.title_versions.versions.keys())

        # Check rank groups
        self.assertTrue(
            self.title_versions.versions[Languages.HEBREW].has_key(
                heb_version.rank_group))
        self.assertTrue(
            self.title_versions.versions[Languages.ENGLISH].has_key(
                eng_version.rank_group))

        self.assertEqual(
            self.title_versions.versions[Languages.HEBREW]\
                [heb_version.rank_group][0][1],
            heb_version)
        self.assertEqual(
            self.title_versions.versions[Languages.ENGLISH]\
                [eng_version.rank_group][0][1],
            eng_version)

    def test_same_language_different_rank_group(self):
        a_version = ProviderVersion(
            [], self.title, Languages.HEBREW, MockedProvider(), rank=80)
        b_version = ProviderVersion(
            [], self.title, Languages.HEBREW, MockedProvider(), rank=65)

        self.title_versions.add_version(a_version)
        self.title_versions.add_version(b_version)

        # Check rank groups
        self.assertTrue(
            self.title_versions.versions[Languages.HEBREW].has_key(
                a_version.rank_group))
        self.assertTrue(
            self.title_versions.versions[Languages.HEBREW].has_key(
                b_version.rank_group))

        self.assertEqual(
            self.title_versions.versions[Languages.HEBREW]\
                [a_version.rank_group][0][1],
            a_version)
        self.assertEqual(
            self.title_versions.versions[Languages.HEBREW]\
                [b_version.rank_group][0][1],
            b_version)                

    def test_same_rank_group_different_rank(self):
        a_version = ProviderVersion(
            [], self.title, Languages.HEBREW, MockedProvider(), rank=82)
        b_version = ProviderVersion(
            [], self.title, Languages.HEBREW, MockedProvider(), rank=81)

        self.title_versions.add_version(a_version)
        self.title_versions.add_version(b_version)

        # Check rank groups
        self.assertTrue(
            self.title_versions.versions[Languages.HEBREW].has_key(
                a_version.rank_group))
        self.assertTrue(
            self.title_versions.versions[Languages.HEBREW].has_key(
                b_version.rank_group))

        # Check that the group contain 2 versions.
        self.assertEqual(
            len(self.title_versions.versions[Languages.HEBREW]
                [a_version.rank_group]),
            2)

        # Check that the first position is held by the version with the higher
        # rank.
        self.assertEqual(
            self.title_versions.versions[Languages.HEBREW]\
                [a_version.rank_group][0][1],
            a_version)
        self.assertEqual(
            self.title_versions.versions[Languages.HEBREW]\
                [b_version.rank_group][1][1],
            b_version)       

    def test_same_rank_different_provider_rank(self):
        a_version = ProviderVersion(
            [], self.title, Languages.HEBREW, MockedProvider(), rank=80)
        b_version = ProviderVersion(
            [], self.title, Languages.HEBREW, MockedProvider(), rank=80)

        self.title_versions.add_version(a_version, provider_rank=1)
        self.title_versions.add_version(b_version, provider_rank=3)

        # Check rank groups
        self.assertTrue(
            self.title_versions.versions[Languages.HEBREW].has_key(
                a_version.rank_group))
        self.assertTrue(
            self.title_versions.versions[Languages.HEBREW].has_key(
                b_version.rank_group))

        # Check that the group contain 2 versions.
        self.assertEqual(
            len(self.title_versions.versions[Languages.HEBREW]
                [a_version.rank_group]),
            2)

        # Check that the first position is held by the version with the higher
        # provider_rank.
        self.assertEqual(
            self.title_versions.versions[Languages.HEBREW]\
                [a_version.rank_group][0][1],
            a_version)
        self.assertEqual(
            self.title_versions.versions[Languages.HEBREW]\
                [b_version.rank_group][1][1],
            b_version)  

    def test_opposite_provider_and_version_rank(self):
        a_version = ProviderVersion(
            [], self.title, Languages.HEBREW, MockedProvider(), rank=85)
        b_version = ProviderVersion(
            [], self.title, Languages.HEBREW, MockedProvider(), rank=87)

        self.title_versions.add_version(a_version, provider_rank=1)
        self.title_versions.add_version(b_version, provider_rank=3)

        # Check rank groups
        self.assertTrue(
            self.title_versions.versions[Languages.HEBREW].has_key(
                a_version.rank_group))
        self.assertTrue(
            self.title_versions.versions[Languages.HEBREW].has_key(
                b_version.rank_group))

        # Check that the group contain 2 versions.
        self.assertEqual(
            len(self.title_versions.versions[Languages.HEBREW]
                [a_version.rank_group]),
            2)

        # Check that the first position is held by the version with the higher
        # provider_rank.
        self.assertEqual(
            self.title_versions.versions[Languages.HEBREW]\
                [a_version.rank_group][0][1],
            a_version)
        self.assertEqual(
            self.title_versions.versions[Languages.HEBREW]\
                [b_version.rank_group][1][1],
            b_version) 


def run_tests():
    unittest.TextTestRunner(verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestTitleVersions))