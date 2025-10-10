import logging
from typing import Optional, Dict
import redis

from backend.config import CONFIG
from backend.utils import throw_server_error

logger = logging.getLogger(__name__)


class RedisClient:
    _instances: Dict[int, "RedisClient"] = {}

    def __init__(self, db: int):
        self.db = db
        self._client: Optional[redis.Redis] = None
        self._pool: Optional[redis.ConnectionPool] = None

    def __new__(cls, db: int):
        if db not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[db] = instance
        return cls._instances[db]

    def connect(self) -> None:
        if not self._pool:
            try:
                self._pool = redis.ConnectionPool(
                    host=CONFIG.redis_host,
                    port=CONFIG.redis_port,
                    db=self.db,
                    password=None,
                    max_connections=CONFIG.redis_max_connections,
                    socket_timeout=CONFIG.redis_socket_timeout,
                    decode_responses=CONFIG.redis_decode_responses,
                    socket_keepalive=True,
                    health_check_interval=30,
                )
                self._client = redis.Redis(connection_pool=self._pool)
                self._client.ping()
                logger.info(f"Redis connection opened for db={self.db}")
            except redis.ConnectionError as error:
                logger.exception(f"Failed to connect to Redis db={self.db}: {error}")
                print(f"Failed to connect to Redis db={self.db}: {error}")
                raise throw_server_error(
                    f"Failed to connect to Redis db={self.db}: {error}"
                )
            except Exception as error:
                print(f"Failed to connect to Redis db={self.db}: {error}")
                logger.exception(
                    f"Unexpected error connecting to Redis db={self.db}: {error}"
                )
                raise throw_server_error(
                    f"Unexpected error connecting to Redis db={self.db}: {error}"
                )

    @property
    def client(self) -> redis.Redis:
        if not self._client:
            self.connect()
        try:
            self._client.ping()
        except (redis.ConnectionError, redis.TimeoutError):
            print(f"Redis connection lost for db={self.db}, reconnecting...")
            logger.warning(f"Redis connection lost for db={self.db}, reconnecting...")
            self.connect()
        return self._client

    def get(self, key: str) -> Optional[str]:
        try:
            return self.client.get(key)
        except Exception as e:
            logger.exception(f"Redis GET error for key '{key}': {e}")
            raise throw_server_error(f"Redis GET error: {e}")

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        try:
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.exception(f"Redis SET error for key '{key}': {e}")
            raise throw_server_error(f"Redis SET error: {e}")

    def delete(self, *keys: str) -> int:
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.exception(f"Redis DELETE error: {e}")
            raise throw_server_error(f"Redis DELETE error: {e}")

    def exists(self, *keys: str) -> int:
        try:
            return self.client.exists(*keys)
        except Exception as e:
            logger.exception(f"Redis EXISTS error: {e}")
            raise throw_server_error(f"Redis EXISTS error: {e}")

    def hget(self, name: str, key: str) -> Optional[str]:
        try:
            return self.client.hget(name, key)
        except Exception as e:
            logger.exception(f"Redis HGET error: {e}")
            raise throw_server_error(f"Redis HGET error: {e}")

    def hset(self, name: str, key: str, value: str) -> int:
        try:
            return self.client.hset(name, key, value)
        except Exception as e:
            logger.exception(f"Redis HSET error: {e}")
            raise throw_server_error(f"Redis HSET error: {e}")

    def hgetall(self, name: str) -> dict:
        try:
            return self.client.hgetall(name)
        except Exception as e:
            logger.exception(f"Redis HGETALL error: {e}")
            raise throw_server_error(f"Redis HGETALL error: {e}")

    def close(self) -> None:
        if self._pool:
            try:
                self._pool.disconnect()
                logger.info(f"Redis connection closed for db={self.db}")
            except Exception as e:
                logger.exception(f"Error closing Redis connection: {e}")
                raise throw_server_error(f"Error closing Redis connection: {e}")

    def keys(self, pattern: str) -> list[str]:
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.exception(f"Redis KEYS error for pattern '{pattern}': {e}")
            raise throw_server_error(f"Redis KEYS error for pattern '{pattern}': {e}")

    def scan_iter(self, pattern: str, count: int = 100):
        """
        Итератор для сканирования ключей (не блокирует Redis).
        Рекомендуется для продакшена.

        Args:
            pattern: Паттерн для поиска ключей (например, "stock:*")
            count: Количество ключей за одну итерацию (по умолчанию 100)

        Yields:
            Ключи, подходящие под паттерн
        """
        try:
            for key in self.client.scan_iter(match=pattern, count=count):
                if isinstance(key, bytes):
                    yield key.decode()
                else:
                    yield key
        except Exception as e:
            logger.exception(f"Redis SCAN error for pattern '{pattern}': {e}")
            raise

    def scan_keys(self, pattern: str, count: int = 100) -> list[str]:
        """
        Получить список ключей через SCAN (не блокирует Redis).
        Обёртка над scan_iter для удобства.
        """
        try:
            return list(self.scan_iter(pattern, count))

        except Exception as e:
            logger.exception(f"Redis SCAN_KEYS error for pattern '{pattern}': {e}")
            raise throw_server_error(
                f"Redis SCAN_KEYS error for pattern '{pattern}': {e}"
            )


# Фабричные функции
def get_redis_broker() -> RedisClient:
    """Redis клиент для брокера Celery (db=0)"""
    return RedisClient(db=0)


def get_redis_backend() -> RedisClient:
    """Redis клиент для результатов Celery (db=1)"""
    return RedisClient(db=1)
