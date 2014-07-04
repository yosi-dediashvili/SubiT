import sys
sys.path.append("..")
from helpers import MockedProvider
from api.providers import get_provider_instance
from api.providers.providersnames import ProvidersNames
from api.languages import Languages
import unittest

MOCKED_PROVIDER_NAME = \
    ProvidersNames.ProviderName("mocked_full_name", "mocked_short_name")

class HebrewOnlyProvider(MockedProvider):
    supported_languages = [Languages.HEBREW]
    provider_name = MOCKED_PROVIDER_NAME

class TestProvidersFactory(unittest.TestCase):
    def test_unsupported_language(self):
        from api.exceptions import UnsupportedLanguage
        providers = [HebrewOnlyProvider]
        languages = [Languages.ENGLISH]
        self.assertRaises(UnsupportedLanguage, get_provider_instance, 
            (MOCKED_PROVIDER_NAME, languages, lambda t: None, providers))

    def test_invalid_provider_name(self):
        from api.exceptions import InvalidProviderName
        providers = [HebrewOnlyProvider]
        languages = [Languages.HEBREW]
        provider_name = ProviderNames.ProviderName("fake_name", "fake")
        self.assertRaises(InvalidProviderName, get_provider_instance, 
            (provider_name, languages, lambda t: None, providers))

    def test_partial_language(self):
        providers = [HebrewOnlyProvider]
        languages = [Languages.HEBREW, Languages.ENGLISH]
        provider = get_provider_instance(
            MOCKED_PROVIDER_NAME, languages, lambda t: None, providers)
        self.assertEqual(provider.provider_name, MOCKED_PROVIDER_NAME)

def run_tests():
    unittest.TextTestRunner(verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            TestProvidersFactory))