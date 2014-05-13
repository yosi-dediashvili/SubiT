from SubProviders.Subscene import ISubsceneProvider

class SubsceneProvider(ISubsceneProvider.ISubsceneProvider):
    PROVIDER_NAME = 'Bulgarian - www.subscene.com'
    SELECTED_LANGUAGE = ISubsceneProvider.SUBSCENE_LANGUAGES.BULGARIAN

    def __init__(self):
        # Set the language
        super(SubsceneProvider, self).__init__()