"""
Usage:
  python main-blob-pipeline.py <func>
  python main-blob-pipeline.py delete_define_ai_pipeline_tables
  python main-blob-pipeline.py create_ai_pipeline_config_json_file
  python main-blob-pipeline.py load_configuration ai_pipeline config/ai_pipeline_config.json
  python main-blob-pipeline.py create_storage_containers
  python main-blob-pipeline.py upload_blobs_into_raw_container ../data/docs/
  python main-blob-pipeline.py load_documents_per_raw_container
  python main-blob-pipeline.py extract_text_from_documents
  python main-blob-pipeline.py ai_process_extracted_text
  python main-blob-pipeline.py evaluate_extracted_qnas
  python main-blob-pipeline.py explore
"""

# This module is an alpha version of a Python-based AI pipeline;
# it is a volatile work-in-progress at this time.
# Much of the code will be refactored at a later date.
# Chris Joakim, 3Cloud, July 2025 

import asyncio
import datetime
import json
import logging
import os
from select import select
import sys
import time
import traceback

from typing import List

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

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.pg_util import PGUtil
from src.db.sqlalchemy_models import AppEngine, Configuration, Document
from src.db.sqlalchemy_models import CommonOperations

from src.io.fs import FS
from src.io.storage_util import StorageUtil
from src.os.env import Env

logging.basicConfig(
    format="%(asctime)s - %(message)s", level=logging.INFO)

def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)

def create_ai_pipeline_config_json_file():
    config = dict()
    config["name"] = _ai_pipeline_config_name()
    containers = dict()
    containers["raw"] = "qna-raw"
    containers["bronze"] = "qna-preprocessed"
    containers["silver"] = "qna-processed"
    containers["telemetry"] = "qna-telemetry"
    containers["testing"] = "qna-test"
    config["containers"] = containers
    config["filetypes"] = _supported_filetypes()

    FS.write_json(
        config, 
        _ai_pipeline_config_filename(),
        sort_keys=False)

async def execute_sql_script(script_filename: str):
    sql = FS.read(script_filename)
    logging.info(f"Executing SQL script: {script_filename}")
    logging.info(sql)

    await PGUtil.initialze_pool()
    results = await PGUtil.execute_query(sql)
    if results is not None:
        logging.info(json.dumps(results, sort_keys=False, indent=2))

async def load_configuration(name: str, json_filename: str):
    """
    Load the configuration table for the specified name with the
    value of the given JSON filename.  The "data" column is a JSONB.
    Then immediately read that row and display it.
    """
    AppEngine.initialize()

    try:
        c = Configuration(name=name, data=FS.read_json(json_filename))
        logging.info("config to be loaded: {}".format(c))
        with Session(AppEngine.get_engine()) as session:
            session.add_all([c])
            session.commit()

        stmt = select(Configuration).where(Configuration.name == name)
        with Session(AppEngine.get_engine()) as session:
            rows = session.execute(stmt)
            for row in rows:
                logging.info("config read from db: {}".format(row))

    except Exception as e:
        #logging.critical("Exception in load_configuration: {}".format(str(e)))
        logging.critical(e, stack_info=True, exc_info=True)

async def create_storage_containers():
    storage_util = _build_storage_util()
    AppEngine.initialize()
    await asyncio.sleep(0.1) 
    try:
        config_name = _ai_pipeline_config_name()
        config = await CommonOperations.read_configuration_object(config_name)
        logging.info(f"config read from db: {config}")
        if config is None:
            return
        current_containers : List[str] = storage_util.list_containers()
        logging.info(f"Storage current containers: {current_containers}")

        containers_dict = config["containers"]
        logging.info(f"Configured containers_dict: {containers_dict}")

        for key in containers_dict.keys():
            cname = containers_dict[key]
            if cname in current_containers:
                logging.info(f"Storage container already exists: {cname}")
            else:
                await asyncio.sleep(1.0)
                logging.info(f"Creating storage container: {cname} ...")
                result = storage_util.create_container(cname)
                if result is not None:
                    logging.info(f"Storage container created: {cname}")
                else:
                    logging.error(f"Storage container creation failed: {cname}")
    except Exception as e:
        logging.critical(e, stack_info=True, exc_info=True)

async def upload_blobs_into_raw_container(sample_docs_dir: str = "../data/docs/"):
    storage_util = _build_storage_util()
    AppEngine.initialize()
    await asyncio.sleep(0.1) 
    try:
        config_name = _ai_pipeline_config_name()
        logging.info(f"config_name: {config_name}")
        config = await CommonOperations.read_configuration_object(config_name)
        logging.info(f"config read from db: {config}")
        if config is None:
            return
        current_containers : List[str] = storage_util.list_containers()
        logging.info(f"Storage current containers: {current_containers}")

        raw_container = config["containers"]["raw"]
        logging.info(f"Configured raw container: {raw_container}")

        if raw_container not in current_containers:
            logging.info(f"Error - the raw storage container '{raw_container}' does not exist!  Exiting.")
            return
        
        basenames = FS.list_files_in_dir(sample_docs_dir)
        for basename in basenames:
            file_path = os.path.join(sample_docs_dir, basename)
            logging.info(f"File to upload into raw container: {file_path}")
            meta = dict()
            meta["uploaded_at"] = datetime.datetime.now().isoformat()
            meta["source_system"] = "sample_files"
            result = storage_util.upload_file_as(
                container_name=raw_container, 
                container_blobname=basename,
                local_filename=file_path, 
                metadata=meta,
                replace=True)
            logging.info(f"Upload result for {file_path}: {result}")
    except Exception as e:
        logging.critical(e, stack_info=True, exc_info=True)

