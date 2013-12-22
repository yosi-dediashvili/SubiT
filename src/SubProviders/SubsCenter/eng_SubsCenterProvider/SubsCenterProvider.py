from SubProviders.SubsCenter import ISubsCenterProvider
from SubProviders.SubsCenter.ISubsCenterProvider import SUBSCENTER_LANGUAGES, SUBSCENTER_PAGES

class SubsCenterProvider(ISubsCenterProvider.ISubsCenterProvider):
    PROVIDER_NAME = 'English - www.subscenter.org'
    
    def __init__(self):
        #Set the language
        SUBSCENTER_PAGES.LANGUAGE = SUBSCENTER_LANGUAGES.ENGLISH
        #Call to the ctor of the IOpenSubtitlesProvider
        super(SubsCenterProvider, self).__init__()
