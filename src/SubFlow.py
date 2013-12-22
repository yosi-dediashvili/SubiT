import os
from imp import reload as reload_module

import SubProviders
from SubProviders import getSubProvider
from SubProviders import getSubProviderByName
from SubProviders import setNextSubProvider as setNextSubProviderInModule
def setNextSubProvider():
    return_value = setNextSubProviderInModule()
    writeLog(INFO_LOGS.SETTING_PROVIDER % getSubProvider().PROVIDER_NAME)
    return return_value

#import SubChoosers

from SubStages.QuerySubStage import QuerySubStage

from Settings.Config import SubiTConfig

from Logs import INFO as INFO_LOGS
from Logs import WARN as WARN_LOGS
from Logs import DIRECTION as DIRC_LOGS
from Logs import FINISH as FINISH_LOGS
from Logs import BuildLog

import Interaction
Interactor  = Interaction.getInteractor()
writeLog    = Interactor.writeLog

from Utils import GetSubtitleDownloadDirectory
from Utils import GetSubtitleSavingExtension
from Utils import GetMoviesExtensions
from Utils import GetSubtitlesExtensions
from Utils import WriteDebug


class SubFlow(object):
    """ SubFlow is the core of SubiT. That's where all the modules are joined 
        together in order to get the subtitles.
        
        The scope of a SubFlow instance is a single session, where session might
        be a movie file name, a movies directory, or simply a movie name query.

        For directories, the executeFlowOnTheGivenDirectory() is called,
        For filenames and queries, the executeFlowOnTheGivenQuery() is called.
        After the first function call, all the types proceed to the same 
        function, because for the flow, there's no different between each type.

        For example, if we're called for directory, the flow will start from
        executeFlowOnTheGivenDirectory(), and then, for each movie, will go
        to executeFlowOnTheGivenQuery()...
    """
    def _add_sub_stages_to_list(self, sub_stages, stages_list_container):
        """ Add the given SubStages to the given container list """
        # If the original list is greater the then the container list, it means
        # that it doesnt contains it, and therefor, we dont need to check every
        # item in sub_stages against the whole items in stages_list_container
        need_to_check_if_contains = len(stages_list_container) > len(sub_stages)

        for sub_stage in sub_stages:
            if not need_to_check_if_contains or not sub_stage in stages_list_container:
                stages_list_container.append(sub_stage)

    def _get_movie_name_from_opensubtitles_global_sub_provider\
        (self, file_name, full_path):
        """ Get the movie name using hash query features, and also file name 
            query (opensubtitles has a huge amount of subtitles, so there is a 
            big change that we will get the movie name by just quering with the 
            file name). We perform a search without specifing a language in 
            order to get results from all of them.
        """
        movie_name = None
        # We take the global provider of OpenSubtitles in order to search 
        # without a specific language, because we only search in order to get 
        # the name
        os_provider = getSubProviderByName('Global - www.opensubtitles.org')
        if not os_provider:
            WriteDebug('Couldnt get [Global - www.opensubtitles.org] for name query')
            return movie_name

        os_provider()
        
        # We first try to find match by the hash. Notice that we are not 
        # checking to see if the path realy exists, and that's because the 
        # inner function is doing that for us
        try:
            
            writeLog(INFO_LOGS.OS_SENDING_QUERY_USING_THE_FILE_HASH_VALUE)
            movie_name = os_provider.findByHash(full_path, True)
        except:
            WriteDebug('Failed in opensubtitles findByHash check')

        # If we didn't get result, we try with the file name
        if not movie_name:
            try:
                writeLog(WARN_LOGS.OS_CANT_GET_MOVIE_NAME_FOR_HASH_VALUE)
                writeLog(INFO_LOGS.OS_SENDING_QUERY_USING_THE_FILE_NAME)
                movie_name = os_provider.findByFileName(file_name, True)
            except:
                WriteDebug('Failed in opnesubtitles findByFileName check')
            
        # Check in order to log the currect message
        if not movie_name:
            writeLog(WARN_LOGS.OS_CANT_GET_MOVIE_NAME_FOR_FILE_NAME)
        else:
            writeLog(INFO_LOGS.OS_FOUND_MOVIE_NAME)

        return movie_name

    def getMovieSubStagesForQueryFromAllSubProviders(self, query, full_path):
        """ Yields MovieSubStages from all the SubProviders for the given query """
        reload_module(SubProviders)
        while setNextSubProvider():
            yield QuerySubStage(getSubProvider().PROVIDER_NAME,\
                query, full_path).getMovieSubStages()
    
    def executeFlowOnTheGivenQuery\
        (self, movie_dir_name, movie_query, movie_file_path, interactive = False):
        """ Does the work on single file (can also be on single query for movie 
            name). the movie_file_path is the full path (including the file 
            name) to the movie file (can be set to None or empty string). The
            function will Return True if subtitle downloaded, else False.
        """
        # We set the SubStages containers for each work on a query, and not 
        # for each instance of SubFlow, because the flow might start from a 
        # directory and therefor, might contain several queries
        self.MovieSubStagesContainer   = []
        self.VersionSubStagesContainer = []

        # For the same reason, we reload the core modules
        reload_module(SubProviders)
        #reload_module(SubChoosers)

        # Will be set to True only if the subtitle download succeded. In any
        # other case, this value will be False
        is_flow_succeeded   = False
        
        version_sub_stage = None

        def _try_download_version_sub_stage(ver_sub_stage):
            """ Try to download the subtitle of the version_sub_stage. Return 
            True if succeeded, else False."""
            try:
                if not ver_sub_stage:
                    WriteDebug('ver_sub_stage is None, returning False')
                    return False

                WriteDebug('Trying to download the subtitle for: %s' % ver_sub_stage.info())
                download_directory = \
                    GetSubtitleDownloadDirectory(movie_dir_name, interactive)
                return ver_sub_stage.downloadSubtitle\
                    (download_directory, GetSubtitleSavingExtension(movie_query))
            except Exception as eX:
                WriteDebug('Failed getting ver_sub_stage: %s' % eX)
                return False

        def _try_getting_version_sub_stage\
            (query, original_query, movie_file_path):
            """ Will try to get VersionSubStage for the given query while using
                The SubStagesRanker"""
            from SubChoosers.CertainSubStagesChooser import \
                CertainSubStagesChooser as current_chooser

            if not original_query:
                # We are not keeping the movie_query original value if it was
                # not a real file query (because in that case, there's no real
                # meaning to the original string (we don't want to compare with
                # him in that case)
                WriteDebug('the original_query is empty, setting query instead: %s' % query)
                original_query = query
            for movie_sub_stages in \
                self.getMovieSubStagesForQueryFromAllSubProviders\
                (query, movie_file_path):
                # Append the results to the container
                self._add_sub_stages_to_list\
                    (movie_sub_stages, self.MovieSubStagesContainer)
                # We send the original query to the chooser, and not the one
                # that was passed to the function. The reson for that is that
                # if we try to get a choose by passed simply a movie name, we
                # probably will never get a certain choose, and therefor, we
                # need to compare the results against the movie_query parameter
                # which might be a file name, and therefor, give us a better
                # match in the ranking
                WriteDebug('Trying to get certain choose for movie_sub_stage')
                movie_sub_stage = current_chooser\
                    .chooseMovieSubStageFromMoviesSubStages\
                    (movie_sub_stages, original_query)
                if movie_sub_stage:
                    WriteDebug('Certain movie_sub_stage got chosen: %s' % movie_sub_stage.info())
                    version_sub_stages = movie_sub_stage.getVersionSubStages()
                    # Append the results to the container
                    self._add_sub_stages_to_list\
                        (version_sub_stages, self.VersionSubStagesContainer)
                    # Same comment about the movie_query parameter as in the 
                    # MovieSubStage ranking
                    WriteDebug('Trying to get certain choose for version_sub_stage')
                    version_sub_stage = current_chooser\
                        .chooseVersionSubStageFromVersionSubStages\
                        (version_sub_stages, self.MovieSubStagesContainer, 
                         original_query)
                    if _try_download_version_sub_stage(version_sub_stage):
                        WriteDebug('Certain version_sub_stage got chosen and downloaded successfully, finishing flow!')
                        return True
                    else:
                        WriteDebug('Certain version_sub_stage failed, trying others!')
                        # Set the version to None, and proceed to the next provider
                        version_sub_stage = None

        
            # If we got to this line, there are two option. The first option is
            # that we couldnt get exact match for a Version or Movie SubStage, and 
            # in this case, we'll have results in the container. The second option 
            # is that we didnt got any MovieSubStage from the query, and therefor
            # the containers will have no results in them
            WriteDebug('MoviesSubStagesContainer has %s items' % len(self.MovieSubStagesContainer))
            WriteDebug('VersionSubStagesContainer has %s items' % len(self.VersionSubStagesContainer))
            # We will continue only if the config say so
            do_properties_based_rank = SubiTConfig.Singleton().getBoolean\
                ('Providers', 'do_properties_based_rank', False)
            # We start by checking the first option
            if do_properties_based_rank and self.MovieSubStagesContainer:
                from SubChoosers.UncertainSubStagesChooser import\
                    UncertainSubStagesChooser as current_chooser
                WriteDebug('Trying to get uncertain choose for movie_sub_stage')
                movie_sub_stage = current_chooser\
                    .chooseMovieSubStageFromMoviesSubStages\
                    (self.MovieSubStagesContainer, original_query)
                if movie_sub_stage:
                    WriteDebug('Uncertain movie_sub_stage got chosen: %s' % movie_sub_stage.info())
                    self._add_sub_stages_to_list\
                        (movie_sub_stage.getVersionSubStages(), 
                         self.VersionSubStagesContainer)
                    WriteDebug('Trying to get uncertain choose for version_sub_stage')
                    version_sub_stage = current_chooser\
                        .chooseVersionSubStageFromVersionSubStages\
                        (version_sub_stages, self.MovieSubStagesContainer, 
                         original_query)
                    if _try_download_version_sub_stage(version_sub_stage):
                        WriteDebug('Uncertain version_sub_stage got chosen and downloaded successfully, finishing flow!')
                        return True
                    else:
                        WriteDebug('Uncertain version_sub_stage failed, trying others!')
                        version_sub_stage = None
            
            return False

        # Our first attempt is to iterate all the providers, and send each of
        # them the query, and for each result we get, we check if we can get
        # the chooser to pick one of the results, and if so, we proceed with 
        # the choose, and if we got a VersionSubStage, we quit the iteration,
        # and if we didnt get, we proceed to the next SubProvider
        if _try_getting_version_sub_stage\
            (movie_query, movie_query, movie_file_path):
            WriteDebug('Query for [%s] finished successfully, got subtitle file!' % movie_query)
            return True
        # If the first option is False, we will go and ask opensubtitles for
        # the movie name (they might give us result)
        elif not self.MovieSubStagesContainer:
            WriteDebug('Couldnt get results from the original query [%s], trying opensubtitles' % movie_query)
            new_query = \
                self._get_movie_name_from_opensubtitles_global_sub_provider\
                (movie_query, movie_file_path)
            if new_query:
                WriteDebug('Got movie_name [%s] from opensubtitles, trying to get results for that name' % new_query)
                if _try_getting_version_sub_stage\
                    (new_query, movie_query, movie_file_path):
                    WriteDebug('Query for [%s] finished successfully, got subtitle file!' % new_query)
                    return True
            else:
                WriteDebug('Couldnt get new movie_name from openubtitles')

        # If we couldnt get results from both the original query and the
        # opensubtitles provider, and we are in interactive mode, we will ask
        # the user for a query, otherwise, we return False for the function
        if not self.MovieSubStagesContainer and interactive:
            WriteDebug('Couldnt get results from the both the original query and the opensubtitles query, asking the user')
            while not self.MovieSubStagesContainer:
                user_query = Interactor.getSearchInput\
                    (DIRC_LOGS.INSERT_MOVIE_NAME_FOR_QUERY)
                if user_query and _try_getting_version_sub_stage\
                    (user_query, movie_query, movie_file_path):
                    WriteDebug('Query for [%s] finished successfully, got subtitle file!' % user_query)
                    return True
                else:
                    WriteDebug('Couldnt get results for the user_query: %s, asking the user again' % user_query)
        # We got nothing to work on in this situation, so we exit the whole
        # function, and return False
        elif not self.MovieSubStagesContainer and not interactive:
            WriteDebug('Tried every thind i could in non interactive mode, but failed')
            WriteDebug('Finishing the flow with failure!')
            return False

        # If we got this far in failing, and we are not in interactive mode, we
        # check to see if there's any version in the container, and if so, try
        # send them to the Certain ranker that will return the first result
        # after the ranking, and we use it as the version_sub_stage
        if not interactive and self.VersionSubStagesContainer:
            from SubChoosers.FirstInCertainSubStagesChooser import \
                FirstInCertainSubStagesChooser as current_chooser
            WriteDebug('We are not in interactive mode, and we got versions to work on!')
            WriteDebug('Trying to get the first version after certain ranking')
            version_sub_stage = current_chooser\
                .chooseVersionSubStageFromVersionSubStages\
                (self.VersionSubStagesContainer, None, movie_query)
            if _try_download_version_sub_stage(version_sub_stage):
                WriteDebug('First version [%s] after certain ranking downloaded successfully!' % version_sub_stage.info())
                return True
            else:
                WriteDebug('Downloading the verison [%s] failed!' % version_sub_stage.info())
        # Our last resort in interactive mode is simply the user. We ask him to
        # the version_sub_stage until we succeed in the download procedure.
        # Notice that the user is allowed to browse the MovieSubStages either
        elif interactive:
            from SubChoosers.InteractiveSubStagesChooser import \
                InteractiveSubStagesChooser as current_chooser
            WriteDebug('We are in interative mode, and we couldnt get version_sub_stage in any other way')
            WriteDebug('Asking the user to choose between all the version_sub_stages')
            while not is_flow_succeeded:
                version_sub_stage = current_chooser\
                    .chooseVersionSubStageFromVersionSubStages\
                    (self.VersionSubStagesContainer, 
                     self.MovieSubStagesContainer, movie_query)
                is_flow_succeeded = _try_download_version_sub_stage\
                    (version_sub_stage)

        return is_flow_succeeded
    
    def executeFlowOnTheGivenDirectory\
        (self, dir_to_process):
        """ Interating whole directory. Works recursivly on all the directory 
            inside. will send request only for directory which contains movie 
            files that are missing a subtitle.
        """
        movies_extensions   = GetMoviesExtensions()
        subs_extensions     = GetSubtitlesExtensions()
        
        writeLog(INFO_LOGS.STARTING_DO_DIR_PROCEDURE % dir_to_process)
        if not os.path.exists(dir_to_process):
            writeLog(WARN_LOGS.ERROR_DIRECTORY_DOESNT_EXISTS % dir_to_process)
            return
        
        for (current_dir, dir_names, file_names) in os.walk(dir_to_process):
            movie_files = filter(lambda fn: os.path.splitext(fn)[1] in \
                                            movies_extensions, file_names)
            sub_files   = filter(lambda fn: os.path.splitext(fn)[1] in \
                                            subs_extensions, file_names)

            movie_files = list(movie_files)
            sub_files = list(sub_files)
            
            # We check for movie files that has coresponding subtitle file by
            # the file name (without the extensions). If there's such, we filter 
            # them out
            subs_in_current_dir = map(lambda sf: os.path.splitext(sf)[0], sub_files)
            subs_in_current_dir = list(subs_in_current_dir)
            movie_files_to_work = filter(lambda mf: os.path.splitext(mf)[0] 
                                         not in subs_in_current_dir, movie_files)
            movie_files_to_work = list(movie_files_to_work)

            # If we got something left to work with
            if len(movie_files_to_work) > 0:
                for movie_file in movie_files_to_work:
                    movie_file_without_ext = os.path.splitext(movie_file)[0]
                    movie_file_full_path   = os.path.join(current_dir, movie_file)
                    # Process the file. We're not calling with interaction set
                    # to True on directory iteration
                    self.executeFlowOnTheGivenQuery\
                        (current_dir, movie_file_without_ext, movie_file_full_path, False)
            # Write to log and go to next dir
            else:
                writeLog(WARN_LOGS.DO_DIR_NO_MISSING_SUBTITLE_FILES % current_dir)
        
        writeLog(FINISH_LOGS.FINISHED_DO_DIR_PROCEDURE)
