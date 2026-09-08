from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.cost_handlers import router as cost_router


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)
app.include_router(cost_router)
