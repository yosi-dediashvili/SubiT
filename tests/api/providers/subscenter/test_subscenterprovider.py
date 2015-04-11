import sys
sys.path.append("..\\..")
import os
from api.providers.subscenter import provider as subscenterprovider
SubscenterProvider = subscenterprovider.SubscenterProvider
from api.requestsmanager import RequestsManager
from api.languages import Languages
from api.title import MovieTitle
from api.title import SeriesTitle
from api.version import ProviderVersion
from api.version import Version

import unittest
import doctest


class TestSubscenterProvider(unittest.TestCase):
    def setUp(self):
        self.provider = SubscenterProvider(
            [Languages.HEBREW], RequestsManager())


    def test_get_title_versions_multiple_results(self):
        """ Make sure we get results using the movie name. """

        title = MovieTitle("The Matrix", 1999)
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)

        self.assertEquals(len(titles_versions), 4)
        for i in xrange(len(titles_versions)):
            versions = titles_versions[i][1][Languages.HEBREW][1]
            self.assertGreater(len(versions), 0)

    def test_get_title_versions_single_movie(self):
        """ Check the content of the movie page. """

        title = MovieTitle("Gone Girl", 2014)
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)
        self.assertEquals(len(titles_versions), 1)
        self.assertEquals(len(titles_versions[0][1]), 1)
        self.assertGreater(
            len(titles_versions[0][1][Languages.HEBREW][1]), 30)

    def test_get_title_versions_series(self):
        """ Make sure we get the episodes correctly. """

        title = SeriesTitle("The Big Bang Theory", 6, 5)
        fake_version = Version(["identifier"], title)

        titles_versions = self.provider.get_title_versions(title, fake_version)

        self.assertEquals(len(titles_versions), 1)
        self.assertEquals(len(titles_versions[0][1]), 1)
        self.assertGreater(
            len(titles_versions[0][1][Languages.HEBREW][1]), 2)

    def test_download_subtitle_buffer(self):
        """ Make sure we download a file correctly (and the fake one). """

        title = MovieTitle("Gone Girl", 2014)
        provider_version = ProviderVersion(
            ['1080p', 'BluRay', 'x264', 'SPARKS'],
            title,
            Languages.HEBREW,
            self.provider, 
            "Gone.Girl.2014.1080p.BluRay.x264-SPARKS",
            attributes = {
                'version_id' : '272642', 
                'version_key' : '578eba9f382d67da4bbcf150fde53642'})

        name, buffer = self.provider.download_subtitle_buffer(provider_version)
        self.assertEquals(
            name, "Gone.Girl.2014.1080p.BluRay.x264-SPARKS.B272642.zip")
        self.assertGreater(len(buffer), 4096)


def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(
            TestSubscenterProvider)
    test_runner.run(tests)