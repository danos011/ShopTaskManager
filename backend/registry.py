import datetime
import os

from backend.storage.db.redis_client import get_redis_broker, get_redis_backend

server_started = datetime.datetime.now()
VERSION = os.getenv("VERSION", "0")
ENV = os.environ.get("ENV", "LOCAL")

broker_redis = get_redis_broker()
backend_redis = get_redis_backend()
