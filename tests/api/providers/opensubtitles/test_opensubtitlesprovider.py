import sys
sys.path.append("..\\..")
import os
from api.providers.opensubtitles import OpenSubtitlesProvider
from api.languages import Languages
from api.title import MovieTitle
from api.title import SeriesTitle

import unittest

import logging
logging.basicConfig()
logging.getLogger("subit").setLevel(logging.DEBUG)

AVI_FILE_PATH = os.path.join(os.path.dirname(__file__), "breakdance.avi")
AVI_FILE_HASH = "8e245d9679d31e12"

class TestOpenSubtitlesProvider(unittest.TestCase):
    def setUp(self):
        self.provider = OpenSubtitlesProvider([Languages.ENGLISH], None)

    def test_calculate_hash(self):
        h = self.provider.calculate_file_hash(AVI_FILE_PATH)
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
        self.assertEquals(title.name, "Games of Thrones")
        self.assertEquals(title.year, 2014)
        self.assertEquals(title.imdb_id, "tt0944947")
        self.assertEquals(title.episode_imdb_id, "tt2816136")
        self.assertEquals(title.season_number, 4)
        self.assertEquals(title.episode_number, 1)
        self.assertEquals(title.episode_name, "Two Swords")

    def test_get_title_by_query_movie(self):
        q = "enders.game.2013.720p.bluray.x264-sparks"
        title = self.provider.get_title_by_query(q)
        self.assertIsNotNone(title)
        self.assertIsInstance(title, MovieTitle)
        self.assertEquals(title.name, "Enter's Game")
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

def run_tests():
    unittest.TextTestRunner(verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestOpenSubtitlesProvider))