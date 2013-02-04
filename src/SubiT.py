from threading import Thread

from Settings.Updaters import getUpdater
from Settings.Config import SubiTConfig

VERSION = SubiTConfig.Singleton().getStr('Global', 'version')

from Utils import WriteDebug
from Utils import exit, restart, sleep
from Utils import GetProgramDir

from Interaction import InteractionTypes
from Interaction import getInteractor

from Logs import INFO as INFO_LOGS
from Logs import WARN as WARN_LOGS
from Logs import DIRECTION as DIRC_LOGS
from Logs import FINISH as FINISH_LOGS
from Logs import GUI_SPECIAL as GUI_SPECIAL_LOGS
from Logs import BuildLog

from SubInputs import getSingleInputFromQuery
from SubInputs.SingleInputsQueue import SingleInputsQueue

SUBIT_WORKER_THREAD = None

class EXIT_CODES:
    """ The currently exit status codes that SubiT supports. The return code
        is the can be achieved using the OS API for getting the last error of
        a program and so on (LAST_ERROR in windows).
    """

    # All the SingleInputs in the queue got subtitles.
    ALL_QUERIES_GOT_RESULTS = 0
    # None of the SingleInputs in the queue got subtitle.
    ALL_QUERIES_FAILED_GETTING_RESULTS = 2
    # Some of the SingleInputs in the queue got subtitles and some did not.
    NOT_ALL_QUERIES_GOT_RESULTS = 3

