from SubProviders.Addic7ed import IAddic7edProvider
from SubProviders.Addic7ed.IAddic7edProvider import ADDIC7ED_LANGUAGES
from SubProviders.Addic7ed.IAddic7edProvider import ADDIC7ED_PAGES

class Addic7edProvider(IAddic7edProvider.IAddic7edProvider):
    PROVIDER_NAME = 'Slovak - www.addic7ed.com'

    def __init__(self):
        #Set the language
        ADDIC7ED_PAGES.LANGUAGE = ADDIC7ED_LANGUAGES.SLOVAK
        #Call to the ctor of the IAddic7edProvider class
        super(Addic7edProvider, self).__init__()