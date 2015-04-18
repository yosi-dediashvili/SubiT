import logging
logger = logging.getLogger("subit.api.providers.ktuvit.provider")
from api.providers.iprovider import IProvider
from api.providers.providersnames import ProvidersNames
from api.languages import Languages


__all__ = ['KtuvitProvider']


class KtuvitProvider(IProvider):
    provider_name = ProviderNames.KTUVIT
    supported_languages = [Languages.HEBREW]

    def __init__(self, languages, requests_manager):
        super(KtuvitProvider, self).__init__(languages, requests_manager)