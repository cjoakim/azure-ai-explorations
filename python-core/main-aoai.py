"""
Usage:
  TODO  - implement samples with the Azure OpenAI SDK
  python main-aoai.py <func>
  python main-aoai.py explore
"""

# See https://github.com/Azure-Samples/openai
# See https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart?tabs=command-line%2Ckeyless%2Ctypescript-keyless%2Ckey&pivots=programming-language-python
# https://pypi.org/project/openai/
# https://github.com/openai/openai-python

import sys
import os
import traceback

from docopt import docopt
from dotenv import load_dotenv

from openai import AzureOpenAI

from src.io.fs import FS
from src.os.env import Env
from src.os.system import System
from src.util.counter import Counter


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def explore():
    url = os.environ.get("AZURE_OPENAI_URL")
    key = os.environ.get("AZURE_OPENAI_KEY")
    print("Azure OpenAI URL:", url)
    print("Azure OpenAI Key:", key)

    client = AzureOpenAI(
        api_key=key,  
        api_version="2024-10-21",
        azure_endpoint = url)
    print(str(type(client)))  # <class 'openai.lib.azure.AzureOpenAI'>
    print(client)

    try:
        models = client.models.list()
        for midx, model in enumerate(models.data):
            print(f"=== model {midx} {model.id}")
            print(model)
        print(f"Total models: {len(models.data)}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            if func == "explore":
                explore()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
