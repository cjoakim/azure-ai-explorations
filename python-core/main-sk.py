"""
Usage:
  python main-sk.py <func>
  python main-sk.py check_env
  python main-sk.py smoketest
  python main-sk.py run_semantic_function
Options: 
  -h --help     Show this screen.
  --version     Show version.
"""

# Entry-point program for Semantic Kernel API examples.
# Chris Joakim, 2025 

import asyncio
import logging
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

from src.ai.sk_util import SKUtil
from src.ai.sk.lights_plugin import LightsPlugin
from src.io.fs import FS


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


async def smoketest():
    completions_dep = os.getenv("AZURE_OPENAI_COMPLETIONS_DEP")
    embedding_dep = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEP")
    opts = dict()
    opts["chat_completion"] = completions_dep
    opts["text_embedding"] = embedding_dep
    opts["kernel_log_level"] = "DEBUG"
    builtin_plugins = list()
    custom_plugins = dict()
    custom_plugins["Lights"] = LightsPlugin()

    print("main generate_embedding opts: {}".format(opts))
    sk_util = SKUtil(opts, builtin_plugins, custom_plugins, True)
    sk_util.build_kernel()
    text = FS.read("../data/text/gettysburg-address.txt").strip()
    #await asyncio.sleep(3)

    embedding_array = await sk_util.generate_embedding(text, embedding_dep)
    print(str(type(embedding_array)))  # <class 'numpy.ndarray'>.
    if embedding_array is not None:
        print(len(embedding_array))
        FS.write_json(embedding_array, "tmp/embedding.json")

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
        elif func == "smoketest":
            asyncio.run(smoketest())
        elif func == "run_semantic_function":
            asyncio.run(run_semantic_function())
        else:
            print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
