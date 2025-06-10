"""
Usage:
  python main.py <func>
  python main.py env
  python main.py duck1
  python main.py ppstats
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import base64
import json
import logging
import sys
import time
import os
import traceback

import duckdb
import pypistats

from pprint import pprint

from docopt import docopt
from dotenv import load_dotenv

from six import moves

from src.util.bytes import Bytes
from src.util.counter import Counter
from src.os.env import Env
from src.io.fs import FS
from src.db.mongo_util import MongoUtil
from src.os.system import System


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    Env.log_standard_env_vars()

    # for name in sorted(os.environ.keys()):
    #     if name.startswith("LOCAL_PG_"):
    #         print("{}: {}".format(name, os.environ[name]))

    print("check_env - username: {}".format(Env.username()))


def duck1():
    data = duckdb.read_csv("data/postal_codes_nc.csv")
    print(data)
    print(str(type(data)))  # <class 'duckdb.duckdb.DuckDBPyRelation'>

    data = duckdb.read_csv("https://datasets.imdbws.com/name.basics.tsv.gz")
    print(data)
    print(str(type(data)))  # <class 'duckdb.duckdb.DuckDBPyRelation'>

    # name.basics.tsv.gz
    # title.akas.tsv.gz
    # title.basics.tsv.gz
    # title.crew.tsv.gz
    # title.episode.tsv.gz
    # title.principals.tsv.gz
    # title.ratings.tsv.gz


def ppstats():
    print(pypistats.recent("m26"))


if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        func = sys.argv[1].lower()
        if func == "env":
            check_env()
        elif func == "duck1":
            duck1()
        elif func == "ppstats":
            ppstats()
        else:
            print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
