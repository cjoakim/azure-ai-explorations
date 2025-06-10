"""
Usage:
  python main-hf.py <func>  
  python main-hf.py list_datasets
  python main-hf.py list_models
  python main-hf.py list_models --verbose
Options: 
  -h --help     Show this screen.
  --version     Show version.
"""

# main entry-point program for Hugging Face API examples.
# Chris Joakim, 2025 

import sys
import time
import traceback

from docopt import docopt
from dotenv import load_dotenv
from pathlib import Path

from urllib.parse import urlparse, parse_qs

from huggingface_hub import HfApi, ModelCard, ModelInfo, DatasetCard, DatasetInfo

from src.io.fs import FS

BASE_DIR = Path(__file__).absolute().parent


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)

def list_datasets():
    api = HfApi()
    datasets = api.list_datasets(sort="downloads", direction=-1, limit=100)
    for d in datasets: 
        print(d)

def list_models():
    authors = "Anthropic,facebook,google,microsoft,mistralai,deepseek-ai,nvidia".split(",")
    api = HfApi()
    for author in authors:
        print(f"Fetching models for author: {author}")
        time.sleep(5.0)
        models_dict = dict()
        models = api.list_models(author=author)
        for midx, m in enumerate(models):
            if midx < 10:
                id = m.modelId
                print(f"Processing model {id}")
                time.sleep(0.1)
                models_dict[id] = model_info_to_dict(m)
                if midx < 3:
                    print(m)

        print(f"Total models count: {len(models_dict)} for author: {author}")
        outfile1 = f"tmp/hf-models-{author}-list.json"
        outfile2 = f"tmp/hf-models-{author}-details.json"
        FS.write_json(sorted(models_dict.keys()), outfile1)
        FS.write_json(models_dict, outfile2)

def model_info_to_dict(model_info: ModelInfo) -> dict:
    # See https://github.com/huggingface/huggingface_hub/blob/v0.32.1/src/huggingface_hub/hf_api.py#L729
    try:
        id = model_info.modelId
        model_dict = {
            "modelId": id,
            "author": model_info.author,
            "created_at": str(model_info.created_at), 
            "last_modified": str(model_info.last_modified), 
            "disabled": model_info.disabled,
            "downloads": model_info.downloads,
            "downloads_all_time": model_info.downloads_all_time,
            "likes": model_info.likes,
            "trending_score": model_info.trending_score,
            "disabled": model_info.disabled,
            "gated": model_info.gated,
            "library_name": model_info.library_name,
            "tags": model_info.tags
        }
        if True:
            card = ModelCard.load(id)
            data = card.data
            if data != None:
                datadict = data.to_dict()
                # prune some verbose fields
                if "extra_gated_fields" in datadict.keys():
                    datadict["extra_gated_fields"] = ""
                if "extra_gated_prompt" in datadict.keys():
                    datadict["extra_gated_prompt"] = ""
                model_dict["card_data"] = datadict
            #model_dict["card_text"] = str(card.text)
        return model_dict
    except Exception as e:
        print(f"Error converting model info to dict: {e}")
        return None 
    
def verbose():
    return '--verbose' in sys.argv


if __name__ == "__main-_":
    load_dotenv(override=True)
    try:
        func = sys.argv[1].lower()
        if func == "list_datasets":
            list_datasets()
        elif func == "list_models":
            list_models()
        else:
            print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
