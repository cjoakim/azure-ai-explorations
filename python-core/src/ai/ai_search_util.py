import httpx
import json
import os

# This class is used to invoke Azure AI Search via HTTP.
# Chris Joakim, 2025

class AISearchUtil:
    def __init__(self, service_name, admin_key):
        self.service_name = service_name
        self.admin_key = admin_key
        self.base_url = f"https://{service_name}.search.windows.net"
        self.api_version = "2020-06-30"
        self.headers = {
            'Content-Type': 'application/json',
            'api-key': admin_key
        }

    def cosmos_nosql_datasource_name_conn_str(self, acct, key, database_name):
        return f"AccountEndpoint=https://{acct}.documents.azure.com:443/;AccountKey={key};Database={database_name}"

    def cosmos_nosql_datasource_name(self, database_name, container_name):
        return f"cosmosdb-{database_name}-{container_name}"

    def create_cosmos_nosql_datasource(self, acct_envvar, key_envvar, database_name, container_name):
        connection_string = self.cosmos_nosql_datasource_name_conn_str(os.getenv(acct_envvar), os.getenv(key_envvar), database_name)
        datasource_name = self.cosmos_nosql_datasource_name(database_name, container_name)
        return {
            "name": datasource_name,
            "type": "cosmosdb",
            "credentials": {"connectionString": connection_string},
            "container": {"name": container_name, "query": None}
        }

    def create_datasource_url(self):
        return f"{self.base_url}/datasources?api-version={self.api_version}"

    def create_index_url(self):
        return f"{self.base_url}/indexes?api-version={self.api_version}"

    def create_index(self, name, schema_json_file):
        with open(schema_json_file, 'r') as file:
            schema = json.load(file)
        url = self.create_index_url()
        return self.http_request("create_index", "POST", url, json_body=schema)

    def create_indexer_url(self):
        return f"{self.base_url}/indexers?api-version={self.api_version}"

    def create_indexer(self, name, schema_json_file):
        with open(schema_json_file, 'r') as file:
            schema = json.load(file)
        url = self.create_indexer_url()
        return self.http_request("create_indexer", "POST", url, json_body=schema)

    def delete_datasource(self, name):
        url = f"{self.base_url}/datasources/{name}?api-version={self.api_version}"
        return self.http_request("delete_datasource", "DELETE", url)

    def delete_index(self, name):
        url = f"{self.base_url}/indexes/{name}?api-version={self.api_version}"
        return self.http_request("delete_index", "DELETE", url)

    def delete_indexer(self, name):
        url = f"{self.base_url}/indexers/{name}?api-version={self.api_version}"
        return self.http_request("delete_indexer", "DELETE", url)

    def get_datasource_url(self, name):
        return f"{self.base_url}/datasources/{name}?api-version={self.api_version}"

    def get_datasource(self, name):
        url = self.get_datasource_url(name)
        return self.http_request("get_datasource", "GET", url)

    def get_index_url(self, name):
        return f"{self.base_url}/indexes/{name}?api-version={self.api_version}"

    def get_index(self, name):
        url = self.get_index_url(name)
        return self.http_request("get_index", "GET", url)

    def get_indexer_status_url(self, name):
        return f"{self.base_url}/indexers/{name}/status?api-version={self.api_version}"

    def get_indexer_status(self, name):
        url = self.get_indexer_status_url(name)
        return self.http_request("get_indexer_status", "GET", url)

    def get_indexer_url(self, name):
        return f"{self.base_url}/indexers/{name}?api-version={self.api_version}"

    def get_indexer(self, name):
        url = self.get_indexer_url(name)
        return self.http_request("get_indexer", "GET", url)

    def http_request(self, function_name, method, url, headers={}, json_body={}):
        if not headers:
            headers = self.headers
        with httpx.Client() as client:
            response = client.request(method, url, headers=headers, json=json_body)
        return response.json()

    def indexer_schema(self, indexer_name, index_name, datasource_name):
        return {
            "name": indexer_name,
            "dataSourceName": datasource_name,
            "targetIndexName": index_name,
            "schedule": {"interval": "PT2H"}
        }

    def list_datasources_url(self):
        return f"{self.base_url}/datasources?api-version={self.api_version}"

    def list_datasources(self):
        url = self.list_datasources_url()
        return self.http_request("list_datasources", "GET", url)

    def list_indexers_url(self):
        return f"{self.base_url}/indexers?api-version={self.api_version}"

    def list_indexers(self):
        url = self.list_indexers_url()
        return self.http_request("list_indexers", "GET", url)

    def list_indexes_url(self):
        return f"{self.base_url}/indexes?api-version={self.api_version}"

    def list_indexes(self):
        url = self.list_indexes_url()
        return self.http_request("list_indexes", "GET", url)

    def lookup_doc_url(self, index_name, doc_key):
        return f"{self.base_url}/indexes/{index_name}/docs/{doc_key}?api-version={self.api_version}"

    def lookup_doc(self, index_name, doc_key):
        url = self.lookup_doc_url(index_name, doc_key)
        return self.http_request("lookup_doc", "GET", url)

    def modify_datasource_url(self, name):
        return f"{self.base_url}/datasources/{name}?api-version={self.api_version}"

    def modify_index_url(self, name):
        return f"{self.base_url}/indexes/{name}?api-version={self.api_version}"

    def modify_index(self, action, name, schema_json_file):
        url = self.modify_index_url(name)
        with open(schema_json_file, 'r') as file:
            schema = json.load(file)
        return self.http_request(f"modify_index_{action}", "PUT", url, json_body=schema)

    def modify_indexer_url(self, name):
        return f"{self.base_url}/indexers/{name}?api-version={self.api_version}"

    def modify_indexer(self, action, name, schema_json_file):
        url = self.modify_indexer_url(name)
        with open(schema_json_file, 'r') as file:
            schema = json.load(file)
        return self.http_request(f"modify_indexer_{action}", "PUT", url, json_body=schema)

    def reset_indexer_url(self, name):
        return f"{self.base_url}/indexers/{name}/reset?api-version={self.api_version}"

    def reset_indexer(self, name):
        url = self.reset_indexer_url(name)
        return self.http_request("reset_indexer", "POST", url)

    def run_indexer_url(self, name):
        return f"{self.base_url}/indexers/{name}/run?api-version={self.api_version}"

    def run_indexer(self, name):
        url = self.run_indexer_url(name)
        return self.http_request("run_indexer", "POST", url)

    def search_index_url(self, idx_name):
        return f"{self.base_url}/indexes/{idx_name}/docs/search?api-version={self.api_version}"

    def search_index(self, idx_name, search_text, search_params={}):
        url = self.search_index_url(idx_name)
        body = {"search": search_text, **search_params}
        return self.http_request("search_index", "POST", url, json_body=body)

    def update_index(self, name, schema_json_file):
        return self.modify_index("update", name, schema_json_file)

    def update_indexer(self, name, schema_json_file):
        return self.modify_indexer("update", name, schema_json_file)
