import SubHandlers
import Utils
import Logs

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

#===============================================================================
# SubHandler class stores the current ISubHandler instance to work with, Init
# most be called before anything else, within Init of SubFlow Object. After that,
# access to handler is made via the static method "Handler()".
#===============================================================================
class SubHandler:
    _subHandler = None
    
    def __init__(self):
        SubHandler.Handler(SubHandlers.getSelectedHandler())
        
    @staticmethod
    def Handler(iSubHandler = None):
        if SubHandler._subHandler == None == iSubHandler:
            #if we got here, and the handler is null
            raise Exception('No SubHandler Passed!')
        elif iSubHandler != None:
            SubHandler._subHandler = iSubHandler
        return SubHandler._subHandler
    
#===============================================================================
# SubSearch represent the first stage in each subtitle search -> sending the 1st
# query, and parsing the result to the second stage -> List of SubMovies
#===============================================================================
class SubSearch:
    Query = ''
    Path  = ''
    _subMovies = None
    
    def __init__( self, query, path = '' ):
        self.Query = query
        self.Path  = path
        self.Results()

    def Results(self):
        if self._subMovies == None:
            Utils.writelog( INFO_LOGS.SENDING_QUERY_FOR_MOVIES % self.Query )
            self._subMovies = SubHandler.Handler().findmovieslist( self )

            if len(self._subMovies) > 1:
                Utils.writelog( INFO_LOGS.GOT_SEVERAL_RESULTS_FOR_MOVIES )
            elif len(self._subMovies) == 1:
                Utils.writelog( INFO_LOGS.GOT_ONE_RESULT_FOR_MOVIES ) 
            else:
                Utils.writelog( WARN_LOGS.CANT_GET_RESULTS_FOR_MOVIE_NAME )
            
        return self._subMovies
    
    def RankResults(self):
        return SubHandler.Handler().findrelevantmovies( self )
        
#===============================================================================
# SubMovie represent the second stage -> hosting the results from SubSearch for
# each movie returned, and supply access to the next stage, SubVersion
#===============================================================================
class SubMovie:
    MovieName = ''
    MovieCode = ''
    VerSum = ''
    Extra = {}
    _versions = None
    
    def __init__( self, moviecode, moviename, versum, extra = {} ):
        self.MovieName  = moviename.encode(errors='replace') if type(moviename) is unicode else moviename
        self.MovieCode  = moviecode
        self.VerSum     = versum.encode(errors='replace') if type(versum) is unicode else versum
        self.Extra = extra
        
    def Versions(self):
        if self._versions == None:
            Utils.writelog(INFO_LOGS.SENDING_QUERY_FOR_SUB_VERSIONS_FOR_MOVIE % 
						   self.MovieName + ' -> ' + (self.VerSum 
                                                      if len(self.VerSum) < 40 else 
                                                      self.VerSum[0:40].ljust(43, '.')
                                                      ) )			
            Utils.writelog( INFO_LOGS.MOVIE_CODE_FOR_SUBVERSIONS_IS % self.MovieCode )
            self._versions = SubHandler.Handler().findversionslist( self )
            
            if len(self._versions) > 1:
                Utils.writelog( INFO_LOGS.GOT_SEVERAL_RESULTS_FOR_SUB_VERSIONS )
            elif len(self._versions) == 1:
                Utils.writelog( INFO_LOGS.GOT_ONE_RESULT_FOR_SUB_VERSIONS ) 
            else:
                Utils.writelog( WARN_LOGS.CANT_GET_RESULTS_FOR_MOVIE_CODE )
                
        return self._versions
    
    def RankVersions(self, filename):
        return SubHandler.Handler().findrelevantsubversions( filename, self )

#===============================================================================
# SubVersion represent the final stage -> specific version of the selected movie
#===============================================================================
class SubVersion:
    VerSum  = ''
    VerCode = ''
    MovieCode = ''
    Extra = {}
    
    def __init__(self, vercode, versum, moviecode, extra={}):
        self.VerCode    = vercode
        self.VerSum     = versum.encode(errors='replace') if type(versum) is unicode else versum
        self.MovieCode  = moviecode
        self.Extra      = extra
        
    def Download(self, path, filename):
        Utils.writelog( INFO_LOGS.SENDING_SUBTITLE_FILE_REQUEST_FOR_SUBTITLE % 
                        self.VerSum )
        (domain, url) = SubHandler.Handler().getsuburl( self ) 
        Utils.getfile( domain, 
                       url, 
                       path, filename + '.srt' )
