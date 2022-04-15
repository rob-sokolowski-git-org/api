from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from api.counter import StatefulCounter
from api.types import PeakResponse, IncrementResponse


counter = StatefulCounter()


def counter_router() -> APIRouter:
    router = APIRouter()

    @router.get("/counter")
    def peak_at_value() -> PeakResponse:
        return PeakResponse(value=counter.value)

    @router.post("/counter")
    def increment_value() -> IncrementResponse:
        was = counter.value
        counter.increment()
        is_ = counter.value
        return IncrementResponse(
            value_was=was,
            value_is=is_,
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
