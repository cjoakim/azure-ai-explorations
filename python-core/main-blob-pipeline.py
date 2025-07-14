"""
Usage:
  python main-blob-pipeline.py <func>
  python main-blob-pipeline.py create_config
  python main-blob-pipeline.py explore
  python main-blob-pipeline.py delete_define_ai_pipeline_tables
  python main-blob-pipeline.py load_configuration pipeline config/pipeline_config.json
"""

import asyncio
import json
import logging
import os
import sys
import time
import traceback


from docopt import docopt
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential

from azure.ai.documentintelligence.aio import (
    DocumentIntelligenceClient as DocumentIntelligenceAsyncClient,
)
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.documentintelligence.models import DocumentContentFormat
from azure.ai.documentintelligence.models import DocumentAnalysisFeature

from sqlalchemy.orm import Session

from src.db.pg_util import PGUtil
from src.db.sqlalchemy_models import AppEngine, Configuration

from src.io.fs import FS
from src.io.storage_util import StorageUtil
from src.os.env import Env

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=logging.INFO)


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def config_filename():
    return "config/pipeline_config.json"


def create_config():
    config = dict()
    config["name"] = "pipeline_config"
    containers = dict()
    containers["raw"] = "di-sample-docs"
    containers["bronze"] = "di-preprocessed"
    containers["telemetry"] = "di-telemetry"
    containers["testing"] = "di-test"
    config["containers"] = containers
    config["filetypes"] = supported_filetypes()

    FS.write_json(
        config, 
        config_filename(),
        sort_keys=False)


def explore():
    config = FS.read_json(config_filename())
    print(f"Pipeline config: {config}")
    cname = config["containers"]["testing"]
    print(f"Testing container name: {cname}")

    storage_util = build_storage_util()
    print("===== StorageUtil constructor")
    time.sleep(1) 

    containers = storage_util.list_containers()
    for container in containers:
        print(f"Container: {container}")

    for n in range(40):
        dir = n % 10
        epoch = int(time.time())
        blobname = "test/{}/test-blob-{}.txt".format(dir, epoch)
        msg = dict()
        msg["n"] = n
        msg["epoch"] = epoch
        msg["blobname"] = blobname
        print(f"Uploading blob: {blobname} to container: {cname}")
        result = storage_util.upload_string_as(
            cname, blobname, json.dumps(msg), replace=True)
        print(f"  result: {result}")
        time.sleep(0.1)

    time.sleep(1) 

    print("===== list container")
    blobs = storage_util.list_container(cname, names_only=False)
    for b in blobs:
        print("---\nlist item: {}".format(b))
        for key in b.keys():
            print(f"  item key: {key}: {b[key]}")

    outfile = f"tmp/storage-blobs-{cname}.json"
    #FS.write_json(blobs, outfile, pretty=True, sort_keys=True)
    time.sleep(1) 


def build_storage_util():
    connection_string = os.getenv("AZURE_STORAGE_CONN_STRING")
    return StorageUtil(connection_string, logging_level=None)


def supported_filetypes() -> list[str]:
    """
    Return the filetypes supported by Document Intelligence, plus 'md':
    Filetypes: bmp, docx, heif, html, jpeg, jpg, md, pdf, png, pptx, tiff, xlsx
    """
    di_types = Env.document_intelligence_supported_filetypes()
    di_types.append("md")
    # di_types.append("txt"). # TODO: what about txt files?
    return sorted(di_types)


def build_async_docintel_client() -> DocumentIntelligenceAsyncClient | None:
    try:
        endpoint = os.environ.get("AZURE_DOCINTEL_URL")
        key = os.environ.get("AZURE_DOCINTEL_KEY")
        client = DocumentIntelligenceAsyncClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        return client
    except Exception as e:
        print("Error building Document Intelligence client:")
        print(str(e))
        print(traceback.format_exc())
        return None

async def explore_async_local_file():
    di_client: build_async_docintel_client = build_async_docintel_client()
    # infile = "../data/docs/dire-straits-sultans-of-swing-lyrics.pdf"
    # infile = "../data/docs/us-constitution.pdf"
    # infile = "../data/docs/simple-sample-doc.pdf"
    # infile = "../data/docs/LawsOfChess.pdf"
    infile = "../data/docs/SampleDocument.pdf"
    print(f"Analyzing file: {infile} ...")

    output_format = DocumentContentFormat.MARKDOWN
    features_list = list()
    # features.append(DocumentAnalysisFeature.STYLE_FONT)

    async with di_client:
        with open(infile, "rb") as f:
            poller = await di_client.begin_analyze_document(
                "prebuilt-layout",
                body=f,
                output_content_format=output_format,
                features=features_list
            )
            print(f"poller type: {str(type(poller))}")

        result: AnalyzeResult = await poller.result()
        print(f"result type: {str(type(result))}")
        print(f"result page count is {len(result.pages)}")
        print(f"result content:\n{result.content}\n")
            
        basename = os.path.basename(infile)
        content_outfile = f"tmp/{basename}.md"
        result_outfile  = f"tmp/{basename}.json"
        FS.write(result.content, content_outfile)
        FS.write_json(result.as_dict(), result_outfile)


async def storage_pipeline_example():
    # TODO
    print("storage_pipeline_example() not implemented yet")

    try:
        asyncio.sleep(0.1)  # Simulate some async work for now:
        raw_storage_container = "di-sample-docs"      # TODO - get from configuration
        bronze_storage_container = "di-preprocessed"  # TODO - get from configuration

        di_client = build_async_docintel_client()
        print(f"Document Intelligence client created: {str(di_client)}")


    except Exception as e:
        print(str(e))
        print(traceback.format_exc())


async def execute_sql_script(script_filename: str):
    sql = FS.read(script_filename)
    print(f"Executing SQL script: {script_filename}")
    print(sql)

    await PGUtil.initialze_pool()
    results = await PGUtil.execute_query(sql)
    if results is not None:
        print(json.dumps(results, sort_keys=False, indent=2))

async def load_configuration(name: str, json_filename: str):
    """
    Load the configuration table for the specified name with the
    value of the given JSON filename.  The "data" column is a JSONB.
    """
    AppEngine.initialize()

    try:
        c = Configuration(name=name, data=FS.read_json(json_filename))
        print(c)
        with Session(AppEngine.get_engine()) as session:
            session.add_all([c])
            session.commit()
    except Exception as e:
        logging.critical("Exception in load_configuration: {}".format(str(e)))

    
async def async_main():
    """
    This is the asyncronous main logic, called from the entry point
    of this module with "asyncio.run(async_main())".
    """
    try:
        if len(sys.argv) < 2:
            print_options("no command-line args given")
        else:
            func = sys.argv[1].lower()
            if func == "create_config":
                create_config()
            elif func == "explore":
                explore()
            elif func == "load_configuration":
                name = sys.argv[2]
                json_filename = sys.argv[3]
                await load_configuration(name, json_filename)
            elif func == "delete_define_ai_pipeline_tables":
                await execute_sql_script("sql/ai_pipeline.ddl")
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        logging.critical(str(e))
        logging.exception(e, stack_info=True, exc_info=True)

    try:
        await PGUtil.close_pool()
    except Exception as e:
        logging.critical(str(e))

    try:
        AppEngine.dispose()
    except Exception as e:
        logging.critical(str(e))

if __name__ == "__main__":
    load_dotenv(override=True)
    if sys.platform == "win32":
        logging.info("Running on Windows, setting WindowsSelectorEventLoopPolicy")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        logging.info("Not running on Windows")

    asyncio.run(async_main())
