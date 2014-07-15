from api import identifiersextractor
import doctest

def run_tests():
    doctest.testmod(identifiersextractor, verbose=False)