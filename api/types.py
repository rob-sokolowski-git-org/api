from dataclasses import dataclass

import pandas as pd
import typing as t

from pydantic import BaseModel
from pydantic.json import Decimal

from env_config import EnvironmentConfig, CONFIG


# begin region internal types
# I'm not sure where I want to put these types yet, putting them in core.py introduces cyclic imports
TableRef = t.NewType("TableRef", str)


@dataclass(frozen=True)
class TableRefGroup:
    ref: TableRef
    bucket_name: str
    parquet_key: str
    firestore_collection_name: str

    @staticmethod
    def from_ref(table_ref: TableRef, env_config: EnvironmentConfig=CONFIG) -> "TableRefGroup":
        return TableRefGroup(
            ref=table_ref,
            bucket_name=env_config.bucket_name,
            firestore_collection_name=env_config.firestore_duckdb_refs_collection,
            parquet_key=f"{table_ref}.parquet",
        )

# end region internal types


class Pong(BaseModel):
    message: str = "PONG!"


class DuckDbQueryRequest(BaseModel):
    query_str: str


class Column(BaseModel):
    # NB: Union type ordering matters!! Basic idea is work from specific to generic, unsure if this is a "good enough"
    #     solution or not
    #
    # Counterpoint: Zip codes with leading zeros won't work with this solution
    #               but custom typing in BaseModel might be manageable, when needed
    name: str
    type: str
    values: t.List[t.Union[Decimal, pd.Timestamp, str]]


class DuckDbQueryResponse(BaseModel):
    columns: t.List[Column]


class DuckDbProcessCsvFileResponse(BaseModel):
    ref_group: TableRefGroup
