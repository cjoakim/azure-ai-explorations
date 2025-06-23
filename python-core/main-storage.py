"""
Usage:
  CLI app for Azure Storage.
  python main_storage.py <func>
  python main_storage.py env
  python main_storage.py smoketest
"""

import os
import sys
import time
import tomllib
import traceback

from docopt import docopt
from dotenv import load_dotenv

from src.io.fs import FS
from src.io.storage_util import StorageUtil
from src.os.env import Env


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    for name in sorted(os.environ.keys()):
        if name.startswith("AZURE_"):
            if "PERSONAL" in name:
                pass
            else:
                print("{}: {}".format(name, os.environ[name]))
    print("username: {}".format(Env.username()))


def smoketest():
    connection_string = os.getenv("AZURE_STORAGE_CONN_STRING")
    if not connection_string:
        print("Error: AZURE_STORAGE_CONN_STRING is not set in the environment.")
        return
    print("Connection string: {}...".format(connection_string))

    print("===== StorageUtil constructor")
    storage_util = StorageUtil(connection_string, logging_level=None)
    time.sleep(1) 

    container_name = "smoketest{}".format(int(Env.epoch()))
    print(f"Container name: {container_name}")
    time.sleep(1)

    print("===== deleting the container")
    if storage_util.delete_container(container_name):
        print(f"Container '{container_name}' deleted successfully.")
    else:
        print(f"Container '{container_name}' does not exist or could not be deleted.")
    time.sleep(1) 

    print("===== creating the container")
    created_container = storage_util.create_container(container_name)
    if created_container:
        print(f"Container '{created_container}' created successfully.")
    else:
        print(f"Failed to create container '{container_name}'.")
    time.sleep(1) 

    print("===== uploading pyproject.toml")
    result = storage_util.upload_blob(container_name, "pyproject.toml", replace=True)
    print(f"Upload result: {result}")
    time.sleep(1) 

    print("===== uploading readme.md")
    result = storage_util.upload_blob(container_name, "readme.md", replace=True)
    print(f"Upload result: {result}")
    time.sleep(1) 

    print("===== list containers")
    containers = storage_util.list_containers()
    print(f"Containers: {containers} {str(type(containers))}")
    FS.write_json(containers, "tmp/storage-containers.json", pretty=True, sort_keys=True)
    time.sleep(1) 

    print("===== list container, not recursive")
    blobs = storage_util.list_container(container_name, recursive=False)
    print(f"Blobs in '{container_name}': {blobs}")
    time.sleep(1) 

    print("===== list container, recursive")
    blobs = storage_util.list_container(container_name, recursive=True)
    print(f"Blobs in '{container_name}': {blobs}")
    FS.write_json(blobs, "tmp/storage-blobs.json", pretty=True, sort_keys=True)
    time.sleep(1) 

    print("===== download_blob_to_file")
    result = storage_util.download_blob_to_file(
        container_name, "pyproject.toml", "tmp/pyproject_downloaded.toml")
    print(f"Download result: {result}")
    time.sleep(1)

    print("===== tomllib.load() downloaded file")
    with open("tmp/pyproject_downloaded.toml", "rb") as f:
        data = tomllib.load(f)
    print(data)
    FS.write_json(data, "tmp/pyproject_downloaded.json", pretty=True, sort_keys=True)
    time.sleep(1)

    print("===== download_blob_as_string")
    txt = storage_util.download_blob_as_string(container_name, "pyproject.toml")
    print(f"txt: \n{txt}")
    time.sleep(1) 


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            load_dotenv(override=True)
            func = sys.argv[1].lower()
            if func == "env":
                check_env()
            elif func == "smoketest":
                smoketest()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
