"""
Usage:
  python main-sk.py <func>
  python main-sk.py check_env
  python main-sk.py generate_embedding
  python main-sk.py run_semantic_function
Options: 
  -h --help     Show this screen.
  --version     Show version.
"""

# main entry-point program for Semantic Kernel API examples.
# Chris Joakim, 2025 

import asyncio
import os
import sys
import traceback

import tiktoken

from docopt import docopt
from dotenv import load_dotenv

from openai import AzureOpenAI

import semantic_kernel as sk

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from enum import Enum
from typing import Literal

from semantic_kernel.kernel_pydantic import KernelBaseSettings

from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding, OpenAIEmbeddingPromptExecutionSettings

from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureTextEmbedding,
    OpenAITextPromptExecutionSettings,
)
from semantic_kernel.functions.kernel_arguments import (
    KernelArguments,
)
from semantic_kernel.prompt_template import (
    PromptTemplateConfig,
    InputVariable,
)

from src.io.fs import FS


class Service(Enum):
    # This class was copied from
    # https://github.com/microsoft/semantic-kernel/blob/main/python/samples/getting_started/services.py
    """
    Attributes:
    OpenAI (str): Represents the OpenAI service.
    AzureOpenAI (str): Represents the Azure OpenAI service.
    HuggingFace (str): Represents the HuggingFace service.
    """
    OpenAI = "openai"
    AzureOpenAI = "azureopenai"
    HuggingFace = "huggingface"

class ServiceSettings(KernelBaseSettings):
    # This class was copied from
    # https://github.com/microsoft/semantic-kernel/blob/main/python/samples/service_settings.py
    """
    The Learn Resources Service Settings.
    The settings are first loaded from environment variables. If the
    environment variables are not found, the settings can be loaded from a .env file with the
    encoding 'utf-8' as default or the specific encoding. If the settings are not found in the
    .env file, the settings are ignored; however, validation will fail alerting that the settings
    are missing.
    Args:
        global_llm_service: The LLM service to use for the samples, either "OpenAI" or "AzureOpenAI"
            If not provided, defaults to "AzureOpenAI".
    """

    global_llm_service: Literal["OpenAI", "AzureOpenAI"] = "AzureOpenAI"


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    for name in sorted(os.environ.keys()):
        print_this = False
        if "AZURE" in name:
            print_this = True
        if "_OPENAI_" in name:
            print_this = True
        if print_this:
            print("{}: {}".format(name, os.environ[name]))


async def generate_embedding():
    # https://github.com/microsoft/semantic-kernel/tree/main/python/samples
    # https://learn.microsoft.com/en-us/python/api/semantic-kernel/semantic_kernel
    # https://learn.microsoft.com/en-us/python/api/semantic-kernel/semantic_kernel.connectors.ai.open_ai.services.azure_text_embedding.azuretextembedding
    kernel = Kernel()
    url = os.environ["AZURE_OPENAI_URL"]
    key = os.environ["AZURE_OPENAI_KEY"]
    dep = os.environ["AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"]
    text = FS.read("../data/misc/gettysburg-address.txt").strip()

    embedding_service = AzureTextEmbedding(
        api_key=key, endpoint=url, deployment_name=dep)
    embedding = await embedding_service.generate_embeddings(text)

    print(str(type(embedding)))  # <class 'numpy.ndarray'>.
    print(str(type(embedding[0])))
    print(embedding[0].shape)  # (1536,)
    array = embedding[0].tolist()
    FS.write_json(array, "tmp/embedding.json")
    return array

async def run_semantic_function():
    # This method was adapted from the SK sample at:
    # https://github.com/microsoft/semantic-kernel/blob/main/python/samples/getting_started/00-getting-started.ipynb
    await asyncio.sleep(0.1)
    kernel = Kernel()
    kernel.remove_all_services()
    print(str(type(kernel)))  # <class 'semantic_kernel.kernel.Kernel'>
    print(kernel)

    service_settings = ServiceSettings()
    print(f"service_settings: {service_settings}")

    # Select a service to use for this notebook (available services: OpenAI, AzureOpenAI, HuggingFace)
    selectedService = (
        Service.AzureOpenAI
        if service_settings.global_llm_service is None
        else Service(service_settings.global_llm_service.lower())
    )
    print(f"Using service type: {selectedService}")

    service_id = None
    if selectedService == Service.OpenAI:
        service_id = "default"
        kernel.add_service(
            OpenAIChatCompletion(
                service_id=service_id,
            ),
        )
    elif selectedService == Service.AzureOpenAI:
        service_id = "default"
        kernel.add_service(
            AzureChatCompletion(
                service_id=service_id,
            ),
        )

    plugin = kernel.add_plugin(parent_directory="sk_plugins/", plugin_name="FunPlugin")
    print(f"plugin: {plugin}")

    joke_function = plugin["Joke"]

    joke = await kernel.invoke(
        joke_function,
        KernelArguments(input="time travel to dinosaur age", style="super silly"),
    )
    print(joke)

def text_summarization_md():
    return """
## Purpose

You are a helpful assistant who summarizes text.

Summarize the following text into bullet points.

"""


def gettysburg_address_user_md():
    text = FS.read("../data/text/gettysburg_address.txt").strip()
    return """
## Text to summarize

{}

""".format(
        text
    ).lstrip()


def industrial_disease_lyrics_md():
    text = FS.read("../data/misc/industrial_disease_lyrics.txt").strip()
    return """
## Text to summarize

{}

""".format(
        text
    ).lstrip()


if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        func = sys.argv[1].lower()
        if func == "check_env":
            check_env()
        elif func == "generate_embedding":
            asyncio.run(generate_embedding())
        elif func == "run_semantic_function":
            asyncio.run(run_semantic_function())
        else:
            print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
