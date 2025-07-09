"""
Usage:
  python main-qa.py <func>
  python main-qa.py check_env
  python main-qa.py parse_qa <deployment> <prompt_file> <raw_file>
  python main-qa.py parse_qa gpt-4.1 prompts/mickey-mantle.txt none
  python main-qa.py parse_qa gpt-4.1 qa1.txt ../data/text/gettysburg-address.txt
Options: 
  -h --help     Show this screen.
  --version     Show version.
"""

import asyncio
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
from src.util.prompt_util import PromptUtil
from src.util.template import Template


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


async def parse_qa(deployment, prompt_file, raw_file="none"):
    url = os.getenv("AZURE_OPENAI_EMBEDDINGS_URL")
    key = os.getenv("AZURE_OPENAI_EMBEDDINGS_KEY")

    await asyncio.sleep(0.01)

    print("=== parse_qa parameters: ===")
    print("url:         {}".format(url))
    print("key:         {}".format(key))
    print("deployment:  {}".format(deployment))
    print("prompt_file: {}".format(prompt_file))
    print("raw_file:    {}".format(raw_file))

    if raw_file != "none":
        raw_text = FS.read(raw_file).strip()
        values = dict()
        values["raw_text"] = raw_text
        t = Template.get_template(os.getcwd(), prompt_file)
        rendered = Template.render(t, values)
        rendered_lines = rendered.split("\n")
        pu = PromptUtil(rendered_lines)
        system_prompt = pu.get_system_prompt()
        user_prompt = pu.get_user_prompt()
        print("system_prompt: {}".format(system_prompt))
        print("user_prompt:   {}".format(user_prompt))
    else:
        pu = PromptUtil(FS.read_lines(prompt_file))
        system_prompt = pu.get_system_prompt()
        user_prompt = pu.get_user_prompt()
        print("system_prompt: {}".format(system_prompt))
        print("user_prompt:   {}".format(user_prompt))
    
    if "--execute" in sys.argv:
        client = AzureOpenAI(azure_endpoint=url, api_key=key, api_version="2024-10-21")

        completion: ChatCompletion = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        print("=== completion type ===")
        print(str(type(completion)))

        print("=== message ===")
        print(completion.choices[0].message)

        print("=== content ===")
        print(completion.choices[0].message.content)

        print("=== model_dump_json ===")
        print(completion.model_dump_json(indent=2))

        FS.write_json(completion.model_dump_json(indent=2), "tmp/parse_qa.json")


def industrial_disease_lyrics_md():
    text = FS.read("../data/text/industrial_disease_lyrics.txt").strip()
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
        # parse_qa <deployment> <prompt_file> <raw_file>
        if func == "parse_qa":
            deployment = sys.argv[2].lower()
            prompt_file = sys.argv[3].lower()
            raw_file = sys.argv[4].lower()
            asyncio.run(parse_qa(deployment, prompt_file, raw_file))
        else:
            print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
