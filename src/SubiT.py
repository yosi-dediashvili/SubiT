#!/usr/bin/python
from threading import Thread
import multiprocessing
import sys
import os

import Utils
import TorecFlow
import Gui
import Logs
if os.name == 'nt':
    import Registry

INFO_LOGS = Logs.LOGS.INFO
WARN_LOGS = Logs.LOGS.WARN
DIRC_LOGS = Logs.LOGS.DIRECTION

VERSION = '1.0.0'

def start( guinstance ):
    try:
        (dir, movie_name) = Utils.parseargs()    
        while True:
            tFlow = TorecFlow.TorecFlow(guinstance)
            Utils.writelog( INFO_LOGS.STARTING )                                
            if len(dir) and not len(movie_name):
                tFlow.doDirectory(dir)        
            else:
                movie_name = movie_name if len(movie_name) > 0 else Utils.askuserforname()
                tFlow.doFile(dir, movie_name)            
            dir = movie_name = ''
            Utils.writelog( INFO_LOGS.FINISHED )
    except Exception as ex:
        Utils.writelog('ERROR: %s' % ex)
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        regparams = {   '-register'         : lambda: Registry.register_all(),
                        '-unregister'       : lambda: Registry.unregister_all() }
        if sys.argv[1] in regparams:
            regparams[sys.argv[1]]()
            sys.exit(0)
    #Lock for single instance - Doesnt work :(
    runner = None
    mutex = multiprocessing.Lock()
    mutex.acquire()
    try:
        mgui = Gui.gui()
        runner = Thread(target=start, args=[mgui])
        runner.daemon = True
        mgui.load( runner.start, 2000 )
    finally:
        mutex.release()
        

