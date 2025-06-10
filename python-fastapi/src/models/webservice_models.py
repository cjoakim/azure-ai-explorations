from pydantic import BaseModel
from typing import Any

# This module contains the several Pydantic "models" that define both the
# request and response payloads for the web endpoints in this application.
# Think of these models as "interfaces" that define the "shapes" of actual
# objects.  Pydantic models are an interesting feature of the FastAPI
# webframework.  Using these models, FastAPI can automatically generate
# OpenAPI/Swagger request/response endpoint documentation.
#
# See https://fastapi.tiangolo.com/tutorial/response-model/
# See https://fastapi.tiangolo.com/tutorial/body/
#
# Chris Joakim, 2025


class PingResponseModel(BaseModel):
    epoch: float

class HealthResponseModel(BaseModel):
    epoch: float
    alive: bool
    rows_read: int

class CosmosQueryRequestModel(BaseModel):
    sql: str

class CosmosQueryResponseModel(BaseModel):
    sql: str
    results: Any = None
    ru: float
    elapsed: float
    error: str | None
    start_time: float
    finish_time: float
