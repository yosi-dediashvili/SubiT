from api.providers.providersnames import ProvidersNames
from api.providers.iprovider import IProvider
from api.languages import Languages


__all__ = ['OpenSubtitlesProvider']


class OpenSubtitlesProvider(IProvider):
    provider_name = ProvidersNames.OPEN_SUBTITLES
    supported_languages = [Languages.ENGLISH]

    def __init__(self, languages, requests_manager):
        """
        The OpenSubtitles provider does not really uses the requests manager,
        so there is not real reason to store its reference.
        """
        self.langauges = languages
        self._languages_in_use = list(
            set(OpenSubtitlesProvider.supported_languages)
            .intersection(set(languages)))

    def get_title_versions(self, input):
        raise NotImplementedError(
            "OpenSubtitlesProvider.get_title_versions")

    def download_subtitle_buffer(self, provider_version):
        raise NotImplementedError(
            "OpenSubtitlesProvider.download_subtitle_buffer")

    def languages_in_use(self):
        return self._languages_in_use