import logging
logger = logging.getLogger("subit.api.providers.torec.provider")

from api.providers.providersnames import ProvidersNames
from api.providers.iprovider import IProvider
from api.languages import Languages


__all__ = ['TorecProvider']


class TorecProvider(IProvider):
    provider_name = ProvidersNames.TOREC
    supported_languages = [
        Languages.HEBREW
    ]

    def __init__(self, languages, requests_manager):
        super(TorecProvider, self).__init__(languages, requests_manager)

    def get_title_versions(self, title, version):
        pass

    def download_subtitle_buffer(self, provider_version):
        pass