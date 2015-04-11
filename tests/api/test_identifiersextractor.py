from api import identifiersextractor
from api.title import MovieTitle
import doctest
import unittest

from api.providers.iprovider import IProvider

class MockedOpenSubtitlesProvider(IProvider):
    """ A provider that receives predefined value in order for it to return 
    them later, as if they were fetched from the server. """
    def __init__(self, hash_value, release_name):
        self._hash_value = hash_value
        self._release_name = release_name

    def calculate_file_hash(self, file_path):
        return (self._hash_value, 0)

    def get_release_name_by_hash(self, file_hash, file_size):
        return self._release_name

    def get_title_versions(self, input):
        pass
    def download_subtitle_buffer(self, provider_version):
        pass
    @property
    def languages_in_use(self):
        pass
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return "<Provider MockedOpenSubtitlesProvider>"

class TestIdentifiersExtractor(unittest.TestCase):
    def setUp(self):
        self._title = MovieTitle("The Matrix", 1999)

    def test_single_file_hash(self):
        identifiersextractor._get_os_provider = \
            lambda: MockedOpenSubtitlesProvider(
                "345878fce3115", "the.matrix.1999.720p.dts")

        identifiers = identifiersextractor.extract_identifiers(
            self._title, ["C:\\The.Matrix.1999.720p.dts\\movie.mkv"])
        self.assertItemsEqual(identifiers, ['720p', 'dts'])

    def test_single_file_hash_no_other_query(self):
        identifiersextractor._get_os_provider = \
            lambda: MockedOpenSubtitlesProvider(
                "345878fce3115", "the.matrix.1999.dvdrip.ac3")

        identifiers = identifiersextractor.extract_identifiers(
            self._title, ["C:\\movie.mkv"])
        self.assertItemsEqual(identifiers, ['ac3', 'dvdrip'])

    def test_multiple_file_hash_cd_in_file_name(self):
        identifiersextractor._get_os_provider = \
            lambda: MockedOpenSubtitlesProvider(
                "345878fce3115", "the.matrix.1999.dvdrip.ac3")

        identifiers = identifiersextractor.extract_identifiers(
            self._title, 
            ["C:\\The.Matrix.1999.dvdrip.ac3\\movie.cd1.mkv",
            "C:\\The.Matrix.1999.dvdrip.ac3\\movie.cd2.mkv"])
        self.assertItemsEqual(identifiers, ['ac3', 'dvdrip'])

    def test_multiple_file_hash_cd_in_directory_name(self):
        identifiersextractor._get_os_provider = \
            lambda: MockedOpenSubtitlesProvider(
                "345878fce3115", "the.matrix.1999.dvdrip.ac3")

        identifiers = identifiersextractor.extract_identifiers(
            self._title, 
            ["C:\\The.Matrix.1999.dvdrip.ac3.cd1\\movie.mkv", 
            "C:\\The.Matrix.1999.dvdrip.ac3.cd2\\movie.mkv"])
        self.assertItemsEqual(identifiers, ['ac3', 'dvdrip'])

def run_tests():
    test_runner = unittest.TextTestRunner(verbosity=0)
    tests = doctest.DocTestSuite(
        identifiersextractor, 
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(
        TestIdentifiersExtractor))
    test_runner.run(tests)