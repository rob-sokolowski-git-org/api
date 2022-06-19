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


class DuckDbQueryResponse(BaseModel):
    # NB: Union type ordering matters!! Basic idea is work from specific to generic, unsure if this is a "good enough"
    #     solution or not
    #
    # Counterpoint: Zip codes with leading zeros won't work with this solution
    #               but custom typing in BaseModel might be manageable, when needed
    #
    # Another note: After implementing this solution, select * from president_polls went from ~40ms to ~70ms for
    #               a warmed-up approx latency metric. There is not enough info at this time to conclude it's due to
    #               the serialization, as the "columns 'just json string'" format was about 50% greater, in bytes
    data:     t.Dict[str, t.List[t.Union[Decimal, pd.Timestamp, str]]]
    metadata: t.Dict[str, t.List[t.Union[Decimal, pd.Timestamp, str]]]
