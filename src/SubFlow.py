import os

from SubHandlers.OpenSubtitles import eng_OpenSubtitlesHandler

import SubResult
import Utils
from Settings import Registry
import Logs

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

class SubFlow:
    def __init__( self ):
        SubResult.SubHandler()              #Call to init of class (will load the selected handler)
        SubResult.SubHandler.Handler()()    #Default call to the Handler's Init Function
        #Print Handler name to the log window
        Utils.writelog(INFO_LOGS.SELECTED_SUB_HANDLER_IS % SubResult.SubHandler.Handler().HANDLER_NAME)
    
    #=======================================================================
    #================first stage - Query Stage - first stage================
    #=======================================================================
    def handleSubSearch(self, subSearch, filename, fullpath, interactive):
        #If we can't get results, and we're not already using English@opensubtitles
        if (not len(subSearch.Results()) and (SubResult.SubHandler.Handler().HANDLER_NAME != eng_OpenSubtitlesHandler.Handler().HANDLER_NAME)):
            #Call to the cstor of the handler
            eng_OpenSubtitlesHandler.Handler()()
            os_result = None #result from opensubtitles

            try:
                Utils.writelog(INFO_LOGS.OS_SENDING_QUERY_USING_THE_FILE_HASH_VALUE)
                os_result = eng_OpenSubtitlesHandler.Handler().findByHash(fullpath, True)
                #if there's no result from the hash check
                if not os_result:
                    Utils.writelog(WARN_LOGS.OS_CANT_GET_MOVIE_NAME_FOR_HASH_VALUE)
                    Utils.writelog(INFO_LOGS.OS_SENDING_QUERY_USING_THE_FILE_NAME)
                    os_result = eng_OpenSubtitlesHandler.Handler().findByFileName(filename, True)
                    #if there's no result from the file name check
                    if not os_result:
                        Utils.writelog(WARN_LOGS.OS_CANT_GET_MOVIE_NAME_FOR_FILE_NAME)
                        if interactive:
                            #If interactive and we got no results
                            while not len(subSearch.Results()):
                                #keep asking
                                subSearch = SubResult.SubSearch( Utils.askuserforname() )

                        else:
                            #Else - quit/go to next movie(non-interactive)
                            return None
            #If the handler failed, ask the user
            except:
                if interactive:
                    #If interactive and we got no results
                    while not len(subSearch.Results()):
                        #keep asking
                        subSearch = SubResult.SubSearch( Utils.askuserforname() )
                else:
                    #Else - quit/go to next movie(non-interactive)
                    return None

            if os_result:
                Utils.writelog(INFO_LOGS.OS_FOUND_MOVIE_NAME)
                tempSubSearch = SubResult.SubSearch(os_result)
                if len(tempSubSearch.Results()):
                    #If we got results, overwrite the value in the original subSearch object
                    subSearch = tempSubSearch   #copy the whole object (so the query results will pass to the old object)
            #put the original value (in order to match in the ranking later, and for the final subtitle file name)
            subSearch.Query = filename  #set the original filename
            subSearch.Path  = fullpath  #set thr original fullpath
        return subSearch

    #=======================================================================
    #==========second stage - Movie Selection Stage - second stage==========
    #=======================================================================
    def handleSubMovie(self, subSearch, subMovie, subVersion, interactive):
        if len(subSearch.Results()) == 1:
            subMovie = subSearch.Results()[0]
        #We got more then one movie
        else:
            (result, first_is_certain) = subSearch.RankResults()
            if interactive and not first_is_certain:
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
                subMovie = result
        return (subMovie, subVersion)

    #=======================================================================
    #===========third stage - Sub Selection Stage - third stage=============
    #=======================================================================        
    def handleSubVersion(self, subVersion, subMovie, filename, interactive):
        if len(subMovie.Versions()):
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

        return subVersion           
    #===================================================================
    # Does the work on single file (can also be on single query - movie name)
    # Logis is simple: 
    #   1. query filename/moviename
    #       1.1. if ther'se no movie, do search on eng@opensubtitle using the file hash
    #       1.2. if ther'se no movie, do search on eng@opensubtitle using the file name
    #   2. select movie
    #   3. select version
    #   4. download wanted version
    #===================================================================
    def doFile( self, dir, filename, interactive = True, fullpath = '' ):
        subSearch     = None
        subMovie      = None
        subVersion    = None
        
        Utils.writelog( INFO_LOGS.STARTING_DO_FILE_PROCEDURE % filename )
        
        #First try to find match, just send the values to the selected handler
        subSearch = SubResult.SubSearch( filename, fullpath )
        #Handle the query
        subSearch = self.handleSubSearch(subSearch, filename, fullpath, interactive)
        #If we got results
        if subSearch:
            #Handle the results -> the movies/serieses. we might get the matched subVersion.
            (subMovie, subVersion) = self.handleSubMovie(subSearch, subMovie, subVersion, interactive)
            #If we didn't get the matched subVersion
            if subVersion is None:
                #Handle the results
                subVersion = self.handleSubVersion(subVersion, subMovie, filename, interactive)
            #=======================================================================
            #===========forth stage - Sub Download Stage - forth stage==============
            #=======================================================================
            #If we got subVersion. A case where we might not get results is when the subtitles are not in the selected language.
            #At start, it might look like we have result, because the movie apears in the search results, be when we enter the movie,
            #we'll find out that the results is from different language.
            if subVersion:    
                #there is no way that dir is empty in non-interactive mode, therefore - 
                #there is no need to check for interactive value.
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
        MOVIE_EXT   = Registry.getExtList()
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
                    self.doFile(currentdir, os.path.splitext(movie_file_to_work)[0], False, os.path.join(currentdir, movie_file_to_work))
            #Write to log and go to next dir
            else:
                Utils.writelog( WARN_LOGS.DO_DIR_NO_MISSING_SUBTITLE_FILES % currentdir )
        
        Utils.writelog( INFO_LOGS.FINISHED_DO_DIR_PROCEDURE )
