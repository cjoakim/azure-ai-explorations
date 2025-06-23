"""
Usage:
  Example use of the Cosmos NoSQL API.
  python main-cosmos-nosql.py load_airports dev airports pk
  python main-cosmos-nosql.py test_cosmos_nosql dbname, db_ru, cname, c_ru, pkpath
  python main-cosmos-nosql.py test_cosmos_nosql dev 1000 test 0 /pk
  python main-cosmos-nosql.py test_cosmos_nosql dev 1000 app 0 /pk
  python main-cosmos-nosql.py test_cosmos_nosql dev 0 test 400 /pk
  python main-cosmos-nosql.py load_python_libraries dev python_libraries
  python main-cosmos-nosql.py vector_search_similar_libs <dbname> <cname> <id>
  python main-cosmos-nosql.py vector_search_similar_libs dev python_libraries pypi_flask
  See https://cosmos.azure.com/ for ad-hoc queries
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


async def load_airports(dbname: str, cname: str, pkpath: str):
    # See the dotnet-cosmos/ directory in this repo for a faster
    # implementation based on bulk-loading.
    try:
        infile = "../data/openflights/json/airports.json"
        json_lines = FS.read_lines(infile)
        documents = list()
        for line in json_lines:
            if len(line) > 10:
                try:
                    rawdoc = json.loads(line)
                    newdoc = dict()
                    for key in sorted(rawdoc.keys()):
                        value = rawdoc[key]
                        newkey = key.lower()
                        newdoc[newkey] = value
                    newdoc["id"] = str(uuid.uuid4())
                    newdoc[pkpath] = newdoc["country"]
                    # TODO - reformat to GeoJSON for Geospatial search
                    newdoc["latitude"] = float(newdoc["latitude"])
                    newdoc["longitude"] = float(newdoc["longitude"])
                    newdoc["altitude"] = float(newdoc["altitude"])
                    newdoc["airportid"] = int(newdoc["airportid"])

                    if newdoc[pkpath] != "\\N":
                        if newdoc["iata"] != "\\N":
                            print(json.dumps(newdoc, sort_keys=False, indent=2))
                            documents.append(newdoc)
                except:
                    print("bad json on line: {}".format(line))
        print("{} documents parsed and filtered from {} file lines".format(
            len(documents), len(json_lines)))

        opts = dict()
        opts["enable_diagnostics_logging"] = True
        nosql_util = CosmosNoSqlUtil(opts)
        await nosql_util.initialize()

        dbproxy = nosql_util.set_db(dbname)
        print("dbproxy: {}".format(dbproxy))

        ctrproxy = nosql_util.set_container(cname)
        print("ctrproxy: {}".format(ctrproxy))

        if True:
            for doc in documents:
                try:
                    cdb_doc = await nosql_util.upsert_item(doc)
                    print("upserted doc: {}".format(json.dumps(cdb_doc, indent=2)))
                    time.sleep(0.05)
                except Exception as e:
                    logging.info("Error upserting doc: {}".format(str(e)))
                    logging.info(traceback.format_exc())
                    time.sleep(1.0)
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())

async def test_cosmos_nosql(
    dbname: str, db_ru: int, cname: str, c_ru: int, pkpath: str):
    logging.info(
        "test_cosmos_nosql, dbname: {}, db_ru: {}, cname: {}, c_ru: {}, pk: {}".format(
            dbname, db_ru, cname, c_ru, pkpath
        )
    )
    try:
        opts = dict()
        opts["enable_diagnostics_logging"] = True
        nosql_util = CosmosNoSqlUtil(opts)
        await nosql_util.initialize()

        dbs = await nosql_util.list_databases()
        logging.info("===== databases: {}".format(dbs))

        try:
            result = await nosql_util.create_database(dbname, db_ru)
            logging.info(
                "===== create_database: {} {} {}".format(dbname, db_ru, result)
            )
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())

        dbproxy = nosql_util.set_db(dbname)
        print("dbproxy: {}".format(dbproxy))

        containers = await nosql_util.list_containers()
        print("containers: {}".format(containers))

        try:
            result = await nosql_util.create_container(cname, c_ru, pkpath)
            logging.info(
                "===== create_container: {} {} {} {}".format(
                    cname, c_ru, pkpath, result
                )
            )
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())

        ctrproxy = nosql_util.set_container(cname)
        print("ctrproxy: {}".format(ctrproxy))

        # throw_exception_here()

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
        nosql_util = await initialize_cosmos_nosql_util(dbname, cname)

        # Use the CosmosAIGraph Python libraries dataset in the public repo.
        # I created this dataset while at Microsoft.
        # See the repo at: https://github.com/AzureCosmosDB/CosmosAIGraph
        # Clone the CosmosAIGraph repo to the same parent directory as this repo.
        input_dir = "../../CosmosAIGraph/data/pypi/wrangled_libs/"
        entries = FS.walk(input_dir, include_dirs=[], include_types=["json"])

        # For DiskANN Vector Search, first enable the Feature as described here:
        # https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search#enable-the-vector-indexing-and-search-feature
        for idx, entry in enumerate(entries):
            if idx < 999999:
                abspath = entry["abspath"]
                print("processing file index {}: {}".format(idx, abspath))
                try:
                    doc = FS.read_json(abspath)
                    if doc is not None:
                        # There is approx 600MB in this dataset, so it will fit in a
                        # 20GB physical partition; the partition key value is "pypi".
                        doc["pk"] = "pypi"
                        await nosql_util.upsert_item(doc)
                except Exception as e:
                    logging.info("Error processing file {}: {}".format(abspath, str(e)))
                    logging.info(traceback.format_exc())
                    time.sleep(0.1)  # to avoid throttling and 429 errors

        print(
            "entry count: {}".format(len(entries))
        )  # 10855 docs, 10761 loaded on 6/10
        await nosql_util.close()

    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())


async def vector_search_similar_libs(dbname: str, cname: str, id: str):
    nosql_util = await initialize_cosmos_nosql_util(dbname, cname)
    try:
        sql = (
            "SELECT c.id, c.pk, c.name, c.embedding FROM c where c.id = '{}' and c.pk = 'pypi' offset 0 limit 1"
        ).format(id)
        docs = await nosql_util.query_items(
            sql, cross_partition=False, pk="/pk", max_items=1
        )
        if len(docs) == 0:
            print("No document found with id: {}".format(id))
        else:
            embedding = docs[0]["embedding"]
            print("embedding length: {}".format(len(embedding)))
            sql = vector_search_sql(12, embedding)
            FS.write(sql, "tmp/vector_search_sql.txt")
            results = await nosql_util.query_items(sql, True)
            for idx, result in enumerate(results):
                print(result)

            # results for pypi_flask:
            # {'id': 'pypi_flask', 'pk': 'pypi', 'name': 'flask', 'SimilarityScore': 0}
            # {'id': 'pypi_flask_restful', 'pk': 'pypi', 'name': 'flask-restful', 'SimilarityScore': 0.4545473538499831}
            # {'id': 'pypi_flask_api', 'pk': 'pypi', 'name': 'flask-api', 'SimilarityScore': 0.46250825400134066}
            # {'id': 'pypi_werkzeug', 'pk': 'pypi', 'name': 'werkzeug', 'SimilarityScore': 0.4705090974004422}
            # {'id': 'pypi_flask_sqlalchemy', 'pk': 'pypi', 'name': 'flask-sqlalchemy', 'SimilarityScore': 0.47186151629061857}
            # {'id': 'pypi_flask_appbuilder', 'pk': 'pypi', 'name': 'flask-appbuilder', 'SimilarityScore': 0.4725431475814093}
            # {'id': 'pypi_flask_caching', 'pk': 'pypi', 'name': 'flask-caching', 'SimilarityScore': 0.48652661445815537}
            # {'id': 'pypi_bottle', 'pk': 'pypi', 'name': 'bottle', 'SimilarityScore': 0.4896278704608053}
            # {'id': 'pypi_pylons', 'pk': 'pypi', 'name': 'pylons', 'SimilarityScore': 0.49081412664406004}
            # {'id': 'pypi_flask_testing', 'pk': 'pypi', 'name': 'flask-testing', 'SimilarityScore': 0.49349240632627694}
            # {'id': 'pypi_flask_admin', 'pk': 'pypi', 'name': 'flask-admin', 'SimilarityScore': 0.4943784751148062}
            # {'id': 'pypi_flask_wtf', 'pk': 'pypi', 'name': 'flask-wtf', 'SimilarityScore': 0.49762255864297505}

    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())
    await nosql_util.close()


def vector_search_sql(top_n: int, embedding: list):
    return """
