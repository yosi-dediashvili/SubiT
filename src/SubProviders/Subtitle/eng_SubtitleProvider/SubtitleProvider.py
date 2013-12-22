from SubProviders.Subtitle import ISubtitleProvider
from SubProviders.Subtitle.ISubtitleProvider import SUBTITLE_PAGES, SUBTITLE_LANGUAGES

class SubtitleProvider(ISubtitleProvider.ISubtitleProvider):
    PROVIDER_NAME = 'English - www.subtitle.co.il'
    
    def __init__(self):
        #Set the language
        SUBTITLE_PAGES.LANGUAGE = SUBTITLE_LANGUAGES.ENGLISH
        #Call to the ctor of the IOpenSubtitlesProvider
        super(SubtitleProvider, self).__init__()
