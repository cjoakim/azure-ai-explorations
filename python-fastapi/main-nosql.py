"""
Usage:
    python main_nosql.py list_standard_envvars
    python main_nosql.py log_standard_envvars
    python main_nosql.py load_openflights
    python main_nosql.py test_cosmos_nosql dbname, db_ru, cname, c_ru, pkpath
    python main_nosql.py test_cosmos_nosql dev 1000 test 0 /pk
    python main_nosql.py test_cosmos_nosql dev 1000 app 0 /pk
    python main_nosql.py test_cosmos_nosql dev 0 test 400 /pk
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

from src.io.fs import FS
from src.os.env import Env
from src.db.cosmos_nosql_util import CosmosNoSqlUtil
from src.util.data_gen import DataGenerator

fake = Faker()

def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)

def list_standard_envvars():
    for name in Env.standard_env_vars():
        print(name)

def log_standard_envvars():
    Env.log_standard_env_vars() 

async def load_openflights():
    try:
        opts = dict()
        opts["enable_diagnostics_logging"] = True
        nosql_util = CosmosNoSqlUtil(opts)
        await nosql_util.initialize()
        print("nosql_util initialized")
        acct = Env.cosmosdb_nosql_acct()
        dbname = Env.cosmosdb_nosql_default_database()
        cname = Env.cosmosdb_nosql_default_container()
        print("Cosmos DB acct: {}, dbname: {}, cname: {}".format(acct, dbname, cname))
        nosql_util.set_db(dbname)
        nosql_util.set_container(cname)
        
        # parsing loop
        json_lines = FS.read_lines("../data/openflights/json/airports.json")
        parsed_airports = list()
        for json_line in json_lines:
            doc = parse_reformat_airport(json_line)
            if doc is not None:
                parsed_airports.append(doc)
        FS.write_json(parsed_airports, "tmp/parsed_airports.json")
        print("{} parsed airports".format(len(parsed_airports)))

        # loading loop.  intentionally inefficient (i.e - not bulk-loaded),
        # so as to enable 1000-RU free Cosmos DB accounts.
        for idx, doc in enumerate(parsed_airports):
            await nosql_util.upsert_item(doc)
            print("airport loaded: {} {}".format(idx + 1, doc["IATA"]))

    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())
    finally:   
        if nosql_util is not None:
            await nosql_util.close()

def parse_reformat_airport(json_line):
    try:
        # The documents look like this.  Cast the numeric attributes
        # to integers and floats in this method.
        # {
        #   "AType": "airport",
        #   "AirportID": "3876",
        #   "Altitude": "748",
        #   "City": "Charlotte",
        #   "Country": "United States",
        #   "DST": "A",
        #   "IATA": "CLT",
        #   "ICAO": "KCLT",
        #   "Latitude": "35.2140007019043",
        #   "Longitude": "-80.94309997558594",
        #   "Name": "Charlotte Douglas International Airport",
        #   "Source": "OurAirports",
        #   "Timezone": "-5",
        #   "Tz": "America/New_York"
        # }
        doc = json.loads(json_line)
        doc["AirportID"] = int(doc["AirportID"])
        doc["Altitude"] = int(doc["Altitude"])
        doc["Latitude"] = float(doc["Latitude"])
        doc["Longitude"] = float(doc["Longitude"])
        doc["Timezone"] = float(doc["Timezone"])
        doc["id"] = str(uuid.uuid4())
        doc["pk"] = doc["Country"]
        if doc['IATA'] == "CLT":
            print(json.dumps(doc, sort_keys=True, indent=2))
        return doc
    except Exception as e:
        print("parse_reformat_airport - unable to parse line:\n{}".format(json_line))
        return None

async def test_cosmos_nosql(
    dbname: str, db_ru: int, cname: str, c_ru: int, pkpath: str):
    nosql_util = None
    logging.info("test_cosmos_nosql, dbname: {}, db_ru: {}, cname: {}, c_ru: {}, pk: {}".format(
        dbname, db_ru, cname, c_ru, pkpath))
    try:
        opts = dict()
        opts["enable_diagnostics_logging"] = True
        nosql_util = CosmosNoSqlUtil(opts)
        await nosql_util.initialize()

        dbs = await nosql_util.list_databases()
        logging.info("databases: {}".format(dbs))
        
        try:
            result = await nosql_util.create_database(dbname, db_ru)
            logging.info("create_database: {} {} {}".format(
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
            logging.info("create_container: {} {} {} {}".format(
                cname, c_ru, pkpath, result))
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())

        ctrproxy = nosql_util.set_container(cname)
        print("ctrproxy: {}".format(ctrproxy))

        ctrproxy = nosql_util.set_container(cname)
        print("ctrproxy: {}".format(ctrproxy))

        id = str(uuid.uuid4())
        pk = "pk"

        doc = await nosql_util.upsert_item(create_random_document(id, pk))
        print("upsert_item doc: {}".format(doc))
        print("last_response_headers: {}".format(nosql_util.last_response_headers()))
        print("last_request_charge: {}".format(nosql_util.last_request_charge()))

        doc = await nosql_util.point_read(id, pk)
        print("point_read doc: {}".format(doc))
        print("last_request_charge: {}".format(nosql_util.last_request_charge()))

        doc["name"] = "updated"
        updated = await nosql_util.upsert_item(doc)
        print("updated doc: {}".format(updated))

        response = await nosql_util.delete_item(id, pk)
        print("delete_item response: {}".format(response))

        try:
            doc = await nosql_util.point_read(id, pk)
            print("point_read of deleted doc: {}".format(doc))
        except Exception as e:
            print("point_read of deleted doc threw an exception")
        operations, pk = list(), "bulk_pk"
        for n in range(3):
            # example: ("create", (get_sales_order("create_item"),))
            # each operation is a 2-tuple, with the operation name as tup[0]
            # tup[1] is a nested 2-tuple , with the document as tup[0]
            op = ("create", (create_random_document(None, pk),))
            operations.append(op)
        results = await nosql_util.execute_item_batch(operations, pk)
        for idx, result in enumerate(results):
            print("batch result {}: {}".format(idx, result))

        results = await nosql_util.query_items(
            "select * from c where c.doctype = 'test'", True
        )
        for idx, result in enumerate(results):
            print("select * query result {}: {}".format(idx, result))
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())
    finally:   
        if nosql_util is not None:
            await nosql_util.close()

def create_random_document(id, pk):
    dg = DataGenerator()
    return dg.random_person_document()

def throw_exception_here():
    # intentionally throw an exception
    intentional_exception = 1 / 0


if __name__ == "__main__":
    # standard initialization of env and logger
    load_dotenv(override=True)
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

    if len(sys.argv) < 2:
        print_options("Error: invalid command-line")
        exit(1)
    else:
        try:
            func = sys.argv[1].lower()
            if func == "list_standard_envvars":
                list_standard_envvars()
            elif func == "log_standard_envvars":
                log_standard_envvars()
            elif func == "load_openflights":
                asyncio.run(load_openflights())
            elif func == "test_cosmos_nosql":
                dbname = sys.argv[2]
                db_ru  = int(sys.argv[3])
                cname  = sys.argv[4]
                c_ru   = int(sys.argv[5])
                pkpath = sys.argv[6]
                asyncio.run(test_cosmos_nosql(dbname, db_ru, cname, c_ru, pkpath))
            else:
                print_options("Error: invalid command-line")
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())

