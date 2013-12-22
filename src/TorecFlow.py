import os

from TorecHandler import TorecHandler
import TorecResult
from HashCodesHamster import Hamster
import Utils
import Logs

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

class TorecFlow:
    def __init__( self, guinstance ):
        TorecHandler( guinstance )
        Hamster()
    #===================================================================
    # Does the work on single file (can also be on single query - movie name)
    # Logis is simple: 
    #   1. query filename/moviename
    #   2. select movie
    #   3. select version
    #   4. download wanted version
    #===================================================================
    def doFile( self, dir, filename, interactive = True ):
        torecSearch     = None
        torecMovie      = None
        torecVersion    = None
        
        Utils.writelog( INFO_LOGS.STARTING_DO_FILE_PROCEDURE )
        
        #=======================================================================
        #================first stage - Query Stage - first stage================
        #=======================================================================
        torecSearch = TorecResult.TorecSearch( filename )
        if not len(torecSearch.Results()):
            if interactive:
                #If interactive and we got no results
                while not len(torecSearch.Results()):
                    torecSearch = TorecResult.TorecSearch( Utils.askuserforname() )
            else:
                #Else - quit/go to next movie(non-interactive)
                return

        #=======================================================================
        #==========second stage - Movie Selection Stage - second stage==========
        #=======================================================================        
        if len(torecSearch.Results()) == 1:
            torecMovie = torecSearch.Results()[0]
        #We got more then one movie
        else:
            if interactive:
                #Logic for interactive selection
                Utils.setmoviechoices( torecSearch.Results(), DIRC_LOGS.CHOOSE_MOVIE_FROM_MOVIES )
                while not torecVersion:
                    (type, result) = Utils.getselection('ANY')
                    if type == 'MOVIE':
                        torecMovie = result
                        Utils.setversionchoices(torecMovie.Versions(), DIRC_LOGS.CHOOSE_VERSION_FROM_VERSIONS)
                    elif type == 'SUB':
                        torecVersion = result
                #=================================
            #We apply self logic - Rank by Version Summary at the search page [TorecMovie.VerSum]
            else:
                torecMovie = torecSearch.RankResults()

        #=======================================================================
        #===========third stage - Sub Selection Stage - third stage=============
        #=======================================================================                
        if torecVersion is None:
            (results, first_is_certain) = torecMovie.RankVersions(filename)        
            if not first_is_certain:
                if interactive:
                    Utils.writelog( INFO_LOGS.NO_EXACT_MATCH_FROM_VERSIONS_RANKING )
                    #ask user for version
                    Utils.setversionchoices(torecMovie.Versions(), DIRC_LOGS.CHOOSE_VERSION_FROM_VERSIONS)
                    torecVersion = Utils.getselection('SUB')[1]
                else:
                    Utils.writelog( INFO_LOGS.NO_EXACT_MATCH_FROM_VERSIONS_RANKING_TAKING_FIRST )
                    #take the first results after ranking
                    torecVersion = results[0]
            else:
                Utils.writelog( INFO_LOGS.GOT_EXACT_MATCH_FROM_VERSIONS_RANKING )
                torecVersion = results[0]

        #=======================================================================
        #===========forth stage - Sub Download Stage - forth stage==============
        #=======================================================================            

        #there is no way that dir is empty in non-interactive mode, therefore - 
        #    there is no need to check for interactive value.
        dir = dir if len(dir) else Utils.askuser( DIRC_LOGS.INSERT_LOCATION_FOR_SUBTITLE_DOWNLOAD % os.getcwd(), True, True )
        torecVersion.Download(dir, filename)

        Utils.writelog( INFO_LOGS.FINISHED_DO_FILE_PROCEDURE )
    
    #===========================================================================
    # Interating whole directory. Works recursivly on all directory. will send 
    #    request only for directory which:
    #        1. contains movie files
    #        2. missing subtitle for movie files
    #===========================================================================
    def doDirectory(self, dir):
        MOVIE_EXT   = [ '.mkv', '.avi', '.wmv', '.mp4' ]
        SUB_EXT     = [ '.srt', '.sub' ]
        
        Utils.writelog( INFO_LOGS.STARTING_DO_DIR_PROCEDURE )
        if not os.path.exists(dir):
            Utils.writelog(WARN_LOGS.ERROR_DIRECTORY_DOESNT_EXISTS % dir)
            return
        
        for (currentdir, dirnames, filenames) in os.walk(dir):
            movie_files = filter(lambda filename: os.path.splitext(filename)[1] in MOVIE_EXT, filenames)
            sub_files   = filter(lambda filename: os.path.splitext(filename)[1] in SUB_EXT, filenames)
            
            #we filter movie file with subtitles (remove ext at both)
            movie_files_to_work = filter( lambda mf: os.path.splitext(mf)[0] not in 
                                                     map(lambda sf: os.path.splitext(sf)[0],sub_files), 
                                          movie_files)

            #If we got something left to work with
            if len(movie_files_to_work) > 0:
                for movie_file_to_work in movie_files_to_work:
                    self.doFile(currentdir, os.path.splitext(movie_file_to_work)[0], False)
            #Write to log and go to next dir
            else:
                Utils.writelog( WARN_LOGS.DO_DIR_NO_MISSING_SUBTITLE_FILES % currentdir )
        
        Utils.writelog( INFO_LOGS.FINISHED_DO_DIR_PROCEDURE )
