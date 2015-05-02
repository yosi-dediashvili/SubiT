import sys
import os
import argparse
import logging

logging.disable(logging.CRITICAL)
sys.path.append(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "src"))

parser = argparse.ArgumentParser(
    description="Executes one or more test files.")
parser.add_argument(
    "test_paths", metavar='FILE', type=str, nargs="+", 
    help="Full or Relative (to the current directory) path to the test file")
args = parser.parse_args()


def run_test(test_path):
    print "Running test file: %s" % test_path
    import imp
    global_wd = os.getcwd()
    dir_name = os.path.dirname(test_path)
    sys.path.append(dir_name)
    os.chdir(dir_name)
    imp.load_source('current_test', test_path).run_tests()
    sys.path.remove(dir_name)
    os.chdir(global_wd)

for test_path in args.test_paths:
    if not os.path.isabs(test_path):
        test_path = os.path.abspath(os.path.join(os.getcwd(), test_path))
    if not os.path.exists(test_path):
        raise ValueError("The test file is missing: %s" % test_path)
    
    run_test(test_path)
    