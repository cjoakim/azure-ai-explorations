"""
Usage:
  Example use of the Cosmos NoSQL API.
  python main-cosmos-nosql.py test_cosmos_nosql dbname, db_ru, cname, c_ru, pkpath
  python main-cosmos-nosql.py test_cosmos_nosql dev 1000 test 0 /pk
  python main-cosmos-nosql.py test_cosmos_nosql dev 1000 app 0 /pk
  python main-cosmos-nosql.py test_cosmos_nosql dev 0 test 400 /pk
  python main-cosmos-nosql.py load_python_libraries dev python_libraries
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import asyncio
import json
import sys
import time
import logging
import traceback
import uuid

from docopt import docopt
from dotenv import load_dotenv

from faker import Faker

from src.os.env import Env
from src.io.fs import FS
from src.db.cosmos_nosql_util import CosmosNoSqlUtil
from src.util.data_gen import DataGenerator

fake = Faker()

def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)

async def test_cosmos_nosql(
    dbname: str, db_ru: int, cname: str, c_ru: int, pkpath: str):

    logging.info("test_cosmos_nosql, dbname: {}, db_ru: {}, cname: {}, c_ru: {}, pk: {}".format(
        dbname, db_ru, cname, c_ru, pkpath))
    try:
        opts = dict()
        opts["enable_diagnostics_logging"] = True
        nosql_util = CosmosNoSqlUtil(opts)
        await nosql_util.initialize()

        dbs = await nosql_util.list_databases()
        logging.info("===== databases: {}".format(dbs))
        
        try:
            result = await nosql_util.create_database(dbname, db_ru)
            logging.info("===== create_database: {} {} {}".format(
                dbname, db_ru, result))
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())

        dbproxy = nosql_util.set_db(dbname)
        print("dbproxy: {}".format(dbproxy))

        containers = await nosql_util.list_containers()
        print("containers: {}".format(containers))

        try:
            result = await nosql_util.create_container(cname, c_ru, pkpath)
            logging.info("===== create_container: {} {} {} {}".format(
                cname, c_ru, pkpath, result))
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())

        ctrproxy = nosql_util.set_container(cname)
        print("ctrproxy: {}".format(ctrproxy))

        #throw_exception_here()

        ctrproxy = nosql_util.set_container(cname)
        print("ctrproxy: {}".format(ctrproxy))

        id = str(uuid.uuid4())

        doc = await nosql_util.upsert_item(create_random_document(id, None))
        print("===== upsert_item doc: {}".format(doc))
        print("last_response_headers: {}".format(nosql_util.last_response_headers()))
        print("last_request_charge: {}".format(nosql_util.last_request_charge()))

        pk = doc["pk"]
        print("===== point_read id: {}, pk: {}".format(id, pk))
        doc = await nosql_util.point_read(id, pk)
        print("point_read doc: {}".format(doc))
        print("last_request_charge: {}".format(nosql_util.last_request_charge()))

        print("===== updating ...")
        doc["name"] = "updated"
        updated = await nosql_util.upsert_item(doc)
        print("updated doc: {}".format(updated))

        print("===== deleting ...")
        response = await nosql_util.delete_item(id, pk)
        print("delete_item response: {}".format(response))

        if False:
            try:
                print("===== point_read of deleted doc ...")
                doc = await nosql_util.point_read(id, pk)
                print("point_read of deleted doc: {}".format(doc))
            except Exception as e:
                print("point_read of deleted doc threw an exception")

        operations, pk = list(), "bulk_pk"
        for n in range(3):
            # example: ("create", (get_sales_order("create_item"),))
            # each operation is a 2-tuple, with the operation name as tup[0]
            # tup[1] is a nested 2-tuple , with the document as tup[0]
            doc = create_random_document(None, pk)
            print("bulk create_item doc: {}".format(doc))
            op = ("create", (doc,))
            operations.append(op)
        print("===== execute_item_batch with {} operations ...".format(len(operations)))
        results = await nosql_util.execute_item_batch(operations, pk)
        for idx, result in enumerate(results):
            print("batch result {}: {}".format(idx, result))

        print("===== query_items ...")
        results = await nosql_util.query_items(
            "select * from c where c.doctype = 'sample'", True
        )
        for idx, result in enumerate(results):
            print("select * query result {}: {}".format(idx, result))
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())
    await nosql_util.close()
    logging.info("end of test_cosmos_service")

async def load_python_libraries(dbname: str, cname: str):
    """
    Load the CosmosAIGraph Python libraries documents into the given
    Cosmos NoSQL API database and container.
    """
    logging.info("load_python_libraries, dbname: {}, cname: {}".format(dbname, cname))
    try:
        opts = dict()
        opts["enable_diagnostics_logging"] = True
        nosql_util = CosmosNoSqlUtil(opts)
        await nosql_util.initialize()
        nosql_util.set_db(dbname)
        nosql_util.set_container(cname)

        # Use the CosmosAIGraph Python libraries dataset in the public repo.
        # I created this dataset while at Microsoft.
        # See the repo at: https://github.com/AzureCosmosDB/CosmosAIGraph
        # Clone the CosmosAIGraph repo to the same parent directory as this repo.
        input_dir = "../../CosmosAIGraph/data/pypi/wrangled_libs/"
        entries = FS.walk(input_dir, include_dirs=[], include_types=['json'])

        # For DiskANN Vector Search, first enable the Feature as described here:
        # https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search#enable-the-vector-indexing-and-search-feature
        for idx, entry in enumerate(entries):
            if idx < 999999:
                abspath = entry["abspath"]
                print("processing file index {}: {}".format(idx, abspath))
                try:
                    doc = FS.read_json(abspath)
                    if doc != None:
                        # There is approx 600MB in this dataset, so it will fit in a
                        # 20GB physical partition; the partition key value is "pypi".
                        doc["pk"] = "pypi"
                        await nosql_util.upsert_item(doc)
                except Exception as e:
                    logging.info("Error processing file {}: {}".format(abspath, str(e)))
                    logging.info(traceback.format_exc())
                    time.sleep(0.1)  # to avoid throttling and 429 errors

        print("entry count: {}".format(len(entries)))  # 10855
        await nosql_util.close()

    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())

def create_random_document(id, pk):
    dg = DataGenerator()
    return dg.random_person_document(id, pk)

def throw_exception_here():
    # intentionally throw an exception
    intentional_exception = 1 / 0


if __name__ == "__main__":
    # standard initialization of env and logger
    load_dotenv(override=True)
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    Env.log_standard_env_vars()
    if len(sys.argv) < 2:
        print_options("Error: invalid command-line")
        exit(1)
    else:
        try:
            func = sys.argv[1].lower()
            if func == "test_cosmos_nosql":
                dbname = sys.argv[2]
                db_ru  = int(sys.argv[3])
                cname  = sys.argv[4]
                c_ru   = int(sys.argv[5])
                pkpath = sys.argv[6]
                asyncio.run(test_cosmos_nosql(dbname, db_ru, cname, c_ru, pkpath))
            elif func == "load_python_libraries":
                dbname = sys.argv[2]
                cname  = sys.argv[3]
                asyncio.run(load_python_libraries(dbname, cname))
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())
