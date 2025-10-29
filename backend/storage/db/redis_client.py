import logging

from redis.asyncio import Redis, ConnectionPool
import redis as redis_sync

from backend.config import CONFIG
from backend.utils import throw_server_error

logger = logging.getLogger(__name__)


class RedisClient:
    _instance: "RedisClient" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._client: Redis | None = None
        self._pool: ConnectionPool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            try:
                self._pool = ConnectionPool(
                    host=CONFIG.redis_host,
                    port=CONFIG.redis_port,
                    db=0,
                    password=None,
                    max_connections=CONFIG.redis_max_connections,
                    socket_timeout=CONFIG.redis_socket_timeout,
                    decode_responses=CONFIG.redis_decode_responses,
                    socket_keepalive=True,
                    health_check_interval=30,
                )
                self._client = Redis(connection_pool=self._pool)
                await self._client.ping()
                logger.info("Redis connection opened")
            except Exception as error:
                logger.exception(f"Failed to connect to Redis: {error}")
                raise throw_server_error(f"Failed to connect to Redis: {error}")

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError(
                "Redis client is not connected. Call await connect() first."
            )
        return self._client

    async def ensure_connected(self) -> None:
        if self._client is None:
            await self.connect()
        try:
            await self._client.ping()
        except Exception:
            logger.warning("Redis connection lost, reconnecting...")
            await self.connect()

    async def get(self, key: str) -> str | bytes | None:
        await self.ensure_connected()
        value = await self.client.get(key)
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        await self.ensure_connected()
        return await self.client.set(key, value, ex=ex)

    async def delete(self, *keys: str) -> int:
        await self.ensure_connected()
        return await self.client.delete(*keys)

    async def exists(self, *keys: str) -> int:
        await self.ensure_connected()
        return await self.client.exists(*keys)

    async def hget(self, name: str, key: str) -> str | None:
        await self.ensure_connected()
        value = await self.client.hget(name, key)
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    async def hset(self, name: str, key: str, value: str) -> int:
        await self.ensure_connected()
        return await self.client.hset(name, key, value)

    async def hgetall(self, name: str) -> dict[str, any]:
        await self.ensure_connected()
        return await self.client.hgetall(name)

    async def keys(self, pattern: str) -> list[str]:
        await self.ensure_connected()
        keys = await self.client.keys(pattern)
        return [k if isinstance(k, str) else k.decode() for k in keys]

    async def scan_iter(self, pattern: str, count: int = 100):
        await self.ensure_connected()
        async for key in self.client.scan_iter(match=pattern, count=count):
            yield key if isinstance(key, str) else key.decode()

    async def scan_keys(self, pattern: str, count: int = 100) -> list[str]:
        results: list[str] = []
        async for key in self.scan_iter(pattern, count):
            results.append(key)
        return results

    async def close(self) -> None:
        if self._client:
            try:
                await self._client.close()
            except Exception:
                pass
        if self._pool:
            try:
                await self._pool.disconnect(inuse_connections=True)
                logger.info("Redis connection closed")
            except Exception as e:
                logger.exception(f"Error closing Redis connection: {e}")
                raise throw_server_error(f"Error closing Redis connection: {e}")


class SyncRedisClient:
    _instances: dict[int, "SyncRedisClient"] = {}

    def __new__(cls, db: int):
        if db not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[db] = instance
        return cls._instances[db]

    def __init__(self, db: int):
        self.db = db
        self._client: redis_sync.Redis | None = None
        self._pool: redis_sync.ConnectionPool | None = None

    def connect(self) -> None:
        if self._pool is None:
            self._pool = redis_sync.ConnectionPool(
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
            self._client = redis_sync.Redis(connection_pool=self._pool)
            self._client.ping()
            logger.info(f"Sync Redis connection opened for db={self.db}")

    @property
    def client(self) -> redis_sync.Redis:
        if self._client is None:
            raise RuntimeError("Redis client is not connected. Call connect() first.")
        return self._client

    def ensure_connected(self) -> None:
        if self._client is None:
            self.connect()
        else:
            try:
                self._client.ping()
            except Exception:
                logger.warning(
                    f"Sync Redis connection lost for db={self.db}, reconnecting..."
                )
                self.connect()

    # Методы совместимы по именам с async-версией, но синхронные
    def get(self, key: str):
        self.ensure_connected()
        return self.client.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> bool:
        self.ensure_connected()
        return self.client.set(key, value, ex=ex)

    def delete(self, *keys: str) -> int:
        self.ensure_connected()
        return self.client.delete(*keys)

    def exists(self, *keys: str) -> int:
        self.ensure_connected()
        return self.client.exists(*keys)

    def hget(self, name: str, key: str):
        self.ensure_connected()
        return self.client.hget(name, key)

    def hset(self, name: str, key: str, value: str) -> int:
        self.ensure_connected()
        return self.client.hset(name, key, value)

    def hgetall(self, name: str) -> dict[str, str]:
        self.ensure_connected()
        return self.client.hgetall(name)

    def keys(self, pattern: str) -> list[str]:
        self.ensure_connected()
        keys = self.client.keys(pattern)
        return [k if isinstance(k, str) else k.decode() for k in keys]

    def close(self) -> None:
        if self._pool:
            try:
                self._pool.disconnect(inuse_connections=True)
                logger.info(f"Sync Redis connection closed for db={self.db}")
            except Exception as e:
                logger.exception(f"Error closing Sync Redis connection: {e}")
                raise throw_server_error(f"Error closing Sync Redis connection: {e}")


def get_async_redis_backend() -> RedisClient:
    return RedisClient()


def get_sync_redis_broker() -> SyncRedisClient:
    return SyncRedisClient(db=0)


def get_sync_redis_backend() -> SyncRedisClient:
    return SyncRedisClient(db=1)
