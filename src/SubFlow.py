from imp import reload as reload_module

import SubProviders
from SubProviders import getSubProvider
from SubProviders import getLanguageFromProviderName
from SubProviders import getSubProviderByName
from SubProviders import setNextSubProvider as setNextSubProviderInModule

def setNextSubProvider():
    return_value = setNextSubProviderInModule()
    writeLog(INFO_LOGS.SETTING_PROVIDER % getSubProvider().PROVIDER_NAME)
    return return_value

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

from Utils import WriteDebug
from Utils import SplitToFileAndDirectory


class SubFlow(object):
    """ SubFlow is the core of SubiT. That's where all the modules are joined 
        together in order to get the subtitles.
        
        The scope of a SubFlow instance is a single SingleInput instance. i.e.
        SubFlow is not responsible for retrieving movie files from directories
        or figure out whether the given file has a subtitle already downloaded
        or not (That's the job of whoever calling the instance).

        A SubFlow instance get initiated with a SingleInput instance as an 
        input. In order for the SubFlow to start working, The process() method
        of the class should be called.
    """
    def __init__(self, single_input):
        """ single_input is an instance of the SingleInput class. If the value
            of in_depth_search is True, the flow will enter all the SubMovies
            (until an Exact Match is found) in order to find the right subtitle
            for the SingleInput. If the properties_based_rank is True, the flow
            will use ALSO (and not only) the less accurate SubChooser in order
            to find a matching subtitle.
        """
        WriteDebug('Creating a new SubFlow.')

        WriteDebug('single_input: %s' % single_input.printableInfo())
        self._single_input = single_input
        
        self._in_depth_search = SubiTConfig.Singleton().getBoolean\
            ('Flow', 'in_depth_search', False)
        WriteDebug('in_depth_search: %s' % self._in_depth_search)
        
        self._properties_based_rank = SubiTConfig.Singleton().getBoolean\
            ('Flow', 'do_properties_based_rank', True)
        WriteDebug('properties_based_rank: %s' % self._properties_based_rank)

        # Will contain the MovieSubStages that was returned when querying using
        # the original query.
        self._movie_sub_stages_by_query = []
        # The VersionSubStages that returned from the above MovieSubStages.
        self._version_sub_stages_by_query = []

        # Will contain the MovieSubStages that was returned when querying using
        # the name that was returned from querying OpenSubtitles for the name.
        self._movie_sub_stages_by_os = []
        # The VersionSubStages that returned from the above MovieSubStages.
        self._version_sub_stages_by_os = []

        WriteDebug('SubFlow created.')

    def process(self, interactive):
        """ Thats the entry point to the SubFlow after initalizing it. When
            this function get called, the real action of SubiT get started.

            The function returnes no value. The result will be stored at the
            SingleInput instnace that was passed to the SubFlow instance.
        """
        WriteDebug('process() called for the SubFlow.')
        WriteDebug('interactive: %s' % interactive)
        self._process(interactive)

    def _add_sub_stages_to_list(self, sub_stages, stages_list_container):
        """ Add the given SubStages to the given container list """

        # If the original list is greater the then the container list, it means
        # that it doesnt contains it, and therefor, we dont need to check every
        # item in sub_stages against the whole items in stages_list_container
        need_to_check_if_contains = len(stages_list_container) > len(sub_stages)

        if not need_to_check_if_contains:
            try:
                stages_list_container.extend(sub_stages)
            except Exception as eX:
                WriteDebug("Failed to append sub_stage: %s" % eX)
        else:
            for sub_stage in sub_stages:
                if not sub_stage in stages_list_container:
                    try:
                        stages_list_container.append(sub_stage)
                    except Exception as eX:
                        WriteDebug("Failed to append sub_stage: %s" % eX)

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
        os_provider_name = 'Global - www.opensubtitles.org'
        os_provider = getSubProviderByName(os_provider_name)
        if not os_provider:
            WriteDebug('Couldnt get [%s] for name query' % os_provider_name)
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

    def _yield_movie_sub_stage_from_all_providers(self, query, full_path):
        """ Will yield MovieSubStages one provider at a time (like a generator).
            The function will proceed to the next provider if the current one 
            failed to return a result.

            The return value is a two-dim array (each row contains result from
            one provider).
        """
        reload_module(SubProviders)
        while setNextSubProvider():
            _stages = QuerySubStage(getSubProvider().PROVIDER_NAME, 
                                    query, full_path).getMovieSubStages()
            # Yield only if we got something.
            if _stages:
                yield _stages
    
    def _get_movie_sub_stage_from_all_providers(self, query, full_path):
        """ Will return MovieSubStages all together (like a list). 
        
            The return value is a two-dim array with a single row in it, a row
            that contains the results from all the providers.
        """
        reload_module(SubProviders)
        # Two-dim array with single row.
        movie_sub_stages = [[]]
        while setNextSubProvider():
            _stages = QuerySubStage(
                getSubProvider().PROVIDER_NAME,
                query, 
                full_path).getMovieSubStages()
            # We might be getting empty list, so append is performed if it's
            # not empty.
            if _stages:
                movie_sub_stages[0].extend(_stages)

        return movie_sub_stages

    def _download_version_sub_stage\
        (self, ver_sub_stage, download_path):
        """ Will try to download the subtitle of the version_sub_stage. The
            download_path is the full path for the subtitle file to be saved 
            with. If a subtitle downloaded successfully, the function will 
            return True, otherwise, False. 
        """
        try:
            if not ver_sub_stage:
                WriteDebug('ver_sub_stage is None, returning False')
                return False

            WriteDebug('Trying to download the subtitle for: %s' % ver_sub_stage.info())
            succeeded = ver_sub_stage.downloadSubtitle\
                (*SplitToFileAndDirectory(download_path))
            if succeeded:
                WriteDebug('The subtitle was successfully downloaded.')
            else:
                WriteDebug('Downloading of the subtitle was failed.')
            return succeeded
        except Exception as eX:
            WriteDebug('Failed getting ver_sub_stage: %s' % eX)
            return False

    def _handle_version_sub_stage(self, version_sub_stage, interactive = False):
        """ The function is responsible for handling the final result of the
            version_sub_stage. If the function return True, everything is OK, 
            and  we should stop the SubFlow, otherwise, we need to continue.
        """
        succeeded = False
        if version_sub_stage:
            # We will try to download the subtitle at most two times.
            for i in range(2):
                WriteDebug("Trying to download the subtitle.")
                succeeded = self._download_version_sub_stage\
                    (version_sub_stage, 
                     self._single_input.getDownloadPath(interactive))
                if succeeded:
                    WriteDebug("Subtitle downloaded successfully.")
                    self._single_input.final_version_sub_stage = version_sub_stage
                    self._single_input.finished = True
                    # Retrieve the first language in the config.
                    config_main_language = SubiTConfig.Singleton().getList\
                        ('Providers', 'languages_order')[0]
                    # Retrieve the language of the provider that is associated
                    # with the VersionSubStage.
                    version_language = getLanguageFromProviderName\
                        (version_sub_stage.provider_name)

                    self._single_input.used_primary_language = \
                        (config_main_language == version_language)
                    # We don't want to try and download again.
                    break
                else:
                    WriteDebug("Failed downloading the subtitle.")
        return succeeded

    def _get_version_sub_stage\
        (self, movie_sub_stages_supplier, sub_chooser, chooser_query, 
         providers_query, providers_full_path, in_depth, movie_sub_stages_list, 
         version_sub_stages_list):
        """ Will try to get a single VersionSubStage for the called. The 
            function will query the avaliable providers for the given query, 
            and using the SubChooser that passed to it, will try to get a 
            specific SubStage.

            movie_sub_stages_supplier is a function that recieves a query and 
            a full path to a file, and returnes a MovieSubStages.

            sub_chooser is the SubChooser that the function will use in order 
            to get the selected SubStage. chooser_query is the query that will
            be passed to the sub_chooser function as the query. providers_query
            is the query that will be passed to the SubProviders function as
            the query, the providers_full_path is the path that will be passed 
            to the SubProviders. movie and version sub_stages_list are the 
            containers for the results of this function.

            If the function succeeded in getting a VersionSubStage, It will 
            return one. Otherwise, it will return None.
        """
        WriteDebug('_get_version_sub_stage() called.')
        WriteDebug('sub_chooser: %s\r\n' % sub_chooser)
        WriteDebug('chooser_query: %s' % chooser_query)
        WriteDebug('providers_query: %s' % providers_query)
        WriteDebug('providers_full_path: %s' % providers_full_path)
        WriteDebug('movie_sub_stages_list size: %s' % len(movie_sub_stages_list))
        WriteDebug('version_sub_stages_list size: %s' % len(version_sub_stages_list))

        # The result.
        version_sub_stage = None

        # This loop should continue until one of the two happens:
        # 1. We manage to get a VersionSubStage.
        # 2. We finish iterating the SubProviders.
        for movie_sub_stages in movie_sub_stages_supplier\
            (providers_query, providers_full_path):
            WriteDebug('Got %s MovieSubStages.' % len(movie_sub_stages))
            self._add_sub_stages_to_list\
                (movie_sub_stages, movie_sub_stages_list)
            WriteDebug('The MovieSubStages added to the list.')
            movie_sub_stage = \
                sub_chooser.chooseMovieSubStageFromMoviesSubStages\
                (movie_sub_stages, chooser_query)

            # Skip that provider, get results from the next provider.
            if not movie_sub_stage:
                WriteDebug('Failed getting MovieSubStage using the chooser.')
                continue

            WriteDebug('MovieSubStage got chosen: %s' % movie_sub_stage.info())
            version_sub_stages = movie_sub_stage.getVersionSubStages()
            self._add_sub_stages_to_list\
                (version_sub_stages, version_sub_stages_list)
            version_sub_stage = \
                sub_chooser.chooseVersionSubStageFromVersionSubStages\
                (version_sub_stages, movie_sub_stages, chooser_query)

            if not version_sub_stage:
                WriteDebug('Failed getting VersionSubStage using the chooser.')
                # Proceed to the next provider if there's any.
                continue
            else:
                WriteDebug('VersionSubStage got chosen.')
                # Break the loop, we got what we wanted.
                break

        if not version_sub_stage and in_depth:
            WriteDebug('Performing in_depth iteration on the MovieSubStages.')
            # Notice that we iterate on all the SubProviders even if there is
            # a chance that we did it in the loop above. We do so because the
            # providers stores the results inside them once they retrieved them
            # and therefor another call to getVersionSubStages() for example, 
            # will not cause another page request from the site.

            # The movie_sub_stages_list contains all the the results from all
            # the SubProviders that are set for this instance of SubiT, we can
            # be sure of that because we check for the value of 
            # version_sub_stage, and if the value is None, it necessarily means
            # that we made a full iteration over the avaliable SubProviders
            for movie_sub_stage in movie_sub_stages_list:
                # The function will insert only the stages that are not already
                # stored in the list.
                WriteDebug('Starting InDepth on: %s' % movie_sub_stage.info())
                version_sub_stages = movie_sub_stage.getVersionSubStages()
                self._add_sub_stages_to_list\
                    (movie_sub_stage.getVersionSubStages(), 
                     version_sub_stages_list)
                version_sub_stage = \
                    sub_chooser.chooseVersionSubStageFromVersionSubStages\
                    (version_sub_stages, movie_sub_stages_list, chooser_query)
                if version_sub_stage:
                    WriteDebug('in_depth got us result, breaking.')
                    break

        if not version_sub_stage:
            WriteDebug('Failed getting any MovieSubStage from the query.')
        else:
            WriteDebug('We got a VersionSubStage: %s' % version_sub_stage.info())

        return version_sub_stage

    def _process(self, interactive):
        WriteDebug('_process called, interactive: %s' % interactive)
        version_sub_stage = None

        # First try, Certain chooser, original query
        WriteDebug('Entering first try, using certain chooser, and original query.')
        from SubChoosers.CertainSubStagesChooser import CertainSubStagesChooser
        version_sub_stage = self._get_version_sub_stage\
            (self._yield_movie_sub_stage_from_all_providers,
             CertainSubStagesChooser,
             self._single_input.query,
             self._single_input.query,
             self._single_input.full_path,
             False,
             self._movie_sub_stages_by_query,
             self._version_sub_stages_by_query)

        if self._handle_version_sub_stage(version_sub_stage, interactive):
            WriteDebug('First try succeeded.')
            return
        else:
            WriteDebug('First try failed.')

        # Second try, Certain chooser, OpenSubtitles query
        WriteDebug('Entering second try, using certain chooser, and opensubtitles query.')
        os_query = self._get_movie_name_from_opensubtitles_global_sub_provider\
            (self._single_input.query, self._single_input.full_path)
        if os_query:
            WriteDebug('OpenSubtitles succeeded, query: %s' % os_query)
            version_sub_stage = self._get_version_sub_stage\
                (self._yield_movie_sub_stage_from_all_providers,
                 CertainSubStagesChooser,
                 self._single_input.query,
                 os_query,
                 self._single_input.full_path,
                 False,
                 self._movie_sub_stages_by_os,
                 self._version_sub_stages_by_os)
        else:
            WriteDebug('OpenSubtitles did not succeeded.')

        if self._handle_version_sub_stage(version_sub_stage, interactive):
            WriteDebug('Second try succeeded.')
            return
        else:
            WriteDebug('Second try failed.')

        # Third try (if there is no results at all)
        WriteDebug('Entering third try, interactive chooser and user query')
        if (not self._movie_sub_stages_by_os and
            not self._movie_sub_stages_by_query):
            WriteDebug('Got no movie sub stages, continuing.')
            if interactive:
                WriteDebug('We are in interactive mode, proceeding.')
                from SubChoosers.InteractiveSubStagesChooser \
                    import InteractiveSubStagesChooser
                while not version_sub_stage:
                    user_query = Interactor.getSearchInput\
                        (DIRC_LOGS.INSERT_MOVIE_NAME_FOR_QUERY)
                    WriteDebug('user_query: %s' % user_query)
                    version_sub_stage = self._get_version_sub_stage\
                        (self._get_movie_sub_stage_from_all_providers,
                         InteractiveSubStagesChooser,
                         user_query,
                         user_query,
                         self._single_input.full_path,
                         False,
                         self._movie_sub_stages_by_query,
                         self._version_sub_stages_by_query)
            else:
                # That's the end for us.
                WriteDebug("Got no result from querying, and not interactive.")
                return

        if self._handle_version_sub_stage(version_sub_stage, interactive):
            WriteDebug('Third try succeeded.')
            return
        else:
            WriteDebug('Third try failed.')


        if self._in_depth_search:
            WriteDebug('Entering InDepth scope.')
            # We split the in_depth search into two parts because the operations
            # is intensive in a manner of time consumption (getting the version
            # of each result returned by now...). Therefore, we start with the
            # result that we got using the original query, and if we can't get
            # result, we proceed to the results from OpenSubtitles.

            # Forth try, Certain chooser, InDepth set to True, query from
            # SingleInput.
            WriteDebug('Entering forth try.')
            from SubChoosers.CertainSubStagesChooser import \
                CertainSubStagesChooser
            version_sub_stage = self._get_version_sub_stage\
                (self._yield_movie_sub_stage_from_all_providers,
                 CertainSubStagesChooser,
                 self._single_input.query,
                 self._single_input.query,
                 self._single_input.full_path,
                 True,
                 self._movie_sub_stages_by_query, 
                 self._version_sub_stages_by_query)

            if self._handle_version_sub_stage(version_sub_stage, interactive):
                WriteDebug('Forth try succeeded.')
                return
            else:
                WriteDebug('Forth try failed.')


            # Fifth try, Certain chooser, InDepth set to True, query from
            # OpenSubtitles
            WriteDebug('Entering fifth try.')
            from SubChoosers.CertainSubStagesChooser import \
                CertainSubStagesChooser

            if os_query:
                WriteDebug('os_query is available, proceeding.')
                version_sub_stage = self._get_version_sub_stage\
                    (self._yield_movie_sub_stage_from_all_providers,
                     CertainSubStagesChooser,
                     self._single_input.query,
                     os_query,
                     self._single_input.full_path,
                     True,
                     self._movie_sub_stages_by_os, 
                     self._version_sub_stages_by_os)
            else:
                WriteDebug('os_query is empty.')

        if self._handle_version_sub_stage(version_sub_stage, interactive):
            WriteDebug('Fifth try succeeded.')
            return
        else:
            WriteDebug('Fifth try failed.')
        
        if self._properties_based_rank:
            WriteDebug('Entering PropertiesBased rank scope.')
            # Sixth try, UnCertain chooser, query from SingleInput
            WriteDebug('Entering sixth try.')
            from SubChoosers.UncertainSubStagesChooser import \
                UncertainSubStagesChooser
            # We set the InDepth to be as the SubFlow's isntance says.
            version_sub_stage = self._get_version_sub_stage\
                (self._yield_movie_sub_stage_from_all_providers,
                 UncertainSubStagesChooser,
                 self._single_input.query,
                 self._single_input.query,
                 self._single_input.full_path,
                 self._in_depth_search,
                 self._movie_sub_stages_by_query,
                 self._version_sub_stages_by_query)

            if self._handle_version_sub_stage(version_sub_stage, interactive):
                WriteDebug('Sixth try succeeded.')
                return
            else:
                WriteDebug('Sixth try failed.')

            # We set the InDepth to be as the SubFlow's isntance says.
            WriteDebug('Entering seventh try.')
            version_sub_stage = self._get_version_sub_stage\
                (self._yield_movie_sub_stage_from_all_providers,
                 UncertainSubStagesChooser,
                 self._single_input.query,
                 os_query,
                 self._single_input.full_path,
                 self._in_depth_search,
                 self._movie_sub_stages_by_os,
                 self._version_sub_stages_by_os)


        if self._handle_version_sub_stage(version_sub_stage, interactive):
            WriteDebug('Seventh try succeeded.')
            return
        else:
            WriteDebug('Seventh try failed.')

        # Eighth try, Interactive chooser, query from SingleInput + OpenSubtitles
        WriteDebug('Entering eighth try.')
        if interactive:
            WriteDebug('Interactive mode is on, continuing.')
            from SubChoosers.InteractiveSubStagesChooser import \
                InteractiveSubStagesChooser
            version_sub_stage = self._get_version_sub_stage\
                (self._get_movie_sub_stage_from_all_providers,
                 InteractiveSubStagesChooser,
                 self._single_input.query,
                 self._single_input.query,
                 self._single_input.full_path,
                 self._in_depth_search, 
                 self._movie_sub_stages_by_query + self._movie_sub_stages_by_os,
                 self._version_sub_stages_by_os + self._version_sub_stages_by_query)
        else:
            WriteDebug('Interactive mode is off, skipping.')

        if self._handle_version_sub_stage(version_sub_stage, interactive):
            WriteDebug('Eighth try succeeded.')
        else:
            WriteDebug('Eighth try failed.')