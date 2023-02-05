import random
import string
import time

import orjson
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from common.CommonError import ResponseException
from common.after_start import after_start
from component.dbsession import getdbsession

if settings.MODE == 'DEV':
    import subprocess
    import sys

    subprocess.Popen([sys.executable, "devtools/debugtools.py"], stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, close_fds=True)

import fastapi.exceptions
import asyncio
import os

os.environ['TZ'] = 'UTC'
if os.name != 'nt':
    time.tzset()  # type: ignore
from sqlalchemy.exc import IntegrityError, OperationalError
import importlib
from typing import Any
from fastapi import FastAPI, Request
from redis.exceptions import ConnectionError
from common import Common500Response, TokenException, PermissionException, XTJsonResponse, writelog, getorgeneratetoken
from component.snowFlakeId import snowFlack
from component.cache import cache
from pathlib import Path

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
import platform


if 'linux' in platform.platform().lower():
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
elif 'windows' in platform.platform().lower():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from starlette.background import BackgroundTask

app = FastAPI(redoc_url=None if settings.MODE == 'main' else '/redoc',
              docs_url=None if settings.MODE == 'main' else '/docs',
              openapi_url=None if settings.MODE == 'main' else '/openapi.json')
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"], )


@app.middleware("http")
async def validate_tokenandperformevent(request: Request, call_next: Any) -> Response:
    # request.state.token=await getorgeneratetoken(request)

    try:
        response = await call_next(request)  # This request will be modified and sent
        if db_client := request.state._state.get('db_client', None):
            await db_client.session.commit()
            backgroundtasks = BackgroundTask(db_client.close, skipcommit=True)
            response.background = backgroundtasks
    except OperationalError as e:
        jsonout = Common500Response(errorcode=500, data=str(e), errormsg='dberror')
        response = XTJsonResponse(jsonout, status_code=200)
        # try:
        #     await request.state.db_client.close()
        # except:
        #     pass
    except IntegrityError as e:
        await request.state._state.get('db_client').session.rollback()  # type: ignore
        jsonout = Common500Response(errorcode=500, data=str(e), errormsg='dberror')
        response = XTJsonResponse(jsonout, status_code=200)
        # try:
        #     await request.state.db_client.close()
        # except:
        #     pass
    except TokenException as e:

        jsonout = Common500Response(errorcode=401, errormsg='tokenerror', data=str(e))
        response = XTJsonResponse(jsonout, status_code=200)
    except PermissionException as e:
        jsonout = Common500Response(errorcode=500, data=str(e), errormsg='no access permission')
        response = XTJsonResponse(jsonout, status_code=200)
    except fastapi.exceptions.ValidationError as e:
        jsonout = Common500Response(errorcode=500, errormsg='validateerror', data=e.errors())
        response = XTJsonResponse(jsonout, status_code=200)
    except  ConnectionError as e:
        jsonout = Common500Response(errorcode=500, errormsg='cacheerror', data=str(e))
        response = XTJsonResponse(jsonout, status_code=200)

    except ResponseException as e:
        response = XTJsonResponse(e.response)
    except Exception as e:
        # es
        print(e)
        # await writelog(str(e),request=str(request))

        if settings.DEBUG:
            raise

        jsonout = Common500Response(errorcode=500, errormsg='unknownerr', data=str(e))
        response = XTJsonResponse(jsonout, status_code=200)

    # if request.state.token.is_guest:
    #    response.set_cookie('token',Service.userService.create_access_token(request.state.token),expires=3600*24*30)
    return response

async def test():
    while 1:

        await cache.write_redis.publish("common",orjson.dumps(
            {"cmd":"strategyinfo",
             "data":{f"D{random.randint(1,8)}":{"flushtimes":random.randint(100,999),
                                                'data':[{"code":'000001',
                                                         "rate":random.randint(10,100),
                                                         "name":''.join([random.choice(string.ascii_letters) for i in range(4)]),
                                                         "indestory":''.join([random.choice(string.ascii_letters) for i in range(4)]),
                                                         "indestorydetail":''.join([random.choice(string.ascii_letters) for i in range(4)]),
                                                         } for i in range(random.randint(20,100  )) ]

                                                }}
             }
        ))
        await asyncio.sleep(100)

@app.on_event("startup")
async def startup() -> None:
    await after_start()

    asyncio.create_task(test())


for f in Path(settings.BASE_DIR).joinpath('modules').rglob('*.py'):
    if f.name.endswith('Controller.py'):
        controller = importlib.import_module(
            str(f.relative_to(settings.BASE_DIR)).replace(os.sep, '.')[0:-3]
        )

        app.include_router(controller.router, prefix='/api')
if not settings.AZ_BLOB_CONNSTR:
    from fastapi.staticfiles import StaticFiles

    app.mount("/img", StaticFiles(directory="img"), name="img")


@app.get('/')
async def forazureping(request: Request) -> dict:  # , site: "Models.Site" =Depends(getSiteInfo)
    return {"status": 'success', 'hello': 'world'}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8001, log_level="info", reload=settings.DEBUG)
