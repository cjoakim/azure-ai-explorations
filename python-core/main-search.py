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
    python main-search.py search_index nosql-airports airports_clt aisearch/searches.json
    python main-search.py search_index nosql-airports airports_atl aisearch/searches.json
    python main-search.py search_index nosql-airports airports_lucene_east_cl_south aisearch/searches.json
    python main-search.py search_index pythonlibs vector_search_fastapi_vector aisearch/searches.json
    -
    python main-search.py lookup_doc nosql-airports eVBWc0FPdExvZzJYQXdBQUFBQUFBQT090
    -
    python main-search.py direct_load_index <index_name> <data_json_filename>
    python main-search.py direct_load_index zipcodes ../data/zipcodes/us_zipcodes.json --load
    python main-search.py direct_load_index pythonlibs ../../CosmosAIGraph/data/pypi/wrangled_libs --load
"""

# TODO - implement 

import json
import os
import sys
import time
import traceback
import uuid

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

def direct_load_index(index_name, input_json_file_or_dir):
    docs = list()
    if input_json_file_or_dir.endswith(".json"):
        # it's a file, assumed to be a JSON array of documents
        # example file: python-ai/data/nc_zipcodes.json in this repo
        docs = FS.read_json(input_json_file_or_dir)
    else:
        # it's a directory, assumed to have one JSON file per document
        files = FS.list_files_in_dir(input_json_file_or_dir)
        print("Found {} files in directory {}".format(len(files), input_json_file_or_dir))
        for file in files:
            if file.endswith(".json"):
                fq_filename = "{}/{}".format(input_json_file_or_dir, file)
                doc = FS.read_json(fq_filename)
                if isinstance(doc, dict):
                    if "CosmosAIGraph" in input_json_file_or_dir:
                        doc = transform_pythonlib_doc(doc)
                    docs.append(doc)      
        print("Read {} documents from directory {}".format(len(docs), input_json_file_or_dir))
    for doc in docs:
        doc["id"] = str(uuid.uuid4())
        #print(json.dumps(doc, sort_keys=False, indent=2))

    if "--load" in sys.argv:
        client = AISearchUtil()
        batch, batch_size, batch_num = list(), 100, 0
        # Azure AI Search has a limit of 1000 documents per batch;
        # see https://learn.microsoft.com/en-us/azure/search/search-what-is-data-import
        for idx, doc in enumerate(docs):
            if idx < 100000:
                if "location" in doc.keys():
                    del doc["location"] # remove the 'location' nested object for now
                print("Document idx {}: id: {}".format(idx, doc["id"]))
                batch.append(doc)
                if len(batch) >= batch_size:
                    batch_num = batch_num + 1
                    print("Adding batch {} of {} documents".format(
                        batch_num, len(batch)))
                    try:
                        result = client.add_documents_to_index(index_name, batch)
                        print(json.dumps(result, sort_keys=False, indent=2))
                    except Exception as e:
                        print("Error adding batch: {}".format(str(e)))
                        print(traceback.format_exc())
                    batch = list()
                    time.sleep(1.0)  # sleep to avoid possible throttling

        if len(batch) > 0:
            batch_num = batch_num + 1
            print("Adding last batch {} of {} documents".format(batch_num, len(batch)))
            result = client.add_documents_to_index(index_name, batch)
            print(json.dumps(result, sort_keys=False, indent=2))
        
        print("{} documents were in the list to load".format(len(docs)))


def transform_pythonlib_doc(doc):
    newdoc = dict()
    for key in "name,description,summary,kwds,project_url,developers,embedding".split(","):
        if key in doc.keys():
            value = doc[key]
            if isinstance(value, str):
                value = value.strip().replace("\n", " ")[0:500].strip()
            newdoc[key] = value
    return newdoc


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

            elif func == 'lookup_datasource':
                name = sys.argv[2]
                result = client.lookup_datasource(name)
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'lookup_index':
                name = sys.argv[2]
                result = client.lookup_index(name)
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'lookup_indexer':
                name = sys.argv[2]
                result = client.lookup_indexer(name)
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'lookup_indexer_schema':
                indexer_name = sys.argv[2]
                index_name = sys.argv[3]
                datasource_name = sys.argv[4]
                result = client.lookup_indexer_schema(
                    indexer_name, index_name, datasource_name)
                print(json.dumps(result, sort_keys=False, indent=2))

            elif func == 'run_indexer':
                name = sys.argv[2]
                result = client.run_indexer(name)
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'reset_indexer':
                name = sys.argv[2]
                result = client.reset_indexer(name)
                print(json.dumps(result, sort_keys=False, indent=2))
            elif func == 'get_indexer_status':
                name = sys.argv[2]
                result = client.get_indexer_status(name)
                print(json.dumps(result, sort_keys=False, indent=2))

            elif func == 'search_index':
                index_name = sys.argv[2]
                search_name = sys.argv[3]
                searches_json_filename = sys.argv[4]
                search_params = FS.read_json(searches_json_filename)[search_name]
                print("Index name:  {}".format(index_name))
                print("Search name: {}".format(search_name))
                print("Search params:\n{}".format(
                    json.dumps(search_params, sort_keys=False, indent=2)))
                result = client.search_index(index_name, search_name, search_params)
                print(json.dumps(result, sort_keys=False, indent=2))
                FS.write_json(result, "tmp/search_result.json", pretty=True, sort_keys=False)

            elif func == 'direct_load_index':
                index_name = sys.argv[2]
                input_json_file_or_dir = sys.argv[3]
                direct_load_index(index_name, input_json_file_or_dir)
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
