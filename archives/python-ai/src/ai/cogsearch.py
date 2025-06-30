import json
import os
import sys
import time
import traceback

import httpx
import requests

from src.env import Env
from src.fs import FS

# This class is used to invoke Azure Cognitive Search via HTTP.
# TODO - refactor to use httpx and test
# Chris Joakim, 2025


class CogSearchClient:
    """
    This class is used to access an Azure Cognitive Search account
    via its REST API endpoints.
    """

    def __init__(self, opts):
        self.opts = opts
        self.user_agent = {"User-agent": "Mozilla/5.0"}
        # self.search_api_version = '2021-04-30-Preview'
        self.search_api_version = "2023-07-01-Preview"
        self.verbose = False

        try:
            self.search_name = opts["name"]
            self.search_url = opts["url"]
            self.search_admin_key = opts["admin_key"]
            self.search_query_key = opts["query_key"]
            if self.search_url.endswith("/"):
                self.search_url = self.search_url[:-1]
        except Exception as excp:
            print(str(excp))
            print(traceback.format_exc())

        self.u = None  # the current url
        self.r = None  # the current requests response object
        self.config = dict()

        self.admin_headers = dict()
        self.admin_headers["Content-Type"] = "application/json"
        self.admin_headers["api-key"] = self.search_admin_key

        self.query_headers = dict()
        self.query_headers["Content-Type"] = "application/json"
        self.query_headers["api-key"] = self.search_query_key

    def display_config(self):
        print("search_name:      {}".format(self.search_name))
        print("search_url:       {}".format(self.search_url))
        print("search_admin_key: {}".format(self.search_admin_key))
        print("search_query_key: {}".format(self.search_query_key))
        print(
            "admin_headers:\n{}".format(
                json.dumps(self.admin_headers, sort_keys=False, indent=2)
            )
        )
        print(
            "query_headers:\n{}".format(
                json.dumps(self.query_headers, sort_keys=False, indent=2)
            )
        )

    # API Invoking methods:

    def list_indexes(self):
        url = self.list_indexes_url()
        self.http_request("list_indexes", "get", url, self.admin_headers)

    def list_indexers(self):
        url = self.list_indexers_url()
        self.http_request("list_indexers", "get", url, self.admin_headers)

    def list_datasources(self):
        url = self.list_datasources_url()
        self.http_request("list_datasources", "get", url, self.admin_headers)

    def get_index(self, name):
        url = self.get_index_url(name)
        self.http_request("get_index", "get", url, self.admin_headers)

    def get_indexer(self, name):
        url = self.get_indexer_url(name)
        self.http_request("get_indexer", "get", url, self.admin_headers)

    def get_indexer_status(self, name):
        url = self.get_indexer_status_url(name)
        self.http_request("get_indexer_status", "get", url, self.admin_headers)

    def get_datasource(self, name):
        url = self.get_datasource_url(name)
        self.http_request("get_datasource", "get", url, self.admin_headers)

    def create_index(self, name, schema_file):
        self.modify_index("create", name, schema_file)

    def update_index(self, name, schema_file):
        self.modify_index("update", name, schema_file)

    def delete_index(self, name):
        self.modify_index("delete", name, None)

    def modify_index(self, action, name, schema_file):
        if self.verbose:
            print(f"modify_index {action} {name} {schema_file}")
        schema = None
        if action in ["create", "update"]:
            filename = f"schemas/{schema_file}"
            schema = FS.read_json(filename)

        if action == "create":
            http_method = "post"
            url = self.create_index_url()
        elif action == "update":
            http_method = "put"
            url = self.modify_index_url(name)
        elif action == "delete":
            http_method = "delete"
            url = self.modify_index_url(name)

        function = "{}_index_{}".format(action, name)
        self.http_request(function, http_method, url, self.admin_headers, schema)

    def create_indexer(self, name, schema_file):
        self.modify_indexer("create", name, schema_file)

    def update_indexer(self, name, schema_file):
        self.modify_indexer("update", name, schema_file)

    def delete_indexer(self, name):
        self.modify_indexer("delete", name, None)

    def modify_indexer(self, action, name, schema_file):
        # read the schema json file if necessary
        schema = None
        if action in ["create", "update"]:
            filename = f"schemas/{schema_file}"
            schema = FS.read_json(filename)

        if action == "create":
            http_method = "post"
            url = self.create_indexer_url()
        elif action == "update":
            http_method = "put"
            url = self.modify_indexer_url(name)
        elif action == "delete":
            http_method = "delete"
            url = self.modify_indexer_url(name)

        function = "{}_indexer_{}".format(action, name)
        self.http_request(function, http_method, url, self.admin_headers, schema)

    def reset_indexer(self, name):
        url = self.reset_indexer_url(name)
        self.http_request("reset_indexer", "post", url, self.admin_headers)

    def run_indexer(self, name):
        url = self.run_indexer_url(name)
        self.http_request("run_indexer", "post", url, self.admin_headers)

    def create_cosmos_nosql_datasource(
        self, acct_envvar, key_envvar, dbname, container
    ):
        acct = os.environ[acct_envvar]
        key = os.environ[key_envvar]
        conn_str = self.cosmos_nosql_datasource_name_conn_str(acct, key, dbname)
        body = self.cosmosdb_nosql_datasource_post_body()
        body["name"] = self.cosmos_nosql_datasource_name(dbname, container)
        body["credentials"]["connectionString"] = conn_str
        body["container"]["name"] = container
        body["dataDeletionDetectionPolicy"] = None
        body["encryptionKey"] = None
        body["identity"] = None

        url = self.create_datasource_url()
        function = "create_cosmos_nosql_datasource_{}_{}".format(dbname, container)
        self.http_request(function, "post", url, self.admin_headers, body)

    def delete_datasource(self, name):
        url = self.modify_datasource_url(name)
        function = "delete_datasource{}".format(name)
        self.http_request(function, "delete", url, self.admin_headers, None)

    def create_synmap(self, name, schema_file):
        self.modify_synmap("create", name, schema_file)

    def update_synmap(self, name, schema_file):
        self.modify_synmap("update", name, schema_file)

    def delete_synmap(self, name):
        self.modify_synmap("delete", name, None)

    def modify_synmap(self, action, name, schema_file):
        # read the schema json file if necessary
        schema = None
        if action in ["create", "update"]:
            schema_file = "schemas/{}.json".format(schema_file)
            schema = self.load_json_file(schema_file)
            schema["name"] = name

        if action == "create":
            http_method = "post"
            url = self.create_synmap_url()
        elif action == "update":
            http_method = "put"
            url = self.modify_synmap_url(name)
        elif action == "delete":
            http_method = "delete"
            url = self.modify_synmap_url(name)

        function = "{}_synmap_{}".format(action, name)
        self.http_request(function, http_method, url, self.admin_headers, schema)

    def search_index(self, idx_name, search_name, search_params):
        url = self.search_index_url(idx_name)
        if self.verbose:
            print("---")
            print(
                "search_index: {} {} -> {}".format(idx_name, search_name, search_params)
            )
            print("search_index url: {}".format(url))
            print("url:     {}".format(url))
            print("method:  {}".format("POST"))
            print("params:  {}".format(search_params))
            print("headers: {}".format(self.admin_headers))

        # Invoke the search via the HTTP API
        r = requests.post(url=url, headers=self.admin_headers, json=search_params)
        if self.verbose:
            print("response: {}".format(r))
        if r.status_code == 200:
            resp_obj = json.loads(r.text)
            outfile = "tmp/search_{}.json".format(search_name)
            self.write_json_file(resp_obj, outfile)
        return r

    def lookup_doc(self, index_name, doc_key):
        if self.verbose:
            print("lookup_doc: {} {}".format(index_name, doc_key))
        url = self.lookup_doc_url(index_name, doc_key)
        headers = self.query_headers
        function = "lookup_doc_{}_{}".format(index_name, doc_key)
        r = self.http_request(function, "get", url, self.query_headers)

    def http_request(self, function_name, method, url, headers={}, json_body={}):
        """
        This is a generic method which invokes ALL HTTP Requests to
        the Azure Search Service.
        """
        if self.verbose:
            print("===")
            print(
                "http_request: {} {} {}\nheaders: {}\nbody: {}".format(
                    function_name, method.upper(), url, headers, json_body
                )
            )
            print(
                "http_request name/method/url: {} {} {}".format(
                    function_name, method.upper(), url
                )
            )
            print(
                "http_request headers:\n{}".format(
                    json.dumps(headers, sort_keys=False, indent=2)
                )
            )
            print(
                "http_request body:\n{}".format(
                    json.dumps(json_body, sort_keys=False, indent=2)
                )
            )

        if self.no_http():
            return {}
        else:
            r = None
            if method == "get":
                r = requests.get(url=url, headers=headers)
            elif method == "post":
                r = requests.post(url=url, headers=headers, json=json_body)
            elif method == "put":
                r = requests.put(url=url, headers=headers, json=json_body)
            elif method == "delete":
                r = requests.delete(url=url, headers=headers)
            else:
                print(
                    "error; unexpected method value passed to invoke: {}".format(method)
                )
            if self.verbose:
                print("response: {}".format(r))
            if r.status_code < 300:
                try:
                    # Save the request and response data as a json file in tmp/
                    outfile = "tmp/{}_{}.json".format(function_name, int(self.epoch()))
                    data = dict()
                    data["function_name"] = function_name
                    data["method"] = method
                    data["url"] = url
                    data["body"] = json_body
                    data["filename"] = outfile
                    data["resp_status_code"] = r.status_code
                    try:
                        data["resp_obj"] = r.json()
                    except:
                        pass  # this is expected as some requests don't return a response, like http 204
                    self.write_json_file(data, outfile)
                except Exception as e:
                    print("exception saving http response".format(e))
                    print(traceback.format_exc())
            return r

    # Datasource Name methods:

    def blob_datasource_name(self, container):
        return "azureblob-{}".format(container)

    def cosmos_nosql_datasource_name(self, dbname, container):
        return "cosmosdb-nosql-{}-{}".format(dbname, container)

    def cosmos_nosql_datasource_name_conn_str(self, acct, key, dbname):
        # acct = os.environ['AZURE_COSMOSDB_NOSQL_ACCT']
        # key  = os.environ['AZURE_COSMOSDB_NOSQL_RO_KEY1']
        return "AccountEndpoint=https://{}.documents.azure.com;AccountKey={};Database={}".format(
            acct, key, dbname
        )

    def cosmos_nosql_datasource_name(self, dbname, container):
        return "cosmosdb-nosql-{}-{}".format(dbname, container)

    # URL methods below:

    def list_indexes_url(self):
        return "{}/indexes?api-version={}".format(
            self.search_url, self.search_api_version
        )

    def list_indexers_url(self):
        return "{}/indexers?api-version={}".format(
            self.search_url, self.search_api_version
        )

    def list_datasources_url(self):
        return "{}/datasources?api-version={}".format(
            self.search_url, self.search_api_version
        )

    def list_skillsets_url(self):
        return "{}/skillsets?api-version={}".format(
            self.search_url, self.search_api_version
        )

    def get_index_url(self, name):
        return "{}/indexes/{}?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def get_indexer_url(self, name):
        return "{}/indexers/{}?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def get_indexer_status_url(self, name):
        return "{}/indexers/{}/status?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def get_datasource_url(self, name):
        return "{}/datasources/{}?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def get_skillset_url(self, name):
        return "{}/skillsets/{}?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def create_index_url(self):
        return "{}/indexes?api-version={}".format(
            self.search_url, self.search_api_version
        )

    def modify_index_url(self, name):
        return "{}/indexes/{}?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def create_indexer_url(self):
        return "{}/indexers?api-version={}".format(
            self.search_url, self.search_api_version
        )

    def modify_indexer_url(self, name):
        return "{}/indexers/{}?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def reset_indexer_url(self, name):
        return "{}/indexers/{}/reset?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def run_indexer_url(self, name):
        return "{}/indexers/{}/run?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def create_datasource_url(self):
        return "{}/datasources?api-version={}".format(
            self.search_url, self.search_api_version
        )

    def modify_datasource_url(self, name):
        return "{}/datasources/{}?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def create_synmap_url(self):
        return "{}/synonymmaps?api-version={}".format(
            self.search_url, self.search_api_version
        )

    def modify_synmap_url(self, name):
        return "{}/synonymmaps/{}?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def create_skillset_url(self):
        return "{}/skillsets?api-version={}".format(
            self.search_url, self.search_api_version
        )

    def modify_skillset_url(self, name):
        return "{}/skillsets/{}?api-version={}".format(
            self.search_url, name, self.search_api_version
        )

    def search_index_url(self, idx_name):
        return "{}/indexes/{}/docs/search?api-version={}".format(
            self.search_url, idx_name, self.search_api_version
        )

    def lookup_doc_url(self, index_name, doc_key):
        return "{}/indexes/{}/docs/{}?api-version={}".format(
            self.search_url, index_name, doc_key, self.search_api_version
        )

    # Schema methods below:

    def blob_datasource_post_body(self):
        body = {
            "name": "... populate me ...",
            "type": "azureblob",
            "credentials": {"connectionString": "... populate me ..."},
            "container": {"name": "... populate me ..."},
        }
        return body

    def cosmosdb_nosql_datasource_post_body(self):
        schema = {
            "name": "... populate me ...",
            "type": "cosmosdb",
            "credentials": {"connectionString": "... populate me ..."},
            "container": {"name": "... populate me ...", "query": None},
            "dataChangeDetectionPolicy": {
                "@odata.type": "#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy",
                "highWaterMarkColumnName": "_ts",
            },
        }
        return schema

    def cosmosdb_nosql_datasource_post_body(self):
        schema = {
            "name": "... populate me ...",
            "type": "cosmosdb",
            "credentials": {"connectionString": "... populate me ..."},
            "container": {"name": "... populate me ...", "query": None},
            "dataChangeDetectionPolicy": {
                "@odata.type": "#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy",
                "highWaterMarkColumnName": "_ts",
            },
            "dataDeletionDetectionPolicy": "null",
            "encryptionKey": "null",
            "identity": "null",
        }
        return schema

    def indexer_schema(self, indexer_name, index_name, datasource_name):
        schema = {}
        schema["name"] = indexer_name
        schema["dataSourceName"] = datasource_name
        schema["targetIndexName"] = index_name
        schema["schedule"] = {"interval": "PT2H"}
        return schema

    # Other methods

    def epoch(self):
        return time.time()

    def no_http(self):
        for arg in sys.argv:
            if arg == "--no-http":
                return True
        return False

    def load_json_file(self, infile):
        with open(infile, "rt") as json_file:
            return json.loads(str(json_file.read()))

    def write_json_file(self, obj, outfile):
        with open(outfile, "wt") as f:
            f.write(json.dumps(obj, sort_keys=False, indent=2))
            print("file written: {}".format(outfile))
