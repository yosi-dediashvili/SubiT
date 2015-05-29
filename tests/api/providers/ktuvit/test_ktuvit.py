import sys
sys.path.append("..\\..")
import os
from api.providers.ktuvit import provider as ktuvitprovider
KtuvitProvider = ktuvitprovider.KtuvitProvider
from api.requestsmanager import RequestsManager
from api.languages import Languages
from api.title import MovieTitle
from api.title import SeriesTitle
from api.version import ProviderVersion
from api.version import Version

import unittest
import doctest


class TestKtuvitProvider(unittest.TestCase):
    def setUp(self):
        self.provider = KtuvitProvider(
            [Languages.HEBREW], RequestsManager())

    def _test_get_title_versions_title(self, title, title_to_versions):
        fake_version = Version(["identifier"], title)
        titles_versions =  self.provider.get_title_versions(title, fake_version)
        for title, versions in titles_versions.iter_title_versions():
            self.assertIn(title.name, title_to_versions)
            self.assertEquals(len(versions), title_to_versions[title.name][0])
            self.assertIn(title_to_versions[title.name][1], 
                [version.version_string for version in versions])
        return titles_versions

    def test_get_title_versions_movie_by_name(self):
        title = MovieTitle("The Matrix", 1999)
        title_name_to_versions_length = {
            "The Matrix" : 
                (37, 'The.Matrix.1999.iNTERNAL.DVDRip.XviD.AC3-XviK'),
            "The Matrix Reloaded" : 
                (20, 'The.Matrix.Reloaded.2003.HDDVDRip.XviD.AC3.PRoDJi'),
            "The Matrix Revolution" : 
                (21, 'The.Matrix.Revolutions.2003.1080p.HDDVD.x264-hV'), 
            "The Animatrix" : 
                (7, 'The.Animatrix.2003.720p.BluRay.x264-HANGOVER'),
            "The Making Of The Matrix" : (1, '')
        }
        self._test_get_title_versions_title(
            title, title_name_to_versions_length)

    def test_get_title_versions_movie_by_imdbid(self):
        title = MovieTitle("The Matrix", 1999, "tt0133093")
        title_name_to_versions_length = {
            title.name : (37, 'The.Matrix.[1999].720p.BluRay.x264.AAC-ZoNe')
        }
        self._test_get_title_versions_title(
            title, title_name_to_versions_length)

    def _test_get_title_versions_episode(self, title):
        title_name_to_versions_length = {
            title.name : 
                (3, 'The.Big.Bang.Theory.S06E05.720p.HDTV.X264-DIMENSION')
        }
        titles_versions = self._test_get_title_versions_title(
            title, title_name_to_versions_length)
        title_got = next(titles_versions.iter_titles())
        self.assertEquals(title_got, title)

    def test_get_title_versions_episode_by_series_name(self):
        title = SeriesTitle("The Big Bang Theory", 6, 5, year=2012)
        self._test_get_title_versions_episode(title)
        
    def test_get_title_versions_episode_by_series_imdbid(self):
        title = SeriesTitle("The Big Bang Theory", 6, 5, imdb_id="tt0898266")
        self._test_get_title_versions_episode(title)

    def test_download_subtitle_buffer(self):
        title = SeriesTitle("The Big Bang Theory", 6, 5, imdb_id="tt0898266")
        provider_version = ProviderVersion(
            ['720p', 'HDTV', 'X264', 'DIMENSION'],
            title,
            Languages.HEBREW,
            self.provider,
            "The.Big.Bang.Theory.S06E05.720p.HDTV.X264-DIMENSION",
            attributes = {
                'version_id' : '229373'
            })
        name, buffer = self.provider.download_subtitle_buffer(provider_version)
        self.assertEquals(name, 
            "Subtitle.The.Big.Bang.Theory.Season.6.Episode.5.The.Holographic.Excitation.123759.zip")
        self.assertGreater(len(buffer), 8192)
        

def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        ktuvitprovider, 
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    tests.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestKtuvitProvider))

    test_runner.run(tests)