SELECT TOP {} c.id, c.pk, c.name, VectorDistance(c.embedding, {}) AS SimilarityScore
 FROM c
 ORDER BY VectorDistance(c.embedding, {})
""".format(
        top_n, embedding, embedding
    ).lstrip()


async def initialize_cosmos_nosql_util(dbname: str, cname: str):
    opts = dict()
    opts["enable_diagnostics_logging"] = True
    nosql_util = CosmosNoSqlUtil(opts)
    await nosql_util.initialize()
    nosql_util.set_db(dbname)
    nosql_util.set_container(cname)
    return nosql_util


def create_random_document(id, pk):
    dg = DataGenerator()
    return dg.random_person_document(id, pk)


def throw_exception_here():
    # intentionally throw an exception
    intentional_exception = 1 / 0
    print("{}".format(intentional_exception))


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
            if func == "load_airports":
                dbname, cname, pk = sys.argv[2], sys.argv[3], sys.argv[4]
                asyncio.run(load_airports(dbname, cname, pk))
            elif func == "test_cosmos_nosql":
                dbname = sys.argv[2]
                db_ru = int(sys.argv[3])
                cname = sys.argv[4]
                c_ru = int(sys.argv[5])
                pkpath = sys.argv[6]
                asyncio.run(test_cosmos_nosql(dbname, db_ru, cname, c_ru, pkpath))
            elif func == "load_python_libraries":
                dbname = sys.argv[2]
                cname = sys.argv[3]
                asyncio.run(load_python_libraries(dbname, cname))
            elif func == "vector_search_similar_libs":
                dbname = sys.argv[2]
                cname = sys.argv[3]
                libname = sys.argv[4]
                asyncio.run(vector_search_similar_libs(dbname, cname, libname))
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())
