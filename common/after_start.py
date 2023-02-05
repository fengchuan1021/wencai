import asyncio
import os

from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import AsyncSession

import Service
import elasticsearchclient
import settings

from component.cache import cache
from component.dbsession import getdbsession
from component.snowFlakeId import snowFlack

async def init(db:AsyncSession):
    cookie = await Service.configService.findOne(db, {'config_name': 'cookie'})
    if cookie:
        await Service.wencaiService.updateCookie(cookie.config_value)
    configs=await Service.configService.find(db,{'config_name__ne': 'cookie'})
    await Service.wencaiService.updateBasicconfig({config.config_name:config.config_value for config in configs})
async def after_start(db: AsyncSession = None) -> None:
    await cache.init(prefix=settings.CACHE_PREFIX, expire=settings.DEFAULT_CACHE_EXPIRE, enable=settings.ENABLE_CACHE,
                     writeurl=settings.REDISURL,
                     readurl=settings.SLAVEREDISURL,
                     ignore_arg_types=[settings.UserTokenData],

                     )
    snowFlack.init(settings.NODEID)
    if db:
        await init(db)
    else:
        async with getdbsession() as dbclient:
            db=dbclient.session
            await init(db)


    elasticsearchclient.es = AsyncElasticsearch([settings.ELASTICSEARCHURL])
