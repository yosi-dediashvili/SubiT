import TorecHandler
import Utils

import Logs

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

class TorecSearch:
    _query = ''
    _torecMovies = None
    
    def __init__( self, query ):
        self._query = query
        self.Results()

    def Results(self):
        if self._torecMovies == None:
            Utils.writelog( INFO_LOGS.SENDING_QUERY_FOR_MOVIES % self._query )
            self._torecMovies = map(lambda x: TorecMovie(x[0], x[1][0], x[1][1]),
                                    TorecHandler.TorecHandler.getmovieslist( self._query).items())
        return self._torecMovies
    
    def RankResults(self):
        return TorecHandler.TorecHandler.findrelevantmovies(self._query, self.Results())
        

class TorecMovie:
    MovieName = ''
    MovieCode = ''
    VerSum = ''
    _versions = None
    
    def __init__( self, moviecode, moviename, versum ):
        self.MovieName  = moviename
        self.MovieCode  = moviecode
        self.VerSum     = versum
        
    def Versions(self):
        if self._versions == None:
            Utils.writelog(INFO_LOGS.SENDING_QUERY_FOR_SUB_VERSIONS_FOR_MOVIE % 
						   self.MovieName + ' -> ' + (self.VerSum if len(self.VerSum) < 20 else 
															self.VerSum[0:20].ljust(23, '.')) )			
            self._versions = map( lambda x: TorecVersion(x[0], x[1], self.MovieCode),
                             TorecHandler.TorecHandler.getmovieversions( self.MovieCode) )
        return self._versions
    
    def RankVersions(self, filename):
        return TorecHandler.TorecHandler.findrelevantsubversions(filename, self.Versions())
    
class TorecVersion:
    VerSum  = ''
    VerCode = ''
    MovieCode = ''
    
    def __init__(self, vercode, versum, moviecode):
        self.VerCode    = vercode
        self.VerSum     = versum
        self.MovieCode  = moviecode
        
    def Download(self, path, filename):
        Utils.writelog( INFO_LOGS.SENDING_SUBTITLE_FILE_REQUEST_FOR_SUBTITLE % self.VerSum )
        Utils.getfile( TorecHandler.TOREC_PAGES.DOMAIN, 
                       TorecHandler.TorecHandler.getsuburl(self.MovieCode, self.VerCode), 
                       path, filename + '.srt' )