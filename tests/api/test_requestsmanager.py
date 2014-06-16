from api import requestsmanager
import doctest

doctest.testmod(requestsmanager, verbose=False, optionflags=doctest.NORMALIZE_WHITESPACE)