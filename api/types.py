from dataclasses import dataclass
from dataclasses_json import dataclass_json

import pandas as pd
import typing as t

from pydantic import BaseModel
from pydantic.json import Decimal

from env_config import EnvironmentConfig, CONFIG


# begin region internal types

# I'm not sure where I want to put these types yet, putting them in core.py introduces cyclic imports
TableRef = t.NewType("TableRef", str)

@dataclass_json
@dataclass(frozen=True)
class TableRefGroup:
    ref: TableRef
    bucket_name: str
    parquet_key: str

    @staticmethod
    def from_ref(table_ref: TableRef, env_config: EnvironmentConfig=CONFIG) -> "TableRefGroup":
        return TableRefGroup(
            ref=table_ref,
            bucket_name=env_config.bucket_name,
            parquet_key=f"{table_ref}.parquet",
        )

# end region internal types


class Pong(BaseModel):
    """used for dev-utilities, and healthchecks"""
    message: str = "PONG!"


class DuckDbQueryRequest(BaseModel):
    query_str: str
    fallback_table_refs: t.List[TableRef]
    allow_blob_fallback: bool


class DefaultColumn(BaseModel):
    name: str
    type: str
    values: t.List[t.Union[
        t.Optional[Decimal],
        t.Optional[pd.Timestamp],
        t.Optional[str]],
    ]


class VarcharColumn(DefaultColumn):
    values: t.List[t.Optional[str]]


class IntegerColumn(DefaultColumn):
    values: t.List[t.Optional[int]]


class BooleanColumn(DefaultColumn):
    values: t.List[t.Optional[bool]]


class DoubleColumn(DefaultColumn):
    values: t.List[t.Optional[float]]

class DuckDbQueryResponse(BaseModel):
    columns: t.List[DefaultColumn]


class DuckDbProcessCsvFileResponse(BaseModel):
    ref_group: TableRefGroup


class DuckDbTableRefsResponse(BaseModel):
    """HTTP response to querying a list of table ref ids"""
    refs: t.List[TableRef]


class DuckDbTableRefGroupResponse(BaseModel):
    """HTTP response for a full ref_gorup, given a ref id"""
    ref_group: TableRefGroup
