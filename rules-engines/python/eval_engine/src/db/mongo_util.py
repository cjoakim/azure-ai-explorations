import json
import traceback

import certifi

from pymongo import MongoClient
from bson.objectid import ObjectId

# This class is used to access a MongoDB database such as
# Azure Cosmos DB vCore or MongoDB Atlas.
# TODO - refine, make more generic, and test
# Chris Joakim, 2025


class MongoUtil:
    
    def __init__(self, opts: dict):
        self._opts = opts
        self._db = None
        self._coll = None
        if "conn_string" in self._opts.keys():
            if "cosmos.azure.com" in opts["conn_string"]:
                self._env = "cosmos"
            else:
                self._env = "mongo"
            self._client = MongoClient(opts["conn_string"], tlsCAFile=certifi.where())
        else:
            if "cosmos.azure.com" in opts["host"]:
                self._env = "cosmos"
            else:
                self._env = "mongo"
            self._client = MongoClient(
                opts["host"], opts["port"], tlsCAFile=certifi.where()
            )

        if self.is_verbose():
            print(json.dumps(self._opts, sort_keys=False, indent=2))

    def is_verbose(self) -> bool:
        """Return True if the verbose option is set."""
        if "verbose" in self._opts.keys():
            return self._opts["verbose"]
        return False

    def list_databases(self) -> list[str]:
        """Return the list of database names in the account."""
        try:
            return sorted(self._client.list_database_names())
        except Exception as excp:
            print(str(excp))
            print(traceback.format_exc())
            return None

    def create_database(self, dbname):
        """Create a database with the given name."""
        return self._client[dbname]

    def delete_database(self, dbname):
        """Delete a database with the given name."""
        if dbname in "admin,local,config".split(","):
            return
        self._client.drop_database(dbname)

    def delete_container(self, cname):
        """Delete a container with the given name."""
        self._db.drop_collection(cname)

    def list_collections(self):
        """Return the list of collection names in the current database."""
        return self._db.list_collection_names(filter={"type": "collection"})

    def set_db(self, dbname):
        """Set the current database to the given name."""
        self._db = self._client[dbname]
        return self._db

    def set_coll(self, collname):
        """Set the current collection to the given name."""
        try:
            self._coll = self._db[collname]
            return self._coll
        except Exception as excp:
            print(str(excp))
            print(traceback.format_exc())
            return None

    def command_db_stats(self):
        """Execute the 'dbstats' command and return the results."""
        return self._db.command({"dbstats": 1})

    def command_coll_stats(self, cname):
        """Execute the 'collStats' command and return the results."""
        return self._db.command("collStats", cname)

    def command_list_commands(self):
        """Execute the 'listCommands' command and return the results."""
        return self._db.command("listCommands")

    def command_sharding_status(self):
        """Execute the 'printShardingStatus' command and return the results."""
        return self._db.command("printShardingStatus")

    def get_shards(self):
        """Return the list of shards in the cluster per the config database."""
        self.set_db("config")
        return self._db.shards.find()

    def extension_command_get_database(self):
        """Execute the 'getDatabase' command and return the results."""
        command = {}
        command["customAction"] = "GetDatabase"
        return self._db.command(command)

    def get_shard_info(self) -> dict:
        """Return a dict of shard info."""
        shard_dict = {}
        for shard in self._client.config.shards.find():
            shard_name = shard.get("_id")
            shard_dict[shard_name] = shard
        return shard_dict

    def create_coll(self, cname):
        """Create a collection with the given name in the current database."""
        return self._db[cname]

    def get_coll_indexes(self, collname) -> list | None:
        """Return the list of indexes for the given collection."""
        try:
            self.set_coll(collname)
            return self._coll.index_information()
        except Exception as excp:
            print(str(excp))
            print(traceback.format_exc())
            return None

    # crud methods below, metadata methods above

    def insert_doc(self, doc):
        """Insert a document into the current collection and return the result."""
        return self._coll.insert_one(doc)

    def find_one(self, query_spec):
        """
        Execute a find_one query in the current collection and return the result.
        """
        return self._coll.find_one(query_spec)

    def find(self, query_spec):
        """
        Execute a find query in the current collection and return the results.
        """
        return self._coll.find(query_spec)

    def find_by_id(self, id_str: str):
        """
        Execute a find_one query in the current collection, with the given id
        as a string, and return the results.
        """
        return self._coll.find_one({"_id": ObjectId(id_str)})

    def aggregate(self, pipeline):
        """Execute an aggregation pipeline in the current collection and return the results."""
        # https://pymongo.readthedocs.io/en/stable/examples/aggregation.html
        # https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/vcore/vector-search
        return self._coll.aggregate(pipeline)

    def delete_by_id(self, id_str: str):
        """Delete a document from the current collection by id and return the result."""
        return self._coll.delete_one({"_id": ObjectId(id_str)})

    def delete_one(self, query_spec):
        """Delete a document from the current collection and return the result."""
        return self._coll.delete_one(query_spec)

    def delete_many(self, query_spec):
        """Delete documents from the current collection and return the result."""
        return self._coll.delete_many(query_spec)

    def update_one(self, filter, update, upsert):
        """Update a document in the current collection and return the result."""
        return self._coll.update_one(filter, update, upsert)

    def update_many(self, filter, update, upsert):
        """Update documents in the current collection and return the result."""
        return self._coll.update_many(filter, update, upsert)

    def count_docs(self, query_spec):
        """
        Return the number of documents in the current collection
        that match the query spec.
        """
        return self._coll.count_documents(query_spec)

    def last_request_stats(self):
        """Return the last request statistics (Cosmos DB)."""
        return self._db.command({"getLastRequestStatistics": 1})

    def last_request_request_charge(self):
        """Return the last request charge in RUs (Cosmos DB)."""
        stats = self.last_request_stats()
        if stats is None:
            return -1
        return stats["RequestCharge"]

    def client(self):
        """Return the pymongo client object."""
        return self._client
