"""
Usage:
  python main-sk.py <func>
  python main-sk.py init
"""

import asyncio
import json
import sys
import os
import traceback

from docopt import docopt
from dotenv import load_dotenv

from openai import AzureOpenAI

from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

from src.ai.sk_util import SKUtil
from src.io.fs import FS


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


async def init():
    await asyncio.sleep(0.1)
    opts = dict()
    opts["chat_DEP"] = os.getenv("AZURE_OPENAI_COMPLETIONS_DEP")
    opts["embeddings_DEP"] = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEP")
    
    plugins = list()
    sk = SKUtil(opts=opts, plugins=plugins, verbose=True)
    print(sk)



if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            if func == "init":
                asyncio.run(init())
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
