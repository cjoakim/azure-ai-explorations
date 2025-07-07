"""
Usage:
    CLI app for Azure AI Search.
    -
    python main-langsvc.py <func>
    python main-langsvc.py explore
"""

import json
import os
import sys
import traceback

from docopt import docopt
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

from src.io.fs import FS
from src.os.env import Env


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    for name in sorted(os.environ.keys()):
        if name.startswith("AZURE_AI_SEARCH"):
            print("{}: {}".format(name, os.environ[name]))

def explore():
    ta_client = build_client() 
    print("TTextAnalyticsClient: {}".format(ta_client))


def build_client():
    url = os.getenv("AZURE_LANGSERVICE_URL", None)
    key = os.getenv("AZURE_LANGSERVICE_KEY", None)
    print("build_client url: {}".format(url))
    print("build_client key: {}".format(key))
    return TextAnalyticsClient(
        endpoint=url, credential=AzureKeyCredential(key))



if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            print("=== CLI function: {}".format(func))

            if func == "explore":
                explore()
            elif func == "explore2":
                explore()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
