import pandas as pd
import typing as t

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from api.counter import StatefulCounter
from api.duck_wrapper import DuckCore
from api.types import PeakResponse, IncrementResponse, DuckDbQueryRequest

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
    async def execute_query(req: DuckDbQueryRequest) -> str:
        df: pd.DataFrame = duck_core.execute_as_df(query_str=req.query_str)
        return df.to_json(orient="columns")

    return router



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

    duck_core.import_csv_file(path="./tests/data/president_polls.csv", table_name="president_polls")

    return app


app = get_app_instance()
