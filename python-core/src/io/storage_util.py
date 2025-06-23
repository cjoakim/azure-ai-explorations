import os

from azure.storage.blob import BlobServiceClient
# from azure.storage.blob import BlobClient
# from azure.storage.blob import ContainerClient

# This Python module defines a class `StorageUtil` that encapsulates operations 
# on Azure Blob Storage using the `azure-storage-blob` SDK.  Each method includes  
# error handling and logging, ensuring that any exceptions are caught and logged, 
# and appropriate values are returned to indicate success or failure.
# Chris Joakim, 2025

from typing import List
import logging


class StorageUtil:

    def __init__(self, connection_string: str, logging_level=logging.INFO):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        if logging_level is not None:
            logging.basicConfig(level=logging.INFO)

    def create_container(self, container_name: str) -> str:
        try:
            container_client = self.blob_service_client.create_container(container_name)
            logging.info(f"Container '{container_name}' created.")
            return container_name
        except Exception as e:
            logging.error(f"Failed to create container '{container_name}': {str(e)}")
            return None

    def delete_container(self, container_name: str) -> bool:
        try:
            self.blob_service_client.delete_container(container_name)
            logging.info(f"Container '{container_name}' deleted.")
            return True
        except Exception as e:
            logging.error(f"Failed to delete container '{container_name}': {str(e)}")
            return False

    def list_containers(self, recursive: bool = False) -> List[str]:
        try:
            containers = self.blob_service_client.list_containers()
            container_names = [container.name for container in containers]
            logging.info("Containers listed.")
            return container_names
        except Exception as e:
            logging.error(f"Failed to list containers: {str(e)}")
            return []

    def list_container(self, container_name: str, recursive: bool = False) -> List[str]:
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            blob_list = container_client.list_blobs()
            blobs = [blob.name for blob in blob_list]
            logging.info(f"Blobs in container '{container_name}' listed.")
            return blobs
        except Exception as e:
            logging.error(f"Failed to list blobs in container '{container_name}': {str(e)}")
            return []

    def upload_blob(self, container_name: str, local_filename: str, replace: bool = True) -> bool:
        return self.upload_blob_as(container_name, local_filename, local_filename, replace)

    def upload_blob_as(self, container_name: str, container_blobname: str, local_filename: str, replace: bool = True) -> bool:
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=container_blobname)
            if not replace and blob_client.exists():
                logging.info(f"Blob '{container_blobname}' already exists and replace is False.")
                return False
            with open(local_filename, "rb") as data:
                blob_client.upload_blob(data, overwrite=replace)
            logging.info(f"Blob '{container_blobname}' uploaded to container '{container_name}'.")
            return True
        except Exception as e:
            logging.error(f"Failed to upload blob '{container_blobname}': {str(e)}")
            return False

    def download_blob(self, container_name: str, container_blobname: str, local_filename: str) -> bool:
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=container_blobname)
            with open(local_filename, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            logging.info(f"Blob '{container_blobname}' downloaded to '{local_filename}'.")
            return True
        except Exception as e:
            logging.error(f"Failed to download blob '{container_blobname}': {str(e)}")
            return False

    def delete_blob(self, container_name: str, container_blobname: str) -> bool:
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=container_blobname)
            blob_client.delete_blob()
            logging.info(f"Blob '{container_blobname}' deleted from container '{container_name}'.")
            return True
        except Exception as e:
            logging.error(f"Failed to delete blob '{container_blobname}': {str(e)}")
            return False
        