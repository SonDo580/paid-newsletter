from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from fastapi import Depends
from typing import Annotated

from app.config.settings import settings

arq_redis_pool: ArqRedis | None = None


async def init_arq_redis() -> ArqRedis:
    global arq_redis_pool
    arq_redis_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    return arq_redis_pool


async def close_arq_redis():
    global arq_redis_pool
    if arq_redis_pool:
        await arq_redis_pool.close()


def get_arq_redis() -> ArqRedis:
    if not arq_redis_pool:
        raise RuntimeError("ARQ Redis pool has not been initialized")
    return arq_redis_pool


ArqRedisDep = Annotated[ArqRedis, Depends(get_arq_redis)]
