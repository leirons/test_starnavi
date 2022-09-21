import pickle
from typing import Any

import ujson

from core.cache.redis import redis


class RedisBackend:
    async def get(self, key: str) -> Any:
        result = await redis.get(key)
        if not result:
            return False

        try:
            return ujson.loads(result.decode("utf8"))
        except UnicodeDecodeError:
            return pickle.loads(result)

    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        if isinstance(response, dict):
            response = ujson.dumps(response)
        elif isinstance(response, object):
            response = pickle.dumps(response)

        await redis.set(name=key, value=response, ex=ttl)
