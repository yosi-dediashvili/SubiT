# Scripts that prepares the environment (logs and paths) for interactive work 
# with subit.
import os
import sys
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..\src")))

import logging
logger = logging.getLogger("subit")
logger.setLevel(logging.DEBUG)
logging.basicConfig()