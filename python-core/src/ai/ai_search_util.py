
import json
import os
import logging
import traceback

import httpx

# This class is used to invoke Azure AI Search via HTTP.
# Chris Joakim, 2025

class AISearchUtil:

    def __init__(self, verbose: bool = False):
        self.service_name = os.getenv("AZURE_AI_SEARCH_NAME")
        self.service_key = os.getenv("AZURE_AI_SEARCH_KEY")
        self.api_version = "2024-07-01"  # 2020-06-30
        self.base_url = f"https://{self.service_name}.search.windows.net/"
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.service_key
        }
        if verbose:
            print(f"AISearchUtil initialized; service_name: {self.service_name}")
            print(f"AISearchUtil initialized; service_key:  {self.service_key}")
            print(f"AISearchUtil initialized; api_version:  {self.api_version}")
            print(f"AISearchUtil initialized; base_url:     {self.base_url}")
            print(f"AISearchUtil initialized; headers:      {self.headers}")

    def _http_request(self, function_name: str, method: str, url: str, headers={}, json_body={}):
        try:
            with httpx.Client() as client:
                if headers is None:
                    headers = self.headers
                if headers == {}:
                    headers = self.headers
                response = client.request(method, url, headers=headers, json=json_body)
                print(f"response.status_code: {response.status_code}")
                data = dict()
                data["url"] = url
                data["method"] = method
                data["headers"] = headers
                data["status_code"] = response.status_code
                if response.content is not None:
                    data["content"] = response.json()
                return data
        except Exception as e:
            logging.error(f"Exception in {function_name}: {str(e)}")
            traceback.print_stack()
            return None

    # TODO - remove these getter methods; inline them where used instead

    def get_cosmos_nosql_datasource_conn_string(self, acct_name: str, key: str, database_name: str) -> str:
        return f"AccountName={acct_name};AccountKey={key};Database={database_name};"

    def get_cosmos_nosql_datasource_name(self, database_name: str, container_name: str) -> str:
        return f"{database_name}-{container_name}"

    def get_create_datasource_url(self) -> str:
        return f"{self.base_url}datasources?api-version={self.api_version}"

    def get_create_index_url(self) -> str:
        return f"{self.base_url}indexes?api-version={self.api_version}"

    def get_create_indexer_url(self) -> str:
        return f"{self.base_url}indexers?api-version={self.api_version}"

    def get_datasource_url(self, name: str) -> str:
        return f"{self.base_url}datasources/{name}?api-version={self.api_version}"

    def get_index_url(self, name: str) -> str:
        return f"{self.base_url}indexes/{name}?api-version={self.api_version}"

    def get_indexer_status_url(self, name: str) -> str:
        return f"{self.base_url}indexers/{name}/status?api-version={self.api_version}"

    def get_indexer_status(self, name: str) -> str:
        url = self.get_indexer_status_url(name)
        return self._http_request("get_indexer_status", "GET", url, headers=self.headers)

    def get_indexer_url(self, name: str) -> str:
        return f"{self.base_url}indexers/{name}?api-version={self.api_version}"

    def get_lookup_doc_url(self, index_name: str, doc_key: str) -> str:
        return f"{self.base_url}indexes/{index_name}/docs/{doc_key}?api-version={self.api_version}"

    def get_modify_datasource_url(self, name: str) -> str:
        return f"{self.base_url}datasources/{name}?api-version={self.api_version}"

    def get_modify_index_url(self, name: str) -> str:
        return f"{self.base_url}indexes/{name}?api-version={self.api_version}"

    def get_modify_indexer_url(self, name: str) -> str:
        return f"{self.base_url}indexers/{name}?api-version={self.api_version}"

    def get_run_indexer_url(self, name: str) -> str:
        return f"{self.base_url}indexers/{name}/run?api-version={self.api_version}"

    def get_search_index_url(self, idx_name: str) -> str:
        return f"{self.base_url}indexes/{idx_name}/docs/search?api-version={self.api_version}"

    def create_cosmos_nosql_datasource(self, database_name: str, container_name: str) -> dict | None:  # main
        try:
            base_conn_str = os.getenv("AZURE_COSMOSDB_NOSQL_CONN_STR")
            db_conn_str = f"{base_conn_str};Database={database_name};"
            datasource_definition = {
                "name": f"cosmosdb-nosql-{database_name}-{container_name}",
                "type": "cosmosdb",
                "credentials": {
                    "connectionString": db_conn_str
                },
                "container": {
                    "name": container_name,
                    "query": None
                },
                "dataChangeDetectionPolicy": {
                    "@odata.type": "#Microsoft.Azure.Search.HighWaterMarkChangeDetectionPolicy",
                    "highWaterMarkColumnName": "_ts"
                }
            }
            url = f"{self.base_url}/datasources?api-version={self.api_version}"
            return self._http_request(
                "create_cosmos_nosql_datasource", "POST", url, json_body=datasource_definition)
        except Exception as e:
            logging.error(f"Error in create_cosmos_nosql_datasource: {str(e)}")
            traceback.print_stack()
            return None

    def create_index(self, name, schema_json_filename: str) -> dict | None:  # main
        try:
            with open(schema_json_filename, 'r') as file:
                schema = json.load(file)
            schema["name"] = name  # override the name in the schema file
            url = f"{self.base_url}/indexes/{name}?api-version={self.api_version}"
            return self._http_request("create_index", "PUT", url, json_body=schema)
        except Exception as e:
            logging.error(f"Error in create_index: {str(e)}")
            traceback.print_stack()
            return False

    def create_indexer(self, name, schema_json_filename: str) -> dict | None:  # main
        try:
            with open(schema_json_filename, 'r') as file:
                schema = json.load(file)
            schema["name"] = name  # override the name in the schema file
            url = f"{self.base_url}/indexers/{name}?api-version={self.api_version}"
            return self._http_request("create_indexer", "PUT", url, json_body=schema)
        except Exception as e:
            logging.error(f"Error in create_indexer: {str(e)}")
            traceback.print_stack()
            return False

    def delete_datasource(self, name: str) -> bool:
        try:
            url = f"{self.base_url}/datasources/{name}?api-version={self.api_version}"
            return self._http_request("delete_datasource", "DELETE", url)
        except Exception as e:
            logging.error(f"Error in delete_datasource: {str(e)}")
            traceback.print_stack()
            return False

    def delete_index(self, name: str) -> bool:  # main
        try:
            url = f"{self.base_url}/indexes/{name}?api-version={self.api_version}"
            return self._http_request("delete_index", "DELETE", url)
        except Exception as e:
            logging.error(f"Error in delete_index: {str(e)}")
            traceback.print_stack()
            return False

    def delete_indexer(self, name: str) -> dict | None:  # main
        try:
            url = f"{self.base_url}/indexers/{name}?api-version={self.api_version}"
            return self._http_request("delete_indexer", "DELETE", url)
        except Exception as e:
            logging.error(f"Error in delete_indexer: {str(e)}")
            traceback.print_stack()
            return None

    def list_datasources(self) -> dict | None:  # main
        try:
            url = f"{self.base_url}datasources?api-version={self.api_version}"
            return self._http_request("list_datasources", "GET", url)
        except Exception as e:
            logging.error(f"Error in list_datasources: {str(e)}")
            traceback.print_stack()
            return None

    def list_indexers(self) -> dict | None:  # main
        try:
            url = f"{self.base_url}indexers?api-version={self.api_version}"
            return self._http_request("list_indexers", "GET", url)
        except Exception as e:
            logging.error(f"Error in list_indexers: {str(e)}")
            traceback.print_stack()
            return 

    def list_indexes(self) -> dict | None:  # main
        try:
            url = f"{self.base_url}indexes?api-version={self.api_version}"
            return self._http_request("list_indexes", "GET", url)
        except Exception as e:
            logging.error(f"Error in list_indexes: {str(e)}")
            traceback.print_stack()
            return []

    def lookup_datasource(self, name: str):
        try:
            url = f"{self.base_url}/datasources/{name}?api-version={self.api_version}"
            return self._http_request("lookup_datasource", "GET", url)
        except Exception as e:
            logging.error(f"Error in lookup_datasource: {str(e)}")
            traceback.print_stack()
            return None

    def lookup_doc(self, index_name: str, doc_key: str):
        try:
            url = f"{self.base_url}/indexes/{index_name}/docs/{doc_key}?api-version={self.api_version}"
            return self._http_request("lookup_doc", "GET", url)
        except Exception as e:
            logging.error(f"Error in lookup_doc: {str(e)}")
            traceback.print_stack()
            return None

    def lookup_index(self, name: str):
        try:
            url = f"{self.base_url}/indexes/{name}?api-version={self.api_version}"
            return self._http_request("lookup_index", "GET", url)
        except Exception as e:
            logging.error(f"Error in lookup_index: {str(e)}")
            traceback.print_stack()
            return None

    def lookup_indexer_schema(self, indexer_name: str, index_name: str, datasource_name: str):
        try:
            indexer = self.lookup_indexer(indexer_name)
            index = self.lookup_index(index_name)
            datasource = self.lookup_datasource(datasource_name)
            return {
                "indexer": indexer,
                "index": index,
                "datasource": datasource
            }
        except Exception as e:
            logging.error(f"Error in lookup_indexer_schema: {str(e)}")
            traceback.print_stack()
            return None

    def lookup_indexer(self, name: str):
        try:
            url = f"{self.base_url}/indexers/{name}?api-version={self.api_version}"
            return self._http_request("lookup_indexer", "GET", url)
        except Exception as e:
            logging.error(f"Error in lookup_indexer: {str(e)}")
            traceback.print_stack()
            return None

    def modify_index(self, action, name: str, schema_json_filename: str):
        try:
            with open(schema_json_filename, 'r') as file:
                schema = json.load(file)
            url = f"{self.base_url}/indexes/{name}?api-version={self.api_version}"
            return self._http_request("modify_index", action, url, json_body=schema)
        except Exception as e:
            logging.error(f"Error in modify_index: {str(e)}")
            traceback.print_stack()
            return None

    def modify_indexer(self, action: str, name: str, schema_json_filename: str):
        try:
            with open(schema_json_filename, 'r') as file:
                schema = json.load(file)
            url = f"{self.base_url}/indexers/{name}?api-version={self.api_version}"
            return self._http_request("modify_indexer", action, url, json_body=schema)
        except Exception as e:
            logging.error(f"Error in modify_indexer: {str(e)}")
            traceback.print_stack()
            return None

    def reset_indexer_url(self, name: str) -> str:
        try:
            url = f"{self.base_url}/indexers/{name}/reset?api-version={self.api_version}"
            result = self._http_request("reset_indexer_url", "POST", url)
            return url if result else ""
        except Exception as e:
            logging.error(f"Error in reset_indexer_url: {str(e)}")
            traceback.print_stack()
            return ""

    def reset_indexer(self, name: str) -> str:
        try:
            url = f"{self.base_url}/indexers/{name}/reset?api-version={self.api_version}"
            result = self._http_request("reset_indexer", "POST", url)
            return "Reset successful" if result else "Reset failed"
        except Exception as e:
            logging.error(f"Error in reset_indexer: {str(e)}")
            traceback.print_stack()
            return "Reset failed"

    def run_indexer(self, name: str) -> bool:
        try:
            url = f"{self.base_url}/indexers/{name}/run?api-version={self.api_version}"
            result = self._http_request("run_indexer", "POST", url)
            return result is not None
        except Exception as e:
            logging.error(f"Error in run_indexer: {str(e)}")
            traceback.print_stack()
            return False

    def search_index(self, idx_name: str, search_name: str, search_params: object) -> list[object] | None:
        try:
            url = f"{self.base_url}/indexes/{idx_name}/docs/search?api-version={self.api_version}"
            search_body = {
                "search": search_name,
                **search_params
            }
            result = self._http_request("search_index", "POST", url, json_body=search_body)
            return result['value'] if result else None
        except Exception as e:
            logging.error(f"Error in search_index: {str(e)}")
            traceback.print_stack()
            return None

    def update_index(self, name, schema_json_filename: str) -> bool:
        return self.modify_index("PUT", name, schema_json_filename)

    def update_indexer(self, name, schema_json_filename: str) -> bool:
        return self.modify_indexer("PUT", name, schema_json_filename)
    
