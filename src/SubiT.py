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

VERSION = '1.1.0'
DEBUG = True

#===============================================================================
# Starting function of the real flow
#===============================================================================
def start( ):
    (dir, movie_name, fullpath) = Utils.parseargs()    
#    dir, movie_name, fullpath=('', 'the matrix', '')
    while True:
        try:
            tFlow = SubFlow.SubFlow()
            Utils.writelog( INFO_LOGS.STARTING )                                
            if len(dir) and not len(movie_name):
                tFlow.doDirectory(dir)        
            else:
                movie_name = movie_name if len(movie_name) > 0 else Utils.askuserforname()
                tFlow.doFile(dir, movie_name, True, fullpath)
            dir = ''
            movie_name = ''
            Utils.writelog( INFO_LOGS.FINISHED )
        except Exception as ex:
            Utils.writelog('WARN__||__ERROR: %s' % ex)
            if DEBUG:
                raise (sys.exc_info()[1], None,sys.exc_info()[2])
#===============================================================================
#===============================================================================
#===============================================================================

if __name__ == '__main__':
    if len(sys.argv) > 1:
        regparams = {   '-register'     : lambda: Registry.register_all(),
                        '-unregister'   : lambda: Registry.unregister_all() }
        if sys.argv[1] in regparams:
            regparams[sys.argv[1]]()
            sys.exit(0)
            
    runner = Thread(target=start)
    runner.daemon = True
    Gui.gui.load(runner.start)
