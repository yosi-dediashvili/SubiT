from Interaction import setInteractor
from Interaction import ConsoleSilentInteractor
setInteractor(ConsoleSilentInteractor.ConsoleSilentInteractor())

from Utils import DownloadSubAsBytesIO
from SubStages import QuerySubStage

from TestUtils import WriteTestLog

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

    def __init__(self, provider):
        self.provider = provider
        
    @property
    def provider_name(self):
        return self.provider.PROVIDER_NAME

    def __get_movie_results(self, query):
        query = QuerySubStage.QuerySubStage(
            self.provider_name, query, "")
        return self.provider.findMovieSubStageList(query)

    def __get_version_results(self, movie_result):
        return self.provider.findVersionSubStageList(movie_result)

    def test_findMovieSubStageList(self):
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
        movies = self.__get_movie_results("The Matrix")
        WriteTestLog("Received total of %s movies." % len(movies))
        for movie in movies:
            WriteTestLog(movie.info())
        self.assertTrue(movies, "Failed getting results from the provider.")
        return movies

    def test_findVersionSubStageList(self):
        """
        The function retrive a list of movie sub stages from the test_findMovi-
        eSubStageList() test, and for each movie, it tests whether it returns
        a list of versions using the findVersionSubStageList(). If all the movie
        stages failed to retrieve results, the function is declares failure.

        The function does not return a value.
        """
        movies = self.test_findMovieSubStageList()

        WriteTestLog("Testing provider findVersionSubStageList: %s" % 
                   self.provider_name)

        all_failed = True
        for movie in movies:
            current_failed = not bool(self.__get_version_results(movie))
            all_failed = all_failed and current_failed
            if current_failed:
                WriteTestLog("Failed getting version for movie: %s" % 
                             movie.info())
        self.assertFalse(all_failed, "All movies failed to retrieve versions")
        
    def test_getSubtitleContent(self):
        """
        The function retrieves a list of movies using test_findMovieSubStageLi-
        st() and takes the version of the first movie returned. After that, the
        function takes the first version in the list, and calls the getSubtitl-
        eContent() function of the provider.

        The size of the downloaded subtitle is checked. If it's smaller than 
        1KB, the test will fail.

        Additionally, the function return the file size.
        """
        movies = self.test_findMovieSubStageList()
        versions = self.__get_version_results(movies[0])
        version = versions[0]
        
        WriteTestLog("Testing provider getSubtitleContent: %s" % 
                     self.provider_name)
        file_io = self.provider.getSubtitleContent(version)
        file_content = file_io.getvalue()
        file_size = len(file_content)
        # Check if greater than 1KB.
        self.assertGreater(
            file_size, 
            1024, 
            "Downloaded file is less than 1KB: %s" % file_size)
        return file_size
