""" 
SubiTProxy serves us for performing operation before starting the real program
with the GUI and all the stuff. Currently, we use it for association and 
updates.

The order of execution is as it appears in main(). Keep in mind, that the last
function call should be for handle_rest() which will initiate the real 
program.

Each handler, whether he should or should not perform his job when he gets
called, should be called directly, without any check in the main function. 
We are not performing any check in the main().
"""

import sys
from traceback import print_exc as print_trace_exc

def handle_rest():
    import SubiTArgumentParser
    SubiTArgumentParser.Parse()

def handle_update():
    from Settings.Updaters import getUpdater
    updater = getUpdater()
    if updater and updater.ShouldAutoUpdate():
        (update_is_waiting, update_path) = \
            updater.UpdateFileIsWaitingInDirectory()
        if update_is_waiting:
            updater.ApplyUpdate(update_path)

def main():    
    handle_update()
    handle_rest()


if __name__ == '__main__':
    from Utils import GetProgramDir
    from os import path as os_path
    log_path = os_path.join(GetProgramDir(), 'Settings', 'crash.log')
    try:
        main()
    except Exception as eX:
        print_trace_exc(file=open(log_path, 'w'))
        raise