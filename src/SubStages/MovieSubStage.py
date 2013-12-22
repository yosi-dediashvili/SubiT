from SubStages.ISubStage import ISubStage
from SubStages.ISubStage import getSubProviderByName

from Utils import WriteDebug, getlist

from Logs import INFO as INFO_LOGS
from Logs import WARN as WARN_LOGS
from Logs import DIRECTION as DIRC_LOGS
from Logs import BuildLog

from Interaction import getInteractor
writeLog = getInteractor().writeLog

class MovieSubStage(ISubStage):
    """ The stage that comes right after we get results from querying the site.
        In case of querying for a movie, this stage realy stand for a single 
        movie, but in case that we are querying for an episode in a series,
        this stage will represent a single episode, and not the whole series.
        What it means is that if the site under a certain provider provides a
        whole series in a query, the SubPorvider will need to enter the series
        and extract all the episode under it.
    """
    def __init__(self, provider_name, movie_name, movie_code, 
                 versions_sum, extra = {}):
        """ Simple constructor. movie_name is the display name of the results,
            movie_code is the code representing the movie_name in the site,
            versions_sum is a string representing the versions that this movie
            stores under it.
        """
        self.provider_name  = provider_name
        self.movie_name     = movie_name
        self.movie_code     = movie_code
        self.versions_sum   = versions_sum
        # Extra param for anything that might come later in the life of SubiT
        self.extra          = extra
        # Will store the VersionSubStages under our MovieSubStage
        self._version_sub_stages = None

    def getVersionSubStages(self):
        """ Get the VersionSubStages under our MovieSubStage. The return value
            is always a list, event if it's an empty list """
        if self._version_sub_stages is None:
            writeLog(INFO_LOGS.SENDING_QUERY_FOR_SUB_VERSIONS_FOR_MOVIE % 
                     self.info())
            WriteDebug('Getting VersionSubStages under us: %s' % self.info())
            writeLog(INFO_LOGS.MOVIE_CODE_FOR_SUBVERSIONS_IS % self.movie_code)
            # We might not get our SubProvider by just getting the current one,
            # so we need to get it implicitly
            results = getSubProviderByName\
                (self.provider_name).findVersionSubStageList(self)
            # We need to perform casting because the type might be a mapper
            self._version_sub_stages = getlist(results)

            # Log message to notify results stats
            if len(self._version_sub_stages) > 1:
                writeLog(INFO_LOGS.GOT_SEVERAL_RESULTS_FOR_SUB_VERSIONS)
                WriteDebug('Got several VersionSubStage under us')
            elif len(self._version_sub_stages) == 1:
                writeLog(INFO_LOGS.GOT_ONE_RESULT_FOR_SUB_VERSIONS) 
                WriteDebug('Got single VersionSubStage under us')
            else:
                writeLog(WARN_LOGS.CANT_GET_RESULTS_FOR_MOVIE_CODE)
                WriteDebug('Got no VersionSubStage under us')

        return self._version_sub_stages

    def info(self):
        return ('provider_name: [%s], movie_name: [%s], movie_code: [%s], '
                'versions_sum: [%s]' % (self.provider_name, self.movie_name,
                                        self.movie_code, self.versions_sum))

    def __eq__(self, other):
        is_equal = True
        WriteDebug('Checking MovieSubStage equality')

        WriteDebug('Checking provider_name values: %s == %s' % (self.provider_name, other.provider_name))
        is_equal = is_equal and self.provider_name == other.provider_name
        WriteDebug('Checking movie_name values: %s == %s' % (self.movie_name, other.movie_name))
        is_equal = is_equal and self.movie_name == other.movie_name
        WriteDebug('Checking movie_code values: %s == %s' % (self.movie_code, other.movie_code))
        is_equal = is_equal and self.movie_code == other.movie_code
        WriteDebug('Checking versions_sum values: %s == %s' % (self.versions_sum, other.versions_sum))
        is_equal = is_equal and self.versions_sum == other.versions_sum

        WriteDebug('is_equal? [%s]' % is_equal)
        return is_equal

    def __ne__(self, other):
        WriteDebug('Checking MovieSubStage negative equality')
        return not self.__eq__(other)