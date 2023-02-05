import settings
from fastapi import Request
from jose import jwt

from common.CommonError import TokenException
from component.snowFlakeId import snowFlack
import asyncio
import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from functools import wraps
from typing import Callable, Any
import elasticsearchclient
from component.cache import cache


async def getorgeneratetoken(request: Request) -> settings.UserTokenData:
    try:
        return await get_token(request)
    except Exception as e:
        guest_token = settings.UserTokenData(user_id=snowFlack.getId(), is_guest=False,role_id=1)
        return guest_token


async def get_token(request: Request) -> settings.UserTokenData:
    if tmp := request.state._state.get('token', None):
        return tmp

    try:
        tokenstr = request.headers.get('Authorization', None)
        if not tokenstr:
            tokenstr = request.cookies.get('token', None)

        if tokenstr:
            payload = jwt.decode(tokenstr, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            data = settings.UserTokenData.parse_obj(payload)
            request.state.token = data
            return data
        else:
            raise Exception("has not token in header or cookie")
    except Exception as e:
        print("eee:", e)
        raise TokenException(str(e))


async def writelog(logstr: str, request: str = '') -> None:
    if elasticsearchclient.es:
        doc = {
            'text': logstr,
            'request': request,
            'timestamp': datetime.datetime.now(),
        }
        await elasticsearchclient.es.index(index=f"xtlog-{settings.MODE.lower()}", document=doc)


def cmdlineApp(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> Any:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            print("3333333333333333333333333")
            from common.after_start import after_start
            from component import dbsession
            dbsession.engines = {
                'master': create_async_engine(settings.DBURL, echo=settings.DEBUG),
                'slaver': create_async_engine(settings.SLAVEDBURL, echo=settings.DEBUG),
            }
            dbclient = dbsession.getdbsession(token=None)

            loop.run_until_complete(after_start(dbclient.session))
            result = loop.run_until_complete(func(dbclient.session, *args, **kwargs))
            loop.run_until_complete(dbclient.__aexit__())

            async def closeengines() -> None:
                [await engine.dispose() for engine in dbsession.engines.values()]

            loop.run_until_complete(closeengines())

            return result
        except Exception as e:
            loop.run_until_complete(dbclient.__aexit__())
            loop.run_until_complete(writelog(str(e)))
            if settings.DEBUG:
                raise

    return decorator
