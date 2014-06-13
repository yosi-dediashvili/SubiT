from api import version
import doctest

doctest.testmod(
    version, 
    verbose=False, 
    optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)