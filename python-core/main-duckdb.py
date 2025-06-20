"""
Usage:
  Simple example use of DuckDB with local and remote files.
  python main-duckdb.py <func>
  python main-duckdb.py env
  python main-duckdb.py duck1_csv
  python main-duckdb.py duck2_imdb
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import sys
import os
import traceback

import duckdb

from docopt import docopt
from dotenv import load_dotenv

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


def duck1_csv():
    infile = "../data/misc/postal_codes_nc.csv"
    data = duckdb.read_csv(infile)
    print(data)
    print(str(type(data)))  # <class 'duckdb.duckdb.DuckDBPyRelation'>


def duck2_imdb():
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


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            if func == "env":
                check_env()
            elif func == "duck1_csv":
                duck1_csv()
            elif func == "duck2_imdb":
                duck2_imdb()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
