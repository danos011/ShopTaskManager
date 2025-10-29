from backend.registry import async_backend_redis


async def redis_ini():
    await async_backend_redis.set("stock:iphone", 50)
    await async_backend_redis.set("stock:macbook", 7)
