import os

from azure.storage.filedatalake import DataLakeServiceClient

# This Python module defines a class `AdlsStorageUtil` that encapsulates operations 
# on Azure ADLS Gen2 Blob Storage using the `azure-storage-file-datalake` SDK.
# Each method includes error handling and logging, ensuring that any exceptions
# are caught and logged, and appropriate values are returned to indicate success or failure.
# See https://learn.microsoft.com/en-us/python/api/overview/azure/storage-file-datalake-readme
# Chris Joakim, 2025
# TODO: build out this class IF regular storage, and class StorageUtil in this repo,
#       is not sufficient for our needs

from typing import List
import logging


class AdlsStorageUtil:

    def __init__(self, logging_level=logging.INFO):
        self.account_name = os.getenv("AZURE_STORAGE_ADLS_ACCOUNT")
        self.account_url = f"https://{self.account_name}.dfs.core.windows.net/"
        account_key = os.getenv("AZURE_STORAGE_ADLS_KEY")
        print(f"AdlsStorageUtil#__init__ account_url: {self.account_url}")
        print(f"AdlsStorageUtil#__init__ account_key: {account_key}")

        self.service_client = DataLakeServiceClient(
            account_url=self.account_url,
            credential=account_key)
        
        if logging_level is not None:
            logging.basicConfig(level=logging.INFO)

    # def create_container(self, container_name: str) -> str:
    #     try:
    #         container_client = self.blob_service_client.create_container(container_name)
    #         logging.info(f"Container '{container_name}' created.")
    #         return container_name
    #     except Exception as e:
    #         logging.error(f"Failed to create container '{container_name}': {str(e)}")
    #         return None

    # def delete_container(self, container_name: str) -> bool:
    #     try:
    #         self.blob_service_client.delete_container(container_name)
    #         logging.info(f"Container '{container_name}' deleted.")
    #         return True
    #     except Exception as e:
    #         logging.error(f"Failed to delete container '{container_name}': {str(e)}")
    #         return False

    # def list_containers(self) -> List[str]:
    #     try:
    #         containers = self.blob_service_client.list_containers()
    #         container_names = [container.name for container in containers]
    #         logging.info("Containers listed.")
    #         return container_names
    #     except Exception as e:
    #         logging.error(f"Failed to list containers: {str(e)}")
    #         return []

    # def list_container(self, container_name: str, names_only: bool = True) -> List:
    #     try:
    #         container_client = self.blob_service_client.get_container_client(container_name)
    #         blob_list = container_client.list_blobs()
    #         if names_only:
    #             return [blob.name for blob in blob_list]
    #         else:
    #             return [self._filtered_list_metadata(blob) for blob in blob_list]
    #     except Exception as e:
    #         logging.error(f"Failed to list blobs in container '{container_name}': {str(e)}")
    #         return []

    # def upload_file(
    #         self,
    #         container_name: str,
    #         local_filename: str,
    #         metadata: dict | None = None,
    #         replace: bool = True) -> bool:
    #     return self.upload_file_as(
    #         container_name,
    #         local_filename,
    #         local_filename,
    #         metadata,
    #         replace)

    # def upload_file_as(
    #         self,
    #         container_name: str,
    #         container_blobname: str,
    #         local_filename: str,
    #         metadata: dict | None = None,
    #         replace: bool = True) -> bool:
    #     try:
    #         blob_client = self.blob_service_client.get_blob_client(
    #             container=container_name, blob=container_blobname)
    #         if blob_client.exists() and not replace:
    #             return False
    #         with open(local_filename, "rb") as data:
    #             blob_client.upload_blob(data, metadata=metadata, overwrite=replace)
    #         logging.info(f"Blob '{container_blobname}' uploaded to container '{container_name}'.")
    #         return True
    #     except Exception as e:
    #         logging.error(f"Failed to upload blob '{container_blobname}': {str(e)}")
    #         return False

    # def upload_string_as(
    #         self,
    #         container_name: str,
    #         container_blobname: str,
    #         content: str,
    #         metadata: dict | None = None,
    #         replace: bool = True) -> bool:
    #     try:
    #         blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=container_blobname)
    #         if not replace and blob_client.exists():
    #             logging.info(f"Blob '{container_blobname}' already exists and replace is False.")
    #             return False
    #         blob_client.upload_blob(content, metadata=metadata, overwrite=replace)
    #         logging.info(f"Blob '{container_blobname}' uploaded to container '{container_name}'.")
    #         return True
    #     except Exception as e:
    #         logging.error(f"Failed to upload blob '{container_blobname}': {str(e)}")
    #         return False
        
    # def download_blob_to_file(
    #         self,
    #         container_name: str,
    #         container_blobname: str,
    #         local_filename: str) -> tuple:
    #     try:
    #         blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=container_blobname)
    #         with open(local_filename, "wb") as download_file:
    #             download_file.write(blob_client.download_blob().readall())
    #         return (True, blob_client.get_blob_properties())
    #     except Exception as e:
    #         logging.error(f"Failed to download blob '{container_blobname}': {str(e)}")
    #         return (False, None)

    # def download_blob_as_string(self, container_name: str, container_blobname: str) -> str | None:
    #     try:
    #         blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=container_blobname)
    #         downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
    #         return downloader.readall()
    #     except Exception as e:
    #         logging.error(f"Failed to download blob '{container_blobname}': {str(e)}")
    #         return None
        
    # def delete_blob(self, container_name: str, container_blobname: str) -> bool:
    #     try:
    #         blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=container_blobname)
    #         blob_client.delete_blob()
    #         logging.info(f"Blob '{container_blobname}' deleted from container '{container_name}'.")
    #         return True
    #     except Exception as e:
    #         logging.error(f"Failed to delete blob '{container_blobname}': {str(e)}")
    #         return False
        
    # def _list_item_keys(self) -> List[str]:
    #     if self.list_item_keys is None:
    #         self.list_item_keys = "name,deleted,creation_time,etag,size".split(",")
    #     return self.list_item_keys
    
    # def _filtered_list_metadata(self, data: dict) -> dict:
    #     filtered = dict()
    #     for key in self._list_item_keys():
    #         if key in data:
    #             filtered[key] = str(data[key])
    #     return filtered 
    