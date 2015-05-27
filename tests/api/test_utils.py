from api import utils
import doctest

def run_tests():
    doctest.testmod(utils, verbose=False, optionflags=doctest.ELLIPSIS)