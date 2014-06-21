from api import title
import doctest

def run_tests():
    doctest.testmod(
        title, 
        verbose=False, 
        optionflags=doctest.NORMALIZE_WHITESPACE)