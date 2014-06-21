from api import namenormalization
import doctest

def run_tests():
    doctest.testmod(namenormalization, verbose=False)