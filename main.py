from fastapi import FastAPI

from api.cost_api import router as cost_router
from api.user_api import router as user_router

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(cost_router)
app.include_router(user_router)
