import sys
sys.path.append("..\\..")
import os
from api.providers.opensubtitles import opensubtitlesprovider
from api.providers.opensubtitles import OpenSubtitlesRequestsManager
OpenSubtitlesProvider = opensubtitlesprovider.OpenSubtitlesProvider
from api.languages import Languages
from api.title import MovieTitle
from api.title import SeriesTitle
from api.version import ProviderVersion

import unittest
import doctest

AVI_FILE_PATH = os.path.join(os.path.dirname(__file__), "breakdance.avi")
AVI_FILE_HASH = "8e245d9679d31e12"

class TestOpenSubtitlesProvider(unittest.TestCase):
    def setUp(self):
        self.provider = OpenSubtitlesProvider(
            [Languages.ENGLISH], OpenSubtitlesRequestsManager())

    def test_calculate_hash(self):
        h, s = self.provider.calculate_file_hash(AVI_FILE_PATH)
        self.assertEqual(h.lower(), AVI_FILE_HASH)

    def test_get_title_by_imdb_id_movie(self):
        title = self.provider.get_title_by_imdb_id("tt0133093")
        self.assertIsNotNone(title)
        self.assertIsInstance(title, MovieTitle)
        self.assertEquals(title.name, "The Matrix")
        self.assertEquals(title.year, 1999)
        self.assertEquals(title.imdb_id, "tt0133093")

    def test_get_title_by_imdb_id_series(self):
        title = self.provider.get_title_by_imdb_id("tt2392630")
        self.assertIsNotNone(title)
        self.assertIsInstance(title, SeriesTitle)
        self.assertEquals(title.name, "The Big Bang Theory")
        self.assertEquals(title.year, 2012)
        self.assertEquals(title.imdb_id, "tt0898266")
        self.assertEquals(title.episode_imdb_id, "tt2392630")
        self.assertEquals(title.season_number, 6)
        self.assertEquals(title.episode_number, 2)
        self.assertEquals(title.episode_name, "The Decoupling Fluctuation")

    def test_get_title_by_hash_movie(self):
        h = "66ea24e3ad41fd47"
        size = 8425019199
        title = self.provider.get_title_by_hash(h, size)
        self.assertIsNotNone(title)
        self.assertIsInstance(title, MovieTitle)
        self.assertEquals(title.name, "The Matrix")
        self.assertEquals(title.year, 1999)
        self.assertEquals(title.imdb_id, "tt0133093")

    def test_get_title_by_hash_series(self):
        h = "46e33be00464c12e"
        title = self.provider.get_title_by_hash(h)
        self.assertIsNotNone(title)
        self.assertIsInstance(title, SeriesTitle)
        self.assertEquals(title.name, "Game of Thrones")
        self.assertEquals(title.year, 2014)
        self.assertEquals(title.imdb_id, "tt0944947")
        self.assertEquals(title.episode_imdb_id, "tt2816136")
        self.assertEquals(title.season_number, 4)
        self.assertEquals(title.episode_number, 1)
        self.assertEquals(title.episode_name, "Two Swords")

    def test_get_title_by_hash_none(self):
        h = "51512252523fe123"
        title = self.provider.get_title_by_hash(h)
        self.assertIsNone(title)

    def test_get_title_by_query_movie(self):
        q = "enders.game.2013.720p.bluray.x264-sparks"
        title = self.provider.get_title_by_query(q)
        self.assertIsNotNone(title)
        self.assertIsInstance(title, MovieTitle)
        self.assertEquals(title.name, "Ender's Game")
        self.assertEquals(title.year, 2013)
        self.assertEquals(title.imdb_id, "tt1731141")

    def test_get_title_by_query_series(self):
        q = "The.Big.Bang.Theory.S06E02.720p.HDTV.X264-DIMENSION"
        title = self.provider.get_title_by_query(q)
        self.assertIsNotNone(title)
        self.assertIsInstance(title, SeriesTitle)
        self.assertEquals(title.name, "The Big Bang Theory")
        self.assertEquals(title.year, 2012)
        self.assertEquals(title.imdb_id, "tt0898266")
        self.assertEquals(title.episode_imdb_id, "tt2392630")
        self.assertEquals(title.season_number, 6)
        self.assertEquals(title.episode_number, 2)
        self.assertEquals(title.episode_name, "The Decoupling Fluctuation")

    def test_get_title_by_query_os_buggy(self):
        q = "The.Lego.Movie.2014.720p.BluRay.DD5.1.x264-HiDt"
        title = self.provider.get_title_by_query(q)
        self.assertIsNotNone(title)
        self.assertIsInstance(title, MovieTitle)
        self.assertEquals(title.name, "The Lego Movie")
        self.assertEquals(title.year, 2014)
        self.assertEquals(title.imdb_id, "tt1490017")

    def test_get_title_by_query_none(self):
        q = "hjsjdhgsdjhg2 23t9tjgs sdgsd"
        title = self.provider.get_title_by_query(q)
        self.assertIsNone(title)

    def test_get_release_name_by_hash(self):
        release_name = self.provider.get_release_name_by_hash(
            "66ea24e3ad41fd47", "8425019199")
        self.assertIsNotNone(release_name)
        self.assertEquals(
            release_name, "the.matrix.1999.720p.hddvd.dts.x264-esir")
        

    def test_get_title_versions_no_results(self):
        self.assertFalse(True)

    def test_get_title_versions_series(self):
        self.assertFalse(True)

    def test_get_title_versions_movie(self):
        self.assertFalse(True)

    def test_download_subtitle_buffer_bad_version(self):
        version = ProviderVersion(
            [],
            MovieTitle("The Matrix Revolution", 2003, "tt0242653"),
            Languages.ENGLISH,
            self.provider,
            attributes = {
                # Incorrect link.
                "ZipDownloadLink" : "http://dl.opensubtitles.org/en/download/subad/src-api/vrf-293106cf48/468615"})

        from api.exceptions import FailedDownloadingSubtitleBuffer
        with self.assertRaises(FailedDownloadingSubtitleBuffer):
            file_name, subtitle_buffer = \
                self.provider.download_subtitle_buffer(version)

    def test_download_subtitle_buffer_good_version(self):
        version = ProviderVersion(
            [],
            MovieTitle("The Matrix Revolution", 2003, "tt0242653"),
            Languages.ENGLISH,
            self.provider,
            attributes = {
                "ZipDownloadLink" : "http://dl.opensubtitles.org/en/download/subad/src-api/vrf-293106cf48/4686151"})

        file_name, subtitle_buffer = \
            self.provider.download_subtitle_buffer(version)
        self.assertEquals(
            file_name, 
            "the.matrix.revolutions.(2003).eng.1cd.(4686151).zip")

        from hashlib import sha1
        download_sha1 = sha1(subtitle_buffer).hexdigest()
        self.assertEquals(
            sha1(subtitle_buffer).hexdigest(),
            "4d48620132c490b392f98edcfc2c39f765a51698")




def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        opensubtitlesprovider, 
        optionflags=doctest.NORMALIZE_WHITESPACE)
    tests.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestOpenSubtitlesProvider))
    test_runner.run(tests)