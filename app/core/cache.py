import json
from typing import Optional
import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()


class RedisCache:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[str]:
        if not self.redis_client:
            return None
        return await self.redis_client.get(key)

    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        if not self.redis_client:
            return False
        return await self.redis_client.set(key, value, ex=expire)

    async def delete(self, key: str) -> bool:
        if not self.redis_client:
            return False
        return await self.redis_client.delete(key) > 0

    async def get_json(self, key: str) -> Optional[dict]:
        data = await self.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_json(self, key: str, value: dict, expire: int = 3600) -> bool:
        return await self.set(key, json.dumps(value), expire)


cache = RedisCache()
