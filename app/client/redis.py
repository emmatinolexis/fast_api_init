from redis.asyncio import Redis
import json
from uuid import UUID
from app.util.class_object import singleton
from app.core.settings import settings
from fastapi.encoders import jsonable_encoder


@singleton
class RedisClient:
    def __init__(self):
        self.client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,
        )

    def get_client(self) -> Redis:
        return self.client

    async def get_cache(self, key: str):
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_cache(self, key: str, value, expire: int = 60 * 60 * 24):  # 24 hours
        # safe_value = convert_uuids(value)
        await self.client.set(key, json.dumps(jsonable_encoder(value)), ex=expire)

    async def delete_cache(self, key: str):
        await self.client.delete(key)

    async def delete_by_pattern(self, pattern: str):
        keys = await self.client.keys(pattern)
        if keys:
            await self.client.delete(*keys)
