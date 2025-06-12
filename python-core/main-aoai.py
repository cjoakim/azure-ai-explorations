"""
Usage:
  TODO  - implement samples with the Azure OpenAI SDK
  python main-aoai.py <func>
  python main-aoai.py explore
"""

import sys
import os
import traceback

from docopt import docopt
from dotenv import load_dotenv

from src.io.fs import FS
from src.os.env import Env
from src.os.system import System
from src.util.counter import Counter


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def explore():
    pass

if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            if func == "explore":
                explore()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
