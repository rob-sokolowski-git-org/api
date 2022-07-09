import random

import pandas as pd
import time
import typing as t


from fastapi import FastAPI, APIRouter, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Response


from api.core import CoreBusinessLogic
from api.types import PeakResponse, IncrementResponse, DuckDbQueryRequest, DuckDbQueryResponse, Pong, TableRef, \
    DuckDbProcessCsvFileResponse
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

    @router.post("/duckdb/files")
    async def create_file(
            duckdb_table_ref: TableRef = Form(...),
            file: UploadFile = File(...),
    ) -> DuckDbProcessCsvFileResponse:
        file_to_save = await file.read()

        tmp_path = f"{CONFIG.temp_dir}/temp-{random.randint(0, 1_000_000)}.csv"

        with open(tmp_path, 'wb') as f:
            f.write(file_to_save)

        ref_group = duckdb.process_new_csv_file_to_gcs_parquet(
            csv_path=tmp_path,
            table_name=duckdb_table_ref,
        )

        return DuckDbProcessCsvFileResponse(
            ref_group=ref_group,
        )

    return router


def import_csv_files() -> None:
    """The following are loaded into DuckDB's memory"""
    duckdb.import_csv_file(path="./data/president_polls.csv", table_ref="president_polls", )
    duckdb.import_csv_file(path="./data/president_polls_historical.csv", table_ref="president_polls_historical", )


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

    return app

import_csv_files()
app = get_app_instance()
