from SubHandlers.OpenSubtitles import IOpenSubtitlesHandler
from SubHandlers.OpenSubtitles.IOpenSubtitlesHandler import OPENSUBTITLES_LANGUAGES, OPENSUBTITLES_PAGES

class OpenSubtitlesHandler(IOpenSubtitlesHandler.IOpenSubtitlesHandler):
	HANDLER_NAME = 'Russian - www.opensubtitles.org'

	def __init__(self):
		#Set the language
		OPENSUBTITLES_PAGES.LANGUAGE = OPENSUBTITLES_LANGUAGES.RUSSIAN
		#Call to the ctor of the IOpenSubtitlesHandler
		super(OpenSubtitlesHandler, self).__init__()
