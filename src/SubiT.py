import sys
import os
from threading import Thread

from Settings.Updaters import getUpdater
from Settings.Config import SubiTConfig

VERSION = SubiTConfig.Singleton().getStr('Global', 'version')


from Utils import WriteDebug, DEBUG
from Utils import exit, restart, sleep
from Utils import GetDirFileNameAndFullPath
from Utils import GetProgramDir

from Interaction import setDefaultInteractorByConfig
from Interaction import InteractionTypes
from Interaction import getInteractor

from Logs import INFO as INFO_LOGS
from Logs import WARN as WARN_LOGS
from Logs import DIRECTION as DIRC_LOGS
from Logs import FINISH as FINISH_LOGS
from Logs import BuildLog

if DEBUG():
    import traceback

SUBIT_WORKER_THREAD = None

class SubiTWorkerThread(Thread):
    """ The Worker Thread of SubiT, that's where the real flow starts """
    def doUpdateCheck(self):
        """ Will run the whole flow for update, Return None """
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

    def run(self):
        # Wait until the interactor finishes the loading procedure        
        while (not getInteractor() or not getInteractor().IsLoaded()):
            sleep(0.05)
        writeLog = getInteractor().writeLog

        self.doUpdateCheck()

        # Now we are ready for the real work
        from SubFlow import SubFlow
        dir, movie_name, full_path = GetDirFileNameAndFullPath()
        close_on_finish = SubiTConfig.Singleton().getBoolean\
            ('Global', 'close_on_finish', False)

        while True:
            try:
                def _debug_params(_dir, _movie_name, _full_path):
                    """ Nice printing of the running params """
                    WriteDebug('Parameters:')
                    WriteDebug('      dir:        %s' % _dir)
                    WriteDebug('      movie_name: %s' % _movie_name)
                    WriteDebug('      full_path:  %s' % _full_path)

                WriteDebug('Initiating SubFlow')
                writeLog(INFO_LOGS.STARTING)
                subFlow = SubFlow()
                if len(dir) and not len(movie_name):
                    WriteDebug('No movie name was passed, running on dir')
                    _debug_params(dir, movie_name, full_path)
                    subFlow.executeFlowOnTheGivenDirectory(dir)
                else:
                    if not movie_name:
                        WriteDebug('No movie_name was passed, asking for it')
                        movie_name = getInteractor().getSearchInput\
                            (DIRC_LOGS.INSERT_MOVIE_NAME_FOR_QUERY)
                        if os.path.exists(movie_name):
                            WriteDebug('Path does exists!')
                            full_path = movie_name
                            dir = os.path.dirname(full_path)
                            # File name without extension
                            user_input_name = os.path.basename(movie_name)
                            user_input_name = os.path.splitext\
                                (user_input_name)[0]
                            # We change the input to be only the file name
                            movie_name = user_input_name
                    _debug_params(dir, movie_name, full_path)
                    subFlow.executeFlowOnTheGivenQuery\
                        (dir, movie_name, full_path, True)
                
                # Initialize the params for the next run
                dir, movie_name, full_path=('', '', '')
                writeLog( FINISH_LOGS.FINISHED )
            except Exception as ex:
                writeLog(BuildLog(WARN_LOGS._TYPE_, str(ex)))
                dir, movie_name, fullpath=('', '', '')
                if DEBUG():
                    raise Exception((traceback.print_exc()))
            if close_on_finish:
                # write log, wait for 2 secs, and exit loop
                writeLog(FINISH_LOGS.APPLICATION_WILL_NOW_EXIT)
                break
        # Close program in this stage
        exit(2)

def start():
    WriteDebug('Running From: %s' % GetProgramDir())
    
    SUBIT_WORKER_THREAD = SubiTWorkerThread()
    SUBIT_WORKER_THREAD.setDaemon(True)
    SUBIT_WORKER_THREAD.start()
    
    setDefaultInteractorByConfig()
    # In Gui mode, after calling load(), the thread enters the event loop
    getInteractor().load()
    # We wait for the worker thread to finish (otherwise, in console mode we
    # are ending the run in here (beacuse there is no event loop))
    if (getInteractor().InteractionType in \
        [InteractionTypes.Console, InteractionTypes.ConsoleSilent]):
        while SUBIT_WORKER_THREAD.isAlive():
            sleep(0.05)
