import logging
logger = logging.getLogger("subit.api.providers")


__all__ = ['get_titles_versions']

# The list will contain the classes (not instances) of all the providers that
# SubiT knows of.
PROVIDERS = []


def get_provider_instance(
    provider_name, languages, requests_manager_factory = None):
    """
    Factory method for creating Provider instances. provider_name value should 
    be one of the providers names stored in ProvidersNames, otherwise, exception
    will be raised. languages should be a list of one or more Language instances
    from the Languages class.

    If none of the languages specified is supported in the provider specified,
    an UnsupportedLanguage exception will be raised.
    """
    pass