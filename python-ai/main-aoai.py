"""
Usage:
  python main-aoai.py <func>
  python main-aoai.py check_env
  python main-aoai.py generate_embedding
  python main-aoai.py generate_completion
  python main-aoai.py generate_completion_with_md_prompt
  python main-aoai.py generate_completion_with_chatml_prompt
Options: 
  -h --help     Show this screen.
  --version     Show version.
"""

import sys
import os
import traceback

from pprint import pprint

from docopt import docopt
from dotenv import load_dotenv

import openai
from openai import AzureOpenAI
from openai.types import CreateEmbeddingResponse
from openai.types.chat.chat_completion import ChatCompletion

from src.io.fs import FS

# https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/chat-markup-language
# https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/prompt-engineering?tabs=chat


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    for name in sorted(os.environ.keys()):
        if "_OPENAI_" in name:
            print("{}: {}".format(name, os.environ[name]))


def generate_embedding():
    # See https://platform.openai.com/docs/guides/embeddings
    # See https://github.com/openai/openai-python/blob/main/src/openai/types/create_embedding_response.py

    url = os.getenv("AZURE_OPENAI_EMBEDDINGS_URL")
    key = os.getenv("AZURE_OPENAI_EMBEDDINGS_KEY")
    dep = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")

    client = AzureOpenAI(azure_endpoint=url, api_key=key, api_version="2024-10-21")

    embedding: CreateEmbeddingResponse = client.embeddings.create(
        model=dep,  # your model deployment name
        input="Running marathons and ultramarathons",
        encoding_format="float",
    )

    print(embedding)
    vector = embedding.data[0].embedding
    print("Embedding: {}".format(vector))
    print("Model:  {}".format(embedding.model))
    print("Usage:  {}".format(embedding.usage))
    print("Length: {}".format(len(vector)))

    FS.write_json(vector, "tmp/embedding.json")

    # [ ... , -0.014864896]
    # Model:  text-embedding-ada-002
    # Usage:  Usage(prompt_tokens=9, total_tokens=9)
    # Length: 1536


def generate_completion():
    url = os.getenv("AZURE_OPENAI_COMPLETIONS_URL")
    key = os.getenv("AZURE_OPENAI_COMPLETIONS_KEY")
    dep = os.getenv("AZURE_OPENAI_COMPLETIONS_DEPLOYMENT")

    client = AzureOpenAI(azure_endpoint=url, api_key=key, api_version="2024-10-21")

    # <class 'openai.types.chat.chat_completion.ChatCompletion'>
    completion: ChatCompletion = client.chat.completions.create(
        model=dep,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant who knows Major League Baseball.",
            },
            {"role": "user", "content": "What uniform number did Mickey Mantle wear?"},
        ],
    )

    print("=== completion type ===")
    print(str(type(completion)))

    print("=== message ===")
    print(completion.choices[0].message)

    print("=== content ===")
    print(completion.choices[0].message.content)
    # Mickey Mantle wore the uniform number 7 for the New York Yankees throughout his Hall of Fame career.

    print("=== model_dump_json ===")
    print(completion.model_dump_json(indent=2))


def generate_completion_with_md_prompt():
    url = os.getenv("AZURE_OPENAI_COMPLETIONS_URL")
    key = os.getenv("AZURE_OPENAI_COMPLETIONS_KEY")
    dep = os.getenv("AZURE_OPENAI_COMPLETIONS_DEPLOYMENT")

    client = AzureOpenAI(azure_endpoint=url, api_key=key, api_version="2024-10-21")

    # <class 'openai.types.chat.chat_completion.ChatCompletion'>
    completion: ChatCompletion = client.chat.completions.create(
        model=dep,
        temperature=0.0,
        max_tokens=1000,
        messages=[
            {"role": "system", "content": text_summarization_md()},
            {"role": "user", "content": gettysburg_address_user_md()},
        ],
    )

    print("=== completion type ===")
    print(str(type(completion)))

    print("=== message ===")
    print(completion.choices[0].message)

    print("=== content ===")
    print(completion.choices[0].message.content)

    # with gettysburg_address_user_md()
    # - Four score and seven years ago, a new nation was founded on the principle of equality
    # - The nation is now in the midst of a civil war to test its endurance
    # - A battlefield is being dedicated as a final resting place for those who died for the nation
    # - The ground is consecrated by the brave men who fought there
    # - The living are urged to continue the work of those who fought and to honor their sacrifice
    # - The goal is for the nation to have a new birth of freedom and for government by the people to endure

    # with industrial_disease_lyrics_md()
    # - Warning lights flashing at quality control
    # - Rumors and anger in the loading bay and town
    # - Whistle blown, walls came down
    # - Meeting in boardroom, trying to trace smell
    # - Leak in washroom, sneak-in personnel
    # - Concerns about industrial disease in corridors
    # - Caretaker crucified for sleeping at post
    # - Watchdog with rabies, foreman with fleas
    # - Panic on switchboard, tongues in knots
    # - Symptoms of monetary squeeze
    # - ITV and BBC discussing curse of industrial disease
    # - Doctor diagnose industrial disease, prescribes for depression
    # - Speaker's Corner scene with protest singer
    # - Protest against war and factories
    # - Jesus figures discussing stopping industrial disease
    # - Critique on societal issues and control tactics.

    print("=== model_dump_json ===")
    print(completion.model_dump_json(indent=2))


def generate_completion_with_chatml_prompt():
    # NOTE: ChatML is in PREVIEW MODE in Azure OpenAI.
    # THIS METHOD IS NOT CURRENTLY WORKING.
    # See https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/chat-markup-language

    url = os.getenv("AZURE_OPENAI_CHAT_URL")
    key = os.getenv("AZURE_OPENAI_CHAT_KEY")
    dep = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

    client = AzureOpenAI(
        azure_endpoint=url, api_key=key, api_version="2024-10-21"  # 2024-02-01
    )

    response = client.chat.completions.create(
        model=dep,  # The deployment name you chose when you deployed the GPT-35-Turbo model
        prompt="<|im_start|>system\nAssistant is a large language model trained by OpenAI.\n<|im_end|>\n<|im_start|>user\nWho were the founders of Microsoft?\n<|im_end|>\n<|im_start|>assistant\n",
        stop=["<|im_end|>"],
    )

    print(response["choices"][0]["text"])


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
    text = FS.read("../data/text/industrial_disease_lyrics.txt").strip()
    return """
## Text to summarize

{}

""".format(
        text
    ).lstrip()


if __name__ == "__main-_":
    try:
        func = sys.argv[1].lower()
        if func == "check_env":
            check_env()
        elif func == "generate_embedding":
            generate_embedding()
        elif func == "generate_completion":
            generate_completion()
        elif func == "generate_completion_with_md_prompt":
            generate_completion_with_md_prompt()
        elif func == "generate_completion_with_chatml_prompt":
            generate_completion_with_chatml_prompt()
        else:
            print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
