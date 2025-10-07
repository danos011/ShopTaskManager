"""
Main config file for FastAPI
"""

import logging.config
import multiprocessing
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware

from backend import api
from backend.registry import ENV

load_dotenv()

if ENV != "PROD":
    logging.config.fileConfig("backend/logging.conf")
else:
    logging.config.fileConfig("logging.conf")

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    process_name = multiprocessing.current_process().name
    logger.info(f"Process {process_name} started")
    logger.info("Server started")

    yield

    logger.info("Server shutting down")


app = FastAPI(lifespan=lifespan)
app.include_router(api.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["<domain-address>"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Shop Task manager API",
        version="0.1",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
