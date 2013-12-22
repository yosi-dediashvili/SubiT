from SubHandlers.Sratim import ISratimHandler
from SubHandlers.Sratim.ISratimHandler import SRATIM_PAGES, SRATIM_LANGUAGES

class SratimHandler(ISratimHandler.ISratimHandler):
	HANDLER_NAME = 'Hebrew - www.sratim.co.il'

	def __init__(self):
		#Set the language
		SRATIM_PAGES.LANGUAGE = SRATIM_LANGUAGES.HEBREW
		#Call to the ctor of the IOpenSubtitlesHandler
		super(SratimHandler, self).__init__()