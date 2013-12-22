from SubHandlers.SubsCenter import ISubsCenterHandler
from SubHandlers.SubsCenter.ISubsCenterHandler import SUBSCENTER_LANGUAGES, SUBSCENTER_PAGES

class SubsCenterHandler(ISubsCenterHandler.ISubsCenterHandler):
	HANDLER_NAME = 'English - www.subscenter.org'
	
	def __init__(self):
		#Set the language
		SUBSCENTER_PAGES.LANGUAGE = SUBSCENTER_LANGUAGES.ENGLISH
		#Call to the ctor of the IOpenSubtitlesHandler
		super(SubsCenterHandler, self).__init__()
