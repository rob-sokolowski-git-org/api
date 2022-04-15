from pydantic import BaseModel


class IncrementResponse(BaseModel):
    value_was: int
    value_is: int


class PeakResponse(BaseModel):
    value: int
