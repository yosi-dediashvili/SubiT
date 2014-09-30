__all__ = ['TitlesVersion']


import logging
logger = logging.getLogger("subit.api.titlesversions")


class TitlesVersions(object):
    def __init__(self, provider_versions = []):
        """
        Constructs new instance, the versions will be inserted with the 
        provider_rank's default value.
        """
        self.titles = {}
        for version in provider_versions:
            self.add_version(version)
        logger.debug("Created TitlesVersions instance: %s" % self)

    def add_version(self, provider_version, provider_rank = 1):
        """
        Adds the version. Locates or create the appropriate title key.
        """
        logger.debug(
            "Adding version to the dictionary: (%s, %s)" % 
            (provider_rank, provider_version))

        title = provider_version.title
        # We need to locate the instance of the title this way, because the
        # dictionary looks for keys using the key's __hash__ value. The Title
        # object does not override the method (too complicated), instead, we
        # keep a single title in the dictionary by extracting the appropriate
        # key manually, and then, accessing it's value.
        stored_title = filter(lambda t: t == title, self.titles.keys())
        if not stored_title:
            logger.debug("The title is missing, adding it: %s" % title)
            self.titles[title] = {}
        else:
            title = stored_title[0]

        title_languages = self.titles[title]
        language = provider_version.language
        if not language in title_languages:
            logger.debug("The language is missing, adding it: %s" % language)
            title_languages[language] = {}

        language_versions = title_languages[language]
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

    def __iter__(self):
        return self.titles.iteritems()

    def __getitem__(self, idx):
        # Return the item itself, i.e., (key, value), and not only the value.
        return self.titles.items()[idx]

    def __len__(self):
        return len(self.titles)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ("<TitlesVersions titles=%(titles)s>" % self.__dict__)
