import pandas as pd
import time
import typing as t


from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import Response

from api.counter import StatefulCounter
from api.duck_wrapper import DuckCore
from api.types import PeakResponse, IncrementResponse, DuckDbQueryRequest, DuckDbQueryResponse
from fastapi.responses import JSONResponse

counter = StatefulCounter()
duck_core = DuckCore()


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
        tic = time.perf_counter()
        df: pd.DataFrame = duck_core.execute_as_df(query_str=req.query_str)
        toc = time.perf_counter()
        print(f"{toc-tic} secs")

        return DuckDbQueryResponse(
            data=df.to_dict(orient="list")
        )
    return router


def import_csv_files() -> None:
    """The following are loaded into DuckDB's memory"""
    duck_core.import_csv_file(path="./data/president_polls.csv", table_name="president_polls", )
    duck_core.import_csv_file(path="./data/president_polls_historical.csv", table_name="president_polls_historical", )


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
