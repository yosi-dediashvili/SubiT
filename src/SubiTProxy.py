""" 
SubiTProxy serves us for performing operation before starting the real program
with the GUI and all the stuff. Currently, we use it for association and updates.

The order of execution is as it apears in main(). Keep in mind, that the last
function call should be for handle_regular() which will initiate the real program.

Each handler should wether or not he should perform his job when he gets called.
We're not handling it in the main().
"""
import sys
import traceback

def handle_regular():
    from Utils import ShouldLaunchInConsoleMode, LaunchInConsole
    if not ShouldLaunchInConsoleMode():
        import SubiT
        SubiT.start()
    else:
        LaunchInConsole()

def handle_update():
    from Settings.Updaters import getUpdater
    updater = getUpdater()
    if updater and updater.ShouldAutoUpdate():
        (update_is_waiting, update_path) = \
            updater.UpdateFileIsWaitingInDirectory()
        if update_is_waiting:
            updater.ApplyUpdate(update_path)

def handle_association():
    from Settings.Associators import getAssociator
    associator = getAssociator()
    if len(sys.argv) > 1 and associator:
        association_params = \
            {associator.ASSOCIATE_COMMAND   : lambda: associator.SetAssociation(),
             associator.UNASSOCIATE_COMMAND : lambda: associator.RemoveAssociation()}
        #If parameter is for association, and we have an associator
        if sys.argv[1] in association_params and associator:
            #execute relevant lambda
            association_params[sys.argv[1]]()
            sys.exit(0)

def main():    
    handle_association()
    handle_update()
    handle_regular()


if __name__ == '__main__':
    from Utils import GetProgramDir, CurrentTimePrintable
    import os
    log_path = os.path.join(GetProgramDir(), 'Settings', 'crash.log')
    try:
        main()
    except Exception as eX:
        traceback.print_exc(file=open(log_path, 'w'))
        raise