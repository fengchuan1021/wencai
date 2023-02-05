from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, Union, List

import jwt
from fastapi import APIRouter, Depends, Body, WebSocket, Cookie, Query, Header, WebSocketException, status

import settings
from component.cache import cache
import orjson

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             cookietoken: Union[str, None] = Cookie(default=None),
                             headertoken: Union[str, None] = Header(default=None),
                             querytoken: Union[str, None] = Query(default=None),

                             ) -> Any:
    try:

        tokenstr = querytoken or cookietoken or headertoken or ''

        payload = jwt.decode(tokenstr, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])  # type: ignore
        token: settings.UserTokenData = settings.UserTokenData.parse_obj(payload)
        user_id = token.user_id
        print('user-id:', user_id)
    except Exception as e:
        print('108', e)


    try:
        await websocket.accept()
        flag = 1

        async def send() -> None:
            nonlocal flag
            while flag:

                try:
                    subscribe=cache.read_redis.pubsub()
                    await subscribe.subscribe('common')
                    while 1:
                        result=await subscribe.get_message(ignore_subscribe_messages=True,timeout=3)
                        print('222')
                        print('result',result)
                        if result:
                        #msg=await ch.get_message()
                            await websocket.send_text(result['data'].decode())


                except Exception as e:
                    print('53',e)
                    flag = 0

        async def recv() -> None:
            nonlocal flag
            while flag:
                try:
                    data = await websocket.receive_json()
                    print('data', data)
                    if data['cmd'] == 'heartbeat':
                        await websocket.send_json(data)
                        continue
                except Exception as e:
                    flag = 0

        await asyncio.wait([send(), recv()])


    except Exception as e:
        flag = 0
        print(112, e)
