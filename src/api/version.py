""" 
Implementation of the Version classes. This package is not responsible for 
resolving the Version from arbitrary string input and such. It simply the 
implementation of Versions.

Users of this package will implement the methods for extracting the required 
info for the Version.
"""

__all__ = ['Version', 'ProviderVersion', 'UKNOWN_NUM_OF_CDS']

from exceptions import InvalidTitleValue
from exceptions import InvalidNumOfCDs

UKNOWN_NUM_OF_CDS = 0

class Version(object):
    def __init__(self, identifiers, title, num_of_cds = UKNOWN_NUM_OF_CDS):
        """
        A version is instantiated with an identifiers list that can be and 
        empty list, a title that must be valid, and an optional num_of_cds
        value that defaults to unknown, and cannot be lower than 0.

        >>> Version(["720p", "dts", "lol"], None, 1)
        Traceback (most recent call last):
            ...
        InvalidTitleValue: Title instance must be provided.

        >>> from title import MovieTitle
        >>> title = MovieTitle("The Matrix")
        >>> Version(["720p", "dts", "lol"], title, -1)
        Traceback (most recent call last):
            ...
        InvalidNumOfCDs: num_of_cds cannot be lower than 0.

        >>> print Version(["720p", "dts", "lol"], title, 1)
        <Version ...>
        """
        if not title:
            raise InvalidTitleValue("Title instance must be provided.")
        if num_of_cds < 0:
            raise InvalidNumOfCDs("num_of_cds cannot be lower than 0.")

        self.identifiers = identifiers
        self.title = title
        self.num_of_cds = num_of_cds

    def __str__(self):
        return repr(self)

    def __repr__(self):
        """
        >>> from title import MovieTitle
        >>> title = MovieTitle("The Matrix")
        >>> print Version(["720p", "dts", "lol"], title, 0)
        <Version identifiers=['720p', 'dts', 'lol'], num_of_cds=0, \
        title=<MovieTitle ...>>
        >>> print Version([], title, 3)
        <Version identifiers=[], num_of_cds=3, title=<MovieTitle ...>>
        """
        return "<{cls} identifiers={identifiers}, num_of_cds={num_of_cds}, "\
            "title={title}>".format(
                cls='Version',
                identifiers=self.identifiers,
                num_of_cds=self.num_of_cds,
                title=repr(self.title)
            )


class ProviderVersion(Version):
    def __init__(
        self, identifiers, title, provider, attributes = {}, 
        is_certain_match = False, rank = 0, num_of_cds = 0):
        """
        Create a new instance of ProviderVersion. The rules includes all the
        Version's rules, and also, a provider instance must be supplied. The 
        rank value should be between 0 to 100. 

        >>> from title import MovieTitle
        >>> title = MovieTitle("The Matrix")
        >>> ProviderVersion([], title, None)
        Traceback (most recent call last):
            ...
        InvalidProviderValue: provider instance must be supplied.

        >>> ProviderVersion([], title, object(), rank=-1)
        Traceback (most recent call last):
            ...
        InvalidRankValue: rank value must be between 0 to 100.

        >>> print ProviderVersion([], title, object(), rank=50)
        <ProviderVersion ...>
        """
        pass