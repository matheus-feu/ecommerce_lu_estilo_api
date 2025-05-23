import redis.asyncio as aioredis

from src.core.settings import settings

token_blocklist = aioredis.from_url(settings.redis.REDIS_URL)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=settings.redis.JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)

    return jti is not None
