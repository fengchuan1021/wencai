# generated timestamp: 2023-01-09T02:44:24+00:00

from __future__ import annotations

import base64
import re
from typing import Any, Dict

from fastapi import APIRouter, Depends, Header, Body
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import Service
import settings
from common import CommonResponse, XTJsonResponse, get_token
from component.cache import cache
from component.dbsession import get_webdbsession
from component.fastQL import fastAdd, fastDel, fastQuery

from .__init__ import dependencies

router = APIRouter(dependencies=dependencies)


# <editor-fold desc="magentoorderchanged">
@router.post(
    '/webhook/magentoorderchanged/{store_id}',
)
async def magentoorderchanged(
        store_id: int,
        body: Dict = Body(),
        Authorization: str = Header(),

        db: AsyncSession = Depends(get_webdbsession)
) -> Any:
    """
    magentoorderchanged
    """
    try:
        print('Authorization', Authorization)
        up = Authorization.split(' ')[1]
        username, password = base64.b64decode(up).decode().split(':')

    except Exception as e:
        print(e)
        return {"errorcode": 500, "errormsg": "username or password not valid"}

    store = await Service.storeService.findByPk(db, store_id)

    if not store:
        return {"errorcode": 500, "errormsg": "store not found"}
    if not (store.verify_username == username and store.verify_password == password):
        return {"errorcode": 500, "errormsg": "invalid token"}

    print(body)
    ret = await Service.magentoService.magentoorderchanged(db, store, body, store.merchant_id)
    return ret

# </editor-fold>
