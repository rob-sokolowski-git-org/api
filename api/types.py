import pandas as pd
import typing as t

from pydantic import BaseModel
from pydantic.json import Decimal


class IncrementResponse(BaseModel):
    value_was: int
    value_is: int


class PeakResponse(BaseModel):
    value: int


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
