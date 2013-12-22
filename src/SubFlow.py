import os

import SubResult
import Utils
import Logs

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

class SubFlow:
    def __init__( self ):
        SubResult.SubHandler()
        SubResult.SubHandler.Handler()()    #Default call to the Handler's Init Function
        Utils.writelog(INFO_LOGS.SELECTED_SUB_HANDLER_IS % SubResult.SubHandler.Handler().HANDLER_NAME)
    #===================================================================
    # Does the work on single file (can also be on single query - movie name)
    # Logis is simple: 
    #   1. query filename/moviename
    #   2. select movie
    #   3. select version
    #   4. download wanted version
    #===================================================================
    def doFile( self, dir, filename, interactive = True, fullpath = '' ):
        subSearch     = None
        subMovie      = None
        subVersion    = None
        
        Utils.writelog( INFO_LOGS.STARTING_DO_FILE_PROCEDURE % filename )
        
        #=======================================================================
        #================first stage - Query Stage - first stage================
        #=======================================================================
        subSearch = SubResult.SubSearch( filename, fullpath )
        if not len(subSearch.Results()):
            if interactive:
                #If interactive and we got no results
                while not len(subSearch.Results()):
                    subSearch = SubResult.SubSearch( Utils.askuserforname() )
            else:
                #Else - quit/go to next movie(non-interactive)
                return

        #=======================================================================
        #==========second stage - Movie Selection Stage - second stage==========
        #=======================================================================        
        if len(subSearch.Results()) == 1:
            subMovie = subSearch.Results()[0]
        #We got more then one movie
        else:
            if interactive:
                #Logic for interactive selection
                Utils.setmoviechoices( subSearch.Results(), DIRC_LOGS.CHOOSE_MOVIE_FROM_MOVIES )
                while not subVersion:
                    (type, result) = Utils.getselection('ANY')
                    if type == 'MOVIE':
                        subMovie = result
                        Utils.setversionchoices(subMovie.Versions(), DIRC_LOGS.CHOOSE_VERSION_FROM_VERSIONS)
                    elif type == 'SUB':
                        subVersion = result
                #=================================
            #We apply self logic - Rank by Version Summary at the search page [TorecMovie.VerSum]
            else:
                subMovie = subSearch.RankResults()

        #=======================================================================
        #===========third stage - Sub Selection Stage - third stage=============
        #=======================================================================                
        if subVersion is None:
            (results, first_is_certain) = subMovie.RankVersions(filename)        
            if not first_is_certain:
                if interactive:
                    Utils.writelog( INFO_LOGS.NO_EXACT_MATCH_FROM_VERSIONS_RANKING )
                    #ask user for version
                    Utils.setversionchoices(subMovie.Versions(), DIRC_LOGS.CHOOSE_VERSION_FROM_VERSIONS)
                    subVersion = Utils.getselection('SUB')[1]
                else:
                    Utils.writelog( INFO_LOGS.NO_EXACT_MATCH_FROM_VERSIONS_RANKING_TAKING_FIRST % results[0].VerSum )
                    #take the first results after ranking
                    subVersion = results[0]
            else:
                Utils.writelog( INFO_LOGS.GOT_EXACT_MATCH_FROM_VERSIONS_RANKING % results[0].VerSum)
                subVersion = results[0]

        #=======================================================================
        #===========forth stage - Sub Download Stage - forth stage==============
        #=======================================================================            

        #there is no way that dir is empty in non-interactive mode, therefore - 
        #    there is no need to check for interactive value.
        dir = dir if len(dir) else Utils.askuser( DIRC_LOGS.INSERT_LOCATION_FOR_SUBTITLE_DOWNLOAD % os.getcwd(), True, True )
        subVersion.Download(dir, filename)

        Utils.writelog( INFO_LOGS.FINISHED_DO_FILE_PROCEDURE )
    
    #===========================================================================
    # Interating whole directory. Works recursivly on all directory. will send 
    #    request only for directory which:
    #        1. contains movie files
    #        2. missing subtitle for movie files
    #===========================================================================
    def doDirectory(self, dir):
        MOVIE_EXT   = Utils.MOVIE_EXT
        SUB_EXT     = Utils.SUB_EXT
        
        Utils.writelog( INFO_LOGS.STARTING_DO_DIR_PROCEDURE % dir )
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
