
from __future__ import annotations
from fastapi import Response
import asyncio
from typing import Any, Dict, Optional, Union, List

import jwt
from fastapi import APIRouter, Depends, Body, WebSocket, Cookie, Query, Header, WebSocketException, status
from sqlalchemy import text, delete
from sqlalchemy.dialects.mysql import insert

import Models
import Service
import settings
from component.cache import cache
import orjson

from Models import Config
from component.dbsession import get_webdbsession

router = APIRouter()
@router.get('/api/daychart/{code}/{begin}/{end}')
async def daychart(code:str,begin:str,end:str):
    data=await Service.sinaService.getHistoryDayData(code,begin,end)
    return data

@router.post('/updatecookie'
            )
async def updatecookie(body=Body(),
                       db=Depends(get_webdbsession)
                       ):
    if tmp:=body.get('cookie'):
        statmetn=insert(Config).values({'config_name':'cookie','config_value':tmp,'gp':'basic'}).on_duplicate_key_update({'config_value':tmp})

        await db.execute(statmetn)
        await Service.wencaiService.updateCookie(tmp)

@router.post('/getfrontconfig'
            )
async def getfrontconfig(
                       db=Depends(get_webdbsession)
                       ):
    models=await Service.configService.find(db,{'gp':'front'})
    dic={}
    for model in models:
        dic[model.config_name]=model.config_value
    return {'status':0,'data':dic}

@router.post('/getbasicconfig'
            )
async def getbasicconfig(
                       db=Depends(get_webdbsession)
                       ):
    models=await Service.configService.find(db,{'gp':'basic','config_name__ne':'cookie'})
    dic={}
    for model in models:
        dic[model.config_name]=model.config_value
    return {'status':0,'data':dic}


@router.post('/updatebasicconfig')
async def updatebasicconfig(body=Body(),
                       db=Depends(get_webdbsession)
                       ):

    #for key,value in body.items():
    statmetn=insert(Config).values([{'config_name':key,'config_value':value,'gp':'basic'} for key,value in body.items()]).on_duplicate_key_update(
        config_value=text("VALUES(config_value)")
    )

    await db.execute(statmetn)
    await Service.wencaiService.updateBasicconfig(body)

@router.post('/updatefrontconfig')
async def updatefrontconfig(body=Body(),
                       db=Depends(get_webdbsession)
                       ):

    statmetn=insert(Config).values([{'config_name':body['key'],'config_value':body['value'],'gp':'front'}]).on_duplicate_key_update(
        config_value=text("VALUES(config_value)")
    )

    await db.execute(statmetn)
    #await Service.wencaiService.updateBasicconfig(body)
#updatebasicconfig

# @router.post('/getstrategy')
# async def getstrategy(db=Depends(get_webdbsession)):
#     ret=await Service.strategyService.find(db)
#     return ret
@router.post('/updatestrategy')
async def updatestrategy(body=Body(),db=Depends(get_webdbsession)):
    values=[]
    for item in body['data']:
        dic={}
        content=item['content'].strip()
        if not content:
            continue
        sep=content.find(';')
        if sep==-1:
            sep = content.find('; ')
        if sep==-1:
            continue
        strategy_name=content[0:sep]
        dic['strategy_name']=strategy_name
        dic['content']=content
        values.append(dic)
    statmetn=delete(Models.Strategy)
    await db.execute(statmetn)
    await db.commit()
    statment=insert(Models.Strategy).values(values)
    await db.execute(statment)
