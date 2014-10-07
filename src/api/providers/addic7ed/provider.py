import logging
logger = logging.getLogger("subit.api.providers.addic7ed.provider")

from api.providers.iprovider import IProvider
from api.providers.providersnames import ProvidersNames
from api.languages import Languages


__all__ = ['Addic7edProvider']


class Addic7edProvider(IProvider):
    provider_name = ProvidersNames.ADDIC7ED
    language_to_addic7ed_code = {
        Languages.HEBREW    : 23,
        Languages.ENGLISH   : 1,
        Languages.SPANISH   : 4,
        Languages.ARABIC    : 38,
        Languages.BULGARIAN : 35,
        Languages.SLOVAK    : 25,
        Languages.TURKISH   : 16,
        Languages.CZECH     : 14,
        Languages.RUSSIAN   : 19,
        Languages.NORWEGIAN : 29,
        Languages.SWEDISH   : 18,
        Languages.FRENCH    : 8
    }
    supported_languages = language_to_addic7ed_code.keys()

    def __init__(self, languages, requests_manager):
        super(Addic7edProvider, self).__init__(languages, requests_manager)