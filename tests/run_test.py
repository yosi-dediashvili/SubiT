import sys
from os.path import *
from os import getcwd, chdir
import argparse

sys.path.append(join(abspath(dirname(__file__)), r"..\src"))

parser = argparse.ArgumentParser(
    description="Executes one or more test files.")
parser.add_argument(
    "test_paths", metavar='FILE', type=str, nargs="+", 
    help="Full or Relative (to the current directory) path to the test file")
args = parser.parse_args()


def run_test(test_path):
    print "Running test file: %s" % test_path
    global_wd = getcwd()
    dir_name = dirname(test_path)
    sys.path.append(dir_name)
    chdir(dir_name)
    execfile(test_path)
    sys.path.remove(dir_name)
    chdir(global_wd)

for test_path in args.test_paths:
    if not isabs(test_path):
        test_path = abspath(join(getcwd(), test_path))
    if not exists(test_path):
        raise ValueError("The test file is missing: %s" % test_path)
    
    run_test(test_path)
    