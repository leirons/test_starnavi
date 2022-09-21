import aioredis

from core.config import settings

redis = aioredis.from_url(url=settings.REDIS_HOST)
