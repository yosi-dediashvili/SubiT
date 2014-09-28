from api import languages
import doctest

def run_tests():
    doctest.testmod(
        languages, 
        verbose=False, 
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)