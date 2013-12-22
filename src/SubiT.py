#!/usr/bin/python
from threading import Thread
import sys

from Settings import Registry
import Utils
import SubFlow
import Gui
import Logs

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

VERSION = '1.2.0'
DEBUG = Utils.DEBUG = True

if DEBUG:
    import traceback

#===============================================================================
# Starting function of the real flow
#===============================================================================
def start( ):
    while Utils.GuiInstance is None: pass

    #dir, movie_name, fullpath=('', 'drive', '') if DEBUG else Utils.parseargs()
    dir, movie_name, fullpath= Utils.parseargs()
    while True:
        try:
            Utils.WriteDebug('Starting Flow')
            tFlow = SubFlow.SubFlow()
            Utils.writelog( INFO_LOGS.STARTING )                                
            if len(dir) and not len(movie_name):
                tFlow.doDirectory(dir)        
            else:
                movie_name = movie_name if len(movie_name) > 0 else Utils.askuserforname()
                tFlow.doFile(dir, movie_name, True, fullpath)
            
            dir, movie_name, fullpath=('', '', '')
            Utils.writelog( INFO_LOGS.FINISHED )
        except Exception as ex:
            Utils.writelog('WARN__||__ERROR: %s' % ex)
            #dir, movie_name, fullpath=('', '', '')
            if DEBUG:
                raise (traceback.print_exc())
#===============================================================================
#===============================================================================
#===============================================================================

if __name__ == '__main__':
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
    
    #Create Runner thread for execution of start function - start is running from a backgroud thread
    runner = Thread(target=start)
    runner.daemon = True
    runner.start()
    #Load the gui - Gui is in the main thread
    Gui.gui.load()
