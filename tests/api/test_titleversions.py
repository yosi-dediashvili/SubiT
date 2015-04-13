from api.titlesversions import TitlesVersions
from api.version import ProviderVersion
from api.title import MovieTitle
from api.languages import Languages

from helpers import MockedProvider

import unittest

class TestTitleVersions(unittest.TestCase):
    def setUp(self):
        self.titles_versions = TitlesVersions()

    def test_single_title_same_rank_different_language(self):
        title = MovieTitle("The Matrix", 1999)
        heb_version = ProviderVersion(
            [], title, Languages.HEBREW, MockedProvider(), rank=80)
        eng_version = ProviderVersion(
            [], title, Languages.ENGLISH, MockedProvider(), rank=80)

        self.titles_versions.add_version(heb_version)
        self.titles_versions.add_version(eng_version)

        self.assertIn(Languages.HEBREW, self.titles_versions[0][1].keys())
        self.assertIn(Languages.ENGLISH, self.titles_versions[0][1].keys())

        # Check rank groups
        self.assertTrue(
            self.titles_versions[0][1][Languages.HEBREW].has_key(
                heb_version.rank_group))
        self.assertTrue(
            self.titles_versions[0][1][Languages.ENGLISH].has_key(
                eng_version.rank_group))

        self.assertEqual(
            self.titles_versions[0][1][Languages.HEBREW]\
                [heb_version.rank_group][0][1],
            heb_version)
        self.assertEqual(
            self.titles_versions[0][1][Languages.ENGLISH]\
                [eng_version.rank_group][0][1],
            eng_version)

    def test_single_title_same_language_different_rank_group(self):
        title = MovieTitle("The Matrix", 1999)
        a_version = ProviderVersion(
            [], title, Languages.HEBREW, MockedProvider(), rank=80)
        b_version = ProviderVersion(
            [], title, Languages.HEBREW, MockedProvider(), rank=65)

        self.titles_versions.add_version(a_version)
        self.titles_versions.add_version(b_version)

        # Check rank groups
        self.assertTrue(
            self.titles_versions[0][1][Languages.HEBREW].has_key(
                a_version.rank_group))
        self.assertTrue(
            self.titles_versions[0][1][Languages.HEBREW].has_key(
                b_version.rank_group))

        self.assertEqual(
            self.titles_versions[0][1][Languages.HEBREW]\
                [a_version.rank_group][0][1],
            a_version)
        self.assertEqual(
            self.titles_versions[0][1][Languages.HEBREW]\
                [b_version.rank_group][0][1],
            b_version)                

    def test_single_title_same_rank_group_different_rank(self):
        title = MovieTitle("The Matrix", 1999)
        a_version = ProviderVersion(
            [], title, Languages.HEBREW, MockedProvider(), rank=82)
        b_version = ProviderVersion(
            [], title, Languages.HEBREW, MockedProvider(), rank=81)

        self.titles_versions.add_version(a_version)
        self.titles_versions.add_version(b_version)

        # Check rank groups
        self.assertTrue(
            self.titles_versions[0][1][Languages.HEBREW].has_key(
                a_version.rank_group))
        self.assertTrue(
            self.titles_versions[0][1][Languages.HEBREW].has_key(
                b_version.rank_group))

        # Check that the group contain 2 versions.
        self.assertEqual(
            len(self.titles_versions[0][1][Languages.HEBREW]
                [a_version.rank_group]),
            2)

        # Check that the first position is held by the version with the higher
        # rank.
        self.assertEqual(
            self.titles_versions[0][1][Languages.HEBREW]\
                [a_version.rank_group][0][1],
            a_version)
        self.assertEqual(
            self.titles_versions[0][1][Languages.HEBREW]\
                [b_version.rank_group][1][1],
            b_version)       

    def test_single_title_same_rank_different_provider_rank(self):
        title = MovieTitle("The Matrix", 1999)
        a_version = ProviderVersion(
            [], title, Languages.HEBREW, MockedProvider(), rank=80)
        b_version = ProviderVersion(
            [], title, Languages.HEBREW, MockedProvider(), rank=80)

        self.titles_versions.add_version(a_version, provider_rank=1)
        self.titles_versions.add_version(b_version, provider_rank=3)

        # Check rank groups
        self.assertTrue(
            self.titles_versions[0][1][Languages.HEBREW].has_key(
                a_version.rank_group))
        self.assertTrue(
            self.titles_versions[0][1][Languages.HEBREW].has_key(
                b_version.rank_group))

        # Check that the group contain 2 versions.
        self.assertEqual(
            len(self.titles_versions[0][1][Languages.HEBREW]
                [a_version.rank_group]),
            2)

        # Check that the first position is held by the version with the higher
        # provider_rank.
        self.assertEqual(
            self.titles_versions[0][1][Languages.HEBREW]\
                [a_version.rank_group][0][1],
            a_version)
        self.assertEqual(
            self.titles_versions[0][1][Languages.HEBREW]\
                [b_version.rank_group][1][1],
            b_version)  

    def test_single_title_opposite_provider_and_version_rank(self):
        title = MovieTitle("The Matrix", 1999)
        a_version = ProviderVersion(
            [], title, Languages.HEBREW, MockedProvider(), rank=85)
        b_version = ProviderVersion(
            [], title, Languages.HEBREW, MockedProvider(), rank=87)

        self.titles_versions.add_version(a_version, provider_rank=1)
        self.titles_versions.add_version(b_version, provider_rank=3)

        # Check rank groups
        self.assertTrue(
            self.titles_versions[0][1][Languages.HEBREW].has_key(
                a_version.rank_group))
        self.assertTrue(
            self.titles_versions[0][1][Languages.HEBREW].has_key(
                b_version.rank_group))

        # Check that the group contain 2 versions.
        self.assertEqual(
            len(self.titles_versions[0][1][Languages.HEBREW]
                [a_version.rank_group]),
            2)

        # Check that the first position is held by the version with the higher
        # provider_rank.
        self.assertEqual(
            self.titles_versions[0][1][Languages.HEBREW]\
                [a_version.rank_group][0][1],
            a_version)
        self.assertEqual(
            self.titles_versions[0][1][Languages.HEBREW]\
                [b_version.rank_group][1][1],
            b_version) 

    def test_two_titles(self):
        title_a = MovieTitle("The Matrix Reloaded", 2003)
        title_b = MovieTitle("The Green Mile", 1999)

        a_version = ProviderVersion(
            [], title_a, Languages.HEBREW, MockedProvider(), rank=85)
        b_version = ProviderVersion(
            [], title_b, Languages.HEBREW, MockedProvider(), rank=87)

        self.titles_versions.add_version(a_version)
        self.titles_versions.add_version(b_version)

        # Check that we have two titles
        self.assertEqual(len(self.titles_versions), 2)

    def test_same_title_different_instance(self):
        title_a = MovieTitle("The Matrix Reloaded", 2003)
        title_b = MovieTitle("The Matrix Reloaded", 2003)

        a_version = ProviderVersion(
            [], title_a, Languages.HEBREW, MockedProvider(), rank=85)
        b_version = ProviderVersion(
            [], title_b, Languages.HEBREW, MockedProvider(), rank=87)

        self.titles_versions.add_version(a_version)
        self.titles_versions.add_version(b_version)

        self.assertEqual(len(self.titles_versions), 1)

    def test_iteration(self):
        versions_list = []
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))

        versions_list.append(ProviderVersion(
            [], MovieTitle("Titanic"), Languages.ENGLISH, MockedProvider()))

        versions_list.append(ProviderVersion(
            [], MovieTitle("Gladiator"), Languages.ENGLISH, MockedProvider()))

        # Just make sure it works, and we got the titles.
        titles_versions = TitlesVersions(versions_list)
        titles = map(lambda v: v.title, versions_list)
        for title, versions in titles_versions:
            self.assertIn(title, titles)

    def test_iterversions(self):
        versions_list = []
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("Titanic"), Languages.ENGLISH, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("Gladiator"), Languages.ENGLISH, MockedProvider()))
        titles_versions = TitlesVersions(versions_list)

        self.assertEquals(len(list(titles_versions.iter_versions())), 5)

    def test_iter_titles(self):
        versions_list = []
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("Titanic"), Languages.ENGLISH, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("Gladiator"), Languages.ENGLISH, MockedProvider()))
        titles_versions = TitlesVersions(versions_list)

        self.assertEquals(len(list(titles_versions.iter_titles())), 3)

    def test_iter_versions(self):
        versions_list = []
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("The Matrix"), Languages.HEBREW, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("Titanic"), Languages.ENGLISH, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("Titanic"), Languages.ENGLISH, MockedProvider()))
        versions_list.append(ProviderVersion(
            [], MovieTitle("Gladiator"), Languages.ENGLISH, MockedProvider()))
        titles_versions = TitlesVersions(versions_list)

        name_to_len = {"The Matrix" : 3, "Titanic" : 2, "Gladiator" : 1}
        for title, versions in titles_versions.iter_title_versions():
            self.assertEquals(len(versions), name_to_len[title.name])

def run_tests():
    unittest.TextTestRunner(verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestTitleVersions))