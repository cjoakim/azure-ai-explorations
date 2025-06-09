import logging
import traceback

from azure.cosmos.aio import CosmosClient
from azure.cosmos import ThroughputProperties
from azure.cosmos.partition_key import PartitionKey

from azure.identity import ClientSecretCredential, DefaultAzureCredential

from src.os.env import Env 

# This class is used to access the Azure Cosmos DB NoSQL API
# via the the asynchronous SDK methods.
# Chris Joakim, 2025

# See https://pypi.org/project/azure-cosmos/
# See https://learn.microsoft.com/en-us/python/api/overview/azure/cosmos-db?view=azure-python
# See https://learn.microsoft.com/en-us/python/api/overview/azure/cosmos-readme?view=azure-python
# See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos/azure-cosmos/samples
# See https://azuresdkdocs.blob.core.windows.net/$web/python/azure-cosmos/4.7.0/azure.cosmos.html
# See https://github.com/Azure/azure-sdk-for-python/tree/azure-cosmos_4.7.0/sdk/cosmos/azure-cosmos/samples
# See https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search

# azure_logger can be used to set the verbosity of the Azure and Cosmos SDK logging
azure_logger = logging.getLogger("azure")
azure_logger.setLevel(logging.WARNING)

LAST_REQUEST_CHARGE_HEADER = "x-ms-request-charge"


