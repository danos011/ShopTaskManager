import datetime
import os

from backend.storage.db.redis_client import get_redis

server_started = datetime.datetime.now()
VERSION = os.getenv("VERSION", "0")
ENV = os.environ.get("ENV", "LOCAL")

db_redis = get_redis()