class SubiTWorkerThread(Thread):
    """ The Worker Thread of SubiT, that's where the real flow starts """
    def __init__(self, queries, files, directories):
        # Put the SingleInput instances from the parameters into the Queue
        self.single_input_queue = \
            SingleInputsQueue(queries, files, directories)

        self.number_of_success = 0
        self.number_of_failures = 0

        # It's considered interactive only if a single input was passed (i.e.
        # single file or single query. directory is considered to be multipile
        # inputs), or no input passed.
        try:
            self.interactive_by_input = (
                (len(directories) == 0 == len(queries) and len(files) == 1) or
                (len(directories) == 0 == len(files) and len(queries) == 1) or
                (len(directories) == 0 == len(queries) == len(files)))
        except:
            WriteDebug("We failed in deciding the interactive value. True is default.")
            self.interactive_by_input = True

        WriteDebug("interactive_by_input: %s" % self.interactive_by_input)

        # Default constructor
        Thread.__init__(self)

    def doUpdateCheck(self):
        """ Will run the whole flow for update, Return None. """
        updater = getUpdater()
        if updater and updater.ShouldCheckUpdates():
            (_is_latest, _latest_ver, _latest_url) = updater.IsLatestVersion()
            if not _is_latest:
                if updater.ShouldAutoUpdate() and _latest_url:
                    if updater.DownloadUpdate(_latest_url, _latest_ver):
                        WriteDebug('Update zip downloaded, restarting!')
                        restart()
                elif not updater.ShouldAutoUpdate() and _latest_url:
                    getInteractor().notifyNewVersion\
                        (updater.CurrentVersion(), _latest_ver, _latest_url)

    def _get_exit_code(self):
        """ Will calculate and return the exit code for the program. """
        if self.number_of_failures == 0:
            return EXIT_CODES.ALL_QUERIES_GOT_RESULTS
        elif self.number_of_success == 0:
            return EXIT_CODES.ALL_QUERIES_FAILED_GETTING_RESULTS
        else:
            return EXIT_CODES.NOT_ALL_QUERIES_GOT_RESULTS

    def _update_working_stats(self, single_input):
        """ Will update the working states according to the info in the
            SingleInput that is passed to it.
        """

        # Notice that we are not checking for the "finished" variable of the
        # SingleInput. The reason for that is that the variable state only
        # whether we are still working on the SingleInput or not, and not
        # whether we succeeded in getting the subtitle. In order to check for
        # that we need to check the value of the final_version_sub_stage of the
        # SingleInput.
        if single_input.final_version_sub_stage:
            self.number_of_success += 1
        else:
            self.number_of_failures += 1

    def _put_user_single_input_in_queue(self):
        query = getInteractor().getSearchInput\
            (DIRC_LOGS.INSERT_MOVIE_NAME_FOR_QUERY)
        self.interactive = True
        WriteDebug('The query from the user is: %s' % query)
        new_single_input = getSingleInputFromQuery(query)
        WriteDebug('Created SingleInput from the query, adding it to the queue')
        self.single_input_queue.putSingleInput(new_single_input)

    def run(self):
        """ Execute the procedure. """

        # Wait until the interactor finishes the loading procedure        
        while not getInteractor() or not getInteractor().IsLoaded():
            sleep(0.05)

        # We can set the writeLog variable only after the interactor was
        # loaded, because before that, we don't have the right underlying
        # function for the writeLog.
        writeLog = getInteractor().writeLog

        if getInteractor().InteractionType == InteractionTypes.Gui:
            from SubProviders import getSelectedLanguages
            # We need to ask the user to select his languages.
            if not getSelectedLanguages():
                getInteractor().showLanguageSelection()

        # We are checking for update in each program's load.
        self.doUpdateCheck()

        # Now we are ready for the real work.
        from SubFlow import SubFlow
        close_on_finish = SubiTConfig.Singleton().getBoolean\
            ('Global', 'close_on_finish', False)
        interactive_by_interactor = getInteractor().InteractionType in [
            InteractionTypes.Console, InteractionTypes.Gui]

        self.interactive = \
            interactive_by_interactor and self.interactive_by_input

        writeLog(INFO_LOGS.STARTING)

        if self.single_input_queue.empty() and interactive_by_interactor:
            WriteDebug('The queue is empty from the start, adding user query.')
            self._put_user_single_input_in_queue()

        while not self.single_input_queue.empty():
            WriteDebug('Getting next_single_input form the queue.')
            next_single_input = self.single_input_queue.getSingleInput()
            WriteDebug('Got next_single_input: %s' % next_single_input.printableInfo())
            writeLog(INFO_LOGS.STARTING_PROCESSING_OF_SINGLE_INPUT %
                     next_single_input.printableInfo())
            writeLog(GUI_SPECIAL_LOGS.SEARCH_LINE_UPDATE % next_single_input.query)
            try:
                SubFlow(next_single_input).process(self.interactive)
            except Exception as eX:
                WriteDebug('Failed processing the next_single_input: %s' % eX)
                writeLog(BuildLog(WARN_LOGS._TYPE_,
                                  'SingleInput failure: %s' % str(eX)))
            else:
                writeLog(FINISH_LOGS.FINISHED_PROCESSING_SINGLE_INPUT % 
                         next_single_input.printableInfo())
            # Update the stats after processing the SingleInput
            self._update_working_stats(next_single_input)

            if self.single_input_queue.empty() and not close_on_finish:
                WriteDebug('Queue is empty, getting query from the user.')
                self._put_user_single_input_in_queue()

        WriteDebug('Successful downloads: %s' % self.number_of_success)
        WriteDebug('Failed downloads: %s' % self.number_of_failures)
        # Finish up.
        writeLog(FINISH_LOGS.FINISHED)
        writeLog(FINISH_LOGS.APPLICATION_WILL_NOW_EXIT)                
        # Close program in this stage.
        exit(2, self._get_exit_code())

def startWorking(queries = [], files = [], directories = []):
    """ The entry point for the real work of SubiT. The parameters are those 
        that parsed successfully from the command line.
    """
    WriteDebug('Starting SubiT\'s real work.')
    WriteDebug('Running from: %s' % GetProgramDir())
    
    WriteDebug('Creating SUBIT_WORKER_THREAD daemon thread.')
    SUBIT_WORKER_THREAD = SubiTWorkerThread(queries, files, directories)
    SUBIT_WORKER_THREAD.setDaemon(True)
    SUBIT_WORKER_THREAD.start()
    WriteDebug('SUBIT_WORKER_THREAD created and started.')

    # In Gui mode, after calling load(), the thread enters the event loop so
    # we don't need to take to much care about the rest of the code.
    getInteractor().load()

    # In Console modes however, we wait for the worker thread to finish 
    # (otherwise, we are ending the run in here beacuse there is no event loop
    # for the console).
    if (getInteractor().InteractionType in \
        [InteractionTypes.Console, InteractionTypes.ConsoleSilent]):
        while SUBIT_WORKER_THREAD.isAlive():
            sleep(0.05)
