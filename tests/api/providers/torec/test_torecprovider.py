import sys
sys.path.append("..\\..")
import os
from api.providers.torec import provider as torecprovider
TorecProvider = torecprovider.TorecProvider
from api.requestsmanager import RequestsManager
from api.languages import Languages
from api.title import MovieTitle
from api.title import SeriesTitle
from api.version import ProviderVersion
from api.version import Version

import unittest
import doctest


class TestTorecProvider(unittest.TestCase):
    def setUp(self):
        self.provider = TorecProvider(
            [Languages.HEBREW], RequestsManager())

    def test_get_title_versions_multiple_results_with_imdb(self):
        """ 
        Make sure we get results using the IMDB id. This means that the 
        number of titles should be 1 in the result. But if we count the number
        of sub_ids in the version, we'll get the proper number.
        """

        title = MovieTitle("The Matrix", 1999, "tt0133093")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)
        
        self.assertEquals(len(titles_versions), 1)
        created_title = titles_versions[0][0]
        self.assertEquals(created_title.imdb_id, "tt0133093")
        versions = titles_versions[0][1][Languages.HEBREW][1]
        
        sub_ids = [ver[1].attributes['sub_id'] for ver in versions]
        sub_ids = list(set(sub_ids))
        self.assertEquals(len(sub_ids), 4)

    def test_get_title_versions_multiple_results_with_name(self):
        """ Make sure we get results using the movie name. """

        title = MovieTitle("The Matrix", 1999)
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)

        self.assertEquals(len(titles_versions), 4)
        sub_ids = []
        for i in xrange(len(titles_versions)):
            versions = titles_versions[i][1][Languages.HEBREW][1]
            for rank, version in versions:
                sub_ids.append(version.attributes['sub_id'])
            
        sub_ids = list(set(sub_ids))
        self.assertEquals(len(sub_ids), 10)

    def test_get_title_versions_single_movie(self):
        """ Check the content of the movie page. """

        title = MovieTitle("Gone Girl", 2014, "tt2267998")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)
        self.assertEquals(len(titles_versions), 1)
        self.assertEquals(len(titles_versions[0][1]), 1)
        self.assertGreater(
            len(titles_versions[0][1][Languages.HEBREW][1]), 20)

    def test_get_title_versions_series(self):
        """ Make sure we get the episodes correctly. """

        title = SeriesTitle(
            "The Big Bang Theory", 6, 5, "tt2411582", 
            "The Holographic Excitation", 2012, "tt0898266")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)

        self.assertEquals(len(titles_versions), 1)
        self.assertEquals(len(titles_versions[0][1]), 1)
        self.assertGreater(\
            len(titles_versions[0][1][Languages.HEBREW][1]), 4)

    def test_download_subtitle_buffer(self):
        """ Make sure we download a file correctly (and the fake one). """
        title = MovieTitle("Gone Girl", 2014, "tt2267998")
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)
        provider_versions = titles_versions[0][1][Languages.HEBREW][1]
        provider_version = filter(
            lambda v: v.version_string == \
                "Gone.Girl.2014.1080p.BluRay.x264-SPARKS",
            provider_versions)

        name, buffer = self.provider.download_subtitle_buffer(provider_version)
        self.assertEquals(name, "Gone.Girl.2014.1080p.BluRay.x264-SPARKS.zip")
        self.assertGreater(len(buffer), 4096)


def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        torecprovider, 
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    tests.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestTorecProvider))

    test_runner.run(tests)