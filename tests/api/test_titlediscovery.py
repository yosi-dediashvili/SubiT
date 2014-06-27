from api import titlediscovery
import doctest

def run_tests():
    doctest.testmod(
        titlediscovery, 
        verbose=False, 
        optionflags=doctest.NORMALIZE_WHITESPACE)