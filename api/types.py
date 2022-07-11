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


class IncrementResponse(BaseModel):
    value_was: int
    value_is: int


class PeakResponse(BaseModel):
    value: int


class Pong(BaseModel):
    message: str = "PONG!"


class DuckDbQueryRequest(BaseModel):
    query_str: str
    fallback_table_refs: t.List[TableRef]
    allow_blob_fallback: bool


class Column(BaseModel):
    # NB: Union type ordering matters!! Basic idea is work from specific to generic, unsure if this is a "good enough"
    #     solution or not
    #
    # Counterpoint: Zip codes with leading zeros won't work with this solution
    #               but custom typing in BaseModel might be manageable, when needed
    #
    #
    #    values: t.List[t.Union[
        # t.Optional[Decimal],
        # t.Optional[pd.Timestamp],
      #  t.Optional[str]],
    #
    #
    name: str
    type: str
    values: t.List[t.Optional[str]]


class DuckDbQueryResponse(BaseModel):
    columns: t.List[Column]


class DuckDbProcessCsvFileResponse(BaseModel):
    ref_group: TableRefGroup


class DuckDbTableRefsResponse(BaseModel):
    """HTTP response to querying a list of table ref ids"""
    refs: t.List[TableRef]


class DuckDbTableRefGroupResponse(BaseModel):
    """HTTP response for a full ref_gorup, given a ref id"""
    ref_group: TableRefGroup
