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

    def iter_versions(self):
        """ 
        Iterates over all the ProviderVersions instances contained within this 
        instance.

        The iteration guarantees that versions under the same title will be
        returned sequentially.

        So, this should work:

        for version in titles_versions.iter_versions():
            print(version.version_string)

        And also, this:

        for title, versions in groupby(
            titles_versions.iter_versions(), key=lambda ver: ver.title):
            print(title.version)
            for version in versions:
                print(version.version_string)

        """
        for title, versions in self.iter_title_versions():
            for version in versions:
                yield version

    def iter_titles(self):
        """
        Iterates over all the Title instances contained within this instance.

        So, this should work:

        for title in titles_versions.iter_titles():
            print(title.imdb_id)

        """
        return self.titles.iterkeys()

    def iter_title_versions(self):
        """
        For each Title contained within it, returns a flat list of all the 
        ProviderVersions instances stored under it.

        So, this should work:

        for title, provider_versions in titles_versions.iter_title_versions():
            print(title.imdb_id)
            for version in provider_versions:
                print(version.version_string)

        """
        for title, values in self:
            all_versions = []
            for groups in values.itervalues():
                for versions in groups.itervalues():
                    for rank, version in versions:
                        all_versions.append(version)
            yield (title, all_versions)

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
