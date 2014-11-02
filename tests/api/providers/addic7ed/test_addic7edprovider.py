import sys
sys.path.append("..\\..")
import os

from api.providers.addic7ed import provider as addic7edprovider
Addic7edProvider = addic7edprovider.Addic7edProvider
from api.requestsmanager import get_manager_instance
from api.languages import Languages
from api.title import MovieTitle
from api.title import SeriesTitle
from api.version import ProviderVersion
from api.version import Version

import unittest
import doctest

class TestAddic7edProvider(unittest.TestCase):
    def setUp(self):
        self.provider = Addic7edProvider(
            [Languages.ENGLISH], get_manager_instance("test_addic7ed_provider"))

    def test_get_titles_versions_no_match(self):
        """
        Checks that we get more than single result when the query returns more
        than one title in the site.
        """
        title = MovieTitle("Star Wars")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)
        # We expect to see 129 Series titles, and 1 Movie title.
        serieses = filter(lambda t: isinstance(t, SeriesTitle), titles_versions)
        movies = filter(lambda t: isinstance(t, MovieTitle), titles_versions)

        self.assertEquals(len(serieses), 129)
        self.assertEquals(len(movies), 1)

    def test_get_titles_versions_no_title(self):
        """
        Checks that we get an empty list when querying for some random letters.
        """
        title = MovieTitle("silhjkl;sdgsdg sdgfsg")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)
        self.assertEquals(len(title_versions), 0)


    def test_get_titles_versions_series_exact(self):
        """
        Simple test to verify that we get version for series. We expect to see
        single SeriesTitle in the result.
        """
        title = SeriesTitle(
            "The Big Bang Theory", 7, 12, "tt3337728",
            "The Hesitation Ramification", 2014, "tt0898266")

        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)

        # Only single title is expected
        self.assertEqual(len(titles_versions), 1)
        # Only single language
        self.assertEqual(len(titles_versions[0][1]), 1)
        # Four versions (At rank group 1)
        versions = titles_versions[0][1][Languages.ENGLISH][1]
        self.assertEqual(len(versions), 4)

        self.assertEquals(versions[0].version_string, "DIMENSION")
        self.assertEquals(versions[1].version_string, "WEB-DL")
        self.assertEquals(versions[2].version_string, "DIMENSION")
        self.assertEquals(versions[3].version_string, "WEB-DL")

        self.assertEquals(
            versions[0].addributes["movie_code"],
            "serie/The%20Big%20Bang%20Theory/7/12/1")
        self.assertEquals(
            versions[1].addributes["movie_code"],
            "serie/The%20Big%20Bang%20Theory/7/12/1")
        self.assertEquals(
            versions[2].addributes["movie_code"],
            "serie/The%20Big%20Bang%20Theory/7/12/1")
        self.assertEquals(
            versions[3].addributes["movie_code"],
            "serie/The%20Big%20Bang%20Theory/7/12/1")

        self.assertEquals(
            versions[0].addributes["version_code"], "/original/82674/0")
        self.assertEquals(
            versions[1].addributes["version_code"], "/original/82674/4")
        self.assertEquals(
            versions[2].addributes["version_code"], "/original/82674/1")
        self.assertEquals(
            versions[3].addributes["version_code"], "/original/82674/3")

    def test_get_titles_versions_movie_exact(self):
        """
        Simple test to verify that we get versions for movie. The query
        returns a single movie in the site.
        """
        title = MovieTitle("Godzilla", 2014, "tt0831387")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)

        # Only single title is expected
        self.assertEqual(len(titles_versions), 1)
        # Only single language
        self.assertEqual(len(titles_versions[0][1]), 1)
        # Two versions (At rank group 1)
        versions = titles_versions[0][1][Languages.ENGLISH][1]
        self.assertEqual(len(versions), 2)

        self.assertEquals(versions[0].version_string, "BluRay_BRrip_BDrip")
        self.assertEquals(versions[1].version_string, "WEBRiP-VAiN")

        self.assertEquals(versions[0].addributes["movie_code"], "/movie/89128")
        self.assertEquals(versions[1].addributes["movie_code"], "/movie/89128")

        self.assertEquals(
            versions[0].addributes["version_code"], "/original/89128/4")
        self.assertEquals(
            versions[1].addributes["version_code"], "/original/89128/2")

    def test_get_subtitle_buffer(self):
        """
        Test that given some ProviderVersion, we manage to get the buffer of
        the subtitle.
        """
        title = SeriesTitle("The Big Bang Theory", 7, 12)
        version = ProviderVersion(
            [],
            title,
            Languages.ENGLISH,
            self.provider,
            attributes = {
                "DownloadURL" : "http://www.addic7ed.com/original/82674/0"})
        file_name, subtitle_buffer = \
            self.provider.download_subtitle_buffer(version)
        self.assertEquals(
            file_name,
            "The Big Bang Theory - 07x12 - The Hesitation Ramification.DIMENSION.English.HI.C.orig.Addic7ed.com.srt")
        self.assertGreater(len(subtitle_buffer), 31000)



def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        addic7edprovider,
        optionflags=doctest.NORMALIZE_WHITESPACE)
    tests.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestAddic7edProvider))
    test_runner.run(tests)