"""
Usage:
  CLI app for Azure AI Search.
  python main_search.py <func>
  python main_search.py env
"""

# TODO - implement 

import sys
import os
import traceback

from docopt import docopt
from dotenv import load_dotenv

from src.ai.ai_search_util import AISearchUtil
from src.io.fs import FS
from src.os.env import Env


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    for name in sorted(os.environ.keys()):
        if name.startswith("AZURE_"):
            if "PERSONAL" in name:
                pass
            else:
                print("{}: {}".format(name, os.environ[name]))
    print("username: {}".format(Env.username()))


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            if func == "env":
                check_env()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
