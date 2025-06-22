from azure.storage.blob import BlobServiceClient
# from azure.storage.blob import BlobClient
# from azure.storage.blob import ContainerClient


class BlobUtil:
    def __init__(self, connection_string):
        self.client = BlobServiceClient.from_connection_string(connection_string)

    def create_container(self, container_name):
        try:
            container_client = self.client.create_container(container_name)
            print(f"Container '{container_name}' created successfully.")
            return container_client
        except Exception as e:
            print(f"Failed to create container '{container_name}': {e}")

    def delete_container(self, container_name):
        try:
            self.client.delete_container(container_name)
            print(f"Container '{container_name}' deleted successfully.")
        except Exception as e:
            print(f"Failed to delete container '{container_name}': {e}")

    def list_containers(self, recursive=False):
        try:
            containers = self.client.list_containers()
            for container in containers:
                print(f"Container Name: {container.name}")
                if recursive:
                    self.list_container(container.name, recursive=True)
        except Exception as e:
            print(f"Failed to list containers: {e}")

    def list_container(self, container_name, recursive=False):
        try:
            container_client = self.client.get_container_client(container_name)
            blobs = container_client.list_blobs()
            for blob in blobs:
                print(f"Blob Name: {blob.name}")
                if recursive:
                    # Recursive listing is not applicable for blobs, only for containers
                    pass
        except Exception as e:
            print(f"Failed to list blobs in container '{container_name}': {e}")

    def upload_blob(self, container_name, local_filename, replace=True):
        blob_name = local_filename.split('/')[-1]
        self.upload_blob_as(container_name, blob_name, local_filename, replace)

    def upload_blob_as(self, container_name, container_blobname, local_filename, replace=True):
        try:
            blob_client = self.client.get_blob_client(container=container_name, blob=container_blobname)
            if replace or not blob_client.exists():
                with open(local_filename, "rb") as data:
                    blob_client.upload_blob(data, overwrite=replace)
                print(f"File '{local_filename}' uploaded as '{container_blobname}' in container '{container_name}'.")
            else:
                print(f"Blob '{container_blobname}' already exists in container '{container_name}'.")
        except Exception as e:
            print(f"Failed to upload blob: {e}")

    def download_blob(self, container_name, container_blobname, local_filename):
        try:
            blob_client = self.client.get_blob_client(container=container_name, blob=container_blobname)
            with open(local_filename, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            print(f"Blob '{container_blobname}' downloaded to '{local_filename}'.")
        except Exception as e:
            print(f"Failed to download blob '{container_blobname}': {e}")

    def delete_blob(self, container_name, container_blobname):
        try:
            blob_client = self.client.get_blob_client(container=container_name, blob=container_blobname)
            blob_client.delete_blob()
            print(f"Blob '{container_blobname}' deleted from container '{container_name}'.")
        except Exception as e:
            print(f"Failed to delete blob '{container_blobname}': {e}")
