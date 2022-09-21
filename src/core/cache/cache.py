from functools import wraps

from core.cache.backend import RedisBackend
from core.cache.key_marker import CustomKeyMaker


class CacheManager:
    def __init__(self, backend: RedisBackend, key_maker: CustomKeyMaker):
        self.backend = backend
        self.key_maker = key_maker

    def cached(self, prefix: str, ttl: int = 60):
        def _cached(function):
            @wraps(function)
            async def __cached(*args, **kwargs):
                if not self.backend or not self.key_maker:
                    raise Exception("backend or key_maker is None")

                key = await self.key_maker.make(function=function, prefix=prefix)
                cached_response = await self.backend.get(key=key)
                if cached_response:
                    return cached_response

                response = await function(*args, **kwargs)
                await self.backend.set(response=response, key=key, ttl=ttl)
                return response

            return __cached

        return _cached
