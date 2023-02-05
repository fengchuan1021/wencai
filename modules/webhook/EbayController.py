

from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any

from fastapi import APIRouter, Header, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import Service
import settings
from component.dbsession import get_webdbsession
from .__init__ import dependencies
from dateutil import parser
router = APIRouter(dependencies=dependencies)

@router.get('/webhook/ebay/authed')
async def authed_callback(state:str,code:str,db: AsyncSession = Depends(get_webdbsession),)->Any:
    store=await Service.ebayService.getAccessToken(db,state,code)#type: ignore

    return {'status':"success",'token':store.token}
