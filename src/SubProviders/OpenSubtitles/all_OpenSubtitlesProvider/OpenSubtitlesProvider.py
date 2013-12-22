from SubProviders.OpenSubtitles import IOpenSubtitlesProvider
from SubProviders.OpenSubtitles.IOpenSubtitlesProvider import OPENSUBTITLES_LANGUAGES, OPENSUBTITLES_PAGES

class OpenSubtitlesProvider(IOpenSubtitlesProvider.IOpenSubtitlesProvider):
    # We keep the Base handler name, in order to get filtered out in the settings
    PROVIDER_NAME = 'Global - www.opensubtitles.org'

    def __init__(self):
        # We set out language to be "all". This providers servs only the SubFlow, we use
        # it for the hash search features, and we don't want to be limited to singly lang
        OPENSUBTITLES_PAGES.LANGUAGE = OPENSUBTITLES_LANGUAGES.GLOBAL
        # Call to the ctor of the IOpenSubtitlesProvider
        super(OpenSubtitlesProvider, self).__init__()