"""
Usage:
  python main-aoai.py <func>
  python main-aoai.py list_models
  python main-aoai.py generate_completion <promptfile>
  python main-aoai.py generate_completion prompts/sample-prompt.txt
  python main-aoai.py generate_completion prompts/gen-aisearch-util.txt
  python main-aoai.py generate_completion prompts/gen-blob-util.txt
  python main-aoai.py generate_completion prompts/gen-foundry-util.txt
"""

import json
import sys
import os
import traceback

from docopt import docopt
from dotenv import load_dotenv

from openai import AzureOpenAI

from src.io.fs import FS


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def generate_completion(promptfile):
    try:
        with open(promptfile, "r") as f:
            prompt = f.read()
        if prompt is None:
            print(f"Error: prompt file {promptfile} not found or empty.")
            return
        else:
            print(f"Prompt file {promptfile} loaded successfully.")
            print(f"Prompt content:\n==========\n{prompt}\n==========")

        client = build_client()
        deployment = completion_DEP()
        print(f"Using deployment: {deployment}")
        messages = parse_promptfile(promptfile)
        print("Parsed messages:\n{}".format(json.dumps(messages, indent=2)))

        response = client.chat.completions.create(
            messages=messages,
            model=deployment,
            temperature=0.0,
            max_tokens=4096
        )

        #     model=deployment,
        #     prompt=prompt,
        #     max_tokens=200,
        #     temperature=0.1,
        #     top_p=1.0,
        #     n=1,
        #     stop=None
        # )
        print("Completion response:")
        content = response.choices[0].message.content
        print(content)
        FS.write(content, "tmp/generate_completion_output.txt", content)
        FS.write(response.model_dump_json(indent=2), "tmp/generate_completion.json")
    except Exception as e:
        print(f"An error occurred: {e}")


def list_models():
    try:
        client = build_client()
        models = client.models.list()
        for midx, model in enumerate(models.data):
            print(f"=== model {midx} {model.id}")
            print(model)
        print(f"Total models: {len(models.data)}")
    except Exception as e:
        print(f"An error occurred: {e}")


def parse_promptfile(promptfile):
    """
    Parse the given delimited prompt txt file and return a JSON list 
    of system and user messages as required by the completions API.
    """
    messages = []
    lines = FS.read_lines(promptfile)
    system_prompt_lines, user_prompt_lines = [], []
    current_role = None
    for line in lines:
        line = line.strip()
        if line.startswith("ROLE-SYSTEM:"):
            current_role = "system"
        elif line.startswith("ROLE-USER:"):
            current_role = "user"
        elif current_role == "system":
            system_prompt_lines.append(line.replace('"', "'"))
        elif current_role == "user":
            user_prompt_lines.append(line.replace('"', "'"))

    messages.append({
        "role": "system",
        "content": "\n".join(system_prompt_lines).strip()
    })
    messages.append({
        "role": "user",
        "content": "\n".join(user_prompt_lines).strip()
    })
    return messages


def build_client():
    url = openai_url()
    key = openai_key()
    print("Azure OpenAI URL:", url)
    print("Azure OpenAI Key:", key[0:4] + "..." if key else "Not set")
    return AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=url,
        api_key=key
    )

def openai_url():
    if "--personal" in sys.argv:
        return os.environ.get("AZURE_PERSONAL_OPENAI_URL")
    else:
        return os.environ.get("AZURE_OPENAI_URL")

def openai_key():
    if "--personal" in sys.argv:
        return os.environ.get("AZURE_PERSONAL_OPENAI_KEY")
    else:
        return os.environ.get("AZURE_OPENAI_KEY")

def completion_DEP():
    if "--personal" in sys.argv:
        return os.environ.get("AZURE_PERSONAL_OPENAI_COMPLETIONS_DEP")
    else:
        return os.environ.get("AZURE_OPENAI_COMPLETIONS_DEP")


if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            if func == "list_models":
                list_models()
            elif func == "generate_completion":
                promptfile = sys.argv[2]
                generate_completion(promptfile)
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
