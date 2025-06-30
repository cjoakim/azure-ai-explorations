import asyncio
import json
import os
import logging
import traceback

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

# This class encapsulates some Semantic Kernel (SK) functionality.
# Links:
# - https://learn.microsoft.com/en-us/semantic-kernel/get-started/quick-start-guide?pivots=programming-language-python
# - https://github.com/microsoft/semantic-kernel
#
# Chris Joakim, 2025

class SKUtil:

    def __init__(self, verbose: bool = False):
        self.api_url = os.getenv("AZURE_OPENAI_URL")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.completions_dep = os.getenv("AZURE_OPENAI_COMPLETIONS_DEPLOYMENT")
        if verbose:
            print(f"SKUtil initialized; api_url: {self.api_url}")
            print(f"SKUtil initialized; api_key:  {self.api_key}")
            print(f"SKUtil initialized; completions_dep:  {self.completions_dep}")