async def load_documents_per_raw_container():
    storage_util = _build_storage_util()
    AppEngine.initialize()
    await asyncio.sleep(0.1) 
    try:
        config_name = _ai_pipeline_config_name()
        config = await CommonOperations.read_configuration_object(config_name)
        logging.info(f"config read from db: {config}")
        if config is None:
            return
        raw_container = config["containers"]["raw"]
        logging.info(f"raw_container: {raw_container}")
        blobs = storage_util.list_container(raw_container, names_only=False)
        for b in blobs:
            logging.info(b)
            doc = Document(
                source_system="test",
                source_path=b["name"],
                raw_container=raw_container,
                raw_file_name=b["name"],
                raw_file_size=int(b["size"]),
                raw_etag=b["etag"],
                raw_file_type=b["name"].split(".")[-1],
                raw_storage_path=b["name"],
                raw_inserted_at=datetime.datetime.now(),
                processing_state="raw",
                preprocessed_container=None,
                preprocessed_path=None,
                preprocessing_chunk_count=0,
                preprocessing_messages=None,
                preprocessed_at=None,
                qna_extracted_at=None,
                qna_extracted_messages=None,
            )
            logging.info("Document to be loaded: {}".format(doc))

            existing_doc = await CommonOperations.read_document(doc)
            logging.info("existing_doc: {}".format(existing_doc))

            if existing_doc is None:
                with Session(AppEngine.get_engine()) as session:
                    session.add_all([doc])
                    session.commit()
            else:
                logging.info("Document already exists in DB, skipping: {}".format(doc))
    except Exception as e:
        #logging.critical("Exception in load_configuration: {}".format(str(e)))
        logging.critical(e, stack_info=True, exc_info=True)

async def extract_text_from_documents():
    logging.info("extract_text_from_documents NOT YET IMPLEMENTED")

async def ai_process_extracted_text():
    logging.info("ai_process_extracted_text NOT YET IMPLEMENTED")

async def evaluate_extracted_qnas():
    logging.info("evaluate_extracted_qnas NOT YET IMPLEMENTED")

# ========== "private" methods below (leading underscore) below ==========

def _ai_pipeline_config_name():
    return "ai_pipeline"

def _ai_pipeline_config_filename():
    return "config/{}_config.json".format(_ai_pipeline_config_name())

def _build_storage_util():
    connection_string = os.getenv("AZURE_STORAGE_CONN_STRING")
    return StorageUtil(connection_string, logging_level=None)

def _supported_filetypes() -> list[str]:
    """
    Return the filetypes supported by Document Intelligence, plus 'md':
    Filetypes: bmp, docx, heif, html, jpeg, jpg, md, pdf, png, pptx, tiff, xlsx
    """
    di_types = Env.document_intelligence_supported_filetypes()
    di_types.append("md")
    # di_types.append("txt"). # TODO: what about txt files?
    return sorted(di_types)

def _build_async_docintel_client() -> DocumentIntelligenceAsyncClient | None:
    try:
        endpoint = os.environ.get("AZURE_DOCINTEL_URL")
        key = os.environ.get("AZURE_DOCINTEL_KEY")
        client = DocumentIntelligenceAsyncClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        return client
    except Exception as e:
        logging.info("Error building Document Intelligence client:")
        logging.info(str(e))
        logging.info(traceback.format_exc())
        return None

# ========== exploratory/ad-hoc methods below ==========

async def explore():
    await asyncio.sleep(0.1)
    logging.info("explore() - no current implementation")

# ========== main entry-point methods below ==========

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
            if func == "delete_define_ai_pipeline_tables":
                await execute_sql_script("sql/ai_pipeline.ddl")
            elif func == "create_ai_pipeline_config_json_file":
                create_ai_pipeline_config_json_file()
            elif func == "load_configuration":
                name = sys.argv[2]
                json_filename = sys.argv[3]
                await load_configuration(name, json_filename)
            elif func == "create_storage_containers":
                await create_storage_containers()
            elif func == "upload_blobs_into_raw_container":
                sample_docs_dir = sys.argv[2]
                await upload_blobs_into_raw_container(sample_docs_dir)
            elif func == "load_documents_per_raw_container":
                await load_documents_per_raw_container()
            elif func == "extract_text_from_documents":
                await extract_text_from_documents()
            elif func == "ai_process_extracted_text":
                await ai_process_extracted_text()
            elif func == "evaluate_extracted_qnas":
                await evaluate_extracted_qnas()
            elif func == "explore":
                await explore()
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
