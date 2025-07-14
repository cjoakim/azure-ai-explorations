"""
Usage:
  CLI app for Azure Storage.
  python main-adls-storage.py <func>
  python main-adls-storage.py env
  python main-adls-storage.py smoketest
"""

import os
import sys
import time
import tomllib
import traceback

from docopt import docopt
from dotenv import load_dotenv

from src.io.fs import FS
from src.io.adls_storage_util import AdlsStorageUtil
from src.os.env import Env


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    for name in sorted(os.environ.keys()):
        if name.startswith("AZURE_STORAGE_ADLS_"):
            print("{}: {}".format(name, os.environ[name]))
    print("username: {}".format(Env.username()))


def smoketest():
    print("===== AdlsStorageUtil constructor")
    storage_util = AdlsStorageUtil()
    time.sleep(1)
    if 1 > 0:
        return

    print("===== initial listing and deletion of smoketest containers")
    containers = storage_util.list_containers()
    print(f"Containers: {containers} {str(type(containers))}")
    for container in containers:
        if container.startswith("smoketest"):
            print(f"Deleting container: {container}")
            if storage_util.delete_container(container):
                print(f"Container '{container}' deleted successfully.")
            else:
                print(f"Container '{container}' does not exist or could not be deleted.")
        else:
            print(f"Retaining container: {container} (not a smoketest container)")
    time.sleep(1) 
    
    cname = "smoketest{}".format(int(Env.epoch()))
    print(f"New container name: {cname}")
    time.sleep(1)

    print("===== creating the container")
    created_container = storage_util.create_container(cname)
    if created_container:
        print(f"Container '{created_container}' created successfully.")
    else:
        print(f"Failed to create container '{cname}'.")
    time.sleep(1) 

    print("===== uploading pyproject.toml")
    metadata = {
        "description": "Sample pyproject.toml file for testing",
        "category": "smoketest",
        "file_size": "42"
    }
    result = storage_util.upload_file(
        cname, "pyproject.toml", metadata=metadata, replace=True)
    print(f"Upload result: {result}")
    time.sleep(1) 

    print("===== uploading readme.md")
    result = storage_util.upload_file(
        cname, "readme.md", replace=True)
    print(f"Upload result: {result}")
    time.sleep(1) 

    print("===== list containers")
    containers = storage_util.list_containers()
    print(f"Containers: {containers} {str(type(containers))}")
    FS.write_json(containers, "tmp/storage-containers.json", pretty=True, sort_keys=True)
    time.sleep(1) 

    print("===== list container, names_only: False")
    blobs = storage_util.list_container(cname, names_only=False)
    for b in blobs:
        print("---\nlist item: {}".format(b))
        for key in b.keys():
            print(f"  item key: {key}: {b[key]}")
    time.sleep(1)

    print("===== list container, names_only: True")
    blobs = storage_util.list_container(cname, names_only=True)
    print(f"Blobs in '{cname}': {blobs}")
    FS.write_json(blobs, "tmp/storage-blobs.json", pretty=True, sort_keys=True)
    time.sleep(1) 

    print("===== download_blob_to_file")
    result = storage_util.download_blob_to_file(
        cname, "pyproject.toml", "tmp/pyproject_downloaded.toml")
    print(f"Download result: {result}")
    print(f"Download result metadata: {result[1]["metadata"]}")
    time.sleep(1)

    print("===== download_blob_to_file")
    result = storage_util.download_blob_to_file(
        cname, "readme.md", "tmp/readme.md")
    print(f"Download result: {result}")
    time.sleep(1)

    print("===== tomllib.load() downloaded file")
    with open("tmp/pyproject_downloaded.toml", "rb") as f:
        data = tomllib.load(f)
    print(data)
    FS.write_json(data, "tmp/pyproject_downloaded.json", pretty=True, sort_keys=True)
    time.sleep(1)

    print("===== download_blob_as_string")
    txt = storage_util.download_blob_as_string(cname, "pyproject.toml")
    print(f"txt: \n{txt}\n{len(txt)}")
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
