import os
import re

def run_tests():
    for root, dirs, files in os.walk("."):
        for f in files:
            if re.match("^test_.*?\.py$", f) and f != 'test_all.py':
                os.system(
                    "python %s %s" % ("run_test.py", os.path.join(root, f)))