from SubStages.ISubStage import ISubStage
from SubStages.ISubStage import getSubProvider

from Utils import WriteDebug, getlist

from Logs import INFO as INFO_LOGS
from Logs import WARN as WARN_LOGS
from Logs import DIRECTION as DIRC_LOGS
from Logs import BuildLog

from Interaction import getInteractor
writeLog = getInteractor().writeLog

class QuerySubStage(ISubStage):
    """ The query stage of the flow. Represent the first interaction with the
        SubProvider, which is simply sending a query to the provider, and 
        recieving the results (if there's any). The Results returned from the 
        query are of instances of MovieSubStage.
    """
    def __init__(self, provider_name, query, full_path, extra = {}):
        """ Simple constructor. query can be either a file name (without the
            extension), or a free text query. full_path is the full path to the 
            file name (if that's what was passed in the query). If that's not the
            case, the param can be empty string or None
        """
        self.provider_name  = provider_name
        self.query          = query
        self.full_path      = full_path
        # Extra param for anything that might come later in the life of SubiT
        self.extra          = extra
        # Will store the result from the actual query
        self._movie_sub_stages = None
        
    def getMovieSubStages(self):
        """ Get the MovieSubStages from the current query. The return value
            is always a list, event if it's an empty list"""
        if self._movie_sub_stages is None:
            writeLog(INFO_LOGS.SENDING_QUERY_FOR_MOVIES % self.info())
            WriteDebug('Sending query for movie: %s' % self.info())
            # Get results for the SubSearch
            results = getSubProvider().findMovieSubStageList(self)
            # We need to perform casting because the type might be a mapper
            self._movie_sub_stages = getlist(results)

            # Log message to notify results stats
            if len(self._movie_sub_stages) > 1:
                writeLog(INFO_LOGS.GOT_SEVERAL_RESULTS_FOR_MOVIES)
                WriteDebug('Got several MovieSubStages from the query')
            elif len(self._movie_sub_stages) == 1:
                writeLog(INFO_LOGS.GOT_ONE_RESULT_FOR_MOVIES) 
                WriteDebug('Got single MovieSubStage from the query')
            else:
                writeLog(WARN_LOGS.CANT_GET_RESULTS_FOR_MOVIE_NAME)
                WriteDebug('Got no results from the query')

        return self._movie_sub_stages

    def info(self):
        return ('provider_name: [%s], query: [%s], full_path: [%s]' %
                (self.provider_name, self.query, self.full_path))

    def __eq__(self, other):
        is_equal = True
        WriteDebug('Checking QuerySubStage equality')

        WriteDebug('Checking provider_name values: %s == %s' % (self.provider_name, other.provider_name))
        is_equal = is_equal and self.provider_name == other.provider_name
        WriteDebug('Checking query values: %s == %s' % (self.query, other.query))
        is_equal = is_equal and self.query == other.query
        WriteDebug('Checking full_path values: %s == %s' % (self.full_path, other.full_path))
        is_equal = is_equal and self.full_path == otehr.full_path

        WriteDebug('is_equal? [%s]' % is_equal)
        return is_equal

    def __ne__(self, other):
        WriteDebug('Checking QuerySubStage negative equality')
        return not self.__eq__(other)