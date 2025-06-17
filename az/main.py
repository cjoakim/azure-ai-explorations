"""
Usage:
  python main.py <func>
  python main.py env
  python main.py extract_env_vars
  python main.py extract_env_vars ; cat tmp/azure-env-vars.txt
  python main.py models_and_quota
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import os
import sys
import traceback

from docopt import docopt
from dotenv import load_dotenv

from src.io.fs import FS

def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    for name in sorted(os.environ.keys()):
        if name.startswith("AZURE_"):
            print("{}: {}".format(name, os.environ[name]))

def extract_env_vars():
    env_dict = dict()
    extract_cosmos_env_vars(env_dict)
    extract_storage_env_vars(env_dict)
    extract_kv_env_vars(env_dict)
    extract_aoai_env_vars(env_dict)
    extract_foundry_env_vars(env_dict)
    extract_docintel_env_vars(env_dict)
    lines = list()
    for key in sorted(env_dict.keys()):
        value = env_dict[key]
        lines.append("{:<30} ||| {}".format(key, value))
    FS.write_lines(lines, "tmp/azure-env-vars.txt")

def extract_cosmos_env_vars(env_dict):
    try:
        show_data = FS.read_json("tmp/cosmosdb-account-show.json")
        keys_data = FS.read_json("tmp/cosmosdb-account-keys.json")
        env_dict["AZURE_COSMOSDB_NOSQL_ACCT"] = show_data["name"]
        env_dict["AZURE_COSMOSDB_NOSQL_URI"] = show_data["documentEndpoint"]
        env_dict["AZURE_COSMOSDB_NOSQL_KEY"] = keys_data["primaryMasterKey"]
        conn_str = "AccountEndpoint={}/;AccountKey={};".format(  
            show_data["documentEndpoint"],
            keys_data["primaryMasterKey"])
        env_dict["AZURE_COSMOSDB_NOSQL_CONN_STR"] = conn_str
    except Exception as e:
        print("Error in extract_cosmos_env_vars: {}".format(str(e)))
        print(traceback.format_exc())
    
def extract_storage_env_vars(env_dict):
    try:
        show_data = FS.read_json("tmp/storage-account-show.json")
        keys_data = FS.read_json("tmp/storage-account-keys.json")
        conn_str = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net".format(  
            show_data["name"],
            keys_data[0]["value"])
        env_dict["AZURE_STORAGE_ACCOUNT"] = show_data["name"]
        env_dict["AZURE_STORAGE_KEY"] = keys_data[0]["value"]
        env_dict["AZURE_STORAGE_CONN_STRING"] = conn_str
    except Exception as e:
        print("Error in extract_storage_env_vars: {}".format(str(e)))
        print(traceback.format_exc())
    
def extract_kv_env_vars(env_dict):
    try:
        show_data = FS.read_json("tmp/kv-show.json")
        env_dict["AZURE_KV_ACCOUNT"] = show_data["name"]
    except Exception as e:
        print("Error in extract_kv_env_vars: {}".format(str(e)))
        print(traceback.format_exc())
    
def extract_aoai_env_vars(env_dict):
    try:
        show_data = FS.read_json("tmp/aoai-account-show.json")
        keys_data = FS.read_json("tmp/aoai-account-keys.json")
        deployments = FS.read_json("tmp/aoai-account-deployment-list.json")
        endpoint = show_data["properties"]["endpoint"]
        env_dict["AZURE_OPENAI_NAME"] = show_data["name"]
        env_dict["AZURE_OPENAI_URL"] = endpoint
        env_dict["AZURE_OPENAI_KEY"] = keys_data["key1"]
        env_dict["AZURE_OPENAI_REGION"] = show_data["location"]
        for d in deployments:
            dname = d["name"]
            dmodel = d["properties"]["model"]["name"]
            if "emb" in dname.lower():
                env_dict["AZURE_OPENAI_EMBEDDINGS_DEP"] = dname
                env_dict["AZURE_OPENAI_EMBEDDINGS_KEY"] = keys_data["key1"]
                env_dict["AZURE_OPENAI_EMBEDDINGS_MODEL"] = dmodel
                env_dict["AZURE_OPENAI_EMBEDDINGS_URL"] = endpoint
            elif "chat" in dname.lower():
                env_dict["AZURE_OPENAI_CHAT_DEP"] = dname
                env_dict["AZURE_OPENAI_CHAT_KEY"] = keys_data["key1"]
                env_dict["AZURE_OPENAI_CHAT_MODEL"] = dmodel
                env_dict["AZURE_OPENAI_CHAT_URL"] = endpoint
            else:
                env_dict["AZURE_OPENAI_COMPLETIONS_DEP"] = dname
                env_dict["AZURE_OPENAI_COMPLETIONS_KEY"] = keys_data["key1"]
                env_dict["AZURE_OPENAI_COMPLETIONS_MODEL"] = dmodel
                env_dict["AZURE_OPENAI_COMPLETIONS_URL"] = endpoint
    except Exception as e:
        print("Error in extract_aoai_env_vars: {}".format(str(e)))
        print(traceback.format_exc())
    
def extract_foundry_env_vars(env_dict):
    try:
        # TODO - implement
        show_data = FS.read_json("tmp/foundry-account-show.json")
        keys_data = FS.read_json("tmp/foundry-account-keys.json")
    except Exception as e:
        print("Error in extract_foundry_env_vars: {}".format(str(e)))
        print(traceback.format_exc())

def extract_docintel_env_vars(env_dict):
    try:
        show_data = FS.read_json("tmp/docintel-account-show.json")
        keys_data = FS.read_json("tmp/docintel-account-keys.json")
        env_dict["AZURE_DOCINTEL_ACCT"] = show_data["name"]
        env_dict["AZURE_DOCINTEL_URL"] = show_data["properties"]["endpoint"]
        env_dict["AZURE_DOCINTEL_KEY"] = keys_data["key1"]
        env_dict["AZURE_DOCINTEL_REGION"] = show_data["location"]
    except Exception as e:
        print("Error in extract_docintel_env_vars: {}".format(str(e)))
        print(traceback.format_exc())

def models_and_quota():
    # The following two scripts produced the JSON files used here:
    # aoai-quota-usage.sh
    # cogsvcs-list-models.sh
    quota_usage = FS.read_json("tmp/cognitiveservices-quota-usage.json")
    models = FS.read_json("tmp/cognitiveservices-list-models.json")
    print("quota_usage: {}".format(len(quota_usage)))
    print("models:      {}".format(len(models)))

    csv_lines, detail_lines = list(), list()
    csv_lines.append("model_name,quota_limit,current_usage,quota_available")
    for q in quota_usage:
        name = q["name"]["value"]
        limit = int(q["limit"])
        current = int(q["currentValue"])
        available = limit - current
        line = "{},{},{},{}".format(name, limit, current, available)
        detail_lines.append(line)
    detail_lines.sort()
    csv_lines.extend(detail_lines)
    FS.write_lines(csv_lines, "tmp/cognitiveservices-quota-usage.csv")

    csv_lines, detail_lines = list(), list() 
    csv_lines.append("kind,format,name,status,sku_name,sku_name,version,depdate,model_sku_count,input_index")  
    for midx, m in enumerate(models):
        kind = m["kind"]
        format = m["model"]["format"]
        name = m["model"]["name"]
        status = m["model"]["lifecycleStatus"]
        version = m["model"]["version"]
        sku_name = m["skuName"]
        sku_count = len(m["model"]["skus"])
        depdate = '?'
        usage_name = ''
        template = "{},{},{},{},{},{},{},{},{},{}"
        if sku_count == 0:
            line = template.format(
                kind, format, name, status, sku_name, usage_name, version, depdate, sku_count, midx)
            detail_lines.append(line)
        for sku in m["model"]["skus"]:
            sku_name = sku["name"]
            depdate = "??"
            usage_name = ''
            if "deprecationDate" in sku.keys():
                depdate = str(sku["deprecationDate"])
                if 'T' in depdate:
                    depdate = depdate.split("T")[0]
            if "usageName" in sku.keys():
                usage_name = sku["usageName"]
            line = template.format(
                kind, format, name, status, sku_name, usage_name, version, depdate, sku_count, midx)
            detail_lines.append(line)
    detail_lines.sort()
    csv_lines.extend(detail_lines)
    FS.write_lines(csv_lines, "tmp/cognitiveservices-list-models.csv")


if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        func = sys.argv[1].lower()
        if func == "env":
            check_env()
        elif func == "extract_env_vars":
            extract_env_vars()
        elif func == "models_and_quota":
            models_and_quota()
        else:
            print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
