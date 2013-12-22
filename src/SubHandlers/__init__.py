#import ISubHandler
import SubiT

import inspect
import os
import sys

#===============================================================================
import TorecHandler
import heb_OpenSubtitlesHandler
import rus_OpenSubtitlesHandler
import eng_OpenSubtitlesHandler
#===============================================================================

TotalHandlerModules = []
TotalHandlerClasses = []


sys.path.append(__path__[0])
print ('Current Path is: %s' % __path__[0])
for module in os.listdir(__path__[0]):
    fullpathModule = os.path.join(__path__[0], module)
    if os.path.isdir(fullpathModule):
        try:
            TotalHandlerModules.append(__import__(module))
            print( 'Loaded: %s' % module )
        except Exception as eX:
            print( 'Failed Loading: %s => %s' % (module, eX))



SUBHANDLERS_DIR_LOCATION = os.path.split(os.path.abspath(__file__))[0].replace('\\library.zip', '')
SELECTED_HANDLER_CONFIG_FILE_NAME = os.path.join(SUBHANDLERS_DIR_LOCATION, 'sh.cfg')

selectedHandler = None


def findISubHandlerImplementation(startModule):
    members = inspect.getmembers(startModule)
    for name, obj in members:
        #1. Check if it's a module and not class, so we can go and call the method again on the inner module
        #2. Check if the given module is under the startModule (SubHandlers) so we wont go and check imported
        #    modules from python's infrastracture.
        try:
            if inspect.ismodule(obj) and os.path.split(inspect.getabsfile(startModule))[0] in os.path.split(inspect.getabsfile(obj))[0]:
                findISubHandlerImplementation(obj)
            #If it's a class
            elif inspect.isclass(obj):
                #We check if it's a subclass (derived) of ISubHandler, and also is not equal to ISubHandler
                if issubclass(obj, ISubHandler.ISubHandler) and obj is not ISubHandler.ISubHandler:
                     if obj not in TotalHandlerClasses:
                         #We Face another handler, and therfore, put it in the list
                         TotalHandlerClasses.append(obj)
        except Exception as eX: 
            print( 'Failure => %s' % eX )
            #We do nothing on execption

def getHandlers():
    for handlerModule in TotalHandlerModules:
        findISubHandlerImplementation(handlerModule)
    return TotalHandlerClasses

def getSelectedHandler():
    global selectedHandler
    if selectedHandler is None:
        #If there's no file, we set the first handler
        if not os.path.exists(SELECTED_HANDLER_CONFIG_FILE_NAME):
            print('Selected handler file is missing, using first handler in the list')
            setSelectedHandler(getHandlers()[0].HANDLER_NAME)
            
        selectedHandlerName = open(SELECTED_HANDLER_CONFIG_FILE_NAME, 'r').read()
        
        print('Location: %s' % __path__[0])
        print('selectedHandlerName: %s' % selectedHandlerName)
        print('Total handlers: %d' % len(getHandlers()))

        selectedHandler = filter(lambda handlerClass: handlerClass.HANDLER_NAME == selectedHandlerName, getHandlers())[0]
        
    return selectedHandler

def setSelectedHandler(selectedHandlerName):
    open(SELECTED_HANDLER_CONFIG_FILE_NAME, 'w').write(selectedHandlerName)