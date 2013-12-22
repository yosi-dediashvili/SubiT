#!/usr/bin/python
import sys
import os
#from PySide import QtCore
from threading import Thread

from Settings import Registry
from Settings import Config
import Utils
import SubFlow
import Gui


import Logs

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

VERSION = Config.SubiTConfig.Singleton().getStr('Global', 'version')

DEBUG = False
if DEBUG:
    import traceback

#===============================================================================
# Worker Thread, that's where the real flow starts
#===============================================================================
class SubiTWorkerThread(Thread):
    def run(self):
        from Settings import Update, UpdateGui    
        #Wait for gui and update module to start
        while Utils.GuiInstance is None or UpdateGui.UpdateGui._Singelton is None: pass
    
        #Check if we're running for the first time and os is windows
        if Config.SubiTConfig.Singleton().getBoolean('Global', 'is_first_run') and os.name == 'nt':
            Utils.GuiInstance.getSettings().askForFirstRegistration()
            #After first time, set to False...
            Config.SubiTConfig.Singleton().setValue('Global', 'is_first_run', False)
            Config.SubiTConfig.Singleton().save()
        
        #Will perform the update flow if needed (including restart of the program, which will
        #cause calling to the handleUpdateZipFile function inside the Update class    
        Update.performUpdate()

        dir, movie_name, fullpath= Utils.parseargs()
        while True:
            try:
                Utils.WriteDebug('Initiating SubFlow')
                subFlow = SubFlow.SubFlow()
                Utils.writelog( INFO_LOGS.STARTING )                                
                if len(dir) and not len(movie_name):
                    subFlow.doDirectory(dir)        
                else:
                    movie_name = movie_name if len(movie_name) > 0 else Utils.askuserforname()
                    subFlow.doFile(dir, movie_name, True, fullpath)
            
                dir, movie_name, fullpath=('', '', '')
                Utils.writelog( INFO_LOGS.FINISHED )
            except Exception as ex:
                Utils.writelog('WARN__||__ERROR: %s' % ex)
                #dir, movie_name, fullpath=('', '', '')
                if DEBUG:
                    raise (traceback.print_exc())
            #If close on finish is set
            if Config.SubiTConfig.Singleton().getBoolean('Global', 'close_on_finish'):
                #write log, wait for 2 secs, and exit loop
                Utils.writelog( INFO_LOGS.APPLICATION_WILL_NOW_EXIT )
                break

        #Close program in this stage
        Utils.exit(2)

#===============================================================================
#===============================================================================
#===============================================================================

#We start here
if __name__ == '__main__':
    Utils.WriteDebug('Running From: %s' % Utils.PROGRAM_DIR_PATH)
    #Handle registration request
    if len(sys.argv) > 1:
        #Dict for lambda's
        regparams = {   '-register'     : lambda: Registry.register_all(),
                        '-unregister'   : lambda: Registry.unregister_all() }
        if sys.argv[1] in regparams:
            #execute relevant lambda
            regparams[sys.argv[1]]()
            sys.exit(0)
            #exit...

    #Handle the update zip file, if there's any (we check it inside the function)
    from Settings import Update
    Update.handleUpdateZipFile()
    
    subitWorkerThread = SubiTWorkerThread()
    subitWorkerThread.setDaemon(True)
    subitWorkerThread.start()
        
    #Load the gui - Gui is in the main thread
    Gui.gui.load()