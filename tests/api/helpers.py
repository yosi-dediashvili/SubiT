from api.providers.iprovider import IProvider

class MockedProvider(IProvider):
    """ A provider that implements all with pass. """
    def __init__(self, languages=None, requests_manager=None):
        pass
    def get_title_versions(self, input):
        pass
    def download_subtitle_buffer(self, provider_version):
        pass
    @property
    def languages_in_use(self):
        pass
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return "<Provider MockedProvider>"