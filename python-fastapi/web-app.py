# This is the entry-point for this web application, built with the
# FastAPI web framework.
#
# This implementation contains several 'FS.write_json(...)' calls
# to write out JSON files to the 'tmp' directory for understanding
# and debugging purposes.
#
# Chris Joakim, 2025

import asyncio
import json
import logging
import sys
import textwrap
import time
import traceback

import httpx

from contextlib import asynccontextmanager

from dotenv import load_dotenv

from fastapi import FastAPI, Request, Response, Form, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Pydantic models defining the "shapes" of requests and responses
from src.models.webservice_models import PingResponseModel
from src.models.webservice_models import HealthResponseModel
from src.models.webservice_models import CosmosQueryRequestModel
from src.models.webservice_models import CosmosQueryResponseModel

from src.io.fs import FS
from src.os.env import Env
from src.db.cosmos_nosql_util import CosmosNoSqlUtil


# standard initialization
load_dotenv(override=True)
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

if sys.platform == "win32":
    logging.warning("Windows platform detected, setting WindowsSelectorEventLoopPolicy")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    logging.warning(
        "platform is {}, not Windows.  Not setting event_loop_policy".format(
            sys.platform
        )
    )

nosql_util = CosmosNoSqlUtil()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Automated startup and shutdown logic for the FastAPI app.
    See https://fastapi.tiangolo.com/advanced/events/#lifespan
    """
    try:
        Env.log_standard_env_vars()
        await nosql_util.initialize()
        logging.error("FastAPI lifespan - CosmosNoSqlUtil initialized")
        dbname = Env.cosmosdb_nosql_default_database()
        cname = Env.cosmosdb_nosql_default_container()
        print("CosmosNoSqlUtil using dbname: {}, cname: {}".format(dbname, cname))
        nosql_util.set_db(dbname)
        nosql_util.set_container(cname)
    except Exception as e:
        logging.error("FastAPI lifespan exception: {}".format(str(e)))
        logging.error(traceback.format_exc())

    yield  # logic above is "startup", logic below is "shutdown"

    logging.info("FastAPI lifespan, shutting down...")
    await nosql_util.close()
    logging.info("FastAPI lifespan, pool closed")


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
views = Jinja2Templates(directory="views")

logging.error("webapp.py started")


@app.get("/ping")
async def get_ping() -> PingResponseModel:
    resp = dict()
    resp["epoch"] = time.time()
    return resp


@app.get("/health")
async def get_health(req: Request, resp: Response) -> HealthResponseModel:
    """
    Return a HealthResponseModel indicating the health of this web app.
    This endpoint is invoked by a container orchestrator such as
    Azure Container Apps (ACA) or Azure Kubernetes Service (AKS).
    """
    alive = True  # TODO - read Cosmos DB to determine the value of alive.
    liveness_data = dict()
    liveness_data["alive"] = alive
    liveness_data["rows_read"] = -1
    liveness_data["epoch"] = time.time()
    logging.info("liveness_check: {}".format(liveness_data))
    return liveness_data


@app.post("/query_cosmos")
async def post_sparql_console(req: CosmosQueryRequestModel) -> CosmosQueryResponseModel:
    global nosql_util
    logging.info("/query_cosmos request: {}".format(req))

    start_time = time.time()
    response_data = dict()
    response_data["sql"] = None
    response_data["start_time"] = start_time
    response_data["error"] = None
    response_data["ru"] = -1.0
    try:
        response_data["sql"] = req.sql
        response_data["results"] = None

        query_results = await nosql_util.query_items(req.sql, True)
        response_results = list()
        for idx, result in enumerate(query_results):
            response_results.append(result)
        response_data["results"] = response_results
        response_data["ru"] = float(nosql_util.last_request_charge())
    except Exception as e:
        response_data["error"] = str(e)

    finish_time = time.time()
    response_data["finish_time"] = finish_time
    response_data["elapsed"] = finish_time - start_time
    return response_data
