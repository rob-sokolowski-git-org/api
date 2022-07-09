import pandas as pd
import time
import typing as t


from fastapi import FastAPI, APIRouter, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Response


from api.core import CoreBusinessLogic
from api.types import PeakResponse, IncrementResponse, DuckDbQueryRequest, DuckDbQueryResponse, Pong
from fastapi.responses import JSONResponse

from env_config import CONFIG

duckdb = CoreBusinessLogic(env_config=CONFIG)


def health_check_router() -> APIRouter:
    router = APIRouter()

    @router.get("/ping")
    async def ping() -> Pong:
        return Pong()

    return router


def duckdb_router() -> APIRouter:
    router = APIRouter()

    @router.post("/duckdb")
    async def execute_query(req: DuckDbQueryRequest) -> DuckDbQueryResponse:
        df, df_meta = duckdb.execute_as_df_with_meta_data(query_str=req.query_str)

        return duckdb.map_response(df_data=df, df_metadata=df_meta)

    return router


def file_router() -> APIRouter:
    router = APIRouter()

    @router.post("/files")
    async def create_file(file: UploadFile = File(...)) -> DuckDbQueryResponse:
        file_to_save = await file.read()
        print("Da fuq?")


    return router


def import_csv_files() -> None:
    """The following are loaded into DuckDB's memory"""
    duckdb.import_csv_file(path="./data/president_polls.csv", table_name="president_polls", )
    duckdb.import_csv_file(path="./data/president_polls_historical.csv", table_name="president_polls_historical", )


def get_app_instance() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=False,
      allow_methods=["*"],
      allow_headers=["*"],
    )

    app.include_router(health_check_router())
    app.include_router(duckdb_router())
    app.include_router(file_router())

    return app

import_csv_files()
app = get_app_instance()
