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

    def add_version(self, provider_version, provider_rank = 1):
        """
        Adds the version to the appropriate list in the versions dictionary, 
        and sorts it afterwards.
        """
        if not provider_version.language in self.versions:
            self.versions[provider_version.language] = {}

        language_versions = self.versions[provider_version.language]

        if not provider_version.rank_group in language_versions:
            language_versions[provider_version.rank_group] = []

        rank_group_versions = language_versions[provider_version.rank_group]
        rank_group_versions.append((provider_rank, provider_version))
        # Sort by the provider_rank.
        rank_group_versions.sort(key=lambda t: t[0])

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "<TitleVersions title={title}, versions={versions}>".format(
            title=self.title, versions=self.versions)
