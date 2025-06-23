"""
Usage:
    CLI app for Azure AI Search.
    -
    python main-search.py <func>
    python main-search.py env
    -
    python main-search.py create_cosmos_nosql_datasource <db> <collection>
    python main-search.py create_cosmos_nosql_datasource dev airports
    -
    python main-search.py create_cosmos_nosql_datasource dev airports
    -
    python main-search.py delete_datasource <name>
    python main-search.py delete_datasource cosmosdb-nosql-dev-airports
    -
    python main-search.py list_indexes
    python main-search.py list_indexers
    python main-search.py list_datasources
    -
    python main-search.py get_index nosql-airports
    python main-search.py get_indexer nosql-airports
    python main-search.py get_indexer_status nosql-airports
    python main-search.py get_datasource cosmosdb-nosql-dev-airports
    -
    python main-search.py create_index <index_name> <schema_file>
    python main-search.py create_index nosql-airports nosql_airports_index
    python main-search.py delete_index nosql-airports
    -
    python main-search.py create_indexer nosql-airports nosql_airports_indexer
    python main-search.py delete_indexer nosql-airports
    python main-search.py run_indexer nosql-airports
    -
    python main-search.py search_index nosql-airports all_airports
    python main-search.py search_index nosql-airports airports_charl
    python main-search.py search_index nosql-airports airports_clt
    python main-search.py search_index nosql-airports airports_campy
    python main-search.py search_index nosql-airports airports_lucene_east_cl_south 
    -
    python main-search.py lookup_doc nosql-airports eVBWc0FPdExvZzJYQXdBQUFBQUFBQT090
"""

# TODO - implement 

import json
import os
import sys
import time
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
        if name.startswith("AZURE_AI_SEARCH"):
            print("{}: {}".format(name, os.environ[name]))


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            print("=== CLI function: {}".format(func))
            client = AISearchUtil()
            time.sleep(1)

            if func == "env":
                check_env()
            elif func == 'list_indexes':
                result = client.list_indexes()
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'list_indexers':
                result = client.list_indexers()
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'list_datasources':
                result = client.list_datasources()
                print(json.dumps(result, sort_keys=False, indent=2))

            elif func == 'delete_indexer':
                name = sys.argv[2]
                result = client.delete_indexer(name)
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'delete_index':
                name = sys.argv[2]
                result = client.delete_index(name)
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'delete_datasource':
                name = sys.argv[2]
                result = client.delete_datasource(name)
                print(json.dumps(result, sort_keys=False, indent=2))

            elif func == 'create_cosmos_nosql_datasource':
                dbname, cname = sys.argv[2], sys.argv[3]
                result = client.create_cosmos_nosql_datasource(dbname, cname)
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'create_index':
                name, schema_json_filename = sys.argv[2], sys.argv[3]
                result = client.create_index(name, schema_json_filename)
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'create_indexer':
                name, schema_json_filename = sys.argv[2], sys.argv[3]
                result = client.create_indexer(name, schema_json_filename)
                print(json.dumps(result, sort_keys=False, indent=2))

            elif func == 'get_indexer_status':
                name = sys.argv[2]
                result = client.get_indexer_status(name)
                print(json.dumps(result, sort_keys=False, indent=2))
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
