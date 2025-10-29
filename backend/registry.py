import datetime
import os

from backend.storage.db.redis_client import (
    get_async_redis_backend,
    get_sync_redis_broker,
    get_sync_redis_backend,
)

server_started = datetime.datetime.now()
VERSION = os.getenv("VERSION", "0")
ENV = os.environ.get("ENV", "LOCAL")

async_backend_redis = get_async_redis_backend()

backend_redis = get_sync_redis_broker()
broker_redis = get_sync_redis_backend()
