"""
Usage:
  TODO  - implement samples with the azure-ai-projects SDK
  python main-foundry.py <func>
  python main-foundry.py explore
"""

import sys
import os
import traceback

from docopt import docopt
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def explore():
    # https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview?pivots=programming-language-python

    endpoint = os.environ.get("AZURE_FOUNDRY_PROJECT_URL")
    print(endpoint)
    project = AIProjectClient(
        endpoint="your_project_endpoint",  # Replace with your endpoint
        credential=DefaultAzureCredential(),
    )
    print(str(type(project)))  # <class 'azure.ai.projects._patch.AIProjectClient'>
    print(project)
    # print("Project ID:", project.project_id)


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
