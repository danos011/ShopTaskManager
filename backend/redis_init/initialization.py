from backend.registry import backend_redis


def redis_ini():
    backend_redis.set("stock:iphone", 50)
    backend_redis.set("stock:macbook", 7)
