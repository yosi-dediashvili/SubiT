import SubiT
import Utils
from Settings import Config

import inspect
import os
import sys
from Queue import Queue
from itertools import groupby

#===============================================================================

#We need to import all the handlers so that the cx_freeze will know that he needs to include the handlers dependencies also
from SubHandlers import Sratim
from SubHandlers import SubsCenter
from SubHandlers import Torec
from SubHandlers import OpenSubtitles

#===============================================================================

SUBHANDLERS_DIR_LOCATION = os.path.split(os.path.abspath(__file__))[0].replace('\\library.zip', '')

TotalHandlerModules = []    #Will stores the handler's modules, not the handlers itself

LTotalHandlers  = []         #List: Will store all the handlers, all the time
QTotalHandlers  = Queue(100) #Queue: Total amount of 100 handlers
SelectedHandler = None       #Will store the selected Handler


def storeISubHandlerImplementations(startModule):
	"""This functions gets a module as input, and stores all the ISubHandler implementation under it"""
	members = inspect.getmembers(startModule)
	for name, obj in members:
		#1. Check if it's a module and not class, so we can go and call the method again on the inner module
		#2. Check if the given module is under the startModule (SubHandlers) so we wont go and check imported modules from python's infrastracture.
		try:
			if inspect.ismodule(obj) and os.path.split(inspect.getabsfile(startModule))[0] in os.path.split(inspect.getabsfile(obj))[0]:
				storeISubHandlerImplementations(obj)
			#If it's a class
			elif inspect.isclass(obj):
				#We check if it's a subclass (derived) of ISubHandler, and also is not equal to ISubHandler
				if issubclass(obj, ISubHandler.ISubHandler) and obj is not ISubHandler.ISubHandler:
					#Filter any handler which servs as a base handler for the other handlers
					if obj not in LTotalHandlers and 'Base - ' not in obj.HANDLER_NAME:
						#We Face another handler, and therfore, put it in the queue
						LTotalHandlers.append(obj)
		except Exception as eX: 
			Utils.WriteDebug( 'Failure => %s' % eX )
			#We do nothing on execption

def getHandlers():
	"""Function to retrieve all the handlers"""
	return LTotalHandlers

def getSelectedHandler():
	"""Function to retrieve the selected handler (the one set in the configuration)"""
	global SelectedHandler
	if SelectedHandler is None:
		try:
			selectedHandlerName = Config.SubiTConfig.Singleton().getStr('Handlers', 'selected_handler')
		
			Utils.WriteDebug('Location: %s' % __path__[0])
			Utils.WriteDebug('selectedHandlerName: %s' % selectedHandlerName)
			Utils.WriteDebug('Total handlers: %d' % len(getHandlers()))

			#Take the first handler found matching the name in the config
			SelectedHandler = filter(lambda handlerClass: handlerClass.HANDLER_NAME == selectedHandlerName, getHandlers())[0]
		except:
			Utils.WriteDebug('Failed Reading Handler name from file, taking first')
			setSelectedHandler(getHandlers()[0].HANDLER_NAME)
			SelectedHandler = getHandlers()[0]

	return SelectedHandler

def getNextHandler():
	nextHandler = QTotalHandlers.get_nowait()
	Utils.WriteDebug('Giving next handler: %s' % nextHandler.HANDLER_NAME)
	return nextHandler

def setSelectedHandler(selectedHandlerName):
	"""Will set the current handler in the config"""
	Config.SubiTConfig.Singleton().setValue('Handlers', 'selected_handler', selectedHandlerName)


#==========================================================
# First, import all the modules under SubHandlers directory
#==========================================================
sys.path.append(__path__[0])
Utils.WriteDebug ('Current Path is: %s' % __path__[0])
for module in os.listdir(__path__[0]):
	fullpathModule = os.path.join(__path__[0], module)
	if os.path.isdir(fullpathModule):
		try:
			TotalHandlerModules.append(__import__(module))
			Utils.WriteDebug( 'Loaded: %s' % module )
		except Exception as eX:
			Utils.WriteDebug( 'Failed Loading: %s => %s' % (module, eX))

#==========================================================
# Then, for each module, we store all the Handlers under it
#==========================================================
for handlerModule in TotalHandlerModules:
	storeISubHandlerImplementations(handlerModule)

#==========================================================
# Last, insert the handlers to the QTotalHandlers queue.
# The queue is sorted, so calling the getNextHandler method
# will give the next handler following the configured order
#==========================================================
config_advanced_features = Config.SubiTConfig.Singleton().getBoolean('Handlers', 'advanced_features', False)
config_primary_lang     = Config.SubiTConfig.Singleton().getStr('Handlers', 'primary_lang', 'Hebrew')
config_secondary_lang   = Config.SubiTConfig.Singleton().getStr('Handlers', 'secondary_lang', 'English')

#Take the selected handler
SelectedHandler = getSelectedHandler()
#Put selected handler as the first handler in the queue
QTotalHandlers.put_nowait(SelectedHandler)												

#If set to advanced features, load more handlers to the queue
if config_advanced_features:
	#We filter out the selected handler, and any handler not in config_primary_lang and config_secondary_lang
	filtered_handlers  = filter(lambda f: f.HANDLER_NAME != SelectedHandler.HANDLER_NAME and  f.HANDLER_NAME.split(' - ')[0] in [config_primary_lang, config_secondary_lang], LTotalHandlers)
	#Put handlers from primary language		
	for primary_handler in filter(lambda f: f.HANDLER_NAME.split(' - ')[0] == config_primary_lang, filtered_handlers):
		QTotalHandlers.put_nowait(primary_handler)
	#Put handlers from secondary language
	for secondary_handler in filter(lambda f: f.HANDLER_NAME.split(' - ')[0] == config_secondary_lang, filtered_handlers):
		QTotalHandlers.put_nowait(secondary_handler)