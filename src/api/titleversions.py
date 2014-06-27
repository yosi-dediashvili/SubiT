__all__ = ['TitleVersion']


import logging
logger = logging.getLogger("subit.api.titleversions")


class TitleVersions(object):
    def __init__(self, title, versions = []):
        """
        Constructs new instance, the versions will be inserted with the 
        provider_rank's default value.
        """
        self.title = title
        self.versions = {}
        for version in versions:
            self.add_version(version)
        logger.debug("Created TitleVersion instance: %s" % self)

    def add_version(self, provider_version, provider_rank = 1):
        """
        Adds the version to the appropriate list in the versions dictionary, 
        and sorts it afterwards.
        """
        logger.debug(
            "Adding version to the dictionary: (%s, %s)" % 
            (provider_rank, provider_version))

        language = provider_version.language
        if not language in self.versions:
            logger.debug("The language is missing, adding it: %s" % language)
            self.versions[language] = {}

        language_versions = self.versions[language]

        rank_group = provider_version.rank_group
        if not rank_group in language_versions:
            logger.debug(
                "The rank_group is missing, adding it: %d" % rank_group)
            language_versions[rank_group] = []

        rank_group_versions = language_versions[rank_group]
        # We're storing a tuple of (provider_rank, provider_version).
        rank_group_versions.append((provider_rank, provider_version))
        # t[0] is the provider_rank.
        rank_group_versions.sort(key=lambda t: t[0])
        logger.debug("The rank_group versions are: %s" % rank_group_versions)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return (
            "<TitleVersions title=%(title)s, "
            "versions=%(versions)s>"
            % self.__dict__)
