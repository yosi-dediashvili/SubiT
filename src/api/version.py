""" 
Implementation of the Version classes. This package is not responsible for 
resolving the Version from arbitrary string input and such. It simply the 
implementation of Versions.

Users of this package will implement the methods for extracting the required 
info for the Version.
"""

__all__ = ['Version', 'ProviderVersion']

class Version(object):
	def __init__(self, identifiers, title, num_of_cds = 0):
		pass

class ProviderVersion(Version):
	def __init__(
		self, identifiers, title, provider, attributes = {}, 
		is_certain_match = False, rank = 0 num_of_cds = 0):
		pass