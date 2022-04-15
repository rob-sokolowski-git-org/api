from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from api.counter import StatefulCounter

counter = StatefulCounter()
counter.increment(amnt=1)


from pydantic import BaseModel


class IncrementResponse(BaseModel):
    value_was: int
    value_is: int


class PeakResponse(BaseModel):
    value: int


def counter_router() -> APIRouter:
    router = APIRouter()

    @router.get("/counter")
    def peak_at_value() -> PeakResponse:
        return PeakResponse(value=counter.value)

    @router.post("/counter")
    def increment_value() -> PeakResponse:
        was = counter.value
        counter.increment()
        is_ = counter.value
        return IncrementResponse(
            value_was=was,
            value_is=is_
        )

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

  return app


app = get_app_instance()
