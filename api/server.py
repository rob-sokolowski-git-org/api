import pandas as pd
import time
import typing as t


from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Response

from api.counter import StatefulCounter
from api.duck_rapper import DuckRapper
from api.types import PeakResponse, IncrementResponse, DuckDbQueryRequest, DuckDbQueryResponse
from fastapi.responses import JSONResponse

counter = StatefulCounter()
duckdb = DuckRapper()


def counter_router() -> APIRouter:
    router = APIRouter()

    @router.get("/counter")
    async def peak_at_value() -> PeakResponse:
        return PeakResponse(value=counter.value)

    @router.post("/counter")
    async def increment_value() -> IncrementResponse:
        was = counter.value
        counter.increment()
        is_ = counter.value
        return IncrementResponse(
            value_was=was,
            value_is=is_,
        )

    return router


def duckdb_router() -> APIRouter:
    router = APIRouter()

    @router.post("/duckdb")
    async def execute_query(req: DuckDbQueryRequest) -> DuckDbQueryResponse:
        df, df_meta = duckdb.execute_as_df_with_meta_data(query_str=req.query_str)

        return duckdb.map_response(df_data=df, df_metadata=df_meta)

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

    app.include_router(counter_router())
    app.include_router(duckdb_router())

    return app

import_csv_files()
app = get_app_instance()
