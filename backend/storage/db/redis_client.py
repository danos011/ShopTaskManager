import logging
from typing import Optional
import redis.asyncio as redis

from backend.config import CONFIG

logger = logging.getLogger(__name__)


def get_redis() -> "AsyncRedisClient":
    """Получить singleton инстанс асинхронного Redis клиента"""
    return AsyncRedisClient()


class AsyncRedisClient:
    _instance: Optional["AsyncRedisClient"] = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        if not self._client:
            try:
                self._client = redis.Redis(
                    host=CONFIG.redis_host,
                    port=CONFIG.redis_port,
                    db=CONFIG.redis_db,
                    password=CONFIG.redis_password,
                    max_connections=CONFIG.redis_max_connections,
                    socket_timeout=CONFIG.redis_socket_timeout,
                    decode_responses=CONFIG.redis_decode_responses,
                    health_check_interval=30,
                )
                await self._client.ping()
                logger.info("Async Redis connection opened")
            except Exception as error:
                logger.exception(f"Async Redis connection error: {error}")
                raise

    async def get(self, key: str) -> Optional[str]:
        if not self._client:
            await self.connect()
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.exception(f"Redis async GET error for key '{key}': {e}")
            raise

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        if not self._client:
            await self.connect()
        try:
            return await self._client.set(key, value, ex=ex)
        except Exception as e:
            logger.exception(f"Redis async SET error for key '{key}': {e}")
            raise

    async def delete(self, *keys: str) -> int:
        if not self._client:
            await self.connect()
        try:
            return await self._client.delete(*keys)
        except Exception as e:
            logger.exception(f"Redis async DELETE error: {e}")
            raise

    async def close(self) -> None:
        if self._client:
            try:
                await self._client.close()
                logger.info("Async Redis connection closed")
            except Exception as e:
                logger.exception(f"Async Redis close error: {e}")
