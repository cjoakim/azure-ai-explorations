import asyncio
import json
import os
import logging
import traceback

from enum import Enum
from typing import Literal

from openai import AzureOpenAI

import semantic_kernel as sk
from semantic_kernel import Kernel

# imports in alphabetical order here
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIEmbeddingPromptExecutionSettings
from semantic_kernel.connectors.ai.open_ai import OpenAITextPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.kernel_pydantic import KernelBaseSettings
from semantic_kernel.prompt_template import InputVariable
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.utils.logging import setup_logging


# This class encapsulates some Semantic Kernel (SK) functionality.
# At this time the logic assumes accessing ONLY AzureOpenAI.
#
# Links:
# - https://learn.microsoft.com/en-us/semantic-kernel/get-started/quick-start-guide?pivots=programming-language-python
# - https://github.com/microsoft/semantic-kernel
#
# Chris Joakim, 2025


class SKUtil:

    def __init__(
            self,
            opts: dict = {},
            plugins: list[str] = [],
            verbose: bool = False):
        self.opts = opts
        self.plugins = plugins
        self.verbose = verbose
        self.aoai_api_url = os.getenv("AZURE_OPENAI_URL")
        self.aoai_api_key = os.getenv("AZURE_OPENAI_KEY")
        self.aoai_only = True  # see method global_llm_service_name()
        self.default_chat_deployment_name = None
        self.default_embedding_deployment_name = None
        self.llm_service_name = self.global_llm_service_name()
        
        # key is deployment name, value is AzureChatCompletion instance
        self.chat_completion_model_cache = dict()

        # key is deployment name, value is AzureTextEmbedding instance
        self.embedding_model_cache = dict()

        if self.verbose:
            print(f"SKUtil#__init__; aoai_api_url: {self.aoai_api_url}")
            print(f"SKUtil#__init__; aoai_api_key: {self.aoai_api_key}")
        self.kernel = Kernel()
        kernel_logger = logging.getLogger("kernel")
        if kernel_logger is not None:
            kernel_logger.setLevel(self.get_kernel_logging_level())
 
    def build_kernel(self) -> Kernel:
        if self.opts is None:
            return self.kernel
        
        if "chat_completion" in self.opts.keys():
            dep_name = self.opts["chat_completion"]
            self.default_chat_deployment_name = dep_name
            completion_instance = self.get_completion_instance(dep_name)
            self.kernel.add_service(completion_instance)

        if "text_embedding" in self.opts.keys():
            dep_name = self.opts["text_embedding"]
            self.default_embedding_deployment_name = dep_name
            embedding_instance = self.get_embedding_instance(dep_name)
            self.kernel.add_service(embedding_instance)

        if self.verbose:
            print(f"SKUtil#build_kernel; default completions dep: {self.default_chat_deployment_name}")
            print(f"SKUtil#build_kernel; default embeddings dep:  {self.default_embedding_deployment_name}")

        for plugin in self.plugins:
            pass

    async def generate_embedding(self, text: str, dep_name: str) -> list[float] | None:
        if text is None:
            print("SKUtil#generate_embedding - given text is None")
            return None
        if dep_name is None:
            def_name = self.default_embedding_deployment_name
        if dep_name is None:
            print("SKUtil#generate_embedding - given dep_name is None or no default value")
            return None
        instance = self.get_embedding_instance(dep_name)
        if instance is None:
            print("SKUtil#generate_embedding - instance for deployment {} is None".format(dep_name))
            return None
        else:
            try:
                embedding = await instance.generate_embeddings(text)
                if self.verbose:
                    print(str(type(embedding)))  # <class 'numpy.ndarray'>.
                    print(str(type(embedding[0])))
                    print(embedding[0].shape)  # (1536,)
                return embedding[0].tolist()
            except Exception as e:
                print(str(e))
                print(traceback.format_exc())
                return None


    # ========== The following methods are intented to be "private" ==========

    def get_kernel_logging_level(self):
        if "kernel_log_level" in self.opts:
            return self.opts["kernel_log_level"]
        else:
            return "DEBUG"
           
    def get_completion_instance(self, deployment_name: str) -> AzureChatCompletion | None:
        instance = None
        if deployment_name is None:
            return instance
        else:
            if deployment_name in self.chat_completion_model_cache.keys():
                return self.chat_completion_model_cache[deployment_name]
            else:
                instance = AzureChatCompletion(
                    api_key=self.aoai_api_key,
                    endpoint=self.aoai_api_url,
                    deployment_name=deployment_name)
                if instance is not None:
                    self.chat_completion_model_cache[deployment_name] = instance
                    if self.verbose:
                        print("SKUtil#get_completion_instance cached: {}".format(deployment_name))
        return instance


    def get_embedding_instance(self, deployment_name: str) -> AzureTextEmbedding | None:
        instance = None
        if deployment_name is None:
            return instance
        else:
            if deployment_name in self.chat_completion_model_cache.keys():
                return self.chat_completion_model_cache[deployment_name]
            else:
                instance = AzureTextEmbedding(
                    api_key=self.aoai_api_key,
                    endpoint=self.aoai_api_url,
                    deployment_name=deployment_name)
                if instance is not None:
                    self.chat_completion_model_cache[deployment_name] = instance
                    if self.verbose:
                        print("SKUtil#get_embedding_instance cached: {}".format(deployment_name))

        return instance

    def global_llm_service_name(self):
        # This method, and your environment variable values, should return one
        # of the following three lowercase values".  "azureopenai" is the default
        # OpenAI      = "openai"
        # AzureOpenAI = "azureopenai"
        # HuggingFace = "huggingface"
        # NOTE:
        # AT THIS TIME ONLY "azureopenai" IS RETURNED DUE TO THE VALUE OF
        # INSTANCE VARIABLE self.aoai_only
        if self.aoai_only:
            return "azureopenai"
        else:
            return os.getenv("GLOBAL_LLM_SERVICE", "azureopenai").strip().lower()
