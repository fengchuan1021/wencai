# generated timestamp: 2022-10-03T10:52:05+00:00

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, Body
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import Service
import settings
from component.dbsession import get_webdbsession
from common.globalFunctions import get_token
from common import XTJsonResponse
from component.fastQL import fastQuery

from .__init__ import dependencies
from .UserShema import (
    FrontendUserLoginPostInShema,

    FrontendUserRegisterPostInShema,
)

router = APIRouter(dependencies=dependencies)


# <editor-fold desc="register">
@router.post(
    '/user/getEmailRegisterVerifyCode',
)
async def getEmailRegisterVerifyCode(
        body: Dict = Body(),
        db: AsyncSession = Depends(get_webdbsession)
) -> Any:
    """
    register
    """
    try:
        email = body['email']
    except Exception as e:
        return {'errorcode': 500, 'errormsg': 'email is required'}
    # simple check if is a valid email
    if '.' not in email or '@' not in email:
        return {'errorcode': 500, 'errormsg': 'email is invalid'}

    user = await Service.userService.getUserByPhoneOrUsernameOrEmail(db, email)
    if user:
        return {'errorcode': 500, 'errormsg': f"{email} has been registered"}
    try:
        await Service.mailService.sendMerchantRegisterVerifyMail(email)
    except Exception as e:
        return {'errorcode': 500, 'errormsg': "send mail failed"}

    return {
        'errorcode': 200,
        'errormsg': 'email has been send, please check your mailbox',

    }


# </editor-fold>

# <editor-fold desc="register">
@router.post(
    '/user/register',
)
async def register(
        body: FrontendUserRegisterPostInShema,
        db: AsyncSession = Depends(get_webdbsession)
) -> Any:
    """
    register
    """

    for i in ['email', 'phone', 'username']:
        if value := getattr(body, i):
            user = await Service.userService.getUserByPhoneOrUsernameOrEmail(db, value)
        if user:
            return {'errorcode': 500, 'errormsg': f"email has been registered"}
    verifyCode = await Service.mailService.verifyMerchantRegisterVerifyMailCode(body.email, body.verifycode)
    if not verifyCode:
        return {'errorcode': 500, 'errormsg': f"verify code is invalid"}
    body.password = Service.userService.get_password_hash(body.password)
    newuser = await Service.userService.create(db, body)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return {'errorcode': 500, 'errormsg': "email has been registered"}
    dic = settings.UserTokenData.from_orm(newuser).dict()
    newtoken, token_expireat = await Service.userService.create_access_token(db, newuser)  # type: ignore
    refreshtoken, refreshtoken_expireat = await Service.userService.create_refresh_token(db, newuser)  # type: ignore
    dic.update({

        'accessToken': newtoken, 'refreshToken': refreshtoken,
        'accessTokenExpireAt': token_expireat, 'refreshTokenExpireAt': refreshtoken_expireat
    })

    return {
        'errorcode': 200,
        'errormsg': 'resigtersuccess',
        'data': dic
    }


# </editor-fold>


# <editor-fold desc="login">
@router.post(
    '/user/login',
)
async def login(
        body: FrontendUserLoginPostInShema,
        db: AsyncSession = Depends(get_webdbsession),
) -> Any:
    """
    login
    """

    user = await Service.userService.authenticate(db, body.username, body.password)
    if not user:
        return {'errorcode': 500, 'errormsg': "username or password not valid"}
    if user.merchant_id:  # type: ignore
        merchant = await Service.merchantService.findByPk(db, user.merchant_id)  # type: ignore
        if merchant.is_reviewed == 'N':
            return {'errorcode': 500, 'errormsg': "merchant are not reviewed"}
    newtoken, token_expireat = await Service.userService.create_access_token(db, user)  # type: ignore
    refreshtoken, refreshtoken_expireat = await Service.userService.create_refresh_token(db, user)  # type: ignore

    return {
        'errorcode': 200,
        'errormsg': '',
        'data': {'accessToken': newtoken, 'refreshToken': refreshtoken,
                 'accessTokenExpireAt': token_expireat, 'refreshTokenExpireAt': refreshtoken_expireat,

                 }
    }


# </editor-fold>


# <editor-fold desc="refreshToken">
@router.post(
    '/user/refreshToken',
)
async def refreshToken(
        body: Dict = Body(),
        db: AsyncSession = Depends(get_webdbsession)
) -> Any:
    """
    register
    """
    try:
        refreshToken = body['refreshToken']
    except Exception as e:
        return {'errorcode': 500, 'errormsg': 'refreshToken is required'}

    try:
        token, tokenexpire = await Service.userService.tokenFromRefreshToken(db, refreshToken)
        print('111111')
    except Exception as e:
        return {'errorcode': 500, 'errormsg': str(e)}

    return {
        'errorcode': 200,
        'data': {'accessToken': token,
                 'accessTokenExpireAt': tokenexpire
                 }

    }


# </editor-fold>


# <editor-fold desc="userInfo">
@router.get(
    '/user/userInfo',
)
async def userInfo(
        db: AsyncSession = Depends(get_webdbsession),
        token: settings.UserTokenData = Depends(get_token),
) -> Any:
    """
    register
    """
    user = await Service.userService.findByPk(db, token.user_id)
    # userrole = await Service.userroleService.findByPk(db, user.role_id)
    if not user:
        return {'errorcode': 500, 'errormsg': 'user not found'}
    dic = token.dict()
    dic.update({'email': user.email, 'avatar': user.avatar,
                'username': user.username or user.email})  # , 'role_name': userrole.role_name}
    return {
        'errorcode': 200,
        'data': dic

    }

# </editor-fold>
