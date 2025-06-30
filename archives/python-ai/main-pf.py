"""
Usage:
  python main-pf.py <func>
  python main-pf.py chat_flow1
  python main-pf.py chat_flow1 --verbose
Options: 
  -h --help     Show this screen.
  --version     Show version.
"""
# main entry-point program for Prompt Flow examples.
# See https://microsoft.github.io/promptflow/how-to-guides/develop-a-prompty/index.html
# Chris Joakim, 2025 

import os
import sys
import traceback

from docopt import docopt
from dotenv import load_dotenv
from pathlib import Path

from urllib.parse import urlparse, parse_qs

from promptflow.tracing import trace

from promptflow.core import Prompty, AzureOpenAIModelConfiguration

BASE_DIR = Path(__file__).absolute().parent


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)

def chat_flow1():
    flowfile = "{}/flows/chat_flow1.prompty".format(BASE_DIR)
    if verbose():
        print(f"chat_flow1; flowfile: {flowfile}")

    config : AzureOpenAIModelConfiguration = build_aoai_model_config()
    override_model = {
        "configuration": config,
        "parameters": {"max_tokens": 512}
    }
    question = prompt_user("Enter a question for the LLM, hit enter to continue:")
    prompty_obj = Prompty.load(source=flowfile, model=override_model)
    result = prompty_obj(question=question)
    print(result)

def build_aoai_model_config() -> AzureOpenAIModelConfiguration:
    """
    Build and return an instance of class AzureOpenAIModelConfiguration
    by using AZURE_OPENAI_XXX environment variable values.
    """
    url = os.environ["AZURE_OPENAI_URL"]
    key = os.environ["AZURE_OPENAI_KEY"]
    dep = os.environ["AZURE_OPENAI_COMPLETIONS_MODEL"]
    url_with_version = os.environ["AZURE_OPENAI_COMPLETIONS_URL"]
    vers = parse_api_version(url_with_version)
    if verbose():
        print(f"build_aoai_model_config; url:  {url}")
        print(f"build_aoai_model_config; key:  {key[0:6]}...")  # Masking key for security
        print(f"build_aoai_model_config; dep:  {dep}")
        print(f"build_aoai_model_config; vers: {vers}")

    return AzureOpenAIModelConfiguration(
        azure_endpoint=url,
        api_key=key,
        azure_deployment=dep,
        api_version="2025-01-01-preview"
    )

def parse_api_version(url_string, default_value="2025-01-01-preview"):
    try:
        parsed_url = urlparse(url_string)
        query_params = parse_qs(parsed_url.query)
        if verbose():
            print(f"parse_api_version; parsed_url: {parsed_url}")
            print(f"parse_api_version; query_params: {query_params}")
        return query_params.get("api-version")[0]
    except Exception as e:
        print(f"parse_api_version; error: {e}")
        return default_value

def prompt_user(display_text):
    """ Prompt the user for their input, and return the input string. """
    print(display_text)
    user_input = input()
    return user_input

def verbose():
    return '--verbose' in sys.argv


if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        func = sys.argv[1].lower()
        if func == "chat_flow1":
            chat_flow1()
        else:
            print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
