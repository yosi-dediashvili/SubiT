from Interaction import setInteractor
from Interaction import ConsoleSilentInteractor
setInteractor(ConsoleSilentInteractor.ConsoleSilentInteractor())

from Utils import DownloadSubAsBytesIO
from SubStages import QuerySubStage

from TestUtils import WriteTestLog, RandomItemFromList

class BaseSubProviderTest(object):       
    """
    Abstract/Base class for testing the SubProvider. The real SubProvider 
    implementation is not known to this class, and should be set by the 
    deriving class. 

    Notice that the class does not derive from unittest.TestCase. We do so 
    in order to bypass the unittest module logic for locating tests in the 
    project. If we're not deriving from TestCase, then we're not a test class
    for the unittest module. On the other hand, we do implement the TestCase
    interface (By the fact that we implement the test_xxx methods. The result
    behaviour is that when the Real provider's test class will derive from us
    and also from unittest.TestCase it will automatically be treated as a Test-
    Case by the unittest module.

    In order to us this class define the test class as follows:

    class SomeSubProviderTest(unittest.TestCase, BaseSubProviderTest):
        def setUp(self):
            BaseSubProviderTest.__init__(self, SomeSubProvider())
    """

    def __init__(self, 
                 provider, 
                 movie_query = "The Matrix", 
                 series_query = "The Big Bang Theory"):
        """
        Init with an instance of a provider, and an optional queries. One for 
        movies and one for serieses.
        """
        self.provider       = provider
        self.movie_query    = movie_query
        self.series_query   = series_query
        
    @property
    def provider_name(self):
        return self.provider.PROVIDER_NAME

    def __get_movie_results(self, query):
        query_stage = QuerySubStage.QuerySubStage(
            self.provider_name, query, "")
        return self.provider.findMovieSubStageList(query_stage)

    def __get_version_results(self, movie_result):
        return self.provider.findVersionSubStageList(movie_result)

    def findMovieSubStageList(self, query):
        """
        The function will create a QuerySubStage for "The Matrix" and retrieve
        the results from the SubProvider using findMovieSubStageList(). 
        
        The function tests whether the provider retrieve a populated list or
        an empty one.

        Additionally, in order to be used by other test, the function returns 
        the movie sub stages that was returned by the provider.
        """
        WriteTestLog("Testing provider findMovieSubStageList: %s" % 
                     self.provider_name)
        movies = self.__get_movie_results(query)
        WriteTestLog("Received total of %s movies." % len(movies))
        for movie in movies:
            WriteTestLog("Movie info: %s" % movie.info())
        self.assertTrue(movies, "Failed getting results from the provider.")
        return movies

    def findVersionSubStageList(self, query):
        """
        The function retrive a list of movie sub stages from the test_findMovi-
        eSubStageList() test, and for each movie, it tests whether it returns
        a list of versions using the findVersionSubStageList(). If all the movie
        stages failed to retrieve results, the function is declares failure.

        The function does not return a value.
        """
        movies = self.findMovieSubStageList(query)

        WriteTestLog("Testing provider findVersionSubStageList: %s" % 
                   self.provider_name)

        all_failed = True
        for movie in movies:
            versions = self.__get_version_results(movie)
            current_failed = not versions
            all_failed = all_failed and current_failed
            if current_failed:
                WriteTestLog("Failed getting version for movie: %s" % 
                             movie.info())
            else:
                WriteTestLog("Succeeded getting version.")
                for version in versions:
                    WriteTestLog("Version info: %s" % version.info())

        self.assertFalse(all_failed, "All movies failed to retrieve versions")
        
    def getSubtitleContent(self, query):
        """
        The function retrieves a list of movies using test_findMovieSubStageLi-
        st(). Then, it chooses a random movie and random version in that movie. 
        After that, the function calls the getSubtitleContent() function of the 
        provider for that version.

        The size of the downloaded subtitle is checked. If it's smaller than 
        1KB, the test will fail.

        Additionally, the function return the file size.
        """
        movies = self.findMovieSubStageList(query)
        WriteTestLog("Testing provider getSubtitleContent: %s" % 
                         self.provider_name)

        # Pick random movie:
        rand_movie = RandomItemFromList(movies)
        WriteTestLog("Picked random movie: %s" % rand_movie.info())
        versions = self.__get_version_results(rand_movie)
        rand_version = RandomItemFromList(versions)
        WriteTestLog("Picked random version: %s" % rand_version.info())
        
        file_io = self.provider.getSubtitleContent(rand_version)
        file_content = file_io.getvalue()
        file_size = len(file_content)
        # Check if greater than 1KB.
        self.assertGreater(
            file_size, 
            1024, 
            "Downloaded file is less than 1KB: %s" % file_size)
        return file_size

    def test_movie_findMovieSubStageList(self):
        return self.findMovieSubStageList(self.movie_query)

    def test_series_findMovieSubStageList(self):
        return self.findMovieSubStageList(self.series_query)

    def test_movie_findVersionSubStageList(self):
        return self.findVersionSubStageList(self.movie_query)

    def test_series_findVersionSubStageList(self):
        return self.findVersionSubStageList(self.series_query)

    def test_movie_getSubtitleContent(self):
        return self.getSubtitleContent(self.movie_query)
        
    def test_series_getSubtitleContent(self):
        return self.getSubtitleContent(self.series_query)