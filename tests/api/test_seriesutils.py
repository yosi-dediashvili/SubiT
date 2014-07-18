from api import seriesutils
import doctest

def run_tests():
    doctest.testmod(seriesutils, verbose=False)