class CosmosNoSqlUtil:
    def __init__(self, opts={}):
        self._opts = opts
        self._dbname = None
        self._dbproxy = None
        self._ctrproxy = None
        self._cname = None
        self._client = None
        logging.info("CosmosNoSqlUtil - constructor")

    async def initialize(self):
        """This method should be called after the above constructor."""
        authtype = Env.cosmosdb_nosql_authtype()
        logging.info("CosmosNoSqlUtil#authtype: {}".format(authtype))

        if authtype == "key":
            logging.info("CosmosNoSqlUtil#initialize with key")
            uri = Env.cosmosdb_nosql_uri()
            key = Env.cosmosdb_nosql_key()
            logging.debug("CosmosNoSqlUtil#uri: {}".format(uri))
            logging.debug("CosmosNoSqlUtil#key: {}".format(key))
            self._client = CosmosClient(uri, key)
            logging.info("CosmosNoSqlUtil - initialize() with key completed")
        else:
            logging.info("CosmosNoSqlUtil#initialize with DefaultAzureCredential")
            uri = Env.cosmosdb_nosql_uri()
            credential = DefaultAzureCredential()
            # credential ino is injected into the runtime environment
            self._client = CosmosClient(uri, credential=credential)
            logging.info(
                "CosmosNoSqlUtil - initialize() with DefaultAzureCredential completed"
            )

    async def close(self):
        if self._client is not None:
            await self._client.close()
            logging.info("CosmosNoSqlUtil - client closed")

    async def create_database(self, dbname, db_level_throughput=0):
        created = False
        if self._client is not None:
            databases = await self.list_databases();
            if dbname in databases:
                logging.info("CosmosNoSqlUtil - database already exists: {}".format(dbname))
            else:
                if int(db_level_throughput) > 0:
                    await self._client.create_database(
                        id=dbname,
                        offer_throughput=ThroughputProperties(
                            auto_scale_max_throughput=db_level_throughput,
                            auto_scale_increment_percent=0))
                else:
                    await self._client.create_database(id=dbname)
                logging.info("CosmosNoSqlUtil - database created: {}".format(dbname))
                self.set_db(dbname)
                created = True
        return created

    async def delete_database(self, dbname):
        result = True
        try:
            await self._client.delete_database(dbname)
        except Exception as e:
            logging.critical(str(e))
            print(traceback.format_exc())
            result = False
        return result

    async def delete_container(self, cname):
        result = True
        try:
            await self._dbproxy.delete_container(cname)
        except Exception as e:
            logging.critical(str(e))
            print(traceback.format_exc())
            result = False
        return result

    async def create_container(self, cname: str, c_ru: int, pkpath: str):
        created = False
        if self._client is not None:
            containers = await self.list_containers();
            if cname in containers:
                logging.info("CosmosNoSqlUtil - containers already exists: {}".format(cname))
            else:
                partition_key = PartitionKey(path=pkpath, kind='Hash')
                if c_ru > 0:
                    throughput = ThroughputProperties(
                        auto_scale_max_throughput=c_ru,
                        auto_scale_increment_percent=0)
                    await self._dbproxy.create_container(
                        id=cname,
                        partition_key=partition_key,
                        offer_throughput=throughput)
                else:
                    await self._dbproxy.create_container(
                        id=cname,
                        partition_key=partition_key)
                logging.info("CosmosNoSqlUtil - container created: {}".format(cname))
                created = True
        return created

    async def list_databases(self):
        """Return the list of database names in the account."""
        dblist = list()
        async for db in self._client.list_databases():
            dblist.append(db["id"])
        return dblist

    def set_db(self, dbname):
        """Set the current database to the given dbname."""
        self._dbname = dbname
        self._dbproxy = self._client.get_database_client(dbname)
        return self._dbproxy  # <class 'azure.cosmos.aio._database.DatabaseProxy'>

    def get_current_dbname(self):
        return self._dbname
    
    def get_current_cname(self):
        return self._cname

    def set_container(self, cname):
        """Set the current container in the current database to the given cname."""
        self._cname = cname
        self._ctrproxy = self._dbproxy.get_container_client(cname)
        return self._ctrproxy  # <class 'azure.cosmos.aio._container.ContainerProxy'>

    def get_database_link(self):
        return self._dbproxy.database_link

    async def get_database_throughput(self):
        return await self._dbproxy.get_throughput()

    def get_container_link(self):
        return self._ctrproxy.container_link
    
    async def get_container_throughput(self):
        try:
            return await self._ctrproxy.get_throughput()
        except Exception as e:
            logging.critical(str(e))
            print(traceback.format_exc())
            return None

    async def get_container_properties(self) -> dict:
        #<class 'azure.cosmos._cosmos_responses.CosmosDict'>
        simple_props = dict()
        cosmos_dict = await self._ctrproxy.read()
        for key in cosmos_dict.keys():
            simple_props[key] = cosmos_dict.get(key)
        return simple_props

    async def list_containers(self):
        """Return the list of container names in the current database."""
        container_list = list()
        async for container in self._dbproxy.list_containers():
            container_list.append(container["id"])
        return container_list

    async def point_read(self, id, pk):
        return await self._ctrproxy.read_item(item=id, partition_key=pk)

    async def create_item(self, doc):
        return await self._ctrproxy.create_item(body=doc)

    async def upsert_item(self, doc):
        return await self._ctrproxy.upsert_item(body=doc)

    async def delete_item(self, id, pk):
        return await self._ctrproxy.delete_item(item=id, partition_key=pk)

    async def count_documents(self):
        docs = list()
        sql = "SELECT VALUE COUNT(1) FROM c"
        items_paged = self._ctrproxy.query_items(query=sql, parameters=[])
        async for item in items_paged:
            docs.append(item)
        return docs

    async def execute_item_batch(self, item_operations: list, pk: str):
        # example item_operations:
        #   [("create", (get_sales_order("create_item"),)), next op, next op, ...]
        # each operation is a 2-tuple, with the operation name as tup[0]
        # tup[1] is a nested 2-tuple , with the document as tup[0]
        return await self._ctrproxy.execute_item_batch(
            batch_operations=item_operations, partition_key=pk
        )

    async def query_items(self, sql, cross_partition=False, pk=None, max_items=100):
        parameters_list, results_list = list(), list()
        parameters_list.append(
            {"name": "@enable_cross_partition_query", "value": cross_partition}
        )
        if pk is not None:
            parameters_list.append({"name": "@partition_key", "value": pk})
        query_results = self._ctrproxy.query_items(
            query=sql, parameters=parameters_list
        )
        async for item in query_results:
            results_list.append(item)
        return results_list

    async def parameterized_query(
        self,
        sql_template,
        sql_parameters,
        cross_partition=False,
        pk=None,
        max_items=100,
    ):
        parameters_list, results_list = list(), list()
        parameters_list.append(
            {"name": "@enable_cross_partition_query", "value": cross_partition}
        )
        parameters_list.append({"name": "@max_item_count", "value": max_items})
        if pk is not None:
            parameters_list.append({"name": "@partition_key", "value": pk})
        if sql_parameters is not None:
            for sql_param in sql_parameters:
                parameters_list.append(sql_param)
        query_results = self._ctrproxy.query_items(
            query=sql_template, parameters=parameters_list
        )
        async for item in query_results:
            results_list.append(item)
        return results_list

    def last_response_headers(self) -> dict:
        """
        The Cosmos DB response headers are an instance of class CIMultiDict,
        which is not JSON serializable.  Convert these CIMultiDict headers
        into a simple dict and return that dict.
        """
        try:
            multidict_headers = self._ctrproxy.client_connection.last_response_headers
            simple_headers = dict()
            for key, value in multidict_headers.items():
                simple_headers[key] = value
            return simple_headers
        except:
            return dict()

    def last_request_charge(self):
        try:
            return float(
                self._ctrproxy.client_connection.last_response_headers[
                    LAST_REQUEST_CHARGE_HEADER
                ]
            )
        except:
            return -1.0
