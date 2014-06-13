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

        >>> Version(["720p", "dts", "lol"], title, 1)
        <Version ...>
		"""
		pass

class ProviderVersion(Version):
	def __init__(
		self, identifiers, title, provider, attributes = {}, 
		is_certain_match = False, rank = 0 num_of_cds = 0):
		pass