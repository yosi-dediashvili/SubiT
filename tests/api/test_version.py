from api import version
import doctest

doctest.testmod(version, verbose=True, optionflags=doctest.NORMALIZE_WHITESPACE)