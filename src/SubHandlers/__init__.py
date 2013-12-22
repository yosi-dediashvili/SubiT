import SubiT
import Utils
from Settings import Config

import inspect
import os
import sys

#===============================================================================

#We need to import all the handlers so that the cx_freeze will know that he needs to include the handlers dependencies also
from SubHandlers import Sratim
from SubHandlers import SubsCenter
from SubHandlers import Torec
from SubHandlers import OpenSubtitles

#===============================================================================

TotalHandlerModules = []
TotalHandlerClasses = []


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



SUBHANDLERS_DIR_LOCATION = os.path.split(os.path.abspath(__file__))[0].replace('\\library.zip', '')
selectedHandler = None


def findISubHandlerImplementation(startModule):
	members = inspect.getmembers(startModule)
	for name, obj in members:
		#1. Check if it's a module and not class, so we can go and call the method again on the inner module
		#2. Check if the given module is under the startModule (SubHandlers) so we wont go and check imported modules from python's infrastracture.
		try:
			if inspect.ismodule(obj) and os.path.split(inspect.getabsfile(startModule))[0] in os.path.split(inspect.getabsfile(obj))[0]:
				findISubHandlerImplementation(obj)
			#If it's a class
			elif inspect.isclass(obj):
				#We check if it's a subclass (derived) of ISubHandler, and also is not equal to ISubHandler
				if issubclass(obj, ISubHandler.ISubHandler) and obj is not ISubHandler.ISubHandler:
					#Filter any handler which servs as a base handler for the other handlers
					if obj not in TotalHandlerClasses and 'Base - ' not in obj.HANDLER_NAME:
						#We Face another handler, and therfore, put it in the list
						TotalHandlerClasses.append(obj)
		except Exception as eX: 
			Utils.WriteDebug( 'Failure => %s' % eX )
			#We do nothing on execption

def getHandlers():
	for handlerModule in TotalHandlerModules:
		findISubHandlerImplementation(handlerModule)
	return TotalHandlerClasses

def getSelectedHandler():
	global selectedHandler
	if selectedHandler is None:
		try:
			selectedHandlerName = Config.SubiTConfig.Singleton().getStr('Handlers', 'selected_handler')
		
			Utils.WriteDebug('Location: %s' % __path__[0])
			Utils.WriteDebug('selectedHandlerName: %s' % selectedHandlerName)
			Utils.WriteDebug('Total handlers: %d' % len(getHandlers()))

			selectedHandler = filter(lambda handlerClass: handlerClass.HANDLER_NAME == selectedHandlerName, getHandlers())[0]
		except:
			Utils.WriteDebug('Failed Reading Handler name from file, taking first')
			setSelectedHandler(getHandlers()[0].HANDLER_NAME)
			selectedHandler = getHandlers()[0]

	return selectedHandler

def setSelectedHandler(selectedHandlerName):
	Config.SubiTConfig.Singleton().setValue('Handlers', 'selected_handler', selectedHandlerName)